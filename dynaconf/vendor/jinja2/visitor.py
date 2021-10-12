_A=None
import typing as t
from .nodes import Node
if t.TYPE_CHECKING:
	import typing_extensions as te
	class VisitCallable(te.Protocol):
		def __call__(A,node,*B,**C):...
class NodeVisitor:
	def get_visitor(A,node):return getattr(A,f"visit_{type(node).__name__}",_A)
	def visit(B,node,*C,**D):
		A=node;E=B.get_visitor(A)
		if E is not _A:return E(A,*(C),**D)
		return B.generic_visit(A,*(C),**D)
	def generic_visit(B,node,*C,**D):
		A=node
		for A in A.iter_child_nodes():B.visit(A,*(C),**D)
class NodeTransformer(NodeVisitor):
	def generic_visit(E,node,*F,**G):
		C=node
		for (H,B) in C.iter_fields():
			if isinstance(B,list):
				D=[]
				for A in B:
					if isinstance(A,Node):
						A=E.visit(A,*(F),**G)
						if A is _A:continue
						elif not isinstance(A,Node):D.extend(A);continue
					D.append(A)
				B[:]=D
			elif isinstance(B,Node):
				I=E.visit(B,*(F),**G)
				if I is _A:delattr(C,H)
				else:setattr(C,H,I)
		return C
	def visit_list(B,node,*C,**D):
		A=B.visit(node,*(C),**D)
		if not isinstance(A,list):return[A]
		return A