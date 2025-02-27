# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:50:33 2019

@author: lfiorito
"""
import io
import shutil
import os
from functools import reduce
from tempfile import TemporaryDirectory
import logging
from urllib.request import urlopen, Request
from zipfile import ZipFile


import pandas as pd

import sandy
from sandy.libraries import (
    N_FILES_ENDFB_71_IAEA,
    N_FILES_JEFF_32_NEA,
    N_FILES_JEFF_33_IAEA,
    N_FILES_JEFF_40T0_NEA,
    N_FILES_ENDFB_80_IAEA,
    N_FILES_JENDL_40U_IAEA,
    URL_N_ENDFB_71_IAEA,
    URL_N_JEFF_32_NEA,
    URL_N_JEFF_33_IAEA,
    URL_N_JEFF_40T0_NEA,
    URL_N_ENDFB_80_IAEA,
    URL_N_JENDL_40U_IAEA,
    URL_NFPY_ENDFB_80_IAEA,
    NFPY_FILES_ENDFB_80_IAEA,
    URL_NFPY_ENDFB_71_IAEA,
    NFPY_FILES_ENDFB_71_IAEA,
    URL_NFPY_JENDL_40U_IAEA,
    NFPY_FILES_JENDL_40U_IAEA,
    URL_NFPY_JEFF_33_IAEA,
    NFPY_FILES_JEFF_33_IAEA,
    URL_DECAY_ENDFB_71_IAEA,
    DECAY_FILES_ENDFB_71_IAEA,
    URL_DECAY_ENDFB_80_IAEA,
    DECAY_FILES_ENDFB_80_IAEA,
    URL_DECAY_JEFF_33_IAEA,
    DECAY_FILES_JEFF_33_IAEA,
    )


__author__ = "Luca Fiorito"
__all__ = [
        "Endf6",
        "get_endf6_file",
        ]

pd.options.display.float_format = '{:.5e}'.format


def get_endf6_file(library, kind, zam, to_file=False):
    """
    Given a library and a nuclide import the corresponding ENDF-6 nuclear
    data file directly from internet.

    Parameters
    ----------
    library : `str`
        nuclear data library. Available libraries are:
        for `xs`
            * `'endfb_71'`
            * `'jeff_32'`
            * `'jeff_33'`
            * `'jeff_40t0'`
            * `'endfb_80'`
            * `'jendl_40u`
        for 'nfpy'
            * `'endfb_71'`
            * `'jeff_33'`
            * `'endfb_80'`
            * `'jendl_40u`
        for decay:
            * `'endfb_71'`
            * `'jeff_33'`
            * `'endfb_80'`
    kind : `str`
        nuclear data type:
            * `xs` is a standard neutron-induced nuclear data file
            * 'nfpy' is a Neutron-Induced Fission Product Yields nuclear data
              file
            * 'decay' is a Radioactive Decay Data nuclear data file
    zam : `int` or 'all' or iterable
        zam = 'int' (individual nuclides) or iterable (group of nuclides)
            ZAM nuclide identifier $Z \\times 10000 + A \\times 10 + M$ where:
                * $Z$ is the charge number
                * $A$ is the mass number
                * $M$ is the metastate level (0=ground, 1=1st level)
        zam = 'all'
            We obtain the information of all the library. Actually,
            the only all libraries available are:
                * for 'nfpy': 'jeff_33'
                * for 'decay': 'jeff_33'
    Raises
    ------
    ValueError
        if library is not among available selection.

    ValueError
        if when you select 'xs', you select zam = 'all'

    Returns
    -------
    `Endf6`
        `Endf6` object with ENDF-6 data for specified library and nuclide.

    Examples
    --------

