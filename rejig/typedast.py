import numpy

import awkward.type

import rejig.syntaxtree

def _typestr(x, indent):
    if isinstance(x, awkward.type.Type):
        return x.__str__(indent=indent).strip()
    else:
        return str(x)

def _typeargs(pairs):
    width = max(len(x) for x, y in pairs)
    formatter = "{0:>%ds}: {1}" % width
    indent = " " * width
    return "\n".join(formatter.format(n, _typestr(x, indent)) for n, x in pairs)

class Action(object):
    def __init__(self, ast, argtypes):
        self.ast = ast
        self.argtypes = argtypes

    def __repr__(self):
        return "<Action {0} from {1}>".format(repr(self.ast), repr(self.argtypes))

    def __str__(self):
        return str(self.ast.ast) + "\n" + _typeargs(list(self.argtypes.items()) + [("", self.ast.type)])

def typify(ast, type):
    if isinstance(ast, rejig.syntaxtree.Call):
        return Call(ast, type)
    elif isinstance(ast, rejig.syntaxtree.Const):
        return Const(ast, type)
    elif isinstance(ast, rejig.syntaxtree.Name):
        return Name(ast, type)
    else:
        raise AssertionError(type(ast))

class AST(object):
    def __init__(self, ast, type):
        self.ast = ast
        self.type = type

    def __eq__(self, other):
        return type(self) == type(other) and self.ast == other.ast and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((type(self), self.ast, self.type))

    @property
    def id(self):
        return self.ast.id

    @property
    def params(self):
        return self.ast.params

    @property
    def sourcepath(self):
        return self.ast.sourcepath

    @property
    def linestart(self):
        return self.ast.linestart

    def errline(self):
        return self.ast.errline()

    def __repr__(self):
        return "<{0} of type {1}>".format(repr(self.ast), repr(self.type))

    def __str__(self):
        value = str(self.ast)
        return "{0} of type {1}".format(value, _typestr(self.type, " " * (len(value) + 9)))
    
class Call(AST):
    @property
    def fcn(self):
        return self.ast.fcn

    @property
    def args(self):
        return self.ast.args

class Const(AST):
    @property
    def value(self):
        return self.params[0]

class Name(AST):
    @property
    def name(self):
        return self.params[0]

def numerical(*types):
    assert all(isinstance(x, numpy.dtype) for x in types)

    if len(types) == 0:
        return None

    elif len(types) == 1:
        return types[0]

    elif len(types) == 2:
        x, y = types
        if issubclass(x.type, (numpy.bool, numpy.bool_)) and issubclass(y.type, (numpy.bool, numpy.bool_)):
            return x

        elif issubclass(x.type, numpy.integer) and issubclass(y.type, numpy.integer):
            minval = min(numpy.iinfo(x.type).min, numpy.iinfo(y.type).min)
            maxval = max(numpy.iinfo(x.type).max, numpy.iinfo(y.type).max)
            for out in (numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64, numpy.int8, numpy.int16, numpy.int32, numpy.int64):
                if numpy.iinfo(out).min <= minval and numpy.iinfo(out).max >= maxval:
                    return numpy.dtype(out)
            else:
                return numpy.dtype(numpy.float64)

        elif issubclass(x.type, (numpy.integer, numpy.floating)) and issubclass(y.type, (numpy.integer, numpy.floating)):
            if issubclass(x.type, (numpy.uint8, numpy.int8, numpy.float16)):
                xprec = 16
            elif issubclass(x.type, (numpy.uint16, numpy.int16, numpy.float32)):
                xprec = 32
            elif issubclass(x.type, (numpy.uint32, numpy.int32, numpy.uint64, numpy.int64, numpy.float64)):   # concession to convenience
                xprec = 64
            elif issubclass(x.type, numpy.float128):   # to be avoided unless necessary
                xprec = 128
            else:
                raise AssertionError(x.type)
            if issubclass(y.type, (numpy.uint8, numpy.int8, numpy.float16)):
                yprec = 16
            elif issubclass(y.type, (numpy.uint16, numpy.int16, numpy.float32)):
                yprec = 32
            elif issubclass(y.type, (numpy.uint32, numpy.int32, numpy.uint64, numpy.int64, numpy.float64)):   # concession to convenience
                yprec = 64
            elif issubclass(y.type, numpy.float128):   # to be avoided unless necessary
                yprec = 128
            else:
                raise AssertionError(y.type)
            prec = max(xprec, yprec)
            if prec == 16:
                return numpy.dtype(numpy.float16)
            elif prec == 32:
                return numpy.dtype(numpy.float32)
            elif prec == 64:
                return numpy.dtype(numpy.float64)
            elif prec == 128:
                return numpy.dtype(numpy.float128)

        elif issubclass(x.type, (numpy.integer, numpy.complexfloating)) and issubclass(y.type, (numpy.integer, numpy.complexfloating)):
            if issubclass(x.type, (numpy.uint8, numpy.int8, numpy.uint16, numpy.int16, numpy.float32, numpy.complex64)):
                xprec = 64
            elif issubclass(x.type, (numpy.uint32, numpy.int32, numpy.uint64, numpy.int64, numpy.float64, numpy.complex128)):   # concession to convenience
                xprec = 128
            elif issubclass(x.type, (numpy.float128, numpy.complex256)):   # to be avoided unless necessary
                xprec = 256
            else:
                raise AssertionError(x.type)
            if issubclass(y.type, (numpy.uint8, numpy.int8, numpy.uint16, numpy.int16, numpy.float32, numpy.complex64)):
                yprec = 64
            elif issubclass(y.type, (numpy.uint32, numpy.int32, numpy.uint64, numpy.int64, numpy.float64, numpy.complex128)):   # concession to convenience
                yprec = 128
            elif issubclass(y.type, (numpy.float128, numpy.complex256)):   # to be avoided unless necessary
                yprec = 256
            else:
                raise AssertionError(y.type)
            prec = max(xprec, yprec)
            if prec == 64:
                return numpy.dtype(numpy.complex64)
            elif prec == 128:
                return numpy.dtype(numpy.complex128)
            elif prec == 256:
                return numpy.dtype(numpy.complex256)

        else:
            return None
