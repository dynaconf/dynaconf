_U='dyn_kwargs'
_T='dyn_args'
_S='kwargs'
_R='filter'
_Q='defaults'
_P='lineno'
_O='items'
_N='value'
_M='with_context'
_L='test'
_K='expr'
_J='args'
_I='target'
_H='template'
_G='ctx'
_F='node'
_E='name'
_D=False
_C='body'
_B=True
_A=None
import inspect,operator,typing as t
from collections import deque
from dynaconf.vendor.markupsafe import Markup
from .utils import _PassArg
if t.TYPE_CHECKING:import typing_extensions as te;from .environment import Environment
_NodeBound=t.TypeVar('_NodeBound',bound='Node')
_binop_to_func={'*':operator.mul,'/':operator.truediv,'//':operator.floordiv,'**':operator.pow,'%':operator.mod,'+':operator.add,'-':operator.sub}
_uaop_to_func={'not':operator.not_,'+':operator.pos,'-':operator.neg}
_cmpop_to_func={'eq':operator.eq,'ne':operator.ne,'gt':operator.gt,'gteq':operator.ge,'lt':operator.lt,'lteq':operator.le,'in':lambda a,b:a in b,'notin':lambda a,b:a not in b}
class Impossible(Exception):0
class NodeType(type):
	def __new__(D,name,bases,d):
		B=bases
		for C in ('fields','attributes'):A=[];A.extend(getattr(B[0]if B else object,C,()));A.extend(d.get(C,()));assert len(B)<=1,'multiple inheritance not allowed';assert len(A)==len(set(A)),'layout conflict';d[C]=tuple(A)
		d.setdefault('abstract',_D);return type.__new__(D,name,B,d)
class EvalContext:
	def __init__(A,environment,template_name=_A):
		B=environment;A.environment=B
		if callable(B.autoescape):A.autoescape=B.autoescape(template_name)
		else:A.autoescape=B.autoescape
		A.volatile=_D
	def save(A):return A.__dict__.copy()
	def revert(A,old):A.__dict__.clear();A.__dict__.update(old)
def get_eval_context(node,ctx):
	if ctx is _A:
		if node.environment is _A:raise RuntimeError('if no eval context is passed, the node must have an attached environment.')
		return EvalContext(node.environment)
	return ctx
class Node(metaclass=NodeType):
	fields=();attributes=_P,'environment';abstract=_B;lineno:0;environment:0
	def __init__(A,*B,**C):
		if A.abstract:raise TypeError('abstract nodes are not instantiable')
		if B:
			if len(B)!=len(A.fields):
				if not A.fields:raise TypeError(f"{type(A).__name__!r} takes 0 arguments")
				raise TypeError(f"{type(A).__name__!r} takes 0 or {len(A.fields)} argument{'s'if len(A.fields)!=1 else''}")
			for (E,F) in zip(A.fields,B):setattr(A,E,F)
		for D in A.attributes:setattr(A,D,C.pop(D,_A))
		if C:raise TypeError(f"unknown attribute {next(iter(C))!r}")
	def iter_fields(D,exclude=_A,only=_A):
		C=only;B=exclude
		for A in D.fields:
			if B is _A and C is _A or B is not _A and A not in B or C is not _A and A in C:
				try:yield(A,getattr(D,A))
				except AttributeError:pass
	def iter_child_nodes(C,exclude=_A,only=_A):
		for (D,A) in C.iter_fields(exclude,only):
			if isinstance(A,list):
				for B in A:
					if isinstance(B,Node):yield B
			elif isinstance(A,Node):yield A
	def find(A,node_type):
		for B in A.find_all(node_type):return B
		return _A
	def find_all(C,node_type):
		B=node_type
		for A in C.iter_child_nodes():
			if isinstance(A,B):yield A
			yield from A.find_all(B)
	def set_ctx(C,ctx):
		A=deque([C])
		while A:
			B=A.popleft()
			if _G in B.fields:B.ctx=ctx
			A.extend(B.iter_child_nodes())
		return C
	def set_lineno(C,lineno,override=_D):
		B=deque([C])
		while B:
			A=B.popleft()
			if _P in A.attributes:
				if A.lineno is _A or override:A.lineno=lineno
			B.extend(A.iter_child_nodes())
		return C
	def set_environment(B,environment):
		A=deque([B])
		while A:C=A.popleft();C.environment=environment;A.extend(C.iter_child_nodes())
		return B
	def __eq__(A,other):
		B=other
		if type(A)is not type(B):return NotImplemented
		return tuple(A.iter_fields())==tuple(B.iter_fields())
	def __hash__(A):return hash(tuple(A.iter_fields()))
	def __repr__(A):B=', '.join((f"{B}={getattr(A,B,_A)!r}"for B in A.fields));return f"{type(A).__name__}({B})"
	def dump(B):
		def C(node):
			B=node
			if not isinstance(B,Node):A.append(repr(B));return
			A.append(f"nodes.{type(B).__name__}(")
			if not B.fields:A.append(')');return
			for (D,F) in enumerate(B.fields):
				if D:A.append(', ')
				E=getattr(B,F)
				if isinstance(E,list):
					A.append('[')
					for (D,G) in enumerate(E):
						if D:A.append(', ')
						C(G)
					A.append(']')
				else:C(E)
			A.append(')')
		A=[];C(B);return ''.join(A)
