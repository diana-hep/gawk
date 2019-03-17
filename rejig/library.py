import collections

import numpy

import awkward.type

import rejig.syntaxtree
import rejig.typedast
import rejig.typing

root = rejig.typing.SymbolTable(None)

root["pi"] = numpy.dtype(float)

class Function(object):
    def infer(self, call):
        return None

class Add(Function):
    def __str__(self):
        return "+"

    def numargs(self, args):
        return len(args) >= 2

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict((str(i), x) for i, x in enumerate(typedargs))

    def infer(self, call, typedargs, symboltable):
        if all(isinstance(x.type, numpy.dtype) and issubclass(x.type.type, numpy.number) for x in typedargs):
            return rejig.typedast.Call(call, typedargs, rejig.typedast.numerical(*[x.type for x in typedargs]))
        else:
            return None

root["+"] = Add()

class ArrayMap(Function):
    def __init__(self, array):
        self.array = array

    def __str__(self):
        return ".map"

    def numargs(self, args):
        return len(args) == 1

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict([("mapper", typedargs[0])])

    def infer(self, call, typedargs, symboltable):
        if len(typedargs) == 1 and isinstance(typedargs[0], rejig.syntaxtree.Def) and len(typedargs[0].argnames) == 1:
            scope = rejig.typing.SymbolTable(symboltable)
            scope[typedargs[0].argnames[0]] = self.array.type.to
            typedbody = rejig.typing.typifystep(typedargs[0].body, scope)
            out = awkward.type.ArrayType(self.array.type.takes, typedbody.type)
            return rejig.typedast.Call(call, (typedbody,), out)

        else:
            return None

class Attrib(Function):
    def __str__(self):
        return "."

    def numargs(self, args):
        return len(args) == 2

    def typedargs(self, typedargs, kwargs):
        return collections.OrderedDict([("object", typedargs[0]), ("attribute", typedargs[1])])

    def infer(self, call, typedargs, symboltable):
        if isinstance(typedargs[0].type, awkward.type.ArrayType) and typedargs[1] == "size":
            if typedargs[0].type.takes == numpy.inf:
                return rejig.typedast.Call(call, typedargs, numpy.dtype(numpy.int64))
            else:
                return rejig.typedast.Const(rejig.syntaxtree.Const(typedargs[0].type.takes), numpy.dtype(numpy.int64))

        elif isinstance(typedargs[0].type, awkward.type.ArrayType) and typedargs[1] == "map":
            return ArrayMap(typedargs[0])

        else:
            return None

root["."] = Attrib()
