import importlib

import uncompyle6

import makeast
importlib.reload(makeast)

uncompyle6.code_deparse((lambda: 5).__code__, walker=makeast.MakeAST)
