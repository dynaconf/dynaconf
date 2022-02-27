_F='root'
_E='comment'
_D='#bygroup'
_C=True
_B='#pop'
_A=None
import re,typing as t
from ast import literal_eval
from collections import deque
from sys import intern
from ._identifier import pattern as name_re
from .exceptions import TemplateSyntaxError
from .utils import LRUCache
if t.TYPE_CHECKING:import typing_extensions as te;from .environment import Environment
_lexer_cache=LRUCache(50)
whitespace_re=re.compile('\\s+')
newline_re=re.compile('(\\r\\n|\\r|\\n)')
string_re=re.compile('(\'([^\'\\\\]*(?:\\\\.[^\'\\\\]*)*)\'|"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)")',re.S)
integer_re=re.compile('\n    (\n        0b(_?[0-1])+ # binary\n    |\n        0o(_?[0-7])+ # octal\n    |\n        0x(_?[\\da-f])+ # hex\n    |\n        [1-9](_?\\d)* # decimal\n    |\n        0(_?0)* # decimal zero\n    )\n    ',re.IGNORECASE|re.VERBOSE)
float_re=re.compile("\n    (?<!\\.)  # doesn't start with a .\n    (\\d+_)*\\d+  # digits, possibly _ separated\n    (\n        (\\.(\\d+_)*\\d+)?  # optional fractional part\n        e[+\\-]?(\\d+_)*\\d+  # exponent part\n    |\n        \\.(\\d+_)*\\d+  # required fractional part\n    )\n    ",re.IGNORECASE|re.VERBOSE)
TOKEN_ADD=intern('add')
TOKEN_ASSIGN=intern('assign')
TOKEN_COLON=intern('colon')
TOKEN_COMMA=intern('comma')
TOKEN_DIV=intern('div')
TOKEN_DOT=intern('dot')
TOKEN_EQ=intern('eq')
TOKEN_FLOORDIV=intern('floordiv')
TOKEN_GT=intern('gt')
TOKEN_GTEQ=intern('gteq')
TOKEN_LBRACE=intern('lbrace')
TOKEN_LBRACKET=intern('lbracket')
TOKEN_LPAREN=intern('lparen')
TOKEN_LT=intern('lt')
TOKEN_LTEQ=intern('lteq')
TOKEN_MOD=intern('mod')
TOKEN_MUL=intern('mul')
TOKEN_NE=intern('ne')
TOKEN_PIPE=intern('pipe')
TOKEN_POW=intern('pow')
TOKEN_RBRACE=intern('rbrace')
TOKEN_RBRACKET=intern('rbracket')
TOKEN_RPAREN=intern('rparen')
TOKEN_SEMICOLON=intern('semicolon')
TOKEN_SUB=intern('sub')
TOKEN_TILDE=intern('tilde')
TOKEN_WHITESPACE=intern('whitespace')
TOKEN_FLOAT=intern('float')
TOKEN_INTEGER=intern('integer')
TOKEN_NAME=intern('name')
TOKEN_STRING=intern('string')
TOKEN_OPERATOR=intern('operator')
TOKEN_BLOCK_BEGIN=intern('block_begin')
TOKEN_BLOCK_END=intern('block_end')
TOKEN_VARIABLE_BEGIN=intern('variable_begin')
TOKEN_VARIABLE_END=intern('variable_end')
TOKEN_RAW_BEGIN=intern('raw_begin')
TOKEN_RAW_END=intern('raw_end')
TOKEN_COMMENT_BEGIN=intern('comment_begin')
TOKEN_COMMENT_END=intern('comment_end')
TOKEN_COMMENT=intern(_E)
TOKEN_LINESTATEMENT_BEGIN=intern('linestatement_begin')
TOKEN_LINESTATEMENT_END=intern('linestatement_end')
TOKEN_LINECOMMENT_BEGIN=intern('linecomment_begin')
TOKEN_LINECOMMENT_END=intern('linecomment_end')
TOKEN_LINECOMMENT=intern('linecomment')
TOKEN_DATA=intern('data')
TOKEN_INITIAL=intern('initial')
TOKEN_EOF=intern('eof')
operators={'+':TOKEN_ADD,'-':TOKEN_SUB,'/':TOKEN_DIV,'//':TOKEN_FLOORDIV,'*':TOKEN_MUL,'%':TOKEN_MOD,'**':TOKEN_POW,'~':TOKEN_TILDE,'[':TOKEN_LBRACKET,']':TOKEN_RBRACKET,'(':TOKEN_LPAREN,')':TOKEN_RPAREN,'{':TOKEN_LBRACE,'}':TOKEN_RBRACE,'==':TOKEN_EQ,'!=':TOKEN_NE,'>':TOKEN_GT,'>=':TOKEN_GTEQ,'<':TOKEN_LT,'<=':TOKEN_LTEQ,'=':TOKEN_ASSIGN,'.':TOKEN_DOT,':':TOKEN_COLON,'|':TOKEN_PIPE,',':TOKEN_COMMA,';':TOKEN_SEMICOLON}
reverse_operators={B:A for(A,B)in operators.items()}
assert len(operators)==len(reverse_operators),'operators dropped'
operator_re=re.compile(f"({'|'.join((re.escape(A)for A in sorted(operators,key=lambda x:-len(x))))})")
ignored_tokens=frozenset([TOKEN_COMMENT_BEGIN,TOKEN_COMMENT,TOKEN_COMMENT_END,TOKEN_WHITESPACE,TOKEN_LINECOMMENT_BEGIN,TOKEN_LINECOMMENT_END,TOKEN_LINECOMMENT])
ignore_if_empty=frozenset([TOKEN_WHITESPACE,TOKEN_DATA,TOKEN_COMMENT,TOKEN_LINECOMMENT])
def _describe_token_type(token_type):
	A=token_type
	if A in reverse_operators:return reverse_operators[A]
	return {TOKEN_COMMENT_BEGIN:'begin of comment',TOKEN_COMMENT_END:'end of comment',TOKEN_COMMENT:_E,TOKEN_LINECOMMENT:_E,TOKEN_BLOCK_BEGIN:'begin of statement block',TOKEN_BLOCK_END:'end of statement block',TOKEN_VARIABLE_BEGIN:'begin of print statement',TOKEN_VARIABLE_END:'end of print statement',TOKEN_LINESTATEMENT_BEGIN:'begin of line statement',TOKEN_LINESTATEMENT_END:'end of line statement',TOKEN_DATA:'template data / text',TOKEN_EOF:'end of template'}.get(A,A)
