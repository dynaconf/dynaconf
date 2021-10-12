import typing as t
from .  import nodes
from .visitor import NodeTransformer
if t.TYPE_CHECKING:from .environment import Environment
def optimize(node,environment):A=Optimizer(environment);return t.cast(nodes.Node,A.visit(node))
class Optimizer(NodeTransformer):
	def __init__(A,environment):A.environment=environment
	def generic_visit(C,node,*B,**D):
		A=node;A=super().generic_visit(A,*(B),**D)
		if isinstance(A,nodes.Expr):
			try:return nodes.Const.from_untrusted(A.as_const(B[0]if B else None),lineno=A.lineno,environment=C.environment)
			except nodes.Impossible:pass
		return A