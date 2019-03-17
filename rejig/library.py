import collections
import numbers

import numpy

import awkward.type

import rejig.syntaxtree
import rejig.typedast
import rejig.typing

root = rejig.typing.SymbolTable(None)

root["pi"] = numpy.dtype(float)

class Function(object):
    def fcnarg(self, i):
        return None

class Add(Function):
    def __str__(self):
        return "+"

    def numargs(self, args):
        return len(args) >= 2

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict((str(i), x) for i, x in enumerate(typedargs))

    def infer(self, call, typedfcn, typedargs, symboltable):
        if all(isinstance(x.rettype, numpy.dtype) and issubclass(x.rettype.type, numpy.number) for x in typedargs):
            return rejig.typedast.Call(call, rejig.typedast.numerical(*[x.rettype for x in typedargs]), typedfcn, typedargs)
        else:
            return None

    def interpreted(self, typedast):
        return lambda *args: sum(args)

    def vectorized(self, typedast):
        return numpy.add

    def fused(self, typedast):
        return lambda *args: "(" + " + ".join(args) + ")"

root["+"] = Add()

class ArrayMap(Function):
    def __init__(self, array):
        self.array = array

    def __str__(self):
        return ".map"

    def fcnarg(self, i):
        if i == 0:
            return 1
        else:
            return None

    def numargs(self, args):
        return len(args) == 1

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict([("mapper", typedargs[0])])

    def infer(self, call, typedfcn, typedargs, symboltable):
        if len(typedargs) == 1 and isinstance(typedargs[0], rejig.syntaxtree.Def) and len(typedargs[0].argnames) == 1:
            scope = rejig.typing.SymbolTable(symboltable)
            scope[typedargs[0].argnames[0]] = self.array.rettype.to
            typedbody = rejig.typing.typifystep(typedargs[0].body, scope)
            rettype = awkward.type.ArrayType(self.array.rettype.takes, typedbody.rettype)
            defn = rejig.typedast.Def(call.args[0], typedbody.rettype, (self.array.rettype.to,), typedbody)
            return rejig.typedast.Call(call, rettype, typedfcn, (defn,))

        else:
            return None

    def interpreted(self, typedast):
        return lambda array, fcn: [fcn(x) for x in array]

    def vectorized(self, typedast):
        return lambda array, fcn: fcn(array)

    def fused(self, typedast):
        return lambda array, fcn: fcn(array)

class Attrib(Function):
    def __str__(self):
        return "."

    def numargs(self, args):
        return len(args) == 2

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict([("object", typedargs[0]), ("attribute", typedargs[1])])

    def infer(self, call, typedfcn, typedargs, symboltable):
        if isinstance(typedargs[0].rettype, awkward.type.ArrayType) and typedargs[1] == "size":
            if typedargs[0].rettype.takes == numpy.inf:
                return rejig.typedast.Call(call, numpy.dtype(numpy.int64), typedfcn, typedargs)
            else:
                return rejig.typedast.Const(rejig.syntaxtree.Const(typedargs[0].rettype.takes), numpy.dtype(numpy.int64))

        elif isinstance(typedargs[0].rettype, awkward.type.ArrayType) and typedargs[1] == "map":
            return ArrayMap(typedargs[0])

        else:
            return None

    def interpreted(self, typedast):
        return lambda obj, attr: getattr(obj, attr)

    def vectorized(self, typedast):
        raise TypeError

    def fused(self, typedast):
        raise TypeError

root["."] = Attrib()
