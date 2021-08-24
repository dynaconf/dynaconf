_F='Assignment ({}) attempted, but this is ignored'
_E=False
_D='help'
_C=True
_B='__len__'
_A=None
import ast,operator as op,sys,warnings
from random import random
PYTHON3=sys.version_info[0]==3
MAX_STRING_LENGTH=100000
MAX_COMPREHENSION_LENGTH=10000
MAX_POWER=4000000
DISALLOW_PREFIXES=['_','func_']
DISALLOW_METHODS=['format','format_map','mro']
DISALLOW_FUNCTIONS={type,isinstance,eval,getattr,setattr,repr,compile,open}
if hasattr(__builtins__,_D)or hasattr(__builtins__,'__contains__')and _D in __builtins__:DISALLOW_FUNCTIONS.add(help)
if PYTHON3:exec('DISALLOW_FUNCTIONS.add(exec)')
class InvalidExpression(Exception):0
class FunctionNotDefined(InvalidExpression):
	def __init__(self,func_name,expression):self.message="Function '{0}' not defined, for expression '{1}'.".format(func_name,expression);setattr(self,'func_name',func_name);self.expression=expression;super(InvalidExpression,self).__init__(self.message)
class NameNotDefined(InvalidExpression):
	def __init__(self,name,expression):self.name=name;self.message="'{0}' is not defined for expression '{1}'".format(name,expression);self.expression=expression;super(InvalidExpression,self).__init__(self.message)
class AttributeDoesNotExist(InvalidExpression):
	def __init__(self,attr,expression):self.message="Attribute '{0}' does not exist in expression '{1}'".format(attr,expression);self.attr=attr;self.expression=expression
class FeatureNotAvailable(InvalidExpression):0
class NumberTooHigh(InvalidExpression):0
class IterableTooLong(InvalidExpression):0
class AssignmentAttempted(UserWarning):0
def random_int(top):return int(random()*top)
def safe_power(a,b):
	if abs(a)>MAX_POWER or abs(b)>MAX_POWER:raise NumberTooHigh("Sorry! I don't want to evaluate {0} ** {1}".format(a,b))
	return a**b
def safe_mult(a,b):
	A='Sorry, I will not evalute something that long.'
	if hasattr(a,_B)and b*len(a)>MAX_STRING_LENGTH:raise IterableTooLong(A)
	if hasattr(b,_B)and a*len(b)>MAX_STRING_LENGTH:raise IterableTooLong(A)
	return a*b
def safe_add(a,b):
	if hasattr(a,_B)and hasattr(b,_B):
		if len(a)+len(b)>MAX_STRING_LENGTH:raise IterableTooLong('Sorry, adding those two together would make something too long.')
	return a+b
