import rejig.pybytecode

def testme():
    return f(g, x=1, y=z)

print(rejig.pybytecode.BytecodeWalker(testme).ast().dump())
