# import rejig.pybytecode

# def testme(x):
#     y = 1
#     z = 2
#     f([y**2 for x in something if x for y in x if y])
#     return f.a.b.c

# print(rejig.pybytecode.ast(testme))

import numpy

import rejig.pybytecode
import rejig.typing

def testme(x, y):
    return x + 3.14

print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"x": numpy.dtype(int), "y": numpy.dtype(float)}))
