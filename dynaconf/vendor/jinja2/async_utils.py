import inspect,typing as t
from functools import wraps
from .utils import _PassArg
from .utils import pass_eval_context
V=t.TypeVar('V')
def async_variant(normal_func):
	B=normal_func
	def A(async_func):
		C=_PassArg.from_obj(B);D=C is None
		if C is _PassArg.environment:
			def E(args):return t.cast(bool,args[0].is_async)
		else:
			def E(args):return t.cast(bool,args[0].environment.is_async)
		@wraps(B)
		def A(*A,**C):
			F=E(A)
			if D:A=A[1:]
			if F:return async_func(*(A),**C)
			return B(*(A),**C)
		if D:A=pass_eval_context(A)
		A.jinja_async_variant=True;return A
	return A
async def auto_await(value):
	A=value
	if inspect.isawaitable(A):return await t.cast('t.Awaitable[V]',A)
	return t.cast('V',A)
async def auto_aiter(iterable):
	A=iterable
	if hasattr(A,'__aiter__'):
		async for B in t.cast('t.AsyncIterable[V]',A):yield B
	else:
		for B in t.cast('t.Iterable[V]',A):yield B
async def auto_to_list(value):return[A async for A in auto_aiter(value)]