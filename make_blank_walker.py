import collections
import re

from uncompyle6.parsers.parse13 import Python13Parser
from uncompyle6.parsers.parse13 import Python13ParserSingle
from uncompyle6.parsers.parse14 import Python14Parser
from uncompyle6.parsers.parse14 import Python14ParserSingle
from uncompyle6.parsers.parse15 import Python15Parser
from uncompyle6.parsers.parse15 import Python15ParserSingle
from uncompyle6.parsers.parse21 import Python21Parser
from uncompyle6.parsers.parse21 import Python21ParserSingle
from uncompyle6.parsers.parse22 import Python22Parser
from uncompyle6.parsers.parse22 import Python22ParserSingle
from uncompyle6.parsers.parse23 import Python23Parser
from uncompyle6.parsers.parse23 import Python23ParserSingle
from uncompyle6.parsers.parse24 import Python24Parser
from uncompyle6.parsers.parse24 import Python24ParserSingle
from uncompyle6.parsers.parse25 import Python25Parser
from uncompyle6.parsers.parse25 import Python25ParserSingle
from uncompyle6.parsers.parse26 import Python26Parser
from uncompyle6.parsers.parse26 import Python26ParserSingle
from uncompyle6.parsers.parse27 import Python27Parser
from uncompyle6.parsers.parse27 import Python27ParserSingle
from uncompyle6.parsers.parse2 import Python2Parser
from uncompyle6.parsers.parse2 import Python2ParserSingle
from uncompyle6.parsers.parse30 import Python30Parser
from uncompyle6.parsers.parse30 import Python30ParserSingle
from uncompyle6.parsers.parse31 import Python31Parser
from uncompyle6.parsers.parse31 import Python31ParserSingle
from uncompyle6.parsers.parse32 import Python32Parser
from uncompyle6.parsers.parse32 import Python32ParserSingle
from uncompyle6.parsers.parse33 import Python33Parser
from uncompyle6.parsers.parse33 import Python33ParserSingle
from uncompyle6.parsers.parse34 import Python34Parser
from uncompyle6.parsers.parse34 import Python34ParserSingle
from uncompyle6.parsers.parse35 import Python35Parser
from uncompyle6.parsers.parse35 import Python35ParserSingle
from uncompyle6.parsers.parse36 import Python36Parser
from uncompyle6.parsers.parse36 import Python36ParserSingle
from uncompyle6.parsers.parse37 import Python37Parser
from uncompyle6.parsers.parse37 import Python37ParserSingle
from uncompyle6.parsers.parse3 import Python3Parser
from uncompyle6.parsers.parse3 import Python3ParserSingle
from uncompyle6.parser import PythonParser

nodes = collections.OrderedDict()
for cls in [Python13Parser, Python13ParserSingle, Python14Parser, Python14ParserSingle, Python15Parser, Python15ParserSingle, Python21Parser, Python21ParserSingle, Python22Parser, Python22ParserSingle, Python23Parser, Python23ParserSingle, Python24Parser, Python24ParserSingle, Python25Parser, Python25ParserSingle, Python26Parser, Python26ParserSingle, Python27Parser, Python27ParserSingle, Python2Parser, Python2ParserSingle, Python30Parser, Python30ParserSingle, Python31Parser, Python31ParserSingle, Python32Parser, Python32ParserSingle, Python33Parser, Python33ParserSingle, Python34Parser, Python34ParserSingle, Python35Parser, Python35ParserSingle, Python36Parser, Python36ParserSingle, Python37Parser, Python37ParserSingle, Python3Parser, Python3ParserSingle, PythonParser]:
    for meth in dir(cls):
        if meth.startswith("p_"):
            doc = getattr(getattr(cls, meth), "__doc__", None)
            if doc is not None:
                for n in re.findall(r"\b[A-Za-z0-9_]+\b", re.sub(r"#.*", "", doc)):
                    if n not in nodes:
                        nodes[n] = None
                    if "p_" + n == meth:
                        nodes[n] = doc

print(r"""import sys
IS_PYPY = "__pypy__" in sys.builtin_module_names

import spark_parser.ast
import uncompyle6.parser

class Walker(spark_parser.GenericASTTraversal):
    def __init__(self, version, out, scanner, showast=False, debug_parser=spark_parser.DEFAULT_DEBUG, compile_mode="exec", is_pypy=IS_PYPY, linestarts={}, tolerate_errors=False):
        super(Walker, self).__init__(ast=None)
        self.scanner = scanner
        self.version = version
        self.p = uncompyle6.parser.get_python_parser(version, debug_parser=dict(debug_parser), compile_mode=compile_mode, is_pypy=is_pypy)

    def build_ast(self, tokens, customize, is_lambda=False, noneInNames=False, isTopLevel=False):
        return uncompyle6.parser.parse(self.p, tokens, customize)

    def gen_source(self, ast, name, customize, is_lambda=False, returnNone=False):
        return self.preorder(ast)

    def _name_lineno(self, name, node):
        lineno = getattr(node, "linestart", None)
        if lineno is None:
            return name
        else:
            return "{0} on line {1}".format(name, node.linestart)

    def default(self, node):
        raise NotImplementedError("unrecognized node type: " + self._name_lineno(type(node).__name__, node))

""" + "\n\n".join("    def n_{0}(self, node):{1}\n        raise NotImplementedError(self._name_lineno({2}, node))\n        # self.prune()".format(n, "" if nodes[n] is None else "\n        ''{0}''".format(repr(nodes[n]).replace(r"\n", "\n")), repr(n)) for n in nodes))
