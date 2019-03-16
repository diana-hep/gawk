import rejig.pybytecode

def testme(x):
    f(y**2 for x in something if x for y in x if y)

print(rejig.pybytecode.ast(testme).dump())
