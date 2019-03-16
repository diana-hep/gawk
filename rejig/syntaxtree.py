class AST(object):
    def __init__(self, id, *params, line=None):
        self.id = id
        self.params = params
        self.line = line

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id and self.params == other.params

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((type(self), self.id, self.params))

    def append(self, node):
        self.params = self.params + (node,)

class Call(AST):
    def __init__(self, fcn, *args, line=None):
        super(Call, self).__init__(fcn, *args, line=line)

    @property
    def fcn(self):
        return self.id

    @property
    def args(self):
        return self.params

    @args.setter
    def args(self, value):
        self.params = value

    def dump(self):
        return u"{0}({1})".format(self.fcn.dump() if isinstance(self.fcn, AST) else self.fcn, u", ".join(x.dump() if isinstance(x, AST) else x for x in self.args))

class CallKeyword(AST):
    def __init__(self, fcn, args, kwargs, line=None):
        super(CallKeyword, self).__init__(fcn, args, sorted(kwargs, key=lambda x: x[0]), line=line)

    @property
    def fcn(self):
        return self.id

    @property
    def args(self):
        return self.params[0]

    @property
    def kwargs(self):
        return self.params[1]

    def dump(self):
        return u"{0}({1}, {2})".format(self.fcn.dump() if isinstance(self.fcn, AST) else self.fcn, u", ".join(x.dump() if isinstance(x, AST) else x for x in self.args), u", ".join("{0}={1}".format(n, x.dump()) if isinstance(x, AST) else x for n, x in self.kwargs))

class Const(AST):
    def __init__(self, value, line=None):
        super(Const, self).__init__(Const, value, line=line)

    @property
    def value(self):
        return self.params[0]

    def dump(self):
        return repr(self.value)

class Name(AST):
    def __init__(self, name, line=None):
        super(Name, self).__init__(Name, name, line=line)

    @property
    def name(self):
        return self.params[0]

    def dump(self):
        return self.name

class Def(AST):
    def __init__(self, argnames, defaults, body, line=None):
        super(Def, self).__init__(Def, argnames, defaults, body, line=line)

    @property
    def argnames(self):
        return self.params[0]

    @property
    def defaults(self):
        return self.params[1]

    @property
    def body(self):
        return self.params[2]

    def dump(self):
        args = self.argnames[:-len(self.defaults)]
        kwargs = tuple(zip(self.argnames[-len(self.defaults):], self.defaults))
        if len(kwargs) == 0:
            return u"({0}) \u2192 {1}".format(u", ".join(args), self.body.dump())
        else:
            return u"({0}, {1}) \u2192 {2}".format(u", ".join(args), u", ".join("{0}={1}".format(n, x) for n, x in kwargs), self.body.dump())

class Suite(AST):
    def __init__(self, body, line=None):
        super(Suite, self).__init__(Suite, *body, line=line)

    @property
    def body(self):
        return self.params

    def dump(self):
        return u"{{{0}}}".format(u"; ".join(x.dump() for x in self.body))

class Assign(AST):
    def __init__(self, targets, expr, line=None):
        super(Assign, self).__init__(Assign, targets, expr, line=line)

    @property
    def targets(self):
        return self.params[0]

    @property
    def expr(self):
        return self.params[1]

    def dump(self):
        return u"{0} := {1}".format(u" := ".join(x.dump() for x in self.targets), self.expr.dump())

class Unpack(AST):
    def __init__(self, subtargets, line=None):
        super(Unpack, self).__init__(Unpack, *subtargets, line=line)

    @property
    def subtargets(self):
        return self.params

    def dump(self):
        return u"({0})".format(u", ".join(x.dump() for x in self.subtargets))
