# -*- coding: utf-8 -*-
"""
Outline
=======
1. Summary_
2. Examples_
3. Routines_

.. _Summary:

Summary
=======
This module contains all classes and functions specific for the cross section 
class `Xs` that acts as a container for energy-dependent tabulated cross 
section values.


Examples
========


Routines
========

"""
import pdb
import logging

import numpy as np
from numpy.polynomial import legendre
import pandas as pd

import sandy

__author__ = "Luca Fiorito"
__all__ = [
        "Lpc",
        "lpc_to_tpd",
        ]


class Lpc():
    """
    Object for energy dependent tabulated Legendre polynomial coefficients
    that describe angular distributions.

    Attributes
    ----------
    data : `pandas.DataFrame`
        source of energy dependent Legendre polynomial coefficients

    Methods
    -------
    custom_perturbation
        Apply a custom perturbation to a given Legendre polynomial coefficient.
    reshape
        Linearly interpolate Legendre polynomial coefficients over new grid
        structure
    to_endf6
        Update cross sections in `Endf6` instance
    from_endf6
        Extract cross sections/nubar from `Endf6` instance
    to_tpd
        Convert `Lpc` instance to `Tpd` instance.
    """

    _indexnames = ["MAT", "MT", "E"]
    _columnsname = "P"

    def __repr__(self):
        return self.data.__repr__()

    def __init__(self, df, **kwargs):
        self.data = pd.DataFrame(df, dtype=float, **kwargs)

    @property
    def data(self):
        """
        Dataframe of energy-dependent tabulated cross sections.

        Attributes
        ----------
        index : `pandas.Index`
            energy grid in eV
        columns : `pandas.MultiIndex`
            MAT/MT indices
        values : `numpy.array`
            cross sections in barns

        Returns
        -------
        `pandas.DataFrame`
            tabulated xs
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._data.index.names = self.__class__._indexnames
        self._data.columns.name = self.__class__._columnsname

    def filter_by(self, key, value):
        """
        Apply condition to source data and return filtered results.

        Parameters
        ----------
        `key` : `str`
            any label present in the index of `data`
        `value` : `int` or `float`
            value used as filtering condition

        Returns
        -------
        `sandy.Edistr`
            filtered dataframe of energy distributions

        Raises
        ------
        `sandy.Error`
            if applied filter returned empty dataframe

        Notes
        -----
        .. note:: The primary function of this method is to make sure that
                  the filtered dataframe is still returned as a `Lpc`
                  object.
        """
        condition = self.data.index.get_level_values(key) == value
        out = self.data[condition]
        if out.empty:
            raise sandy.Error("applied filter returned empty dataframe")
        return self.__class__(out)

    def custom_perturbation(self, mat, mt, p, pert, inplace=False):
        """
        Apply a custom perturbation (energy dependent) to a given
        Legendre polynomial coefficient.

        Parameters
        ----------
        mat : `int`
            MAT material number
        mt : `int`
            MT reaction number
        p : `int`
            order of the Legendre polynomial coefficient
        pert : `sandy.Pert`
            tabulated perturbations
        inplace : `bool`, optional, default is `False`
            flag to activate inplace replacement

        Returns
        -------
        `Lpc`
            lpc instance with given series polynomial coefficient perturbed
        """
        eg = self.data.loc[(mat, mt)].index.values
        enew = np.union1d(eg, pert.right.index.values)
        u_lpc = self.reshape(enew, selected_mat=mat, selected_mt=mt)
        u_pert = pert.reshape(enew)
        u_lpc.data.loc[(mat, mt)][p] *= u_pert.right.values
        if inplace:
            self.data = u_lpc.data
        else:
            return Lpc(u_lpc.data)

    def reshape(self, eg, selected_mat=None, selected_mt=None, inplace=False):
        """
        Linearly interpolate Legendre polynomial coefficients
        over new grid structure.

        Parameters
        ----------
        eg : array-like object
            new energy grid
        selected_mat : `int`, optional, default is `None`
            MAT number for which the reshape will apply (all MAT by default)
        selected_mt : `int`, optional, default is `None`
            MT number for which the reshape will apply (all MT by default)
        inplace : `bool`, optional, default is `False`
            flag to activate inplace replacement

        Returns
        -------
        `Lpc`
            Legendre polynomial coefficients instance over new grid

        Warnings
        --------
        The new Legendre polynomial coefficients are tabulated over the
        union between the old and the given energy grid
        """
        listdf = []
        for (mat, mt), df in self.data.groupby(["MAT", "MT"]):
            if selected_mat:
                if mat != selected_mat:
                    listdf.append(df)
                    continue
            if selected_mt:
                if mt != selected_mt:
                    listdf.append(df)
                    continue
            df = df.T[mat][mt].T
            enew = df.index.union(eg).astype("float").rename("E")
            valsnew = sandy.shared.reshape_differential(
                df.index.values,
                df.values,
                enew
                )
            dfnew = pd.DataFrame(valsnew, index=enew, columns=df.columns) \
                      .reset_index(drop=False)
            dfnew.insert(0, "MAT", mat)
            dfnew.insert(0, "MT", mt)
            dfnew.set_index(self._indexnames, inplace=True)
            listdf.append(dfnew)
        data = pd.concat(listdf, axis=0)
        if inplace:
            self.data = data
        else:
            return Lpc(data)

    def to_endf6(self, endf6):
        """
        Update angular distributions in `Endf6` instance with those available
        in a `Lpc` instance.

        Parameters
        ----------
        `endf6` : `sandy.Endf6`
            `Endf6` instance

        Returns
        -------
        `sandy.Endf6`
            `Endf6` instance with updated angular distributions

        Warnings
        --------
        .. warning:: only lpc with `(MAT,MT)` combinations that are originally
                     present in the `Endf6` instance are modififed, the others
                     are discarded.
                     The reason behind this is that to reconstruct a endf6
                     section we need info that is not available in the `Lpc`
                     instance itself.
        """
        data = endf6.data.copy()
        mf = 4
        for (mat, mt), group in self.data.groupby(["MAT", "MT"]):
            # Must read original section to extract info not given in `Lpc` instance
            if (mat, mf, mt) not in endf6.keys:
                continue
            sec = endf6.read_section(mat, mf, mt)
            if "LPC" not in sec:
                continue
            for e in group.loc[mat, mt].index:
                T = sec["LPC"]["E"][e]["T"] if e in sec["LPC"]["E"] else 0
                LT = sec["LPC"]["E"][e]["LT"] if e in sec["LPC"]["E"] else 0
                coeff = group.loc[mat, mt, e]
                len_coeff = coeff.ne(0)[::-1].idxmax()
                if len_coeff < 4:
                    len_coeff = 4
                # reduce number of coefficient for each energy by cutting the zeros
                # (keep at least 4 coefficients)
                dict_distr = {
                    "COEFF": coeff[1:len_coeff+1],
                    "LT": LT,
                    "T": T,
                    }
                sec["LPC"]["E"].update({e: dict_distr})
            sec["LPC"]["NBT"] = [len(sec["LPC"]["E"])]
            sec["LPC"]["INT"] = [2]
            data[mat, mf, mt] = sandy.write_mf4(sec)
        return sandy.Endf6(data)

    def _to_tab(self, mat, mt, e, cosines):
        """
        Return tabulated angular distribution for given MAT, MT and energy
        point.
        """
        from numpy.polynomial import legendre
        sec = self.loc[mat, mt]
        if (e < min(sec.index)) | (e > max(sec.index)):
            raise NotImplementedError("Energy is out of range")
        if e not in sec.index:
            eg = sorted(set(sec.index) | {e})
            sec = sec.reindex(eg).interpolate(method="slinear")
        coeff = sec.loc[e].dropna()
        c = (coeff.index.values*2+1)/2 * coeff.values
        adistr = legendre.legval(cosines, c)
        return pd.Series(adistr, index=cosines, name=(mat, mt, e))

    def _add_points(self, extra_points):
        """
        Add additional entries to Lpc incoming energies.
        """
        points = np.array(sorted(extra_points))
        frame = self.copy()
        List = []
        for (mat, mt),df in frame.groupby(["MAT","MT"]):
            rdf = df.loc[mat, mt]
            mask = (points >= min(rdf.index)) & (points <= max(rdf.index))
            grid = sorted((set(rdf.index) | set(points[mask])))
            rdf = rdf.reindex(grid)
            df_notnan = rdf.dropna(axis="columns", thresh=2).interpolate(method='slinear')
            rdf.update(df_notnan)
            rdf = rdf.reset_index()
            rdf["MAT"] = mat
            rdf["MT"] = mt
            rdf = rdf.set_index(["MAT", "MT", "E"])
            List.append(rdf)
        return Lpc(pd.concat(List, axis=0))

    def _perturb(self, pert, method=2, **kwargs):
        """
        Perturb Legendre polynomials coefficients given a set of perturbations.
        
        Parameters
        ----------
        pert : pandas.Series
            multigroup perturbations from sandy.LpcSamples
        method : int
            * 1 : samples outside the range [0, 2*_mean_] are set to _mean_.
            * 2 : samples outside the range [0, 2*_mean_] are set to 0 or 2*_mean_ respectively if they fall below or above the defined range.

        Returns
        -------
        sandy.Lpc
        """
        frame = self.copy()
        for (mat, mt), _ in self.groupby(["MAT", "MT"]):
            if (mat, mt) not in pert.index:
                continue
            lpc = frame.loc[mat, mt]
            prt = pert.loc[mat, mt]
            eprt = prt.index.get_level_values("E").unique().values # get cov energies
            elpc = lpc.index.get_level_values("E").unique().values # get lpc energies
            eg = np.array(sorted(set(eprt) | set(elpc)))
            eg = eg[(eg <= max(elpc)) & (eg >= min(elpc))]  # limit to lpc range
            lpc_copy = lpc.reindex(eg)
            df_notnan = lpc_copy.dropna(axis="columns", thresh=2) # cut P columns with less than 2 not-NaN
            df_notnan = df_notnan.interpolate(method='slinear')
            lpc_copy.update(df_notnan)
            for l, _ in prt.groupby("L"):
                P = prt.loc[l].reindex(eg).ffill()
                if method == 2:
                    P = P.where(P > 0, 0.0)
                    P = P.where(P < 2, 2.0)
                elif method == 1:
                    P = P.where((P > 0) & (P < 2), 1.0)
                lpc_copy[l] *= P
            lpc_copy = lpc_copy.reset_index()
            lpc_copy["MAT"] = mat
            lpc_copy["MT"] = mt
            lpc_copy = Lpc(lpc_copy.set_index(["MAT", "MT", "E"]))
            frame.update(lpc_copy)
        return Lpc(frame)

    def to_tpd(self, cosines=np.linspace(-1, 1, 101)):
        """
        Convert `Lpc` instance to `Tpd` instance.
        """
        df = self.data.T.agg(lpc_to_tpd, cosines=cosines).T
        return Tpd(df)

    @classmethod
    def from_endf6(cls, endf6):
        """
        Extract legendre polynomial coefficients from `Endf6` instance.

        Parameters
        ----------
        `endf6` : `sandy.Endf6`
            `Endf6` instance

        Returns
        -------
        `Lpc`
            Legendre polynomial coefficient data

        Raises
        ------
        `sandy.Error`
            if requested LPC were not found

        Warnings
        --------
        `logging.warn`
            skip section if coefficiets request an interpolation scheme over 
            energy that is not lin-lin.
        """
        tape = endf6.filter_by(listmf=[4])
        data = []
        for mat, mf, mt in tape.data:
            sec = tape.read_section(mat, mf, mt)
            if "LPC" not in sec:
                continue
            if sec["LPC"]["INT"] != [2]:
                logging.warn("skip LPC with non-linlin interpolation for MAT{}/MF{}/MT{}".format(mat, mf, mt))
                continue
            for energy, vals in sec["LPC"]["E"].items():
                # add P0 coefficient, which is 1
                coefficients = [1] + vals["COEFF"]
                name = (sec["MAT"], sec["MT"], energy)
                series = pd.Series(coefficients, name=name)
                data.append(series)
        if not data:
            raise sandy.Error("requested LPC were not found")
        df = pd.DataFrame(data).fillna(0)
        df.index = pd.MultiIndex.from_tuples(df.index, names=["MF", "MT", "E"])
        return Lpc(df)


class Tpd():
    """
    Tabulated probability distribution for angular distribution of outgoing
    particles.

    Dataframe components
    --------------------
    index :
        - MAT number
        - MT number
        - incoming neutron energy

    columns :
        - cosines
    """

    _indexnames = ["MAT", "MT", "E"]
    _columnsname = "COSINE"

    def __repr__(self):
        return self.data.__repr__()

    def __init__(self, df, **kwargs):
        self.data = pd.DataFrame(df, dtype=float, **kwargs)

    @property
    def data(self):
        """
        Dataframe of angular distibutions tabulated along energy and cosine.

        Attributes
        ----------
        index : `pandas.MultiIndex`
            MAT/MT/energy (in eV) indices
        columns : `pandas.Index`
            cosines
        values : `numpy.array`
            tabulated angular distribution values (normalized to 1)

        Returns
        -------
        `pandas.DataFrame`
            tabulated angular distibutions

        Raises
        ------
        `sandy.Error`
            if `data` is not a `pandas.DataFrame`
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._data.index.names = self.__class__._indexnames
        self._data.columns.name = self.__class__._columnsname

    @property
    def integrals(self):
        """
        Integrals of each angular distribution given per energy value

        .. note:: these integrals should always be equal to 1
                  (within a tolerance)

        Returns
        -------
        `pandas.Series`
            integrals of the distributions
        """
        delta_cos = np.diff(self.data.columns.values)
        vleft = self.data.iloc[:, :-1].values
        vright = self.data.iloc[:, 1:].values
        values = (vleft + vright) / 2.
        integrals = np.dot(values, delta_cos)
        return pd.Series(integrals, index=self.data.index, name="integral")


def lpc_to_tpd(coeff, cosines):
    """
    Convert polynomial coefficients into cosine-tabulated distribution.

    Parameters
    ----------
    coeff : array-like object
        Legendre prolynomial coefficients starting from P0 up to any order
    cosines : array-like object
        Cosines values over which to tabulate the distribution

    Returns
    -------
    `pandas.Series`
        tabulated distribution
    """
    ll = np.arange(coeff.size)  # order of the polynomial
    a = (2 * ll + 1) / 2 * coeff
    distr = legendre.legval(cosines, a)
    index = pd.Series(cosines, name="COSINE")
    return pd.Series(distr, index=index)
