import collections

import numpy

import awkward.type

import rejig.typedast
import rejig.typing

root = rejig.typing.SymbolTable(None)

root["pi"] = numpy.dtype(float)

class Function(object):
    def infer(self, call):
        return None
        
class Add(Function):
    def args(self, args, kwargs):
        return collections.OrderedDict((str(i), x) for i, x in enumerate(args))

    def infer(self, call, args, symboltable):
        if all(isinstance(x.type, numpy.dtype) and issubclass(x.type.type, numpy.number) for x in args):
            return rejig.typedast.typify(call, rejig.typedast.numerical(*[x.type for x in args]))
        else:
            return None

root["+"] = Add()

class Attrib(Function):
    def args(self, args, kwargs):
        return collections.OrderedDict([("object", args[0]), ("attribute", args[1])])

    def infer(self, call, args, symboltable):
        if isinstance(args[0].type, awkward.type.ArrayType) and args[1] == "size":
            return rejig.typedast.typify(call, numpy.dtype(numpy.int64))
        else:
            return None

root["."] = Attrib()
