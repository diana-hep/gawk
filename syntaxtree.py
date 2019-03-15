class AST(object):
    def __init__(self, name, *params, linestart=None):
        self.name = name
        self.params = params
        self.linestart = linestart

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name and self.params == other.params

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((type(self), self.name, self.params))

class Const(AST):
    def __init__(self, value, linestart=None):
        super(Const, self).__init__(value, linestart=linestart)

class Call(AST):
    pass

class Def(AST):
    def __init__(self, argnames, body, linestart=None):
        super(Def, self).__init__("def", argnames, body, linestart=linestart)

class Assign(AST):
    def __init__(self, target, expr, linestart=None):
        super(Assign, self).__init__("assign", target, expr, linestart=linestart)

class Builder(object):
    def __init__(self):
        self.out = None
