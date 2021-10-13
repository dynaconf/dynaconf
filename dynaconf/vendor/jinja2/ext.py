_N='ext.i18n.trimmed'
_M='name:pluralize'
_L='trimmed'
_K='name'
_J='context'
_I='ngettext'
_H='npgettext'
_G='pgettext'
_F='gettext'
_E='load'
_D=False
_C='num'
_B=True
_A=None
import pprint,re,typing as t,warnings
from dynaconf.vendor.markupsafe import Markup
from .  import defaults
from .  import nodes
from .environment import Environment
from .exceptions import TemplateAssertionError
from .exceptions import TemplateSyntaxError
from .runtime import concat
from .runtime import Context
from .runtime import Undefined
from .utils import import_string
from .utils import pass_context
if t.TYPE_CHECKING:
	import typing_extensions as te;from .lexer import Token,TokenStream;from .parser import Parser
	class _TranslationsBasic(te.Protocol):
		def gettext(A,message):...
		def ngettext(A,singular,plural,n):0
	class _TranslationsContext(_TranslationsBasic):
		def pgettext(A,context,message):...
		def npgettext(A,context,singular,plural,n):...
	_SupportedTranslations=t.Union[_TranslationsBasic,_TranslationsContext]
GETTEXT_FUNCTIONS='_',_F,_I,_G,_H
_ws_re=re.compile('\\s*\\n\\s*')
class Extension:
	identifier:0
	def __init_subclass__(A):A.identifier=f"{A.__module__}.{A.__name__}"
	tags=set();priority=100
	def __init__(A,environment):A.environment=environment
	def bind(B,environment):A=t.cast(Extension,object.__new__(B.__class__));A.__dict__.update(B.__dict__);A.environment=environment;return A
	def preprocess(A,source,name,filename=_A):return source
	def filter_stream(A,stream):return stream
	def parse(A,parser):raise NotImplementedError()
	def attr(A,name,lineno=_A):return nodes.ExtensionAttribute(A.identifier,name,lineno=lineno)
	def call_method(D,name,args=_A,kwargs=_A,dyn_args=_A,dyn_kwargs=_A,lineno=_A):
		C=lineno;B=kwargs;A=args
		if A is _A:A=[]
		if B is _A:B=[]
		return nodes.Call(D.attr(name,lineno=C),A,B,dyn_args,dyn_kwargs,lineno=C)
@pass_context
def _gettext_alias(__context,*B,**C):A=__context;return A.call(A.resolve(_F),*(B),**C)
def _make_new_gettext(func):
	@pass_context
	def A(__context,__string,**C):
		B=__context;A=B.call(func,__string)
		if B.eval_ctx.autoescape:A=Markup(A)
		return A%C
	return A
def _make_new_ngettext(func):
	@pass_context
	def A(__context,__singular,__plural,__num,**D):
		C=__num;B=__context;D.setdefault(_C,C);A=B.call(func,__singular,__plural,C)
		if B.eval_ctx.autoescape:A=Markup(A)
		return A%D
	return A
def _make_new_pgettext(func):
	@pass_context
	def A(__context,__string_ctx,__string,**D):
		C=__string_ctx;B=__context;D.setdefault(_J,C);A=B.call(func,C,__string)
		if B.eval_ctx.autoescape:A=Markup(A)
		return A%D
	return A
def _make_new_npgettext(func):
	@pass_context
	def A(__context,__string_ctx,__singular,__plural,__num,**A):
		E=__num;D=__string_ctx;C=__context;A.setdefault(_J,D);A.setdefault(_C,E);B=C.call(func,D,__singular,__plural,E)
		if C.eval_ctx.autoescape:B=Markup(B)
		return B%A
	return A
