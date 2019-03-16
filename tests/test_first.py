import rejig.pybytecode

def testme(x):
    [x**2 for x, y in something]

print(rejig.pybytecode.ast(testme).dump())
