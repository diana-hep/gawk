#!/usr/bin/env python

import lark

grammar = """
start: NEWLINE* (statement (NEWLINE | ";"))* statement NEWLINE*

match:      "match" pattern+
pattern:    CNAME "=" expression constraint* -> intermediate
          | CNAME "in" expression constraint* -> terminal
constraint: "cut" expression -> cut | "fit" expression -> fit

statement:  assignment -> pass | funcassign -> pass
assignment: CNAME "=" (expression | match)
funcassign: CNAME "(" [CNAME ("," CNAME)*] ")" "=" block

expression: function   -> pass
function:   block      -> pass | paramlist "=>" block
block:      or         -> pass | "{" NEWLINE* (statement (NEWLINE | ";"))* expression NEWLINE* "}"

or:         and        -> pass | and "or" and
and:        not        -> pass | not "and" not
not:        comparison -> pass | "not" not
comparison: arith      -> pass | arith "==" arith -> eq | arith "!=" arith -> ne
                               | arith ">" arith -> gt  | arith ">=" arith -> ge
                               | arith "<" arith -> lt  | arith "<=" arith -> le

arith:   term          -> pass | term "+" arith  -> add | term "-" arith  -> sub
term:    factor        -> pass | factor "*" term -> mul | factor "/" term -> div
factor:  pow           -> pass | "+" factor      -> pos | "-" factor      -> neg
pow:     call          -> pass | call "**" factor
call:    atom          -> pass
    |    call "(" arglist ")"  | call "[" expression "]" -> subscript | call "." CNAME -> attribute

atom:    "(" expression ")" -> pass | CNAME -> symbol | INT -> int | FLOAT -> float

paramlist: "(" [CNAME ("," CNAME)*] ")" | CNAME
arglist:    expression ("," expression)*

%import common.CNAME
%import common.INT
%import common.FLOAT
%import common.NEWLINE
%import common.WS
%ignore WS
"""

parser = lark.Lark(grammar)

class AST:
    _fields = ()

    def __init__(self, *args, line=None):
        self.line = line
        assert len(self._fields) == len(args)
        for n, x in zip(self._fields, args):
            setattr(self, n, x)
            if self.line is None:
                self.line = getattr(x, "line", None)

    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, ", ".join(getattr(self, n) for n in self._fields))

class Literal(AST):
    _fields = ("value",)
    def __str__(self):
        return str(self.value)

class Symbol(AST):
    _fields = ("symbol",)
    def __str__(self):
        return self.symbol

class Call(AST):
    _fields = ("function", "arguments")
    def __str__(self):
        return "{0}({1})".format(str(self.function), ", ".join(str(x) for x in self.arguments))

class Subscript(AST):
    _fields = ("object", "index")
    def __str__(self):
        return "{0}[{1}]".format(str(self.object), str(self.index))

class Attribute(AST):
    _fields = ("object", "field")
    def __str__(self):
        return "{0}.{1}".format(str(self.object), self.field)

class Module(AST):
    _fields = ("statements",)
    def __str__(self):
        return "\n".join(str(x) for x in self.statements)

class Block(AST):
    _fields = ("statements", "expression")
    def __str__(self):
        return "{" + "; ".join(str(x) for x in self.statements + [self.expression]) + "}"

class Function(AST):
    _fields = ("parameters", "body")
    def __str__(self):
        left, right = ("", "") if len(self.parameters) == 1 else ("(", ")")
        return "{0}{1}{2} => {3}".format(left, ", ".join(self.parameters), right, str(self.body))

class Assignment(AST):
    _fields = ("symbol", "expression")
    def __str__(self):
        return "{0} = {1}".format(self.symbol, str(self.expression))

class Pattern(AST):
    _fields = ("symbol", "expression", "cuts", "fits", "terminal")
    def __str__(self):
        constraints = [" cut " + str(x) for x in self.cuts] + [" fit " + str(x) for x in self.fits]
        return "{0} {1} {2}{3}".format(self.symbol, "in" if self.terminal else "=", str(self.expression), "\n              ".join(constraints))

class Match(AST):
    _fields = ("patterns",)
    def __str__(self):
        return "\n    match " + "\n          ".join(str(x) for x in self.patterns)

class SymbolTable:
    def __init__(self, parent, symbols):
        self.parent = parent
        self.symbols = symbols

    def __contains__(self, symbol):
        if symbol in self.symbols:
            return True
        elif self.parent is not None:
            return symbol in self.parent
        else:
            return False

    def __getitem__(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif self.parent is not None:
            return self.parent[symbol]
        else:
            raise KeyError(symbol)

    def __setitem__(self, symbol, value):
        if symbol in self:
            raise TypeError("symbol {0} has multiple definitions".format(repr(symbol)))
        else:
            self.symbols[symbol] = value

opname = {
    "and": "and", "or": "or", "not": "not",
    "eq": "==", "ne": "!=", "gt": ">", "ge": ">=", "lt": "<", "le": "<=",
    "add": "+", "sub": "-", "mul": "*", "div": "/", "pos": "+", "neg": "-", "pow": "**"
    }

def toast(node):
    if node.data == "pass":
        return toast(node.children[0])
    elif node.data == "start":
        return Module([toast(x) for x in node.children if not isinstance(x, lark.lexer.Token)])
    elif node.data == "match":
        return Match([toast(x) for x in node.children])
    elif node.data == "intermediate" or node.data == "terminal":
        cuts = [toast(x.children[0]) for x in node.children[2:] if x.data == "cut"]
        fits = [toast(x.children[0]) for x in node.children[2:] if x.data == "fit"]
        return Pattern(str(node.children[0]), toast(node.children[1]), cuts, fits, node.data == "terminal")
    elif node.data == "assignment":
        return Assignment(str(node.children[0]), toast(node.children[1]))
    elif node.data == "funcassign":
        return Assignment(str(node.children[0]), Function(node.children[1:-1], toast(node.children[-1])))
    elif node.data == "function":
        return Function(toast(node.children[0]), toast(node.children[1]))
    elif node.data == "paramlist":
        return [str(x) for x in node.children]
    elif node.data == "block":
        items = [toast(x) for x in node.children if not isinstance(x, lark.lexer.Token)]
        if len(items) == 1:
            return items[0]
        else:
            return Block(items[:-1], items[-1])
    elif node.data == "call":
        return Call(toast(node.children[0]), toast(node.children[1]))
    elif node.data == "arglist":
        return [toast(x) for x in node.children]
    elif node.data == "subscript":
        return Subscript(toast(node.children[0]), toast(node.children[1]))
    elif node.data == "attribute":
        return Attribute(toast(node.children[0]), node.children[1])
    elif node.data == "symbol":
        return Symbol(node.children[0])
    elif node.data == "int":
        return Literal(int(node.children[0]))
    elif node.data == "float":
        return Literal(float(node.children[0]))
    elif node.data in opname:
        return Call(Symbol(opname[node.data]), [toast(x) for x in node.children])
    else:
        raise AssertionError(node.data)

print(toast(parser.parse("""
higgs =
    match h = z1 + z2 fit (h.mass - 125)**2
          z1 = mu1 + mu2
              cut mu1.charge != mu2.charge
              fit (z1.mass - 91)**2
          mu1 in muons
          mu2 in muons
          z2 = mu3 + mu4
              cut mu3.charge != mu4.charge
              fit (z2.mass - 91)**2
          mu3 in muons
          mu4 in muons
""")))

