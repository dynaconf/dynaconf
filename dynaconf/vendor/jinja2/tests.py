_B=False
_A=True
import operator,typing as t
from collections import abc
from numbers import Number
from .runtime import Undefined
from .utils import pass_environment
if t.TYPE_CHECKING:from .environment import Environment
def test_odd(value):return value%2==1
def test_even(value):return value%2==0
def test_divisibleby(value,num):return value%num==0
def test_defined(value):return not isinstance(value,Undefined)
def test_undefined(value):return isinstance(value,Undefined)
@pass_environment
def test_filter(env,value):return value in env.filters
@pass_environment
def test_test(env,value):return value in env.tests
def test_none(value):return value is None
def test_boolean(value):A=value;return A is _A or A is _B
def test_false(value):return value is _B
def test_true(value):return value is _A
def test_integer(value):A=value;return isinstance(A,int)and A is not _A and A is not _B
def test_float(value):return isinstance(value,float)
def test_lower(value):return str(value).islower()
def test_upper(value):return str(value).isupper()
def test_string(value):return isinstance(value,str)
def test_mapping(value):return isinstance(value,abc.Mapping)
def test_number(value):return isinstance(value,Number)
def test_sequence(value):
	A=value
	try:len(A);A.__getitem__
	except Exception:return _B
	return _A
def test_sameas(value,other):return value is other
def test_iterable(value):
	try:iter(value)
	except TypeError:return _B
	return _A
def test_escaped(value):return hasattr(value,'__html__')
def test_in(value,seq):return value in seq
TESTS={'odd':test_odd,'even':test_even,'divisibleby':test_divisibleby,'defined':test_defined,'undefined':test_undefined,'filter':test_filter,'test':test_test,'none':test_none,'boolean':test_boolean,'false':test_false,'true':test_true,'integer':test_integer,'float':test_float,'lower':test_lower,'upper':test_upper,'string':test_string,'mapping':test_mapping,'number':test_number,'sequence':test_sequence,'iterable':test_iterable,'callable':callable,'sameas':test_sameas,'escaped':test_escaped,'in':test_in,'==':operator.eq,'eq':operator.eq,'equalto':operator.eq,'!=':operator.ne,'ne':operator.ne,'>':operator.gt,'gt':operator.gt,'greaterthan':operator.gt,'ge':operator.ge,'>=':operator.ge,'<':operator.lt,'lt':operator.lt,'lessthan':operator.lt,'<=':operator.le,'le':operator.le}