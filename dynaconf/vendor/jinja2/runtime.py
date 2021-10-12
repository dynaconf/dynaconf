_F='there is no next item'
_E='Undefined'
_D='caller'
_C=True
_B=False
_A=None
import functools,sys,typing as t
from collections import abc
from itertools import chain
from markupsafe import escape
from markupsafe import Markup
from markupsafe import soft_str
from .async_utils import auto_aiter
from .async_utils import auto_await
from .exceptions import TemplateNotFound
from .exceptions import TemplateRuntimeError
from .exceptions import UndefinedError
from .nodes import EvalContext
from .utils import _PassArg
from .utils import concat
from .utils import internalcode
from .utils import missing
from .utils import Namespace
from .utils import object_type_repr
from .utils import pass_eval_context
V=t.TypeVar('V')
F=t.TypeVar('F',bound=t.Callable[...,t.Any])
if t.TYPE_CHECKING:
	import logging,typing_extensions as te;from .environment import Environment
	class LoopRenderFunc(te.Protocol):
		def __call__(A,reciter,loop_render_func,depth=0):...
exported=['LoopContext','TemplateReference','Macro','Markup','TemplateRuntimeError','missing','concat','escape','markup_join','str_join','identity','TemplateNotFound','Namespace',_E,'internalcode']
async_exported=['AsyncLoopContext','auto_aiter','auto_await']
def identity(x):return x
def markup_join(seq):
	A=[];B=map(soft_str,seq)
	for C in B:
		A.append(C)
		if hasattr(C,'__html__'):return Markup('').join(chain(A,B))
	return concat(A)
def str_join(seq):return concat(map(str,seq))
def unicode_join(seq):import warnings as A;A.warn('This template must be recompiled with at least Jinja 3.0, or it will fail in Jinja 3.1.',DeprecationWarning,stacklevel=2);return str_join(seq)
def new_context(environment,template_name,blocks,vars=_A,shared=_B,globals=_A,locals=_A):
	C=shared;B=environment
	if vars is _A:vars={}
	if C:A=vars
	else:A=dict(globals or(),**vars)
	if locals:
		if C:A=dict(A)
		for (E,D) in locals.items():
			if D is not missing:A[E]=D
	return B.context_class(B,A,template_name,blocks,globals=globals)
class TemplateReference:
	def __init__(A,context):A.__context=context
	def __getitem__(A,name):B=A.__context.blocks[name];return BlockReference(name,A.__context,B,0)
	def __repr__(A):return f"<{type(A).__name__} {A.__context.name!r}>"
def _dict_method_all(dict_method):
	A=dict_method
	@functools.wraps(A)
	def B(self):return A(self.get_all())
	return t.cast(F,B)
