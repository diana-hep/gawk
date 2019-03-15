import importlib

import uncompyle6

import walker
importlib.reload(walker)

uncompyle6.code_deparse((lambda: 5).__code__, walker=walker.Walker)
