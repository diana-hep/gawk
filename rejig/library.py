import collections
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

import numpy

import awkward.type

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

    def __iter__(self):
        return iter(self.types)

    def __len__(self):
        return len(self.types)

root = SymbolTable(None)

root["pi"] = numpy.dtype(float)

class Function(object):
    def infer(self, call):
        return None

class Add(Function):
    def args(self, args, kwargs):
        return collections.OrderedDict((str(i), x) for i in enumerate(args))

    def infer(self, args):
        if all(isinstance(x.type, numpy.dtype) and issubclass(x.type.type, numpy.number) for x in args):
            return rejig.typedast.numerical(*[x.type for x in args])
        else:
            return None

root["+"] = Add()

# class Method(object):
#     def typify(self, call):
        
#         return self.base(dot.args[0]) and self.args(dot.args[1:])

#         return None

# class ArrayMap(Method):
#     def typify(self, call):
#         pass
