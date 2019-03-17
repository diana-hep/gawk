# import rejig.pybytecode

# def testme(x):
#     y = 1
#     z = 2
#     f([y**2 for x in something if x for y in x if y])
#     return f.a.b.c

# print(rejig.pybytecode.ast(testme))

import numpy

import awkward.type

import rejig.pybytecode
import rejig.typing

def testme(x):
    return x + 3.14

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"x": numpy.dtype(int)}))
print()

def testme(a):
    return a.size

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
print()

def testme(a):
    return a.map(lambda x: x + 3.14)

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
print()

def testme(a):
    return [x + 3.14 for x in a]

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
print()

def testme(a):
    return a.map(x + 3.14)

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
print()
