import rejig.pybytecode

def testme():
    return 1 < y < 2

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