DEFAULT_OPERATORS={ast.Add:safe_add,ast.Sub:op.sub,ast.Mult:safe_mult,ast.Div:op.truediv,ast.FloorDiv:op.floordiv,ast.Pow:safe_power,ast.Mod:op.mod,ast.Eq:op.eq,ast.NotEq:op.ne,ast.Gt:op.gt,ast.Lt:op.lt,ast.GtE:op.ge,ast.LtE:op.le,ast.Not:op.not_,ast.USub:op.neg,ast.UAdd:op.pos,ast.In:lambda x,y:op.contains(y,x),ast.NotIn:lambda x,y:not op.contains(y,x),ast.Is:lambda x,y:x is y,ast.IsNot:lambda x,y:x is not y}
DEFAULT_FUNCTIONS={'rand':random,'randint':random_int,'int':int,'float':float,'str':str if PYTHON3 else unicode}
DEFAULT_NAMES={'True':_C,'False':_E,'None':_A}
ATTR_INDEX_FALLBACK=_C
class SimpleEval:
	expr=''
	def __init__(self,operators=_A,functions=_A,names=_A):
		if not operators:operators=DEFAULT_OPERATORS.copy()
		if not functions:functions=DEFAULT_FUNCTIONS.copy()
		if not names:names=DEFAULT_NAMES.copy()
		self.operators=operators;self.functions=functions;self.names=names;self.nodes={ast.Expr:self._eval_expr,ast.Assign:self._eval_assign,ast.AugAssign:self._eval_aug_assign,ast.Import:self._eval_import,ast.Num:self._eval_num,ast.Str:self._eval_str,ast.Name:self._eval_name,ast.UnaryOp:self._eval_unaryop,ast.BinOp:self._eval_binop,ast.BoolOp:self._eval_boolop,ast.Compare:self._eval_compare,ast.IfExp:self._eval_ifexp,ast.Call:self._eval_call,ast.keyword:self._eval_keyword,ast.Subscript:self._eval_subscript,ast.Attribute:self._eval_attribute,ast.Index:self._eval_index,ast.Slice:self._eval_slice}
		if hasattr(ast,'NameConstant'):self.nodes[ast.NameConstant]=self._eval_constant
		if hasattr(ast,'JoinedStr'):self.nodes[ast.JoinedStr]=self._eval_joinedstr;self.nodes[ast.FormattedValue]=self._eval_formattedvalue
		if hasattr(ast,'Constant'):self.nodes[ast.Constant]=self._eval_constant
		self.ATTR_INDEX_FALLBACK=ATTR_INDEX_FALLBACK
		for f in self.functions.values():
			if f in DISALLOW_FUNCTIONS:raise FeatureNotAvailable('This function {} is a really bad idea.'.format(f))
	def eval(self,expr):self.expr=expr;return self._eval(ast.parse(expr.strip()).body[0])
	def _eval(self,node):
		try:handler=self.nodes[type(node)]
		except KeyError:raise FeatureNotAvailable('Sorry, {0} is not available in this evaluator'.format(type(node).__name__))
		return handler(node)
	def _eval_expr(self,node):return self._eval(node.value)
	def _eval_assign(self,node):warnings.warn(_F.format(self.expr),AssignmentAttempted);return self._eval(node.value)
	def _eval_aug_assign(self,node):warnings.warn(_F.format(self.expr),AssignmentAttempted);return self._eval(node.value)
	def _eval_import(self,node):raise FeatureNotAvailable("Sorry, 'import' is not allowed.");return self._eval(node.value)
	@staticmethod
	def _eval_num(node):return node.n
	@staticmethod
	def _eval_str(node):
		if len(node.s)>MAX_STRING_LENGTH:raise IterableTooLong('String Literal in statement is too long! ({0}, when {1} is max)'.format(len(node.s),MAX_STRING_LENGTH))
		return node.s
	@staticmethod
	def _eval_constant(node):
		if hasattr(node.value,_B)and len(node.value)>MAX_STRING_LENGTH:raise IterableTooLong('Literal in statement is too long! ({0}, when {1} is max)'.format(len(node.value),MAX_STRING_LENGTH))
		return node.value
	def _eval_unaryop(self,node):return self.operators[type(node.op)](self._eval(node.operand))
	def _eval_binop(self,node):return self.operators[type(node.op)](self._eval(node.left),self._eval(node.right))
	def _eval_boolop(self,node):
		if isinstance(node.op,ast.And):
			vout=_E
			for value in node.values:
				vout=self._eval(value)
				if not vout:return vout
			return vout
		elif isinstance(node.op,ast.Or):
			for value in node.values:
				vout=self._eval(value)
				if vout:return vout
			return vout
	def _eval_compare(self,node):
		right=self._eval(node.left);to_return=_C
		for (operation,comp) in zip(node.ops,node.comparators):
			if not to_return:break
			left=right;right=self._eval(comp);to_return=self.operators[type(operation)](left,right)
		return to_return
	def _eval_ifexp(self,node):return self._eval(node.body)if self._eval(node.test)else self._eval(node.orelse)
	def _eval_call(self,node):
		if isinstance(node.func,ast.Attribute):func=self._eval(node.func)
		else:
			try:func=self.functions[node.func.id]
			except KeyError:raise FunctionNotDefined(node.func.id,self.expr)
			except AttributeError as e:raise FeatureNotAvailable('Lambda Functions not implemented')
			if func in DISALLOW_FUNCTIONS:raise FeatureNotAvailable('This function is forbidden')
		return func(*(self._eval(a)for a in node.args),**dict((self._eval(k)for k in node.keywords)))
	def _eval_keyword(self,node):return node.arg,self._eval(node.value)
	def _eval_name(self,node):
		try:
			if hasattr(self.names,'__getitem__'):return self.names[node.id]
			elif callable(self.names):return self.names(node)
			else:raise InvalidExpression('Trying to use name (variable) "{0}" when no "names" defined for evaluator'.format(node.id))
		except KeyError:
			if node.id in self.functions:return self.functions[node.id]
			raise NameNotDefined(node.id,self.expr)
	def _eval_subscript(self,node):
		container=self._eval(node.value);key=self._eval(node.slice)
		try:return container[key]
		except KeyError:raise
	def _eval_attribute(self,node):
		for prefix in DISALLOW_PREFIXES:
			if node.attr.startswith(prefix):raise FeatureNotAvailable('Sorry, access to __attributes  or func_ attributes is not available. ({0})'.format(node.attr))
		if node.attr in DISALLOW_METHODS:raise FeatureNotAvailable('Sorry, this method is not available. ({0})'.format(node.attr))
		node_evaluated=self._eval(node.value)
		try:return getattr(node_evaluated,node.attr)
		except (AttributeError,TypeError):pass
		if self.ATTR_INDEX_FALLBACK:
			try:return node_evaluated[node.attr]
			except (KeyError,TypeError):pass
		raise AttributeDoesNotExist(node.attr,self.expr)
	def _eval_index(self,node):return self._eval(node.value)
	def _eval_slice(self,node):
		lower=upper=step=_A
		if node.lower is not _A:lower=self._eval(node.lower)
		if node.upper is not _A:upper=self._eval(node.upper)
		if node.step is not _A:step=self._eval(node.step)
		return slice(lower,upper,step)
	def _eval_joinedstr(self,node):
		length=0;evaluated_values=[]
		for n in node.values:
			val=str(self._eval(n))
			if len(val)+length>MAX_STRING_LENGTH:raise IterableTooLong('Sorry, I will not evaluate something this long.')
			evaluated_values.append(val)
		return ''.join(evaluated_values)
	def _eval_formattedvalue(self,node):
		if node.format_spec:fmt='{:'+self._eval(node.format_spec)+'}';return fmt.format(self._eval(node.value))
		return self._eval(node.value)
