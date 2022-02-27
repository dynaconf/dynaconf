_B='tb_next'
_A=None
import platform,sys,typing as t
from types import CodeType,TracebackType
from .exceptions import TemplateSyntaxError
from .utils import internal_code
from .utils import missing
if t.TYPE_CHECKING:from .runtime import Context
def rewrite_traceback_stack(source=_A):
	_,exc_value,tb=sys.exc_info();exc_value=t.cast(BaseException,exc_value);tb=t.cast(TracebackType,tb)
	if isinstance(exc_value,TemplateSyntaxError)and not exc_value.translated:exc_value.translated=True;exc_value.source=source;exc_value.with_traceback(_A);tb=fake_traceback(exc_value,_A,exc_value.filename or'<unknown>',exc_value.lineno)
	else:tb=tb.tb_next
	stack=[]
	while tb is not _A:
		if tb.tb_frame.f_code in internal_code:tb=tb.tb_next;continue
		template=tb.tb_frame.f_globals.get('__jinja_template__')
		if template is not _A:lineno=template.get_corresponding_lineno(tb.tb_lineno);fake_tb=fake_traceback(exc_value,tb,template.filename,lineno);stack.append(fake_tb)
		else:stack.append(tb)
		tb=tb.tb_next
	tb_next=_A
	for tb in reversed(stack):tb_next=tb_set_next(tb,tb_next)
	return exc_value.with_traceback(tb_next)
def fake_traceback(exc_value,tb,filename,lineno):
	A='__jinja_exception__'
	if tb is not _A:locals=get_template_locals(tb.tb_frame.f_locals);locals.pop(A,_A)
	else:locals={}
	globals={'__name__':filename,'__file__':filename,A:exc_value};code=compile('\n'*(lineno-1)+'raise __jinja_exception__',filename,'exec')
	try:
		location='template'
		if tb is not _A:
			function=tb.tb_frame.f_code.co_name
			if function=='root':location='top-level template code'
			elif function.startswith('block_'):location=f"block {function[6:]!r}"
		code_args=[]
		for attr in ('argcount','posonlyargcount','kwonlyargcount','nlocals','stacksize','flags','code','consts','names','varnames',('filename',filename),('name',location),'firstlineno','lnotab','freevars','cellvars','linetable'):
			if isinstance(attr,tuple):code_args.append(attr[1]);continue
			try:code_args.append(getattr(code,'co_'+t.cast(str,attr)))
			except AttributeError:continue
		code=CodeType(*(code_args))
	except Exception:pass
	try:exec(code,globals,locals)
	except BaseException:return sys.exc_info()[2].tb_next
def get_template_locals(real_locals):
	ctx=real_locals.get('context')
	if ctx is not _A:data=ctx.get_all().copy()
	else:data={}
	local_overrides={}
	for (name,value) in real_locals.items():
		if not name.startswith('l_')or value is missing:continue
		try:_,depth_str,name=name.split('_',2);depth=int(depth_str)
		except ValueError:continue
		cur_depth=local_overrides.get(name,(-1,))[0]
		if cur_depth<depth:local_overrides[name]=depth,value
	for (name,(_,value)) in local_overrides.items():
		if value is missing:data.pop(name,_A)
		else:data[name]=value
	return data
if sys.version_info>=(3,7):
	def tb_set_next(tb,tb_next):tb.tb_next=tb_next;return tb
elif platform.python_implementation()=='PyPy':
	try:import tputil
	except ImportError:
		def tb_set_next(tb,tb_next):return tb
	else:
		def tb_set_next(tb,tb_next):
			def controller(op):
				if op.opname=='__getattribute__'and op.args[0]==_B:return tb_next
				return op.delegate()
			return tputil.make_proxy(controller,obj=tb)
else:
	import ctypes
	class _CTraceback(ctypes.Structure):_fields_=[('PyObject_HEAD',ctypes.c_byte*object().__sizeof__()),(_B,ctypes.py_object)]
	def tb_set_next(tb,tb_next):
		c_tb=_CTraceback.from_address(id(tb))
		if tb.tb_next is not _A:c_tb_next=ctypes.py_object(tb.tb_next);c_tb.tb_next=ctypes.py_object();ctypes.pythonapi.Py_DecRef(c_tb_next)
		if tb_next is not _A:c_tb_next=ctypes.py_object(tb_next);ctypes.pythonapi.Py_IncRef(c_tb_next);c_tb.tb_next=c_tb_next
		return tb