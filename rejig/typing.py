try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

import numpy

import rejig.syntaxtree
import rejig.typedast

class SymbolTable(MutableMapping):
    def __init__(self, parent):
        self.parent = parent
        self.types = {}

    def __getitem__(self, symbol):
        if symbol in self.types:
            return self.types[symbol]
        elif self.parent is not None:
            return self.parent[symbol]
        else:
            return None

    def __setitem__(self, symbol, type):
        self.types[symbol] = type

    def __delitem__(self, symbol):
        del self.types[symbol]

    def __contains__(self, symbol):
        if symbol in self.types:
            return True
        elif self.parent is not None:
            return self.parent.__contains__(symbol)
        else:
            return False

    def __iter__(self):
        return iter(self.types)

    def __len__(self):
        return len(self.types)

def _indent(x):
    return "           " + x.replace("\n", "\n           ")

def tofcn(fcnarg, ast, symboltable):
    if isinstance(fcnarg, int):
        argnames = list(ast.firstnames(fcnarg, symboltable))

        yes = [x for x in argnames if x.startswith("_")]
        no = [x for x in argnames if not x.startswith("_")]

        yes = sorted(x[1:] for x in yes)
        argnames = yes + no

        return rejig.syntaxtree.Def(argnames, (), rejig.syntaxtree.Suite((rejig.syntaxtree.Call("return", ast, sourcepath=ast.sourcepath, linestart=ast.linestart),), sourcepath=ast.sourcepath, linestart=ast.linestart), sourcepath=ast.sourcepath, linestart=ast.linestart)

    else:
        raise AssertionError(fcnarg)

def typifystep(ast, symboltable):
    import rejig.library

    if isinstance(ast, rejig.syntaxtree.Suite):
        if len(ast.body) != 1:
            raise NotImplementedError

        if isinstance(ast.body[-1], rejig.syntaxtree.Call) and ast.body[-1].fcn == "return":
            return typifystep(ast.body[-1].args[0], symboltable)

        raise AssertionError(type(ast))

    elif isinstance(ast, rejig.syntaxtree.Call):
        if isinstance(ast.fcn, str):
            if symboltable[ast.fcn] is None:
                raise AssertionError("unrecognized builtin: {0}".format(ast.fcn))
            fcn = symboltable[ast.fcn]
        else:
            fcn = typifystep(ast.fcn, symboltable)

        if not isinstance(fcn, rejig.library.Function):
            raise TypeError("not a function{0}\n{1}".format(ast.errline(), _indent(str(fcn))))

        if not fcn.numargs(ast.args):
            raise TypeError("wrong number of arguments{0}\n{1}\n{2}".format(ast.errline(), _indent("function: " + str(fcn)), _indent(rejig.typedast._typeargs([(str(i), x) for i, x in enumerate(ast.args)]))))

        typedargs = []
        for i, x in enumerate(ast.args):
            fcnarg = fcn.fcnarg(i)
            if fcnarg is not None and not isinstance(x, rejig.syntaxtree.Def):
                typedargs.append(tofcn(fcnarg, x, symboltable))
            elif isinstance(x, str):
                typedargs.append(x)
            else:
                typedargs.append(typifystep(x, symboltable))

        out = fcn.infer(ast, typedargs, symboltable)
        if out is None:
            raise TypeError("wrong argument type(s){0}\n{1}\n{2}".format(ast.errline(), _indent("function: " + str(fcn)), _indent(rejig.typedast._typeargs(fcn.typedargs(typedargs, ()).items()))))
        else:
            return out

    elif isinstance(ast, rejig.syntaxtree.Const):
        return rejig.typedast.Const(ast, numpy.dtype(type(ast.value)))

    elif isinstance(ast, rejig.syntaxtree.Name):
        if symboltable[ast.name] is None:
            raise TypeError("unrecognized name{0}\n{1}".format(ast.errline(), _indent("name: " + str(ast.name))))
        else:
            return rejig.typedast.Name(ast, symboltable[ast.name])

    elif isinstance(ast, rejig.syntaxtree.Def):
        return ast

    else:
        raise NotImplementedError(type(ast))

def typify(ast, argtypes):
    import rejig.library

    symboltable = SymbolTable(rejig.library.root)
    for n, x in argtypes.items():
        symboltable[n] = x

    return rejig.typedast.Action(typifystep(ast, symboltable), argtypes)
