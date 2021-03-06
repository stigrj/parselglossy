#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2019 Roberto Di Remigio, Radovan Bast, and contributors.
#
# This file is part of parselglossy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# Roberto Di Remigio, and contributors. OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

# -*- coding: utf-8 -*-
"""Atoms."""

import functools
import json

import pyparsing as pp

truthy = ['TRUE', 'ON', 'YES', 'Y']
falsey = ['FALSE', 'OFF', 'NO', 'N']


def to_bool(token):
    defined = False
    if token[0] is None:
        defined = False
    elif token[0].upper() in falsey:
        defined = False
    elif token[0].upper() in truthy:
        defined = True
    else:
        defined = False

    return defined


bool_t = functools.reduce(lambda x, y: x ^ y,
                          map(pp.CaselessLiteral, truthy + falsey))
bool_t.setName('bool')
bool_t.setParseAction(to_bool)

int_t = pp.pyparsing_common.signed_integer
float_t = pp.Regex(r'[+-]?\d+\.?\d*([eE][+-]?\d+)?')
float_t.setName('float')
float_t.setParseAction(pp.tokenMap(float))

str_t = pp.quotedString.setParseAction(pp.removeQuotes) ^ pp.Word(pp.alphanums)
str_t.setName('str')
str_t.setParseAction(pp.tokenMap(str))


def to_complex(token):
    return complex(token[0], token[1]) if len(token) == 2 else complex(
        0.0, token[0])


I_unit = functools.reduce(lambda x, y: x ^ y,
                          map(pp.CaselessLiteral, ['*j', '*i'])).suppress()
complex_t = pp.OneOrMore(float_t | int_t) + I_unit
complex_t.setParseAction(to_complex)

num_t = complex_t | float_t | int_t
num_t.setName('numeric')

SDATA = pp.Literal('$').suppress()
EDATA = pp.CaselessLiteral('$end').suppress()
data_t = pp.Combine(SDATA + pp.Word(pp.alphas + '_', pp.alphanums + '_'))(
    'key') + pp.SkipTo(EDATA)('value') + EDATA
data_t.setName('raw data')
# Flatten to a key-value tuple
data_t.setParseAction(lambda token: (token['key'], token['value']))


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, complex):
            return {'__complex__': [obj.real, obj.imag]}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def as_complex(dct):
    if '__complex__' in dct:
        return complex(dct['__complex__'][0], dct['__complex__'][1])
    return dct
