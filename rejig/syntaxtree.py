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
    def dump(self):
        return u"{0}({1})".format(self.id, u", ".join(x.dump() for x in self.params))

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
    def __init__(self, argnames, body, line=None):
        super(Def, self).__init__(Def, argnames, body, line=line)

    @property
    def argnames(self):
        return self.params[0]

    @property
    def body(self):
        return self.params[1]

    def dump(self):
        return u"({0}) \u2291 {1}".format(u", ".join(self.argnames), self.body.dump())

class Suite(AST):
    def __init__(self, body, line=None):
        super(Suite, self).__init__(Suite, *body, line=line)

    @property
    def body(self):
        return self.params

    def dump(self):
        return u"{{{0}}}".format(u"; ".join(x.dump() for x in self.body))

class Assign(AST):
    def __init__(self, target, expr, line=None):
        super(Assign, self).__init__(Assign, target, expr, line=line)

    @property
    def target(self):
        return self.params[0]

    @property
    def expr(self):
        return self.params[1]

    def dump(self):
        return u"{0} := {1}".format(self.target, self.expr.dump())
