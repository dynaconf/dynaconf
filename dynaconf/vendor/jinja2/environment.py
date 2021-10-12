_H='The environment was not created with async mode enabled.'
_G='__file__'
_F='environment'
_E='No loader configured.'
_D='result'
_C=True
_B=False
_A=None
import os,sys,typing,typing as t,weakref
from collections import ChainMap
from functools import lru_cache
from functools import partial
from functools import reduce
from types import CodeType
from markupsafe import Markup
from .  import nodes
from .compiler import CodeGenerator
from .compiler import generate
from .defaults import BLOCK_END_STRING
from .defaults import BLOCK_START_STRING
from .defaults import COMMENT_END_STRING
from .defaults import COMMENT_START_STRING
from .defaults import DEFAULT_FILTERS
from .defaults import DEFAULT_NAMESPACE
from .defaults import DEFAULT_POLICIES
from .defaults import DEFAULT_TESTS
from .defaults import KEEP_TRAILING_NEWLINE
from .defaults import LINE_COMMENT_PREFIX
from .defaults import LINE_STATEMENT_PREFIX
from .defaults import LSTRIP_BLOCKS
from .defaults import NEWLINE_SEQUENCE
from .defaults import TRIM_BLOCKS
from .defaults import VARIABLE_END_STRING
from .defaults import VARIABLE_START_STRING
from .exceptions import TemplateNotFound
from .exceptions import TemplateRuntimeError
from .exceptions import TemplatesNotFound
from .exceptions import TemplateSyntaxError
from .exceptions import UndefinedError
from .lexer import get_lexer
from .lexer import Lexer
from .lexer import TokenStream
from .nodes import EvalContext
from .parser import Parser
from .runtime import Context
from .runtime import new_context
from .runtime import Undefined
from .utils import _PassArg
from .utils import concat
from .utils import consume
from .utils import import_string
from .utils import internalcode
from .utils import LRUCache
from .utils import missing
if t.TYPE_CHECKING:import typing_extensions as te;from .bccache import BytecodeCache;from .ext import Extension;from .loaders import BaseLoader
_env_bound=t.TypeVar('_env_bound',bound='Environment')
@lru_cache(maxsize=10)
def get_spontaneous_environment(cls,*args):env=cls(*(args));env.shared=_C;return env
def create_cache(size):
	if size==0:return _A
	if size<0:return{}
	return LRUCache(size)
def copy_cache(cache):
	if cache is _A:return _A
	if type(cache)is dict:return{}
	return LRUCache(cache.capacity)
def load_extensions(environment,extensions):
	result={}
	for extension in extensions:
		if isinstance(extension,str):extension=t.cast(t.Type['Extension'],import_string(extension))
		result[extension.identifier]=extension(environment)
	return result
