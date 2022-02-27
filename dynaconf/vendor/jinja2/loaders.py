_C=False
_B='utf-8'
_A=None
import importlib.util,os,sys,typing as t,weakref,zipimport
from collections import abc
from hashlib import sha1
from importlib import import_module
from types import ModuleType
from .exceptions import TemplateNotFound
from .utils import internalcode
from .utils import open_if_exists
if t.TYPE_CHECKING:from .environment import Environment,Template
def split_template_path(template):
	B=template;C=[]
	for A in B.split('/'):
		if os.path.sep in A or os.path.altsep and os.path.altsep in A or A==os.path.pardir:raise TemplateNotFound(B)
		elif A and A!='.':C.append(A)
	return C
class BaseLoader:
	has_source_access=True
	def get_source(A,environment,template):
		if not A.has_source_access:raise RuntimeError(f"{type(A).__name__} cannot provide access to the source")
		raise TemplateNotFound(template)
	def list_templates(A):raise TypeError('this loader cannot iterate over all templates')
	@internalcode
	def load(self,environment,name,globals=_A):
		E=name;A=environment;B=_A
		if globals is _A:globals={}
		F,G,H=self.get_source(A,E);C=A.bytecode_cache
		if C is not _A:D=C.get_bucket(A,E,G,F);B=D.code
		if B is _A:B=A.compile(F,E,G)
		if C is not _A and D.code is _A:D.code=B;C.set_bucket(D)
		return A.template_class.from_code(A,B,globals,H)
class FileSystemLoader(BaseLoader):
	def __init__(B,searchpath,encoding=_B,followlinks=_C):
		A=searchpath
		if not isinstance(A,abc.Iterable)or isinstance(A,str):A=[A]
		B.searchpath=[os.fspath(B)for B in A];B.encoding=encoding;B.followlinks=followlinks
	def get_source(C,environment,template):
		D=template;E=split_template_path(D)
		for F in C.searchpath:
			A=os.path.join(F,*(E));B=open_if_exists(A)
			if B is _A:continue
			try:G=B.read().decode(C.encoding)
			finally:B.close()
			H=os.path.getmtime(A)
			def I():
				try:return os.path.getmtime(A)==H
				except OSError:return _C
			return G,A,I
		raise TemplateNotFound(D)
	def list_templates(C):
		B=set()
		for D in C.searchpath:
			E=os.walk(D,followlinks=C.followlinks)
			for (F,I,G) in E:
				for H in G:
					A=os.path.join(F,H)[len(D):].strip(os.path.sep).replace(os.path.sep,'/')
					if A[:2]=='./':A=A[2:]
					if A not in B:B.add(A)
		return sorted(B)
class PackageLoader(BaseLoader):
	def __init__(B,package_name,package_path='templates',encoding=_B):
		D=package_name;A=package_path;A=os.path.normpath(A).rstrip(os.path.sep)
		if A==os.path.curdir:A=''
		elif A[:2]==os.path.curdir+os.path.sep:A=A[2:]
		B.package_path=A;B.package_name=D;B.encoding=encoding;import_module(D);C=importlib.util.find_spec(D);assert C is not _A,'An import spec was not found for the package.';E=C.loader;assert E is not _A,'A loader was not found for the package.';B._loader=E;B._archive=_A;F=_A
		if isinstance(E,zipimport.zipimporter):B._archive=E.archive;H=next(iter(C.submodule_search_locations));F=os.path.join(H,A)
		elif C.submodule_search_locations:
			for G in C.submodule_search_locations:
				G=os.path.join(G,A)
				if os.path.isdir(G):F=G;break
		if F is _A:raise ValueError(f"The {D!r} package was not installed in a way that PackageLoader understands.")
		B._template_root=F
	def get_source(B,environment,template):
		C=template;A=os.path.join(B._template_root,*split_template_path(C));D:0
		if B._archive is _A:
			if not os.path.isfile(A):raise TemplateNotFound(C)
			with open(A,'rb')as F:E=F.read()
			G=os.path.getmtime(A)
			def D():return os.path.isfile(A)and os.path.getmtime(A)==G
		else:
			try:E=B._loader.get_data(A)
			except OSError as H:raise TemplateNotFound(C) from H
			D=_A
		return E.decode(B.encoding),A,D
	def list_templates(A):
		B=[]
		if A._archive is _A:
			C=len(A._template_root)
			for (D,H,G) in os.walk(A._template_root):D=D[C:].lstrip(os.path.sep);B.extend((os.path.join(D,A).replace(os.path.sep,'/')for A in G))
		else:
			if not hasattr(A._loader,'_files'):raise TypeError('This zip import does not have the required metadata to list templates.')
			F=A._template_root[len(A._archive):].lstrip(os.path.sep)+os.path.sep;C=len(F)
			for E in A._loader._files.keys():
				if E.startswith(F)and E[-1]!=os.path.sep:B.append(E[C:].replace(os.path.sep,'/'))
		B.sort();return B
