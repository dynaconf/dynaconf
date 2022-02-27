import typing as t
from ast import literal_eval
from itertools import chain
from itertools import islice
from .  import nodes
from .compiler import CodeGenerator
from .compiler import Frame
from .compiler import has_safe_repr
from .environment import Environment
from .environment import Template
def native_concat(values):
	C=values;B=list(islice(C,2))
	if not B:return None
	if len(B)==1:
		A=B[0]
		if not isinstance(A,str):return A
	else:A=''.join([str(A)for A in chain(B,C)])
	try:return literal_eval(A)
	except (ValueError,SyntaxError,MemoryError):return A
class NativeCodeGenerator(CodeGenerator):
	@staticmethod
	def _default_finalize(value):return value
	def _output_const_repr(A,group):return repr(''.join([str(A)for A in group]))
	def _output_child_to_const(B,node,frame,finalize):
		A=node.as_const(frame.eval_ctx)
		if not has_safe_repr(A):raise nodes.Impossible()
		if isinstance(node,nodes.TemplateData):return A
		return finalize.const(A)
	def _output_child_pre(B,node,frame,finalize):
		A=finalize
		if A.src is not None:B.write(A.src)
	def _output_child_post(A,node,frame,finalize):
		if finalize.src is not None:A.write(')')
class NativeEnvironment(Environment):code_generator_class=NativeCodeGenerator
class NativeTemplate(Template):
	environment_class=NativeEnvironment
	def render(A,*B,**C):
		D=A.new_context(dict(*(B),**C))
		try:return native_concat(A.root_render_func(D))
		except Exception:return A.environment.handle_exception()
	async def render_async(A,*B,**C):
		if not A.environment.is_async:raise RuntimeError('The environment was not created with async mode enabled.')
		D=A.new_context(dict(*(B),**C))
		try:return native_concat([B async for B in A.root_render_func(D)])
		except Exception:return A.environment.handle_exception()
NativeEnvironment.template_class=NativeTemplate