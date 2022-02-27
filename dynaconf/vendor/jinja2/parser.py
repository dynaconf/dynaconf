_f='name:and'
_e='name:or'
_d='name:as'
_c='name:context'
_b='variable_end'
_a='floordiv'
_Z='autoescape'
_Y='lbrace'
_X='integer'
_W='string'
_V='name:not'
_U='name:if'
_T='mul'
_S='add'
_R='name:in'
_Q='assign'
_P='sub'
_O='with'
_N='lbracket'
_M='dot'
_L='name:else'
_K='block_end'
_J='load'
_I='colon'
_H='rbracket'
_G='rparen'
_F='lparen'
_E='comma'
_D='name'
_C=False
_B=True
_A=None
import typing,typing as t
from .  import nodes
from .exceptions import TemplateAssertionError
from .exceptions import TemplateSyntaxError
from .lexer import describe_token
from .lexer import describe_token_expr
if t.TYPE_CHECKING:import typing_extensions as te;from .environment import Environment
_ImportInclude=t.TypeVar('_ImportInclude',nodes.Import,nodes.Include)
_MacroCall=t.TypeVar('_MacroCall',nodes.Macro,nodes.CallBlock)
_statement_keywords=frozenset(['for','if','block','extends','print','macro','include','from','import','set',_O,_Z])
_compare_operators=frozenset(['eq','ne','lt','lteq','gt','gteq'])
_math_nodes={_S:nodes.Add,_P:nodes.Sub,_T:nodes.Mul,'div':nodes.Div,_a:nodes.FloorDiv,'mod':nodes.Mod}
class Parser:
	def __init__(A,environment,source,name=_A,filename=_A,state=_A):
		C=filename;B=environment;A.environment=B;A.stream=B._tokenize(source,name,C,state);A.name=name;A.filename=C;A.closed=_C;A.extensions={}
		for D in B.iter_extensions():
			for E in D.tags:A.extensions[E]=D.parse
		A._last_identifier=0;A._tag_stack=[];A._end_token_stack=[]
	def fail(A,msg,lineno=_A,exc=TemplateSyntaxError):
		B=lineno
		if B is _A:B=A.stream.current.lineno
		raise exc(msg,B,A.name,A.filename)
	def _fail_ut_eof(D,name,end_token_stack,lineno):
		E=end_token_stack;B=name;F=set()
		for G in E:F.update(map(describe_token_expr,G))
		if E:C=' or '.join(map(repr,map(describe_token_expr,E[-1])))
		else:C=_A
		if B is _A:A=['Unexpected end of template.']
		else:A=[f"Encountered unknown tag {B!r}."]
		if C:
			if B is not _A and B in F:A.append(f"You probably made a nesting mistake. Jinja is expecting this tag, but currently looking for {C}.")
			else:A.append(f"Jinja was looking for the following tags: {C}.")
		if D._tag_stack:A.append(f"The innermost block that needs to be closed is {D._tag_stack[-1]!r}.")
		D.fail(' '.join(A),lineno)
	def fail_unknown_tag(A,name,lineno=_A):A._fail_ut_eof(name,A._end_token_stack,lineno)
	def fail_eof(A,end_tokens=_A,lineno=_A):
		B=end_tokens;C=list(A._end_token_stack)
		if B is not _A:C.append(B)
		A._fail_ut_eof(_A,C,lineno)
	def is_tuple_end(A,extra_end_rules=_A):
		B=extra_end_rules
		if A.stream.current.type in(_b,_K,_G):return _B
		elif B is not _A:return A.stream.current.test_any(B)
		return _C
	def free_identifier(A,lineno=_A):A._last_identifier+=1;B=object.__new__(nodes.InternalName);nodes.Node.__init__(B,f"fi{A._last_identifier}",lineno=lineno);return B
	def parse_statement(A):
		B=A.stream.current
		if B.type!=_D:A.fail('tag name expected',B.lineno)
		A._tag_stack.append(B.value);C=_B
		try:
			if B.value in _statement_keywords:E=getattr(A,f"parse_{A.stream.current.value}");return E()
			if B.value=='call':return A.parse_call_block()
			if B.value=='filter':return A.parse_filter_block()
			D=A.extensions.get(B.value)
			if D is not _A:return D(A)
			A._tag_stack.pop();C=_C;A.fail_unknown_tag(B.value,B.lineno)
		finally:
			if C:A._tag_stack.pop()
	def parse_statements(A,end_tokens,drop_needle=_C):
		B=end_tokens;A.stream.skip_if(_I);A.stream.expect(_K);C=A.subparse(B)
		if A.stream.current.type=='eof':A.fail_eof(B)
		if drop_needle:next(A.stream)
		return C
	def parse_set(A):
		B=next(A.stream).lineno;C=A.parse_assign_target(with_namespace=_B)
		if A.stream.skip_if(_Q):D=A.parse_tuple();return nodes.Assign(C,D,lineno=B)
		E=A.parse_filter(_A);F=A.parse_statements(('name:endset',),drop_needle=_B);return nodes.AssignBlock(C,E,F,lineno=B)
	def parse_for(A):
		E='name:endfor';D='name:recursive';F=A.stream.expect('name:for').lineno;G=A.parse_assign_target(extra_end_rules=(_R,));A.stream.expect(_R);iter=A.parse_tuple(with_condexpr=_C,extra_end_rules=(D,));B=_A
		if A.stream.skip_if(_U):B=A.parse_expression()
		H=A.stream.skip_if(D);I=A.parse_statements((E,_L))
		if next(A.stream).value=='endfor':C=[]
		else:C=A.parse_statements((E,),drop_needle=_B)
		return nodes.For(G,iter,I,C,B,H,lineno=F)
	def parse_if(A):
		F='name:endif';E='name:elif';B=C=nodes.If(lineno=A.stream.expect(_U).lineno)
		while _B:
			B.test=A.parse_tuple(with_condexpr=_C);B.body=A.parse_statements((E,_L,F));B.elif_=[];B.else_=[];D=next(A.stream)
			if D.test(E):B=nodes.If(lineno=A.stream.current.lineno);C.elif_.append(B);continue
			elif D.test(_L):C.else_=A.parse_statements((F,),drop_needle=_B)
			break
		return C
	def parse_with(A):
		B=nodes.With(lineno=next(A.stream).lineno);C=[];D=[]
		while A.stream.current.type!=_K:
			if C:A.stream.expect(_E)
			E=A.parse_assign_target();E.set_ctx('param');C.append(E);A.stream.expect(_Q);D.append(A.parse_expression())
		B.targets=C;B.values=D;B.body=A.parse_statements(('name:endwith',),drop_needle=_B);return B
	def parse_autoescape(A):B=nodes.ScopedEvalContextModifier(lineno=next(A.stream).lineno);B.options=[nodes.Keyword(_Z,A.parse_expression())];B.body=A.parse_statements(('name:endautoescape',),drop_needle=_B);return nodes.Scope([B])
	def parse_block(A):
		B=nodes.Block(lineno=next(A.stream).lineno);B.name=A.stream.expect(_D).value;B.scoped=A.stream.skip_if('name:scoped');B.required=A.stream.skip_if('name:required')
		if A.stream.current.type==_P:A.fail('Block names in Jinja have to be valid Python identifiers and may not contain hyphens, use an underscore instead.')
		B.body=A.parse_statements(('name:endblock',),drop_needle=_B)
		if B.required and not all((isinstance(A,nodes.TemplateData)and A.data.isspace()for C in B.body for A in C.nodes)):A.fail('Required blocks can only contain comments or whitespace')
		A.stream.skip_if('name:'+B.name);return B
	def parse_extends(A):B=nodes.Extends(lineno=next(A.stream).lineno);B.template=A.parse_expression();return B
	def parse_import_context(A,node,default):
		B=node
		if A.stream.current.test_any('name:with','name:without')and A.stream.look().test(_c):B.with_context=next(A.stream).value==_O;A.stream.skip()
		else:B.with_context=default
		return B
	def parse_include(A):
		B=nodes.Include(lineno=next(A.stream).lineno);B.template=A.parse_expression()
		if A.stream.current.test('name:ignore')and A.stream.look().test('name:missing'):B.ignore_missing=_B;A.stream.skip(2)
		else:B.ignore_missing=_C
		return A.parse_import_context(B,_B)
	def parse_import(A):B=nodes.Import(lineno=next(A.stream).lineno);B.template=A.parse_expression();A.stream.expect(_d);B.target=A.parse_assign_target(name_only=_B).name;return A.parse_import_context(B,_C)
	def parse_from(A):
		B=nodes.FromImport(lineno=next(A.stream).lineno);B.template=A.parse_expression();A.stream.expect('name:import');B.names=[]
		def D():
			if A.stream.current.value in{_O,'without'}and A.stream.look().test(_c):B.with_context=next(A.stream).value==_O;A.stream.skip();return _B
			return _C
		while _B:
			if B.names:A.stream.expect(_E)
			if A.stream.current.type==_D:
				if D():break
				C=A.parse_assign_target(name_only=_B)
				if C.name.startswith('_'):A.fail('names starting with an underline can not be imported',C.lineno,exc=TemplateAssertionError)
				if A.stream.skip_if(_d):E=A.parse_assign_target(name_only=_B);B.names.append((C.name,E.name))
				else:B.names.append(C.name)
				if D()or A.stream.current.type!=_E:break
			else:A.stream.expect(_D)
		if not hasattr(B,'with_context'):B.with_context=_C
		return B
	def parse_signature(A,node):
		B=node.args=[];C=node.defaults=[];A.stream.expect(_F)
		while A.stream.current.type!=_G:
			if B:A.stream.expect(_E)
			D=A.parse_assign_target(name_only=_B);D.set_ctx('param')
			if A.stream.skip_if(_Q):C.append(A.parse_expression())
			elif C:A.fail('non-default argument follows default argument')
			B.append(D)
		A.stream.expect(_G)
	def parse_call_block(B):
		A=nodes.CallBlock(lineno=next(B.stream).lineno)
		if B.stream.current.type==_F:B.parse_signature(A)
		else:A.args=[];A.defaults=[]
		C=B.parse_expression()
		if not isinstance(C,nodes.Call):B.fail('expected call',A.lineno)
		A.call=C;A.body=B.parse_statements(('name:endcall',),drop_needle=_B);return A
	def parse_filter_block(A):B=nodes.FilterBlock(lineno=next(A.stream).lineno);B.filter=A.parse_filter(_A,start_inline=_B);B.body=A.parse_statements(('name:endfilter',),drop_needle=_B);return B
	def parse_macro(A):B=nodes.Macro(lineno=next(A.stream).lineno);B.name=A.parse_assign_target(name_only=_B).name;A.parse_signature(B);B.body=A.parse_statements(('name:endmacro',),drop_needle=_B);return B
	def parse_print(A):
		B=nodes.Output(lineno=next(A.stream).lineno);B.nodes=[]
		while A.stream.current.type!=_K:
			if B.nodes:A.stream.expect(_E)
			B.nodes.append(A.parse_expression())
		return B
	@typing.overload
	def parse_assign_target(self,with_tuple=...,name_only=...):...
	@typing.overload
	def parse_assign_target(self,with_tuple=_B,name_only=_C,extra_end_rules=_A,with_namespace=_C):...
	def parse_assign_target(B,with_tuple=_B,name_only=_C,extra_end_rules=_A,with_namespace=_C):
		D='store';A:0
		if with_namespace and B.stream.look().type==_M:C=B.stream.expect(_D);next(B.stream);E=B.stream.expect(_D);A=nodes.NSRef(C.value,E.value,lineno=C.lineno)
		elif name_only:C=B.stream.expect(_D);A=nodes.Name(C.value,D,lineno=C.lineno)
		else:
			if with_tuple:A=B.parse_tuple(simplified=_B,extra_end_rules=extra_end_rules)
			else:A=B.parse_primary()
			A.set_ctx(D)
		if not A.can_assign():B.fail(f"can't assign to {type(A).__name__.lower()!r}",A.lineno)
		return A
	def parse_expression(A,with_condexpr=_B):
		if with_condexpr:return A.parse_condexpr()
		return A.parse_or()
	def parse_condexpr(A):
		D=A.stream.current.lineno;B=A.parse_or();C:0
		while A.stream.skip_if(_U):
			E=A.parse_or()
			if A.stream.skip_if(_L):C=A.parse_condexpr()
			else:C=_A
			B=nodes.CondExpr(E,B,C,lineno=D);D=A.stream.current.lineno
		return B
	def parse_or(A):
		C=A.stream.current.lineno;B=A.parse_and()
		while A.stream.skip_if(_e):D=A.parse_and();B=nodes.Or(B,D,lineno=C);C=A.stream.current.lineno
		return B
	def parse_and(A):
		C=A.stream.current.lineno;B=A.parse_not()
		while A.stream.skip_if(_f):D=A.parse_not();B=nodes.And(B,D,lineno=C);C=A.stream.current.lineno
		return B
	def parse_not(A):
		if A.stream.current.test(_V):B=next(A.stream).lineno;return nodes.Not(A.parse_not(),lineno=B)
		return A.parse_compare()
	def parse_compare(A):
		C=A.stream.current.lineno;D=A.parse_math1();B=[]
		while _B:
			E=A.stream.current.type
			if E in _compare_operators:next(A.stream);B.append(nodes.Operand(E,A.parse_math1()))
			elif A.stream.skip_if(_R):B.append(nodes.Operand('in',A.parse_math1()))
			elif A.stream.current.test(_V)and A.stream.look().test(_R):A.stream.skip(2);B.append(nodes.Operand('notin',A.parse_math1()))
			else:break
			C=A.stream.current.lineno
		if not B:return D
		return nodes.Compare(D,B,lineno=C)
	def parse_math1(A):
		C=A.stream.current.lineno;B=A.parse_concat()
		while A.stream.current.type in(_S,_P):D=_math_nodes[A.stream.current.type];next(A.stream);E=A.parse_concat();B=D(B,E,lineno=C);C=A.stream.current.lineno
		return B
	def parse_concat(A):
		C=A.stream.current.lineno;B=[A.parse_math2()]
		while A.stream.current.type=='tilde':next(A.stream);B.append(A.parse_math2())
		if len(B)==1:return B[0]
		return nodes.Concat(B,lineno=C)
	def parse_math2(A):
		C=A.stream.current.lineno;B=A.parse_pow()
		while A.stream.current.type in(_T,'div',_a,'mod'):D=_math_nodes[A.stream.current.type];next(A.stream);E=A.parse_pow();B=D(B,E,lineno=C);C=A.stream.current.lineno
		return B
	def parse_pow(A):
		C=A.stream.current.lineno;B=A.parse_unary()
		while A.stream.current.type=='pow':next(A.stream);D=A.parse_unary();B=nodes.Pow(B,D,lineno=C);C=A.stream.current.lineno
		return B
	def parse_unary(A,with_filter=_B):
		C=A.stream.current.type;D=A.stream.current.lineno;B:0
		if C==_P:next(A.stream);B=nodes.Neg(A.parse_unary(_C),lineno=D)
		elif C==_S:next(A.stream);B=nodes.Pos(A.parse_unary(_C),lineno=D)
		else:B=A.parse_primary()
		B=A.parse_postfix(B)
		if with_filter:B=A.parse_filter_expr(B)
		return B
	def parse_primary(B):
		F='True';E='true';A=B.stream.current;C:0
		if A.type==_D:
			if A.value in(E,'false',F,'False'):C=nodes.Const(A.value in(E,F),lineno=A.lineno)
			elif A.value in('none','None'):C=nodes.Const(_A,lineno=A.lineno)
			else:C=nodes.Name(A.value,_J,lineno=A.lineno)
			next(B.stream)
		elif A.type==_W:
			next(B.stream);D=[A.value];G=A.lineno
			while B.stream.current.type==_W:D.append(B.stream.current.value);next(B.stream)
			C=nodes.Const(''.join(D),lineno=G)
		elif A.type in(_X,'float'):next(B.stream);C=nodes.Const(A.value,lineno=A.lineno)
		elif A.type==_F:next(B.stream);C=B.parse_tuple(explicit_parentheses=_B);B.stream.expect(_G)
		elif A.type==_N:C=B.parse_list()
		elif A.type==_Y:C=B.parse_dict()
		else:B.fail(f"unexpected {describe_token(A)!r}",A.lineno)
		return C
	def parse_tuple(A,simplified=_C,with_condexpr=_B,extra_end_rules=_A,explicit_parentheses=_C):
		D=A.stream.current.lineno
		if simplified:C=A.parse_primary
		elif with_condexpr:C=A.parse_expression
		else:
			def C():return A.parse_expression(with_condexpr=_C)
		B=[];E=_C
		while _B:
			if B:A.stream.expect(_E)
			if A.is_tuple_end(extra_end_rules):break
			B.append(C())
			if A.stream.current.type==_E:E=_B
			else:break
			D=A.stream.current.lineno
		if not E:
			if B:return B[0]
			if not explicit_parentheses:A.fail(f"Expected an expression, got {describe_token(A.stream.current)!r}")
		return nodes.Tuple(B,_J,lineno=D)
	def parse_list(A):
		C=A.stream.expect(_N);B=[]
		while A.stream.current.type!=_H:
			if B:A.stream.expect(_E)
			if A.stream.current.type==_H:break
			B.append(A.parse_expression())
		A.stream.expect(_H);return nodes.List(B,lineno=C.lineno)
	def parse_dict(A):
		C='rbrace';E=A.stream.expect(_Y);B=[]
		while A.stream.current.type!=C:
			if B:A.stream.expect(_E)
			if A.stream.current.type==C:break
			D=A.parse_expression();A.stream.expect(_I);F=A.parse_expression();B.append(nodes.Pair(D,F,lineno=D.lineno))
		A.stream.expect(C);return nodes.Dict(B,lineno=E.lineno)
	def parse_postfix(B,node):
		A=node
		while _B:
			C=B.stream.current.type
			if C==_M or C==_N:A=B.parse_subscript(A)
			elif C==_F:A=B.parse_call(A)
			else:break
		return A
	def parse_filter_expr(B,node):
		A=node
		while _B:
			C=B.stream.current.type
			if C=='pipe':A=B.parse_filter(A)
			elif C==_D and B.stream.current.value=='is':A=B.parse_test(A)
			elif C==_F:A=B.parse_call(A)
			else:break
		return A
	def parse_subscript(A,node):
		F=node;B=next(A.stream);D:0
		if B.type==_M:
			C=A.stream.current;next(A.stream)
			if C.type==_D:return nodes.Getattr(F,C.value,_J,lineno=B.lineno)
			elif C.type!=_X:A.fail('expected name or number',C.lineno)
			D=nodes.Const(C.value,lineno=C.lineno);return nodes.Getitem(F,D,_J,lineno=B.lineno)
		if B.type==_N:
			E=[]
			while A.stream.current.type!=_H:
				if E:A.stream.expect(_E)
				E.append(A.parse_subscribed())
			A.stream.expect(_H)
			if len(E)==1:D=E[0]
			else:D=nodes.Tuple(E,_J,lineno=B.lineno)
			return nodes.Getitem(F,D,_J,lineno=B.lineno)
		A.fail('expected subscript expression',B.lineno)
	def parse_subscribed(A):
		D=A.stream.current.lineno;B:0
		if A.stream.current.type==_I:next(A.stream);B=[_A]
		else:
			C=A.parse_expression()
			if A.stream.current.type!=_I:return C
			next(A.stream);B=[C]
		if A.stream.current.type==_I:B.append(_A)
		elif A.stream.current.type not in(_H,_E):B.append(A.parse_expression())
		else:B.append(_A)
		if A.stream.current.type==_I:
			next(A.stream)
			if A.stream.current.type not in(_H,_E):B.append(A.parse_expression())
			else:B.append(_A)
		else:B.append(_A)
		return nodes.Slice(*(B),lineno=D)
	def parse_call_args(A):
		I=A.stream.expect(_F);F=[];E=[];C=_A;B=_A;G=_C
		def D(expr):
			if not expr:A.fail('invalid syntax for function call expression',I.lineno)
		while A.stream.current.type!=_G:
			if G:
				A.stream.expect(_E)
				if A.stream.current.type==_G:break
			if A.stream.current.type==_T:D(C is _A and B is _A);next(A.stream);C=A.parse_expression()
			elif A.stream.current.type=='pow':D(B is _A);next(A.stream);B=A.parse_expression()
			elif A.stream.current.type==_D and A.stream.look().type==_Q:D(B is _A);J=A.stream.current.value;A.stream.skip(2);H=A.parse_expression();E.append(nodes.Keyword(J,H,lineno=H.lineno))
			else:D(C is _A and B is _A and not E);F.append(A.parse_expression())
			G=_B
		A.stream.expect(_G);return F,E,C,B
	def parse_call(A,node):B=A.stream.current;C,D,E,F=A.parse_call_args();return nodes.Call(node,C,D,E,F,lineno=B.lineno)
	def parse_filter(A,node,start_inline=_C):
		C=start_inline;B=node
		while A.stream.current.type=='pipe'or C:
			if not C:next(A.stream)
			D=A.stream.expect(_D);E=D.value
			while A.stream.current.type==_M:next(A.stream);E+='.'+A.stream.expect(_D).value
			if A.stream.current.type==_F:F,G,H,I=A.parse_call_args()
			else:F=[];G=[];H=I=_A
			B=nodes.Filter(B,E,F,G,H,I,lineno=D.lineno);C=_C
		return B
	def parse_test(A,node):
		B=node;E=next(A.stream)
		if A.stream.current.test(_V):next(A.stream);F=_B
		else:F=_C
		G=A.stream.expect(_D).value
		while A.stream.current.type==_M:next(A.stream);G+='.'+A.stream.expect(_D).value
		H=I=_A;J=[]
		if A.stream.current.type==_F:C,J,H,I=A.parse_call_args()
		elif A.stream.current.type in{_D,_W,_X,'float',_F,_N,_Y}and not A.stream.current.test_any(_L,_e,_f):
			if A.stream.current.test('name:is'):A.fail('You cannot chain multiple tests with is')
			D=A.parse_primary();D=A.parse_postfix(D);C=[D]
		else:C=[]
		B=nodes.Test(B,G,C,J,H,I,lineno=E.lineno)
		if F:B=nodes.Not(B,lineno=E.lineno)
		return B
	def subparse(A,end_tokens=_A):
		C=end_tokens;D=[];E=[];G=E.append
		if C is not _A:A._end_token_stack.append(C)
		def H():
			if E:A=E[0].lineno;D.append(nodes.Output(E[:],lineno=A));del E[:]
		try:
			while A.stream:
				B=A.stream.current
				if B.type=='data':
					if B.value:G(nodes.TemplateData(B.value,lineno=B.lineno))
					next(A.stream)
				elif B.type=='variable_begin':next(A.stream);G(A.parse_tuple(with_condexpr=_B));A.stream.expect(_b)
				elif B.type=='block_begin':
					H();next(A.stream)
					if C is not _A and A.stream.current.test_any(*(C)):return D
					F=A.parse_statement()
					if isinstance(F,list):D.extend(F)
					else:D.append(F)
					A.stream.expect(_K)
				else:raise AssertionError('internal parsing error')
			H()
		finally:
			if C is not _A:A._end_token_stack.pop()
		return D
	def parse(A):B=nodes.Template(A.subparse(),lineno=1);B.set_environment(A.environment);return B