@abc.Mapping.register
class Context:
	_legacy_resolve_mode=_B
	def __init_subclass__(A):
		if'resolve_or_missing'in A.__dict__:A._legacy_resolve_mode=_B
		elif'resolve'in A.__dict__ or A._legacy_resolve_mode:import warnings as B;B.warn("Overriding 'resolve' is deprecated and will not have the expected behavior in Jinja 3.1. Override 'resolve_or_missing' instead ",DeprecationWarning,stacklevel=2);A._legacy_resolve_mode=_C
	def __init__(A,environment,parent,name,blocks,globals=_A):A.parent=parent;A.vars={};A.environment=environment;A.eval_ctx=EvalContext(A.environment,name);A.exported_vars=set();A.name=name;A.globals_keys=set()if globals is _A else set(globals);A.blocks={A:[B]for(A,B)in blocks.items()}
	def super(A,name,current):
		B=name
		try:C=A.blocks[B];D=C.index(current)+1;C[D]
		except LookupError:return A.environment.undefined(f"there is no parent block called {B!r}.",name='super')
		return BlockReference(B,A,C,D)
	def get(A,key,default=_A):
		try:return A[key]
		except KeyError:return default
	def resolve(A,key):
		B=key
		if A._legacy_resolve_mode:
			if B in A.vars:return A.vars[B]
			if B in A.parent:return A.parent[B]
			return A.environment.undefined(name=B)
		C=A.resolve_or_missing(B)
		if C is missing:return A.environment.undefined(name=B)
		return C
	def resolve_or_missing(A,key):
		B=key
		if A._legacy_resolve_mode:
			C=A.resolve(B)
			if isinstance(C,Undefined):return missing
			return C
		if B in A.vars:return A.vars[B]
		if B in A.parent:return A.parent[B]
		return missing
	def get_exported(A):return{B:A.vars[B]for B in A.exported_vars}
	def get_all(A):
		if not A.vars:return A.parent
		if not A.parent:return A.vars
		return dict(A.parent,**A.vars)
	@internalcode
	def call(__self,__obj,*B,**C):
		G='_block_vars';F='_loop_vars';D=__obj;A=__self
		if __debug__:__traceback_hide__=_C
		if hasattr(D,'__call__')and _PassArg.from_obj(D.__call__)is not _A:D=D.__call__
		E=_PassArg.from_obj(D)
		if E is _PassArg.context:
			if C.get(F):A=A.derived(C[F])
			if C.get(G):A=A.derived(C[G])
			B=(A,)+B
		elif E is _PassArg.eval_context:B=(A.eval_ctx,)+B
		elif E is _PassArg.environment:B=(A.environment,)+B
		C.pop(G,_A);C.pop(F,_A)
		try:return D(*(B),**C)
		except StopIteration:return A.environment.undefined('value was undefined because a callable raised a StopIteration exception')
	def derived(A,locals=_A):B=new_context(A.environment,A.name,{},A.get_all(),_C,_A,locals);B.eval_ctx=A.eval_ctx;B.blocks.update(((B,list(C))for(B,C)in A.blocks.items()));return B
	keys=_dict_method_all(dict.keys);values=_dict_method_all(dict.values);items=_dict_method_all(dict.items)
	def __contains__(A,name):return name in A.vars or name in A.parent
	def __getitem__(B,key):
		A=B.resolve_or_missing(key)
		if A is missing:raise KeyError(key)
		return A
	def __repr__(A):return f"<{type(A).__name__} {A.get_all()!r} of {A.name!r}>"
class BlockReference:
	def __init__(A,name,context,stack,depth):A.name=name;A._context=context;A._stack=stack;A._depth=depth
	@property
	def super(self):
		A=self
		if A._depth+1>=len(A._stack):return A._context.environment.undefined(f"there is no parent block called {A.name!r}.",name='super')
		return BlockReference(A.name,A._context,A._stack,A._depth+1)
	@internalcode
	async def _async_call(self):
		A=self;B=concat([B async for B in A._stack[A._depth](A._context)])
		if A._context.eval_ctx.autoescape:return Markup(B)
		return B
	@internalcode
	def __call__(self):
		A=self
		if A._context.environment.is_async:return A._async_call()
		B=concat(A._stack[A._depth](A._context))
		if A._context.eval_ctx.autoescape:return Markup(B)
		return B
class LoopContext:
	index0=-1;_length=_A;_after=missing;_current=missing;_before=missing;_last_changed_value=missing
	def __init__(A,iterable,undefined,recurse=_A,depth0=0):B=iterable;A._iterable=B;A._iterator=A._to_iterator(B);A._undefined=undefined;A._recurse=recurse;A.depth0=depth0
	@staticmethod
	def _to_iterator(iterable):return iter(iterable)
	@property
	def length(self):
		A=self
		if A._length is not _A:return A._length
		try:A._length=len(A._iterable)
		except TypeError:B=list(A._iterator);A._iterator=A._to_iterator(B);A._length=len(B)+A.index+(A._after is not missing)
		return A._length
	def __len__(A):return A.length
	@property
	def depth(self):return self.depth0+1
	@property
	def index(self):return self.index0+1
	@property
	def revindex0(self):return self.length-self.index
	@property
	def revindex(self):return self.length-self.index0
	@property
	def first(self):return self.index0==0
	def _peek_next(A):
		if A._after is not missing:return A._after
		A._after=next(A._iterator,missing);return A._after
	@property
	def last(self):return self._peek_next()is missing
	@property
	def previtem(self):
		A=self
		if A.first:return A._undefined('there is no previous item')
		return A._before
	@property
	def nextitem(self):
		A=self._peek_next()
		if A is missing:return self._undefined(_F)
		return A
	def cycle(B,*A):
		if not A:raise TypeError('no items for cycling given')
		return A[B.index0%len(A)]
	def changed(A,*B):
		if A._last_changed_value!=B:A._last_changed_value=B;return _C
		return _B
	def __iter__(A):return A
	def __next__(A):
		if A._after is not missing:B=A._after;A._after=missing
		else:B=next(A._iterator)
		A.index0+=1;A._before=A._current;A._current=B;return B,A
	@internalcode
	def __call__(self,iterable):
		A=self
		if A._recurse is _A:raise TypeError("The loop must have the 'recursive' marker to be called recursively.")
		return A._recurse(iterable,A._recurse,depth=A.depth)
	def __repr__(A):return f"<{type(A).__name__} {A.index}/{A.length}>"
