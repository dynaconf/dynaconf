import typing as t
from .  import nodes
from .compiler import CodeGenerator
from .compiler import Frame
if t.TYPE_CHECKING:from .environment import Environment
class TrackingCodeGenerator(CodeGenerator):
	def __init__(B,environment):A='<introspection>';super().__init__(environment,A,A);B.undeclared_identifiers=set()
	def write(A,x):0
	def enter_frame(A,frame):
		B=frame;super().enter_frame(B)
		for (E,(D,C)) in B.symbols.loads.items():
			if D=='resolve'and C not in A.environment.globals:A.undeclared_identifiers.add(C)
def find_undeclared_variables(ast):A=TrackingCodeGenerator(ast.environment);A.visit(ast);return A.undeclared_identifiers
_ref_types=nodes.Extends,nodes.FromImport,nodes.Import,nodes.Include
_RefType=t.Union[nodes.Extends,nodes.FromImport,nodes.Import,nodes.Include]
def find_referenced_templates(ast):
	C=None;A:0
	for D in ast.find_all(_ref_types):
		B=D.template
		if not isinstance(B,nodes.Const):
			if isinstance(B,(nodes.Tuple,nodes.List)):
				for A in B.items:
					if isinstance(A,nodes.Const):
						if isinstance(A.value,str):yield A.value
					else:yield C
			else:yield C
			continue
		if isinstance(B.value,str):yield B.value
		elif isinstance(D,nodes.Include)and isinstance(B.value,(tuple,list)):
			for A in B.value:
				if isinstance(A,str):yield A
		else:yield C