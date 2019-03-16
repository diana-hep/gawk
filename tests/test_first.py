import rejig.pybytecode

def testme():
    x = ()

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
