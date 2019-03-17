class AST(object):
    def __init__(self, id, *params, sourcepath=None, linestart=None):
        self.id = id
        self.params = params
        self.sourcepath = sourcepath
        self.linestart = linestart

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id and self.params == other.params

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((type(self), self.id, self.params))

class Call(AST):
    def __init__(self, fcn, *args, sourcepath=None, linestart=None):
        super(Call, self).__init__(fcn, *args, sourcepath=sourcepath, linestart=linestart)

    @property
    def fcn(self):
        return self.id

    @property
    def args(self):
        return self.params

    @args.setter
    def args(self, value):
        self.params = value

    def __repr__(self):
        return "Call({0}, {1})".format(repr(self.fcn), ", ".join(repr(x) for x in self.args))

    def dump(self):
        return u"{0}({1})".format(self.fcn.dump() if isinstance(self.fcn, AST) else self.fcn, u", ".join(x.dump() if isinstance(x, AST) else repr(x) for x in self.args))

class CallKeyword(AST):
    def __init__(self, fcn, args, kwargs, sourcepath=None, linestart=None):
        super(CallKeyword, self).__init__(fcn, args, sorted(kwargs, key=lambda x: x[0]), sourcepath=sourcepath, linestart=linestart)

    @property
    def fcn(self):
        return self.id

    @property
    def args(self):
        return self.params[0]

    @property
    def kwargs(self):
        return self.params[1]

    def __repr__(self):
        return "CallKeyword({0}, ({1}), ({2}))".format(repr(self.fcn), " ".join(repr(x) + "," for x in self.args), " ".join(repr(x) + "," for x in self.kwargs))

    def dump(self):
        return u"{0}({1}, {2})".format(self.fcn.dump() if isinstance(self.fcn, AST) else self.fcn, u", ".join(x.dump() if isinstance(x, AST) else repr(x) for x in self.args), u", ".join("{0}={1}".format(n, x.dump()) if isinstance(x, AST) else repr(x) for n, x in self.kwargs))

class Const(AST):
    def __init__(self, value, sourcepath=None, linestart=None):
        super(Const, self).__init__(Const, value, sourcepath=sourcepath, linestart=linestart)

    @property
    def value(self):
        return self.params[0]

    def __repr__(self):
        return "Const({0})".format(repr(self.value))

    def dump(self):
        return repr(self.value)

class Name(AST):
    def __init__(self, name, sourcepath=None, linestart=None):
        super(Name, self).__init__(Name, name, sourcepath=sourcepath, linestart=linestart)

    @property
    def name(self):
        return self.params[0]

    def __repr__(self):
        return "Name({0})".format(repr(self.name))

    def dump(self):
        return self.name

class Def(AST):
    def __init__(self, argnames, defaults, body, sourcepath=None, linestart=None):
        super(Def, self).__init__(Def, argnames, defaults, body, sourcepath=sourcepath, linestart=linestart)

    @property
    def argnames(self):
        return self.params[0]

    @property
    def defaults(self):
        return self.params[1]

    @property
    def body(self):
        return self.params[2]

    def __repr__(self):
        return "Def(({0}), ({1}), ({2}))".format(" ".join(repr(x) + "," for x in self.argnames), " ".join(repr(x) + "," for x in self.defaults), " ".join(repr(x) + "," for x in self.body))

    def dump(self):
        if len(self.defaults) == 0:
            args = self.argnames
            kwargs = ()
        else:
            args = self.argnames[:-len(self.defaults)]
            kwargs = tuple(zip(self.argnames[-len(self.defaults):], self.defaults))
        if len(kwargs) == 0:
            return u"({0}) \u2192 {1}".format(u", ".join(args), self.body.dump())
        else:
            return u"({0}, {1}) \u2192 {2}".format(u", ".join(args), u", ".join("{0}={1}".format(n, x) for n, x in kwargs), self.body.dump())

class Suite(AST):
    def __init__(self, body, sourcepath=None, linestart=None):
        super(Suite, self).__init__(Suite, *body, sourcepath=sourcepath, linestart=linestart)

    @property
    def body(self):
        return self.params

    def __repr__(self):
        return "Suite(({0}))".format(" ".join(repr(x) + "," for x in self.body))

    def dump(self):
        return u"{{{0}}}".format(u"; ".join(x.dump() for x in self.body))

class Assign(AST):
    def __init__(self, targets, expr, sourcepath=None, linestart=None):
        super(Assign, self).__init__(Assign, targets, expr, sourcepath=sourcepath, linestart=linestart)

    @property
    def targets(self):
        return self.params[0]

    @property
    def expr(self):
        return self.params[1]

    def __repr__(self):
        return "Assign(({0}), {1})".format(" ".join(repr(x) + "," for x in self.targets), repr(self.expr))

    def dump(self):
        return u"{0} := {1}".format(u" := ".join(x.dump() for x in self.targets), self.expr.dump())

class Unpack(AST):
    def __init__(self, subtargets, sourcepath=None, linestart=None):
        super(Unpack, self).__init__(Unpack, *subtargets, sourcepath=sourcepath, linestart=linestart)

    @property
    def subtargets(self):
        return self.params

    def __repr__(self):
        return "Unpack(({0}))".format(" ".join(repr(x) + "," for x in self.subtargets))

    def dump(self):
        return u"({0})".format(u", ".join(x.dump() for x in self.subtargets))
