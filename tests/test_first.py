import rejig.pybytecode

def testme():
    return []

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