class Stmt(Node):abstract=_B
class Helper(Node):abstract=_B
class Template(Node):fields=_C,;body:0
class Output(Stmt):fields='nodes',;nodes:0
class Extends(Stmt):fields=_H,;template:0
class For(Stmt):fields=_I,'iter',_C,'else_',_L,'recursive';target:0;iter:0;body:0;else_:0;test:0;recursive:0
class If(Stmt):fields=_L,_C,'elif_','else_';test:0;body:0;elif_:0;else_:0
class Macro(Stmt):fields=_E,_J,_Q,_C;name:0;args:0;defaults:0;body:0
class CallBlock(Stmt):fields='call',_J,_Q,_C;call:0;args:0;defaults:0;body:0
class FilterBlock(Stmt):fields=_C,_R;body:0;filter:0
class With(Stmt):fields='targets','values',_C;targets:0;values:0;body:0
class Block(Stmt):fields=_E,_C,'scoped','required';name:0;body:0;scoped:0;required:0
class Include(Stmt):fields=_H,_M,'ignore_missing';template:0;with_context:0;ignore_missing:0
class Import(Stmt):fields=_H,_I,_M;template:0;target:0;with_context:0
class FromImport(Stmt):fields=_H,'names',_M;template:0;names:0;with_context:0
class ExprStmt(Stmt):fields=_F,;node:0
class Assign(Stmt):fields=_I,_F;target:0;node:0
class AssignBlock(Stmt):fields=_I,_R,_C;target:0;filter:0;body:0
class Expr(Node):
	abstract=_B
	def as_const(A,eval_ctx=_A):raise Impossible()
	def can_assign(A):return _D
class BinExpr(Expr):
	fields='left','right';left:0;right:0;operator:0;abstract=_B
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A)
		if A.environment.sandboxed and B.operator in A.environment.intercepted_binops:raise Impossible()
		C=_binop_to_func[B.operator]
		try:return C(B.left.as_const(A),B.right.as_const(A))
		except Exception as D:raise Impossible() from D
class UnaryExpr(Expr):
	fields=_F,;node:0;operator:0;abstract=_B
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A)
		if A.environment.sandboxed and B.operator in A.environment.intercepted_unops:raise Impossible()
		C=_uaop_to_func[B.operator]
		try:return C(B.node.as_const(A))
		except Exception as D:raise Impossible() from D
class Name(Expr):
	fields=_E,_G;name:0;ctx:0
	def can_assign(A):return A.name not in{'true','false','none','True','False','None'}
class NSRef(Expr):
	fields=_E,'attr';name:0;attr:0
	def can_assign(A):return _B
class Literal(Expr):abstract=_B
class Const(Literal):
	fields=_N,;value:0
	def as_const(A,eval_ctx=_A):return A.value
	@classmethod
	def from_untrusted(B,value,lineno=_A,environment=_A):
		A=value;from .compiler import has_safe_repr as C
		if not C(A):raise Impossible()
		return B(A,lineno=lineno,environment=environment)
class TemplateData(Literal):
	fields='data',;data:0
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A)
		if A.volatile:raise Impossible()
		if A.autoescape:return Markup(B.data)
		return B.data
class Tuple(Literal):
	fields=_O,_G;items:0;ctx:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return tuple((C.as_const(A)for C in B.items))
	def can_assign(A):
		for B in A.items:
			if not B.can_assign():return _D
		return _B
class List(Literal):
	fields=_O,;items:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return[C.as_const(A)for C in B.items]
class Dict(Literal):
	fields=_O,;items:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return dict((C.as_const(A)for C in B.items))
class Pair(Helper):
	fields='key',_N;key:0;value:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return B.key.as_const(A),B.value.as_const(A)
class Keyword(Helper):
	fields='key',_N;key:0;value:0
	def as_const(A,eval_ctx=_A):B=eval_ctx;B=get_eval_context(A,B);return A.key,A.value.as_const(B)
class CondExpr(Expr):
	fields=_L,'expr1','expr2';test:0;expr1:0;expr2:0
	def as_const(A,eval_ctx=_A):
		B=eval_ctx;B=get_eval_context(A,B)
		if A.test.as_const(B):return A.expr1.as_const(B)
		if A.expr2 is _A:raise Impossible()
		return A.expr2.as_const(B)
def args_as_const(node,eval_ctx):
	B=eval_ctx;A=node;D=[C.as_const(B)for C in A.args];E=dict((C.as_const(B)for C in A.kwargs))
	if A.dyn_args is not _A:
		try:D.extend(A.dyn_args.as_const(B))
		except Exception as C:raise Impossible() from C
	if A.dyn_kwargs is not _A:
		try:E.update(A.dyn_kwargs.as_const(B))
		except Exception as C:raise Impossible() from C
	return D,E
