# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 14:02:00 2018

@author: Luca Fiorito
"""

import pytest
import os

import numpy as np

import sandy

__author__ = "Luca Fiorito"




#@pytest.fixture(scope="module")
#def rdd1():
#    data = {
#        581480 : {'decay_constant': 0.01, 'decay_mode': {10: {'branching_ratio': 1.0, 'decay_products': {591480: 1.0}}}},
#        591480 : {'decay_constant': 0.05, 'decay_mode': {10: {'branching_ratio': 1.0, 'decay_products': {601480: 1.0}}}},
#        591481 : {'decay_constant': 0.06, 'decay_mode': {10: {'branching_ratio': 0.4, 'decay_products': {601480: 1.0, 10010: 2.0}},
#                                                         12: {'branching_ratio': 0.6, 'decay_products': {601470: 1.0}}
#                                                        }},
#        601480 : {'decay_constant': 0},
#        601470 : {'decay_constant': 0},
#        10010  : {'decay_constant': 0},
#        }
#    rdd = sandy.DecayData()
#    rdd.data = data
#    return rdd
#
#def test_get_decay_chains(rdd1):
#    DC = rdd1.get_decay_chains()
#    assert (DC[DC.PARENT == DC.DAUGHTER].YIELD == -1).all()
#    assert (DC[DC.PARENT == DC.DAUGHTER].BR == 1).all()
#    assert (DC[DC.PARENT==581480].LAMBDA == 0.01).all()
#    assert (DC[DC.PARENT==591480].LAMBDA == 0.05).all()
#    assert (DC[DC.PARENT==591481].LAMBDA == 0.06).all()
#    assert (DC[DC.PARENT==601480].LAMBDA == 0).all()
#    assert (DC[DC.PARENT==601470].LAMBDA == 0).all()
#    assert (DC[DC.PARENT==10010].LAMBDA == 0).all()
#    dec = DC[(DC.PARENT==581480) & (DC.DAUGHTER==591480)].iloc[0]
#    assert dec.YIELD == 1.0
#    assert dec.BR == 1.0
#    dec = DC[(DC.PARENT==591480) & (DC.DAUGHTER==601480)].iloc[0]
#    assert dec.YIELD == 1.0
#    assert dec.BR == 1.0
#    dec = DC[(DC.PARENT==591481) & (DC.DAUGHTER==601480)].iloc[0]
#    assert dec.YIELD == 1.0
#    assert dec.BR == 0.4
#    dec = DC[(DC.PARENT==591481) & (DC.DAUGHTER==10010)].iloc[0]
#    assert dec.YIELD == 2.0
#    assert dec.BR == 0.4
#    dec = DC[(DC.PARENT==591481) & (DC.DAUGHTER==601470)].iloc[0]
#    assert dec.YIELD == 1.0
#    assert dec.BR == 0.6
#    assert DC.PARENT.equals(DC.PARENT.sort_values())
#    
#def test_get_bmatrix(rdd1):
#    B = rdd1.get_bmatrix()
#    assert (B.values == np.array([
#       [0., 0., 0., 2., 0., 0.],
#       [0., 0., 0., 0., 0., 0.],
#       [0., 1., 0., 0., 0., 0.],
#       [0., 0., 0., 0., 0., 0.],
#       [0., 0., 0., 1., 0., 0.],
#       [0., 0., 1., 1., 0., 0.]])).all()
#    assert (B.index == sorted(rdd1.data.keys())).all()
#    assert (B.index == B.columns).all()
#
#def test_get_transition_matrix(rdd1):
#    T = rdd1.get_transition_matrix()
#    assert (T.values == np.array(
#      [[ 0.   ,  0.   ,  0.   ,  0.048,  0.   ,  0.   ],
#       [ 0.   , -0.01 ,  0.   ,  0.   ,  0.   ,  0.   ],
#       [ 0.   ,  0.01 , -0.05 ,  0.   ,  0.   ,  0.   ],
#       [ 0.   ,  0.   ,  0.   , -0.06 ,  0.   ,  0.   ],
#       [ 0.   ,  0.   ,  0.   ,  0.036,  0.   ,  0.   ],
#       [ 0.   ,  0.   ,  0.05 ,  0.024,  0.   ,  0.   ]])).all()
#    assert (T.index == sorted(rdd1.data.keys())).all()
#    assert (T.index == T.columns).all()