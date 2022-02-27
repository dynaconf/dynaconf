_D='escape'
_C='__getitem__'
_B=None
_A='__html__'
import functools,re,string,typing as t
if t.TYPE_CHECKING:
	import typing_extensions as te
	class HasHTML(te.Protocol):
		def __html__(self):0
__version__='2.1.0.dev0'
_striptags_re=re.compile('(<!--.*?-->|<[^>]*>)')
def _simple_escaping_wrapper(name):
	orig=getattr(str,name)
	@functools.wraps(orig)
	def wrapped(self,*args,**kwargs):args=_escape_argspec(list(args),enumerate(args),self.escape);_escape_argspec(kwargs,kwargs.items(),self.escape);return self.__class__(orig(self,*(args),**kwargs))
	return wrapped
class Markup(str):
	'A string that is ready to be safely inserted into an HTML or XML\n    document, either because it was escaped or because it was marked\n    safe.\n\n    Passing an object to the constructor converts it to text and wraps\n    it to mark it safe without escaping. To escape the text, use the\n    :meth:`escape` class method instead.\n\n    >>> Markup("Hello, <em>World</em>!")\n    Markup(\'Hello, <em>World</em>!\')\n    >>> Markup(42)\n    Markup(\'42\')\n    >>> Markup.escape("Hello, <em>World</em>!")\n    Markup(\'Hello &lt;em&gt;World&lt;/em&gt;!\')\n\n    This implements the ``__html__()`` interface that some frameworks\n    use. Passing an object that implements ``__html__()`` will wrap the\n    output of that method, marking it safe.\n\n    >>> class Foo:\n    ...     def __html__(self):\n    ...         return \'<a href="/foo">foo</a>\'\n    ...\n    >>> Markup(Foo())\n    Markup(\'<a href="/foo">foo</a>\')\n\n    This is a subclass of :class:`str`. It has the same methods, but\n    escapes their arguments and returns a ``Markup`` instance.\n\n    >>> Markup("<em>%s</em>") % ("foo & bar",)\n    Markup(\'<em>foo &amp; bar</em>\')\n    >>> Markup("<em>Hello</em> ") + "<foo>"\n    Markup(\'<em>Hello</em> &lt;foo&gt;\')\n    ';__slots__=()
	def __new__(cls,base='',encoding=_B,errors='strict'):
		if hasattr(base,_A):base=base.__html__()
		if encoding is _B:return super().__new__(cls,base)
		return super().__new__(cls,base,encoding,errors)
	def __html__(self):return self
	def __add__(self,other):
		if isinstance(other,str)or hasattr(other,_A):return self.__class__(super().__add__(self.escape(other)))
		return NotImplemented
	def __radd__(self,other):
		if isinstance(other,str)or hasattr(other,_A):return self.escape(other).__add__(self)
		return NotImplemented
	def __mul__(self,num):
		if isinstance(num,int):return self.__class__(super().__mul__(num))
		return NotImplemented
	__rmul__=__mul__
	def __mod__(self,arg):
		if isinstance(arg,tuple):arg=tuple((_MarkupEscapeHelper(x,self.escape)for x in arg))
		elif hasattr(type(arg),_C)and not isinstance(arg,str):arg=_MarkupEscapeHelper(arg,self.escape)
		else:arg=_MarkupEscapeHelper(arg,self.escape),
		return self.__class__(super().__mod__(arg))
	def __repr__(self):return f"{self.__class__.__name__}({super().__repr__()})"
	def join(self,seq):return self.__class__(super().join(map(self.escape,seq)))
	join.__doc__=str.join.__doc__
	def split(self,sep=_B,maxsplit=-1):return[self.__class__(v)for v in super().split(sep,maxsplit)]
	split.__doc__=str.split.__doc__
	def rsplit(self,sep=_B,maxsplit=-1):return[self.__class__(v)for v in super().rsplit(sep,maxsplit)]
	rsplit.__doc__=str.rsplit.__doc__
	def splitlines(self,keepends=False):return[self.__class__(v)for v in super().splitlines(keepends)]
	splitlines.__doc__=str.splitlines.__doc__
	def unescape(self):'Convert escaped markup back into a text string. This replaces\n        HTML entities with the characters they represent.\n\n        >>> Markup("Main &raquo; <em>About</em>").unescape()\n        \'Main » <em>About</em>\'\n        ';from html import unescape;return unescape(str(self))
	def striptags(self):':meth:`unescape` the markup, remove tags, and normalize\n        whitespace to single spaces.\n\n        >>> Markup("Main &raquo;\t<em>About</em>").striptags()\n        \'Main » About\'\n        ';stripped=' '.join(_striptags_re.sub('',self).split());return Markup(stripped).unescape()
	@classmethod
	def escape(cls,s):
		'Escape a string. Calls :func:`escape` and ensures that for\n        subclasses the correct type is returned.\n        ';rv=escape(s)
		if rv.__class__ is not cls:return cls(rv)
		return rv
	for method in (_C,'capitalize','title','lower','upper','replace','ljust','rjust','lstrip','rstrip','center','strip','translate','expandtabs','swapcase','zfill'):locals()[method]=_simple_escaping_wrapper(method)
	del method
	def partition(self,sep):l,s,r=super().partition(self.escape(sep));cls=self.__class__;return cls(l),cls(s),cls(r)
	def rpartition(self,sep):l,s,r=super().rpartition(self.escape(sep));cls=self.__class__;return cls(l),cls(s),cls(r)
	def format(self,*args,**kwargs):formatter=EscapeFormatter(self.escape);return self.__class__(formatter.vformat(self,args,kwargs))
	def __html_format__(self,format_spec):
		if format_spec:raise ValueError('Unsupported format specification for Markup.')
		return self
class EscapeFormatter(string.Formatter):
	__slots__=_D,
	def __init__(self,escape):self.escape=escape;super().__init__()
	def format_field(self,value,format_spec):
		if hasattr(value,'__html_format__'):rv=value.__html_format__(format_spec)
		elif hasattr(value,_A):
			if format_spec:raise ValueError(f"Format specifier {format_spec} given, but {type(value)} does not define __html_format__. A class that defines __html__ must define __html_format__ to work with format specifiers.")
			rv=value.__html__()
		else:rv=string.Formatter.format_field(self,value,str(format_spec))
		return str(self.escape(rv))
_ListOrDict=t.TypeVar('_ListOrDict',list,dict)
def _escape_argspec(obj,iterable,escape):
	'Helper for various string-wrapped functions.'
	for (key,value) in iterable:
		if isinstance(value,str)or hasattr(value,_A):obj[key]=escape(value)
	return obj
class _MarkupEscapeHelper:
	'Helper for :meth:`Markup.__mod__`.';__slots__='obj',_D
	def __init__(self,obj,escape):self.obj=obj;self.escape=escape
	def __getitem__(self,item):return _MarkupEscapeHelper(self.obj[item],self.escape)
	def __str__(self):return str(self.escape(self.obj))
	def __repr__(self):return str(self.escape(repr(self.obj)))
	def __int__(self):return int(self.obj)
	def __float__(self):return float(self.obj)
try:from ._speedups import escape as escape,escape_silent as escape_silent,soft_str as soft_str,soft_unicode
except ImportError:from ._native import escape as escape;from ._native import escape_silent as escape_silent;from ._native import soft_str as soft_str;from ._native import soft_unicode