class DictLoader(BaseLoader):
	def __init__(A,mapping):A.mapping=mapping
	def get_source(B,environment,template):
		A=template
		if A in B.mapping:C=B.mapping[A];return C,_A,lambda:C==B.mapping.get(A)
		raise TemplateNotFound(A)
	def list_templates(A):return sorted(A.mapping)
class FunctionLoader(BaseLoader):
	def __init__(A,load_func):A.load_func=load_func
	def get_source(C,environment,template):
		B=template;A=C.load_func(B)
		if A is _A:raise TemplateNotFound(B)
		if isinstance(A,str):return A,_A,_A
		return A
class PrefixLoader(BaseLoader):
	def __init__(A,mapping,delimiter='/'):A.mapping=mapping;A.delimiter=delimiter
	def get_loader(A,template):
		B=template
		try:C,D=B.split(A.delimiter,1);E=A.mapping[C]
		except (ValueError,KeyError)as F:raise TemplateNotFound(B) from F
		return E,D
	def get_source(B,environment,template):
		A=template;C,D=B.get_loader(A)
		try:return C.get_source(environment,D)
		except TemplateNotFound as E:raise TemplateNotFound(A) from E
	@internalcode
	def load(self,environment,name,globals=_A):
		A,B=self.get_loader(name)
		try:return A.load(environment,B,globals)
		except TemplateNotFound as C:raise TemplateNotFound(name) from C
	def list_templates(A):
		B=[]
		for (C,D) in A.mapping.items():
			for E in D.list_templates():B.append(C+A.delimiter+E)
		return B
class ChoiceLoader(BaseLoader):
	def __init__(A,loaders):A.loaders=loaders
	def get_source(B,environment,template):
		A=template
		for C in B.loaders:
			try:return C.get_source(environment,A)
			except TemplateNotFound:pass
		raise TemplateNotFound(A)
	@internalcode
	def load(self,environment,name,globals=_A):
		for A in self.loaders:
			try:return A.load(environment,name,globals)
			except TemplateNotFound:pass
		raise TemplateNotFound(name)
	def list_templates(B):
		A=set()
		for C in B.loaders:A.update(C.list_templates())
		return sorted(A)
class _TemplateModule(ModuleType):0
class ModuleLoader(BaseLoader):
	has_source_access=_C
	def __init__(C,path):
		A=path;B=f"_jinja2_module_templates_{id(C):x}";D=_TemplateModule(B)
		if not isinstance(A,abc.Iterable)or isinstance(A,str):A=[A]
		D.__path__=[os.fspath(B)for B in A];sys.modules[B]=weakref.proxy(D,lambda x:sys.modules.pop(B,_A));C.module=D;C.package_name=B
	@staticmethod
	def get_template_key(name):return'tmpl_'+sha1(name.encode(_B)).hexdigest()
	@staticmethod
	def get_module_filename(name):return ModuleLoader.get_template_key(name)+'.py'
	@internalcode
	def load(self,environment,name,globals=_A):
		D=environment;A=self;E=A.get_template_key(name);B=f"{A.package_name}.{E}";C=getattr(A.module,B,_A)
		if C is _A:
			try:C=__import__(B,_A,_A,['root'])
			except ImportError as F:raise TemplateNotFound(name) from F
			sys.modules.pop(B,_A)
		if globals is _A:globals={}
		return D.template_class.from_module_dict(D,C.__dict__,globals)