#!/usr/bin/env python

import collections
import itertools
import math

import uproot

import lark

# pattern:    derivation* constraint* "for" multiple
# derivation: CNAME "=" expression
# constraint: "if" expression -> if | "best" expression -> best | "sort" expression -> sort
# multiple:   single ("," single)*
# single:     CNAME ("," CNAME)* "in" expression

grammar = """
start: (NEWLINE | ";")* (statement (NEWLINE | ";")+)* statement (NEWLINE | ";")*

statement:  assignment -> pass | funcassign -> pass
assignment: CNAME "=" expression
funcassign: CNAME "(" [CNAME ("," CNAME)*] ")" "=" block

fieldassign: CNAME "=" expression
           | CNAME "~" (pattern | expression) -> symmetric
           | CNAME "!~" (pattern | expression) -> asymmetric
pattern:     "{" (NEWLINE | ";")* (fieldassign (NEWLINE | ";")+)* fieldassign (NEWLINE | ";")* "}"

expression: function   -> pass
function:   block      -> pass | paramlist "=>" block
block:      or         -> pass | "{" (NEWLINE | ";")* (statement (NEWLINE | ";")+)* expression (NEWLINE | ";")* "}"

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

atom:    CNAME -> symbol | INT -> int | FLOAT -> float | "(" expression ")" -> pass | "match" pattern -> pass

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

print(parser.parse("""
higgs = match {
        z1 ~ {
            mu1 ~ muons
            mu2 ~ muons
            p4 = mu1.p4 + mu2.p4
        }
        z2 !~ {
            mu1 ~ muons
            mu2 ~ muons
            p4 = mu1.p4 + mu2.p4
        }
        p4 = z1.p4 + z2.p4
    }
