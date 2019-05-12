#!/usr/bin/env python

import collections
import math

import lark

grammar = """
start: NEWLINE* (statement (NEWLINE | ";"))* statement NEWLINE*

pattern:    derivation* constraint* "for" multiple
derivation: CNAME "=" expression
constraint: "if" expression -> if | "best" expression -> best | "sort" expression -> sort
multiple:   single ("," single)*
single:     CNAME ("," CNAME)* "in" expression

statement:  assignment -> pass | funcassign -> pass
assignment: CNAME "=" expression
funcassign: CNAME "(" [CNAME ("," CNAME)*] ")" "=" block

expression: match      -> pass
match:      function   -> pass | "match" "{" pattern "}"
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
       | call "(" arglist ")"  | call "[" slice "]" -> subscript | call "." CNAME -> attribute

atom:    "(" expression ")" -> pass | CNAME -> symbol | INT -> int | FLOAT -> float

paramlist: "(" [CNAME ("," CNAME)*] ")" | CNAME
arglist:   expression ("," expression)*
slice:     expression -> pass
         | expression ":" -> slice1 | ":" expression -> slice2 | expression ":" expression -> slice12

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
            if not isinstance(x, list):
                x = [x]
            for xi in x:
                if self.line is None:
                    self.line = getattr(xi, "line", None)

    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, ", ".join(getattr(self, n) for n in self._fields))

class Module(AST):
    _fields = ("statements",)
    def __str__(self):
        return "\n".join(str(x) for x in self.statements)

class Pattern(AST):
    _fields = ("derivations", "constraints", "sources")
    def __str__(self):
        return "match {{\n    {0}}}".format("\n    ".join(str(x) for x in self.derivations + self.constraints + [self.sources]))

class Constraint(AST):
    _fields = ("clause", "expression")
    def __str__(self):
        return self.clause + " " + str(self.expression)

class Sources(AST):
    _fields = ("singles",)
    def __str__(self):
        return "for " + ", ".join(str(x) for x in self.singles)

class Source(AST):
    _fields = ("symbols", "expression")
    def __str__(self):
        return ", ".join(self.symbols) + " in " + str(self.expression)

class Assignment(AST):
    _fields = ("symbol", "expression")
    def __str__(self):
        return "{0} = {1}".format(self.symbol, str(self.expression))

class Function(AST):
    _fields = ("parameters", "body")
    def __str__(self):
        left, right = ("", "") if len(self.parameters) == 1 else ("(", ")")
        return "{0}{1}{2} => {3}".format(left, ", ".join(self.parameters), right, str(self.body))

class Block(AST):
    _fields = ("statements", "expression")
    def __str__(self):
        return "{" + "; ".join(str(x) for x in self.statements + [self.expression]) + "}"

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

class Slice(AST):
    _fields = ("start", "stop")
    def __str__(self):
        return "{0}:{1}".format("" if self.start is None else str(self.start), "" if self.stop is None else str(self.stop))

class Symbol(AST):
    _fields = ("symbol",)
    def __str__(self):
        return self.symbol

class Literal(AST):
    _fields = ("value",)
    def __str__(self):
        return str(self.value)

opname = {
    "and": "and", "or": "or", "not": "not",
    "eq": "==", "ne": "!=", "gt": ">", "ge": ">=", "lt": "<", "le": "<=",
    "add": "+", "sub": "-", "mul": "*", "div": "/", "pos": "+", "neg": "-", "pow": "**"
    }

def toast(node):
    if node.data == "pass" or node.data == "match":
        return toast(node.children[0])
    elif node.data == "start":
        return Module([toast(x) for x in node.children if not isinstance(x, lark.lexer.Token)])
    elif node.data == "pattern":
        args = [toast(x) for x in node.children]
        derivations = [x for x in args if isinstance(x, Assignment)]
        constraints = [x for x in args if isinstance(x, Constraint)]
        count = 0
        for x in constraints:
            if x.clause == "best" or x.clause == "sort":
                count += 1
            if count > 1:
                raise SyntaxError("on line {0}, only one best/sort is allowed".format("???" if x.line is None else x.line))
        return Pattern(derivations, constraints, args[-1])
    elif node.data == "if" or node.data == "best" or node.data == "sort":
        return Constraint(node.data, toast(node.children[0]))
    elif node.data == "multiple":
        return Sources([toast(x) for x in node.children])
    elif node.data == "single":
        return Source([str(x) for x in node.children[:-1]], toast(node.children[-1]), line=node.children[0].line)
    elif node.data == "assignment" or node.data == "derivation":
        return Assignment(str(node.children[0]), toast(node.children[1]), line=node.children[0].line)
    elif node.data == "funcassign":
        return Assignment(str(node.children[0]), Function(node.children[1:-1], toast(node.children[-1])), line=node.children[0].line)
    elif node.data == "function":
        return Function(toast(node.children[0]), toast(node.children[1]), line=node.children[0].line)
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
    elif node.data == "slice1":
        return Slice(toast(node.children[0]), None)
    elif node.data == "slice2":
        return Slice(None, toast(node.children[0]))
    elif node.data == "slice12":
        return Slice(toast(node.children[0]), toast(node.children[1]))
    elif node.data == "symbol":
        return Symbol(node.children[0], line=node.children[0].line)
    elif node.data == "int":
        return Literal(int(node.children[0]), line=node.children[0].line)
    elif node.data == "float":
        return Literal(float(node.children[0]), line=node.children[0].line)
    elif node.data in opname:
        return Call(Symbol(opname[node.data]), [toast(x) for x in node.children])
    else:
        raise AssertionError(node.data)

# print(toast(parser.parse("""
# genreco = match for gen in generator, reco in reconstructed
# """)))

