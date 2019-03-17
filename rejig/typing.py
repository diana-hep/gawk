import numpy

import rejig.syntaxtree
import rejig.typedast
import rejig.library

def typifystep(ast, symboltable):
    if isinstance(ast, rejig.syntaxtree.Call):
        if isinstance(ast.fcn, str):
            if symboltable[ast.fcn] is None:
                raise AssertionError("unrecognized builtin: {0}".format(ast.fcn))
            fcn = symboltable[ast.fcn]
        else:
            fcn = typifystep(ast.fcn, symboltable)

        args = [typifystep(x, symboltable) for x in ast.args]

        if not isinstance(fcn, rejig.library.Function):
            raise TypeError("not a function: {0}".format(str(fcn)))

        typ = fcn.infer(args)
        if typ is None:
            raise TypeError("illegal arguments{0}\n{1}".format(ast.errline(), rejig.typedast._typeargs(fcn.args(args, ()).items())))
        else:
            return rejig.typedast.typify(ast, typ)

    elif isinstance(ast, rejig.syntaxtree.Const):
        return rejig.typedast.typify(ast, numpy.dtype(type(ast.value)))

    elif isinstance(ast, rejig.syntaxtree.Name):
        if symboltable[ast.name] is None:
            raise TypeError("unrecognized name: {0}".format(repr(ast.name)))
        else:
            return rejig.typedast.typify(ast, symboltable[ast.name])

    else:
        raise NotImplementedError(type(ast))

def typify(ast, argtypes):
    symboltable = rejig.library.SymbolTable(rejig.library.root)
    for n, x in argtypes.items():
        symboltable[n] = x

    if isinstance(ast, rejig.syntaxtree.Suite):
        if len(ast.body) != 1:
            raise NotImplementedError

        if isinstance(ast.body[-1], rejig.syntaxtree.Call) and ast.body[-1].fcn == "return":
            return rejig.typedast.Action(typifystep(ast.body[-1].args[0], symboltable), argtypes)

    else:
        raise AssertionError(type(ast))