""").pretty())



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

# class Pattern(AST):
#     _fields = ("derivations", "constraints", "sources")
#     def __str__(self):
#         return "match {{\n    {0}}}".format("\n    ".join(str(x) for x in self.derivations + self.constraints + [self.sources]))

# class Constraint(AST):
#     _fields = ("clause", "expression")
#     def __str__(self):
#         return self.clause + " " + str(self.expression)

# class Sources(AST):
#     _fields = ("singles",)
#     def __str__(self):
#         return "for " + ", ".join(str(x) for x in self.singles)

# class Source(AST):
#     _fields = ("symbols", "expression")
#     def __str__(self):
#         return ", ".join(self.symbols) + " in " + str(self.expression)

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
    # elif node.data == "pattern":
    #     args = [toast(x) for x in node.children]
    #     derivations = [x for x in args if isinstance(x, Assignment)]
    #     constraints = [x for x in args if isinstance(x, Constraint)]
    #     count = 0
    #     for x in constraints:
    #         if x.clause == "best" or x.clause == "sort":
    #             count += 1
    #         if count > 1:
    #             raise SyntaxError("on line {0}, only one best/sort is allowed".format("???" if x.line is None else x.line))
    #     return Pattern(derivations, constraints, args[-1])
    elif node.data == "if" or node.data == "best" or node.data == "sort":
        return Constraint(node.data, toast(node.children[0]))
    elif node.data == "multiple":
        return Sources([toast(x) for x in node.children])
    elif node.data == "single":
        return Source([str(x) for x in node.children[:-1]], toast(node.children[-1]))
    elif node.data == "assignment" or node.data == "derivation":
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
    elif node.data == "slice1":
        return Slice(toast(node.children[0]), None)
    elif node.data == "slice2":
        return Slice(None, toast(node.children[0]))
    elif node.data == "slice12":
        return Slice(toast(node.children[0]), toast(node.children[1]))
    elif node.data == "symbol":
        return Symbol(str(node.children[0]), line=node.children[0].line)
    elif node.data == "int":
        return Literal(int(node.children[0]), line=node.children[0].line)
    elif node.data == "float":
        return Literal(float(node.children[0]), line=node.children[0].line)
    elif node.data in opname:
        return Call(Symbol(opname[node.data]), [toast(x) for x in node.children])
    else:
        raise AssertionError(node.data)

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
        if symbol in self.symbols:
            raise TypeError("symbol {0} has multiple definitions at this scope".format(repr(symbol)))
        else:
            self.symbols[symbol] = value

    def __str__(self):
        return "{" + ",\n ".join(repr(n) + ": " + repr(x) for n, x in self.symbols.items() if not callable(x)) + "}"

def run(node, symbols):
    if isinstance(node, Module):
        for x in node.statements:
            run(x, symbols)

    # elif isinstance(node, Pattern):
    #     dummys = []
    #     for single in node.sources.singles:
    #         for x in single.symbols:
    #             if x in dummys:
    #                 raise TypeError("on line {0}, match variable names are not all unique".format(single.line))
    #             dummys.append(x)
    #     fields = list(dummys)
    #     for derivation in node.derivations:
    #         if derivation.symbol in fields:
    #             raise TypeError("on line {0}, match variable names are not all unique".format(derivation.line))
    #         fields.append(derivation.symbol)
    #     select = [constraint.expression for constraint in node.constraints if constraint.clause == "if"]
    #     metric = [constraint for constraint in node.constraints if constraint.clause != "if"]
    #     if len(metric) > 0:
    #         fields.append("metric")
    #     outputlist = []
    #     outputtype = collections.namedtuple("match", fields)

    #     dummys = sum([x.symbols for x in node.sources.singles], [])
    #     data   = [run(x.expression, symbols) for x in node.sources.singles]
    #     def recurse(singles, data):
    #         if len(singles) == 1:
    #             for row in itertools.combinations(data[0], len(singles[0].symbols)):
    #                 yield row
    #         else:
    #             for row in itertools.combinations(data[0], len(singles[0].symbols)):
    #                 for rest in recurse(singles[1:], data[1:]):
    #                     yield row + rest
    #     for row in recurse(node.sources.singles, data):
    #         current = SymbolTable(symbols, dict(zip(dummys, row)))
    #         for derivation in node.derivations:
    #             run(derivation, current)
    #         if all(run(x, current) for x in select):
    #             if len(metric) > 0:
    #                 current["metric"] = run(metric[0].expression, current)
    #             outputlist.append(outputtype(*[current[n] for n in fields]))

    #     if len(metric) > 0:
    #         outputlist.sort(key=lambda x: x.metric)
    #         if metric[0].clause == "best":
    #             if len(outputlist) == 0:
    #                 raise RuntimeError("on line {0}, requesting 'best' of an empty set".format(metric[0].line))
    #             return outputlist[0]
    #     return outputlist

    elif isinstance(node, Assignment):
        symbols[node.symbol] = run(node.expression, symbols)

    elif isinstance(node, Function):
        def function(arguments, symbols):
            if len(node.parameters) != len(arguments):
                raise TypeError("on line {0}, function expects {1} arguments, got {2}".format(node.line, len(node.parameters), len(arguments)))
            scope = {}
            for param, arg in zip(node.parameters, arguments):
                scope[param] = run(arg, symbols)
            return run(node.body, SymbolTable(symbols, scope))
        return function

    elif isinstance(node, Block):
        symbols = SymbolTable(symbols, {})
        for x in node.statements:
            run(x, symbols)
        return run(node.expression, symbols)

    elif isinstance(node, Call):
        try:
            return run(node.function, symbols)(node.arguments, symbols)
        except Exception as err:
            raise RuntimeError("on line {0}, encountered {1}: {2}".format("???" if node.line is None else node.line, type(err).__name__, str(err)))

    elif isinstance(node, Subscript):
        try:
            return run(node.object, symbols)[run(node.index, symbols)]
        except Exception as err:
            raise RuntimeError("on line {0}, encountered {1}: {2}".format("???" if node.line is None else node.line, type(err).__name__, str(err)))

    elif isinstance(node, Attribute):
        try:
            return getattr(run(node.object, symbols), node.field)
        except Exception as err:
            raise RuntimeError("on line {0}, encountered {1}: {2}".format("???" if node.line is None else node.line, type(err).__name__, str(err)))
        
    elif isinstance(node, Slice):
        return slice(None if node.start is None else run(node.start, symbols), None if node.stop is None else run(node.stop, symbols), None)

    elif isinstance(node, Symbol):
        try:
            return symbols[node.symbol]
        except Exception as err:
            raise RuntimeError("on line {0}, encountered {1}: {2}".format("???" if node.line is None else node.line, type(err).__name__, str(err)))
        
    elif isinstance(node, Literal):
        return node.value

    else:
        raise AssertionError(type(node))

builtins = SymbolTable(None, {
    "len":  lambda arguments, symbols: len(run(arguments[0], symbols)),
    "abs":  lambda arguments, symbols: abs(run(arguments[0], symbols)),

    "and":  lambda arguments, symbols: run(arguments[0], symbols) and run(arguments[1], symbols),
    "or":   lambda arguments, symbols: run(arguments[0], symbols) or run(arguments[1], symbols),
    "not":  lambda arguments, symbols: not run(arguments[0], symbols),

    "==":   lambda arguments, symbols: run(arguments[0], symbols) == run(arguments[1], symbols),
    "!=":   lambda arguments, symbols: run(arguments[0], symbols) != run(arguments[1], symbols),
    ">":    lambda arguments, symbols: run(arguments[0], symbols) > run(arguments[1], symbols),
    ">=":   lambda arguments, symbols: run(arguments[0], symbols) >= run(arguments[1], symbols),
    "<":    lambda arguments, symbols: run(arguments[0], symbols) < run(arguments[1], symbols),
    "<=":   lambda arguments, symbols: run(arguments[0], symbols) <= run(arguments[1], symbols),
    "+":    lambda arguments, symbols: +run(arguments[0], symbols) if len(arguments) == 1 else (run(arguments[0], symbols) + run(arguments[1], symbols)),
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

    "union": lambda arguments, symbols: sum((run(x, symbols) for x in arguments), []),   # all sorts of unwarranted assumptions
    })

class LorentzVector:
    def __init__(self, px, py, pz, E):
        self.px = px
        self.py = py
        self.pz = pz
        self.E = E
    def __repr__(self):
        return "LorentzVector({0:g}, {1:g}, {2:g}, {3:g})".format(self.px, self.py, self.pz, self.E)
    @property
    def pt(self):
        return math.sqrt(self.px**2 + self.py**2)
    @property
    def mass(self):
        try:
            return math.sqrt(self.E**2 - self.px**2 - self.py**2 - self.pz**2)
        except ValueError:
            return float("nan")
    def __add__(self, other):
        return LorentzVector(self.px + other.px, self.py + other.py, self.pz + other.pz, self.E + other.E)

symbols = SymbolTable(builtins, {"x": LorentzVector(1, 2, 3, 4)})
run(toast(parser.parse("""
q = {
    quad(x, y) = sqrt(x**2 + y**2);
    z = quad(x.pz, x.E);
    z
}
""")), symbols)
print(symbols)

# symbols = SymbolTable(builtins, {"generator": [1, 2, 3], "reconstructed": [1.1, 3.3]})
# run(toast(parser.parse("""
# diff(x, y) = abs(x - y)
# genreco = match {
#     if diff(gen, reco) < 0.5
#     for gen in generator, reco in reconstructed
# }
# """)), symbols)
# print(symbols)