print(toast(parser.parse("""
higgs = match {
        h = z1 + z2
        z1 = mu1 + mu2
        z2 = mu3 + mu4
        if mu1.charge != mu2.charge
        if mu3.charge != mu4.charge
        best (mass(z1) - 91)**2 + (mass(z2) - 91)**2
        for mu1, mu2, mu3, mu4 in muons
    }
""")))






# print(toast(parser.parse("""
# genreco =
#     match fit (gen - reco)**2
#           gen in generator
#               reco in reconstructed
# """)))

# print(parser.parse("""
# higgs =
#     match fit (z1.eta - z2.eta)**2
#           z1 = mu1 + mu2
#               cut mu1.charge != mu2.charge
#               fit (z1.mass - 91)**2
#           mu1 in muons
#           mu2 in muons
#           z2 = mu3 + mu4
#               cut mu3.charge != mu4.charge
#               fit (z2.mass - 91)**2
#           mu3 in muons
#           mu4 in muons
# """).pretty())

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
        if symbol in self.symbols:
            raise TypeError("symbol {0} has multiple definitions at this scope".format(repr(symbol)))
        else:
            self.symbols[symbol] = value

    def __str__(self):
        return "{" + ", ".join(repr(n) + ": " + repr(x) for n, x in self.symbols.items() if not callable(x)) + "}"

def run(node, symbols):
    if isinstance(node, Module):
        for x in node.statements:
            run(x, symbols)

# class Match(AST):    _fields = ("patterns",)
# class Pattern(AST):     _fields = ("symbol", "expression", "cuts", "fits", "terminal")

    # elif isinstance(node, Match):
        




    #     for row in itertools.product(*iterables)



    elif isinstance(node, Assignment):
        symbols[node.symbol] = run(node.expression, symbols)
    elif isinstance(node, Function):
        def function(arguments, symbols):
            if len(node.parameters) != len(arguments):
                raise TypeError("function expects {0} arguments, got {1}".format(len(node.parameters), len(arguments)))
            scope = {}
            for param, arg in zip(node.parameters, arguments):
                scope[param] = run(arg, symbols)
            return run(node.body, SymbolTable(symbols, scope))
        return function
    elif isinstance(node, Block):
        symbols = SymbolTable(symbols, {})
        for x in node.statements:
            run(x, symbols)
        return run(x.expression, symbols)
    elif isinstance(node, Call):
        try:
            return run(node.function, symbols)(node.arguments, symbols)
        except Exception as err:
            raise RuntimeError("on line {0}, encountered {1}: {2}".format("???" if node.line is None else node.line, type(err).__name__, str(err)))
    elif isinstance(node, Subscript):
        return run(node.object, symbols)[run(node.index, symbols)]
    elif isinstance(node, Attribute):
        return getattr(run(node.object, symbols), node.field)
    elif isinstance(node, Slice):
        return slice(None if node.start is None else run(node.start, symbols), None if node.stop is None else run(node.stop, symbols), None)
    elif isinstance(node, Symbol):
        return symbols[node.symbol]
    elif isinstance(node, Literal):
        return node.value
    else:
        raise AssertionError(type(node))

