import rejig.pybytecode

def testme(x):
    if x < 0:
        y = -1
        z = -1
    else:
        z = 2

print(rejig.pybytecode.ast(testme).dump())