def _environment_config_check(environment):assert issubclass(environment.undefined,Undefined),"'undefined' must be a subclass of 'jinja2.Undefined'.";assert environment.block_start_string!=environment.variable_start_string!=environment.comment_start_string,'block, variable and comment start strings must be different.';assert environment.newline_sequence in{'\r','\r\n','\n'},"'newline_sequence' must be one of '\\n', '\\r\\n', or '\\r'.";return environment
class Environment:
	sandboxed=_B;overlayed=_B;linked_to=_A;shared=_B;code_generator_class=CodeGenerator;context_class=Context;template_class:0
	def __init__(self,block_start_string=BLOCK_START_STRING,block_end_string=BLOCK_END_STRING,variable_start_string=VARIABLE_START_STRING,variable_end_string=VARIABLE_END_STRING,comment_start_string=COMMENT_START_STRING,comment_end_string=COMMENT_END_STRING,line_statement_prefix=LINE_STATEMENT_PREFIX,line_comment_prefix=LINE_COMMENT_PREFIX,trim_blocks=TRIM_BLOCKS,lstrip_blocks=LSTRIP_BLOCKS,newline_sequence=NEWLINE_SEQUENCE,keep_trailing_newline=KEEP_TRAILING_NEWLINE,extensions=(),optimized=_C,undefined=Undefined,finalize=_A,autoescape=_B,loader=_A,cache_size=400,auto_reload=_C,bytecode_cache=_A,enable_async=_B):self.block_start_string=block_start_string;self.block_end_string=block_end_string;self.variable_start_string=variable_start_string;self.variable_end_string=variable_end_string;self.comment_start_string=comment_start_string;self.comment_end_string=comment_end_string;self.line_statement_prefix=line_statement_prefix;self.line_comment_prefix=line_comment_prefix;self.trim_blocks=trim_blocks;self.lstrip_blocks=lstrip_blocks;self.newline_sequence=newline_sequence;self.keep_trailing_newline=keep_trailing_newline;self.undefined=undefined;self.optimized=optimized;self.finalize=finalize;self.autoescape=autoescape;self.filters=DEFAULT_FILTERS.copy();self.tests=DEFAULT_TESTS.copy();self.globals=DEFAULT_NAMESPACE.copy();self.loader=loader;self.cache=create_cache(cache_size);self.bytecode_cache=bytecode_cache;self.auto_reload=auto_reload;self.policies=DEFAULT_POLICIES.copy();self.extensions=load_extensions(self,extensions);self.is_async=enable_async;_environment_config_check(self)
	def add_extension(self,extension):self.extensions.update(load_extensions(self,[extension]))
	def extend(self,**attributes):
		for (key,value) in attributes.items():
			if not hasattr(self,key):setattr(self,key,value)
	def overlay(self,block_start_string=missing,block_end_string=missing,variable_start_string=missing,variable_end_string=missing,comment_start_string=missing,comment_end_string=missing,line_statement_prefix=missing,line_comment_prefix=missing,trim_blocks=missing,lstrip_blocks=missing,extensions=missing,optimized=missing,undefined=missing,finalize=missing,autoescape=missing,loader=missing,cache_size=missing,auto_reload=missing,bytecode_cache=missing):
		args=dict(locals());del args['self'],args['cache_size'],args['extensions'];rv=object.__new__(self.__class__);rv.__dict__.update(self.__dict__);rv.overlayed=_C;rv.linked_to=self
		for (key,value) in args.items():
			if value is not missing:setattr(rv,key,value)
		if cache_size is not missing:rv.cache=create_cache(cache_size)
		else:rv.cache=copy_cache(self.cache)
		rv.extensions={}
		for (key,value) in self.extensions.items():rv.extensions[key]=value.bind(rv)
		if extensions is not missing:rv.extensions.update(load_extensions(rv,extensions))
		return _environment_config_check(rv)
	@property
	def lexer(self):return get_lexer(self)
	def iter_extensions(self):return iter(sorted(self.extensions.values(),key=lambda x:x.priority))
	def getitem(self,obj,argument):
		try:return obj[argument]
		except (AttributeError,TypeError,LookupError):
			if isinstance(argument,str):
				try:attr=str(argument)
				except Exception:pass
				else:
					try:return getattr(obj,attr)
					except AttributeError:pass
			return self.undefined(obj=obj,name=argument)
	def getattr(self,obj,attribute):
		try:return getattr(obj,attribute)
		except AttributeError:pass
		try:return obj[attribute]
		except (TypeError,LookupError,AttributeError):return self.undefined(obj=obj,name=attribute)
	def _filter_test_common(self,name,value,args,kwargs,context,eval_ctx,is_filter):
		if is_filter:env_map=self.filters;type_name='filter'
		else:env_map=self.tests;type_name='test'
		func=env_map.get(name)
		if func is _A:
			msg=f"No {type_name} named {name!r}."
			if isinstance(name,Undefined):
				try:name._fail_with_undefined_error()
				except Exception as e:msg=f"{msg} ({e}; did you forget to quote the callable name?)"
			raise TemplateRuntimeError(msg)
		args=[value,*(args if args is not _A else())];kwargs=kwargs if kwargs is not _A else{};pass_arg=_PassArg.from_obj(func)
		if pass_arg is _PassArg.context:
			if context is _A:raise TemplateRuntimeError(f"Attempted to invoke a context {type_name} without context.")
			args.insert(0,context)
		elif pass_arg is _PassArg.eval_context:
			if eval_ctx is _A:
				if context is not _A:eval_ctx=context.eval_ctx
				else:eval_ctx=EvalContext(self)
			args.insert(0,eval_ctx)
		elif pass_arg is _PassArg.environment:args.insert(0,self)
		return func(*(args),**kwargs)
	def call_filter(self,name,value,args=_A,kwargs=_A,context=_A,eval_ctx=_A):return self._filter_test_common(name,value,args,kwargs,context,eval_ctx,_C)
	def call_test(self,name,value,args=_A,kwargs=_A,context=_A,eval_ctx=_A):return self._filter_test_common(name,value,args,kwargs,context,eval_ctx,_B)
	@internalcode
	def parse(self,source,name=_A,filename=_A):
		try:return self._parse(source,name,filename)
		except TemplateSyntaxError:self.handle_exception(source=source)
	def _parse(self,source,name,filename):return Parser(self,source,name,filename).parse()
	def lex(self,source,name=_A,filename=_A):
		source=str(source)
		try:return self.lexer.tokeniter(source,name,filename)
		except TemplateSyntaxError:self.handle_exception(source=source)
	def preprocess(self,source,name=_A,filename=_A):return reduce(lambda s,e:e.preprocess(s,name,filename),self.iter_extensions(),str(source))
	def _tokenize(self,source,name,filename=_A,state=_A):
		source=self.preprocess(source,name,filename);stream=self.lexer.tokenize(source,name,filename,state)
		for ext in self.iter_extensions():
			stream=ext.filter_stream(stream)
			if not isinstance(stream,TokenStream):stream=TokenStream(stream,name,filename)
		return stream
	def _generate(self,source,name,filename,defer_init=_B):return generate(source,self,name,filename,defer_init=defer_init,optimized=self.optimized)
	def _compile(self,source,filename):return compile(source,filename,'exec')
	@typing.overload
	def compile(self,source,name=_A,filename=_A,raw=_B,defer_init=_B):...
	@typing.overload
	def compile(self,source,name=_A,filename=_A,raw=...,defer_init=_B):...
	@internalcode
	def compile(self,source,name=_A,filename=_A,raw=_B,defer_init=_B):
		source_hint=_A
		try:
			if isinstance(source,str):source_hint=source;source=self._parse(source,name,filename)
			source=self._generate(source,name,filename,defer_init=defer_init)
			if raw:return source
			if filename is _A:filename='<template>'
			return self._compile(source,filename)
		except TemplateSyntaxError:self.handle_exception(source=source_hint)
	def compile_expression(self,source,undefined_to_none=_C):
		parser=Parser(self,source,state='variable')
		try:
			expr=parser.parse_expression()
			if not parser.stream.eos:raise TemplateSyntaxError('chunk after expression',parser.stream.current.lineno,_A,_A)
			expr.set_environment(self)
		except TemplateSyntaxError:self.handle_exception(source=source)
		body=[nodes.Assign(nodes.Name(_D,'store'),expr,lineno=1)];template=self.from_string(nodes.Template(body,lineno=1));return TemplateExpression(template,undefined_to_none)
	def compile_templates(self,target,extensions=_A,filter_func=_A,zip='deflated',log_function=_A,ignore_errors=_C):
		from .loaders import ModuleLoader
		if log_function is _A:
			def log_function(x):0
		assert log_function is not _A;assert self.loader is not _A,_E
		def write_file(filename,data):
			if zip:info=ZipInfo(filename);info.external_attr=493<<16;zip_file.writestr(info,data)
			else:
				with open(os.path.join(target,filename),'wb')as f:f.write(data.encode('utf8'))
		if zip is not _A:from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED,ZIP_STORED;zip_file=ZipFile(target,'w',dict(deflated=ZIP_DEFLATED,stored=ZIP_STORED)[zip]);log_function(f"Compiling into Zip archive {target!r}")
		else:
			if not os.path.isdir(target):os.makedirs(target)
			log_function(f"Compiling into folder {target!r}")
		try:
			for name in self.list_templates(extensions,filter_func):
				source,filename,_=self.loader.get_source(self,name)
				try:code=self.compile(source,name,filename,_C,_C)
				except TemplateSyntaxError as e:
					if not ignore_errors:raise
					log_function(f'Could not compile "{name}": {e}');continue
				filename=ModuleLoader.get_module_filename(name);write_file(filename,code);log_function(f'Compiled "{name}" as {filename}')
		finally:
			if zip:zip_file.close()
		log_function('Finished compiling templates')
	def list_templates(self,extensions=_A,filter_func=_A):
		assert self.loader is not _A,_E;names=self.loader.list_templates()
		if extensions is not _A:
			if filter_func is not _A:raise TypeError('either extensions or filter_func can be passed, but not both')
			def filter_func(x):return'.'in x and x.rsplit('.',1)[1]in extensions
		if filter_func is not _A:names=[name for name in names if filter_func(name)]
		return names
	def handle_exception(self,source=_A):from .debug import rewrite_traceback_stack;raise rewrite_traceback_stack(source=source)
	def join_path(self,template,parent):return template
	@internalcode
	def _load_template(self,name,globals):
		if self.loader is _A:raise TypeError('no loader for this environment specified')
		cache_key=weakref.ref(self.loader),name
		if self.cache is not _A:
			template=self.cache.get(cache_key)
			if template is not _A and(not self.auto_reload or template.is_up_to_date):
				if globals:template.globals.update(globals)
				return template
		template=self.loader.load(self,name,self.make_globals(globals))
		if self.cache is not _A:self.cache[cache_key]=template
		return template
	@internalcode
	def get_template(self,name,parent=_A,globals=_A):
		if isinstance(name,Template):return name
		if parent is not _A:name=self.join_path(name,parent)
		return self._load_template(name,globals)
	@internalcode
	def select_template(self,names,parent=_A,globals=_A):
		if isinstance(names,Undefined):names._fail_with_undefined_error()
		if not names:raise TemplatesNotFound(message='Tried to select from an empty list of templates.')
		for name in names:
			if isinstance(name,Template):return name
			if parent is not _A:name=self.join_path(name,parent)
			try:return self._load_template(name,globals)
			except (TemplateNotFound,UndefinedError):pass
		raise TemplatesNotFound(names)
	@internalcode
	def get_or_select_template(self,template_name_or_list,parent=_A,globals=_A):
		if isinstance(template_name_or_list,(str,Undefined)):return self.get_template(template_name_or_list,parent,globals)
		elif isinstance(template_name_or_list,Template):return template_name_or_list
		return self.select_template(template_name_or_list,parent,globals)
	def from_string(self,source,globals=_A,template_class=_A):gs=self.make_globals(globals);cls=template_class or self.template_class;return cls.from_code(self,self.compile(source),gs,_A)
	def make_globals(self,d):
		if d is _A:d={}
		return ChainMap(d,self.globals)