#    Import hydrogen file from JEFF-4.0T0.
#    >>> tape = sandy.get_endf6_file("jeff_40t0", 'xs', 10010)
#    >>> assert type(tape) is sandy.Endf6

    Import hydrogen file from JEFF-3.3.
    >>> tape = sandy.get_endf6_file("jeff_33", 'xs', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import hydrogen file from ENDF/B-VII.1.
    >>> tape = sandy.get_endf6_file("endfb_71", 'xs', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import hydrogen file from ENDF/B-VIII.0.
    >>> tape = sandy.get_endf6_file("endfb_80", 'xs', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import hydrogen file from JENDL-4.0u
    >>> tape = sandy.get_endf6_file("jendl_40u", 'xs', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import Neutron-Induced Fission Product Yields for Th-227 from ENDF/B-VII.1.
    >>> tape = sandy.get_endf6_file("endfb_71", 'nfpy', 902270)
    >>> assert type(tape) is sandy.Endf6

    Import Neutron-Induced Fission Product Yields for Th-227 from ENDF/B-VIII.0
    >>> tape = sandy.get_endf6_file("endfb_80", 'nfpy', 902270)
    >>> assert type(tape) is sandy.Endf6

    Import Neutron-Induced Fission Product Yields for Th-227 from JENDL-4.0u
    >>> tape = sandy.get_endf6_file("jendl_40u", 'nfpy', 902270)
    >>> assert type(tape) is sandy.Endf6

    Import Neutron-Induced Fission Product Yields for Th-232 from JEFF-3.3
    >>> tape = sandy.get_endf6_file("jeff_33", 'nfpy', 902320)
    >>> assert type(tape) is sandy.Endf6

    Import Radioactive Decay Data for H-1 from JEFF-3.3
    >>> tape = sandy.get_endf6_file("jeff_33", 'decay', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import Radioactive Decay Data for H-1 from ENDF/B-VII.1.
    >>> tape = sandy.get_endf6_file("endfb_71", 'decay', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import Radioactive Decay Data for H-1 from ENDF/B-VIII.0.
    >>> tape = sandy.get_endf6_file("endfb_80", 'decay', 10010)
    >>> assert type(tape) is sandy.Endf6

    Import all Neutron-Induced Fission Product Yields from ENDF/B-VII.1.
    >>> tape = sandy.get_endf6_file("endfb_71", 'nfpy', 'all')
    >>> assert type(tape) is sandy.Endf6

    Import a list of Decay Data for JEFF-3.3.
    >>> tape = sandy.get_endf6_file("jeff_33", 'decay', [380900, 551370, 541350])
    >>> assert type(tape) is sandy.Endf6

#    Checked, but the test takes too long(~10 min), that's why it is commented.
#    Import all Radioactive Decay Data from ENDF/B-VIII.0.
#    >>> tape = sandy.get_endf6_file("endfb_80", 'decay', 'all')
#    >>> assert type(tape) is sandy.Endf6
    """
    foo_get = Endf6.from_zipurl
    foo_read = Endf6.read_zipurl
    if kind == 'xs':
        available_libs = (
            "jeff_32".upper(),
            "jeff_33".upper(),
            "jeff_40t0".upper(),
            "endfb_71".upper(),
            "endfb_80".upper(),
            "jendl_40u".upper(),
            )
        library_ = library.lower()
        if library_ == "jeff_40t0":
            url = URL_N_JEFF_40T0_NEA
            files = N_FILES_JEFF_40T0_NEA
            foo_read = Endf6.read_url
            foo_get = Endf6.from_url
        elif library_ == "jeff_33":
            url = URL_N_JEFF_33_IAEA
            files = N_FILES_JEFF_33_IAEA
        elif library_ == "jeff_32":
            url = URL_N_JEFF_32_NEA
            files = N_FILES_JEFF_32_NEA
            foo_read = Endf6.read_url
            foo_get = Endf6.from_url
        elif library_ == "endfb_71":
            url = URL_N_ENDFB_71_IAEA
            files = N_FILES_ENDFB_71_IAEA
        elif library_ == "endfb_80":
            url = URL_N_ENDFB_80_IAEA
            files = N_FILES_ENDFB_80_IAEA
        elif library_ == "jendl_40u":
            url = URL_N_JENDL_40U_IAEA
            files = N_FILES_JENDL_40U_IAEA
        else:
            raise ValueError(
                f"""library '{library}' is not available.
                Available libraries are: {available_libs}
                """
                )
    elif kind == 'nfpy':
        available_libs = (
            "endfb_71".upper(),
            "endfb_80".upper(),
            "jendl_40u".upper(),
            "jeff_33".upper(),
            )
        library_ = library.lower()
        if library_ == "endfb_71":
            url = URL_NFPY_ENDFB_71_IAEA
            files = NFPY_FILES_ENDFB_71_IAEA
        elif library_ == "endfb_80":
            url = URL_NFPY_ENDFB_80_IAEA
            files = NFPY_FILES_ENDFB_80_IAEA
        elif library_ == "jendl_40u":
            url = URL_NFPY_JENDL_40U_IAEA
            files = NFPY_FILES_JENDL_40U_IAEA
        elif library_ == "jeff_33":
            url = URL_NFPY_JEFF_33_IAEA
            files = NFPY_FILES_JEFF_33_IAEA
        else:
            raise ValueError(
                f"""library '{library}' is not available.
                Available libraries are: {available_libs}
                """
                    )

    elif kind == 'decay':
        available_libs = (
            "endfb_71".upper(),
            "endfb_80".upper(),
            "jeff_33".upper(),
            )
        library_ = library.lower()
        if library_ == "endfb_71":
            url = URL_DECAY_ENDFB_71_IAEA
            files = DECAY_FILES_ENDFB_71_IAEA
        elif library_ == "endfb_80":
            url = URL_DECAY_ENDFB_80_IAEA
            files = DECAY_FILES_ENDFB_80_IAEA
        elif library_ == "jeff_33":
            url = URL_DECAY_JEFF_33_IAEA
            files = DECAY_FILES_JEFF_33_IAEA
        else:
            raise ValueError(
                f"""library '{library}' is not available.
                Available libraries are: {available_libs}
                """
                    )
    if str(zam).lower() == 'all':
        if kind.lower() == 'xs':
            raise ValueError("'all' option is not available for xs")
        text = "".join([foo_read(name, url) for name in files.values()])
        tape = Endf6.from_text(text)
    else:
        if hasattr(zam, "__len__"):
            tapes = map(lambda x: foo_get(files[x], url), zam)
            tape = reduce(lambda x, y: x.add_sections(y.data), tapes)
        else:
            tape = foo_get(files[zam], url)

    if to_file:
        basename = sandy.zam.zam2nuclide(zam, atomic_number=True, sep="-")
        filename = f"{basename}.{library_}"
        logging.info(f"writing nuclear data to file '{filename}'")
        tape.to_file(filename)
    return tape


class _FormattedFile():
    """
    Base class to store ENDF-6 content grouped by `(MAT, MF, MT)`

    Attributes
    ----------
    data

    keys

    kind : `str`
        Kind of ENDF-6 formatted file (`'endf6'`, `'pendf'`, `'gendf'`,
        `'errorr'`) .

    mat : `int`
        MAT number.
    mf : `int`
        MF number.
    mt : `int`
        MT number

    Methods
    -------
    add_sections
        Add text section for given `(MAT, MF, MT)`.
    filter_by
        Filter dataframe based on `(MAT, MF, MT)` lists.
    from_file
        Create dataframe by reading a ENDF-6-formatted file.
    from_text
        Create dataframe from endf6 text in string.
    to_series
        Covert content into `pandas.Series`.

    Notes
    -----
    This class supports ENDF-6 content from ENDF-6 files, ERRORR files and
    GROUPR files.
    """

    def __repr__(self):
        return self.to_series().__repr__()

    def __init__(self, data, file=None):
        self.data = data
        self.file = file

    @property
    def data(self):
        """
        """
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, dict):
            raise sandy.Error("'data' is not a 'dict'")
        self._data = data

    @property
    def keys(self):
        """
        List of keys `(MAT, MF, MT)` used to identify each tape section.

        Returns
        -------
        `list`
            list of tuples of type `(MAT, MF, MT)` for each section found in
            tape.
        """
        return list(self.data.keys())

    @property
    def _keys(self):
        mat, mf, mt = zip(*self.data.keys())
        return {"MAT": mat, "MF": mf, "MT": mt}

    @property
    def mat(self):
        return sorted(set(self._keys["MAT"]))

    @property
    def mf(self):
        return sorted(set(self._keys["MF"]))

    @property
    def mt(self):
        return sorted(set(self._keys["MT"]))

    def to_series(self, **kwargs):
        series = pd.Series(self.data, **kwargs).sort_index(ascending=True)
        series.index.names = ["MAT", "MF", "MT"]
        return series

    @property
    def is_empty(self):
        return False if self.data else True

    @property
    def kind(self):
        """
        Kind of ENDF-6 formatted file (`'endf6'`, `'pendf'`, `'gendf'`,
        `'errorr'`) .

        Returns
        -------
        `str`
            kind of ENDF-6 formatted file

        Examples
        --------
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> _FormattedFile.from_file(file).kind
        'endf6'

        >>> file = os.path.join(sandy.data.__path__[0], "h1.pendf")
        >>> _FormattedFile.from_file(file).kind
        'pendf'
        """
        if len(self.mat) > 1:
            msg = "Attribute 'kind' does not work if more than 1 MAT number is"
            "found"
            raise AttributeError(msg)
        mat = self.mat[0]
        text = self.data[(mat, 1, 451)]
        lrp = int(text[22:33])
        nlib = int(text[44:55])
        if nlib == -11 or nlib == -12:
            kind = "errorr"
        elif nlib == -1:
            kind = "gendf"
        else:
            if lrp == 2:
                kind = "pendf"
            elif lrp == 1 or lrp == 0:
                kind = "endf6"
            else:
                kind == "unkwown"
        return kind

    @classmethod
    def from_url(cls, filename, rooturl):
        """
        Given a filename and the url where the file is located,
        extract the ENDF6 data from the file into a sandy.Endf6
        instance.

        Parameters
        ----------
        filename: 'str'
            The filename without path of the zip file to read
        rooturl: 'str'
            The url direction to extract the zip files

        Returns
        -------
        `Endf6`
            `Endf6` object with ENDF-6 data for specified library and nuclide.

        Examples
        --------

        >>> filename = "n-1-H-001.jeff32"
        >>> rooturl = "https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_32/"
        >>> sandy.Endf6.from_url(filename, rooturl)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
            2   151     1.001000+3 9.991673-1          0          0  ...
            3   1       1.001000+3 9.991673-1          0          0  ...
                2       1.001000+3 9.991673-1          0          0  ...
                102     1.001000+3 9.991673-1          0          0  ...
            4   2       1.001000+3 9.991673-1          0          1  ...
            6   102     1.001000+3 9.991673-1          0          2  ...
            33  1       1.001000+3 9.991673-1          0          0  ...
                2       1.001000+3 9.991673-1          0          0  ...
                102     1.001000+3 9.991673-1          0          0  ...
        dtype: object
        """
        text = cls.read_url(filename, rooturl)
        tape = cls.from_text(text)
        return tape

    @staticmethod
    def read_url(filename, rooturl):
        """
        Given a filename and the url where the file is located,
        extract the ENDF6 data from the file into a string.

        Parameters
        ----------
        filename: 'str'
            The filename without path of the zip file to read
        rooturl: 'str'
            The url direction to extract the zip files

        Returns
        -------
        `str`
            All the endf6 data in a 'str'

        Examples
        --------

        >>> filename = "n-1-H-001.jeff32"
        >>> rooturl = "https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_32/"
        >>> file = sandy.Endf6.read_url(filename, rooturl)
        >>> print(file[0:890])
        JEFF-3.2 Release - Neutron File March 2014                             0  0    0
        1.001000+3 9.991673-1          0          0          2          5 125 1451    1
        0.000000+0 0.000000+0          0          0          0          6 125 1451    2
        1.000000+0 2.000000+7          1          0         10         32 125 1451    3
        0.000000+0 0.000000+0          0          0         87         10 125 1451    4
        1-H -  1 LANL       EVAL-OCT05 G.M.Hale                          125 1451    5
                            DIST-DEC06                       20111222    125 1451    6
        ----JEFF32            MATERIAL  125                                125 1451    7
        -----INCIDENT NEUTRON DATA                                         125 1451    8
        ------ENDF-6 FORMAT                                                125 1451    9
        *****************************  JEFF-3.2    *********************** 125 1451   10
        """
        url = f"{rooturl}/{filename}"
        # set a known browser user agent to ensure access
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'},)
        with urlopen(req) as f:
            text = f.read().decode('utf-8')
        return text

    @classmethod
    def from_zipurl(cls, filename, rooturl):
        """
        Given a filename and the url where the file is located (in
        zipped format), extract the ENDF6 data from the file into a
        sandy.Endf6 instance.

        Parameters
        ----------
        filename: 'str'
            The filename without path of the zip file to read
        rooturl: 'str'
            The url direction to extract the zip files

        Returns
        -------
        `Endf6`
            `Endf6` object with ENDF-6 data for specified library and nuclide.

        Examples
        --------

        >>> filename = "decay_1907_57-La-149.dat"
        >>> rooturl = "https://www-nds.iaea.org/public/download-endf/ENDF-B-VII.1/decay/"
        >>> sandy.Endf6.from_zipurl(filename, rooturl)
        MAT   MF  MT
        1907  1   451     5.714900+4 1.476553+2         -1          0  ...
            8   457     5.714900+4 1.476553+2          0          0  ...
        dtype: object
        """
        text = cls.read_zipurl(filename, rooturl)
        tape = cls.from_text(text)
        return tape

    @staticmethod
    def read_zipurl(filename, rooturl):
        """
        Given a filename and the url where the file is located (in
        zipped format), extract the ENDF6 data from the file into
        a string.

        Parameters
        ----------
        filename: 'str'
            The filename without path of the zip file to read
        rooturl: 'str'
            The url direction to extract the zip files

        Returns
        -------
        `str`
            All the endf6 data in a 'str'

        Examples
        --------

        >>> filename = "decay_1907_57-La-149.dat"
        >>> rooturl = "https://www-nds.iaea.org/public/download-endf/ENDF-B-VII.1/decay/"
        >>> file = sandy.Endf6.read_zipurl(filename, rooturl)
        >>> print(file[0:971])
        Retrieved by E4-util: 2012/01/16,13:45:44                            1 0  0    0
        5.714900+4 1.476553+2         -1          0          0          11907 1451    1
        0.000000+0 1.000000+0          0          0          0          61907 1451    2
        0.000000+0 0.000000+0          1          0          4          71907 1451    3
        0.000000+0 0.000000+0          0          0         27          21907 1451    4
        57-La-149  BNL        EVAL-AUG11 Conv. from CGM                  1907 1451    5
        /ENSDF/                                               20111222   1907 1451    6
        ----ENDF/B-VII.1      Material 1907                               1907 1451    7
        -----RADIOACTIVE DECAY DATA                                       1907 1451    8
        ------ENDF-6 FORMAT                                               1907 1451    9
        *********************** Begin Description *********************** 1907 1451   10
        **         ENDF/B-VII.1 RADIOACTIVE DECAY DATA FILE            ** 1907 1451   11
        """
        rootname = os.path.splitext(filename)[0]
        zipurl = f"{rooturl}/{rootname}.zip"
        # set a known browser user agent to ensure access
        req = Request(zipurl, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as zipresp:
            with ZipFile(io.BytesIO(zipresp.read())) as zfile:
                with TemporaryDirectory() as td:
                    zfile.extract(filename, path=td)
                    tmpfile = os.path.join(td, filename)
                    with open(tmpfile, "r") as f:
                        text = f.read()
        return text

    @classmethod
    def from_file(cls, file):
        """
        Create dataframe by reading a file.

        Parameters
        ----------
        file : `str`
            filename

        Returns
        -------
        `sandy.formats.endf6.BaseFile` or derived instance
            Dataframe containing ENDF6 data grouped by MAT/MF/MT

        Examples
        --------
        Read hydrogen tape from endf-6 formatted file.
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> _FormattedFile.from_file(file)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object

        Read hydrogen tape from text stream.
        >>> stream = io.StringIO(open(file).read())
        >>> _FormattedFile.from_file(stream)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object
        """
        if isinstance(file, io.StringIO):
            text = file.read()
        else:
            with open(file) as f:
                text = f.read()
        return cls.from_text(text)

    @classmethod
    def from_text(cls, text):
        """Create dataframe from endf6 text in string.

        Parameters
        ----------
        text : `str`
            string containing the evaluated data

        Returns
        -------
        `sandy.formats.endf6.BaseFile` or derived instance
            Dataframe containing ENDF6 data grouped by MAT/MF/MT

        Examples
        --------
        Read hydrogen tape from text.
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> text = open(file).read()
        >>> _FormattedFile.from_text(text)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object
        """
        df = pd.read_fwf(
            io.StringIO(text),
            widths=[66, 4, 2, 3],
            names=["TEXT", "MAT", "MF", "MT"],
            dtype={"TEXT": str, "MAT": str, "MF": int, "MT": int},
            na_filter=False,  # speeds up and does not add NaN in empty lines
            # Do not use TEXT because  the parser does not preserve the
            # whitespaces
            usecols=("MAT", "MF", "MT"),
            )
        # use splitlines instead of readlines to remove "\n"
        df["TEXT"] = text.splitlines()
        #
        title = df["TEXT"].iloc[0]
        title_mat = df["MAT"].iloc[0]
        try:
            int(title_mat)
        except ValueError:
            logging.warning(f"wrong MAT number in the file title\n'{title}'")
            df = df.iloc[1:].reset_index(drop=True)
        finally:
            df["MAT"] = df["MAT"].astype(int)
        condition = (df.MT > 0) & (df.MF > 0) & (df.MAT > 0)
        data = df[condition].groupby(["MAT", "MF", "MT"])\
                            .agg({"TEXT": "\n".join})\
                            .TEXT\
                            .to_dict()
        return cls(data)

    def _get_section_df(self, mat, mf, mt, delimiter="?"):
        """
        """
        text = self.data[(mat, mf, mt)]

        def foo(x):
            return sandy.shared.add_delimiter_every_n_characters(
                x[:66],
                11,
                delimiter=delimiter,
            )
        newtext = "\n".join(map(foo, text.splitlines())).replace('"', '*')
        df = pd.read_csv(
            io.StringIO(sandy.shared.add_exp_in_endf6_text(newtext)),
            delimiter=delimiter,
            na_filter=True,
            names=["C1", "C2", "L1", "L2", "N1", "N2"],
        )
        return df

    def add_section(self, mat, mf, mt, text):
        """
        Given MAT, MF and MT add/replace the corresponding section in the
        `Endf6.data`.

        Parameters
        ----------
        mat : `int`
            MAT number
        mf : `int`
            MF number
        mt : `int`
            MT number

        Returns
        -------
        `sandy._FormattedFile` or derived instance
            object with new section

        Examples
        --------
        >>> tape = sandy.Endf6({(9437, 3, 102) : "lorem ipsum"})
        >>> tape.add_section(9999, 1, 1, "dolor sit amet")
        MAT   MF  MT
        9437  3   102       lorem ipsum
        9999  1   1      dolor sit amet
        dtype: object
        """
        d = self.data.copy()
        key = (mat, mf, mt)
        d[key] = text
        return self.__class__(d)

    def add_sections(self, sections):
        d = self.data.copy()
        for (mat, mf, mt), text in sections.items():
            key = (mat, mf, mt)
            d[key] = text
        return self.__class__(d)

    def delete_section(self, mat, mf, mt, raise_error=True):
        """
        Given MAT, MF and MT delete the corresponding section from the
        `Endf6.data`.

        Parameters
        ----------
        mat : `int`
            MAT number
        mf : `int`
            MF number
        mt : `int`
            MT number

        Returns
        -------
        `sandy._FormattedFile` or derived instance
            object without given section

        Examples
        --------
        Delete capture cross section from hydrogen file.
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> tape = _FormattedFile.from_file(file)
        >>> new = tape.delete_section(125, 3, 102)
        >>> new
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object
        """
        d = self.data.copy()
        key = (mat, mf, mt)
        if key not in d and raise_error is False:
            pass
        else:
            del d[key]
        return self.__class__(d)

    def delete_sections(self, sections, raise_error=True):
        d = self.data.copy()
        for mat, mf, mt in sections:
            key = (mat, mf, mt)
            if key not in d and raise_error is False:
                pass
            else:
                del d[key]
        return self.__class__(d)

    def merge(self, *iterable):
        """
        Given a single `sandy.Endf6` object or an iterable of `sandy.Endf6`
        objects as keyword arguments, add their sections to a copy of the
        `self` instance and return a new `sandy.Endf6` object.
        The new `sandy.Endf6` object contains all MAT/MF/MT sections in `self`
        and in the passed arguments.

        Parameters
        ----------
        iterable : `sandy.Endf6` or iterable of `sandy.Endf6` objects
            The ENDF6 files that will be merged to `self`.

        Returns
        -------
        merged : TYPE
            a ENDF6 file containing the MAT/MF/MT sections of `self` and of
            the passed ENDF6 files.

        Notes
        -----
        .. note:: if any section (MAT/MF/MT) already present in the orginal
                  ENDF6 tape also appears in any tape that is being merged,
                  then the original ENDF6 section will be overwritten.

        Examples
        --------
        Merge two files.
        >>> h1 = sandy.get_endf6_file("jeff_33", 'xs', 10010)
        >>> h2 = sandy.get_endf6_file("endfb_71", 'xs', 10020)
        >>> h1.merge(h2)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        128  1   451     1.002000+3 1.996800+0          0          0  ...
             2   151     1.002000+3 1.996800+0          0          0  ...
             3   1       1.002000+3 1.996800+0          0          0  ...
                 2       1.002000+3 1.996800+0          0          0  ...
                 3       1.002000+3 1.996800+0          0          0  ...
                 16      1.002000+3 1.996800+0          0          0  ...
                 102     1.002000+3 1.996800+0          0          0  ...
             4   2       1.002000+3 1.996800+0          0          2  ...
             6   16      1.002000+3 1.996800+0          0          1  ...
             8   102     1.002000+3 1.996800+0          0          0  ...
             9   102     1.002000+3 1.996800+0          0          0  ...
             12  102     1.002000+3 1.996800+0          1          0  ...
             14  102     1.002000+3 1.996800+0          1          0  ...
             33  1       1.002000+3 1.996800+0          0          0  ...
                 2       1.002000+3 1.996800+0          0          0  ...
                 16      1.002000+3 1.996800+0          0          0  ...
                 102     1.002000+3 1.996800+0          0          0  ...
        dtype: object

        Merge three files from different libraries.
        >>> h3 = sandy.get_endf6_file("endfb_71", 'xs', 10030)
        >>> h1.merge(h2, h3)
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          0          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        128  1   451     1.002000+3 1.996800+0          0          0  ...
             2   151     1.002000+3 1.996800+0          0          0  ...
             3   1       1.002000+3 1.996800+0          0          0  ...
                 2       1.002000+3 1.996800+0          0          0  ...
                 3       1.002000+3 1.996800+0          0          0  ...
                 16      1.002000+3 1.996800+0          0          0  ...
                 102     1.002000+3 1.996800+0          0          0  ...
             4   2       1.002000+3 1.996800+0          0          2  ...
             6   16      1.002000+3 1.996800+0          0          1  ...
             8   102     1.002000+3 1.996800+0          0          0  ...
             9   102     1.002000+3 1.996800+0          0          0  ...
             12  102     1.002000+3 1.996800+0          1          0  ...
             14  102     1.002000+3 1.996800+0          1          0  ...
             33  1       1.002000+3 1.996800+0          0          0  ...
                 2       1.002000+3 1.996800+0          0          0  ...
                 16      1.002000+3 1.996800+0          0          0  ...
                 102     1.002000+3 1.996800+0          0          0  ...
        131  1   451     1.003000+3 2.989596+0          0          0  ...
             2   151     1.003000+3 2.989596+0          0          0  ...
             3   1       1.003000+3 2.989596+0          0          0  ...
                 2       1.003000+3 2.989596+0          0          0  ...
                 16      1.003000+3 2.989596+0          0          0  ...
             4   2       1.003000+3 2.989596+0          0          1  ...
                 16      1.003000+3 2.989596+0          0          2  ...
             5   16      1.003000+3 2.989596+0          0          0  ...
        dtype: object

        Merge two evaluations for the same nuclide.
        >>> h2_2 = sandy.get_endf6_file("jeff_32", 'xs', 10020)
        >>> h2.merge(h2_2)
        MAT  MF  MT
        128  1   451     1.002000+3 1.995712+0          0          0  ...
             2   151     1.002000+3 1.995712+0          0          0  ...
             3   1       1.002000+3 1.995712+0          0          0  ...
                 2       1.002000+3 1.995712+0          0          0  ...
                 3       1.002000+3 1.995712+0          0          0  ...
                 16      1.002000+3 1.995712+0          0          0  ...
                 102     1.002000+3 1.995712+0          0          0  ...
             4   2       1.002000+3 1.995712+0          0          1  ...
             6   16      1.002000+3 1.995712+0          0          1  ...
             8   102     1.002000+3 1.996800+0          0          0  ...
             9   102     1.002000+3 1.996800+0          0          0  ...
             12  102     1.002000+3 1.995712+0          1          0  ...
             14  102     1.002000+3 1.995712+0          1          0  ...
             33  1       1.002000+3 1.996800+0          0          0  ...
                 2       1.002000+3 1.996800+0          0          0  ...
                 16      1.002000+3 1.996800+0          0          0  ...
                 102     1.002000+3 1.996800+0          0          0  ...
        dtype: object
        """
        tape = reduce(lambda x, y: x.add_sections(y.data), iterable)
        merged = self.add_sections(tape.data)
        return merged

    def filter_by(self,
                  listmat=range(1, 10000),
                  listmf=range(1, 10000),
                  listmt=range(1, 10000)):
        """Filter dataframe based on MAT, MF, MT lists.

        Parameters
        ----------
        listmat : `list` or `None`
            list of requested MAT values (default is `None`: use all MAT)
        listmf : `list` or `None`
            list of requested MF values (default is `None`: use all MF)
        listmt : `list` or `None`
            list of requested MT values (default is `None`: use all MT)

        Returns
        -------
        `sandy.formats.endf6.BaseFile` or derived instance
            Copy of the original instance with filtered MAT, MF and MT sections
        """
        series = self.to_series()
        cond_mat = series.index.get_level_values("MAT").isin(listmat)
        cond_mf = series.index.get_level_values("MF").isin(listmf)
        cond_mt = series.index.get_level_values("MT").isin(listmt)
        d = series.loc[cond_mat & cond_mf & cond_mt].to_dict()
        return self.__class__(d, file=self.file)

    def get_value(self, mat, mf, mt, line_number, pos):
        return self._get_section_df(mat, mf, mt)[pos.upper()] \
                   .iloc[line_number - 1]

    def change_value(self, val, mat, mf, mt, line_number, pos, inplace=False,
                     dtype=float):
        items = ("C1", "C2", "L1", "L2", "N1", "N2")
        positions = {y: x for x, y in enumerate(items)}
        step = positions[pos]
        length = 81
        ibeg = length * (line_number - 1) + 11 * step
        iend = length * (line_number - 1) + 11 * (step + 1)
        text = self.data[(mat, mf, mt)]
        new = sandy.write_int(val) if dtype is int else sandy.write_float(val)
        new_text = "".join((text[:ibeg], new, text[iend:]))
        new_tape = self.add_section(mat, mf, mt, new_text, inplace=False)
        if inplace:
            self.data = new_tape.data
        else:
            return new_tape
        print(new_text)

    @classmethod
    def _from_old_format(cls, old_endf6):
        """
        Convert old endf6 tape into new one!
        """
        return cls(old_endf6.TEXT.to_dict())


class Endf6(_FormattedFile):
    """
    Container for ENDF-6 file text grouped by MAT, MF and MT numbers.

    Methods
    -------
    read_section
        Parse MAT/MF/MT section.
    write_string
        Write ENDF-6 content to string.
    """

    def _get_nsub(self):
        """
        Determine ENDF-6 sub-library type by reading flag "NSUB" of first MAT
        in file:

            * `NSUB = 10` : Incident-Neutron Data
            * `NSUB = 11` : Neutron-Induced Fission Product Yields

        Returns
        -------
        `int`
            NSUB value
        """
        return self.read_section(self.mat[0], 1, 451)["NSUB"]

    def read_section(self, mat, mf, mt, raise_error=True):
        """
        Parse MAT/MF/MT section.

        Parameters
        ----------
        `mat` : int
            MAT number
        `mf` : int
            MF number
        `mt` : int
            MT number

        Returns
        -------
        `dict`
        """
        read_module = f"read_mf{mf}"
        found = hasattr(sandy, read_module)
        if not raise_error and not found:
            return
        foo = eval(f"sandy.{read_module}")
        return foo(self, mat, mt)

    def write_string(self, title="", skip_title=False, skip_fend=False):
        """
        .. warning:: OUTDATED, use `to_file`.
        """
        string = sandy.write_line(title, 1, 0, 0, 0)
        string += "\n"
        for mat, dfmat in self.to_series().groupby('MAT', sort=True):
            for mf, dfmf in dfmat.groupby('MF', sort=True):
                for mt, text in dfmf.groupby('MT', sort=True):
                    string += text.squeeze()\
                                  .encode('ascii', 'replace')\
                                  .decode('ascii')
                    string += "\n"
                    string += sandy.write_line("", mat, mf, 0, 99999)
                    string += "\n"
                string += sandy.write_line("", mat, 0, 0, 0)
                string += "\n"
            string += sandy.write_line("", 0, 0, 0, 0)
            string += "\n"
        string += sandy.write_line("", -1, 0, 0, 0)
        return string

    def to_string(self, title="", skip_title=False, skip_fend=False):
        """
        Write `Endf6.data` content to string according to the ENDF-6 file
        rules.

        Parameters
        ----------
        title : `str`, optional, default is an empty string
            first line of the file

        Returns
        -------
        `str`
            string containing the ENDF-6 information stored in this instance.

        Notes
        -----
        ..note:: no modification is implemented to the actual content of
                 the `Endf6.data` object.

        Examples
        --------
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> string = sandy.Endf6.from_file(file).write_string()
        >>> print(string[:81 * 4 - 1])
                                                                             1 0  0    0
         1.001000+3 9.991673-1          0          0          2          5 125 1451    1
         0.000000+0 0.000000+0          0          0          0          6 125 1451    2
         1.000000+0 2.000000+7          3          0         10          3 125 1451    3

        if no modification is applied to the `Endf6` content, the
        `write_string` returns an output identical to the file ASCII content.
        >>> assert string == open(file).read()

        ..note:: differences might appear from the way zeros were handled at
                 the end of ENDF-6 section, or if a different fiel title is
                 given
        """
        string = sandy.write_line(title, 1, 0, 0, 0)
        string += "\n"
        for mat, dfmat in self.to_series().groupby('MAT', sort=True):
            for mf, dfmf in dfmat.groupby('MF', sort=True):
                for mt, text in dfmf.groupby('MT', sort=True):
                    string += text.squeeze()\
                                  .encode('ascii', 'replace')\
                                  .decode('ascii')
                    string += "\n"
                    string += sandy.write_line("", mat, mf, 0, 99999)
                    string += "\n"
                string += sandy.write_line("", mat, 0, 0, 0)
                string += "\n"
            string += sandy.write_line("", 0, 0, 0, 0)
            string += "\n"
        string += sandy.write_line("", -1, 0, 0, 0)
        return string

    def to_file(self, filename, mode="w", **kwargs):
        text = self.write_string(**kwargs)
        with open(filename, mode) as f:
            f.write(text)

    def _update_info(self, descr=None):
        """Update RECORDS item (in DATA column) for MF1/MT451 of each MAT based on the content of the TEXT column.
        """
        from .mf1 import write
        tape = self.copy()
        for mat in sorted(tape.index.get_level_values('MAT').unique()):
            sec = self.read_section(mat,1,451)
            records = pd.DataFrame(sec["RECORDS"], columns=["MF","MT","NC","MOD"]).set_index(["MF","MT"])
            new_records = []
            dfmat=tape.loc[mat]
#            for (mf,mt),text in sorted(tape.loc[mat].query('MT!=451'.format(mat)).TEXT.items()):
            for (mf,mt),text in sorted(dfmat[dfmat.index.get_level_values("MT")!=451].TEXT.items()):
                nc = len(text.splitlines())
                # when copying PENDF sections (MF2/MT152) mod is not present in the dictionary
                try:
                    mod = records.MOD.loc[mf,mt]
                except:
                    mod = 0
                new_records.append((mf,mt,nc,mod))
            if descr is not None:
                sec["TEXT"] = descr
            nc = 4 + len(sec["TEXT"]) + len(new_records) + 1
            mod = records.MOD.loc[1,451]
            new_records = [(1,451,nc,mod)] + new_records
            sec["RECORDS"] = new_records
            text = write(sec)
            tape.loc[mat,1,451].TEXT = text
        return Endf6(tape)

    def parse(self):
        mats = self.index.get_level_values("MAT").unique()
        if len(mats) > 1:
            raise NotImplementedError("file contains more than 1 MAT")
        self.mat = self.endf = mats[0]
        if hasattr(self, "tape"):
            self.filename = os.path.basename(self.tape)
        INFO = self.read_section(mats[0], 1 ,451)
        del INFO["TEXT"], INFO["RECORDS"]
        self.__dict__.update(**INFO)
        self.SECTIONS = self.loc[INFO["MAT"]].reset_index()["MF"].unique()
        self.EHRES = 0
        self.THNMAX = - self.EHRES if self.EHRES != 0 else 1.0E6

    def get_ace(self,
                temperature,
                njoy=None,
                verbose=False,
                pendf=None,
                **kwargs,
                ):
        """
        Process `Endf6` instance into an ACE file using NJOY.

        Parameters
        ----------
        temperature : `float`
            temperature of the cross sections in K.
        njoy : `str`, optional, default is `None`
            NJOY executable, if `None` search in the system path.
        verbose : TYPE, optional, default is `False`
            flag to print NJOY input file to screen before running the
            executable.
        **kwargs : TYPE
            keyword argument to pass to `sandy.njoy.process`.

        Returns
        -------
        outs : `dict`
            output with `'ace'` and `'xsdir'` as keys pointing to the
            filenames of the corresponding ACE and xsdir files generated in
            the run.

        Examples
        --------
        >>> sandy.get_endf6_file("jeff_33", "xs", 10010).get_ace(700)
        {'ace': '1001.07c', 'xsdir': '1001.07c.xsd'}
        """
        outs = {}
        pendftape = None
        with TemporaryDirectory() as td:
            endf6file = os.path.join(td, "endf6_file")
            self.to_file(endf6file)
            if pendf:
                pendftape = os.path.join(td, "pendf_file")
                pendf.to_file(pendftape)
            text, inputs, outputs = sandy.njoy.process(
                endf6file,
                pendftape=pendftape,
                wdir=".",
                keep_pendf=False,
                exe=njoy,
                temperatures=[temperature],
                verbose=verbose,
                **kwargs,
                )
            acefile = outputs["tape50"]
            basename = os.path.split(acefile)[1]
            dest = os.path.join(os.getcwd(), basename)
            outs["ace"] = basename
            shutil.move(acefile, dest)
            xsdfile = outputs["tape70"]
            basename = os.path.split(xsdfile)[1]
            dest = os.path.join(os.getcwd(), basename)
            outs["xsdir"] = basename
            shutil.move(xsdfile, dest)
        return outs

    def get_pendf(self,
                  temperature=0,
                  njoy=None,
                  to_file=False,
                  verbose=False,
                  **kwargs,
                  ):
        """
        Process `Endf6` instance into an PENDF file using NJOY.

        Parameters
        ----------
        temperature : `float`, optional, default is `0`.
            temperature of the cross sections in K.
            If not given, stop the processing after RECONR (before BROADR).
        njoy : `str`, optional, default is `None`
            NJOY executable, if `None` search in the system path.
        to_file : `bool`, optional, default is `False`
            flag to write processed PENDF data to file.
            The name of the PENDF file is defined by an internal routine.
        verbose : `bool`, optional, default is `False`
            flag to print NJOY input file to screen before running the
            executable.
        **kwargs : `dict`
            keyword argument to pass to `sandy.njoy.process`.

        Returns
        -------
        pendf : `sandy.Endf6`
            `Endf6` instance constaining the nuclear data of the PENDF file.

        Examples
        --------
        Process H1 file from ENDF/B-VII.1 into PENDF
        >>> pendf =sandy.get_endf6_file("endfb_71", "xs", 10010).get_pendf(verbose=True)
        moder
        20 -21 /
        reconr
        -21 -22 /
        'sandy runs njoy'/
        125 0 0 /
        0.001 0. /
        0/
        moder
        -22 30 /
        stop

        >>> pendf
        MAT  MF  MT 
        125  1   451     1.001000+3 9.991673-1          2          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0         99  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object

        >>> pendf.kind
        'pendf'
        """
        if float(temperature) == 0:
            kwargs["broadr"] = False
            kwargs["thermr"] = False
            kwargs["gaspr"] = False
            kwargs["heatr"] = False
            kwargs["purr"] = False
            kwargs["unresr"] = False
            msg = """Zero or no temperature was requested, NJOY processing will stop after RECONR.
If you want to process 0K cross sections use `temperature=0.1`.
"""
            logging.info(msg)
        with TemporaryDirectory() as td:
            endf6file = os.path.join(td, "endf6_file")
            self.to_file(endf6file)
            text, inputs, outputs = sandy.njoy.process(
                endf6file,
                acer=False,
                keep_pendf=True,
                exe=njoy,
                temperatures=[temperature],
                suffixes=[0],
                verbose=verbose,
                **kwargs,
                )
            pendffile = outputs["tape30"]
            if to_file:
                basename = os.path.split(pendffile)[1]
                dest = os.path.join(os.getcwd(), basename)
                shutil.move(pendffile, dest)
            pendf = Endf6.from_file(pendffile)
        return pendf

    def merge_pendf(self, pendf):
        """
        Merge endf-6 file content with that of a pendf file.

        Parameters
        ----------
        pendf : `sandy.Endf6`
            `Endf6` object containing pendf tape.

        Returns
        -------
        `sandy.Endf6`
            `Endf6` object with MF3 and MF1MT451 from PENDF

        Notes
        -----
        .. note:: the `Endf6` object in output has attribute `kind='pendf'`.

        .. note:: the `Endf6` object in output contains all sections from the
                  original endf-6 file, but for all MF=3 and MF=1 MT=451.

        Examples
        --------
        >>> file = os.path.join(sandy.data.__path__[0], "h1.endf")
        >>> endf6 = sandy.Endf6.from_file(file)
        >>> file = os.path.join(sandy.data.__path__[0], "h1.pendf")
        >>> pendf = sandy.Endf6.from_file(file)
        >>> merged = endf6.merge_pendf(pendf)
        >>> merged
        MAT  MF  MT
        125  1   451     1.001000+3 9.991673-1          2          0  ...
             2   151     1.001000+3 9.991673-1          0          0  ...
             3   1       1.001000+3 9.991673-1          0         99  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
             4   2       1.001000+3 9.991673-1          0          1  ...
             6   102     1.001000+3 9.991673-1          0          2  ...
             33  1       1.001000+3 9.991673-1          0          0  ...
                 2       1.001000+3 9.991673-1          0          0  ...
                 102     1.001000+3 9.991673-1          0          0  ...
        dtype: object

        The cross section in the merged file come from the pendf.
        >>> assert merged.data[125, 3, 1] == pendf.data[125, 3, 1]
        >>> assert merged.data[125, 3, 1] != endf6.data[125, 3, 1]

        The new file is also a pendf.
        >>> merged.kind
        'pendf'
        """
        if pendf.kind != "pendf":
            raise sandy.Error("given file is not a pendf")
        section_3_endf6 = self.filter_by(listmf=[3]).data
        section_3_pendf = pendf.filter_by(listmf=[3]).data
        section_1451_pendf = pendf.filter_by(listmf=[1], listmt=[451]).data
        return self.delete_sections(section_3_endf6) \
                   .add_sections(section_3_pendf) \
                   .add_sections(section_1451_pendf)

    def get_errorr(self,
                   temperature=0,
                   njoy=None,
                   to_file=False,
                   verbose=False,
                   err=0.005,
                   **kwargs,
                   ):
        """
        Process `Endf6` instance into a Errorr file using NJOY.

        Parameters
        ----------
        temperature : `float`, optional, default is `0`.
            temperature of the cross sections in K.
            If not given, stop the processing after RECONR (before BROADR).
        njoy : `str`, optional, default is `None`
            NJOY executable, if `None` search in the system path.
        to_file : `bool`, optional, default is `False`
            flag to write processed PENDF data to file.
            The name of the PENDF file is defined by an internal routine.
        verbose : `bool`, optional, default is `False`
            flag to print NJOY input file to screen before running the
            executable.
        **kwargs : `dict`
            keyword argument to pass to `sandy.njoy.process`.

        Parameters for RECONR
        ---------------------
        err : `float`, optional
            reconstruction tolerance (default is 0.005)

        Parameters for ERRORR
        ---------------------
        ign : `int`, optional
            neutron group option (default is 2, csewg 239-group structure)
        ek : iterable, optional
            derived cross section energy bounds (default is `[1e-5, 2e7]`)
        iwt : `int`, optional
            weight function option (default is 2, constant)

        Returns
        -------
        errorr : `sandy.Errorr`
            `Errorr` instance constaining the nuclear data of the ERRORR file.

        .. important:: this module uses `read_formatted_file`, which is no
                       longer supported.

        Notes
        -----
        .. note:: method arguments are consistent with those of `get_pendf`.
                      

        Examples
        --------
        Test verbose keyword
        >>> endf6 = sandy.get_endf6_file("jeff_33", "xs", 10010)
        >>> out = endf6.get_errorr(ign=1, ek=sandy.energy_grids.CASMO12, verbose=True)
        moder
        20 -21 /
        reconr
        -21 -22 /
        'sandy runs njoy'/
        125 0 0 /
        0.005 0. /
        0/
        moder
        -22 30 /
        errorr
        -21 -22 0 33 0 /
        125 1 2 0 1 /
        0 0.0 /
        0 33 /
        12 /
        1.00000e-05 3.00000e-02 5.80000e-02 1.40000e-01 2.80000e-01 3.50000e-01 6.25000e-01 4.00000e+00 4.80520e+01 5.53000e+03 8.21000e+05 2.23100e+06 1.00000e+07 /
        stop
        
        Test output type
        >>> assert isinstance(out, sandy.Errorr)

        Test ign and ek
        >>> assert out.get_xs(125, 1).size == 12
        """
        if float(temperature) == 0:
            kwargs["broadr"] = False
            kwargs["thermr"] = False
            kwargs["gaspr"] = False
            kwargs["heatr"] = False
            kwargs["purr"] = False
            kwargs["unresr"] = False
        with TemporaryDirectory() as td:
            endf6file = os.path.join(td, "endf6_file")
            self.to_file(endf6file)
            outputs = sandy.njoy.process(
                    endf6file,
                    errorr=True,
                    acer=False,
                    verbose=verbose,
                    temperatures=[temperature],
                    suffixes=[0],
                    err=0.005,
                    **kwargs,
                    )[2]  # keep only pendf filename
            errorrfile = outputs["tape33"]
            if to_file:
                basename = os.path.split(errorrfile)[1]
                dest = os.path.join(os.getcwd(), basename)
                shutil.move(errorrfile, dest)
            errorr = sandy.Errorr.from_file(errorrfile)
        return errorr
