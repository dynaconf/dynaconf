_H='getint'
_G='getfloat'
_F='getboolean'
_E='list'
_D='float'
_C='int'
_B='bool'
_A=None
from dynaconf.vendor.box.box import Box
class ConfigBox(Box):
	_protected_keys=dir(Box)+[_B,_C,_D,_E,_F,_G,_H]
	def __getattr__(A,item):
		try:return super().__getattr__(item)
		except AttributeError:return super().__getattr__(item.lower())
	def __dir__(A):return super().__dir__()+[_B,_C,_D,_E,_F,_G,_H]
	def bool(C,item,default=_A):
		E=False;B=default;A=item
		try:A=C.__getattr__(A)
		except AttributeError as D:
			if B is not _A:return B
			raise D
		if isinstance(A,(bool,int)):return bool(A)
		if isinstance(A,str)and A.lower()in('n','no','false','f','0'):return E
		return True if A else E
	def int(C,item,default=_A):
		B=default;A=item
		try:A=C.__getattr__(A)
		except AttributeError as D:
			if B is not _A:return B
			raise D
		return int(A)
	def float(C,item,default=_A):
		B=default;A=item
		try:A=C.__getattr__(A)
		except AttributeError as D:
			if B is not _A:return B
			raise D
		return float(A)
	def list(E,item,default=_A,spliter=',',strip=True,mod=_A):
		C=strip;B=default;A=item
		try:A=E.__getattr__(A)
		except AttributeError as F:
			if B is not _A:return B
			raise F
		if C:A=A.lstrip('[').rstrip(']')
		D=[B.strip()if C else B for B in A.split(spliter)]
		if mod:return list(map(mod,D))
		return D
	def getboolean(A,item,default=_A):return A.bool(item,default)
	def getint(A,item,default=_A):return A.int(item,default)
	def getfloat(A,item,default=_A):return A.float(item,default)
	def __repr__(A):return '<ConfigBox: {0}>'.format(str(A.to_dict()))
	def copy(A):return ConfigBox(super().copy())
	def __copy__(A):return ConfigBox(super().copy())