class EvalWithCompoundTypes(SimpleEval):
	def __init__(self,operators=_A,functions=_A,names=_A):super(EvalWithCompoundTypes,self).__init__(operators,functions,names);self.functions.update(list=list,tuple=tuple,dict=dict,set=set);self.nodes.update({ast.Dict:self._eval_dict,ast.Tuple:self._eval_tuple,ast.List:self._eval_list,ast.Set:self._eval_set,ast.ListComp:self._eval_comprehension,ast.GeneratorExp:self._eval_comprehension})
	def eval(self,expr):self._max_count=0;return super(EvalWithCompoundTypes,self).eval(expr)
	def _eval_dict(self,node):return{self._eval(k):self._eval(v)for(k,v)in zip(node.keys,node.values)}
	def _eval_tuple(self,node):return tuple((self._eval(x)for x in node.elts))
	def _eval_list(self,node):return list((self._eval(x)for x in node.elts))
	def _eval_set(self,node):return set((self._eval(x)for x in node.elts))
	def _eval_comprehension(self,node):
		to_return=[];extra_names={};previous_name_evaller=self.nodes[ast.Name]
		def eval_names_extra(node):
			if node.id in extra_names:return extra_names[node.id]
			return previous_name_evaller(node)
		self.nodes.update({ast.Name:eval_names_extra})
		def recurse_targets(target,value):
			if isinstance(target,ast.Name):extra_names[target.id]=value
			else:
				for (t,v) in zip(target.elts,value):recurse_targets(t,v)
		def do_generator(gi=0):
			g=node.generators[gi]
			for i in self._eval(g.iter):
				self._max_count+=1
				if self._max_count>MAX_COMPREHENSION_LENGTH:raise IterableTooLong('Comprehension generates too many elements')
				recurse_targets(g.target,i)
				if all((self._eval(iff)for iff in g.ifs)):
					if len(node.generators)>gi+1:do_generator(gi+1)
					else:to_return.append(self._eval(node.elt))
		try:do_generator()
		finally:self.nodes.update({ast.Name:previous_name_evaller})
		return to_return
def simple_eval(expr,operators=_A,functions=_A,names=_A):s=SimpleEval(operators=operators,functions=functions,names=names);return s.eval(expr)