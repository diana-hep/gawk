import os
os.chdir("..")

import rejig.pybytecode

import uncompyle6

def testme(x):
    if x < 0:
        y = -1
    elif x > 0:
        y = 1
    else:
        y = 0
    return y

uncompyle6.code_deparse(testme.__code__)
print()

print(rejig.pybytecode.ast(testme))
