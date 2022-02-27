_D=True
_C=False
_B='.'
_A=None
import enum,json,os,re,typing as t,warnings
from collections import abc,deque
from random import choice
from random import randrange
from threading import Lock
from types import CodeType
from urllib.parse import quote_from_bytes
import dynaconf.vendor.markupsafe as markupsafe
if t.TYPE_CHECKING:import typing_extensions as te
F=t.TypeVar('F',bound=t.Callable[...,t.Any])
missing=type('MissingType',(),{'__repr__':lambda x:'missing'})()
internal_code=set()
concat=''.join
def pass_context(f):f.jinja_pass_arg=_PassArg.context;return f
def pass_eval_context(f):f.jinja_pass_arg=_PassArg.eval_context;return f
def pass_environment(f):f.jinja_pass_arg=_PassArg.environment;return f
class _PassArg(enum.Enum):
	context=enum.auto();eval_context=enum.auto();environment=enum.auto()
	@classmethod
	def from_obj(E,obj):
		A=obj
		if hasattr(A,'jinja_pass_arg'):return A.jinja_pass_arg
		for B in ('context','eval_context','environment'):
			C=B.replace('_','')
			for D in (f"{C}function",f"{C}filter"):
				if getattr(A,D,_C)is _D:warnings.warn(f"{D!r} is deprecated and will stop working in Jinja 3.1. Use 'pass_{B}' instead.",DeprecationWarning,stacklevel=2);return E[B]
		return _A
