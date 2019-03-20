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
nodes["build_slice2"] = None
nodes["build_slice3"] = None
nodes["tuple"] = None
nodes["call_kw36"] = None
nodes["set"] = None
nodes["LOAD_LISTCOMP"] = None
nodes["listcomp"] = None
nodes["LOAD_SETCOMP"] = None

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
import types

import spark_parser
import uncompyle6.parser
import uncompyle6.scanner

import rejig.syntaxtree

def ast(code, pyversion=None, debug_parser=spark_parser.DEFAULT_DEBUG, linestart=None):
    if not isinstance(code, types.CodeType):
        code = code.__code__
    return BytecodeWalker(code, pyversion=pyversion, debug_parser=debug_parser).ast(linestart=linestart)

class BytecodeWalker(object):
    def __init__(self, code, pyversion=None, debug_parser=spark_parser.DEFAULT_DEBUG):
        self.code = code
        self.sourcepath = self.code.co_filename

        if pyversion is None:
            pyversion = float(sys.version[0:3])
        self.pyversion = pyversion

        self.debug_parser = debug_parser
        self.parser = uncompyle6.parser.get_python_parser(self.pyversion, debug_parser=dict(self.debug_parser), compile_mode="exec", is_pypy=("__pypy__" in sys.builtin_module_names))

    def ast(self, linestart=None):
        scanner = uncompyle6.scanner.get_scanner(self.pyversion, is_pypy=("__pypy__" in sys.builtin_module_names))
        tokens, customize = scanner.ingest(self.code, code_objects={}, show_asm=self.debug_parser.get("asm", False))
        parsed = uncompyle6.parser.parse(self.parser, tokens, customize)

        def pullup(node):
            if isinstance(node, uncompyle6.parsers.treenode.SyntaxTree):
                node.linestart = getattr(node, "linestart", None)
                for x in node:
                    if node.linestart is None:
                        node.linestart = pullup(x)
                    else:
                        pullup(x)
            return node.linestart
        pullup(parsed)

        def pushdown(node, linestart):
            if node.linestart is None:
                node.linestart = linestart
            if isinstance(node, uncompyle6.parsers.treenode.SyntaxTree):
                for x in node:
                    pushdown(x, node.linestart)
        pushdown(parsed, linestart)

        return self.n(parsed)

    def nameline(self, name, node):
        lineno = node.linestart
        if lineno is None:
            if self.sourcepath is None:
                return name
            else:
                return "{0} in {1}".format(name, self.sourcepath)
        else:
            if self.sourcepath is None:
                return "{0} on line {1}".format(name, node.linestart)
            else:
                return "{0} on line {1} of {2}".format(name, node.linestart, self.sourcepath)

    def find_offset(self, node, offset):
        if hasattr(node, "offset"):
            return True, node if isinstance(node.offset, int) and node.offset >= offset else None
        else:
            first = True
            for x in node:
                subfirst, subnode = self.find_offset(x, offset)
                if subnode is not None:
                    if first and subfirst:
                        return True, node
                    else:
                        return False, subnode
                first = False
            else:
                return False, None

    def make_const(self, value, sourcepath, linestart):
        if isinstance(value, tuple):
            return rejig.syntaxtree.Call("tuple", *[self.make_const(x, sourcepath, linestart) for x in value], sourcepath=sourcepath, linestart=linestart)
        elif isinstance(value, list):
            return rejig.syntaxtree.Call("list", *[self.make_const(x, sourcepath, linestart) for x in value], sourcepath=sourcepath, linestart=linestart)
        elif isinstance(value, set):
            return rejig.syntaxtree.Call("set", *[self.make_const(x, sourcepath, linestart) for x in value], sourcepath=sourcepath, linestart=linestart)
        elif isinstance(value, dict):
            pairs = []
            for n, x in value.items():
                pairs.append(self.make_const(n, sourcepath, linestart))
                pairs.append(self.make_const(x, sourcepath, linestart))
            return rejig.syntaxtree.Call("dict", *pairs, sourcepath=sourcepath, linestart=linestart)
        else:
            return rejig.syntaxtree.Const(value, sourcepath=sourcepath, linestart=linestart)

    def make_suite(self, node):
        suite = []
        for x in node:
            suite.append(self.n(x))
            if isinstance(suite[-1], rejig.syntaxtree.Call) and suite[-1].fcn == "return":
                break
        return rejig.syntaxtree.Suite(tuple(suite), sourcepath=self.sourcepath, linestart=node.linestart)

    def make_comp(self, source, loops):
        if len(loops) == 1:
            return loops[0]

        else:
            src, args, pred = loops[:3]
            if source is not None:
                src = source
            next = self.make_comp(None, loops[3:])

            if isinstance(args, rejig.syntaxtree.Name):
                args = (args.name,)
            elif isinstance(args, rejig.syntaxtree.Unpack):
                args = tuple(x.name for x in args.subtargets)
            else:
                raise AssertionError(type(args))

            if pred is not None:
                filterer = rejig.syntaxtree.Def(args, (), rejig.syntaxtree.Suite((pred,), sourcepath=pred.sourcepath, linestart=pred.linestart), sourcepath=pred.sourcepath, linestart=pred.linestart)
                src = rejig.syntaxtree.Call(rejig.syntaxtree.Call(".", src, "filter", sourcepath=pred.sourcepath, linestart=pred.linestart), filterer, sourcepath=pred.sourcepath, linestart=pred.linestart)
            
            mapper = rejig.syntaxtree.Def(args, (), rejig.syntaxtree.Suite((next,), sourcepath=next.sourcepath, linestart=next.linestart), sourcepath=next.sourcepath, linestart=next.linestart)
            return rejig.syntaxtree.Call(rejig.syntaxtree.Call(".", src, "map", sourcepath=next.sourcepath, linestart=next.linestart), mapper, sourcepath=next.sourcepath, linestart=next.linestart)

    def n(self, node):
        return getattr(self, "n_" + node.kind, self.default)(node)

    def default(self, node):
        raise NotImplementedError("unrecognized node type: " + self.nameline(type(node).__name__ + (" " + repr(node.kind) if hasattr(node, "kind") else ""), node))

""" + "\n\n".join("    def n_{0}(self, node):{1}\n        raise NotImplementedError(self.nameline({2}, node))".format(n, "" if nodes[n] is None else "\n        ''{0}''".format(repr(nodes[n]).replace(r"\n", "\n")), repr(n)) for n in nodes))
