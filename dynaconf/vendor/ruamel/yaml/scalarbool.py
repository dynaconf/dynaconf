from __future__ import print_function,absolute_import,division,unicode_literals
_B=False
_A=None
from .anchor import Anchor
if _B:from typing import Text,Any,Dict,List
__all__=['ScalarBoolean']
class ScalarBoolean(int):
	def __new__(D,*E,**A):
		B=A.pop('anchor',_A);C=int.__new__(D,*E,**A)
		if B is not _A:C.yaml_set_anchor(B,always_dump=True)
		return C
	@property
	def anchor(self):
		A=self
		if not hasattr(A,Anchor.attrib):setattr(A,Anchor.attrib,Anchor())
		return getattr(A,Anchor.attrib)
	def yaml_anchor(A,any=_B):
		if not hasattr(A,Anchor.attrib):return _A
		if any or A.anchor.always_dump:return A.anchor
		return _A
	def yaml_set_anchor(A,value,always_dump=_B):A.anchor.value=value;A.anchor.always_dump=always_dump