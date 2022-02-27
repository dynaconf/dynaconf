_I='default'
_H='indent'
_G='No first item, sequence was empty.'
_F='HasHTML'
_E='common'
_D='__html__'
_C=True
_B=False
_A=None
import math,random,re,typing,typing as t,warnings
from collections import abc
from itertools import chain
from itertools import groupby
from dynaconf.vendor.markupsafe import escape
from dynaconf.vendor.markupsafe import Markup
from dynaconf.vendor.markupsafe import soft_str
from .async_utils import async_variant
from .async_utils import auto_aiter
from .async_utils import auto_await
from .async_utils import auto_to_list
from .exceptions import FilterArgumentError
from .runtime import Undefined
from .utils import htmlsafe_json_dumps
from .utils import pass_context
from .utils import pass_environment
from .utils import pass_eval_context
from .utils import pformat
from .utils import url_quote
from .utils import urlize
if t.TYPE_CHECKING:
	import typing_extensions as te;from .environment import Environment;from .nodes import EvalContext;from .runtime import Context;from .sandbox import SandboxedEnvironment
	class HasHTML(te.Protocol):
		def __html__(A):0
F=t.TypeVar('F',bound=t.Callable[...,t.Any])
K=t.TypeVar('K')
V=t.TypeVar('V')
def contextfilter(f):warnings.warn("'contextfilter' is renamed to 'pass_context', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_context(f)
def evalcontextfilter(f):warnings.warn("'evalcontextfilter' is renamed to 'pass_eval_context', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_eval_context(f)
def environmentfilter(f):warnings.warn("'environmentfilter' is renamed to 'pass_environment', the old name will be removed in Jinja 3.1.",DeprecationWarning,stacklevel=2);return pass_environment(f)
def ignore_case(value):
	A=value
	if isinstance(A,str):return t.cast(V,A.lower())
	return A
def make_attrgetter(environment,attribute,postprocess=_A,default=_A):
	C=default;B=postprocess;D=_prepare_attribute_parts(attribute)
	def A(item):
		A=item
		for E in D:
			A=environment.getitem(A,E)
			if C is not _A and isinstance(A,Undefined):A=C
		if B is not _A:A=B(A)
		return A
	return A
def make_multi_attrgetter(environment,attribute,postprocess=_A):
	B=postprocess;A=attribute
	if isinstance(A,str):C=A.split(',')
	else:C=[A]
	D=[_prepare_attribute_parts(A)for A in C]
	def E(item):
		C=[_A]*len(D)
		for (E,F) in enumerate(D):
			A=item
			for G in F:A=environment.getitem(A,G)
			if B is not _A:A=B(A)
			C[E]=A
		return C
	return E
def _prepare_attribute_parts(attr):
	A=attr
	if A is _A:return[]
	if isinstance(A,str):return[int(B)if B.isdigit()else B for B in A.split('.')]
	return[A]
def do_forceescape(value):
	A=value
	if hasattr(A,_D):A=t.cast(_F,A).__html__()
	return escape(str(A))
def do_urlencode(value):
	A=value
	if isinstance(A,str)or not isinstance(A,abc.Iterable):return url_quote(A)
	if isinstance(A,dict):B=A.items()
	else:B=A
	return '&'.join((f"{url_quote(A,for_qs=_C)}={url_quote(C,for_qs=_C)}"for(A,C)in B))
@pass_eval_context
def do_replace(eval_ctx,s,old,new,count=_A):
	C=new;B=old;A=count
	if A is _A:A=-1
	if not eval_ctx.autoescape:return str(s).replace(str(B),str(C),A)
	if hasattr(B,_D)or hasattr(C,_D)and not hasattr(s,_D):s=escape(s)
	else:s=soft_str(s)
	return s.replace(soft_str(B),soft_str(C),A)
def do_upper(s):return soft_str(s).upper()
def do_lower(s):return soft_str(s).lower()
@pass_eval_context
def do_xmlattr(eval_ctx,d,autospace=_C):
	A=' '.join((f'{escape(B)}="{escape(A)}"'for(B,A)in d.items()if A is not _A and not isinstance(A,Undefined)))
	if autospace and A:A=' '+A
	if eval_ctx.autoescape:A=Markup(A)
	return A
def do_capitalize(s):return soft_str(s).capitalize()
_word_beginning_split_re=re.compile('([-\\s({\\[<]+)')
def do_title(s):return ''.join([A[0].upper()+A[1:].lower()for A in _word_beginning_split_re.split(soft_str(s))if A])
def do_dictsort(value,case_sensitive=_B,by='key',reverse=_B):
	if by=='key':B=0
	elif by=='value':B=1
	else:raise FilterArgumentError('You can only sort by either "key" or "value"')
	def A(item):
		A=item[B]
		if not case_sensitive:A=ignore_case(A)
		return A
	return sorted(value.items(),key=A,reverse=reverse)
@pass_environment
def do_sort(environment,value,reverse=_B,case_sensitive=_B,attribute=_A):A=make_multi_attrgetter(environment,attribute,postprocess=ignore_case if not case_sensitive else _A);return sorted(value,key=A,reverse=reverse)
@pass_environment
def do_unique(environment,value,case_sensitive=_B,attribute=_A):
	D=make_attrgetter(environment,attribute,postprocess=ignore_case if not case_sensitive else _A);A=set()
	for B in value:
		C=D(B)
		if C not in A:A.add(C);yield B
def _min_or_max(environment,value,func,case_sensitive,attribute):
	A=environment;B=iter(value)
	try:C=next(B)
	except StopIteration:return A.undefined('No aggregated item, sequence was empty.')
	D=make_attrgetter(A,attribute,postprocess=ignore_case if not case_sensitive else _A);return func(chain([C],B),key=D)
@pass_environment
def do_min(environment,value,case_sensitive=_B,attribute=_A):return _min_or_max(environment,value,min,case_sensitive,attribute)
@pass_environment
def do_max(environment,value,case_sensitive=_B,attribute=_A):return _min_or_max(environment,value,max,case_sensitive,attribute)
def do_default(value,default_value='',boolean=_B):
	A=value
	if isinstance(A,Undefined)or boolean and not A:return default_value
	return A
@pass_eval_context
def sync_do_join(eval_ctx,value,d='',attribute=_A):
	C=attribute;B=eval_ctx;A=value
	if C is not _A:A=map(make_attrgetter(B.environment,C),A)
	if not B.autoescape:return str(d).join(map(str,A))
	if not hasattr(d,_D):
		A=list(A);D=_B
		for (F,E) in enumerate(A):
			if hasattr(E,_D):D=_C
			else:A[F]=str(E)
		if D:d=escape(d)
		else:d=str(d)
		return d.join(A)
	return soft_str(d).join(map(soft_str,A))
@async_variant(sync_do_join)
async def do_join(eval_ctx,value,d='',attribute=_A):return sync_do_join(eval_ctx,await auto_to_list(value),d,attribute)
def do_center(value,width=80):return soft_str(value).center(width)
@pass_environment
def sync_do_first(environment,seq):
	try:return next(iter(seq))
	except StopIteration:return environment.undefined(_G)
@async_variant(sync_do_first)
async def do_first(environment,seq):
	try:return await auto_aiter(seq).__anext__()
	except StopAsyncIteration:return environment.undefined(_G)
@pass_environment
def do_last(environment,seq):
	try:return next(iter(reversed(seq)))
	except StopIteration:return environment.undefined('No last item, sequence was empty.')
@pass_context
def do_random(context,seq):
	try:return random.choice(seq)
	except IndexError:return context.environment.undefined('No random item, sequence was empty.')
def do_filesizeformat(value,binary=_B):
	A=binary;bytes=float(value);B=1024 if A else 1000;E=['KiB'if A else'kB','MiB'if A else'MB','GiB'if A else'GB','TiB'if A else'TB','PiB'if A else'PB','EiB'if A else'EB','ZiB'if A else'ZB','YiB'if A else'YB']
	if bytes==1:return'1 Byte'
	elif bytes<B:return f"{int(bytes)} Bytes"
	else:
		for (F,D) in enumerate(E):
			C=B**(F+2)
			if bytes<C:return f"{B*bytes/C:.1f} {D}"
		return f"{B*bytes/C:.1f} {D}"
def do_pprint(value):return pformat(value)
_uri_scheme_re=re.compile('^([\\w.+-]{2,}:(/){0,2})$')
@pass_eval_context
def do_urlize(eval_ctx,value,trim_url_limit=_A,nofollow=_B,target=_A,rel=_A,extra_schemes=_A):
	G=eval_ctx;C=rel;B=target;A=extra_schemes;D=G.environment.policies;E=set((C or'').split())
	if nofollow:E.add('nofollow')
	E.update((D['urlize.rel']or'').split());C=' '.join(sorted(E))or _A
	if B is _A:B=D['urlize.target']
	if A is _A:A=D['urlize.extra_schemes']or()
	for H in A:
		if _uri_scheme_re.fullmatch(H)is _A:raise FilterArgumentError(f"{H!r} is not a valid URI scheme prefix.")
	F=urlize(value,trim_url_limit=trim_url_limit,rel=C,target=B,extra_schemes=A)
	if G.autoescape:F=Markup(F)
	return F
def do_indent(s,width=4,first=_B,blank=_B):
	D=width
	if isinstance(D,str):A=D
	else:A=' '*D
	B='\n'
	if isinstance(s,Markup):A=Markup(A);B=Markup(B)
	s+=B
	if blank:C=(B+A).join(s.splitlines())
	else:
		E=s.splitlines();C=E.pop(0)
		if E:C+=B+B.join((A+B if B else B for B in E))
	if first:C=A+C
	return C
@pass_environment
def do_truncate(env,s,length=255,killwords=_B,end='...',leeway=_A):
	C=leeway;B=length;A=end
	if C is _A:C=env.policies['truncate.leeway']
	assert B>=len(A),f"expected length >= {len(A)}, got {B}";assert C>=0,f"expected leeway >= 0, got {C}"
	if len(s)<=B+C:return s
	if killwords:return s[:B-len(A)]+A
	D=s[:B-len(A)].rsplit(' ',1)[0];return D+A
@pass_environment
def do_wordwrap(environment,s,width=79,break_long_words=_C,wrapstring=_A,break_on_hyphens=_C):
	A=wrapstring;import textwrap as B
	if A is _A:A=environment.newline_sequence
	return A.join([A.join(B.wrap(C,width=width,expand_tabs=_B,replace_whitespace=_B,break_long_words=break_long_words,break_on_hyphens=break_on_hyphens))for C in s.splitlines()])
_word_re=re.compile('\\w+')
def do_wordcount(s):return len(_word_re.findall(soft_str(s)))
def do_int(value,default=0,base=10):
	A=value
	try:
		if isinstance(A,str):return int(A,base)
		return int(A)
	except (TypeError,ValueError):
		try:return int(float(A))
		except (TypeError,ValueError):return default
def do_float(value,default=0.0):
	try:return float(value)
	except (TypeError,ValueError):return default
def do_format(value,*A,**B):
	if A and B:raise FilterArgumentError("can't handle positional and keyword arguments at the same time")
	return soft_str(value)%(B or A)
def do_trim(value,chars=_A):return soft_str(value).strip(chars)
def do_striptags(value):
	A=value
	if hasattr(A,_D):A=t.cast(_F,A).__html__()
	return Markup(str(A)).striptags()
def sync_do_slice(value,slices,fill_with=_A):
	D=fill_with;B=slices;E=list(value);F=len(E);G=F//B;H=F%B;C=0
	for A in range(B):
		J=C+A*G
		if A<H:C+=1
		K=C+(A+1)*G;I=E[J:K]
		if D is not _A and A>=H:I.append(D)
		yield I
@async_variant(sync_do_slice)
async def do_slice(value,slices,fill_with=_A):return sync_do_slice(await auto_to_list(value),slices,fill_with)
def do_batch(value,linecount,fill_with=_A):
	C=fill_with;B=linecount;A=[]
	for D in value:
		if len(A)==B:yield A;A=[]
		A.append(D)
	if A:
		if C is not _A and len(A)<B:A+=[C]*(B-len(A))
		yield A
def do_round(value,precision=0,method=_E):
	C=value;B=method;A=precision
	if B not in{_E,'ceil','floor'}:raise FilterArgumentError('method must be common, ceil or floor')
	if B==_E:return round(C,A)
	D=getattr(math,B);return t.cast(float,D(C*10**A)/10**A)
class _GroupTuple(t.NamedTuple):
	grouper:t.Any;list:t.List
	def __repr__(A):return tuple.__repr__(A)
	def __str__(A):return tuple.__str__(A)
@pass_environment
def sync_do_groupby(environment,value,attribute,default=_A):A=make_attrgetter(environment,attribute,default=default);return[_GroupTuple(B,list(C))for(B,C)in groupby(sorted(value,key=A),A)]
@async_variant(sync_do_groupby)
async def do_groupby(environment,value,attribute,default=_A):A=make_attrgetter(environment,attribute,default=default);return[_GroupTuple(B,await auto_to_list(C))for(B,C)in groupby(sorted(await auto_to_list(value),key=A),A)]
@pass_environment
def sync_do_sum(environment,iterable,attribute=_A,start=0):
	B=attribute;A=iterable
	if B is not _A:A=map(make_attrgetter(environment,B),A)
	return sum(A,start)
@async_variant(sync_do_sum)
async def do_sum(environment,iterable,attribute=_A,start=0):
	A=attribute;B=start
	if A is not _A:C=make_attrgetter(environment,A)
	else:
		def C(x):return x
	async for D in auto_aiter(iterable):B+=C(D)
	return B
def sync_do_list(value):return list(value)
@async_variant(sync_do_list)
async def do_list(value):return await auto_to_list(value)
def do_mark_safe(value):return Markup(value)
def do_mark_unsafe(value):return str(value)
@typing.overload
def do_reverse(value):...
@typing.overload
def do_reverse(value):...
def do_reverse(value):
	A=value
	if isinstance(A,str):return A[::-1]
	try:return reversed(A)
	except TypeError:
		try:B=list(A);B.reverse();return B
		except TypeError as C:raise FilterArgumentError('argument must be iterable') from C
@pass_environment
def do_attr(environment,obj,name):
	C=obj;B=name;A=environment
	try:B=str(B)
	except UnicodeError:pass
	else:
		try:D=getattr(C,B)
		except AttributeError:pass
		else:
			if A.sandboxed:
				A=t.cast('SandboxedEnvironment',A)
				if not A.is_safe_attribute(C,B,D):return A.unsafe_undefined(C,B)
			return D
	return A.undefined(obj=C,name=B)
@typing.overload
def sync_do_map(context,value,name,*A,**B):...
@typing.overload
def sync_do_map(context,value,*,attribute=...,default=_A):...
@pass_context
def sync_do_map(context,value,*B,**C):
	A=value
	if A:
		D=prepare_map(context,B,C)
		for E in A:yield D(E)
@typing.overload
def do_map(context,value,name,*A,**B):...
@typing.overload
def do_map(context,value,*,attribute=...,default=_A):...
@async_variant(sync_do_map)
async def do_map(context,value,*B,**C):
	A=value
	if A:
		D=prepare_map(context,B,C)
		async for E in auto_aiter(A):yield await auto_await(D(E))
@pass_context
def sync_do_select(context,value,*A,**B):return select_or_reject(context,value,A,B,lambda x:x,_B)
@async_variant(sync_do_select)
async def do_select(context,value,*A,**B):return async_select_or_reject(context,value,A,B,lambda x:x,_B)
@pass_context
def sync_do_reject(context,value,*A,**B):return select_or_reject(context,value,A,B,lambda x:not x,_B)
@async_variant(sync_do_reject)
async def do_reject(context,value,*A,**B):return async_select_or_reject(context,value,A,B,lambda x:not x,_B)
@pass_context
def sync_do_selectattr(context,value,*A,**B):return select_or_reject(context,value,A,B,lambda x:x,_C)
@async_variant(sync_do_selectattr)
async def do_selectattr(context,value,*A,**B):return async_select_or_reject(context,value,A,B,lambda x:x,_C)
@pass_context
def sync_do_rejectattr(context,value,*A,**B):return select_or_reject(context,value,A,B,lambda x:not x,_C)
@async_variant(sync_do_rejectattr)
async def do_rejectattr(context,value,*A,**B):return async_select_or_reject(context,value,A,B,lambda x:not x,_C)
@pass_eval_context
def do_tojson(eval_ctx,value,indent=_A):
	B=indent;C=eval_ctx.environment.policies;D=C['json.dumps_function'];A=C['json.dumps_kwargs']
	if B is not _A:A=A.copy();A[_H]=B
	return htmlsafe_json_dumps(value,dumps=D,**A)
def prepare_map(context,args,kwargs):
	E='attribute';C=context;B=args;A=kwargs
	if not B and E in A:
		F=A.pop(E);G=A.pop(_I,_A)
		if A:raise FilterArgumentError(f"Unexpected keyword argument {next(iter(A))!r}")
		D=make_attrgetter(C.environment,F,default=G)
	else:
		try:H=B[0];B=B[1:]
		except LookupError:raise FilterArgumentError('map requires a filter argument') from _A
		def D(item):return C.environment.call_filter(H,item,B,A,context=C)
	return D
def prepare_select_or_reject(context,args,kwargs,modfunc,lookup_attr):
	C=context;A=args
	if lookup_attr:
		try:F=A[0]
		except LookupError:raise FilterArgumentError('Missing parameter for attribute name') from _A
		D=make_attrgetter(C.environment,F);B=1
	else:
		B=0
		def D(x):return x
	try:
		G=A[B];A=A[1+B:]
		def E(item):return C.environment.call_test(G,item,A,kwargs)
	except LookupError:E=bool
	return lambda item:modfunc(E(D(item)))
def select_or_reject(context,value,args,kwargs,modfunc,lookup_attr):
	A=value
	if A:
		C=prepare_select_or_reject(context,args,kwargs,modfunc,lookup_attr)
		for B in A:
			if C(B):yield B
async def async_select_or_reject(context,value,args,kwargs,modfunc,lookup_attr):
	A=value
	if A:
		C=prepare_select_or_reject(context,args,kwargs,modfunc,lookup_attr)
		async for B in auto_aiter(A):
			if C(B):yield B
FILTERS={'abs':abs,'attr':do_attr,'batch':do_batch,'capitalize':do_capitalize,'center':do_center,'count':len,'d':do_default,_I:do_default,'dictsort':do_dictsort,'e':escape,'escape':escape,'filesizeformat':do_filesizeformat,'first':do_first,'float':do_float,'forceescape':do_forceescape,'format':do_format,'groupby':do_groupby,_H:do_indent,'int':do_int,'join':do_join,'last':do_last,'length':len,'list':do_list,'lower':do_lower,'map':do_map,'min':do_min,'max':do_max,'pprint':do_pprint,'random':do_random,'reject':do_reject,'rejectattr':do_rejectattr,'replace':do_replace,'reverse':do_reverse,'round':do_round,'safe':do_mark_safe,'select':do_select,'selectattr':do_selectattr,'slice':do_slice,'sort':do_sort,'string':soft_str,'striptags':do_striptags,'sum':do_sum,'title':do_title,'trim':do_trim,'truncate':do_truncate,'unique':do_unique,'upper':do_upper,'urlencode':do_urlencode,'urlize':do_urlize,'wordcount':do_wordcount,'wordwrap':do_wordwrap,'xmlattr':do_xmlattr,'tojson':do_tojson}