# events = uproot.open("http://scikit-hep.org/uproot/examples/HZZ.root")["events"]
# Electron_Px, Electron_Py, Electron_Pz, Electron_E, Electron_Charge = events.arrays(["Electron_Px", "Electron_Py", "Electron_Pz", "Electron_E", "Electron_Charge"], outputtype=tuple, entrystop=5)
# Muon_Px, Muon_Py, Muon_Pz, Muon_E, Muon_Charge = events.arrays(["Muon_Px", "Muon_Py", "Muon_Pz", "Muon_E", "Muon_Charge"], outputtype=tuple, entrystop=5)
# Particle = collections.namedtuple("Particle", ["px", "py", "pz", "E", "charge"])

# engine = toast(parser.parse("""
# mass(particle) = sqrt(particle.E**2 - particle.px**2 - particle.py**2 - particle.pz**2)

# same_flavor(collection) = match {
#     z1 = lep1 + lep2
#     z2 = lep3 + lep4
#     hmass = mass(z1 + z2)
#     if lep1.charge != lep2.charge
#     if lep3.charge != lep4.charge
#     sort (mass(z1) - 91)**2 + (mass(z2) - 91)**2
#     for lep1, lep2, lep3, lep4 in collection
# }

# higgs4e = same_flavor(electrons)
# higgs4mu = same_flavor(muons)

# higgs2e2mu = match {
#     z1 = lep1 + lep2
#     z2 = lep3 + lep4
#     hmass = mass(z1 + z2)
#     if lep1.charge != lep2.charge
#     if lep3.charge != lep4.charge
#     for lep1, lep2 in electrons, lep3, lep4 in muons
# }
# """))

# for i in range(len(Muon_Px)):
#     symbols = SymbolTable(builtins, {
#         "electrons": [Particle(Electron_Px[i][j], Electron_Py[i][j], Electron_Pz[i][j], Electron_E[i][j], Electron_Charge[i][j]) for j in range(len(Electron_Px[i]))],
#         "muons": [Particle(Muon_Px[i][j], Muon_Py[i][j], Muon_Pz[i][j], Muon_E[i][j], Muon_Charge[i][j]) for j in range(len(Muon_Px[i]))]
#         })
#     run(engine, symbols)
#     del symbols["electrons"]
#     del symbols["muons"]
#     print(symbols)
