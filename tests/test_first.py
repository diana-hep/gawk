import gawk.pybytecode

def testme():
    return x + 5 + y

print(gawk.pybytecode.BytecodeWalker(testme).ast().dump())