class InternationalizationExtension(Extension):
	tags={'trans'}
	def __init__(A,environment):B=environment;super().__init__(B);B.globals['_']=_gettext_alias;B.extend(install_gettext_translations=A._install,install_null_translations=A._install_null,install_gettext_callables=A._install_callables,uninstall_gettext_translations=A._uninstall,extract_translations=A._extract,newstyle_gettext=_D)
	def _install(D,translations,newstyle=_A):
		A=translations;B=getattr(A,'ugettext',_A)
		if B is _A:B=A.gettext
		C=getattr(A,'ungettext',_A)
		if C is _A:C=A.ngettext
		E=getattr(A,_G,_A);F=getattr(A,_H,_A);D._install_callables(B,C,newstyle=newstyle,pgettext=E,npgettext=F)
	def _install_null(D,newstyle=_A):
		import gettext as E;A=E.NullTranslations()
		if hasattr(A,_G):B=A.pgettext
		else:
			def B(c,s):return s
		if hasattr(A,_H):C=A.npgettext
		else:
			def C(c,s,p,n):return s if n==1 else p
		D._install_callables(gettext=A.gettext,ngettext=A.ngettext,newstyle=newstyle,pgettext=B,npgettext=C)
	def _install_callables(C,gettext,ngettext,newstyle=_A,pgettext=_A,npgettext=_A):
		F=newstyle;E=ngettext;D=gettext;B=npgettext;A=pgettext
		if F is not _A:C.environment.newstyle_gettext=F
		if C.environment.newstyle_gettext:
			D=_make_new_gettext(D);E=_make_new_ngettext(E)
			if A is not _A:A=_make_new_pgettext(A)
			if B is not _A:B=_make_new_npgettext(B)
		C.environment.globals.update(gettext=D,ngettext=E,pgettext=A,npgettext=B)
	def _uninstall(A,translations):
		for B in (_F,_I,_G,_H):A.environment.globals.pop(B,_A)
	def _extract(B,source,gettext_functions=GETTEXT_FUNCTIONS):
		A=source
		if isinstance(A,str):A=B.environment.parse(A)
		return extract_from_ast(A,gettext_functions)
	def parse(E,parser):
		S='_trans';L='block_end';A=parser;R=next(A.stream).lineno;H=_D;C=_A;M=_A;D={};F=_A
		while A.stream.current.type!=L:
			if D:A.stream.expect('comma')
			if A.stream.skip_if('colon'):break
			B=A.stream.expect(_K)
			if B.value in D:A.fail(f"translatable variable {B.value!r} defined twice.",B.lineno,exc=TemplateAssertionError)
			if A.stream.current.type=='assign':next(A.stream);D[B.value]=I=A.parse_expression()
			elif F is _A and B.value in(_L,'notrimmed'):F=B.value==_L;continue
			else:D[B.value]=I=nodes.Name(B.value,_E)
			if C is _A:
				if isinstance(I,nodes.Call):C=nodes.Name(S,_E);D[B.value]=C;M=nodes.Assign(nodes.Name(S,'store'),I)
				else:C=I
				H=B.value==_C
		A.stream.expect(L);G=_A;N=_D;J=set();K,O=E._parse_block(A,_B)
		if K:
			J.update(K)
			if C is _A:C=nodes.Name(K[0],_E);H=K[0]==_C
		if A.stream.current.test(_M):
			N=_B;next(A.stream)
			if A.stream.current.type!=L:
				B=A.stream.expect(_K)
				if B.value not in D:A.fail(f"unknown variable {B.value!r} for pluralization",B.lineno,exc=TemplateAssertionError)
				C=D[B.value];H=B.value==_C
			A.stream.expect(L);T,G=E._parse_block(A,_D);next(A.stream);J.update(T)
		else:next(A.stream)
		for P in J:
			if P not in D:D[P]=nodes.Name(P,_E)
		if not N:C=_A
		elif C is _A:A.fail('pluralize without variables',R)
		if F is _A:F=E.environment.policies[_N]
		if F:
			O=E._trim_whitespace(O)
			if G:G=E._trim_whitespace(G)
		Q=E._make_node(O,G,D,C,bool(J),H and N);Q.set_lineno(R)
		if M is not _A:return[M,Q]
		else:return Q
	def _trim_whitespace(A,string,_ws_re=_ws_re):return _ws_re.sub(' ',string.strip())
	def _parse_block(E,parser,allow_pluralize):
		A=parser;C=[];B=[]
		while _B:
			if A.stream.current.type=='data':B.append(A.stream.current.value.replace('%','%%'));next(A.stream)
			elif A.stream.current.type=='variable_begin':next(A.stream);D=A.stream.expect(_K).value;C.append(D);B.append(f"%({D})s");A.stream.expect('variable_end')
			elif A.stream.current.type=='block_begin':
				next(A.stream)
				if A.stream.current.test('name:endtrans'):break
				elif A.stream.current.test(_M):
					if allow_pluralize:break
					A.fail('a translatable section can have only one pluralize section')
				A.fail('control structures in translatable sections are not allowed')
			elif A.stream.eos:A.fail('unclosed translation block')
			else:raise RuntimeError('internal parser error')
		return C,concat(B)
	def _make_node(H,singular,plural,variables,plural_expr,vars_referenced,num_called_num):
		E=plural_expr;D=variables;C=plural;B=singular;F=H.environment.newstyle_gettext;A:0
		if not vars_referenced and not F:
			B=B.replace('%%','%')
			if C:C=C.replace('%%','%')
		if E is _A:I=nodes.Name(_F,_E);A=nodes.Call(I,[nodes.Const(B)],[],_A,_A)
		else:J=nodes.Name(_I,_E);A=nodes.Call(J,[nodes.Const(B),nodes.Const(C),E],[],_A,_A)
		if F:
			for (G,K) in D.items():
				if num_called_num and G==_C:continue
				A.kwargs.append(nodes.Keyword(G,K))
		else:
			A=nodes.MarkSafeIfAutoescape(A)
			if D:A=nodes.Mod(A,nodes.Dict([nodes.Pair(nodes.Const(A),B)for(A,B)in D.items()]))
		return nodes.Output([A])
