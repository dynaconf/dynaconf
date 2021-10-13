_S='await auto_await('
_R='(await auto_await('
_Q='context.eval_ctx'
_P='await '
_O='if parent_template is None:'
_N='if parent_template is not None:'
_M='environment'
_L='else:'
_K='))'
_J=' = '
_I='yield '
_H='context'
_G='caller'
_F=':'
_E=', '
_D=')'
_C=True
_B=False
_A=None
import typing as t
from contextlib import contextmanager
from functools import update_wrapper
from io import StringIO
from itertools import chain
from keyword import iskeyword as is_python_keyword
from dynaconf.vendor.markupsafe import escape
from dynaconf.vendor.markupsafe import Markup
from .  import nodes
from .exceptions import TemplateAssertionError
from .idtracking import Symbols
from .idtracking import VAR_LOAD_ALIAS
from .idtracking import VAR_LOAD_PARAMETER
from .idtracking import VAR_LOAD_RESOLVE
from .idtracking import VAR_LOAD_UNDEFINED
from .nodes import EvalContext
from .optimizer import Optimizer
from .utils import _PassArg
from .utils import concat
from .visitor import NodeVisitor
if t.TYPE_CHECKING:import typing_extensions as te;from .environment import Environment
F=t.TypeVar('F',bound=t.Callable[...,t.Any])
operators={'eq':'==','ne':'!=','gt':'>','gteq':'>=','lt':'<','lteq':'<=','in':'in','notin':'not in'}
def optimizeconst(f):
	def A(self,node,frame,**E):
		C=node;B=frame;A=self
		if A.optimizer is not _A and not B.eval_ctx.volatile:
			D=A.optimizer.visit(C,B.eval_ctx)
			if D!=C:return A.visit(D,B)
		return f(A,C,B,**E)
	return update_wrapper(t.cast(F,A),f)
def _make_binop(op):
	@optimizeconst
	def A(self,node,frame):
		C=frame;B=node;A=self
		if A.environment.sandboxed and op in A.environment.intercepted_binops:A.write(f"environment.call_binop(context, {op!r}, ");A.visit(B.left,C);A.write(_E);A.visit(B.right,C)
		else:A.write('(');A.visit(B.left,C);A.write(f" {op} ");A.visit(B.right,C)
		A.write(_D)
	return A
def _make_unop(op):
	@optimizeconst
	def A(self,node,frame):
		B=frame;A=self
		if A.environment.sandboxed and op in A.environment.intercepted_unops:A.write(f"environment.call_unop(context, {op!r}, ");A.visit(node.node,B)
		else:A.write('('+op);A.visit(node.node,B)
		A.write(_D)
	return A
def generate(node,environment,name,filename,stream=_A,defer_init=_B,optimized=_C):
	B=stream;A=environment
	if not isinstance(node,nodes.Template):raise TypeError("Can't compile non template nodes")
	C=A.code_generator_class(A,name,filename,B,defer_init,optimized);C.visit(node)
	if B is _A:return C.stream.getvalue()
	return _A
def has_safe_repr(value):
	A=value
	if A is _A or A is NotImplemented or A is Ellipsis:return _C
	if type(A)in{bool,int,float,complex,range,str,Markup}:return _C
	if type(A)in{tuple,list,set,frozenset}:return all((has_safe_repr(B)for B in A))
	if type(A)is dict:return all((has_safe_repr(B)and has_safe_repr(C)for(B,C)in A.items()))
	return _B
def find_undeclared(nodes,names):
	A=UndeclaredNameVisitor(names)
	try:
		for B in nodes:A.visit(B)
	except VisitorExit:pass
	return A.undeclared
class MacroRef:
	def __init__(A,node):A.node=node;A.accesses_caller=_B;A.accesses_kwargs=_B;A.accesses_varargs=_B
class Frame:
	def __init__(A,eval_ctx,parent=_A,level=_A):
		C=level;B=parent;A.eval_ctx=eval_ctx;A.parent=B
		if B is _A:A.symbols=Symbols(level=C);A.require_output_check=_B;A.buffer=_A;A.block=_A
		else:A.symbols=Symbols(B.symbols,level=C);A.require_output_check=B.require_output_check;A.buffer=B.buffer;A.block=B.block
		A.toplevel=_B;A.rootlevel=_B;A.loop_frame=_B;A.block_frame=_B;A.soft_frame=_B
	def copy(A):B=t.cast(Frame,object.__new__(A.__class__));B.__dict__.update(A.__dict__);B.symbols=A.symbols.copy();return B
	def inner(A,isolated=_B):
		if isolated:return Frame(A.eval_ctx,level=A.symbols.level+1)
		return Frame(A.eval_ctx,A)
	def soft(B):A=B.copy();A.rootlevel=_B;A.soft_frame=_C;return A
	__copy__=copy
class VisitorExit(RuntimeError):0
class DependencyFinderVisitor(NodeVisitor):
	def __init__(A):A.filters=set();A.tests=set()
	def visit_Filter(A,node):A.generic_visit(node);A.filters.add(node.name)
	def visit_Test(A,node):A.generic_visit(node);A.tests.add(node.name)
	def visit_Block(A,node):0