class AsyncLoopContext(LoopContext):
	_iterator:0
	@staticmethod
	def _to_iterator(iterable):return auto_aiter(iterable)
	@property
	async def length(self):
		A=self
		if A._length is not _A:return A._length
		try:A._length=len(A._iterable)
		except TypeError:B=[B async for B in A._iterator];A._iterator=A._to_iterator(B);A._length=len(B)+A.index+(A._after is not missing)
		return A._length
	@property
	async def revindex0(self):return await self.length-self.index
	@property
	async def revindex(self):return await self.length-self.index0
	async def _peek_next(A):
		if A._after is not missing:return A._after
		try:A._after=await A._iterator.__anext__()
		except StopAsyncIteration:A._after=missing
		return A._after
	@property
	async def last(self):return await self._peek_next()is missing
	@property
	async def nextitem(self):
		A=await self._peek_next()
		if A is missing:return self._undefined(_F)
		return A
	def __aiter__(A):return A
	async def __anext__(A):
		if A._after is not missing:B=A._after;A._after=missing
		else:B=await A._iterator.__anext__()
		A.index0+=1;A._before=A._current;A._current=B;return B,A
class Macro:
	def __init__(A,environment,func,name,arguments,catch_kwargs,catch_varargs,caller,default_autoescape=_A):
		D=arguments;C=default_autoescape;B=environment;A._environment=B;A._func=func;A._argument_count=len(D);A.name=name;A.arguments=D;A.catch_kwargs=catch_kwargs;A.catch_varargs=catch_varargs;A.caller=caller;A.explicit_caller=_D in D
		if C is _A:
			if callable(B.autoescape):C=B.autoescape(_A)
			else:C=B.autoescape
		A._default_autoescape=C
	@internalcode
	@pass_eval_context
	def __call__(self,*B,**D):
		A=self
		if B and isinstance(B[0],EvalContext):G=B[0].autoescape;B=B[1:]
		else:G=A._default_autoescape
		C=list(B[:A._argument_count]);J=len(C);E=_B
		if J!=A._argument_count:
			for H in A.arguments[len(C):]:
				try:I=D.pop(H)
				except KeyError:I=missing
				if H==_D:E=_C
				C.append(I)
		else:E=A.explicit_caller
		if A.caller and not E:
			F=D.pop(_D,_A)
			if F is _A:F=A._environment.undefined('No caller defined',name=_D)
			C.append(F)
		if A.catch_kwargs:C.append(D)
		elif D:
			if _D in D:raise TypeError(f"macro {A.name!r} was invoked with two values for the special caller argument. This is most likely a bug.")
			raise TypeError(f"macro {A.name!r} takes no keyword argument {next(iter(D))!r}")
		if A.catch_varargs:C.append(B[A._argument_count:])
		elif len(B)>A._argument_count:raise TypeError(f"macro {A.name!r} takes not more than {len(A.arguments)} argument(s)")
		return A._invoke(C,G)
	async def _async_invoke(B,arguments,autoescape):
		A=await B._func(*(arguments))
		if autoescape:return Markup(A)
		return A
	def _invoke(A,arguments,autoescape):
		D=autoescape;C=arguments
		if A._environment.is_async:return A._async_invoke(C,D)
		B=A._func(*(C))
		if D:B=Markup(B)
		return B
	def __repr__(A):B='anonymous'if A.name is _A else repr(A.name);return f"<{type(A).__name__} {B}>"