def contextfunction(f):warnings.warn("'contextfunction' is renamed to 'pass_context', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_context(f)
def evalcontextfunction(f):warnings.warn("'evalcontextfunction' is renamed to 'pass_eval_context', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_eval_context(f)
def environmentfunction(f):warnings.warn("'environmentfunction' is renamed to 'pass_environment', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_environment(f)
def internalcode(f):internal_code.add(f.__code__);return f
def is_undefined(obj):from .runtime import Undefined as A;return isinstance(obj,A)
def consume(iterable):
	for A in iterable:0
def clear_caches():from .environment import get_spontaneous_environment as A;from .lexer import _lexer_cache as B;A.cache_clear();B.clear()
def import_string(import_name,silent=_C):
	A=import_name
	try:
		if':'in A:C,B=A.split(':',1)
		elif _B in A:C,D,B=A.rpartition(_B)
		else:return __import__(A)
		return getattr(__import__(C,_A,_A,[B]),B)
	except (ImportError,AttributeError):
		if not silent:raise
def open_if_exists(filename,mode='rb'):
	A=filename
	if not os.path.isfile(A):return _A
	return open(A,mode)
def object_type_repr(obj):
	B=obj
	if B is _A:return'None'
	elif B is Ellipsis:return'Ellipsis'
	A=type(B)
	if A.__module__=='builtins':return f"{A.__name__} object"
	return f"{A.__module__}.{A.__name__} object"
def pformat(obj):from pprint import pformat as A;return A(obj)
_http_re=re.compile('\n    ^\n    (\n        (https?://|www\\.)  # scheme or www\n        (([\\w%-]+\\.)+)?  # subdomain\n        (\n            [a-z]{2,63}  # basic tld\n        |\n            xn--[\\w%]{2,59}  # idna tld\n        )\n    |\n        ([\\w%-]{2,63}\\.)+  # basic domain\n        (com|net|int|edu|gov|org|info|mil)  # basic tld\n    |\n        (https?://)  # scheme\n        (\n            (([\\d]{1,3})(\\.[\\d]{1,3}){3})  # IPv4\n        |\n            (\\[([\\da-f]{0,4}:){2}([\\da-f]{0,4}:?){1,6}])  # IPv6\n        )\n    )\n    (?::[\\d]{1,5})?  # port\n    (?:[/?#]\\S*)?  # path, query, and fragment\n    $\n    ',re.IGNORECASE|re.VERBOSE)
_email_re=re.compile('^\\S+@\\w[\\w.-]*\\.\\w+$')
def urlize(text,trim_url_limit=_A,rel=_A,target=_A,extra_schemes=_A):
	P='&gt;';K=extra_schemes;J=target;E=trim_url_limit
	if E is not _A:
		def F(x):
			if len(x)>E:return f"{x[:E]}..."
			return x
	else:
		def F(x):return x
	G=re.split('(\\s+)',str(markupsafe.escape(text)));H=f' rel="{markupsafe.escape(rel)}"'if rel else'';I=f' target="{markupsafe.escape(J)}"'if J else''
	for (Q,R) in enumerate(G):
		L,A,B='',R,'';C=re.match('^([(<]|&lt;)+',A)
		if C:L=C.group();A=A[C.end():]
		if A.endswith((')','>',_B,',','\n',P)):
			C=re.search('([)>.,\\n]|&gt;)+$',A)
			if C:B=C.group();A=A[:C.start()]
		for (S,D) in (('(',')'),('<','>'),('&lt;',P)):
			M=A.count(S)
			if M<=A.count(D):continue
			for T in range(min(M,B.count(D))):N=B.index(D)+len(D);A+=B[:N];B=B[N:]
		if _http_re.match(A):
			if A.startswith('https://')or A.startswith('http://'):A=f'<a href="{A}"{H}{I}>{F(A)}</a>'
			else:A=f'<a href="https://{A}"{H}{I}>{F(A)}</a>'
		elif A.startswith('mailto:')and _email_re.match(A[7:]):A=f'<a href="{A}">{A[7:]}</a>'
		elif'@'in A and not A.startswith('www.')and':'not in A and _email_re.match(A):A=f'<a href="mailto:{A}">{A}</a>'
		elif K is not _A:
			for O in K:
				if A!=O and A.startswith(O):A=f'<a href="{A}"{H}{I}>{A}</a>'
		G[Q]=f"{L}{A}{B}"
	return ''.join(G)
def generate_lorem_ipsum(n=5,html=_D,min=20,max=100):
	from .constants import LOREM_IPSUM_WORDS as J;K=J.split();D=[]
	for L in range(n):
		E=_D;F=G=0;A=_A;H=_A;I=[]
		for (C,L) in enumerate(range(randrange(min,max))):
			while _D:
				A=choice(K)
				if A!=H:H=A;break
			if E:A=A.capitalize();E=_C
			if C-randrange(3,8)>F:F=C;G+=2;A+=','
			if C-randrange(10,20)>G:F=G=C;A+=_B;E=_D
			I.append(A)
		B=' '.join(I)
		if B.endswith(','):B=B[:-1]+_B
		elif not B.endswith(_B):B+=_B
		D.append(B)
	if not html:return '\n\n'.join(D)
	return markupsafe.Markup('\n'.join((f"<p>{markupsafe.escape(A)}</p>"for A in D)))
def url_quote(obj,charset='utf-8',for_qs=_C):
	C=for_qs;A=obj
	if not isinstance(A,bytes):
		if not isinstance(A,str):A=str(A)
		A=A.encode(charset)
	D=b''if C else b'/';B=quote_from_bytes(A,D)
	if C:B=B.replace('%20','+')
	return B
def unicode_urlencode(obj,charset='utf-8',for_qs=_C):import warnings as A;A.warn("'unicode_urlencode' has been renamed to 'url_quote'. The old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return url_quote(obj,charset=charset,for_qs=for_qs)
@abc.MutableMapping.register
class LRUCache:
	def __init__(A,capacity):A.capacity=capacity;A._mapping={};A._queue=deque();A._postinit()
	def _postinit(A):A._popleft=A._queue.popleft;A._pop=A._queue.pop;A._remove=A._queue.remove;A._wlock=Lock();A._append=A._queue.append
	def __getstate__(A):return{'capacity':A.capacity,'_mapping':A._mapping,'_queue':A._queue}
	def __setstate__(A,d):A.__dict__.update(d);A._postinit()
	def __getnewargs__(A):return A.capacity,
	def copy(A):B=A.__class__(A.capacity);B._mapping.update(A._mapping);B._queue.extend(A._queue);return B
	def get(A,key,default=_A):
		try:return A[key]
		except KeyError:return default
	def setdefault(A,key,default=_A):
		B=default
		try:return A[key]
		except KeyError:A[key]=B;return B
	def clear(A):
		with A._wlock:A._mapping.clear();A._queue.clear()
	def __contains__(A,key):return key in A._mapping
	def __len__(A):return len(A._mapping)
	def __repr__(A):return f"<{type(A).__name__} {A._mapping!r}>"
	def __getitem__(A,key):
		B=key
		with A._wlock:
			C=A._mapping[B]
			if A._queue[-1]!=B:
				try:A._remove(B)
				except ValueError:pass
				A._append(B)
			return C
	def __setitem__(A,key,value):
		B=key
		with A._wlock:
			if B in A._mapping:A._remove(B)
			elif len(A._mapping)==A.capacity:del A._mapping[A._popleft()]
			A._append(B);A._mapping[B]=value
	def __delitem__(A,key):
		with A._wlock:
			del A._mapping[key]
			try:A._remove(key)
			except ValueError:pass
	def items(A):B=[(B,A._mapping[B])for B in list(A._queue)];B.reverse();return B
	def values(A):return[B[1]for B in A.items()]
	def keys(A):return list(A)
	def __iter__(A):return reversed(tuple(A._queue))
	def __reversed__(A):return iter(tuple(A._queue))
	__copy__=copy
def select_autoescape(enabled_extensions=('html','htm','xml'),disabled_extensions=(),default_for_string=_D,default=_C):
	B=tuple((f".{A.lstrip(_B).lower()}"for A in enabled_extensions));C=tuple((f".{A.lstrip(_B).lower()}"for A in disabled_extensions))
	def A(template_name):
		A=template_name
		if A is _A:return default_for_string
		A=A.lower()
		if A.endswith(B):return _D
		if A.endswith(C):return _C
		return default
	return A
def htmlsafe_json_dumps(obj,dumps=_A,**B):
	A=dumps
	if A is _A:A=json.dumps
	return markupsafe.Markup(A(obj,**B).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace("'",'\\u0027'))
class Cycler:
	def __init__(A,*B):
		if not B:raise RuntimeError('at least one item has to be provided')
		A.items=B;A.pos=0
	def reset(A):A.pos=0
	@property
	def current(self):return self.items[self.pos]
	def next(A):B=A.current;A.pos=(A.pos+1)%len(A.items);return B
	__next__=next
class Joiner:
	def __init__(A,sep=', '):A.sep=sep;A.used=_C
	def __call__(A):
		if not A.used:A.used=_D;return''
		return A.sep
class Namespace:
	def __init__(*A,**B):C,A=A[0],A[1:];C.__attrs=dict(*(A),**B)
	def __getattribute__(B,name):
		A=name
		if A in{'_Namespace__attrs','__class__'}:return object.__getattribute__(B,A)
		try:return B.__attrs[A]
		except KeyError:raise AttributeError(A) from _A
	def __setitem__(A,name,value):A.__attrs[name]=value
	def __repr__(A):return f"<Namespace {A.__attrs!r}>"
class Markup(markupsafe.Markup):
	def __new__(A,base='',encoding=_A,errors='strict'):warnings.warn("'jinja2.Markup' is deprecated and will be removed in Jinja 3.1. Import 'markupsafe.Markup' instead.",DeprecationWarning,stacklevel=2);return super().__new__(A,base,encoding,errors)
def escape(s):warnings.warn("'jinja2.escape' is deprecated and will be removed in Jinja 3.1. Import 'markupsafe.escape' instead.",DeprecationWarning,stacklevel=2);return markupsafe.escape(s)