import rejig.pybytecode

def testme():
    return x + 5 + y

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
