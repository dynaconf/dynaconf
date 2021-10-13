import typing as t
from .  import Markup
def escape(s):
	if hasattr(s,'__html__'):return Markup(s.__html__())
	return Markup(str(s).replace('&','&amp;').replace('>','&gt;').replace('<','&lt;').replace("'",'&#39;').replace('"','&#34;'))
def escape_silent(s):
	if s is None:return Markup()
	return escape(s)
def soft_str(s):
	if not isinstance(s,str):return str(s)
	return s
def soft_unicode(s):import warnings as A;A.warn("'soft_unicode' has been renamed to 'soft_str'. The old name will be removed in MarkupSafe 2.1.",DeprecationWarning,stacklevel=2);return soft_str(s)