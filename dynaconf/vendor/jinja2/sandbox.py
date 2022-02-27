_J='format_map'
_I='extend'
_H='append'
_G='update'
_F='remove'
_E='pop'
_D='clear'
_C=False
_B=None
_A=True
import operator,types,typing as t
from _string import formatter_field_name_split
from collections import abc
from collections import deque
from string import Formatter
from dynaconf.vendor.markupsafe import EscapeFormatter
from dynaconf.vendor.markupsafe import Markup
from .environment import Environment
from .exceptions import SecurityError
from .runtime import Context
from .runtime import Undefined
F=t.TypeVar('F',bound=t.Callable[...,t.Any])
MAX_RANGE=100000
UNSAFE_FUNCTION_ATTRIBUTES=set()
UNSAFE_METHOD_ATTRIBUTES=set()
UNSAFE_GENERATOR_ATTRIBUTES={'gi_frame','gi_code'}
UNSAFE_COROUTINE_ATTRIBUTES={'cr_frame','cr_code'}
UNSAFE_ASYNC_GENERATOR_ATTRIBUTES={'ag_code','ag_frame'}
_mutable_spec=(abc.MutableSet,frozenset(['add',_D,'difference_update','discard',_E,_F,'symmetric_difference_update',_G])),(abc.MutableMapping,frozenset([_D,_E,'popitem','setdefault',_G])),(abc.MutableSequence,frozenset([_H,'reverse','insert','sort',_I,_F])),(deque,frozenset([_H,'appendleft',_D,_I,'extendleft',_E,'popleft',_F,'rotate']))
def inspect_format_method(callable):
	if not isinstance(callable,(types.MethodType,types.BuiltinMethodType))or callable.__name__ not in('format',_J):return _B
	A=callable.__self__
	if isinstance(A,str):return A
	return _B
def safe_range(*B):
	A=range(*(B))
	if len(A)>MAX_RANGE:raise OverflowError(f"Range too big. The sandbox blocks ranges larger than MAX_RANGE ({MAX_RANGE}).")
	return A
def unsafe(f):f.unsafe_callable=_A;return f
def is_internal_attribute(obj,attr):
	B=obj;A=attr
	if isinstance(B,types.FunctionType):
		if A in UNSAFE_FUNCTION_ATTRIBUTES:return _A
	elif isinstance(B,types.MethodType):
		if A in UNSAFE_FUNCTION_ATTRIBUTES or A in UNSAFE_METHOD_ATTRIBUTES:return _A
	elif isinstance(B,type):
		if A=='mro':return _A
	elif isinstance(B,(types.CodeType,types.TracebackType,types.FrameType)):return _A
	elif isinstance(B,types.GeneratorType):
		if A in UNSAFE_GENERATOR_ATTRIBUTES:return _A
	elif hasattr(types,'CoroutineType')and isinstance(B,types.CoroutineType):
		if A in UNSAFE_COROUTINE_ATTRIBUTES:return _A
	elif hasattr(types,'AsyncGeneratorType')and isinstance(B,types.AsyncGeneratorType):
		if A in UNSAFE_ASYNC_GENERATOR_ATTRIBUTES:return _A
	return A.startswith('__')
def modifies_known_mutable(obj,attr):
	for (A,B) in _mutable_spec:
		if isinstance(obj,A):return attr in B
	return _C
class SandboxedEnvironment(Environment):
	sandboxed=_A;default_binop_table={'+':operator.add,'-':operator.sub,'*':operator.mul,'/':operator.truediv,'//':operator.floordiv,'**':operator.pow,'%':operator.mod};default_unop_table={'+':operator.pos,'-':operator.neg};intercepted_binops=frozenset();intercepted_unops=frozenset()
	def __init__(A,*B,**C):super().__init__(*(B),**C);A.globals['range']=safe_range;A.binop_table=A.default_binop_table.copy();A.unop_table=A.default_unop_table.copy()
	def is_safe_attribute(A,obj,attr,value):return not(attr.startswith('_')or is_internal_attribute(obj,attr))
	def is_safe_callable(A,obj):return not(getattr(obj,'unsafe_callable',_C)or getattr(obj,'alters_data',_C))
	def call_binop(A,context,operator,left,right):return A.binop_table[operator](left,right)
	def call_unop(A,context,operator,arg):return A.unop_table[operator](arg)
	def getitem(C,obj,argument):
		B=obj;A=argument
		try:return B[A]
		except (TypeError,LookupError):
			if isinstance(A,str):
				try:E=str(A)
				except Exception:pass
				else:
					try:D=getattr(B,E)
					except AttributeError:pass
					else:
						if C.is_safe_attribute(B,A,D):return D
						return C.unsafe_undefined(B,A)
		return C.undefined(obj=B,name=A)
	def getattr(C,obj,attribute):
		B=attribute;A=obj
		try:D=getattr(A,B)
		except AttributeError:
			try:return A[B]
			except (TypeError,LookupError):pass
		else:
			if C.is_safe_attribute(A,B,D):return D
			return C.unsafe_undefined(A,B)
		return C.undefined(obj=A,name=B)
	def unsafe_undefined(B,obj,attribute):A=attribute;return B.undefined(f"access to attribute {A!r} of {type(obj).__name__!r} object is unsafe.",name=A,obj=obj,exc=SecurityError)
	def format_string(D,s,args,kwargs,format_func=_B):
		E=format_func;B=kwargs;A=args;C:0
		if isinstance(s,Markup):C=SandboxedEscapeFormatter(D,escape=s.escape)
		else:C=SandboxedFormatter(D)
		if E is not _B and E.__name__==_J:
			if len(A)!=1 or B:raise TypeError(f"format_map() takes exactly one argument {len(A)+(B is not _B)} given")
			B=A[0];A=()
		F=C.vformat(s,A,B);return type(s)(F)
	def call(B,__context,__obj,*C,**D):
		A=__obj;E=inspect_format_method(A)
		if E is not _B:return B.format_string(E,C,D,A)
		if not B.is_safe_callable(A):raise SecurityError(f"{A!r} is not safely callable")
		return __context.call(A,*(C),**D)
class ImmutableSandboxedEnvironment(SandboxedEnvironment):
	def is_safe_attribute(A,obj,attr,value):
		if not super().is_safe_attribute(obj,attr,value):return _C
		return not modifies_known_mutable(obj,attr)
class SandboxedFormatter(Formatter):
	def __init__(A,env,**B):A._env=env;super().__init__(**B)
	def get_field(B,field_name,args,kwargs):
		C,E=formatter_field_name_split(field_name);A=B.get_value(C,args,kwargs)
		for (F,D) in E:
			if F:A=B._env.getattr(A,D)
			else:A=B._env.getitem(A,D)
		return A,C
class SandboxedEscapeFormatter(SandboxedFormatter,EscapeFormatter):0