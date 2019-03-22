import sys
import types
import numbers

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
            for i in range(len(node)):
                subfirst, subnode = self.find_offset(node[i], offset)
                if subnode is not None:
                    if first and subfirst:
                        return True, node
                    elif subnode is node[i]:
                        return False, node[i:]
                    else:
                        return False, subnode
                first = False
            else:
                return False, None

    def no_unary_plus(self, node):
        if isinstance(node, rejig.syntaxtree.Call) and node.fcn == "u+" and isinstance(node.args[0], rejig.syntaxtree.Const) and isinstance(node.args[0].value, numbers.Number):
            return node.args[0]
        elif isinstance(node, rejig.syntaxtree.Call) and node.fcn == "u+":
            node.args = tuple(self.no_unary_plus(x) for x in node.args)
        return node

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

    def make_suite(self, node, sourcepath, linestart):
        suite = []
        for i in range(len(node)):
            if node[i].kind == "_stmts":
                for x in node[i]:
                    suite.append(self.n(x))
            else:
                suite.append(self.n(node[i]))

            if isinstance(suite[-1], rejig.syntaxtree.Suite):
                suite, flatten = suite[:-1], suite[-1]
                for x in flatten:
                    suite.append(x)

            if isinstance(suite[-1], rejig.syntaxtree.Call) and suite[-1].fcn == "return":
                break
            elif isinstance(suite[-1], rejig.syntaxtree.Call) and suite[-1].fcn == "if" and len(suite[-1].args) == 2 and any(isinstance(x, rejig.syntaxtree.Call) and x.fcn == "return" for x in suite[-1].args[1].body):
                suite[-1].args = suite[-1].args + (self.make_suite(node[i + 1 :], sourcepath, linestart),)
                break
        return rejig.syntaxtree.Suite(tuple(suite), sourcepath=sourcepath, linestart=linestart)

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
                filterer = rejig.syntaxtree.Def(args, (), rejig.syntaxtree.Suite((rejig.syntaxtree.Call("return", pred, sourcepath=pred.sourcepath, linestart=pred.linestart),), sourcepath=pred.sourcepath, linestart=pred.linestart), sourcepath=pred.sourcepath, linestart=pred.linestart)
                src = rejig.syntaxtree.Call(rejig.syntaxtree.Call(".", src, "filter", sourcepath=pred.sourcepath, linestart=pred.linestart), filterer, sourcepath=pred.sourcepath, linestart=pred.linestart)
            
            mapper = rejig.syntaxtree.Def(args, (), rejig.syntaxtree.Suite((rejig.syntaxtree.Call("return", next, sourcepath=next.sourcepath, linestart=next.linestart),), sourcepath=next.sourcepath, linestart=next.linestart), sourcepath=next.sourcepath, linestart=next.linestart)
            return rejig.syntaxtree.Call(rejig.syntaxtree.Call(".", src, "map", sourcepath=next.sourcepath, linestart=next.linestart), mapper, sourcepath=next.sourcepath, linestart=next.linestart)

    def n(self, node):
        return getattr(self, "n_" + node.kind, self.default)(node)

    def default(self, node):
        raise NotImplementedError("unrecognized node type: " + self.nameline(type(node).__name__ + (" " + repr(node.kind) if hasattr(node, "kind") else ""), node))

    def n_build_slice2(self, node):
        return rejig.syntaxtree.Call("slice", self.n(node[0]), self.n(node[1]), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_build_slice3(self, node):
        return rejig.syntaxtree.Call("slice", self.n(node[0]), self.n(node[1]), self.n(node[2]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_tuple(self, node):
        return rejig.syntaxtree.Call("tuple", *[self.n(x) for x in node[:-1]], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_call_kw36(self, node):
        fcn = self.n(node[0])
        allargs = tuple(self.n(x) for x in node[1:-2])
        keywords = node[-2].pattr
        args = allargs[:-len(keywords)]
        kwargs = tuple(zip(keywords, allargs[-len(keywords):]))
        return rejig.syntaxtree.CallKeyword(fcn, args, kwargs, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_set(self, node):
        return rejig.syntaxtree.Call("set", *[self.n(x) for x in node[:-1]], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_LOAD_LISTCOMP(self, node):
        return node.attr

    def n_listcomp(self, node):
        source = self.n(node[3])
        loops = ast(self.n(node[0]), linestart=node.linestart).params[0].args[0]
        return self.make_comp(source, loops)

    def n_LOAD_SETCOMP(self, node):
        return node.attr

    def n_stmt(self, node):
        '''
        pass ::=

        _stmts ::= stmt+

        # statements with continue
        c_stmts ::= _stmts
        c_stmts ::= _stmts lastc_stmt
        c_stmts ::= lastc_stmt
        c_stmts ::= continues

        lastc_stmt ::= iflaststmt
        lastc_stmt ::= forelselaststmt
        lastc_stmt ::= ifelsestmtc

        c_stmts_opt ::= c_stmts
        c_stmts_opt ::= pass

        # statements inside a loop
        l_stmts ::= _stmts
        l_stmts ::= returns
        l_stmts ::= continues
        l_stmts ::= _stmts lastl_stmt
        l_stmts ::= lastl_stmt

        lastl_stmt ::= iflaststmtl
        lastl_stmt ::= ifelsestmtl
        lastl_stmt ::= forelselaststmtl
        lastl_stmt ::= tryelsestmtl

        l_stmts_opt ::= l_stmts
        l_stmts_opt ::= pass

        suite_stmts ::= _stmts
        suite_stmts ::= returns
        suite_stmts ::= continues

        suite_stmts_opt ::= suite_stmts

        # passtmt is needed for semantic actions to add "pass"
        suite_stmts_opt ::= pass

        else_suite ::= suite_stmts
        else_suitel ::= l_stmts
        else_suitec ::= c_stmts
        else_suitec ::= returns

        stmt ::= assert

        stmt ::= classdef
        stmt ::= call_stmt

        stmt ::= ifstmt
        stmt ::= ifelsestmt

        stmt ::= whilestmt
        stmt ::= while1stmt
        stmt ::= whileelsestmt
        stmt ::= while1elsestmt
        stmt ::= for
        stmt ::= forelsestmt
        stmt ::= try_except
        stmt ::= tryelsestmt
        stmt ::= tryfinallystmt
        stmt ::= withstmt
        stmt ::= withasstmt

        stmt ::= del_stmt
        del_stmt ::= DELETE_FAST
        del_stmt ::= DELETE_NAME
        del_stmt ::= DELETE_GLOBAL


        stmt   ::= return
        return ::= ret_expr RETURN_VALUE

        # "returns" nonterminal is a sequence of statements that ends in a RETURN statement.
        # In later Python versions with jump optimization, this can cause JUMPs
        # that would normally appear to be omitted.

        returns ::= return
        returns ::= _stmts return

        '''
        return self.n(node[0])

    def n_assign(self, node):
        '''
        stmt ::= assign
        assign ::= expr DUP_TOP designList
        assign ::= expr store

        stmt ::= assign2
        stmt ::= assign3
        assign2 ::= expr expr ROT_TWO store store
        assign3 ::= expr expr expr ROT_THREE ROT_TWO store store store
        '''
        return rejig.syntaxtree.Assign(self.n(node[-1]), self.n(node[0]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_expr(self, node):
        '''
        expr ::= _mklambda
        expr ::= LOAD_FAST
        expr ::= LOAD_NAME
        expr ::= LOAD_CONST
        expr ::= LOAD_GLOBAL
        expr ::= LOAD_DEREF
        expr ::= binary_expr
        expr ::= list
        expr ::= compare
        expr ::= dict
        expr ::= and
        expr ::= or
        expr ::= unary_expr
        expr ::= call
        expr ::= unary_not
        expr ::= subscript
        expr ::= subscript2
        expr ::= yield

        binary_expr ::= expr expr binary_op
        binary_op   ::= BINARY_ADD
        binary_op   ::= BINARY_MULTIPLY
        binary_op   ::= BINARY_AND
        binary_op   ::= BINARY_OR
        binary_op   ::= BINARY_XOR
        binary_op   ::= BINARY_SUBTRACT
        binary_op   ::= BINARY_TRUE_DIVIDE
        binary_op   ::= BINARY_FLOOR_DIVIDE
        binary_op   ::= BINARY_MODULO
        binary_op   ::= BINARY_LSHIFT
        binary_op   ::= BINARY_RSHIFT
        binary_op   ::= BINARY_POWER

        unary_expr  ::= expr unary_op
        unary_op    ::= UNARY_POSITIVE
        unary_op    ::= UNARY_NEGATIVE
        unary_op    ::= UNARY_INVERT

        unary_not ::= expr UNARY_NOT

        subscript ::= expr expr BINARY_SUBSCR

        attribute ::= expr LOAD_ATTR
        get_iter  ::= expr GET_ITER

        yield ::= expr YIELD_VALUE

        _mklambda ::= mklambda

        expr ::= conditional

        ret_expr ::= expr
        ret_expr ::= ret_and
        ret_expr ::= ret_or

        ret_expr_or_cond ::= ret_expr
        ret_expr_or_cond ::= ret_cond

        stmt ::= return_lambda

        return_lambda ::= ret_expr RETURN_VALUE_LAMBDA LAMBDA_MARKER
        return_lambda ::= ret_expr RETURN_VALUE_LAMBDA

        compare        ::= compare_chained
        compare        ::= compare_single
        compare_single ::= expr expr COMPARE_OP

        # A compare_chained is two comparisions like x <= y <= z
        compare_chained  ::= expr compare_chained1 ROT_TWO POP_TOP _come_froms
        compare_chained2 ::= expr COMPARE_OP JUMP_FORWARD

        # Non-null kvlist items are broken out in the indiviual grammars
        kvlist ::=

        # Positional arguments in make_function
        pos_arg ::= expr
        '''
        return self.n(node[0])

    def n_DUP_TOP(self, node):
        raise NotImplementedError(self.nameline('DUP_TOP', node))

    def n_designList(self, node):
        return self.n(node[0]) + self.n(node[-1])

    def n_store(self, node):
        '''
        # Note. The below is right-recursive:
        designList ::= store store
        designList ::= store DUP_TOP designList

        ## Can we replace with left-recursive, and redo with:
        ##
        ##   designList  ::= designLists store store
        ##   designLists ::= designLists store DUP_TOP
        ##   designLists ::=
        ## Will need to redo semantic actiion

        store        ::= STORE_FAST
        store        ::= STORE_NAME
        store        ::= STORE_GLOBAL
        store        ::= STORE_DEREF
        store        ::= expr STORE_ATTR
        store        ::= store_subscr
        store_subscr ::= expr expr STORE_SUBSCR
        store        ::= unpack
        '''
        if len(node) == 1:
            return self.n(node[0])
        elif node[-1].kind == "STORE_ATTR":
            return (rejig.syntaxtree.Call(".", self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart),)
        elif node[-1].kind == "STORE_SUBSCR":
            return (rejig.syntaxtree.Call("[.]", self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart),)
        else:
            raise NotImplementedError(self.nameline('store', node))

    def n_assign2(self, node):
        raise NotImplementedError(self.nameline('assign2', node))

    def n_assign3(self, node):
        raise NotImplementedError(self.nameline('assign3', node))

    def n_ROT_TWO(self, node):
        raise NotImplementedError(self.nameline('ROT_TWO', node))

    def n_ROT_THREE(self, node):
        raise NotImplementedError(self.nameline('ROT_THREE', node))

    def n_aug_assign1(self, node):
        raise NotImplementedError(self.nameline('aug_assign1', node))

    def n_aug_assign2(self, node):
        raise NotImplementedError(self.nameline('aug_assign2', node))

    def n_inplace_op(self, node):
        raise NotImplementedError(self.nameline('inplace_op', node))

    def n_STORE_SUBSCR(self, node):
        raise NotImplementedError(self.nameline('STORE_SUBSCR', node))

    def n_LOAD_ATTR(self, node):
        return node.pattr

    def n_STORE_ATTR(self, node):
        return node.pattr

    def n_INPLACE_ADD(self, node):
        raise NotImplementedError(self.nameline('INPLACE_ADD', node))

    def n_INPLACE_SUBTRACT(self, node):
        raise NotImplementedError(self.nameline('INPLACE_SUBTRACT', node))

    def n_INPLACE_MULTIPLY(self, node):
        raise NotImplementedError(self.nameline('INPLACE_MULTIPLY', node))

    def n_INPLACE_TRUE_DIVIDE(self, node):
        raise NotImplementedError(self.nameline('INPLACE_TRUE_DIVIDE', node))

    def n_INPLACE_FLOOR_DIVIDE(self, node):
        raise NotImplementedError(self.nameline('INPLACE_FLOOR_DIVIDE', node))

    def n_INPLACE_MODULO(self, node):
        raise NotImplementedError(self.nameline('INPLACE_MODULO', node))

    def n_INPLACE_POWER(self, node):
        raise NotImplementedError(self.nameline('INPLACE_POWER', node))

    def n_INPLACE_LSHIFT(self, node):
        raise NotImplementedError(self.nameline('INPLACE_LSHIFT', node))

    def n_INPLACE_RSHIFT(self, node):
        raise NotImplementedError(self.nameline('INPLACE_RSHIFT', node))

    def n_INPLACE_AND(self, node):
        raise NotImplementedError(self.nameline('INPLACE_AND', node))

    def n_INPLACE_XOR(self, node):
        raise NotImplementedError(self.nameline('INPLACE_XOR', node))

    def n_INPLACE_OR(self, node):
        raise NotImplementedError(self.nameline('INPLACE_OR', node))

    def n_call_stmt(self, node):
        '''
        # eval-mode compilation.  Single-mode interactive compilation
        # adds another rule.
        call_stmt ::= expr POP_TOP
        '''
        return self.n(node[0])

    def n_POP_TOP(self, node):
        raise NotImplementedError(self.nameline('POP_TOP', node))

    def n_list_for(self, node):
        raise NotImplementedError(self.nameline('list_for', node))

    def n_for_iter(self, node):
        raise NotImplementedError(self.nameline('for_iter', node))

    def n_list_iter(self, node):
        raise NotImplementedError(self.nameline('list_iter', node))

    def n_JUMP_BACK(self, node):
        raise NotImplementedError(self.nameline('JUMP_BACK', node))

    def n_come_froms(self, node):
        raise NotImplementedError(self.nameline('come_froms', node))

    def n_JUMP_FORWARD(self, node):
        raise NotImplementedError(self.nameline('JUMP_FORWARD', node))

    def n_COME_FROM(self, node):
        return None

    def n_jb_cont(self, node):
        raise NotImplementedError(self.nameline('jb_cont', node))

    def n_JUMP_ABSOLUTE(self, node):
        raise NotImplementedError(self.nameline('JUMP_ABSOLUTE', node))

    def n_jb_pop(self, node):
        raise NotImplementedError(self.nameline('jb_pop', node))

    def n_list_if(self, node):
        raise NotImplementedError(self.nameline('list_if', node))

    def n_list_comp(self, node):
        out = ()
        node = node[1][0]

        while True:
            src = self.n(node[0])
            args = self.n(node[2])[0]
            if node[3][0].kind == "list_if":
                pred = self.n(node[3][0][0])
                node = node[3][0][2]
            else:
                pred = None
                node = node[3]

            out = out + (src, args, pred)

            if node[0].kind == "lc_body":
                body = self.n(node[0][0])
                out = out + (body,)
                if self.pyversion < 3:
                    return self.make_comp(out[0], out)
                else:
                    return out
            else:
                node = node[0]

    def n_BUILD_LIST_0(self, node):
        raise NotImplementedError(self.nameline('BUILD_LIST_0', node))

    def n_del_stmt(self, node):
        raise NotImplementedError(self.nameline('del_stmt', node))

    def n_lc_body(self, node):
        raise NotImplementedError(self.nameline('lc_body', node))

    def n_LOAD_NAME(self, node):
        raise NotImplementedError(self.nameline('LOAD_NAME', node))

    def n_LIST_APPEND(self, node):
        raise NotImplementedError(self.nameline('LIST_APPEND', node))

    def n_LOAD_FAST(self, node):
        if node.pattr == "None":
            return rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart)
        elif node.pattr == "True":
            return rejig.syntaxtree.Const(True, sourcepath=self.sourcepath, linestart=node.linestart)
        elif node.pattr == "False":
            return rejig.syntaxtree.Const(False, sourcepath=self.sourcepath, linestart=node.linestart)
        else:
            return rejig.syntaxtree.Name(node.pattr, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_comp_for(self, node):
        raise NotImplementedError(self.nameline('comp_for', node))

    def n_SETUP_LOOP(self, node):
        raise NotImplementedError(self.nameline('SETUP_LOOP', node))

    def n_comp_iter(self, node):
        raise NotImplementedError(self.nameline('comp_iter', node))

    def n_jb_pb_come_from(self, node):
        raise NotImplementedError(self.nameline('jb_pb_come_from', node))

    def n_comp_body(self, node):
        raise NotImplementedError(self.nameline('comp_body', node))

    def n_gen_comp_body(self, node):
        raise NotImplementedError(self.nameline('gen_comp_body', node))

    def n_for_block(self, node):
        raise NotImplementedError(self.nameline('for_block', node))

    def n_l_stmts_opt(self, node):
        raise NotImplementedError(self.nameline('l_stmts_opt', node))

    def n__come_froms(self, node):
        raise NotImplementedError(self.nameline('_come_froms', node))

    def n_setup_loop_lf(self, node):
        raise NotImplementedError(self.nameline('setup_loop_lf', node))

    def n_genexpr_func(self, node):
        out = ()

        while True:
            src = self.n(node[0])
            args = self.n(node[2])[0]
            if node[3][0].kind == "comp_if":
                pred = self.n(node[3][0][0])
                node = node[3][0][2]
            else:
                pred = None
                node = node[3]

            out = out + (src, args, pred)

            if node[0].kind == "comp_body":
                body = self.n(node[0][0][0])
                out = out + (body,)
                return out
            else:
                node = node[0]

    def n_FOR_ITER(self, node):
        raise NotImplementedError(self.nameline('FOR_ITER', node))

    def n_come_from_pop(self, node):
        raise NotImplementedError(self.nameline('come_from_pop', node))

    def n_generator_exp(self, node):
        '''
        expr ::= generator_exp
        stmt ::= genexpr_func

        genexpr_func ::= LOAD_FAST FOR_ITER store comp_iter JUMP_BACK
        '''
        if node[3].kind == "GET_ITER":
            source = self.n(node[2])
        elif node[4].kind == "GET_ITER":
            source = self.n(node[3])
        else:
            raise NotImplementedError('generator_exp', node)
        loops = ast(self.n(node[0]), linestart=node.linestart).params[0]
        return self.make_comp(source, loops)

    def n_LOAD_GENEXPR(self, node):
        return node.attr

    def n_MAKE_FUNCTION_0(self, node):
        raise NotImplementedError(self.nameline('MAKE_FUNCTION_0', node))

    def n_GET_ITER(self, node):
        raise NotImplementedError(self.nameline('GET_ITER', node))

    def n_CALL_FUNCTION_1(self, node):
        raise NotImplementedError(self.nameline('CALL_FUNCTION_1', node))

    def n_jmp_false_then(self, node):
        raise NotImplementedError(self.nameline('jmp_false_then', node))

    def n_except_suite(self, node):
        raise NotImplementedError(self.nameline('except_suite', node))

    def n_c_stmts_opt(self, node):
        raise NotImplementedError(self.nameline('c_stmts_opt', node))

    def n_jmp_abs(self, node):
        raise NotImplementedError(self.nameline('jmp_abs', node))

    def n__mklambda(self, node):
        return self.n(node[0])
    
    def n_LOAD_CONST(self, node):
        return self.make_const(node.pattr, self.sourcepath, node.linestart)

    def n_LOAD_GLOBAL(self, node):
        if node.pattr == "None":
            return rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart)
        elif node.pattr == "True":
            return rejig.syntaxtree.Const(True, sourcepath=self.sourcepath, linestart=node.linestart)
        elif node.pattr == "False":
            return rejig.syntaxtree.Const(False, sourcepath=self.sourcepath, linestart=node.linestart)
        else:
            return rejig.syntaxtree.Name(node.pattr, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_LOAD_DEREF(self, node):
        raise NotImplementedError(self.nameline('LOAD_DEREF', node))

    def n_binary_expr(self, node):
        return rejig.syntaxtree.Call(self.n(node[2]), self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_list(self, node):
        return rejig.syntaxtree.Call("list", *[self.n(x) for x in node[:-1]], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_compare(self, node):
        return self.n(node[0])

    def n_dict(self, node):
        if len(node) == 1 and node[0].kind.startswith("kvlist_"):
            return rejig.syntaxtree.Call("dict", *[self.n(x) for x in node[0][:-1]], sourcepath=self.sourcepath, linestart=node.linestart)
        elif node[-1].kind.startswith("BUILD_CONST_KEY_MAP_"):
            pairs = []
            for i, x in enumerate(node[:-2]):
                pairs.append(rejig.syntaxtree.Const(node[-2].pattr[i], sourcepath=self.sourcepath, linestart=x.linestart))
                pairs.append(self.n(x))
            return rejig.syntaxtree.Call("dict", *pairs, sourcepath=self.sourcepath, linestart=node.linestart)
        else:
            pairs = []
            for pair in node[1:]:
                pairs.extend(self.n(pair))
            return rejig.syntaxtree.Call("dict", *pairs, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_and(self, node):
        args = [self.n(x) for x in node]
        return rejig.syntaxtree.Call("and", *[x for x in args if x is not None], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_or(self, node):
        args = [self.n(x) for x in node]
        return rejig.syntaxtree.Call("or", *[x for x in args if x is not None], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_unary_expr(self, node):
        return self.no_unary_plus(rejig.syntaxtree.Call(self.n(node[1]), self.n(node[0]), sourcepath=self.sourcepath, linestart=node.linestart))

    def n_call(self, node):
        if any(x.kind == "kwarg" for x in node):
            fcn = self.n(node[0])
            args = ()
            kwargs = ()
            for x in node[1:-1]:
                if x.kind == "kwarg":
                    kwargs = kwargs + (self.n(x),)
                else:
                    args = args + (self.n(x),)
            return rejig.syntaxtree.CallKeyword(fcn, args, kwargs, sourcepath=self.sourcepath, linestart=node.linestart)
        else:
            return rejig.syntaxtree.Call(*[self.n(x) for x in node[:-1]], sourcepath=self.sourcepath, linestart=node.linestart)

    def n_unary_not(self, node):
        return rejig.syntaxtree.Call("not", self.n(node[0]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_subscript(self, node):
        args = self.n(node[1])
        if isinstance(args, rejig.syntaxtree.Call) and args.fcn == "tuple":
            args = args.args
        else:
            args = (args,)
        return rejig.syntaxtree.Call("[.]", self.n(node[0]), *args, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_subscript2(self, node):
        raise NotImplementedError(self.nameline('subscript2', node))

    def n_yield(self, node):
        raise NotImplementedError(self.nameline('yield', node))

    def n_binary_op(self, node):
        return self.n(node[0])

    def n_BINARY_ADD(self, node):
        return "+"

    def n_BINARY_MULTIPLY(self, node):
        return "*"

    def n_BINARY_AND(self, node):
        return "&"

    def n_BINARY_OR(self, node):
        return "|"

    def n_BINARY_XOR(self, node):
        return "^"

    def n_BINARY_SUBTRACT(self, node):
        return "-"

    def n_BINARY_TRUE_DIVIDE(self, node):
        return "/"

    def n_BINARY_FLOOR_DIVIDE(self, node):
        return "//"

    def n_BINARY_MODULO(self, node):
        return "%"

    def n_BINARY_LSHIFT(self, node):
        return "<<"

    def n_BINARY_RSHIFT(self, node):
        return ">>"

    def n_BINARY_POWER(self, node):
        return "**"

    def n_unary_op(self, node):
        return self.n(node[0])

    def n_UNARY_POSITIVE(self, node):
        return "u+"

    def n_UNARY_NEGATIVE(self, node):
        return "u-"

    def n_UNARY_INVERT(self, node):
        return "~"

    def n_UNARY_NOT(self, node):
        raise NotImplementedError(self.nameline('UNARY_NOT', node))

    def n_BINARY_SUBSCR(self, node):
        raise NotImplementedError(self.nameline('BINARY_SUBSCR', node))

    def n_attribute(self, node):
        return rejig.syntaxtree.Call(".", self.n(node[0]), node[1].pattr, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_get_iter(self, node):
        return self.n(node[0])

    def n_YIELD_VALUE(self, node):
        raise NotImplementedError(self.nameline('YIELD_VALUE', node))

    def n_mklambda(self, node):
        code = node[0].attr
        return rejig.syntaxtree.Def(code.co_varnames[:code.co_argcount], (), ast(code, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_conditional(self, node):
        return rejig.syntaxtree.Call("?", self.n(node[0]), self.n(node[2]), self.n(node[4]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_ret_expr(self, node):
        return rejig.syntaxtree.Call("return", self.n(node[0]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_ret_and(self, node):
        raise NotImplementedError(self.nameline('ret_and', node))

    def n_ret_or(self, node):
        raise NotImplementedError(self.nameline('ret_or', node))

    def n_ret_expr_or_cond(self, node):
        raise NotImplementedError(self.nameline('ret_expr_or_cond', node))

    def n_ret_cond(self, node):
        raise NotImplementedError(self.nameline('ret_cond', node))

    def n_return_lambda(self, node):
        raise NotImplementedError(self.nameline('return_lambda', node))

    def n_RETURN_VALUE_LAMBDA(self, node):
        raise NotImplementedError(self.nameline('RETURN_VALUE_LAMBDA', node))

    def n_LAMBDA_MARKER(self, node):
        raise NotImplementedError(self.nameline('LAMBDA_MARKER', node))

    def n_compare_chained(self, node):
        expr = self.n(node[0])
        rest = self.n(node[1])
        rest[0].args = (expr,) + rest[0].args
        return rejig.syntaxtree.Call("and", *rest, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_compare_single(self, node):
        return rejig.syntaxtree.Call(self.n(node[2]), self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_COMPARE_OP(self, node):
        return node.pattr

    def n_compare_chained1(self, node):
        expr = self.n(node[0])
        op = self.n(node[3])
        rest = self.n(node[5])
        rest[0].args = (expr,) + rest[0].args
        return (rejig.syntaxtree.Call(op, expr, sourcepath=self.sourcepath, linestart=node.linestart),) + rest

    def n_compare_chained2(self, node):
        expr = self.n(node[0])
        op = self.n(node[1])
        return (rejig.syntaxtree.Call(op, expr, sourcepath=self.sourcepath, linestart=node.linestart),)

    def n_kvlist(self, node):
        raise NotImplementedError(self.nameline('kvlist', node))

    def n_pos_arg(self, node):
        return self.n(node[0])

    def n_LOAD_LOCALS(self, node):
        raise NotImplementedError(self.nameline('LOAD_LOCALS', node))

    def n_LOAD_ASSERT(self, node):
        raise NotImplementedError(self.nameline('LOAD_ASSERT', node))

    def n_slice0(self, node):
        return rejig.syntaxtree.Call("[.]", self.n(node[0]), rejig.syntaxtree.Call("slice", rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_slice1(self, node):
        return rejig.syntaxtree.Call("[.]", self.n(node[0]), rejig.syntaxtree.Call("slice", self.n(node[1]), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_slice2(self, node):
        '''
        store ::= expr STORE_SLICE+0
        store ::= expr expr STORE_SLICE+1
        store ::= expr expr STORE_SLICE+2
        store ::= expr expr expr STORE_SLICE+3

        aug_assign1 ::= expr expr inplace_op ROT_FOUR  STORE_SLICE+3
        aug_assign1 ::= expr expr inplace_op ROT_THREE STORE_SLICE+1
        aug_assign1 ::= expr expr inplace_op ROT_THREE STORE_SLICE+2
        aug_assign1 ::= expr expr inplace_op ROT_TWO   STORE_SLICE+0

        slice0 ::= expr SLICE+0
        slice0 ::= expr DUP_TOP SLICE+0
        slice1 ::= expr expr SLICE+1
        slice1 ::= expr expr DUP_TOPX_2 SLICE+1
        slice2 ::= expr expr SLICE+2
        slice2 ::= expr expr DUP_TOPX_2 SLICE+2
        slice3 ::= expr expr expr SLICE+3
        slice3 ::= expr expr expr DUP_TOPX_3 SLICE+3
        '''
        return rejig.syntaxtree.Call("[.]", self.n(node[0]), rejig.syntaxtree.Call("slice", rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), self.n(node[1]), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_slice3(self, node):
        return rejig.syntaxtree.Call("[.]", self.n(node[0]), rejig.syntaxtree.Call("slice", self.n(node[1]), self.n(node[2]), rejig.syntaxtree.Const(None, sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_unary_convert(self, node):
        raise NotImplementedError(self.nameline('unary_convert', node))

    def n_jmp_false(self, node):
        return None

    def n_come_from_opt(self, node):
        raise NotImplementedError(self.nameline('come_from_opt', node))

    def n_jmp_true(self, node):
        return None

    def n_UNARY_CONVERT(self, node):
        raise NotImplementedError(self.nameline('UNARY_CONVERT', node))

    def n_DUP_TOPX_2(self, node):
        raise NotImplementedError(self.nameline('DUP_TOPX_2', node))

    def n_forelsestmt(self, node):
        raise NotImplementedError(self.nameline('forelsestmt', node))

    def n_POP_BLOCK(self, node):
        raise NotImplementedError(self.nameline('POP_BLOCK', node))

    def n_else_suite(self, node):
        return self.n(node[0])

    def n_forelselaststmt(self, node):
        raise NotImplementedError(self.nameline('forelselaststmt', node))

    def n_else_suitec(self, node):
        raise NotImplementedError(self.nameline('else_suitec', node))

    def n_forelselaststmtl(self, node):
        raise NotImplementedError(self.nameline('forelselaststmtl', node))

    def n_else_suitel(self, node):
        raise NotImplementedError(self.nameline('else_suitel', node))

    def n_for(self, node):
        raise NotImplementedError(self.nameline('for', node))

    def n_returns(self, node):
        if node[0].kind == "_stmts" and len(node[0]) > 1 and node[0][0][0].kind == "ifstmt":
            out = self.n(node[0][0][0])
            assert isinstance(out, rejig.syntaxtree.Call) and out.fcn == "if"
            assert len(out.args) == 2
            out.args = out.args + (rejig.syntaxtree.Suite(tuple(self.n(x) for x in node[0][1:]), sourcepath=self.sourcepath, linestart=node.linestart),)
            return out
        else:
            return self.n(node[0])

    def n__jump_back(self, node):
        raise NotImplementedError(self.nameline('_jump_back', node))

    def n_function_def(self, node):
        '''
        stmt               ::= function_def
        function_def       ::= mkfunc store
        stmt               ::= function_def_deco
        function_def_deco  ::= mkfuncdeco store
        mkfuncdeco         ::= expr mkfuncdeco CALL_FUNCTION_1
        mkfuncdeco         ::= expr mkfuncdeco0 CALL_FUNCTION_1
        mkfuncdeco0        ::= mkfunc
        load_closure       ::= load_closure LOAD_CLOSURE
        load_closure       ::= LOAD_CLOSURE
        '''
        return rejig.syntaxtree.Assign(self.n(node[-1]), self.n(node[0]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_mkfunc(self, node):
        code = node[0].attr
        return rejig.syntaxtree.Def(code.co_varnames[:code.co_argcount], (), ast(code, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_function_def_deco(self, node):
        raise NotImplementedError(self.nameline('function_def_deco', node))

    def n_mkfuncdeco(self, node):
        raise NotImplementedError(self.nameline('mkfuncdeco', node))

    def n_mkfuncdeco0(self, node):
        raise NotImplementedError(self.nameline('mkfuncdeco0', node))

    def n_load_closure(self, node):
        raise NotImplementedError(self.nameline('load_closure', node))

    def n_LOAD_CLOSURE(self, node):
        raise NotImplementedError(self.nameline('LOAD_CLOSURE', node))

    def n_sstmt(self, node):
        return self.n(node[0])

    def n_return(self, node):
        return self.n(node[0])

    def n_RETURN_LAST(self, node):
        raise NotImplementedError(self.nameline('RETURN_LAST', node))

    def n_return_if_stmts(self, node):
        out = self.make_suite(node, self.sourcepath, node.linestart)
        if not (isinstance(out.body[-1], rejig.syntaxtree.Call) and out.body[-1].fcn == "return"):
            out.body = out.body[:-1] + (rejig.syntaxtree.Call("return", out.body[-1], sourcepath=self.sourcepath, linestart=node.linestart),)
        return out

    def n_return_if_stmt(self, node):
        return self.n(node[0])

    def n__stmts(self, node):
        return self.n(node[0])

    def n_RETURN_END_IF(self, node):
        raise NotImplementedError(self.nameline('RETURN_END_IF', node))

    def n_return_stmt_lambda(self, node):
        raise NotImplementedError(self.nameline('return_stmt_lambda', node))

    def n_break(self, node):
        raise NotImplementedError(self.nameline('break', node))

    def n_BREAK_LOOP(self, node):
        raise NotImplementedError(self.nameline('BREAK_LOOP', node))

    def n_continue(self, node):
        raise NotImplementedError(self.nameline('continue', node))

    def n_CONTINUE(self, node):
        raise NotImplementedError(self.nameline('CONTINUE', node))

    def n_continues(self, node):
        raise NotImplementedError(self.nameline('continues', node))

    def n_lastl_stmt(self, node):
        raise NotImplementedError(self.nameline('lastl_stmt', node))

    def n_assert2(self, node):
        raise NotImplementedError(self.nameline('assert2', node))

    def n_raise_stmt0(self, node):
        raise NotImplementedError(self.nameline('raise_stmt0', node))

    def n_raise_stmt1(self, node):
        raise NotImplementedError(self.nameline('raise_stmt1', node))

    def n_raise_stmt2(self, node):
        raise NotImplementedError(self.nameline('raise_stmt2', node))

    def n_raise_stmt3(self, node):
        raise NotImplementedError(self.nameline('raise_stmt3', node))

    def n_RAISE_VARARGS_0(self, node):
        raise NotImplementedError(self.nameline('RAISE_VARARGS_0', node))

    def n_RAISE_VARARGS_1(self, node):
        raise NotImplementedError(self.nameline('RAISE_VARARGS_1', node))

    def n_RAISE_VARARGS_2(self, node):
        raise NotImplementedError(self.nameline('RAISE_VARARGS_2', node))

    def n_RAISE_VARARGS_3(self, node):
        raise NotImplementedError(self.nameline('RAISE_VARARGS_3', node))

    def n_DELETE_SLICE(self, node):
        raise NotImplementedError(self.nameline('DELETE_SLICE', node))

    def n_0(self, node):
        raise NotImplementedError(self.nameline('0', node))

    def n_1(self, node):
        raise NotImplementedError(self.nameline('1', node))

    def n_2(self, node):
        raise NotImplementedError(self.nameline('2', node))

    def n_3(self, node):
        raise NotImplementedError(self.nameline('3', node))

    def n_delete_subscr(self, node):
        raise NotImplementedError(self.nameline('delete_subscr', node))

    def n_DELETE_SUBSCR(self, node):
        raise NotImplementedError(self.nameline('DELETE_SUBSCR', node))

    def n_DELETE_ATTR(self, node):
        raise NotImplementedError(self.nameline('DELETE_ATTR', node))

    def n_kwarg(self, node):
        return (node[0].pattr, self.n(node[1]))

    def n_kv3(self, node):
        return self.n(node[1]), self.n(node[0])

    def n_STORE_MAP(self, node):
        raise NotImplementedError(self.nameline('STORE_MAP', node))

    def n_classdef(self, node):
        raise NotImplementedError(self.nameline('classdef', node))

    def n_buildclass(self, node):
        raise NotImplementedError(self.nameline('buildclass', node))

    def n_CALL_FUNCTION_0(self, node):
        raise NotImplementedError(self.nameline('CALL_FUNCTION_0', node))

    def n_BUILD_CLASS(self, node):
        raise NotImplementedError(self.nameline('BUILD_CLASS', node))

    def n_classdefdeco(self, node):
        raise NotImplementedError(self.nameline('classdefdeco', node))

    def n_classdefdeco1(self, node):
        raise NotImplementedError(self.nameline('classdefdeco1', node))

    def n_classdefdeco2(self, node):
        raise NotImplementedError(self.nameline('classdefdeco2', node))

    def n_assert_expr(self, node):
        raise NotImplementedError(self.nameline('assert_expr', node))

    def n_assert_expr_or(self, node):
        raise NotImplementedError(self.nameline('assert_expr_or', node))

    def n_assert_expr_and(self, node):
        raise NotImplementedError(self.nameline('assert_expr_and', node))

    def n_ifstmt(self, node):
        if node[1].kind == "return_if_stmts":
            return rejig.syntaxtree.Call("if", self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart)
        else:
            jump = node[0][0][1][0].attr
            alternate = self.find_offset(node[1], jump)[1]
            if alternate is None:
                return rejig.syntaxtree.Call("if", self.n(node[0]), self.n(node[1]), sourcepath=self.sourcepath, linestart=node.linestart)
            else:
                alternate = self.make_suite(alternate, self.sourcepath, node.linestart)
                return rejig.syntaxtree.Call("if", self.n(node[0]), self.n(node[1]), alternate, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_testexpr(self, node):
        return self.n(node[0])

    def n__ifstmts_jump(self, node):
        return self.n(node[0])

    def n_testfalse(self, node):
        return self.n(node[0])

    def n_testtrue(self, node):
        return self.n(node[0])

    def n_iflaststmt(self, node):
        raise NotImplementedError(self.nameline('iflaststmt', node))

    def n_iflaststmtl(self, node):
        raise NotImplementedError(self.nameline('iflaststmtl', node))

    def n_tryfinallystmt(self, node):
        raise NotImplementedError(self.nameline('tryfinallystmt', node))

    def n_SETUP_FINALLY(self, node):
        raise NotImplementedError(self.nameline('SETUP_FINALLY', node))

    def n_suite_stmts_opt(self, node):
        raise NotImplementedError(self.nameline('suite_stmts_opt', node))

    def n_END_FINALLY(self, node):
        raise NotImplementedError(self.nameline('END_FINALLY', node))

    def n_lastc_stmt(self, node):
        raise NotImplementedError(self.nameline('lastc_stmt', node))

    def n_tryelsestmtc(self, node):
        raise NotImplementedError(self.nameline('tryelsestmtc', node))

    def n_SETUP_EXCEPT(self, node):
        raise NotImplementedError(self.nameline('SETUP_EXCEPT', node))

    def n_except_handler(self, node):
        raise NotImplementedError(self.nameline('except_handler', node))

    def n_tryelsestmtl(self, node):
        raise NotImplementedError(self.nameline('tryelsestmtl', node))

    def n_try_except(self, node):
        raise NotImplementedError(self.nameline('try_except', node))

    def n_except_stmts(self, node):
        raise NotImplementedError(self.nameline('except_stmts', node))

    def n_except_stmt(self, node):
        raise NotImplementedError(self.nameline('except_stmt', node))

    def n_except_cond1(self, node):
        raise NotImplementedError(self.nameline('except_cond1', node))

    def n_except(self, node):
        raise NotImplementedError(self.nameline('except', node))

    def n__jump(self, node):
        raise NotImplementedError(self.nameline('_jump', node))

    def n_import(self, node):
        raise NotImplementedError(self.nameline('import', node))

    def n_filler(self, node):
        raise NotImplementedError(self.nameline('filler', node))

    def n_IMPORT_NAME(self, node):
        raise NotImplementedError(self.nameline('IMPORT_NAME', node))

    def n_STORE_FAST(self, node):
        return (rejig.syntaxtree.Name(node.pattr, sourcepath=self.sourcepath, linestart=node.linestart),)

    def n_STORE_NAME(self, node):
        raise NotImplementedError(self.nameline('STORE_NAME', node))

    def n_import_from(self, node):
        raise NotImplementedError(self.nameline('import_from', node))

    def n_importlist(self, node):
        raise NotImplementedError(self.nameline('importlist', node))

    def n_IMPORT_FROM(self, node):
        raise NotImplementedError(self.nameline('IMPORT_FROM', node))

    def n_import_from_star(self, node):
        raise NotImplementedError(self.nameline('import_from_star', node))

    def n_importmultiple(self, node):
        raise NotImplementedError(self.nameline('importmultiple', node))

    def n_alias(self, node):
        raise NotImplementedError(self.nameline('alias', node))

    def n_attributes(self, node):
        raise NotImplementedError(self.nameline('attributes', node))

    def n_IMPORT_STAR(self, node):
        raise NotImplementedError(self.nameline('IMPORT_STAR', node))

    def n_imports_cont(self, node):
        raise NotImplementedError(self.nameline('imports_cont', node))

    def n_import_cont(self, node):
        raise NotImplementedError(self.nameline('import_cont', node))

    def n_IMPORT_NAME_CONT(self, node):
        raise NotImplementedError(self.nameline('IMPORT_NAME_CONT', node))

    def n_JUMP_IF_TRUE(self, node):
        raise NotImplementedError(self.nameline('JUMP_IF_TRUE', node))

    def n_JUMP_IF_FALSE(self, node):
        raise NotImplementedError(self.nameline('JUMP_IF_FALSE', node))

    def n_jf_pop(self, node):
        raise NotImplementedError(self.nameline('jf_pop', node))

    def n_jb_cf_pop(self, node):
        raise NotImplementedError(self.nameline('jb_cf_pop', node))

    def n_ja_cf_pop(self, node):
        raise NotImplementedError(self.nameline('ja_cf_pop', node))

    def n_jf_cf_pop(self, node):
        raise NotImplementedError(self.nameline('jf_cf_pop', node))

    def n_cf_jb_cf_pop(self, node):
        raise NotImplementedError(self.nameline('cf_jb_cf_pop', node))

    def n_bp_come_from(self, node):
        raise NotImplementedError(self.nameline('bp_come_from', node))

    def n_come_froms_pop(self, node):
        raise NotImplementedError(self.nameline('come_froms_pop', node))

    def n_list_if_not(self, node):
        raise NotImplementedError(self.nameline('list_if_not', node))

    def n_doc_junk(self, node):
        raise NotImplementedError(self.nameline('doc_junk', node))

    def n_jb_pop14(self, node):
        raise NotImplementedError(self.nameline('jb_pop14', node))

    def n_whileelsestmt(self, node):
        raise NotImplementedError(self.nameline('whileelsestmt', node))

    def n_print_items_nl_stmt(self, node):
        fcn = rejig.syntaxtree.Name("print", sourcepath=self.sourcepath, linestart=node.linestart)
        args = [self.n(x) for x in node[:-3]]
        return rejig.syntaxtree.Call(*([fcn] + args))

    def n_PRINT_ITEM_CONT(self, node):
        raise NotImplementedError(self.nameline('PRINT_ITEM_CONT', node))

    def n_print_items_opt(self, node):
        raise NotImplementedError(self.nameline('print_items_opt', node))

    def n_PRINT_NEWLINE_CONT(self, node):
        raise NotImplementedError(self.nameline('PRINT_NEWLINE_CONT', node))

    def n_FOR_LOOP(self, node):
        raise NotImplementedError(self.nameline('FOR_LOOP', node))

    def n_print_items_stmt(self, node):
        raise NotImplementedError(self.nameline('print_items_stmt', node))

    def n_if1_stmt(self, node):
        raise NotImplementedError(self.nameline('if1_stmt', node))

    def n_THEN(self, node):
        raise NotImplementedError(self.nameline('THEN', node))

    def n_stmts(self, node):
        return self.make_suite(node, self.sourcepath, node.linestart)

    def n__while1test(self, node):
        raise NotImplementedError(self.nameline('_while1test', node))

    def n_while1stmt(self, node):
        raise NotImplementedError(self.nameline('while1stmt', node))

    def n_and2(self, node):
        raise NotImplementedError(self.nameline('and2', node))

    def n_nop_stmt(self, node):
        raise NotImplementedError(self.nameline('nop_stmt', node))

    def n_iftrue_stmt24(self, node):
        raise NotImplementedError(self.nameline('iftrue_stmt24', node))

    def n__ifstmts_jump24(self, node):
        raise NotImplementedError(self.nameline('_ifstmts_jump24', node))

    def n_suite_stmts(self, node):
        return self.make_suite(node, self.sourcepath, node.linestart)

    def n_kv2(self, node):
        raise NotImplementedError(self.nameline('kv2', node))

    def n_setupwithas(self, node):
        raise NotImplementedError(self.nameline('setupwithas', node))

    def n_setup_finally(self, node):
        raise NotImplementedError(self.nameline('setup_finally', node))

    def n_setupwith(self, node):
        raise NotImplementedError(self.nameline('setupwith', node))

    def n_withstmt(self, node):
        raise NotImplementedError(self.nameline('withstmt', node))

    def n_with_cleanup(self, node):
        raise NotImplementedError(self.nameline('with_cleanup', node))

    def n_tryelsestmt(self, node):
        raise NotImplementedError(self.nameline('tryelsestmt', node))

    def n_withasstmt(self, node):
        raise NotImplementedError(self.nameline('withasstmt', node))

    def n_DELETE_FAST(self, node):
        raise NotImplementedError(self.nameline('DELETE_FAST', node))

    def n_WITH_CLEANUP(self, node):
        raise NotImplementedError(self.nameline('WITH_CLEANUP', node))

    def n_DELETE_NAME(self, node):
        raise NotImplementedError(self.nameline('DELETE_NAME', node))

    def n_kv(self, node):
        raise NotImplementedError(self.nameline('kv', node))

    def n_BUILD_MAP(self, node):
        raise NotImplementedError(self.nameline('BUILD_MAP', node))

    def n_conditional_not(self, node):
        raise NotImplementedError(self.nameline('conditional_not', node))

    def n_RETURN_VALUE(self, node):
        raise NotImplementedError(self.nameline('RETURN_VALUE', node))

    def n_RETURN_END_IF_LAMBDA(self, node):
        raise NotImplementedError(self.nameline('RETURN_END_IF_LAMBDA', node))

    def n_return_if_lambda(self, node):
        raise NotImplementedError(self.nameline('return_if_lambda', node))

    def n_conditional_lambda(self, node):
        raise NotImplementedError(self.nameline('conditional_lambda', node))

    def n_conditional_not_lambda(self, node):
        raise NotImplementedError(self.nameline('conditional_not_lambda', node))

    def n_jmp_true_then(self, node):
        raise NotImplementedError(self.nameline('jmp_true_then', node))

    def n_conditional_true(self, node):
        raise NotImplementedError(self.nameline('conditional_true', node))

    def n_conditional_false(self, node):
        raise NotImplementedError(self.nameline('conditional_false', node))

    def n_INPLACE_DIVIDE(self, node):
        raise NotImplementedError(self.nameline('INPLACE_DIVIDE', node))

    def n_BINARY_DIVIDE(self, node):
        return "/"

    def n_print_nl(self, node):
        raise NotImplementedError(self.nameline('print_nl', node))

    def n_PRINT_ITEM(self, node):
        raise NotImplementedError(self.nameline('PRINT_ITEM', node))

    def n_print_items(self, node):
        raise NotImplementedError(self.nameline('print_items', node))

    def n_print_item(self, node):
        raise NotImplementedError(self.nameline('print_item', node))

    def n_PRINT_NEWLINE(self, node):
        raise NotImplementedError(self.nameline('PRINT_NEWLINE', node))

    def n_print_to(self, node):
        '''
        stmt ::= print_to
        stmt ::= print_to_nl
        stmt ::= print_nl_to
        print_to ::= expr print_to_items POP_TOP
        print_to_nl ::= expr print_to_items PRINT_NEWLINE_TO
        print_nl_to ::= expr PRINT_NEWLINE_TO
        print_to_items ::= print_to_items print_to_item
        print_to_items ::= print_to_item
        print_to_item ::= DUP_TOP expr ROT_TWO PRINT_ITEM_TO
        '''
        raise NotImplementedError(self.nameline('print_to', node))

    def n_print_to_nl(self, node):
        raise NotImplementedError(self.nameline('print_to_nl', node))

    def n_print_nl_to(self, node):
        raise NotImplementedError(self.nameline('print_nl_to', node))

    def n_print_to_items(self, node):
        raise NotImplementedError(self.nameline('print_to_items', node))

    def n_PRINT_NEWLINE_TO(self, node):
        raise NotImplementedError(self.nameline('PRINT_NEWLINE_TO', node))

    def n_print_to_item(self, node):
        raise NotImplementedError(self.nameline('print_to_item', node))

    def n_PRINT_ITEM_TO(self, node):
        raise NotImplementedError(self.nameline('PRINT_ITEM_TO', node))

    def n_comp_if(self, node):
        raise NotImplementedError(self.nameline('comp_if', node))

    def n_STORE_SLICE(self, node):
        raise NotImplementedError(self.nameline('STORE_SLICE', node))

    def n_ROT_FOUR(self, node):
        raise NotImplementedError(self.nameline('ROT_FOUR', node))

    def n_SLICE(self, node):
        raise NotImplementedError(self.nameline('SLICE', node))

    def n_DUP_TOPX_3(self, node):
        raise NotImplementedError(self.nameline('DUP_TOPX_3', node))

    def n_pass(self, node):
        raise NotImplementedError(self.nameline('pass', node))

    def n_c_stmts(self, node):
        return self.make_suite(node, self.sourcepath, node.linestart)

    def n_ifelsestmtc(self, node):
        raise NotImplementedError(self.nameline('ifelsestmtc', node))

    def n_l_stmts(self, node):
        raise NotImplementedError(self.nameline('l_stmts', node))

    def n_ifelsestmtl(self, node):
        raise NotImplementedError(self.nameline('ifelsestmtl', node))

    def n_assert(self, node):
        raise NotImplementedError(self.nameline('assert', node))

    def n_ifelsestmt(self, node):
        return rejig.syntaxtree.Call("if", self.n(node[0]), self.n(node[1]), self.n(node[3]), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_whilestmt(self, node):
        raise NotImplementedError(self.nameline('whilestmt', node))

    def n_while1elsestmt(self, node):
        raise NotImplementedError(self.nameline('while1elsestmt', node))

    def n_DELETE_GLOBAL(self, node):
        raise NotImplementedError(self.nameline('DELETE_GLOBAL', node))

    def n_testexpr_then(self, node):
        raise NotImplementedError(self.nameline('testexpr_then', node))

    def n_testtrue_then(self, node):
        raise NotImplementedError(self.nameline('testtrue_then', node))

    def n_testfalse_then(self, node):
        raise NotImplementedError(self.nameline('testfalse_then', node))

    def n_STORE_GLOBAL(self, node):
        raise NotImplementedError(self.nameline('STORE_GLOBAL', node))

    def n_STORE_DEREF(self, node):
        raise NotImplementedError(self.nameline('STORE_DEREF', node))

    def n_store_subscr(self, node):
        args = self.n(node[1])
        if isinstance(args, rejig.syntaxtree.Call) and args.fcn == "tuple":
            args = args.args
        else:
            args = (args,)
        return (rejig.syntaxtree.Call("[.]", self.n(node[0]), *args, sourcepath=self.sourcepath, linestart=node.linestart),)

    def n_unpack(self, node):
        return (rejig.syntaxtree.Unpack(sum((self.n(x) for x in node[1:]), ()), sourcepath=self.sourcepath, linestart=node.linestart),)

    def n_except_cond3(self, node):
        raise NotImplementedError(self.nameline('except_cond3', node))

    def n_PRINT_EXPR(self, node):
        raise NotImplementedError(self.nameline('PRINT_EXPR', node))

    def n_set_comp_func(self, node):
        raise NotImplementedError(self.nameline('set_comp_func', node))

    def n_dict_comp(self, node):
        raise NotImplementedError(self.nameline('dict_comp', node))

    def n_LOAD_DICTCOMP(self, node):
        raise NotImplementedError(self.nameline('LOAD_DICTCOMP', node))

    def n_dict_comp_func(self, node):
        raise NotImplementedError(self.nameline('dict_comp_func', node))

    def n_BUILD_MAP_0(self, node):
        raise NotImplementedError(self.nameline('BUILD_MAP_0', node))

    def n_BUILD_SET_0(self, node):
        raise NotImplementedError(self.nameline('BUILD_SET_0', node))

    def n_comp_if_not(self, node):
        raise NotImplementedError(self.nameline('comp_if_not', node))

    def n_dict_comp_body(self, node):
        raise NotImplementedError(self.nameline('dict_comp_body', node))

    def n_set_comp_body(self, node):
        raise NotImplementedError(self.nameline('set_comp_body', node))

    def n_MAP_ADD(self, node):
        raise NotImplementedError(self.nameline('MAP_ADD', node))

    def n_SET_ADD(self, node):
        raise NotImplementedError(self.nameline('SET_ADD', node))

    def n_POP_JUMP_IF_FALSE(self, node):
        raise NotImplementedError(self.nameline('POP_JUMP_IF_FALSE', node))

    def n_POP_JUMP_IF_TRUE(self, node):
        raise NotImplementedError(self.nameline('POP_JUMP_IF_TRUE', node))

    def n_JUMP_IF_FALSE_OR_POP(self, node):
        return None

    def n_JUMP_IF_TRUE_OR_POP(self, node):
        return None

    def n_SETUP_WITH(self, node):
        raise NotImplementedError(self.nameline('SETUP_WITH', node))

    def n_COME_FROM_WITH(self, node):
        raise NotImplementedError(self.nameline('COME_FROM_WITH', node))

    def n_return_stmts(self, node):
        raise NotImplementedError(self.nameline('return_stmts', node))

    def n_return_stmt(self, node):
        raise NotImplementedError(self.nameline('return_stmt', node))

    def n_COME_FROM_FINALLY(self, node):
        raise NotImplementedError(self.nameline('COME_FROM_FINALLY', node))

    def n_except_cond2(self, node):
        raise NotImplementedError(self.nameline('except_cond2', node))

    def n_whileTruestmt(self, node):
        raise NotImplementedError(self.nameline('whileTruestmt', node))

    def n_COME_FROM_LOOP(self, node):
        raise NotImplementedError(self.nameline('COME_FROM_LOOP', node))

    def n_jb_pop_top(self, node):
        raise NotImplementedError(self.nameline('jb_pop_top', node))

    def n_set_comp_func_header(self, node):
        raise NotImplementedError(self.nameline('set_comp_func_header', node))

    def n_list_comp_header(self, node):
        raise NotImplementedError(self.nameline('list_comp_header', node))

    def n_set_comp_header(self, node):
        raise NotImplementedError(self.nameline('set_comp_header', node))

    def n_set_comp(self, node):
        raise NotImplementedError(self.nameline('dict_comp_header', node))

    def n_dict_comp_header(self, node):
        raise NotImplementedError(self.nameline('dict_comp_header', node))

    def n_dict_comp_iter(self, node):
        raise NotImplementedError(self.nameline('dict_comp_iter', node))

    def n_jump_forward_else(self, node):
        raise NotImplementedError(self.nameline('jump_forward_else', node))

    def n_jump_absolute_else(self, node):
        raise NotImplementedError(self.nameline('jump_absolute_else', node))

    def n_POP_EXCEPT(self, node):
        raise NotImplementedError(self.nameline('POP_EXCEPT', node))

    def n_jump_except(self, node):
        raise NotImplementedError(self.nameline('jump_except', node))

    def n_except_suite_finalize(self, node):
        raise NotImplementedError(self.nameline('except_suite_finalize', node))

    def n_except_var_finalize(self, node):
        raise NotImplementedError(self.nameline('except_var_finalize', node))

    def n_COME_FROM_EXCEPT(self, node):
        raise NotImplementedError(self.nameline('COME_FROM_EXCEPT', node))

    def n_DUP_TOPX(self, node):
        raise NotImplementedError(self.nameline('DUP_TOPX', node))

    def n_load(self, node):
        raise NotImplementedError(self.nameline('load', node))

    def n_setupwithas31(self, node):
        raise NotImplementedError(self.nameline('setupwithas31', node))

    def n_DUP_TOP_TWO(self, node):
        raise NotImplementedError(self.nameline('DUP_TOP_TWO', node))

    def n_store_locals(self, node):
        raise NotImplementedError(self.nameline('store_locals', node))

    def n_STORE_LOCALS(self, node):
        raise NotImplementedError(self.nameline('STORE_LOCALS', node))

    def n_jump_excepts(self, node):
        raise NotImplementedError(self.nameline('jump_excepts', node))

    def n_come_from_except_clauses(self, node):
        raise NotImplementedError(self.nameline('come_from_except_clauses', node))

    def n_opt_come_from_except(self, node):
        raise NotImplementedError(self.nameline('opt_come_from_except', node))

    def n_COME_FROM_EXCEPT_CLAUSE(self, node):
        raise NotImplementedError(self.nameline('COME_FROM_EXCEPT_CLAUSE', node))

    def n_jb_or_c(self, node):
        raise NotImplementedError(self.nameline('jb_or_c', node))

    def n_function_def_annotate(self, node):
        raise NotImplementedError(self.nameline('function_def_annotate', node))

    def n_mkfunc_annotate(self, node):
        raise NotImplementedError(self.nameline('mkfunc_annotate', node))

    def n_annotate_arg(self, node):
        raise NotImplementedError(self.nameline('annotate_arg', node))

    def n_annotate_tuple(self, node):
        raise NotImplementedError(self.nameline('annotate_tuple', node))

    def n_conditionalnot(self, node):
        raise NotImplementedError(self.nameline('conditionalnot', node))

    def n_load_genexpr(self, node):
        return self.n(node[0])

    def n_BUILD_TUPLE_1(self, node):
        raise NotImplementedError(self.nameline('BUILD_TUPLE_1', node))

    def n_ifelsestmtr(self, node):
        return rejig.syntaxtree.Call("if", self.n(node[0]), rejig.syntaxtree.Suite((self.n(node[1][0]),), sourcepath=self.sourcepath, linestart=node.linestart), rejig.syntaxtree.Suite((self.n(node[2]),), sourcepath=self.sourcepath, linestart=node.linestart), sourcepath=self.sourcepath, linestart=node.linestart)

    def n_kwargs(self, node):
        raise NotImplementedError(self.nameline('kwargs', node))

    def n_build_class(self, node):
        raise NotImplementedError(self.nameline('build_class', node))

    def n_LOAD_BUILD_CLASS(self, node):
        raise NotImplementedError(self.nameline('LOAD_BUILD_CLASS', node))

    def n_CALL_FUNCTION_3(self, node):
        raise NotImplementedError(self.nameline('CALL_FUNCTION_3', node))

    def n_CALL_FUNCTION_4(self, node):
        raise NotImplementedError(self.nameline('CALL_FUNCTION_4', node))

    def n_ELSE(self, node):
        raise NotImplementedError(self.nameline('ELSE', node))

    def n_cf_jump_back(self, node):
        raise NotImplementedError(self.nameline('cf_jump_back', node))

    def n_except_pop_except(self, node):
        raise NotImplementedError(self.nameline('except_pop_except', node))

    def n_NOP(self, node):
        raise NotImplementedError(self.nameline('NOP', node))

    def n_return_closure(self, node):
        raise NotImplementedError(self.nameline('return_closure', node))

    def n_yield_from(self, node):
        raise NotImplementedError(self.nameline('yield_from', node))

    def n_YIELD_FROM(self, node):
        raise NotImplementedError(self.nameline('YIELD_FROM', node))

    def n_pb_ja(self, node):
        raise NotImplementedError(self.nameline('pb_ja', node))

    def n_await_expr(self, node):
        raise NotImplementedError(self.nameline('await_expr', node))

    def n_GET_AWAITABLE(self, node):
        raise NotImplementedError(self.nameline('GET_AWAITABLE', node))

    def n_await_stmt(self, node):
        raise NotImplementedError(self.nameline('await_stmt', node))

    def n_WITH_CLEANUP_START(self, node):
        raise NotImplementedError(self.nameline('WITH_CLEANUP_START', node))

    def n_WITH_CLEANUP_FINISH(self, node):
        raise NotImplementedError(self.nameline('WITH_CLEANUP_FINISH', node))

    def n_async_for_stmt(self, node):
        raise NotImplementedError(self.nameline('async_for_stmt', node))

    def n_GET_AITER(self, node):
        raise NotImplementedError(self.nameline('GET_AITER', node))

    def n_GET_ANEXT(self, node):
        raise NotImplementedError(self.nameline('GET_ANEXT', node))

    def n_async_forelse_stmt(self, node):
        raise NotImplementedError(self.nameline('async_forelse_stmt', node))

    def n_INPLACE_MATRIX_MULTIPLY(self, node):
        raise NotImplementedError(self.nameline('INPLACE_MATRIX_MULTIPLY', node))

    def n_BINARY_MATRIX_MULTIPLY(self, node):
        raise NotImplementedError(self.nameline('BINARY_MATRIX_MULTIPLY', node))

    def n_jb_else(self, node):
        raise NotImplementedError(self.nameline('jb_else', node))

    def n_GET_YIELD_FROM_ITER(self, node):
        raise NotImplementedError(self.nameline('GET_YIELD_FROM_ITER', node))

    def n_come_from_loops(self, node):
        raise NotImplementedError(self.nameline('come_from_loops', node))

    def n_jf_cf(self, node):
        raise NotImplementedError(self.nameline('jf_cf', node))

    def n_jb_cfs(self, node):
        raise NotImplementedError(self.nameline('jb_cfs', node))

    def n_except_return(self, node):
        raise NotImplementedError(self.nameline('except_return', node))

    def n_except_handler36(self, node):
        raise NotImplementedError(self.nameline('except_handler36', node))

    def n_try_except36(self, node):
        raise NotImplementedError(self.nameline('try_except36', node))

    def n_tryfinally36(self, node):
        raise NotImplementedError(self.nameline('tryfinally36', node))

    def n_tryfinally_return_stmt(self, node):
        raise NotImplementedError(self.nameline('tryfinally_return_stmt', node))

    def n_import37(self, node):
        raise NotImplementedError(self.nameline('import37', node))

    def n_attribute37(self, node):
        return rejig.syntaxtree.Call(".", self.n(node[0]), node[1].pattr, sourcepath=self.sourcepath, linestart=node.linestart)

    def n_LOAD_METHOD(self, node):
        return node.pattr

    def n_CALL_METHOD_0(self, node):
        raise NotImplementedError(self.nameline('CALL_METHOD_0', node))
