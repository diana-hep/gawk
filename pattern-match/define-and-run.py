#!/usr/bin/env python

import lark

grammar = """
start: NEWLINE* (statement (NEWLINE | ";"))* statement NEWLINE*

match:      "match" pattern+
pattern:    CNAME "=" expression constraint* -> intermediate
          | CNAME "in" expression constraint* -> terminal
constraint: "cut" expression -> cut | "fit" expression -> fit

statement:  assignment -> pass
assignment: CNAME "=" (expression | match)

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

atom:    "(" expression ")" -> pass | CNAME -> symbol | NUMBER -> literal

paramlist: "(" [CNAME ("," CNAME)*] ")" | CNAME
arglist:   expression ("," expression)*

%import common.CNAME
%import common.NUMBER
%import common.NEWLINE
%import common.WS
%ignore WS
"""

parser = lark.Lark(grammar)

print(parser.parse("""
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
""").pretty())

opname = {
    "and": "&", "or": "|", "not": "~", "eq": "==", "ne": "!=", "gt": ">", "ge": ">=", "lt": "<", "le": "<=",
    "add": "+", "sub": "-", "mul": "*", "div": "/", "pos": "+_", "neg": "-_", "pow": "**",
    "subscript": "[]", "attribute": "."
    }

class AST:
    _fields = ()

    def __init__(self, *args, line=None):
        self.line = line
        assert len(self._fields) == len(args)
        for n, x in zip(self._fields, args):
            setattr(self, n, x)
            if self.line is None:
                self.line = x.line

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

class Function(AST):
    _fields = ("parameters", "body")
    def __str__(self):
        return "({0}) => {1}".format(", ".join(self.parameters), str(self.body))

class SymbolTable:
    def __init__(self, parent, symbols):
        self.parent = parent
        self.symbols = symbols

    def __getitem__(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif self.parent is not None:
            return self.parent[symbol]
        else:
            raise KeyError(symbol)

    def __setitem__(self, symbol, value):
        self.symbols[symbol] = value