def describe_token(token):
	A=token
	if A.type==TOKEN_NAME:return A.value
	return _describe_token_type(A.type)
def describe_token_expr(expr):
	A=expr
	if':'in A:
		type,B=A.split(':',1)
		if type==TOKEN_NAME:return B
	else:type=A
	return _describe_token_type(type)
def count_newlines(value):return len(newline_re.findall(value))
def compile_rules(environment):
	A=environment;B=re.escape;C=[(len(A.comment_start_string),TOKEN_COMMENT_BEGIN,B(A.comment_start_string)),(len(A.block_start_string),TOKEN_BLOCK_BEGIN,B(A.block_start_string)),(len(A.variable_start_string),TOKEN_VARIABLE_BEGIN,B(A.variable_start_string))]
	if A.line_statement_prefix is not _A:C.append((len(A.line_statement_prefix),TOKEN_LINESTATEMENT_BEGIN,'^[ \\t\\v]*'+B(A.line_statement_prefix)))
	if A.line_comment_prefix is not _A:C.append((len(A.line_comment_prefix),TOKEN_LINECOMMENT_BEGIN,'(?:^|(?<=\\S))[^\\S\\r\\n]*'+B(A.line_comment_prefix)))
	return[A[1:]for A in sorted(C,reverse=_C)]
class Failure:
	def __init__(A,message,cls=TemplateSyntaxError):A.message=message;A.error_class=cls
	def __call__(A,lineno,filename):raise A.error_class(A.message,lineno,filename)
class Token(t.NamedTuple):
	lineno:int;type:str;value:str
	def __str__(A):return describe_token(A)
	def test(A,expr):
		B=expr
		if A.type==B:return _C
		if':'in B:return B.split(':',1)==[A.type,A.value]
		return False
	def test_any(A,*B):return any((A.test(C)for C in B))
class TokenStreamIterator:
	def __init__(A,stream):A.stream=stream
	def __iter__(A):return A
	def __next__(A):
		B=A.stream.current
		if B.type is TOKEN_EOF:A.stream.close();raise StopIteration
		next(A.stream);return B
