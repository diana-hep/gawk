#!/usr/bin/env python

import collections
import itertools
import functools
import math

import uproot

class p4obj:
    def __init__(self, cut=None, fit=None, asymm=False, **daughters):
        self.cut = cut
        self.fit = fit
        self.asymm = asymm
        self.daughters = daughters

    def __repr__(self):
        args = []
        if self.cut is not None:
            args.append("cut = {0}".format(repr(self.cut)))
        if self.fit is not None:
            args.append("fit = {0}".format(repr(self.fit)))
        if self.asymm:
            args.append("asymm = {0}".format(self.asymm))
        for n, x in self.daughters.items():
            args.append("{0} = {1}".format(n, repr(x)))
        return "p4obj({0})".format(", ".join(args))

    def __str__(self, indent=""):
        args = []
        if self.cut is not None:
            args.append("cut = {0}".format(repr(self.cut)))
        if self.fit is not None:
            args.append("fit = {0}".format(repr(self.fit)))
        if self.asymm:
            args.append("asymm = {0}".format(self.asymm))
        for n, x in self.daughters.items():
            args.append("{0} = {1}".format(n, x.__str__(indent + "    ").lstrip()))
        if self.cut is None and self.fit is None:
            return indent + "p4obj(\n{0}    {1})".format(indent, (",\n" + indent + "    ").join(args))
        else:
            return indent + "p4obj({0})".format((",\n" + indent + "    ").join(args))

class member:
    def __init__(self, collection, cut=None, fit=None, asymm=False):
        self.collection = collection
        self.cut = cut
        self.fit = fit
        self.asymm = asymm

    def __repr__(self):
        args = []
        if self.cut is not None:
            args.append(", cut = {0}".format(repr(self.cut)))
        if self.fit is not None:
            args.append(", fit = {0}".format(repr(self.fit)))
        if self.fit is not None:
            args.append(", fit = {0}".format(repr(self.fit)))
        if self.asymm:
            args.append(", asymm = {0}".format(self.asymm))
        return "{0}({1}{2})".format(type(self).__name__, repr(self.collection), "".join(args))

    def __str__(self, indent=""):
        return indent + repr(self)

class unique(member): pass

@functools.total_ordering
class ID:
    def __init__(self, n):
        self.n = n
    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, self.n)
    def __hash__(self):
        return hash((type(self), self.n))
    def __eq__(self, other):
        return type(self) == type(other) and self.n == other.n
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        if type(self) is type(other):
            return self.n < other.n
        else:
            return type(self).__name__ < type(other).__name__

class e(ID): pass
class m(ID): pass

class P4Object:
    def __init__(self, id, px, py, pz, E, **others):
        self.id = id
        self.px = px
        self.py = py
        self.pz = pz
        self.E = E
        for n, x in others.items():
            setattr(self, n, x)

    def __repr__(self):
        return "P4Object({0}, {1:5g}, {2:5g}, {3:5g}, {4:5g}{5})".format(
            repr(self.id), self.px, self.py, self.pz, self.E,
            "".join(", {0}={1}".format(n, x) for n, x in self.__dict__.items() if not n.startswith("_") and n not in ("id", "px", "py", "pz", "E")))

    def __str__(self, indent=""):
        return indent + "P4Object({0}, {1:5g}, {2:5g}, {3:5g}, {4:5g}{5}{6})".format(
            repr(self.id), self.px, self.py, self.pz, self.E,
            "".join(", {0} = {1}".format(n, x) for n, x in self.__dict__.items() if not n.startswith("_") and n not in ("id", "px", "py", "pz", "E") and not isinstance(x, P4Object)),
            "".join(",\n{0}{1} = {2}".format(indent + "    ", n, x.__str__(indent + "    ").lstrip()) for n, x in self.__dict__.items() if isinstance(x, P4Object)))

    # def copy(self):
    #     return P4Object(self.id, self.px, self.py, self.pz, self.E, **{n: x for n, x in self.__dict__.items() if not n.startswith("_" and not n in ("id", "px", "py", "pz", "E"))})

    @property
    def pt(self):
        return math.sqrt(self.px**2 + self.py**2)

    @property
    def mass(self):
        try:
            return math.sqrt(self.E**2 - self.px**2 - self.py**2 - self.pz**2)
        except ValueError:
            return float("nan")

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

def match(criteria, symbols):
    collections = []

    def getthem(node):
        if isinstance(node, p4obj):
            for n in sorted(node.daughters):
                getthem(node.daughters[n])
        elif isinstance(node, member):
            collections.append(symbols[node.collection])
        else:
            assert type(node)
    getthem(criteria)

    class MatchError(Exception): pass

    def usethem(row, node):
        if isinstance(node, p4obj):
            asymmid, symmid, px, py, pz, E = [], [], 0.0, 0.0, 0.0, 0.0
            daughters = {}
            for n in sorted(node.daughters):
                d = usethem(row, node.daughters[n])
                if node.daughters[n].asymm:
                    asymmid.append(d.id)
                else:
                    symmid.append(d.id)
                px += d.px
                py += d.py
                pz += d.pz
                E += d.E
                daughters[n] = d

            return P4Object(tuple(asymmid + sorted(symmid)), px, py, pz, E, **daughters)

        elif isinstance(node, member):
            if isinstance(node, unique):
                if row[0].id in [x.id for x in row[1:]]:
                    raise MatchError
            return row.pop(0)

        else:
            assert type(node)

    out = []
    seen = set()
    for row in itertools.product(*collections):
        try:
            x = usethem(list(row), criteria)
        except MatchError:
            pass
        else:
            if x.id not in seen:
                print(x)
            seen.add(x.id)

higgs = p4obj(fit = "(Z1.mass - 91)**2 + (Z2.mass - 91)**2",
              Z1 = p4obj(cut = "lep1.charge != lep2.charge",
                         lep1 = unique("electrons"),
                         lep2 = unique("electrons")),
              Z2 = p4obj(cut = "lep1.charge != lep2.charge",
                         lep1 = unique("muons"),
                         lep2 = unique("muons")))

events = uproot.open("http://scikit-hep.org/uproot/examples/HZZ.root")["events"]
Electron_Px, Electron_Py, Electron_Pz, Electron_E, Electron_Charge = events.arrays(["Electron_Px", "Electron_Py", "Electron_Pz", "Electron_E", "Electron_Charge"], outputtype=tuple, entrystop=5)
Muon_Px, Muon_Py, Muon_Pz, Muon_E, Muon_Charge = events.arrays(["Muon_Px", "Muon_Py", "Muon_Pz", "Muon_E", "Muon_Charge"], outputtype=tuple, entrystop=5)

for i in range(len(Muon_Px)):
    electrons = [P4Object(e(j), Electron_Px[i][j], Electron_Py[i][j], Electron_Pz[i][j], Electron_E[i][j], charge=Electron_Charge[i][j]) for j in range(len(Electron_Px[i]))]
    muons = [P4Object(m(j), Muon_Px[i][j], Muon_Py[i][j], Muon_Pz[i][j], Muon_E[i][j], charge=Muon_Charge[i][j]) for j in range(len(Muon_Px[i]))]
    print(muons)

match(higgs, {"electrons": electrons, "muons": muons})

genreco = p4obj(gen = member("electrons"),
                matchreco = p4obj(reco = member("muons")))
