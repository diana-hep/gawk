import rejig.pybytecode

def testme(x):
    {1: 1, 2: 2}

print(rejig.pybytecode.ast(testme).dump())