class TokenStream:
	def __init__(A,generator,name,filename):A._iter=iter(generator);A._pushed=deque();A.name=name;A.filename=filename;A.closed=False;A.current=Token(1,TOKEN_INITIAL,'');next(A)
	def __iter__(A):return TokenStreamIterator(A)
	def __bool__(A):return bool(A._pushed)or A.current.type is not TOKEN_EOF
	@property
	def eos(self):return not self
	def push(A,token):A._pushed.append(token)
	def look(A):C=next(A);B=A.current;A.push(B);A.current=C;return B
	def skip(A,n=1):
		for B in range(n):next(A)
	def next_if(A,expr):
		if A.current.test(expr):return next(A)
		return _A
	def skip_if(A,expr):return A.next_if(expr)is not _A
	def __next__(A):
		B=A.current
		if A._pushed:A.current=A._pushed.popleft()
		elif A.current.type is not TOKEN_EOF:
			try:A.current=next(A._iter)
			except StopIteration:A.close()
		return B
	def close(A):A.current=Token(A.current.lineno,TOKEN_EOF,'');A._iter=iter(());A.closed=_C
	def expect(A,expr):
		B=expr
		if not A.current.test(B):
			B=describe_token_expr(B)
			if A.current.type is TOKEN_EOF:raise TemplateSyntaxError(f"unexpected end of template, expected {B!r}.",A.current.lineno,A.name,A.filename)
			raise TemplateSyntaxError(f"expected token {B!r}, got {describe_token(A.current)!r}",A.current.lineno,A.name,A.filename)
		return next(A)
def get_lexer(environment):
	A=environment;C=A.block_start_string,A.block_end_string,A.variable_start_string,A.variable_end_string,A.comment_start_string,A.comment_end_string,A.line_statement_prefix,A.line_comment_prefix,A.trim_blocks,A.lstrip_blocks,A.newline_sequence,A.keep_trailing_newline;B=_lexer_cache.get(C)
	if B is _A:_lexer_cache[C]=B=Lexer(A)
	return B
class OptionalLStrip(tuple):
	__slots__=()
	def __new__(A,*B,**C):return super().__new__(A,B)