class Template:
	environment_class=Environment;environment:0;globals:0;name:0;filename:0;blocks:0;root_render_func:0;_module:0;_debug_info:0;_uptodate:0
	def __new__(cls,source,block_start_string=BLOCK_START_STRING,block_end_string=BLOCK_END_STRING,variable_start_string=VARIABLE_START_STRING,variable_end_string=VARIABLE_END_STRING,comment_start_string=COMMENT_START_STRING,comment_end_string=COMMENT_END_STRING,line_statement_prefix=LINE_STATEMENT_PREFIX,line_comment_prefix=LINE_COMMENT_PREFIX,trim_blocks=TRIM_BLOCKS,lstrip_blocks=LSTRIP_BLOCKS,newline_sequence=NEWLINE_SEQUENCE,keep_trailing_newline=KEEP_TRAILING_NEWLINE,extensions=(),optimized=_C,undefined=Undefined,finalize=_A,autoescape=_B,enable_async=_B):env=get_spontaneous_environment(cls.environment_class,block_start_string,block_end_string,variable_start_string,variable_end_string,comment_start_string,comment_end_string,line_statement_prefix,line_comment_prefix,trim_blocks,lstrip_blocks,newline_sequence,keep_trailing_newline,frozenset(extensions),optimized,undefined,finalize,autoescape,_A,0,_B,_A,enable_async);return env.from_string(source,template_class=cls)
	@classmethod
	def from_code(cls,environment,code,globals,uptodate=_A):namespace={_F:environment,_G:code.co_filename};exec(code,namespace);rv=cls._from_namespace(environment,namespace,globals);rv._uptodate=uptodate;return rv
	@classmethod
	def from_module_dict(cls,environment,module_dict,globals):return cls._from_namespace(environment,module_dict,globals)
	@classmethod
	def _from_namespace(cls,environment,namespace,globals):t=object.__new__(cls);t.environment=environment;t.globals=globals;t.name=namespace['name'];t.filename=namespace[_G];t.blocks=namespace['blocks'];t.root_render_func=namespace['root'];t._module=_A;t._debug_info=namespace['debug_info'];t._uptodate=_A;namespace[_F]=environment;namespace['__jinja_template__']=t;return t
	def render(self,*args,**kwargs):
		if self.environment.is_async:
			import asyncio;close=_B
			if sys.version_info<(3,7):loop=asyncio.get_event_loop()
			else:
				try:loop=asyncio.get_running_loop()
				except RuntimeError:loop=asyncio.new_event_loop();close=_C
			try:return loop.run_until_complete(self.render_async(*(args),**kwargs))
			finally:
				if close:loop.close()
		ctx=self.new_context(dict(*(args),**kwargs))
		try:return concat(self.root_render_func(ctx))
		except Exception:self.environment.handle_exception()
	async def render_async(self,*args,**kwargs):
		if not self.environment.is_async:raise RuntimeError(_H)
		ctx=self.new_context(dict(*(args),**kwargs))
		try:return concat([n async for n in self.root_render_func(ctx)])
		except Exception:return self.environment.handle_exception()
	def stream(self,*args,**kwargs):return TemplateStream(self.generate(*(args),**kwargs))
	def generate(self,*args,**kwargs):
		if self.environment.is_async:
			import asyncio
			async def to_list():return[x async for x in self.generate_async(*(args),**kwargs)]
			if sys.version_info<(3,7):loop=asyncio.get_event_loop();out=loop.run_until_complete(to_list())
			else:out=asyncio.run(to_list())
			yield from out;return
		ctx=self.new_context(dict(*(args),**kwargs))
		try:yield from self.root_render_func(ctx)
		except Exception:yield self.environment.handle_exception()
	async def generate_async(self,*args,**kwargs):
		if not self.environment.is_async:raise RuntimeError(_H)
		ctx=self.new_context(dict(*(args),**kwargs))
		try:
			async for event in self.root_render_func(ctx):yield event
		except Exception:yield self.environment.handle_exception()
	def new_context(self,vars=_A,shared=_B,locals=_A):return new_context(self.environment,self.name,self.blocks,vars,shared,self.globals,locals)
	def make_module(self,vars=_A,shared=_B,locals=_A):ctx=self.new_context(vars,shared,locals);return TemplateModule(self,ctx)
	async def make_module_async(self,vars=_A,shared=_B,locals=_A):ctx=self.new_context(vars,shared,locals);return TemplateModule(self,ctx,[x async for x in self.root_render_func(ctx)])
	@internalcode
	def _get_default_module(self,ctx=_A):
		if self.environment.is_async:raise RuntimeError('Module is not available in async mode.')
		if ctx is not _A:
			keys=ctx.globals_keys-self.globals.keys()
			if keys:return self.make_module({k:ctx.parent[k]for k in keys})
		if self._module is _A:self._module=self.make_module()
		return self._module
	async def _get_default_module_async(self,ctx=_A):
		if ctx is not _A:
			keys=ctx.globals_keys-self.globals.keys()
			if keys:return await self.make_module_async({k:ctx.parent[k]for k in keys})
		if self._module is _A:self._module=await self.make_module_async()
		return self._module
	@property
	def module(self):return self._get_default_module()
	def get_corresponding_lineno(self,lineno):
		for (template_line,code_line) in reversed(self.debug_info):
			if code_line<=lineno:return template_line
		return 1
	@property
	def is_up_to_date(self):
		if self._uptodate is _A:return _C
		return self._uptodate()
	@property
	def debug_info(self):
		if self._debug_info:return[tuple(map(int,x.split('=')))for x in self._debug_info.split('&')]
		return[]
	def __repr__(self):
		if self.name is _A:name=f"memory:{id(self):x}"
		else:name=repr(self.name)
		return f"<{type(self).__name__} {name}>"