builtins = SymbolTable(None, {
    "len":  lambda arguments, symbols: len(run(arguments[0], symbols)),

    "and":  lambda arguments, symbols: run(arguments[0], symbols) and run(arguments[1], symbols),
    "or":   lambda arguments, symbols: run(arguments[0], symbols) or run(arguments[1], symbols),
    "not":  lambda arguments, symbols: not run(arguments[0], symbols),

    "==":   lambda arguments, symbols: run(arguments[0], symbols) == run(arguments[1], symbols),
    "!=":   lambda arguments, symbols: run(arguments[0], symbols) != run(arguments[1], symbols),
    ">":    lambda arguments, symbols: run(arguments[0], symbols) > run(arguments[1], symbols),
    ">=":   lambda arguments, symbols: run(arguments[0], symbols) >= run(arguments[1], symbols),
    "<":    lambda arguments, symbols: run(arguments[0], symbols) < run(arguments[1], symbols),
    "<=":   lambda arguments, symbols: run(arguments[0], symbols) <= run(arguments[1], symbols),
    "+":    lambda arguments, symbols: run(arguments[0], symbols) if len(arguments) == 1 else (run(arguments[0], symbols) + run(arguments[1], symbols)),
    "-":    lambda arguments, symbols: -run(arguments[0], symbols) if len(arguments) == 1 else (run(arguments[0], symbols) - run(arguments[1], symbols)),
    "*":    lambda arguments, symbols: run(arguments[0], symbols) * run(arguments[1], symbols),
    "/":    lambda arguments, symbols: float(run(arguments[0], symbols)) / float(run(arguments[1], symbols)),
    "**":   lambda arguments, symbols: run(arguments[0], symbols) ** run(arguments[1], symbols),

    "sqrt": lambda arguments, symbols: math.sqrt(run(arguments[0], symbols)),
    "exp":  lambda arguments, symbols: math.exp(run(arguments[0], symbols)),
    "sin":  lambda arguments, symbols: math.sin(run(arguments[0], symbols)),
    "cos":  lambda arguments, symbols: math.cos(run(arguments[0], symbols)),
    "tan":  lambda arguments, symbols: math.tan(run(arguments[0], symbols)),
    "sinh": lambda arguments, symbols: math.sinh(run(arguments[0], symbols)),
    "cosh": lambda arguments, symbols: math.cosh(run(arguments[0], symbols)),
    "tanh": lambda arguments, symbols: math.tanh(run(arguments[0], symbols)),
    })

LorentzVector = collections.namedtuple("LorentzVector", ["px", "py", "pz", "E"])

symbols = SymbolTable(builtins, {"x": LorentzVector(1, 2, 3, 4)})

run(toast(parser.parse("""
quad(x, y) = sqrt(x**2 + y**2)
z = quad(x.pz, x.E)
""")), symbols)

print(symbols)

# print(toast(parser.parse("""
# higgs =
#     match h = z1 + z2 fit (h.mass - 125)**2 {
#               z1 = mu1 + mu2
#                   cut mu1.charge != mu2.charge
#                   fit (z1.mass - 91)**2
#               mu1 in muons
#               mu2 in muons
#           }
#           z2 = mu3 + mu4
#               cut mu3.charge != mu4.charge
#               fit (z2.mass - 91)**2
#           mu3 in muons
#           mu4 in muons
# """)))

"""

{mu1 in muons, mu2 in muons, {mu3 in muons, mu4 in muons}}

{gen in generator, {reco in reconstructed}}

"""

# match fit (gen - reco)**2
#       gen in generator {
#         reco in reconstructed
#       }