class _Rule(t.NamedTuple):pattern:t.Pattern[str];tokens:t.Union[str,t.Tuple[str,...],t.Tuple[Failure]];command:t.Optional[str]
class Lexer:
	def __init__(D,environment):
		K='(.)';B=environment;E=re.escape
		def A(x):return re.compile(x,re.M|re.S)
		F=[_Rule(whitespace_re,TOKEN_WHITESPACE,_A),_Rule(float_re,TOKEN_FLOAT,_A),_Rule(integer_re,TOKEN_INTEGER,_A),_Rule(name_re,TOKEN_NAME,_A),_Rule(string_re,TOKEN_STRING,_A),_Rule(operator_re,TOKEN_OPERATOR,_A)];L=compile_rules(B);I=E(B.block_start_string);C=E(B.block_end_string);G=E(B.comment_end_string);J=E(B.variable_end_string);H='\\n?'if B.trim_blocks else'';D.lstrip_unless_re=A('[^ \\t]')if B.lstrip_blocks else _A;D.newline_sequence=B.newline_sequence;D.keep_trailing_newline=B.keep_trailing_newline;M=f"(?P<raw_begin>{I}(\\-|\\+|)\\s*raw\\s*(?:\\-{C}\\s*|{C}))";N='|'.join([M]+[f"(?P<{A}>{B}(\\-|\\+|))"for(A,B)in L]);D.rules={_F:[_Rule(A(f"(.*?)(?:{N})"),OptionalLStrip(TOKEN_DATA,_D),_D),_Rule(A('.+'),TOKEN_DATA,_A)],TOKEN_COMMENT_BEGIN:[_Rule(A(f"(.*?)((?:\\+{G}|\\-{G}\\s*|{G}{H}))"),(TOKEN_COMMENT,TOKEN_COMMENT_END),_B),_Rule(A(K),(Failure('Missing end of comment tag'),),_A)],TOKEN_BLOCK_BEGIN:[_Rule(A(f"(?:\\+{C}|\\-{C}\\s*|{C}{H})"),TOKEN_BLOCK_END,_B)]+F,TOKEN_VARIABLE_BEGIN:[_Rule(A(f"\\-{J}\\s*|{J}"),TOKEN_VARIABLE_END,_B)]+F,TOKEN_RAW_BEGIN:[_Rule(A(f"(.*?)((?:{I}(\\-|\\+|))\\s*endraw\\s*(?:\\+{C}|\\-{C}\\s*|{C}{H}))"),OptionalLStrip(TOKEN_DATA,TOKEN_RAW_END),_B),_Rule(A(K),(Failure('Missing end of raw directive'),),_A)],TOKEN_LINESTATEMENT_BEGIN:[_Rule(A('\\s*(\\n|$)'),TOKEN_LINESTATEMENT_END,_B)]+F,TOKEN_LINECOMMENT_BEGIN:[_Rule(A('(.*?)()(?=\\n|$)'),(TOKEN_LINECOMMENT,TOKEN_LINECOMMENT_END),_B)]}
	def _normalize_newlines(A,value):return newline_re.sub(A.newline_sequence,value)
	def tokenize(C,source,name=_A,filename=_A,state=_A):B=filename;A=name;D=C.tokeniter(source,A,B,state);return TokenStream(C.wrap(D,A,B),A,B)
	def wrap(E,stream,name=_A,filename=_A):
		F=filename
		for (D,A,B) in stream:
			if A in ignored_tokens:continue
			C=B
			if A==TOKEN_LINESTATEMENT_BEGIN:A=TOKEN_BLOCK_BEGIN
			elif A==TOKEN_LINESTATEMENT_END:A=TOKEN_BLOCK_END
			elif A in(TOKEN_RAW_BEGIN,TOKEN_RAW_END):continue
			elif A==TOKEN_DATA:C=E._normalize_newlines(B)
			elif A=='keyword':A=B
			elif A==TOKEN_NAME:
				C=B
				if not C.isidentifier():raise TemplateSyntaxError('Invalid character in identifier',D,name,F)
			elif A==TOKEN_STRING:
				try:C=E._normalize_newlines(B[1:-1]).encode('ascii','backslashreplace').decode('unicode-escape')
				except Exception as G:H=str(G).split(':')[-1].strip();raise TemplateSyntaxError(H,D,name,F) from G
			elif A==TOKEN_INTEGER:C=int(B.replace('_',''),0)
			elif A==TOKEN_FLOAT:C=literal_eval(B.replace('_',''))
			elif A==TOKEN_OPERATOR:A=operators[B]
			yield Token(D,A,C)
	def tokeniter(N,source,name,filename=_A,state=_A):
		S=name;P=state;O=filename;J=source;F='\n';T=newline_re.split(J)[::2]
		if not N.keep_trailing_newline and T[-1]=='':del T[-1]
		J=F.join(T);G=0;B=1;H=[_F]
		if P is not _A and P!=_F:assert P in('variable','block'),'invalid state';H.append(P+'_begin')
		X=N.rules[H[-1]];e=len(J);I=[];Y=N.lstrip_unless_re;U=0;Z=_C
		while _C:
			for (Q,D,R) in X:
				C=Q.match(J,G)
				if C is _A:continue
				if I and D in(TOKEN_VARIABLE_END,TOKEN_BLOCK_END,TOKEN_LINESTATEMENT_END):continue
				if isinstance(D,tuple):
					E=C.groups()
					if isinstance(D,OptionalLStrip):
						K=E[0];a=next((A for A in E[2::2]if A is not _A))
						if a=='-':b=K.rstrip();U=K[len(b):].count(F);E=[b,*E[1:]]
						elif a!='+'and Y is not _A and not C.groupdict().get(TOKEN_VARIABLE_BEGIN):
							V=K.rfind(F)+1
							if V>0 or Z:
								if not Y.search(K,V):E=[K[:V],*E[1:]]
					for (f,L) in enumerate(D):
						if L.__class__ is Failure:raise L(B,O)
						elif L==_D:
							for (W,M) in C.groupdict().items():
								if M is not _A:yield(B,W,M);B+=M.count(F);break
							else:raise RuntimeError(f"{Q!r} wanted to resolve the token dynamically but no group matched")
						else:
							A=E[f]
							if A or L not in ignore_if_empty:yield(B,L,A)
							B+=A.count(F)+U;U=0
				else:
					A=C.group()
					if D==TOKEN_OPERATOR:
						if A=='{':I.append('}')
						elif A=='(':I.append(')')
						elif A=='[':I.append(']')
						elif A in('}',')',']'):
							if not I:raise TemplateSyntaxError(f"unexpected '{A}'",B,S,O)
							c=I.pop()
							if c!=A:raise TemplateSyntaxError(f"unexpected '{A}', expected '{c}'",B,S,O)
					if A or D not in ignore_if_empty:yield(B,D,A)
					B+=A.count(F)
				Z=C.group()[-1:]==F;d=C.end()
				if R is not _A:
					if R==_B:H.pop()
					elif R==_D:
						for (W,M) in C.groupdict().items():
							if M is not _A:H.append(W);break
						else:raise RuntimeError(f"{Q!r} wanted to resolve the new state dynamically but no group matched")
					else:H.append(R)
					X=N.rules[H[-1]]
				elif d==G:raise RuntimeError(f"{Q!r} yielded empty string without stack change")
				G=d;break
			else:
				if G>=e:return
				raise TemplateSyntaxError(f"unexpected char {J[G]!r} at {G}",B,S,O)