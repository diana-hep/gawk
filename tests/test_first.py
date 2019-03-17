import rejig.pybytecode

def testme(x):
    y = 1
    z = 2
    f(y**2 for x in something if x for y in x if y)
    return f.a.b.c

print(rejig.pybytecode.ast(testme).dump())
