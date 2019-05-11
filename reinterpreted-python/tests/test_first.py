import rejig.pybytecode

def testme(x):
    if x < 0:
        y = 0
    else:
        if x == 0:
            y = 1
        else:
            if x == 1:
                y = 2
            else:
                y = 3
    return "there"

print(rejig.pybytecode.ast(testme))

# import numpy

# import awkward.type

# import rejig.pybytecode
# import rejig.typing

# def testme(x):
#     return x + 3.14

# print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"x": numpy.dtype(int)}))
# print()

# def testme(a):
#     return a.size

# t = awkward.type.ArrayType(10, numpy.dtype(int))
# # t.takes = numpy.inf
# print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": t}))
# print()

# def testme(a):
#     return a.map(lambda x: x + 3.14)

# print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
# print()

# def testme(a):
#     return [x + 3.14 for x in a]

# print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
# print()

# def testme(a):
#     return a.map(x + 3.14)

# print(rejig.typing.typify(rejig.pybytecode.ast(testme), {"a": awkward.type.ArrayType(10, numpy.dtype(int))}))
# print()
