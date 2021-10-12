_A=None
import typing as t
if t.TYPE_CHECKING:from .runtime import Undefined
class TemplateError(Exception):
	def __init__(A,message=_A):super().__init__(message)
	@property
	def message(self):return self.args[0]if self.args else _A
class TemplateNotFound(IOError,LookupError,TemplateError):
	message=_A
	def __init__(B,name,message=_A):
		C=message;A=name;IOError.__init__(B,A)
		if C is _A:
			from .runtime import Undefined as D
			if isinstance(A,D):A._fail_with_undefined_error()
			C=A
		B.message=C;B.name=A;B.templates=[A]
	def __str__(A):return str(A.message)
class TemplatesNotFound(TemplateNotFound):
	def __init__(E,names=(),message=_A):
		B=message;A=names
		if B is _A:
			from .runtime import Undefined as F;C=[]
			for D in A:
				if isinstance(D,F):C.append(D._undefined_message)
				else:C.append(D)
			G=', '.join(map(str,C));B=f"none of the templates given were found: {G}"
		super().__init__(A[-1]if A else _A,B);E.templates=list(A)
class TemplateSyntaxError(TemplateError):
	def __init__(A,message,lineno,name=_A,filename=_A):super().__init__(message);A.lineno=lineno;A.name=name;A.filename=filename;A.source=_A;A.translated=False
	def __str__(A):
		if A.translated:return t.cast(str,A.message)
		B=f"line {A.lineno}";C=A.filename or A.name
		if C:B=f'File "{C}", {B}'
		D=[t.cast(str,A.message),'  '+B]
		if A.source is not _A:
			try:E=A.source.splitlines()[A.lineno-1]
			except IndexError:pass
			else:D.append('    '+E.strip())
		return '\n'.join(D)
	def __reduce__(A):return A.__class__,(A.message,A.lineno,A.name,A.filename)
class TemplateAssertionError(TemplateSyntaxError):0
class TemplateRuntimeError(TemplateError):0
class UndefinedError(TemplateRuntimeError):0
class SecurityError(TemplateRuntimeError):0
class FilterArgumentError(TemplateRuntimeError):0