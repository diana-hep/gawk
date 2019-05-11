#!/usr/bin/env python

import lark

grammar = """
start: expression
expression: function   -> pass

function:   or         -> pass | paramlist "=>" or

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
call:    atom          -> pass | call "(" arglist ")"   | call "." CNAME -> attr

atom:    "(" expression ")" -> pass | CNAME -> symbol | NUMBER -> literal

paramlist: "(" [CNAME ("," CNAME)*] ")" | CNAME
arglist:   expression ("," expression)*

%import common.CNAME
%import common.NUMBER
%import common.WS
%ignore WS
"""

parser = lark.Lark(grammar)

print(parser.parse("a.map(x => x**2)").pretty())
