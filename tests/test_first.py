import rejig.pybytecode

def testme(x):
    f(x**2 for x in something if x > 0)

print(rejig.pybytecode.ast(testme).dump())
