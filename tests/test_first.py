import rejig.pybytecode

def testme():
    def g(): return 3.14
    return None

print(rejig.pybytecode.ast(testme).dump())