class ExprStmtExtension(Extension):
	tags={'do'}
	def parse(C,parser):A=parser;B=nodes.ExprStmt(lineno=next(A.stream).lineno);B.node=A.parse_tuple();return B
class LoopControlExtension(Extension):
	tags={'break','continue'}
	def parse(B,parser):
		A=next(parser.stream)
		if A.value=='break':return nodes.Break(lineno=A.lineno)
		return nodes.Continue(lineno=A.lineno)
class WithExtension(Extension):
	def __init__(A,environment):super().__init__(environment);warnings.warn("The 'with' extension is deprecated and will be removed in Jinja 3.1. This is built in now.",DeprecationWarning,stacklevel=3)
class AutoEscapeExtension(Extension):
	def __init__(A,environment):super().__init__(environment);warnings.warn("The 'autoescape' extension is deprecated and will be removed in Jinja 3.1. This is built in now.",DeprecationWarning,stacklevel=3)
class DebugExtension(Extension):
	tags={'debug'}
	def parse(B,parser):A=parser.stream.expect('name:debug').lineno;C=nodes.ContextReference();D=B.call_method('_render',[C],lineno=A);return nodes.Output([D],lineno=A)
	def _render(A,context):B={_J:context.get_all(),'filters':sorted(A.environment.filters.keys()),'tests':sorted(A.environment.tests.keys())};return pprint.pformat(B,depth=3,compact=_B)
def extract_from_ast(ast,gettext_functions=GETTEXT_FUNCTIONS,babel_style=_B):
	C:0
	for B in ast.find_all(nodes.Call):
		if not isinstance(B.node,nodes.Name)or B.node.name not in gettext_functions:continue
		A=[]
		for D in B.args:
			if isinstance(D,nodes.Const)and isinstance(D.value,str):A.append(D.value)
			else:A.append(_A)
		for E in B.kwargs:A.append(_A)
		if B.dyn_args is not _A:A.append(_A)
		if B.dyn_kwargs is not _A:A.append(_A)
		if not babel_style:
			C=tuple((B for B in A if B is not _A))
			if not C:continue
		elif len(A)==1:C=A[0]
		else:C=tuple(A)
		yield(B.lineno,B.node.name,C)
class _CommentFinder:
	def __init__(A,tokens,comment_tags):A.tokens=tokens;A.comment_tags=comment_tags;A.offset=0;A.last_lineno=0
	def find_backwards(A,offset):
		B=offset
		try:
			for (G,C,D) in reversed(A.tokens[A.offset:B]):
				if C in('comment','linecomment'):
					try:E,F=D.split(_A,1)
					except ValueError:continue
					if E in A.comment_tags:return[F.rstrip()]
			return[]
		finally:A.offset=B
	def find_comments(A,lineno):
		B=lineno
		if not A.comment_tags or A.last_lineno>B:return[]
		for (C,(D,E,E)) in enumerate(A.tokens[A.offset:]):
			if D>B:return A.find_backwards(A.offset+C)
		return A.find_backwards(len(A.tokens))
def babel_extract(fileobj,keywords,comment_tags,options):
	A=options;D={}
	for E in A.get('extensions','').split(','):
		E=E.strip()
		if not E:continue
		D[import_string(E)]=_A
	if InternationalizationExtension not in D:D[InternationalizationExtension]=_A
	def B(options,key,default=_D):return options.get(key,str(default)).lower()in{'1','on','yes','true'}
	H=B(A,'silent',_B);C=Environment(A.get('block_start_string',defaults.BLOCK_START_STRING),A.get('block_end_string',defaults.BLOCK_END_STRING),A.get('variable_start_string',defaults.VARIABLE_START_STRING),A.get('variable_end_string',defaults.VARIABLE_END_STRING),A.get('comment_start_string',defaults.COMMENT_START_STRING),A.get('comment_end_string',defaults.COMMENT_END_STRING),A.get('line_statement_prefix')or defaults.LINE_STATEMENT_PREFIX,A.get('line_comment_prefix')or defaults.LINE_COMMENT_PREFIX,B(A,'trim_blocks',defaults.TRIM_BLOCKS),B(A,'lstrip_blocks',defaults.LSTRIP_BLOCKS),defaults.NEWLINE_SEQUENCE,B(A,'keep_trailing_newline',defaults.KEEP_TRAILING_NEWLINE),tuple(D),cache_size=0,auto_reload=_D)
	if B(A,_L):C.policies[_N]=_B
	if B(A,'newstyle_gettext'):C.newstyle_gettext=_B
	F=fileobj.read().decode(A.get('encoding','utf-8'))
	try:I=C.parse(F);J=list(C.lex(C.preprocess(F)))
	except TemplateSyntaxError:
		if not H:raise
		return
	K=_CommentFinder(J,comment_tags)
	for (G,L,M) in extract_from_ast(I,keywords):yield(G,L,M,K.find_comments(G))
i18n=InternationalizationExtension
do=ExprStmtExtension
loopcontrols=LoopControlExtension
with_=WithExtension
autoescape=AutoEscapeExtension
debug=DebugExtension