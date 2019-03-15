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

nodes = set()
for cls in [Python13Parser, Python13ParserSingle, Python14Parser, Python14ParserSingle, Python15Parser, Python15ParserSingle, Python21Parser, Python21ParserSingle, Python22Parser, Python22ParserSingle, Python23Parser, Python23ParserSingle, Python24Parser, Python24ParserSingle, Python25Parser, Python25ParserSingle, Python26Parser, Python26ParserSingle, Python27Parser, Python27ParserSingle, Python2Parser, Python2ParserSingle, Python30Parser, Python30ParserSingle, Python31Parser, Python31ParserSingle, Python32Parser, Python32ParserSingle, Python33Parser, Python33ParserSingle, Python34Parser, Python34ParserSingle, Python35Parser, Python35ParserSingle, Python36Parser, Python36ParserSingle, Python37Parser, Python37ParserSingle, Python3Parser, Python3ParserSingle, PythonParser]:
    for meth in dir(cls):
        if meth.startswith("p_"):
            doc = getattr(getattr(cls, meth), "__doc__", None)
            if doc is not None:
                doc = re.sub(r"#.*", "", doc)
                nodes.update(re.findall(r"\b[A-Za-z0-9_]+\b", doc))

print(r"""import uncompyle6.semantics.pysource

class MakeAST(uncompyle6.semantics.pysource.SourceWalker):
    def _name_lineno(self, name, node):
        lineno = getattr(node, "linestart", None)
        if lineno is None:
            return name
        else:
            return "{0} on line {1}".format(name, node.linestart)

""" + "\n\n".join("    def n_{0}(self, node):\n        raise NotImplementedError(self._name_lineno({1}, node))".format(x, repr(x)) for x in sorted(nodes)))