class _FilterTestCommon(Expr):
	fields=_F,_E,_J,_S,_T,_U;node:0;name:0;args:0;kwargs:0;dyn_args:0;dyn_kwargs:0;abstract=_B;_is_filter=_B
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A)
		if A.volatile:raise Impossible()
		if B._is_filter:F=A.environment.filters
		else:F=A.environment.tests
		C=F.get(B.name);E=_PassArg.from_obj(C)
		if C is _A or E is _PassArg.context:raise Impossible()
		if A.environment.is_async and(getattr(C,'jinja_async_variant',_D)is _B or inspect.iscoroutinefunction(C)):raise Impossible()
		D,G=args_as_const(B,A);D.insert(0,B.node.as_const(A))
		if E is _PassArg.eval_context:D.insert(0,A)
		elif E is _PassArg.environment:D.insert(0,A.environment)
		try:return C(*(D),**G)
		except Exception as H:raise Impossible() from H
class Filter(_FilterTestCommon):
	node:0
	def as_const(A,eval_ctx=_A):
		if A.node is _A:raise Impossible()
		return super().as_const(eval_ctx=eval_ctx)
class Test(_FilterTestCommon):_is_filter=_D
class Call(Expr):fields=_F,_J,_S,_T,_U;node:0;args:0;kwargs:0;dyn_args:0;dyn_kwargs:0
class Getitem(Expr):
	fields=_F,'arg',_G;node:0;arg:0;ctx:0
	def as_const(B,eval_ctx=_A):
		A=eval_ctx
		if B.ctx!='load':raise Impossible()
		A=get_eval_context(B,A)
		try:return A.environment.getitem(B.node.as_const(A),B.arg.as_const(A))
		except Exception as C:raise Impossible() from C
class Getattr(Expr):
	fields=_F,'attr',_G;node:0;attr:0;ctx:0
	def as_const(A,eval_ctx=_A):
		B=eval_ctx
		if A.ctx!='load':raise Impossible()
		B=get_eval_context(A,B)
		try:return B.environment.getattr(A.node.as_const(B),A.attr)
		except Exception as C:raise Impossible() from C
class Slice(Expr):
	fields='start','stop','step';start:0;stop:0;step:0
	def as_const(A,eval_ctx=_A):
		B=eval_ctx;B=get_eval_context(A,B)
		def C(obj):
			if obj is _A:return _A
			return obj.as_const(B)
		return slice(C(A.start),C(A.stop),C(A.step))
class Concat(Expr):
	fields='nodes',;nodes:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return ''.join((str(C.as_const(A))for C in B.nodes))
class Compare(Expr):
	fields=_K,'ops';expr:0;ops:0
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A);C=D=B.expr.as_const(A)
		try:
			for E in B.ops:
				F=E.expr.as_const(A);C=_cmpop_to_func[E.op](D,F)
				if not C:return _D
				D=F
		except Exception as G:raise Impossible() from G
		return C
class Operand(Helper):fields='op',_K;op:0;expr:0
class Mul(BinExpr):operator='*'
class Div(BinExpr):operator='/'
class FloorDiv(BinExpr):operator='//'
class Add(BinExpr):operator='+'
class Sub(BinExpr):operator='-'
class Mod(BinExpr):operator='%'
class Pow(BinExpr):operator='**'
class And(BinExpr):
	operator='and'
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return B.left.as_const(A)and B.right.as_const(A)
class Or(BinExpr):
	operator='or'
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return B.left.as_const(A)or B.right.as_const(A)
class Not(UnaryExpr):operator='not'
class Neg(UnaryExpr):operator='-'
class Pos(UnaryExpr):operator='+'
class EnvironmentAttribute(Expr):fields=_E,;name:0
class ExtensionAttribute(Expr):fields='identifier',_E;identifier:0;name:0
class ImportedName(Expr):fields='importname',;importname:0
class InternalName(Expr):
	fields=_E,;name:0
	def __init__(A):raise TypeError("Can't create internal names.  Use the `free_identifier` method on a parser.")
class MarkSafe(Expr):
	fields=_K,;expr:0
	def as_const(B,eval_ctx=_A):A=eval_ctx;A=get_eval_context(B,A);return Markup(B.expr.as_const(A))
class MarkSafeIfAutoescape(Expr):
	fields=_K,;expr:0
	def as_const(B,eval_ctx=_A):
		A=eval_ctx;A=get_eval_context(B,A)
		if A.volatile:raise Impossible()
		C=B.expr.as_const(A)
		if A.autoescape:return Markup(C)
		return C
class ContextReference(Expr):0
class DerivedContextReference(Expr):0
class Continue(Stmt):0
class Break(Stmt):0
class Scope(Stmt):fields=_C,;body:0
class OverlayScope(Stmt):fields='context',_C;context:0;body:0
class EvalContextModifier(Stmt):fields='options',;options:0
class ScopedEvalContextModifier(EvalContextModifier):fields=_C,;body:0
def _failing_new(*A,**B):raise TypeError("can't create custom node types")
NodeType.__new__=staticmethod(_failing_new)
del _failing_new