class UndeclaredNameVisitor(NodeVisitor):
	def __init__(A,names):A.names=set(names);A.undeclared=set()
	def visit_Name(A,node):
		B=node
		if B.ctx=='load'and B.name in A.names:
			A.undeclared.add(B.name)
			if A.undeclared==A.names:raise VisitorExit()
		else:A.names.discard(B.name)
	def visit_Block(A,node):0
class CompilerExit(Exception):0
class CodeGenerator(NodeVisitor):
	def __init__(A,environment,name,filename,stream=_A,defer_init=_B,optimized=_C):
		C=environment;B=stream
		if B is _A:B=StringIO()
		A.environment=C;A.name=name;A.filename=filename;A.stream=B;A.created_block_context=_B;A.defer_init=defer_init;A.optimizer=_A
		if optimized:A.optimizer=Optimizer(C)
		A.import_aliases={};A.blocks={};A.extends_so_far=0;A.has_known_extends=_B;A.code_lineno=1;A.tests={};A.filters={};A.debug_info=[];A._write_debug_info=_A;A._new_lines=0;A._last_line=0;A._first_write=_C;A._last_identifier=0;A._indentation=0;A._assign_stack=[];A._param_def_block=[];A._context_reference_stack=[_H]
	@property
	def optimized(self):return self.optimizer is not _A
	def fail(A,msg,lineno):raise TemplateAssertionError(msg,lineno,A.name,A.filename)
	def temporary_identifier(A):A._last_identifier+=1;return f"t_{A._last_identifier}"
	def buffer(A,frame):B=frame;B.buffer=A.temporary_identifier();A.writeline(f"{B.buffer} = []")
	def return_buffer_contents(A,frame,force_unescaped=_B):
		B=frame
		if not force_unescaped:
			if B.eval_ctx.volatile:A.writeline('if context.eval_ctx.autoescape:');A.indent();A.writeline(f"return Markup(concat({B.buffer}))");A.outdent();A.writeline(_L);A.indent();A.writeline(f"return concat({B.buffer})");A.outdent();return
			elif B.eval_ctx.autoescape:A.writeline(f"return Markup(concat({B.buffer}))");return
		A.writeline(f"return concat({B.buffer})")
	def indent(A):A._indentation+=1
	def outdent(A,step=1):A._indentation-=step
	def start_write(A,frame,node=_A):
		B=frame
		if B.buffer is _A:A.writeline(_I,node)
		else:A.writeline(f"{B.buffer}.append(",node)
	def end_write(A,frame):
		if frame.buffer is not _A:A.write(_D)
	def simple_write(A,s,frame,node=_A):B=frame;A.start_write(B,node);A.write(s);A.end_write(B)
	def blockvisit(A,nodes,frame):
		try:
			A.writeline('pass')
			for B in nodes:A.visit(B,frame)
		except CompilerExit:pass
	def write(A,x):
		if A._new_lines:
			if not A._first_write:
				A.stream.write('\n'*A._new_lines);A.code_lineno+=A._new_lines
				if A._write_debug_info is not _A:A.debug_info.append((A._write_debug_info,A.code_lineno));A._write_debug_info=_A
			A._first_write=_B;A.stream.write('    '*A._indentation);A._new_lines=0
		A.stream.write(x)
	def writeline(A,x,node=_A,extra=0):A.newline(node,extra);A.write(x)
	def newline(A,node=_A,extra=0):
		B=node;A._new_lines=max(A._new_lines,1+extra)
		if B is not _A and B.lineno!=A._last_line:A._write_debug_info=B.lineno;A._last_line=B.lineno
	def signature(A,node,frame,extra_kwargs=_A):
		D=extra_kwargs;C=frame;B=node;H=any((is_python_keyword(t.cast(str,A))for A in chain((A.key for A in B.kwargs),D or())))
		for I in B.args:A.write(_E);A.visit(I,C)
		if not H:
			for E in B.kwargs:A.write(_E);A.visit(E,C)
			if D is not _A:
				for (F,G) in D.items():A.write(f", {F}={G}")
		if B.dyn_args:A.write(', *');A.visit(B.dyn_args,C)
		if H:
			if B.dyn_kwargs is not _A:A.write(', **dict({')
			else:A.write(', **{')
			for E in B.kwargs:A.write(f"{E.key!r}: ");A.visit(E.value,C);A.write(_E)
			if D is not _A:
				for (F,G) in D.items():A.write(f"{F!r}: {G}, ")
			if B.dyn_kwargs is not _A:A.write('}, **');A.visit(B.dyn_kwargs,C);A.write(_D)
			else:A.write('}')
		elif B.dyn_kwargs is not _A:A.write(', **');A.visit(B.dyn_kwargs,C)
	def pull_dependencies(A,nodes):
		D=DependencyFinderVisitor()
		for F in nodes:D.visit(F)
		for (C,G,E) in ((A.filters,D.filters,'filters'),(A.tests,D.tests,'tests')):
			for B in sorted(G):
				if B not in C:C[B]=A.temporary_identifier()
				A.writeline('try:');A.indent();A.writeline(f"{C[B]} = environment.{E}[{B!r}]");A.outdent();A.writeline('except KeyError:');A.indent();A.writeline('@internalcode');A.writeline(f"def {C[B]}(*unused):");A.indent();A.writeline(f'raise TemplateRuntimeError("No {E[:-1]} named {B!r} found.")');A.outdent();A.outdent()
	def enter_frame(A,frame):
		C=[]
		for (D,(B,E)) in frame.symbols.loads.items():
			if B==VAR_LOAD_PARAMETER:0
			elif B==VAR_LOAD_RESOLVE:A.writeline(f"{D} = {A.get_resolve_func()}({E!r})")
			elif B==VAR_LOAD_ALIAS:A.writeline(f"{D} = {E}")
			elif B==VAR_LOAD_UNDEFINED:C.append(D)
			else:raise NotImplementedError('unknown load instruction')
		if C:A.writeline(f"{_J.join(C)} = missing")
	def leave_frame(B,frame,with_python_scope=_B):
		if not with_python_scope:
			A=[]
			for C in frame.symbols.loads:A.append(C)
			if A:B.writeline(f"{_J.join(A)} = missing")
	def choose_async(A,async_value='async ',sync_value=''):return async_value if A.environment.is_async else sync_value
	def func(A,name):return f"{A.choose_async()}def {name}"
	def macro_body(A,node,frame):
		G='varargs';F='kwargs';C=node;B=frame;B=B.inner();B.symbols.analyze_node(C);H=MacroRef(C);J=_A;K=set();E=[]
		for (L,D) in enumerate(C.args):
			if D.name==_G:J=L
			if D.name in(F,G):K.add(D.name)
			E.append(B.symbols.ref(D.name))
		M=find_undeclared(C.body,(_G,F,G))
		if _G in M:
			if J is not _A:
				try:C.defaults[J-len(C.args)]
				except IndexError:A.fail('When defining macros or call blocks the special "caller" argument must be omitted or be given a default.',C.lineno)
			else:E.append(B.symbols.declare_parameter(_G))
			H.accesses_caller=_C
		if F in M and F not in K:E.append(B.symbols.declare_parameter(F));H.accesses_kwargs=_C
		if G in M and G not in K:E.append(B.symbols.declare_parameter(G));H.accesses_varargs=_C
		B.require_output_check=_B;B.symbols.analyze_node(C);A.writeline(f"{A.func('macro')}({_E.join(E)}):",C);A.indent();A.buffer(B);A.enter_frame(B);A.push_parameter_definitions(B)
		for (L,D) in enumerate(C.args):
			I=B.symbols.ref(D.name);A.writeline(f"if {I} is missing:");A.indent()
			try:N=C.defaults[L-len(C.args)]
			except IndexError:A.writeline(f'{I} = undefined("parameter {D.name!r} was not provided", name={D.name!r})')
			else:A.writeline(f"{I} = ");A.visit(N,B)
			A.mark_parameter_stored(I);A.outdent()
		A.pop_parameter_definitions();A.blockvisit(C.body,B);A.return_buffer_contents(B,force_unescaped=_C);A.leave_frame(B,with_python_scope=_C);A.outdent();return B,H
	def macro_def(C,macro_ref,frame):
		A=macro_ref;B=_E.join((repr(B.name)for B in A.node.args));D=getattr(A.node,'name',_A)
		if len(A.node.args)==1:B+=','
		C.write(f"Macro(environment, macro, {D!r}, ({B}), {A.accesses_kwargs!r}, {A.accesses_varargs!r}, {A.accesses_caller!r}, context.eval_ctx.autoescape)")
	def position(B,node):
		A=f"line {node.lineno}"
		if B.name is not _A:A=f"{A} in {B.name!r}"
		return A
	def dump_local_context(B,frame):A=_E.join((f"{A!r}: {B}"for(A,B)in frame.symbols.dump_stores().items()));return f"{{{A}}}"
	def write_commons(A):A.writeline('resolve = context.resolve_or_missing');A.writeline('undefined = environment.undefined');A.writeline('cond_expr_undefined = Undefined');A.writeline('if 0: yield None')
	def push_parameter_definitions(A,frame):A._param_def_block.append(frame.symbols.dump_param_targets())
	def pop_parameter_definitions(A):A._param_def_block.pop()
	def mark_parameter_stored(A,target):
		if A._param_def_block:A._param_def_block[-1].discard(target)
	def push_context_reference(A,target):A._context_reference_stack.append(target)
	def pop_context_reference(A):A._context_reference_stack.pop()
	def get_context_ref(A):return A._context_reference_stack[-1]
	def get_resolve_func(B):
		A=B._context_reference_stack[-1]
		if A==_H:return'resolve'
		return f"{A}.resolve"
	def derive_context(A,frame):return f"{A.get_context_ref()}.derived({A.dump_local_context(frame)})"
	def parameter_is_undeclared(A,target):
		if not A._param_def_block:return _B
		return target in A._param_def_block[-1]
	def push_assign_tracking(A):A._assign_stack.append(set())
	def pop_assign_tracking(A,frame):
		B=frame;vars=A._assign_stack.pop()
		if not B.block_frame and not B.loop_frame and not B.toplevel or not vars:return
		E=[A for A in vars if A[:1]!='_']
		if len(vars)==1:
			C=next(iter(vars));D=B.symbols.ref(C)
			if B.loop_frame:A.writeline(f"_loop_vars[{C!r}] = {D}");return
			if B.block_frame:A.writeline(f"_block_vars[{C!r}] = {D}");return
			A.writeline(f"context.vars[{C!r}] = {D}")
		else:
			if B.loop_frame:A.writeline('_loop_vars.update({')
			elif B.block_frame:A.writeline('_block_vars.update({')
			else:A.writeline('context.vars.update({')
			for (F,C) in enumerate(vars):
				if F:A.write(_E)
				D=B.symbols.ref(C);A.write(f"{C!r}: {D}")
			A.write('})')
		if not B.block_frame and not B.loop_frame and E:
			if len(E)==1:A.writeline(f"context.exported_vars.add({E[0]!r})")
			else:G=_E.join(map(repr,E));A.writeline(f"context.exported_vars.update(({G}))")
	def visit_Template(A,node,frame=_A):
		K='super';F='self';E=node;C=frame;assert C is _A,'no root frame allowed';L=EvalContext(A.environment,A.name);from .runtime import exported as M,async_exported as S
		if A.environment.is_async:N=sorted(M+S)
		else:N=sorted(M)
		A.writeline('from __future__ import generator_stop');A.writeline('from dynaconf.vendor.jinja2.runtime import '+_E.join(N));O=''if A.defer_init else', environment=environment';J=E.find(nodes.Extends)is not _A
		for B in E.find_all(nodes.Block):
			if B.name in A.blocks:A.fail(f"block {B.name!r} defined twice",B.lineno)
			A.blocks[B.name]=B
		for P in E.find_all(nodes.ImportedName):
			if P.importname not in A.import_aliases:
				H=P.importname;A.import_aliases[H]=Q=A.temporary_identifier()
				if'.'in H:T,U=H.rsplit('.',1);A.writeline(f"from {T} import {U} as {Q}")
				else:A.writeline(f"import {H} as {Q}")
		A.writeline(f"name = {A.name!r}");A.writeline(f"{A.func('root')}(context, missing=missing{O}):",extra=1);A.indent();A.write_commons();C=Frame(L)
		if F in find_undeclared(E.body,(F,)):G=C.symbols.declare_parameter(F);A.writeline(f"{G} = TemplateReference(context)")
		C.symbols.analyze_node(E);C.toplevel=C.rootlevel=_C;C.require_output_check=J and not A.has_known_extends
		if J:A.writeline('parent_template = None')
		A.enter_frame(C);A.pull_dependencies(E.body);A.blockvisit(E.body,C);A.leave_frame(C,with_python_scope=_C);A.outdent()
		if J:
			if not A.has_known_extends:A.indent();A.writeline(_N)
			A.indent()
			if not A.environment.is_async:A.writeline('yield from parent_template.root_render_func(context)')
			else:A.writeline('async for event in parent_template.root_render_func(context):');A.indent();A.writeline('yield event');A.outdent()
			A.outdent(1+(not A.has_known_extends))
		for (I,B) in A.blocks.items():
			A.writeline(f"{A.func('block_'+I)}(context, missing=missing{O}):",B,1);A.indent();A.write_commons();D=Frame(L);D.block_frame=_C;R=find_undeclared(B.body,(F,K))
			if F in R:G=D.symbols.declare_parameter(F);A.writeline(f"{G} = TemplateReference(context)")
			if K in R:G=D.symbols.declare_parameter(K);A.writeline(f"{G} = context.super({I!r}, block_{I})")
			D.symbols.analyze_node(B);D.block=I;A.writeline('_block_vars = {}');A.enter_frame(D);A.pull_dependencies(B.body);A.blockvisit(B.body,D);A.leave_frame(D,with_python_scope=_C);A.outdent()
		V=_E.join((f"{B!r}: block_{B}"for B in A.blocks));A.writeline(f"blocks = {{{V}}}",extra=1);W='&'.join((f"{B}={C}"for(B,C)in A.debug_info));A.writeline(f"debug_info = {W!r}")
	def visit_Block(A,node,frame):
		C=frame;B=node;E=0
		if C.toplevel:
			if A.has_known_extends:return
			if A.extends_so_far>0:A.writeline(_O);A.indent();E+=1
		if B.scoped:D=A.derive_context(C)
		else:D=A.get_context_ref()
		if B.required:A.writeline(f"if len(context.blocks[{B.name!r}]) <= 1:",B);A.indent();A.writeline(f'raise TemplateRuntimeError("Required block {B.name!r} not found")',B);A.outdent()
		if not A.environment.is_async and C.buffer is _A:A.writeline(f"yield from context.blocks[{B.name!r}][0]({D})",B)
		else:A.writeline(f"{A.choose_async()}for event in context.blocks[{B.name!r}][0]({D}):",B);A.indent();A.simple_write('event',C);A.outdent()
		A.outdent(E)
	def visit_Extends(A,node,frame):
		C=frame;B=node
		if not C.toplevel:A.fail('cannot use extend from a non top-level scope',B.lineno)
		if A.extends_so_far>0:
			if not A.has_known_extends:A.writeline(_N);A.indent()
			A.writeline('raise TemplateRuntimeError("extended multiple times")')
			if A.has_known_extends:raise CompilerExit()
			else:A.outdent()
		A.writeline('parent_template = environment.get_template(',B);A.visit(B.template,C);A.write(f", {A.name!r})");A.writeline('for name, parent_block in parent_template.blocks.items():');A.indent();A.writeline('context.blocks.setdefault(name, []).append(parent_block)');A.outdent()
		if C.rootlevel:A.has_known_extends=_C
		A.extends_so_far+=1
	def visit_Include(A,node,frame):
		F='select_template';D=frame;B=node
		if B.ignore_missing:A.writeline('try:');A.indent()
		C='get_or_select_template'
		if isinstance(B.template,nodes.Const):
			if isinstance(B.template.value,str):C='get_template'
			elif isinstance(B.template.value,(tuple,list)):C=F
		elif isinstance(B.template,(nodes.Tuple,nodes.List)):C=F
		A.writeline(f"template = environment.{C}(",B);A.visit(B.template,D);A.write(f", {A.name!r})")
		if B.ignore_missing:A.outdent();A.writeline('except TemplateNotFound:');A.indent();A.writeline('pass');A.outdent();A.writeline(_L);A.indent()
		E=_B
		if B.with_context:A.writeline(f"{A.choose_async()}for event in template.root_render_func(template.new_context(context.get_all(), True, {A.dump_local_context(D)})):")
		elif A.environment.is_async:A.writeline('for event in (await template._get_default_module_async())._body_stream:')
		else:A.writeline('yield from template._get_default_module()._body_stream');E=_C
		if not E:A.indent();A.simple_write('event',D);A.outdent()
		if B.ignore_missing:A.outdent()
	def _import_common(A,node,frame):
		C='_async';B=frame;A.write(f"{A.choose_async(_P)}environment.get_template(");A.visit(node.template,B);A.write(f", {A.name!r}).")
		if node.with_context:D=f"make_module{A.choose_async(C)}";A.write(f"{D}(context.get_all(), True, {A.dump_local_context(B)})")
		else:A.write(f"_get_default_module{A.choose_async(C)}(context)")
	def visit_Import(B,node,frame):
		C=frame;A=node;B.writeline(f"{C.symbols.ref(A.target)} = ",A)
		if C.toplevel:B.write(f"context.vars[{A.target!r}] = ")
		B._import_common(A,C)
		if C.toplevel and not A.target.startswith('_'):B.writeline(f"context.exported_vars.discard({A.target!r})")
	def visit_FromImport(A,node,frame):
		G=node;C=frame;A.newline(G);A.write('included_template = ');A._import_common(G,C);E=[];F=[]
		for B in G.names:
			if isinstance(B,tuple):B,D=B
			else:D=B
			A.writeline(f"{C.symbols.ref(D)} = getattr(included_template, {B!r}, missing)");A.writeline(f"if {C.symbols.ref(D)} is missing:");A.indent();H=f"the template {{included_template.__name__!r}} (imported on {A.position(G)}) does not export the requested name {B!r}";A.writeline(f"{C.symbols.ref(D)} = undefined(f{H!r}, name={B!r})");A.outdent()
			if C.toplevel:
				E.append(D)
				if not D.startswith('_'):F.append(D)
		if E:
			if len(E)==1:B=E[0];A.writeline(f"context.vars[{B!r}] = {C.symbols.ref(B)}")
			else:I=_E.join((f"{A!r}: {C.symbols.ref(A)}"for A in E));A.writeline(f"context.vars.update({{{I}}})")
		if F:
			if len(F)==1:A.writeline(f"context.exported_vars.discard({F[0]!r})")
			else:J=_E.join(map(repr,F));A.writeline(f"context.exported_vars.difference_update(({J}))")
	def visit_For(A,node,frame):
		Q='auto_aiter(';P=' in ';O='for ';N='async for ';M='body';G='loop';D=frame;B=node;C=D.inner();C.loop_frame=_C;H=D.inner();F=D.inner();E=B.recursive or G in find_undeclared(B.iter_child_nodes(only=(M,)),(G,))or any((A.scoped for A in B.find_all(nodes.Block)));I=_A
		if E:I=C.symbols.declare_parameter(G)
		C.symbols.analyze_node(B,for_branch=M)
		if B.else_:F.symbols.analyze_node(B,for_branch='else')
		if B.test:L=A.temporary_identifier();H.symbols.analyze_node(B,for_branch='test');A.writeline(f"{A.func(L)}(fiter):",B.test);A.indent();A.enter_frame(H);A.writeline(A.choose_async(N,O));A.visit(B.target,C);A.write(P);A.write(A.choose_async('auto_aiter(fiter)','fiter'));A.write(_F);A.indent();A.writeline('if ',B.test);A.visit(B.test,H);A.write(_F);A.indent();A.writeline(_I);A.visit(B.target,C);A.outdent(3);A.leave_frame(H,with_python_scope=_C)
		if B.recursive:A.writeline(f"{A.func(G)}(reciter, loop_render_func, depth=0):",B);A.indent();A.buffer(C);F.buffer=C.buffer
		if E:A.writeline(f"{I} = missing")
		for J in B.find_all(nodes.Name):
			if J.ctx=='store'and J.name==G:A.fail("Can't assign to special loop variable in for-loop target",J.lineno)
		if B.else_:K=A.temporary_identifier();A.writeline(f"{K} = 1")
		A.writeline(A.choose_async(N,O),B);A.visit(B.target,C)
		if E:A.write(f", {I} in {A.choose_async('Async')}LoopContext(")
		else:A.write(P)
		if B.test:A.write(f"{L}(")
		if B.recursive:A.write('reciter')
		else:
			if A.environment.is_async and not E:A.write(Q)
			A.visit(B.iter,D)
			if A.environment.is_async and not E:A.write(_D)
		if B.test:A.write(_D)
		if B.recursive:A.write(', undefined, loop_render_func, depth):')
		else:A.write(', undefined):'if E else _F)
		A.indent();A.enter_frame(C);A.writeline('_loop_vars = {}');A.blockvisit(B.body,C)
		if B.else_:A.writeline(f"{K} = 0")
		A.outdent();A.leave_frame(C,with_python_scope=B.recursive and not B.else_)
		if B.else_:A.writeline(f"if {K}:");A.indent();A.enter_frame(F);A.blockvisit(B.else_,F);A.leave_frame(F);A.outdent()
		if B.recursive:
			A.return_buffer_contents(C);A.outdent();A.start_write(D,B);A.write(f"{A.choose_async(_P)}loop(")
			if A.environment.is_async:A.write(Q)
			A.visit(B.iter,D)
			if A.environment.is_async:A.write(_D)
			A.write(', loop)');A.end_write(D)
		if A._assign_stack:A._assign_stack[-1].difference_update(C.symbols.stores)
	def visit_If(A,node,frame):
		B=node;C=frame.soft();A.writeline('if ',B);A.visit(B.test,C);A.write(_F);A.indent();A.blockvisit(B.body,C);A.outdent()
		for D in B.elif_:A.writeline('elif ',D);A.visit(D.test,C);A.write(_F);A.indent();A.blockvisit(D.body,C);A.outdent()
		if B.else_:A.writeline(_L);A.indent();A.blockvisit(B.else_,C);A.outdent()
	def visit_Macro(A,node,frame):
		C=frame;B=node;D,E=A.macro_body(B,C);A.newline()
		if C.toplevel:
			if not B.name.startswith('_'):A.write(f"context.exported_vars.add({B.name!r})")
			A.writeline(f"context.vars[{B.name!r}] = ")
		A.write(f"{C.symbols.ref(B.name)} = ");A.macro_def(E,D)
	def visit_CallBlock(A,node,frame):C=node;B=frame;D,E=A.macro_body(C,B);A.writeline('caller = ');A.macro_def(E,D);A.start_write(B,C);A.visit_Call(C.call,B,forward_caller=_C);A.end_write(B)
	def visit_FilterBlock(A,node,frame):D=frame;C=node;B=D.inner();B.symbols.analyze_node(C);A.enter_frame(B);A.buffer(B);A.blockvisit(C.body,B);A.start_write(D,C);A.visit_Filter(C.filter,B);A.end_write(D);A.leave_frame(B)
	def visit_With(A,node,frame):
		D=frame;C=node;B=D.inner();B.symbols.analyze_node(C);A.enter_frame(B)
		for (E,F) in zip(C.targets,C.values):A.newline();A.visit(E,B);A.write(_J);A.visit(F,D)
		A.blockvisit(C.body,B);A.leave_frame(B)
	def visit_ExprStmt(A,node,frame):A.newline(node);A.visit(node.node,frame)
	class _FinalizeInfo(t.NamedTuple):const:t.Optional[t.Callable[...,str]];src:t.Optional[str]
	@staticmethod
	def _default_finalize(value):return str(value)
	_finalize=_A
	def _make_finalize(A):
		if A._finalize is not _A:return A._finalize
		B:0;B=F=A._default_finalize;C=_A
		if A.environment.finalize:
			C='environment.finalize(';D=A.environment.finalize;E={_PassArg.context:_H,_PassArg.eval_context:_Q,_PassArg.environment:_M}.get(_PassArg.from_obj(D));B=_A
			if E is _A:
				def B(value):return F(D(value))
			else:
				C=f"{C}{E}, "
				if E==_M:
					def B(value):return F(D(A.environment,value))
		A._finalize=A._FinalizeInfo(B,C);return A._finalize
	def _output_const_repr(A,group):return repr(concat(group))
	def _output_child_to_const(C,node,frame,finalize):
		B=frame;A=node.as_const(B.eval_ctx)
		if B.eval_ctx.autoescape:A=escape(A)
		if isinstance(node,nodes.TemplateData):return str(A)
		return finalize.const(A)
	def _output_child_pre(A,node,frame,finalize):
		C=finalize;B=frame
		if B.eval_ctx.volatile:A.write('(escape if context.eval_ctx.autoescape else str)(')
		elif B.eval_ctx.autoescape:A.write('escape(')
		else:A.write('str(')
		if C.src is not _A:A.write(C.src)
	def _output_child_post(A,node,frame,finalize):
		A.write(_D)
		if finalize.src is not _A:A.write(_D)
	def visit_Output(A,node,frame):
		B=frame
		if B.require_output_check:
			if A.has_known_extends:return
			A.writeline(_O);A.indent()
		E=A._make_finalize();C=[]
		for F in node.nodes:
			try:
				if not(E.const or isinstance(F,nodes.TemplateData)):raise nodes.Impossible()
				G=A._output_child_to_const(F,B,E)
			except (nodes.Impossible,Exception):C.append(F);continue
			if C and isinstance(C[-1],list):C[-1].append(G)
			else:C.append([G])
		if B.buffer is not _A:
			if len(C)==1:A.writeline(f"{B.buffer}.append(")
			else:A.writeline(f"{B.buffer}.extend((")
			A.indent()
		for D in C:
			if isinstance(D,list):
				H=A._output_const_repr(D)
				if B.buffer is _A:A.writeline(_I+H)
				else:A.writeline(H+',')
			else:
				if B.buffer is _A:A.writeline(_I,D)
				else:A.newline(D)
				A._output_child_pre(D,B,E);A.visit(D,B);A._output_child_post(D,B,E)
				if B.buffer is not _A:A.write(',')
		if B.buffer is not _A:A.outdent();A.writeline(_D if len(C)==1 else _K)
		if B.require_output_check:A.outdent()
	def visit_Assign(A,node,frame):C=frame;B=node;A.push_assign_tracking();A.newline(B);A.visit(B.target,C);A.write(_J);A.visit(B.node,C);A.pop_assign_tracking(C)
	def visit_AssignBlock(A,node,frame):
		D=frame;C=node;A.push_assign_tracking();B=D.inner();B.require_output_check=_B;B.symbols.analyze_node(C);A.enter_frame(B);A.buffer(B);A.blockvisit(C.body,B);A.newline(C);A.visit(C.target,D);A.write(' = (Markup if context.eval_ctx.autoescape else identity)(')
		if C.filter is not _A:A.visit_Filter(C.filter,B)
		else:A.write(f"concat({B.buffer})")
		A.write(_D);A.pop_assign_tracking(D);A.leave_frame(B)
	def visit_Name(A,node,frame):
		C=frame;B=node
		if B.ctx=='store'and(C.toplevel or C.loop_frame or C.block_frame):
			if A._assign_stack:A._assign_stack[-1].add(B.name)
		D=C.symbols.ref(B.name)
		if B.ctx=='load':
			E=C.symbols.find_load(D)
			if not(E is not _A and E[0]==VAR_LOAD_PARAMETER and not A.parameter_is_undeclared(D)):A.write(f"(undefined(name={B.name!r}) if {D} is missing else {D})");return
		A.write(D)
	def visit_NSRef(A,node,frame):B=frame.symbols.ref(node.name);A.writeline(f"if not isinstance({B}, Namespace):");A.indent();A.writeline('raise TemplateRuntimeError("cannot assign attribute on non-namespace object")');A.outdent();A.writeline(f"{B}[{node.attr!r}]")
	def visit_Const(B,node,frame):
		A=node.as_const(frame.eval_ctx)
		if isinstance(A,float):B.write(str(A))
		else:B.write(repr(A))
	def visit_TemplateData(A,node,frame):
		try:A.write(repr(node.as_const(frame.eval_ctx)))
		except nodes.Impossible:A.write(f"(Markup if context.eval_ctx.autoescape else identity)({node.data!r})")
	def visit_Tuple(A,node,frame):
		A.write('(');B=-1
		for (B,C) in enumerate(node.items):
			if B:A.write(_E)
			A.visit(C,frame)
		A.write(',)'if B==0 else _D)
	def visit_List(A,node,frame):
		A.write('[')
		for (B,C) in enumerate(node.items):
			if B:A.write(_E)
			A.visit(C,frame)
		A.write(']')
	def visit_Dict(A,node,frame):
		B=frame;A.write('{')
		for (D,C) in enumerate(node.items):
			if D:A.write(_E)
			A.visit(C.key,B);A.write(': ');A.visit(C.value,B)
		A.write('}')
	visit_Add=_make_binop('+');visit_Sub=_make_binop('-');visit_Mul=_make_binop('*');visit_Div=_make_binop('/');visit_FloorDiv=_make_binop('//');visit_Pow=_make_binop('**');visit_Mod=_make_binop('%');visit_And=_make_binop('and');visit_Or=_make_binop('or');visit_Pos=_make_unop('+');visit_Neg=_make_unop('-');visit_Not=_make_unop('not ')
	@optimizeconst
	def visit_Concat(self,node,frame):
		B=frame;A=self
		if B.eval_ctx.volatile:C='(markup_join if context.eval_ctx.volatile else str_join)'
		elif B.eval_ctx.autoescape:C='markup_join'
		else:C='str_join'
		A.write(f"{C}((")
		for D in node.nodes:A.visit(D,B);A.write(_E)
		A.write(_K)
	@optimizeconst
	def visit_Compare(self,node,frame):
		B=frame;A=self;A.write('(');A.visit(node.expr,B)
		for C in node.ops:A.visit(C,B)
		A.write(_D)
	def visit_Operand(A,node,frame):A.write(f" {operators[node.op]} ");A.visit(node.expr,frame)
	@optimizeconst
	def visit_Getattr(self,node,frame):
		A=self
		if A.environment.is_async:A.write(_R)
		A.write('environment.getattr(');A.visit(node.node,frame);A.write(f", {node.attr!r})")
		if A.environment.is_async:A.write(_K)
	@optimizeconst
	def visit_Getitem(self,node,frame):
		C=frame;B=node;A=self
		if isinstance(B.arg,nodes.Slice):A.visit(B.node,C);A.write('[');A.visit(B.arg,C);A.write(']')
		else:
			if A.environment.is_async:A.write(_R)
			A.write('environment.getitem(');A.visit(B.node,C);A.write(_E);A.visit(B.arg,C);A.write(_D)
			if A.environment.is_async:A.write(_K)
	def visit_Slice(B,node,frame):
		C=frame;A=node
		if A.start is not _A:B.visit(A.start,C)
		B.write(_F)
		if A.stop is not _A:B.visit(A.stop,C)
		if A.step is not _A:B.write(_F);B.visit(A.step,C)
	@contextmanager
	def _filter_test_common(self,node,frame,is_filter):
		E=is_filter;D=frame;B=node;A=self
		if A.environment.is_async:A.write(_S)
		if E:A.write(f"{A.filters[B.name]}(");C=A.environment.filters.get(B.name)
		else:A.write(f"{A.tests[B.name]}(");C=A.environment.tests.get(B.name)
		if C is _A and not D.soft_frame:G='filter'if E else'test';A.fail(f"No {G} named {B.name!r}.",B.lineno)
		F={_PassArg.context:_H,_PassArg.eval_context:_Q,_PassArg.environment:_M}.get(_PassArg.from_obj(C))
		if F is not _A:A.write(f"{F}, ")
		yield;A.signature(B,D);A.write(_D)
		if A.environment.is_async:A.write(_D)
	@optimizeconst
	def visit_Filter(self,node,frame):
		C=node;B=self;A=frame
		with B._filter_test_common(C,A,_C):
			if C.node is not _A:B.visit(C.node,A)
			elif A.eval_ctx.volatile:B.write(f"(Markup(concat({A.buffer})) if context.eval_ctx.autoescape else concat({A.buffer}))")
			elif A.eval_ctx.autoescape:B.write(f"Markup(concat({A.buffer}))")
			else:B.write(f"concat({A.buffer})")
	@optimizeconst
	def visit_Test(self,node,frame):
		A=frame
		with self._filter_test_common(node,A,_B):self.visit(node.node,A)
	@optimizeconst
	def visit_CondExpr(self,node,frame):
		C=frame;B=node;A=self;C=C.soft()
		def D():
			if B.expr2 is not _A:A.visit(B.expr2,C);return
			A.write(f'cond_expr_undefined("the inline if-expression on {A.position(B)} evaluated to false and no else section was defined.")')
		A.write('(');A.visit(B.expr1,C);A.write(' if ');A.visit(B.test,C);A.write(' else ');D();A.write(_D)
	@optimizeconst
	def visit_Call(self,node,frame,forward_caller=_B):
		G='_block_vars';F='_loop_vars';B=frame;A=self
		if A.environment.is_async:A.write(_S)
		if A.environment.sandboxed:A.write('environment.call(context, ')
		else:A.write('context.call(')
		A.visit(node.node,B);C={_G:_G}if forward_caller else _A;D={F:F}if B.loop_frame else{};E={G:G}if B.block_frame else{}
		if C:C.update(D,**E)
		elif D or E:C=dict(D,**E)
		A.signature(node,B,C);A.write(_D)
		if A.environment.is_async:A.write(_D)
	def visit_Keyword(A,node,frame):A.write(node.key+'=');A.visit(node.value,frame)
	def visit_MarkSafe(A,node,frame):A.write('Markup(');A.visit(node.expr,frame);A.write(_D)
	def visit_MarkSafeIfAutoescape(A,node,frame):A.write('(Markup if context.eval_ctx.autoescape else identity)(');A.visit(node.expr,frame);A.write(_D)
	def visit_EnvironmentAttribute(A,node,frame):A.write('environment.'+node.name)
	def visit_ExtensionAttribute(A,node,frame):A.write(f"environment.extensions[{node.identifier!r}].{node.name}")
	def visit_ImportedName(A,node,frame):A.write(A.import_aliases[node.importname])
	def visit_InternalName(A,node,frame):A.write(node.name)
	def visit_ContextReference(A,node,frame):A.write(_H)
	def visit_DerivedContextReference(A,node,frame):A.write(A.derive_context(frame))
	def visit_Continue(A,node,frame):A.writeline('continue',node)
	def visit_Break(A,node,frame):A.writeline('break',node)
	def visit_Scope(B,node,frame):A=frame.inner();A.symbols.analyze_node(node);B.enter_frame(A);B.blockvisit(node.body,A);B.leave_frame(A)
	def visit_OverlayScope(A,node,frame):D=frame;C=node;E=A.temporary_identifier();A.writeline(f"{E} = {A.derive_context(D)}");A.writeline(f"{E}.vars = ");A.visit(C.context,D);A.push_context_reference(E);B=D.inner(isolated=_C);B.symbols.analyze_node(C);A.enter_frame(B);A.blockvisit(C.body,B);A.leave_frame(B);A.pop_context_reference()
	def visit_EvalContextModifier(C,node,frame):
		A=frame
		for B in node.options:
			C.writeline(f"context.eval_ctx.{B.key} = ");C.visit(B.value,A)
			try:D=B.value.as_const(A.eval_ctx)
			except nodes.Impossible:A.eval_ctx.volatile=_C
			else:setattr(A.eval_ctx,B.key,D)
	def visit_ScopedEvalContextModifier(A,node,frame):
		B=frame;C=A.temporary_identifier();D=B.eval_ctx.save();A.writeline(f"{C} = context.eval_ctx.save()");A.visit_EvalContextModifier(node,B)
		for E in node.body:A.visit(E,B)
		B.eval_ctx.revert(D);A.writeline(f"context.eval_ctx.revert({C})")