class TemplateModule:
	def __init__(self,template,context,body_stream=_A):
		if body_stream is _A:
			if context.environment.is_async:raise RuntimeError('Async mode requires a body stream to be passed to a template module. Use the async methods of the API you are using.')
			body_stream=list(template.root_render_func(context))
		self._body_stream=body_stream;self.__dict__.update(context.get_exported());self.__name__=template.name
	def __html__(self):return Markup(concat(self._body_stream))
	def __str__(self):return concat(self._body_stream)
	def __repr__(self):
		if self.__name__ is _A:name=f"memory:{id(self):x}"
		else:name=repr(self.__name__)
		return f"<{type(self).__name__} {name}>"
class TemplateExpression:
	def __init__(self,template,undefined_to_none):self._template=template;self._undefined_to_none=undefined_to_none
	def __call__(self,*args,**kwargs):
		context=self._template.new_context(dict(*(args),**kwargs));consume(self._template.root_render_func(context));rv=context.vars[_D]
		if self._undefined_to_none and isinstance(rv,Undefined):rv=_A
		return rv
class TemplateStream:
	def __init__(self,gen):self._gen=gen;self.disable_buffering()
	def dump(self,fp,encoding=_A,errors='strict'):
		close=_B
		if isinstance(fp,str):
			if encoding is _A:encoding='utf-8'
			fp=open(fp,'wb');close=_C
		try:
			if encoding is not _A:iterable=(x.encode(encoding,errors)for x in self)
			else:iterable=self
			if hasattr(fp,'writelines'):fp.writelines(iterable)
			else:
				for item in iterable:fp.write(item)
		finally:
			if close:fp.close()
	def disable_buffering(self):self._next=partial(next,self._gen);self.buffered=_B
	def _buffered_generator(self,size):
		buf=[];c_size=0;push=buf.append
		while _C:
			try:
				while c_size<size:
					c=next(self._gen);push(c)
					if c:c_size+=1
			except StopIteration:
				if not c_size:return
			yield concat(buf);del buf[:];c_size=0
	def enable_buffering(self,size=5):
		if size<=1:raise ValueError('buffer size too small')
		self.buffered=_C;self._next=partial(next,self._buffered_generator(size))
	def __iter__(self):return self
	def __next__(self):return self._next()
Environment.template_class=Template