class Undefined:
	__slots__='_undefined_hint','_undefined_obj','_undefined_name','_undefined_exception'
	def __init__(A,hint=_A,obj=missing,name=_A,exc=UndefinedError):A._undefined_hint=hint;A._undefined_obj=obj;A._undefined_name=name;A._undefined_exception=exc
	@property
	def _undefined_message(self):
		A=self
		if A._undefined_hint:return A._undefined_hint
		if A._undefined_obj is missing:return f"{A._undefined_name!r} is undefined"
		if not isinstance(A._undefined_name,str):return f"{object_type_repr(A._undefined_obj)} has no element {A._undefined_name!r}"
		return f"{object_type_repr(A._undefined_obj)!r} has no attribute {A._undefined_name!r}"
	@internalcode
	def _fail_with_undefined_error(self,*A,**B):raise self._undefined_exception(self._undefined_message)
	@internalcode
	def __getattr__(self,name):
		if name[:2]=='__':raise AttributeError(name)
		return self._fail_with_undefined_error()
	__add__=__radd__=__sub__=__rsub__=_fail_with_undefined_error;__mul__=__rmul__=__div__=__rdiv__=_fail_with_undefined_error;__truediv__=__rtruediv__=_fail_with_undefined_error;__floordiv__=__rfloordiv__=_fail_with_undefined_error;__mod__=__rmod__=_fail_with_undefined_error;__pos__=__neg__=_fail_with_undefined_error;__call__=__getitem__=_fail_with_undefined_error;__lt__=__le__=__gt__=__ge__=_fail_with_undefined_error;__int__=__float__=__complex__=_fail_with_undefined_error;__pow__=__rpow__=_fail_with_undefined_error
	def __eq__(A,other):return type(A)is type(other)
	def __ne__(A,other):return not A.__eq__(other)
	def __hash__(A):return id(type(A))
	def __str__(A):return''
	def __len__(A):return 0
	def __iter__(A):yield from()
	async def __aiter__(A):
		for B in ():yield
	def __bool__(A):return _B
	def __repr__(A):return _E
def make_logging_undefined(logger=_A,base=Undefined):
	A=logger
	if A is _A:import logging as C;A=C.getLogger(__name__);A.addHandler(C.StreamHandler(sys.stderr))
	def B(undef):A.warning('Template variable warning: %s',undef._undefined_message)
	class D(base):
		__slots__=()
		def _fail_with_undefined_error(C,*D,**E):
			try:super()._fail_with_undefined_error(*(D),**E)
			except C._undefined_exception as B:A.error('Template variable error: %s',B);raise B
		def __str__(A):B(A);return super().__str__()
		def __iter__(A):B(A);return super().__iter__()
		def __bool__(A):B(A);return super().__bool__()
	return D
class ChainableUndefined(Undefined):
	__slots__=()
	def __html__(A):return str(A)
	def __getattr__(A,_):return A
	__getitem__=__getattr__
class DebugUndefined(Undefined):
	__slots__=()
	def __str__(A):
		if A._undefined_hint:B=f"undefined value printed: {A._undefined_hint}"
		elif A._undefined_obj is missing:B=A._undefined_name
		else:B=f"no such element: {object_type_repr(A._undefined_obj)}[{A._undefined_name!r}]"
		return f"{{{{ {B} }}}}"
class StrictUndefined(Undefined):__slots__=();__iter__=__str__=__len__=Undefined._fail_with_undefined_error;__eq__=__ne__=__bool__=__hash__=Undefined._fail_with_undefined_error;__contains__=Undefined._fail_with_undefined_error
del(Undefined.__slots__,ChainableUndefined.__slots__,DebugUndefined.__slots__,StrictUndefined.__slots__)