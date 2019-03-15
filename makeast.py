import uncompyle6.semantics.pysource

class MakeAST(uncompyle6.semantics.pysource.SourceWalker):
    def _name_lineno(self, name, node):
        lineno = getattr(node, "linestart", None)
        if lineno is None:
            return name
        else:
            return "{0} on line {1}".format(name, node.linestart)

    def n_0(self, node):
        raise NotImplementedError(self._name_lineno('0', node))

    def n_1(self, node):
        raise NotImplementedError(self._name_lineno('1', node))

    def n_2(self, node):
        raise NotImplementedError(self._name_lineno('2', node))

    def n_3(self, node):
        raise NotImplementedError(self._name_lineno('3', node))

    def n_BINARY_ADD(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_ADD', node))

    def n_BINARY_AND(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_AND', node))

    def n_BINARY_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_DIVIDE', node))

    def n_BINARY_FLOOR_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_FLOOR_DIVIDE', node))

    def n_BINARY_LSHIFT(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_LSHIFT', node))

    def n_BINARY_MATRIX_MULTIPLY(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_MATRIX_MULTIPLY', node))

    def n_BINARY_MODULO(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_MODULO', node))

    def n_BINARY_MULTIPLY(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_MULTIPLY', node))

    def n_BINARY_OR(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_OR', node))

    def n_BINARY_POWER(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_POWER', node))

    def n_BINARY_RSHIFT(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_RSHIFT', node))

    def n_BINARY_SUBSCR(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_SUBSCR', node))

    def n_BINARY_SUBTRACT(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_SUBTRACT', node))

    def n_BINARY_TRUE_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_TRUE_DIVIDE', node))

    def n_BINARY_XOR(self, node):
        raise NotImplementedError(self._name_lineno('BINARY_XOR', node))

    def n_BREAK_LOOP(self, node):
        raise NotImplementedError(self._name_lineno('BREAK_LOOP', node))

    def n_BUILD_CLASS(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_CLASS', node))

    def n_BUILD_LIST_0(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_LIST_0', node))

    def n_BUILD_MAP(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_MAP', node))

    def n_BUILD_MAP_0(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_MAP_0', node))

    def n_BUILD_SET_0(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_SET_0', node))

    def n_BUILD_TUPLE_1(self, node):
        raise NotImplementedError(self._name_lineno('BUILD_TUPLE_1', node))

    def n_CALL_FUNCTION_0(self, node):
        raise NotImplementedError(self._name_lineno('CALL_FUNCTION_0', node))

    def n_CALL_FUNCTION_1(self, node):
        raise NotImplementedError(self._name_lineno('CALL_FUNCTION_1', node))

    def n_CALL_FUNCTION_3(self, node):
        raise NotImplementedError(self._name_lineno('CALL_FUNCTION_3', node))

    def n_CALL_FUNCTION_4(self, node):
        raise NotImplementedError(self._name_lineno('CALL_FUNCTION_4', node))

    def n_CALL_METHOD_0(self, node):
        raise NotImplementedError(self._name_lineno('CALL_METHOD_0', node))

    def n_COME_FROM(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM', node))

    def n_COME_FROM_EXCEPT(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM_EXCEPT', node))

    def n_COME_FROM_EXCEPT_CLAUSE(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM_EXCEPT_CLAUSE', node))

    def n_COME_FROM_FINALLY(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM_FINALLY', node))

    def n_COME_FROM_LOOP(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM_LOOP', node))

    def n_COME_FROM_WITH(self, node):
        raise NotImplementedError(self._name_lineno('COME_FROM_WITH', node))

    def n_COMPARE_OP(self, node):
        raise NotImplementedError(self._name_lineno('COMPARE_OP', node))

    def n_CONTINUE(self, node):
        raise NotImplementedError(self._name_lineno('CONTINUE', node))

    def n_DELETE_ATTR(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_ATTR', node))

    def n_DELETE_FAST(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_FAST', node))

    def n_DELETE_GLOBAL(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_GLOBAL', node))

    def n_DELETE_NAME(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_NAME', node))

    def n_DELETE_SLICE(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_SLICE', node))

    def n_DELETE_SUBSCR(self, node):
        raise NotImplementedError(self._name_lineno('DELETE_SUBSCR', node))

    def n_DUP_TOP(self, node):
        raise NotImplementedError(self._name_lineno('DUP_TOP', node))

    def n_DUP_TOPX(self, node):
        raise NotImplementedError(self._name_lineno('DUP_TOPX', node))

    def n_DUP_TOPX_2(self, node):
        raise NotImplementedError(self._name_lineno('DUP_TOPX_2', node))

    def n_DUP_TOPX_3(self, node):
        raise NotImplementedError(self._name_lineno('DUP_TOPX_3', node))

    def n_DUP_TOP_TWO(self, node):
        raise NotImplementedError(self._name_lineno('DUP_TOP_TWO', node))

    def n_ELSE(self, node):
        raise NotImplementedError(self._name_lineno('ELSE', node))

    def n_END_FINALLY(self, node):
        raise NotImplementedError(self._name_lineno('END_FINALLY', node))

    def n_FOR_ITER(self, node):
        raise NotImplementedError(self._name_lineno('FOR_ITER', node))

    def n_FOR_LOOP(self, node):
        raise NotImplementedError(self._name_lineno('FOR_LOOP', node))

    def n_GET_AITER(self, node):
        raise NotImplementedError(self._name_lineno('GET_AITER', node))

    def n_GET_ANEXT(self, node):
        raise NotImplementedError(self._name_lineno('GET_ANEXT', node))

    def n_GET_AWAITABLE(self, node):
        raise NotImplementedError(self._name_lineno('GET_AWAITABLE', node))

    def n_GET_ITER(self, node):
        raise NotImplementedError(self._name_lineno('GET_ITER', node))

    def n_GET_YIELD_FROM_ITER(self, node):
        raise NotImplementedError(self._name_lineno('GET_YIELD_FROM_ITER', node))

    def n_IMPORT_FROM(self, node):
        raise NotImplementedError(self._name_lineno('IMPORT_FROM', node))

    def n_IMPORT_NAME(self, node):
        raise NotImplementedError(self._name_lineno('IMPORT_NAME', node))

    def n_IMPORT_NAME_CONT(self, node):
        raise NotImplementedError(self._name_lineno('IMPORT_NAME_CONT', node))

    def n_IMPORT_STAR(self, node):
        raise NotImplementedError(self._name_lineno('IMPORT_STAR', node))

    def n_INPLACE_ADD(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_ADD', node))

    def n_INPLACE_AND(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_AND', node))

    def n_INPLACE_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_DIVIDE', node))

    def n_INPLACE_FLOOR_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_FLOOR_DIVIDE', node))

    def n_INPLACE_LSHIFT(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_LSHIFT', node))

    def n_INPLACE_MATRIX_MULTIPLY(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_MATRIX_MULTIPLY', node))

    def n_INPLACE_MODULO(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_MODULO', node))

    def n_INPLACE_MULTIPLY(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_MULTIPLY', node))

    def n_INPLACE_OR(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_OR', node))

    def n_INPLACE_POWER(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_POWER', node))

    def n_INPLACE_RSHIFT(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_RSHIFT', node))

    def n_INPLACE_SUBTRACT(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_SUBTRACT', node))

    def n_INPLACE_TRUE_DIVIDE(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_TRUE_DIVIDE', node))

    def n_INPLACE_XOR(self, node):
        raise NotImplementedError(self._name_lineno('INPLACE_XOR', node))

    def n_JUMP_ABSOLUTE(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_ABSOLUTE', node))

    def n_JUMP_BACK(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_BACK', node))

    def n_JUMP_FORWARD(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_FORWARD', node))

    def n_JUMP_IF_FALSE(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_IF_FALSE', node))

    def n_JUMP_IF_FALSE_OR_POP(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_IF_FALSE_OR_POP', node))

    def n_JUMP_IF_TRUE(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_IF_TRUE', node))

    def n_JUMP_IF_TRUE_OR_POP(self, node):
        raise NotImplementedError(self._name_lineno('JUMP_IF_TRUE_OR_POP', node))

    def n_LAMBDA_MARKER(self, node):
        raise NotImplementedError(self._name_lineno('LAMBDA_MARKER', node))

    def n_LIST_APPEND(self, node):
        raise NotImplementedError(self._name_lineno('LIST_APPEND', node))

    def n_LOAD_ASSERT(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_ASSERT', node))

    def n_LOAD_ATTR(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_ATTR', node))

    def n_LOAD_BUILD_CLASS(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_BUILD_CLASS', node))

    def n_LOAD_CLOSURE(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_CLOSURE', node))

    def n_LOAD_CONST(self, node):
        print(type(node)); return node

    def n_LOAD_DEREF(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_DEREF', node))

    def n_LOAD_DICTCOMP(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_DICTCOMP', node))

    def n_LOAD_FAST(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_FAST', node))

    def n_LOAD_GENEXPR(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_GENEXPR', node))

    def n_LOAD_GLOBAL(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_GLOBAL', node))

    def n_LOAD_LOCALS(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_LOCALS', node))

    def n_LOAD_METHOD(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_METHOD', node))

    def n_LOAD_NAME(self, node):
        raise NotImplementedError(self._name_lineno('LOAD_NAME', node))

    def n_MAKE_FUNCTION_0(self, node):
        raise NotImplementedError(self._name_lineno('MAKE_FUNCTION_0', node))

    def n_MAP_ADD(self, node):
        raise NotImplementedError(self._name_lineno('MAP_ADD', node))

    def n_NOP(self, node):
        raise NotImplementedError(self._name_lineno('NOP', node))

    def n_POP_BLOCK(self, node):
        raise NotImplementedError(self._name_lineno('POP_BLOCK', node))

    def n_POP_EXCEPT(self, node):
        raise NotImplementedError(self._name_lineno('POP_EXCEPT', node))

    def n_POP_JUMP_IF_FALSE(self, node):
        raise NotImplementedError(self._name_lineno('POP_JUMP_IF_FALSE', node))

    def n_POP_JUMP_IF_TRUE(self, node):
        raise NotImplementedError(self._name_lineno('POP_JUMP_IF_TRUE', node))

    def n_POP_TOP(self, node):
        raise NotImplementedError(self._name_lineno('POP_TOP', node))

    def n_PRINT_EXPR(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_EXPR', node))

    def n_PRINT_ITEM(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_ITEM', node))

    def n_PRINT_ITEM_CONT(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_ITEM_CONT', node))

    def n_PRINT_ITEM_TO(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_ITEM_TO', node))

    def n_PRINT_NEWLINE(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_NEWLINE', node))

    def n_PRINT_NEWLINE_CONT(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_NEWLINE_CONT', node))

    def n_PRINT_NEWLINE_TO(self, node):
        raise NotImplementedError(self._name_lineno('PRINT_NEWLINE_TO', node))

    def n_RAISE_VARARGS_0(self, node):
        raise NotImplementedError(self._name_lineno('RAISE_VARARGS_0', node))

    def n_RAISE_VARARGS_1(self, node):
        raise NotImplementedError(self._name_lineno('RAISE_VARARGS_1', node))

    def n_RAISE_VARARGS_2(self, node):
        raise NotImplementedError(self._name_lineno('RAISE_VARARGS_2', node))

    def n_RAISE_VARARGS_3(self, node):
        raise NotImplementedError(self._name_lineno('RAISE_VARARGS_3', node))

    def n_RETURN_END_IF(self, node):
        raise NotImplementedError(self._name_lineno('RETURN_END_IF', node))

    def n_RETURN_END_IF_LAMBDA(self, node):
        raise NotImplementedError(self._name_lineno('RETURN_END_IF_LAMBDA', node))

    def n_RETURN_LAST(self, node):
        print(type(node)); return node

    def n_RETURN_VALUE(self, node):
        print(type(node)); return node

    def n_RETURN_VALUE_LAMBDA(self, node):
        raise NotImplementedError(self._name_lineno('RETURN_VALUE_LAMBDA', node))

    def n_ROT_FOUR(self, node):
        raise NotImplementedError(self._name_lineno('ROT_FOUR', node))

    def n_ROT_THREE(self, node):
        raise NotImplementedError(self._name_lineno('ROT_THREE', node))

    def n_ROT_TWO(self, node):
        raise NotImplementedError(self._name_lineno('ROT_TWO', node))

    def n_SETUP_EXCEPT(self, node):
        raise NotImplementedError(self._name_lineno('SETUP_EXCEPT', node))

    def n_SETUP_FINALLY(self, node):
        raise NotImplementedError(self._name_lineno('SETUP_FINALLY', node))

    def n_SETUP_LOOP(self, node):
        raise NotImplementedError(self._name_lineno('SETUP_LOOP', node))

    def n_SETUP_WITH(self, node):
        raise NotImplementedError(self._name_lineno('SETUP_WITH', node))

    def n_SET_ADD(self, node):
        raise NotImplementedError(self._name_lineno('SET_ADD', node))

    def n_SLICE(self, node):
        raise NotImplementedError(self._name_lineno('SLICE', node))

    def n_STORE_ATTR(self, node):
        raise NotImplementedError(self._name_lineno('STORE_ATTR', node))

    def n_STORE_DEREF(self, node):
        raise NotImplementedError(self._name_lineno('STORE_DEREF', node))

    def n_STORE_FAST(self, node):
        raise NotImplementedError(self._name_lineno('STORE_FAST', node))

    def n_STORE_GLOBAL(self, node):
        raise NotImplementedError(self._name_lineno('STORE_GLOBAL', node))

    def n_STORE_LOCALS(self, node):
        raise NotImplementedError(self._name_lineno('STORE_LOCALS', node))

    def n_STORE_MAP(self, node):
        raise NotImplementedError(self._name_lineno('STORE_MAP', node))

    def n_STORE_NAME(self, node):
        raise NotImplementedError(self._name_lineno('STORE_NAME', node))

    def n_STORE_SLICE(self, node):
        raise NotImplementedError(self._name_lineno('STORE_SLICE', node))

    def n_STORE_SUBSCR(self, node):
        raise NotImplementedError(self._name_lineno('STORE_SUBSCR', node))

    def n_THEN(self, node):
        raise NotImplementedError(self._name_lineno('THEN', node))

    def n_UNARY_CONVERT(self, node):
        raise NotImplementedError(self._name_lineno('UNARY_CONVERT', node))

    def n_UNARY_INVERT(self, node):
        raise NotImplementedError(self._name_lineno('UNARY_INVERT', node))

    def n_UNARY_NEGATIVE(self, node):
        raise NotImplementedError(self._name_lineno('UNARY_NEGATIVE', node))

    def n_UNARY_NOT(self, node):
        raise NotImplementedError(self._name_lineno('UNARY_NOT', node))

    def n_UNARY_POSITIVE(self, node):
        raise NotImplementedError(self._name_lineno('UNARY_POSITIVE', node))

    def n_WITH_CLEANUP(self, node):
        raise NotImplementedError(self._name_lineno('WITH_CLEANUP', node))

    def n_WITH_CLEANUP_FINISH(self, node):
        raise NotImplementedError(self._name_lineno('WITH_CLEANUP_FINISH', node))

    def n_WITH_CLEANUP_START(self, node):
        raise NotImplementedError(self._name_lineno('WITH_CLEANUP_START', node))

    def n_YIELD_FROM(self, node):
        raise NotImplementedError(self._name_lineno('YIELD_FROM', node))

    def n_YIELD_VALUE(self, node):
        raise NotImplementedError(self._name_lineno('YIELD_VALUE', node))

    def n__come_froms(self, node):
        raise NotImplementedError(self._name_lineno('_come_froms', node))

    def n__ifstmts_jump(self, node):
        raise NotImplementedError(self._name_lineno('_ifstmts_jump', node))

    def n__ifstmts_jump24(self, node):
        raise NotImplementedError(self._name_lineno('_ifstmts_jump24', node))

    def n__jump(self, node):
        raise NotImplementedError(self._name_lineno('_jump', node))

    def n__jump_back(self, node):
        raise NotImplementedError(self._name_lineno('_jump_back', node))

    def n__mklambda(self, node):
        raise NotImplementedError(self._name_lineno('_mklambda', node))

    def n__stmts(self, node):
        raise NotImplementedError(self._name_lineno('_stmts', node))

    def n__while1test(self, node):
        raise NotImplementedError(self._name_lineno('_while1test', node))

    def n_alias(self, node):
        raise NotImplementedError(self._name_lineno('alias', node))

    def n_and(self, node):
        raise NotImplementedError(self._name_lineno('and', node))

    def n_and2(self, node):
        raise NotImplementedError(self._name_lineno('and2', node))

    def n_annotate_arg(self, node):
        raise NotImplementedError(self._name_lineno('annotate_arg', node))

    def n_annotate_tuple(self, node):
        raise NotImplementedError(self._name_lineno('annotate_tuple', node))

    def n_assert(self, node):
        raise NotImplementedError(self._name_lineno('assert', node))

    def n_assert2(self, node):
        raise NotImplementedError(self._name_lineno('assert2', node))

    def n_assert_expr(self, node):
        raise NotImplementedError(self._name_lineno('assert_expr', node))

    def n_assert_expr_and(self, node):
        raise NotImplementedError(self._name_lineno('assert_expr_and', node))

    def n_assert_expr_or(self, node):
        raise NotImplementedError(self._name_lineno('assert_expr_or', node))

    def n_assign(self, node):
        raise NotImplementedError(self._name_lineno('assign', node))

    def n_assign2(self, node):
        raise NotImplementedError(self._name_lineno('assign2', node))

    def n_assign3(self, node):
        raise NotImplementedError(self._name_lineno('assign3', node))

    def n_async_for_stmt(self, node):
        raise NotImplementedError(self._name_lineno('async_for_stmt', node))

    def n_async_forelse_stmt(self, node):
        raise NotImplementedError(self._name_lineno('async_forelse_stmt', node))

    def n_attribute(self, node):
        raise NotImplementedError(self._name_lineno('attribute', node))

    def n_attribute37(self, node):
        raise NotImplementedError(self._name_lineno('attribute37', node))

    def n_attributes(self, node):
        raise NotImplementedError(self._name_lineno('attributes', node))

    def n_aug_assign1(self, node):
        raise NotImplementedError(self._name_lineno('aug_assign1', node))

    def n_aug_assign2(self, node):
        raise NotImplementedError(self._name_lineno('aug_assign2', node))

    def n_await_expr(self, node):
        raise NotImplementedError(self._name_lineno('await_expr', node))

    def n_await_stmt(self, node):
        raise NotImplementedError(self._name_lineno('await_stmt', node))

    def n_binary_expr(self, node):
        raise NotImplementedError(self._name_lineno('binary_expr', node))

    def n_binary_op(self, node):
        raise NotImplementedError(self._name_lineno('binary_op', node))

    def n_bp_come_from(self, node):
        raise NotImplementedError(self._name_lineno('bp_come_from', node))

    def n_break(self, node):
        raise NotImplementedError(self._name_lineno('break', node))

    def n_build_class(self, node):
        raise NotImplementedError(self._name_lineno('build_class', node))

    def n_buildclass(self, node):
        raise NotImplementedError(self._name_lineno('buildclass', node))

    def n_c_stmts(self, node):
        raise NotImplementedError(self._name_lineno('c_stmts', node))

    def n_c_stmts_opt(self, node):
        raise NotImplementedError(self._name_lineno('c_stmts_opt', node))

    def n_call(self, node):
        raise NotImplementedError(self._name_lineno('call', node))

    def n_call_stmt(self, node):
        raise NotImplementedError(self._name_lineno('call_stmt', node))

    def n_cf_jb_cf_pop(self, node):
        raise NotImplementedError(self._name_lineno('cf_jb_cf_pop', node))

    def n_cf_jump_back(self, node):
        raise NotImplementedError(self._name_lineno('cf_jump_back', node))

    def n_classdef(self, node):
        raise NotImplementedError(self._name_lineno('classdef', node))

    def n_classdefdeco(self, node):
        raise NotImplementedError(self._name_lineno('classdefdeco', node))

    def n_classdefdeco1(self, node):
        raise NotImplementedError(self._name_lineno('classdefdeco1', node))

    def n_classdefdeco2(self, node):
        raise NotImplementedError(self._name_lineno('classdefdeco2', node))

    def n_come_from_except_clauses(self, node):
        raise NotImplementedError(self._name_lineno('come_from_except_clauses', node))

    def n_come_from_loops(self, node):
        raise NotImplementedError(self._name_lineno('come_from_loops', node))

    def n_come_from_opt(self, node):
        raise NotImplementedError(self._name_lineno('come_from_opt', node))

    def n_come_from_pop(self, node):
        raise NotImplementedError(self._name_lineno('come_from_pop', node))

    def n_come_froms(self, node):
        raise NotImplementedError(self._name_lineno('come_froms', node))

    def n_come_froms_pop(self, node):
        raise NotImplementedError(self._name_lineno('come_froms_pop', node))

    def n_comp_body(self, node):
        raise NotImplementedError(self._name_lineno('comp_body', node))

    def n_comp_for(self, node):
        raise NotImplementedError(self._name_lineno('comp_for', node))

    def n_comp_if(self, node):
        raise NotImplementedError(self._name_lineno('comp_if', node))

    def n_comp_if_not(self, node):
        raise NotImplementedError(self._name_lineno('comp_if_not', node))

    def n_comp_iter(self, node):
        raise NotImplementedError(self._name_lineno('comp_iter', node))

    def n_compare(self, node):
        raise NotImplementedError(self._name_lineno('compare', node))

    def n_compare_chained(self, node):
        raise NotImplementedError(self._name_lineno('compare_chained', node))

    def n_compare_chained1(self, node):
        raise NotImplementedError(self._name_lineno('compare_chained1', node))

    def n_compare_chained2(self, node):
        raise NotImplementedError(self._name_lineno('compare_chained2', node))

    def n_compare_single(self, node):
        raise NotImplementedError(self._name_lineno('compare_single', node))

    def n_conditional(self, node):
        raise NotImplementedError(self._name_lineno('conditional', node))

    def n_conditional_false(self, node):
        raise NotImplementedError(self._name_lineno('conditional_false', node))

    def n_conditional_lambda(self, node):
        raise NotImplementedError(self._name_lineno('conditional_lambda', node))

    def n_conditional_not(self, node):
        raise NotImplementedError(self._name_lineno('conditional_not', node))

    def n_conditional_not_lambda(self, node):
        raise NotImplementedError(self._name_lineno('conditional_not_lambda', node))

    def n_conditional_true(self, node):
        raise NotImplementedError(self._name_lineno('conditional_true', node))

    def n_conditionalnot(self, node):
        raise NotImplementedError(self._name_lineno('conditionalnot', node))

    def n_continue(self, node):
        raise NotImplementedError(self._name_lineno('continue', node))

    def n_continues(self, node):
        raise NotImplementedError(self._name_lineno('continues', node))

    def n_del_stmt(self, node):
        raise NotImplementedError(self._name_lineno('del_stmt', node))

    def n_delete_subscr(self, node):
        raise NotImplementedError(self._name_lineno('delete_subscr', node))

    def n_designList(self, node):
        raise NotImplementedError(self._name_lineno('designList', node))

    def n_dict(self, node):
        raise NotImplementedError(self._name_lineno('dict', node))

    def n_dict_comp(self, node):
        raise NotImplementedError(self._name_lineno('dict_comp', node))

    def n_dict_comp_body(self, node):
        raise NotImplementedError(self._name_lineno('dict_comp_body', node))

    def n_dict_comp_func(self, node):
        raise NotImplementedError(self._name_lineno('dict_comp_func', node))

    def n_dict_comp_header(self, node):
        raise NotImplementedError(self._name_lineno('dict_comp_header', node))

    def n_dict_comp_iter(self, node):
        raise NotImplementedError(self._name_lineno('dict_comp_iter', node))

    def n_doc_junk(self, node):
        raise NotImplementedError(self._name_lineno('doc_junk', node))

    def n_else_suite(self, node):
        raise NotImplementedError(self._name_lineno('else_suite', node))

    def n_else_suitec(self, node):
        raise NotImplementedError(self._name_lineno('else_suitec', node))

    def n_else_suitel(self, node):
        raise NotImplementedError(self._name_lineno('else_suitel', node))

    def n_except(self, node):
        raise NotImplementedError(self._name_lineno('except', node))

    def n_except_cond1(self, node):
        raise NotImplementedError(self._name_lineno('except_cond1', node))

    def n_except_cond2(self, node):
        raise NotImplementedError(self._name_lineno('except_cond2', node))

    def n_except_cond3(self, node):
        raise NotImplementedError(self._name_lineno('except_cond3', node))

    def n_except_handler(self, node):
        raise NotImplementedError(self._name_lineno('except_handler', node))

    def n_except_handler36(self, node):
        raise NotImplementedError(self._name_lineno('except_handler36', node))

    def n_except_pop_except(self, node):
        raise NotImplementedError(self._name_lineno('except_pop_except', node))

    def n_except_return(self, node):
        raise NotImplementedError(self._name_lineno('except_return', node))

    def n_except_stmt(self, node):
        raise NotImplementedError(self._name_lineno('except_stmt', node))

    def n_except_stmts(self, node):
        raise NotImplementedError(self._name_lineno('except_stmts', node))

    def n_except_suite(self, node):
        raise NotImplementedError(self._name_lineno('except_suite', node))

    def n_except_suite_finalize(self, node):
        raise NotImplementedError(self._name_lineno('except_suite_finalize', node))

    def n_except_var_finalize(self, node):
        raise NotImplementedError(self._name_lineno('except_var_finalize', node))

    def n_expr(self, node):
        print(type(node)); return node

    def n_filler(self, node):
        raise NotImplementedError(self._name_lineno('filler', node))

    def n_for(self, node):
        raise NotImplementedError(self._name_lineno('for', node))

    def n_for_block(self, node):
        raise NotImplementedError(self._name_lineno('for_block', node))

    def n_for_iter(self, node):
        raise NotImplementedError(self._name_lineno('for_iter', node))

    def n_forelselaststmt(self, node):
        raise NotImplementedError(self._name_lineno('forelselaststmt', node))

    def n_forelselaststmtl(self, node):
        raise NotImplementedError(self._name_lineno('forelselaststmtl', node))

    def n_forelsestmt(self, node):
        raise NotImplementedError(self._name_lineno('forelsestmt', node))

    def n_function_def(self, node):
        raise NotImplementedError(self._name_lineno('function_def', node))

    def n_function_def_annotate(self, node):
        raise NotImplementedError(self._name_lineno('function_def_annotate', node))

    def n_function_def_deco(self, node):
        raise NotImplementedError(self._name_lineno('function_def_deco', node))

    def n_gen_comp_body(self, node):
        raise NotImplementedError(self._name_lineno('gen_comp_body', node))

    def n_generator_exp(self, node):
        raise NotImplementedError(self._name_lineno('generator_exp', node))

    def n_genexpr_func(self, node):
        raise NotImplementedError(self._name_lineno('genexpr_func', node))

    def n_get_iter(self, node):
        raise NotImplementedError(self._name_lineno('get_iter', node))

    def n_if1_stmt(self, node):
        raise NotImplementedError(self._name_lineno('if1_stmt', node))

    def n_ifelsestmt(self, node):
        raise NotImplementedError(self._name_lineno('ifelsestmt', node))

    def n_ifelsestmtc(self, node):
        raise NotImplementedError(self._name_lineno('ifelsestmtc', node))

    def n_ifelsestmtl(self, node):
        raise NotImplementedError(self._name_lineno('ifelsestmtl', node))

    def n_ifelsestmtr(self, node):
        raise NotImplementedError(self._name_lineno('ifelsestmtr', node))

    def n_iflaststmt(self, node):
        raise NotImplementedError(self._name_lineno('iflaststmt', node))

    def n_iflaststmtl(self, node):
        raise NotImplementedError(self._name_lineno('iflaststmtl', node))

    def n_ifstmt(self, node):
        raise NotImplementedError(self._name_lineno('ifstmt', node))

    def n_iftrue_stmt24(self, node):
        raise NotImplementedError(self._name_lineno('iftrue_stmt24', node))

    def n_import(self, node):
        raise NotImplementedError(self._name_lineno('import', node))

    def n_import37(self, node):
        raise NotImplementedError(self._name_lineno('import37', node))

    def n_import_cont(self, node):
        raise NotImplementedError(self._name_lineno('import_cont', node))

    def n_import_from(self, node):
        raise NotImplementedError(self._name_lineno('import_from', node))

    def n_import_from_star(self, node):
        raise NotImplementedError(self._name_lineno('import_from_star', node))

    def n_importlist(self, node):
        raise NotImplementedError(self._name_lineno('importlist', node))

    def n_importmultiple(self, node):
        raise NotImplementedError(self._name_lineno('importmultiple', node))

    def n_imports_cont(self, node):
        raise NotImplementedError(self._name_lineno('imports_cont', node))

    def n_inplace_op(self, node):
        raise NotImplementedError(self._name_lineno('inplace_op', node))

    def n_ja_cf_pop(self, node):
        raise NotImplementedError(self._name_lineno('ja_cf_pop', node))

    def n_jb_cf_pop(self, node):
        raise NotImplementedError(self._name_lineno('jb_cf_pop', node))

    def n_jb_cfs(self, node):
        raise NotImplementedError(self._name_lineno('jb_cfs', node))

    def n_jb_cont(self, node):
        raise NotImplementedError(self._name_lineno('jb_cont', node))

    def n_jb_else(self, node):
        raise NotImplementedError(self._name_lineno('jb_else', node))

    def n_jb_or_c(self, node):
        raise NotImplementedError(self._name_lineno('jb_or_c', node))

    def n_jb_pb_come_from(self, node):
        raise NotImplementedError(self._name_lineno('jb_pb_come_from', node))

    def n_jb_pop(self, node):
        raise NotImplementedError(self._name_lineno('jb_pop', node))

    def n_jb_pop14(self, node):
        raise NotImplementedError(self._name_lineno('jb_pop14', node))

    def n_jb_pop_top(self, node):
        raise NotImplementedError(self._name_lineno('jb_pop_top', node))

    def n_jf_cf(self, node):
        raise NotImplementedError(self._name_lineno('jf_cf', node))

    def n_jf_cf_pop(self, node):
        raise NotImplementedError(self._name_lineno('jf_cf_pop', node))

    def n_jf_pop(self, node):
        raise NotImplementedError(self._name_lineno('jf_pop', node))

    def n_jmp_abs(self, node):
        raise NotImplementedError(self._name_lineno('jmp_abs', node))

    def n_jmp_false(self, node):
        raise NotImplementedError(self._name_lineno('jmp_false', node))

    def n_jmp_false_then(self, node):
        raise NotImplementedError(self._name_lineno('jmp_false_then', node))

    def n_jmp_true(self, node):
        raise NotImplementedError(self._name_lineno('jmp_true', node))

    def n_jmp_true_then(self, node):
        raise NotImplementedError(self._name_lineno('jmp_true_then', node))

    def n_jump_absolute_else(self, node):
        raise NotImplementedError(self._name_lineno('jump_absolute_else', node))

    def n_jump_except(self, node):
        raise NotImplementedError(self._name_lineno('jump_except', node))

    def n_jump_excepts(self, node):
        raise NotImplementedError(self._name_lineno('jump_excepts', node))

    def n_jump_forward_else(self, node):
        raise NotImplementedError(self._name_lineno('jump_forward_else', node))

    def n_kv(self, node):
        raise NotImplementedError(self._name_lineno('kv', node))

    def n_kv2(self, node):
        raise NotImplementedError(self._name_lineno('kv2', node))

    def n_kv3(self, node):
        raise NotImplementedError(self._name_lineno('kv3', node))

    def n_kvlist(self, node):
        raise NotImplementedError(self._name_lineno('kvlist', node))

    def n_kwarg(self, node):
        raise NotImplementedError(self._name_lineno('kwarg', node))

    def n_kwargs(self, node):
        raise NotImplementedError(self._name_lineno('kwargs', node))

    def n_l_stmts(self, node):
        raise NotImplementedError(self._name_lineno('l_stmts', node))

    def n_l_stmts_opt(self, node):
        raise NotImplementedError(self._name_lineno('l_stmts_opt', node))

    def n_lastc_stmt(self, node):
        raise NotImplementedError(self._name_lineno('lastc_stmt', node))

    def n_lastl_stmt(self, node):
        raise NotImplementedError(self._name_lineno('lastl_stmt', node))

    def n_lc_body(self, node):
        raise NotImplementedError(self._name_lineno('lc_body', node))

    def n_list(self, node):
        raise NotImplementedError(self._name_lineno('list', node))

    def n_list_comp(self, node):
        raise NotImplementedError(self._name_lineno('list_comp', node))

    def n_list_comp_header(self, node):
        raise NotImplementedError(self._name_lineno('list_comp_header', node))

    def n_list_for(self, node):
        raise NotImplementedError(self._name_lineno('list_for', node))

    def n_list_if(self, node):
        raise NotImplementedError(self._name_lineno('list_if', node))

    def n_list_if_not(self, node):
        raise NotImplementedError(self._name_lineno('list_if_not', node))

    def n_list_iter(self, node):
        raise NotImplementedError(self._name_lineno('list_iter', node))

    def n_load(self, node):
        raise NotImplementedError(self._name_lineno('load', node))

    def n_load_closure(self, node):
        raise NotImplementedError(self._name_lineno('load_closure', node))

    def n_load_genexpr(self, node):
        raise NotImplementedError(self._name_lineno('load_genexpr', node))

    def n_mkfunc(self, node):
        raise NotImplementedError(self._name_lineno('mkfunc', node))

    def n_mkfunc_annotate(self, node):
        raise NotImplementedError(self._name_lineno('mkfunc_annotate', node))

    def n_mkfuncdeco(self, node):
        raise NotImplementedError(self._name_lineno('mkfuncdeco', node))

    def n_mkfuncdeco0(self, node):
        raise NotImplementedError(self._name_lineno('mkfuncdeco0', node))

    def n_mklambda(self, node):
        raise NotImplementedError(self._name_lineno('mklambda', node))

    def n_nop_stmt(self, node):
        raise NotImplementedError(self._name_lineno('nop_stmt', node))

    def n_opt_come_from_except(self, node):
        raise NotImplementedError(self._name_lineno('opt_come_from_except', node))

    def n_or(self, node):
        raise NotImplementedError(self._name_lineno('or', node))

    def n_pass(self, node):
        raise NotImplementedError(self._name_lineno('pass', node))

    def n_pb_ja(self, node):
        raise NotImplementedError(self._name_lineno('pb_ja', node))

    def n_pos_arg(self, node):
        raise NotImplementedError(self._name_lineno('pos_arg', node))

    def n_print_item(self, node):
        raise NotImplementedError(self._name_lineno('print_item', node))

    def n_print_items(self, node):
        raise NotImplementedError(self._name_lineno('print_items', node))

    def n_print_items_nl_stmt(self, node):
        raise NotImplementedError(self._name_lineno('print_items_nl_stmt', node))

    def n_print_items_opt(self, node):
        raise NotImplementedError(self._name_lineno('print_items_opt', node))

    def n_print_items_stmt(self, node):
        raise NotImplementedError(self._name_lineno('print_items_stmt', node))

    def n_print_nl(self, node):
        raise NotImplementedError(self._name_lineno('print_nl', node))

    def n_print_nl_to(self, node):
        raise NotImplementedError(self._name_lineno('print_nl_to', node))

    def n_print_to(self, node):
        raise NotImplementedError(self._name_lineno('print_to', node))

    def n_print_to_item(self, node):
        raise NotImplementedError(self._name_lineno('print_to_item', node))

    def n_print_to_items(self, node):
        raise NotImplementedError(self._name_lineno('print_to_items', node))

    def n_print_to_nl(self, node):
        raise NotImplementedError(self._name_lineno('print_to_nl', node))

    def n_raise_stmt0(self, node):
        raise NotImplementedError(self._name_lineno('raise_stmt0', node))

    def n_raise_stmt1(self, node):
        raise NotImplementedError(self._name_lineno('raise_stmt1', node))

    def n_raise_stmt2(self, node):
        raise NotImplementedError(self._name_lineno('raise_stmt2', node))

    def n_raise_stmt3(self, node):
        raise NotImplementedError(self._name_lineno('raise_stmt3', node))

    def n_ret_and(self, node):
        raise NotImplementedError(self._name_lineno('ret_and', node))

    def n_ret_cond(self, node):
        raise NotImplementedError(self._name_lineno('ret_cond', node))

    def n_ret_expr(self, node):
        print(type(node)); return node

    def n_ret_expr_or_cond(self, node):
        raise NotImplementedError(self._name_lineno('ret_expr_or_cond', node))

    def n_ret_or(self, node):
        raise NotImplementedError(self._name_lineno('ret_or', node))

    def n_return(self, node):
        print(type(node)); return node

    def n_return_closure(self, node):
        raise NotImplementedError(self._name_lineno('return_closure', node))

    def n_return_if_lambda(self, node):
        raise NotImplementedError(self._name_lineno('return_if_lambda', node))

    def n_return_if_stmt(self, node):
        raise NotImplementedError(self._name_lineno('return_if_stmt', node))

    def n_return_if_stmts(self, node):
        raise NotImplementedError(self._name_lineno('return_if_stmts', node))

    def n_return_lambda(self, node):
        raise NotImplementedError(self._name_lineno('return_lambda', node))

    def n_return_stmt(self, node):
        raise NotImplementedError(self._name_lineno('return_stmt', node))

    def n_return_stmt_lambda(self, node):
        raise NotImplementedError(self._name_lineno('return_stmt_lambda', node))

    def n_return_stmts(self, node):
        raise NotImplementedError(self._name_lineno('return_stmts', node))

    def n_returns(self, node):
        raise NotImplementedError(self._name_lineno('returns', node))

    def n_set_comp(self, node):
        raise NotImplementedError(self._name_lineno('set_comp', node))

    def n_set_comp_body(self, node):
        raise NotImplementedError(self._name_lineno('set_comp_body', node))

    def n_set_comp_func(self, node):
        raise NotImplementedError(self._name_lineno('set_comp_func', node))

    def n_set_comp_func_header(self, node):
        raise NotImplementedError(self._name_lineno('set_comp_func_header', node))

    def n_set_comp_header(self, node):
        raise NotImplementedError(self._name_lineno('set_comp_header', node))

    def n_setup_finally(self, node):
        raise NotImplementedError(self._name_lineno('setup_finally', node))

    def n_setup_loop_lf(self, node):
        raise NotImplementedError(self._name_lineno('setup_loop_lf', node))

    def n_setupwith(self, node):
        raise NotImplementedError(self._name_lineno('setupwith', node))

    def n_setupwithas(self, node):
        raise NotImplementedError(self._name_lineno('setupwithas', node))

    def n_setupwithas31(self, node):
        raise NotImplementedError(self._name_lineno('setupwithas31', node))

    def n_slice0(self, node):
        raise NotImplementedError(self._name_lineno('slice0', node))

    def n_slice1(self, node):
        raise NotImplementedError(self._name_lineno('slice1', node))

    def n_slice2(self, node):
        raise NotImplementedError(self._name_lineno('slice2', node))

    def n_slice3(self, node):
        raise NotImplementedError(self._name_lineno('slice3', node))

    def n_sstmt(self, node):
        print(type(node)); return node

    def n_stmt(self, node):
        print(type(node)); return node

    def n_stmts(self, node):
        print(type(node)); return node

    def n_store(self, node):
        raise NotImplementedError(self._name_lineno('store', node))

    def n_store_locals(self, node):
        raise NotImplementedError(self._name_lineno('store_locals', node))

    def n_store_subscr(self, node):
        raise NotImplementedError(self._name_lineno('store_subscr', node))

    def n_subscript(self, node):
        raise NotImplementedError(self._name_lineno('subscript', node))

    def n_subscript2(self, node):
        raise NotImplementedError(self._name_lineno('subscript2', node))

    def n_suite_stmts(self, node):
        raise NotImplementedError(self._name_lineno('suite_stmts', node))

    def n_suite_stmts_opt(self, node):
        raise NotImplementedError(self._name_lineno('suite_stmts_opt', node))

    def n_testexpr(self, node):
        raise NotImplementedError(self._name_lineno('testexpr', node))

    def n_testexpr_then(self, node):
        raise NotImplementedError(self._name_lineno('testexpr_then', node))

    def n_testfalse(self, node):
        raise NotImplementedError(self._name_lineno('testfalse', node))

    def n_testfalse_then(self, node):
        raise NotImplementedError(self._name_lineno('testfalse_then', node))

    def n_testtrue(self, node):
        raise NotImplementedError(self._name_lineno('testtrue', node))

    def n_testtrue_then(self, node):
        raise NotImplementedError(self._name_lineno('testtrue_then', node))

    def n_try_except(self, node):
        raise NotImplementedError(self._name_lineno('try_except', node))

    def n_try_except36(self, node):
        raise NotImplementedError(self._name_lineno('try_except36', node))

    def n_tryelsestmt(self, node):
        raise NotImplementedError(self._name_lineno('tryelsestmt', node))

    def n_tryelsestmtc(self, node):
        raise NotImplementedError(self._name_lineno('tryelsestmtc', node))

    def n_tryelsestmtl(self, node):
        raise NotImplementedError(self._name_lineno('tryelsestmtl', node))

    def n_tryfinally36(self, node):
        raise NotImplementedError(self._name_lineno('tryfinally36', node))

    def n_tryfinally_return_stmt(self, node):
        raise NotImplementedError(self._name_lineno('tryfinally_return_stmt', node))

    def n_tryfinallystmt(self, node):
        raise NotImplementedError(self._name_lineno('tryfinallystmt', node))

    def n_unary_convert(self, node):
        raise NotImplementedError(self._name_lineno('unary_convert', node))

    def n_unary_expr(self, node):
        raise NotImplementedError(self._name_lineno('unary_expr', node))

    def n_unary_not(self, node):
        raise NotImplementedError(self._name_lineno('unary_not', node))

    def n_unary_op(self, node):
        raise NotImplementedError(self._name_lineno('unary_op', node))

    def n_unpack(self, node):
        raise NotImplementedError(self._name_lineno('unpack', node))

    def n_while1elsestmt(self, node):
        raise NotImplementedError(self._name_lineno('while1elsestmt', node))

    def n_while1stmt(self, node):
        raise NotImplementedError(self._name_lineno('while1stmt', node))

    def n_whileTruestmt(self, node):
        raise NotImplementedError(self._name_lineno('whileTruestmt', node))

    def n_whileelsestmt(self, node):
        raise NotImplementedError(self._name_lineno('whileelsestmt', node))

    def n_whilestmt(self, node):
        raise NotImplementedError(self._name_lineno('whilestmt', node))

    def n_with_cleanup(self, node):
        raise NotImplementedError(self._name_lineno('with_cleanup', node))

    def n_withasstmt(self, node):
        raise NotImplementedError(self._name_lineno('withasstmt', node))

    def n_withstmt(self, node):
        raise NotImplementedError(self._name_lineno('withstmt', node))

    def n_yield(self, node):
        raise NotImplementedError(self._name_lineno('yield', node))

    def n_yield_from(self, node):
        raise NotImplementedError(self._name_lineno('yield_from', node))
