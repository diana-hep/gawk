import rejig.pybytecode

def testme():
    return x[1, 2]

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
