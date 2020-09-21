from __future__ import print_function,absolute_import,division
_AD='expected the empty value, but found %r'
_AC='cannot find module %r (%s)'
_AB='expected non-empty name appended to the tag'
_AA='tag:yaml.org,2002:map'
_A9='tag:yaml.org,2002:seq'
_A8='tag:yaml.org,2002:set'
_A7='tag:yaml.org,2002:pairs'
_A6='tag:yaml.org,2002:omap'
_A5='tag:yaml.org,2002:timestamp'
_A4='tag:yaml.org,2002:binary'
_A3='tag:yaml.org,2002:float'
_A2='tag:yaml.org,2002:int'
_A1='tag:yaml.org,2002:bool'
_A0='tag:yaml.org,2002:null'
_z='could not determine a constructor for the tag %r'
_y='second'
_x='minute'
_w='day'
_v='month'
_u='year'
_t='failed to construct timestamp from "{}"'
_s='decodebytes'
_r='failed to convert base64 data into ascii: %s'
_q='.nan'
_p='.inf'
_o='expected a mapping or list of mappings for merging, but found %s'
_n='expected a mapping for merging, but found %s'
_m='                        Duplicate keys will become an error in future releases, and are errors\n                        by default when using the new API.\n                        '
_l='\n                        To suppress this check see:\n                           http://yaml.readthedocs.io/en/latest/api.html#duplicate-keys\n                        '
_k='tag:yaml.org,2002:merge'
_j='                    Duplicate keys will become an error in future releases, and are errors\n                    by default when using the new API.\n                    '
_i='\n                    To suppress this check see:\n                        http://yaml.readthedocs.io/en/latest/api.html#duplicate-keys\n                    '
_h='expected a sequence node, but found %s'
_g='expected a scalar node, but found %s'
_f='typ'
_e='while constructing a Python module'
_d='expected a single mapping item, but found %d items'
_c='expected a mapping of length 1, but found %s'
_b='expected a sequence, but found %s'
_a='failed to decode base64 data: %s'
_Z='tag:yaml.org,2002:value'
_Y='found duplicate key "{}"'
_X='found unhashable key'
_W='found unacceptable key (%s)'
_V='__setstate__'
_U='tz_hour'
_T='hour'
_S='ascii'
_R='tag:yaml.org,2002:str'
_Q='utf-8'
_P='expected a mapping node, but found %s'
_O='tz_minute'
_N='e'
_M='+-'
_L='while constructing an ordered map'
_K='tz_sign'
_J='-'
_I='fraction'
_H='.'
_G=':'
_F='0'
_E='while constructing a mapping'
_D='_'
_C=True
_B=False
_A=None
import datetime,base64,binascii,re,sys,types,warnings
from .error import MarkedYAMLError,MarkedYAMLFutureWarning,MantissaNoDotYAML1_1Warning
from .nodes import *
from .nodes import SequenceNode,MappingNode,ScalarNode
from .compat import utf8,builtins_module,to_str,PY2,PY3,text_type,nprint,nprintf,version_tnf
from .compat import ordereddict,Hashable,MutableSequence
from .compat import MutableMapping
from .comments import *
from .comments import CommentedMap,CommentedOrderedMap,CommentedSet,CommentedKeySeq,CommentedSeq,TaggedScalar,CommentedKeyMap
from .scalarstring import SingleQuotedScalarString,DoubleQuotedScalarString,LiteralScalarString,FoldedScalarString,PlainScalarString,ScalarString
from .scalarint import ScalarInt,BinaryInt,OctalInt,HexInt,HexCapsInt
from .scalarfloat import ScalarFloat
from .scalarbool import ScalarBoolean
from .timestamp import TimeStamp
from .util import RegExp
if _B:from typing import Any,Dict,List,Set,Generator,Union,Optional
__all__=['BaseConstructor','SafeConstructor','Constructor','ConstructorError','RoundTripConstructor']
class ConstructorError(MarkedYAMLError):0
class DuplicateKeyFutureWarning(MarkedYAMLFutureWarning):0
class DuplicateKeyError(MarkedYAMLFutureWarning):0
class BaseConstructor:
	yaml_constructors={};yaml_multi_constructors={}
	def __init__(self,preserve_quotes=_A,loader=_A):
		self.loader=loader
		if self.loader is not _A and getattr(self.loader,'_constructor',_A)is _A:self.loader._constructor=self
		self.loader=loader;self.yaml_base_dict_type=dict;self.yaml_base_list_type=list;self.constructed_objects={};self.recursive_objects={};self.state_generators=[];self.deep_construct=_B;self._preserve_quotes=preserve_quotes;self.allow_duplicate_keys=version_tnf((0,15,1),(0,16))
	@property
	def composer(self):
		if hasattr(self.loader,_f):return self.loader.composer
		try:return self.loader._composer
		except AttributeError:sys.stdout.write('slt {}\n'.format(type(self)));sys.stdout.write('slc {}\n'.format(self.loader._composer));sys.stdout.write('{}\n'.format(dir(self)));raise
	@property
	def resolver(self):
		if hasattr(self.loader,_f):return self.loader.resolver
		return self.loader._resolver
	def check_data(self):return self.composer.check_node()
	def get_data(self):
		if self.composer.check_node():return self.construct_document(self.composer.get_node())
	def get_single_data(self):
		node=self.composer.get_single_node()
		if node is not _A:return self.construct_document(node)
		return _A
	def construct_document(self,node):
		data=self.construct_object(node)
		while bool(self.state_generators):
			state_generators=self.state_generators;self.state_generators=[]
			for generator in state_generators:
				for _dummy in generator:0
		self.constructed_objects={};self.recursive_objects={};self.deep_construct=_B;return data
	def construct_object(self,node,deep=_B):
		if node in self.constructed_objects:return self.constructed_objects[node]
		if deep:old_deep=self.deep_construct;self.deep_construct=_C
		if node in self.recursive_objects:return self.recursive_objects[node]
		self.recursive_objects[node]=_A;data=self.construct_non_recursive_object(node);self.constructed_objects[node]=data;del self.recursive_objects[node]
		if deep:self.deep_construct=old_deep
		return data
	def construct_non_recursive_object(self,node,tag=_A):
		constructor=_A;tag_suffix=_A
		if tag is _A:tag=node.tag
		if tag in self.yaml_constructors:constructor=self.yaml_constructors[tag]
		else:
			for tag_prefix in self.yaml_multi_constructors:
				if tag.startswith(tag_prefix):tag_suffix=tag[len(tag_prefix):];constructor=self.yaml_multi_constructors[tag_prefix];break
			else:
				if _A in self.yaml_multi_constructors:tag_suffix=tag;constructor=self.yaml_multi_constructors[_A]
				elif _A in self.yaml_constructors:constructor=self.yaml_constructors[_A]
				elif isinstance(node,ScalarNode):constructor=self.__class__.construct_scalar
				elif isinstance(node,SequenceNode):constructor=self.__class__.construct_sequence
				elif isinstance(node,MappingNode):constructor=self.__class__.construct_mapping
		if tag_suffix is _A:data=constructor(self,node)
		else:data=constructor(self,tag_suffix,node)
		if isinstance(data,types.GeneratorType):
			generator=data;data=next(generator)
			if self.deep_construct:
				for _dummy in generator:0
			else:self.state_generators.append(generator)
		return data
	def construct_scalar(self,node):
		if not isinstance(node,ScalarNode):raise ConstructorError(_A,_A,_g%node.id,node.start_mark)
		return node.value
	def construct_sequence(self,node,deep=_B):
		if not isinstance(node,SequenceNode):raise ConstructorError(_A,_A,_h%node.id,node.start_mark)
		return[self.construct_object(child,deep=deep)for child in node.value]
	def construct_mapping(self,node,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_P%node.id,node.start_mark)
		total_mapping=self.yaml_base_dict_type()
		if getattr(node,'merge',_A)is not _A:todo=[(node.merge,_B),(node.value,_B)]
		else:todo=[(node.value,_C)]
		for (values,check) in todo:
			mapping=self.yaml_base_dict_type()
			for (key_node,value_node) in values:
				key=self.construct_object(key_node,deep=_C)
				if not isinstance(key,Hashable):
					if isinstance(key,list):key=tuple(key)
				if PY2:
					try:hash(key)
					except TypeError as exc:raise ConstructorError(_E,node.start_mark,_W%exc,key_node.start_mark)
				elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_X,key_node.start_mark)
				value=self.construct_object(value_node,deep=deep)
				if check:
					if self.check_mapping_key(node,key_node,mapping,key,value):mapping[key]=value
				else:mapping[key]=value
			total_mapping.update(mapping)
		return total_mapping
	def check_mapping_key(self,node,key_node,mapping,key,value):
		if key in mapping:
			if not self.allow_duplicate_keys:
				mk=mapping.get(key)
				if PY2:
					if isinstance(key,unicode):key=key.encode(_Q)
					if isinstance(value,unicode):value=value.encode(_Q)
					if isinstance(mk,unicode):mk=mk.encode(_Q)
				args=[_E,node.start_mark,'found duplicate key "{}" with value "{}" (original value: "{}")'.format(key,value,mk),key_node.start_mark,_i,_j]
				if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
				else:raise DuplicateKeyError(*args)
			return _B
		return _C
	def check_set_key(self,node,key_node,setting,key):
		if key in setting:
			if not self.allow_duplicate_keys:
				if PY2:
					if isinstance(key,unicode):key=key.encode(_Q)
				args=['while constructing a set',node.start_mark,_Y.format(key),key_node.start_mark,_i,_j]
				if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
				else:raise DuplicateKeyError(*args)
	def construct_pairs(self,node,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_P%node.id,node.start_mark)
		pairs=[]
		for (key_node,value_node) in node.value:key=self.construct_object(key_node,deep=deep);value=self.construct_object(value_node,deep=deep);pairs.append((key,value))
		return pairs
	@classmethod
	def add_constructor(cls,tag,constructor):
		if'yaml_constructors'not in cls.__dict__:cls.yaml_constructors=cls.yaml_constructors.copy()
		cls.yaml_constructors[tag]=constructor
	@classmethod
	def add_multi_constructor(cls,tag_prefix,multi_constructor):
		if'yaml_multi_constructors'not in cls.__dict__:cls.yaml_multi_constructors=cls.yaml_multi_constructors.copy()
		cls.yaml_multi_constructors[tag_prefix]=multi_constructor
class SafeConstructor(BaseConstructor):
	def construct_scalar(self,node):
		if isinstance(node,MappingNode):
			for (key_node,value_node) in node.value:
				if key_node.tag==_Z:return self.construct_scalar(value_node)
		return BaseConstructor.construct_scalar(self,node)
	def flatten_mapping(self,node):
		merge=[];index=0
		while index<len(node.value):
			key_node,value_node=node.value[index]
			if key_node.tag==_k:
				if merge:
					if self.allow_duplicate_keys:del node.value[index];index+=1;continue
					args=[_E,node.start_mark,_Y.format(key_node.value),key_node.start_mark,_l,_m]
					if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
					else:raise DuplicateKeyError(*args)
				del node.value[index]
				if isinstance(value_node,MappingNode):self.flatten_mapping(value_node);merge.extend(value_node.value)
				elif isinstance(value_node,SequenceNode):
					submerge=[]
					for subnode in value_node.value:
						if not isinstance(subnode,MappingNode):raise ConstructorError(_E,node.start_mark,_n%subnode.id,subnode.start_mark)
						self.flatten_mapping(subnode);submerge.append(subnode.value)
					submerge.reverse()
					for value in submerge:merge.extend(value)
				else:raise ConstructorError(_E,node.start_mark,_o%value_node.id,value_node.start_mark)
			elif key_node.tag==_Z:key_node.tag=_R;index+=1
			else:index+=1
		if bool(merge):node.merge=merge;node.value=merge+node.value
	def construct_mapping(self,node,deep=_B):
		if isinstance(node,MappingNode):self.flatten_mapping(node)
		return BaseConstructor.construct_mapping(self,node,deep=deep)
	def construct_yaml_null(self,node):self.construct_scalar(node);return _A
	bool_values={'yes':_C,'no':_B,'y':_C,'n':_B,'true':_C,'false':_B,'on':_C,'off':_B}
	def construct_yaml_bool(self,node):value=self.construct_scalar(node);return self.bool_values[value.lower()]
	def construct_yaml_int(self,node):
		value_s=to_str(self.construct_scalar(node));value_s=value_s.replace(_D,'');sign=+1
		if value_s[0]==_J:sign=-1
		if value_s[0]in _M:value_s=value_s[1:]
		if value_s==_F:return 0
		elif value_s.startswith('0b'):return sign*int(value_s[2:],2)
		elif value_s.startswith('0x'):return sign*int(value_s[2:],16)
		elif value_s.startswith('0o'):return sign*int(value_s[2:],8)
		elif self.resolver.processing_version==(1,1)and value_s[0]==_F:return sign*int(value_s,8)
		elif self.resolver.processing_version==(1,1)and _G in value_s:
			digits=[int(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		else:return sign*int(value_s)
	inf_value=1e+300
	while inf_value!=inf_value*inf_value:inf_value*=inf_value
	nan_value=-inf_value/inf_value
	def construct_yaml_float(self,node):
		value_so=to_str(self.construct_scalar(node));value_s=value_so.replace(_D,'').lower();sign=+1
		if value_s[0]==_J:sign=-1
		if value_s[0]in _M:value_s=value_s[1:]
		if value_s==_p:return sign*self.inf_value
		elif value_s==_q:return self.nan_value
		elif self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[float(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0.0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		else:
			if self.resolver.processing_version!=(1,2)and _N in value_s:
				mantissa,exponent=value_s.split(_N)
				if _H not in mantissa:warnings.warn(MantissaNoDotYAML1_1Warning(node,value_so))
			return sign*float(value_s)
	if PY3:
		def construct_yaml_binary(self,node):
			try:value=self.construct_scalar(node).encode(_S)
			except UnicodeEncodeError as exc:raise ConstructorError(_A,_A,_r%exc,node.start_mark)
			try:
				if hasattr(base64,_s):return base64.decodebytes(value)
				else:return base64.decodestring(value)
			except binascii.Error as exc:raise ConstructorError(_A,_A,_a%exc,node.start_mark)
	else:
		def construct_yaml_binary(self,node):
			value=self.construct_scalar(node)
			try:return to_str(value).decode('base64')
			except (binascii.Error,UnicodeEncodeError)as exc:raise ConstructorError(_A,_A,_a%exc,node.start_mark)
	timestamp_regexp=RegExp('^(?P<year>[0-9][0-9][0-9][0-9])\n          -(?P<month>[0-9][0-9]?)\n          -(?P<day>[0-9][0-9]?)\n          (?:((?P<t>[Tt])|[ \\t]+)   # explictly not retaining extra spaces\n          (?P<hour>[0-9][0-9]?)\n          :(?P<minute>[0-9][0-9])\n          :(?P<second>[0-9][0-9])\n          (?:\\.(?P<fraction>[0-9]*))?\n          (?:[ \\t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9][0-9]?)\n          (?::(?P<tz_minute>[0-9][0-9]))?))?)?$',re.X)
	def construct_yaml_timestamp(self,node,values=_A):
		if values is _A:
			try:match=self.timestamp_regexp.match(node.value)
			except TypeError:match=_A
			if match is _A:raise ConstructorError(_A,_A,_t.format(node.value),node.start_mark)
			values=match.groupdict()
		year=int(values[_u]);month=int(values[_v]);day=int(values[_w])
		if not values[_T]:return datetime.date(year,month,day)
		hour=int(values[_T]);minute=int(values[_x]);second=int(values[_y]);fraction=0
		if values[_I]:
			fraction_s=values[_I][:6]
			while len(fraction_s)<6:fraction_s+=_F
			fraction=int(fraction_s)
			if len(values[_I])>6 and int(values[_I][6])>4:fraction+=1
		delta=_A
		if values[_K]:
			tz_hour=int(values[_U]);minutes=values[_O];tz_minute=int(minutes)if minutes else 0;delta=datetime.timedelta(hours=tz_hour,minutes=tz_minute)
			if values[_K]==_J:delta=-delta
		data=datetime.datetime(year,month,day,hour,minute,second,fraction)
		if delta:data-=delta
		return data
	def construct_yaml_omap(self,node):
		omap=ordereddict();yield omap
		if not isinstance(node,SequenceNode):raise ConstructorError(_L,node.start_mark,_b%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(_L,node.start_mark,_c%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(_L,node.start_mark,_d%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);assert key not in omap;value=self.construct_object(value_node);omap[key]=value
	def construct_yaml_pairs(self,node):
		A='while constructing pairs';pairs=[];yield pairs
		if not isinstance(node,SequenceNode):raise ConstructorError(A,node.start_mark,_b%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(A,node.start_mark,_c%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(A,node.start_mark,_d%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);value=self.construct_object(value_node);pairs.append((key,value))
	def construct_yaml_set(self,node):data=set();yield data;value=self.construct_mapping(node);data.update(value)
	def construct_yaml_str(self,node):
		value=self.construct_scalar(node)
		if PY3:return value
		try:return value.encode(_S)
		except UnicodeEncodeError:return value
	def construct_yaml_seq(self,node):data=self.yaml_base_list_type();yield data;data.extend(self.construct_sequence(node))
	def construct_yaml_map(self,node):data=self.yaml_base_dict_type();yield data;value=self.construct_mapping(node);data.update(value)
	def construct_yaml_object(self,node,cls):
		data=cls.__new__(cls);yield data
		if hasattr(data,_V):state=self.construct_mapping(node,deep=_C);data.__setstate__(state)
		else:state=self.construct_mapping(node);data.__dict__.update(state)
	def construct_undefined(self,node):raise ConstructorError(_A,_A,_z%utf8(node.tag),node.start_mark)
SafeConstructor.add_constructor(_A0,SafeConstructor.construct_yaml_null)
SafeConstructor.add_constructor(_A1,SafeConstructor.construct_yaml_bool)
SafeConstructor.add_constructor(_A2,SafeConstructor.construct_yaml_int)
SafeConstructor.add_constructor(_A3,SafeConstructor.construct_yaml_float)
SafeConstructor.add_constructor(_A4,SafeConstructor.construct_yaml_binary)
SafeConstructor.add_constructor(_A5,SafeConstructor.construct_yaml_timestamp)
SafeConstructor.add_constructor(_A6,SafeConstructor.construct_yaml_omap)
SafeConstructor.add_constructor(_A7,SafeConstructor.construct_yaml_pairs)
SafeConstructor.add_constructor(_A8,SafeConstructor.construct_yaml_set)
SafeConstructor.add_constructor(_R,SafeConstructor.construct_yaml_str)
SafeConstructor.add_constructor(_A9,SafeConstructor.construct_yaml_seq)
SafeConstructor.add_constructor(_AA,SafeConstructor.construct_yaml_map)
SafeConstructor.add_constructor(_A,SafeConstructor.construct_undefined)
if PY2:
	class classobj:0
class Constructor(SafeConstructor):
	def construct_python_str(self,node):return utf8(self.construct_scalar(node))
	def construct_python_unicode(self,node):return self.construct_scalar(node)
	if PY3:
		def construct_python_bytes(self,node):
			try:value=self.construct_scalar(node).encode(_S)
			except UnicodeEncodeError as exc:raise ConstructorError(_A,_A,_r%exc,node.start_mark)
			try:
				if hasattr(base64,_s):return base64.decodebytes(value)
				else:return base64.decodestring(value)
			except binascii.Error as exc:raise ConstructorError(_A,_A,_a%exc,node.start_mark)
	def construct_python_long(self,node):
		val=self.construct_yaml_int(node)
		if PY3:return val
		return int(val)
	def construct_python_complex(self,node):return complex(self.construct_scalar(node))
	def construct_python_tuple(self,node):return tuple(self.construct_sequence(node))
	def find_python_module(self,name,mark):
		if not name:raise ConstructorError(_e,mark,_AB,mark)
		try:__import__(name)
		except ImportError as exc:raise ConstructorError(_e,mark,_AC%(utf8(name),exc),mark)
		return sys.modules[name]
	def find_python_name(self,name,mark):
		A='while constructing a Python object'
		if not name:raise ConstructorError(A,mark,_AB,mark)
		if _H in name:
			lname=name.split(_H);lmodule_name=lname;lobject_name=[]
			while len(lmodule_name)>1:
				lobject_name.insert(0,lmodule_name.pop());module_name=_H.join(lmodule_name)
				try:__import__(module_name);break
				except ImportError:continue
		else:module_name=builtins_module;lobject_name=[name]
		try:__import__(module_name)
		except ImportError as exc:raise ConstructorError(A,mark,_AC%(utf8(module_name),exc),mark)
		module=sys.modules[module_name];object_name=_H.join(lobject_name);obj=module
		while lobject_name:
			if not hasattr(obj,lobject_name[0]):raise ConstructorError(A,mark,'cannot find %r in the module %r'%(utf8(object_name),module.__name__),mark)
			obj=getattr(obj,lobject_name.pop(0))
		return obj
	def construct_python_name(self,suffix,node):
		value=self.construct_scalar(node)
		if value:raise ConstructorError('while constructing a Python name',node.start_mark,_AD%utf8(value),node.start_mark)
		return self.find_python_name(suffix,node.start_mark)
	def construct_python_module(self,suffix,node):
		value=self.construct_scalar(node)
		if value:raise ConstructorError(_e,node.start_mark,_AD%utf8(value),node.start_mark)
		return self.find_python_module(suffix,node.start_mark)
	def make_python_instance(self,suffix,node,args=_A,kwds=_A,newobj=_B):
		if not args:args=[]
		if not kwds:kwds={}
		cls=self.find_python_name(suffix,node.start_mark)
		if PY3:
			if newobj and isinstance(cls,type):return cls.__new__(cls,*args,**kwds)
			else:return cls(*args,**kwds)
		elif newobj and isinstance(cls,type(classobj))and not args and not kwds:instance=classobj();instance.__class__=cls;return instance
		elif newobj and isinstance(cls,type):return cls.__new__(cls,*args,**kwds)
		else:return cls(*args,**kwds)
	def set_python_instance_state(self,instance,state):
		if hasattr(instance,_V):instance.__setstate__(state)
		else:
			slotstate={}
			if isinstance(state,tuple)and len(state)==2:state,slotstate=state
			if hasattr(instance,'__dict__'):instance.__dict__.update(state)
			elif state:slotstate.update(state)
			for (key,value) in slotstate.items():setattr(instance,key,value)
	def construct_python_object(self,suffix,node):instance=self.make_python_instance(suffix,node,newobj=_C);self.recursive_objects[node]=instance;yield instance;deep=hasattr(instance,_V);state=self.construct_mapping(node,deep=deep);self.set_python_instance_state(instance,state)
	def construct_python_object_apply(self,suffix,node,newobj=_B):
		if isinstance(node,SequenceNode):args=self.construct_sequence(node,deep=_C);kwds={};state={};listitems=[];dictitems={}
		else:value=self.construct_mapping(node,deep=_C);args=value.get('args',[]);kwds=value.get('kwds',{});state=value.get('state',{});listitems=value.get('listitems',[]);dictitems=value.get('dictitems',{})
		instance=self.make_python_instance(suffix,node,args,kwds,newobj)
		if bool(state):self.set_python_instance_state(instance,state)
		if bool(listitems):instance.extend(listitems)
		if bool(dictitems):
			for key in dictitems:instance[key]=dictitems[key]
		return instance
	def construct_python_object_new(self,suffix,node):return self.construct_python_object_apply(suffix,node,newobj=_C)
Constructor.add_constructor('tag:yaml.org,2002:python/none',Constructor.construct_yaml_null)
Constructor.add_constructor('tag:yaml.org,2002:python/bool',Constructor.construct_yaml_bool)
Constructor.add_constructor('tag:yaml.org,2002:python/str',Constructor.construct_python_str)
Constructor.add_constructor('tag:yaml.org,2002:python/unicode',Constructor.construct_python_unicode)
if PY3:Constructor.add_constructor('tag:yaml.org,2002:python/bytes',Constructor.construct_python_bytes)
Constructor.add_constructor('tag:yaml.org,2002:python/int',Constructor.construct_yaml_int)
Constructor.add_constructor('tag:yaml.org,2002:python/long',Constructor.construct_python_long)
Constructor.add_constructor('tag:yaml.org,2002:python/float',Constructor.construct_yaml_float)
Constructor.add_constructor('tag:yaml.org,2002:python/complex',Constructor.construct_python_complex)
Constructor.add_constructor('tag:yaml.org,2002:python/list',Constructor.construct_yaml_seq)
Constructor.add_constructor('tag:yaml.org,2002:python/tuple',Constructor.construct_python_tuple)
Constructor.add_constructor('tag:yaml.org,2002:python/dict',Constructor.construct_yaml_map)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/name:',Constructor.construct_python_name)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/module:',Constructor.construct_python_module)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object:',Constructor.construct_python_object)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object/apply:',Constructor.construct_python_object_apply)
Constructor.add_multi_constructor('tag:yaml.org,2002:python/object/new:',Constructor.construct_python_object_new)
class RoundTripConstructor(SafeConstructor):
	def construct_scalar(self,node):
		A='\x07'
		if not isinstance(node,ScalarNode):raise ConstructorError(_A,_A,_g%node.id,node.start_mark)
		if node.style=='|'and isinstance(node.value,text_type):
			lss=LiteralScalarString(node.value,anchor=node.anchor)
			if node.comment and node.comment[1]:lss.comment=node.comment[1][0]
			return lss
		if node.style=='>'and isinstance(node.value,text_type):
			fold_positions=[];idx=-1
			while _C:
				idx=node.value.find(A,idx+1)
				if idx<0:break
				fold_positions.append(idx-len(fold_positions))
			fss=FoldedScalarString(node.value.replace(A,''),anchor=node.anchor)
			if node.comment and node.comment[1]:fss.comment=node.comment[1][0]
			if fold_positions:fss.fold_pos=fold_positions
			return fss
		elif bool(self._preserve_quotes)and isinstance(node.value,text_type):
			if node.style=="'":return SingleQuotedScalarString(node.value,anchor=node.anchor)
			if node.style=='"':return DoubleQuotedScalarString(node.value,anchor=node.anchor)
		if node.anchor:return PlainScalarString(node.value,anchor=node.anchor)
		return node.value
	def construct_yaml_int(self,node):
		width=_A;value_su=to_str(self.construct_scalar(node))
		try:sx=value_su.rstrip(_D);underscore=[len(sx)-sx.rindex(_D)-1,_B,_B]
		except ValueError:underscore=_A
		except IndexError:underscore=_A
		value_s=value_su.replace(_D,'');sign=+1
		if value_s[0]==_J:sign=-1
		if value_s[0]in _M:value_s=value_s[1:]
		if value_s==_F:return 0
		elif value_s.startswith('0b'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return BinaryInt(sign*int(value_s[2:],2),width=width,underscore=underscore,anchor=node.anchor)
		elif value_s.startswith('0x'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			hex_fun=HexInt
			for ch in value_s[2:]:
				if ch in'ABCDEF':hex_fun=HexCapsInt;break
				if ch in'abcdef':break
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return hex_fun(sign*int(value_s[2:],16),width=width,underscore=underscore,anchor=node.anchor)
		elif value_s.startswith('0o'):
			if self.resolver.processing_version>(1,1)and value_s[2]==_F:width=len(value_s[2:])
			if underscore is not _A:underscore[1]=value_su[2]==_D;underscore[2]=len(value_su[2:])>1 and value_su[-1]==_D
			return OctalInt(sign*int(value_s[2:],8),width=width,underscore=underscore,anchor=node.anchor)
		elif self.resolver.processing_version!=(1,2)and value_s[0]==_F:return sign*int(value_s,8)
		elif self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[int(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		elif self.resolver.processing_version>(1,1)and value_s[0]==_F:
			if underscore is not _A:underscore[2]=len(value_su)>1 and value_su[-1]==_D
			return ScalarInt(sign*int(value_s),width=len(value_s),underscore=underscore)
		elif underscore:underscore[2]=len(value_su)>1 and value_su[-1]==_D;return ScalarInt(sign*int(value_s),width=_A,underscore=underscore,anchor=node.anchor)
		elif node.anchor:return ScalarInt(sign*int(value_s),width=_A,anchor=node.anchor)
		else:return sign*int(value_s)
	def construct_yaml_float(self,node):
		A='E'
		def leading_zeros(v):
			lead0=0;idx=0
			while idx<len(v)and v[idx]in'0.':
				if v[idx]==_F:lead0+=1
				idx+=1
			return lead0
		m_sign=_B;value_so=to_str(self.construct_scalar(node));value_s=value_so.replace(_D,'').lower();sign=+1
		if value_s[0]==_J:sign=-1
		if value_s[0]in _M:m_sign=value_s[0];value_s=value_s[1:]
		if value_s==_p:return sign*self.inf_value
		if value_s==_q:return self.nan_value
		if self.resolver.processing_version!=(1,2)and _G in value_s:
			digits=[float(part)for part in value_s.split(_G)];digits.reverse();base=1;value=0.0
			for digit in digits:value+=digit*base;base*=60
			return sign*value
		if _N in value_s:
			try:mantissa,exponent=value_so.split(_N);exp=_N
			except ValueError:mantissa,exponent=value_so.split(A);exp=A
			if self.resolver.processing_version!=(1,2):
				if _H not in mantissa:warnings.warn(MantissaNoDotYAML1_1Warning(node,value_so))
			lead0=leading_zeros(mantissa);width=len(mantissa);prec=mantissa.find(_H)
			if m_sign:width-=1
			e_width=len(exponent);e_sign=exponent[0]in _M;return ScalarFloat(sign*float(value_s),width=width,prec=prec,m_sign=m_sign,m_lead0=lead0,exp=exp,e_width=e_width,e_sign=e_sign,anchor=node.anchor)
		width=len(value_so);prec=value_so.index(_H);lead0=leading_zeros(value_so);return ScalarFloat(sign*float(value_s),width=width,prec=prec,m_sign=m_sign,m_lead0=lead0,anchor=node.anchor)
	def construct_yaml_str(self,node):
		value=self.construct_scalar(node)
		if isinstance(value,ScalarString):return value
		if PY3:return value
		try:return value.encode(_S)
		except AttributeError:return value
		except UnicodeEncodeError:return value
	def construct_rt_sequence(self,node,seqtyp,deep=_B):
		if not isinstance(node,SequenceNode):raise ConstructorError(_A,_A,_h%node.id,node.start_mark)
		ret_val=[]
		if node.comment:
			seqtyp._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:seqtyp.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):seqtyp.yaml_set_anchor(node.anchor)
		for (idx,child) in enumerate(node.value):
			if child.comment:seqtyp._yaml_add_comment(child.comment,key=idx);child.comment=_A
			ret_val.append(self.construct_object(child,deep=deep));seqtyp._yaml_set_idx_line_col(idx,[child.start_mark.line,child.start_mark.column])
		return ret_val
	def flatten_mapping(self,node):
		def constructed(value_node):
			if value_node in self.constructed_objects:value=self.constructed_objects[value_node]
			else:value=self.construct_object(value_node,deep=_B)
			return value
		merge_map_list=[];index=0
		while index<len(node.value):
			key_node,value_node=node.value[index]
			if key_node.tag==_k:
				if merge_map_list:
					if self.allow_duplicate_keys:del node.value[index];index+=1;continue
					args=[_E,node.start_mark,_Y.format(key_node.value),key_node.start_mark,_l,_m]
					if self.allow_duplicate_keys is _A:warnings.warn(DuplicateKeyFutureWarning(*args))
					else:raise DuplicateKeyError(*args)
				del node.value[index]
				if isinstance(value_node,MappingNode):merge_map_list.append((index,constructed(value_node)))
				elif isinstance(value_node,SequenceNode):
					for subnode in value_node.value:
						if not isinstance(subnode,MappingNode):raise ConstructorError(_E,node.start_mark,_n%subnode.id,subnode.start_mark)
						merge_map_list.append((index,constructed(subnode)))
				else:raise ConstructorError(_E,node.start_mark,_o%value_node.id,value_node.start_mark)
			elif key_node.tag==_Z:key_node.tag=_R;index+=1
			else:index+=1
		return merge_map_list
	def _sentinel(self):0
	def construct_mapping(self,node,maptyp,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_P%node.id,node.start_mark)
		merge_map=self.flatten_mapping(node)
		if node.comment:
			maptyp._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:maptyp.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):maptyp.yaml_set_anchor(node.anchor)
		last_key,last_value=_A,self._sentinel
		for (key_node,value_node) in node.value:
			key=self.construct_object(key_node,deep=_C)
			if not isinstance(key,Hashable):
				if isinstance(key,MutableSequence):
					key_s=CommentedKeySeq(key)
					if key_node.flow_style is _C:key_s.fa.set_flow_style()
					elif key_node.flow_style is _B:key_s.fa.set_block_style()
					key=key_s
				elif isinstance(key,MutableMapping):
					key_m=CommentedKeyMap(key)
					if key_node.flow_style is _C:key_m.fa.set_flow_style()
					elif key_node.flow_style is _B:key_m.fa.set_block_style()
					key=key_m
			if PY2:
				try:hash(key)
				except TypeError as exc:raise ConstructorError(_E,node.start_mark,_W%exc,key_node.start_mark)
			elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_X,key_node.start_mark)
			value=self.construct_object(value_node,deep=deep)
			if self.check_mapping_key(node,key_node,maptyp,key,value):
				if key_node.comment and len(key_node.comment)>4 and key_node.comment[4]:
					if last_value is _A:key_node.comment[0]=key_node.comment.pop(4);maptyp._yaml_add_comment(key_node.comment,value=last_key)
					else:key_node.comment[2]=key_node.comment.pop(4);maptyp._yaml_add_comment(key_node.comment,key=key)
					key_node.comment=_A
				if key_node.comment:maptyp._yaml_add_comment(key_node.comment,key=key)
				if value_node.comment:maptyp._yaml_add_comment(value_node.comment,value=key)
				maptyp._yaml_set_kv_line_col(key,[key_node.start_mark.line,key_node.start_mark.column,value_node.start_mark.line,value_node.start_mark.column]);maptyp[key]=value;last_key,last_value=key,value
		if merge_map:maptyp.add_yaml_merge(merge_map)
	def construct_setting(self,node,typ,deep=_B):
		if not isinstance(node,MappingNode):raise ConstructorError(_A,_A,_P%node.id,node.start_mark)
		if node.comment:
			typ._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:typ.yaml_end_comment_extend(node.comment[2],clear=_C)
		if node.anchor:
			from dynaconf.vendor.ruamel.yaml.serializer import templated_id
			if not templated_id(node.anchor):typ.yaml_set_anchor(node.anchor)
		for (key_node,value_node) in node.value:
			key=self.construct_object(key_node,deep=_C)
			if not isinstance(key,Hashable):
				if isinstance(key,list):key=tuple(key)
			if PY2:
				try:hash(key)
				except TypeError as exc:raise ConstructorError(_E,node.start_mark,_W%exc,key_node.start_mark)
			elif not isinstance(key,Hashable):raise ConstructorError(_E,node.start_mark,_X,key_node.start_mark)
			value=self.construct_object(value_node,deep=deep);self.check_set_key(node,key_node,typ,key)
			if key_node.comment:typ._yaml_add_comment(key_node.comment,key=key)
			if value_node.comment:typ._yaml_add_comment(value_node.comment,value=key)
			typ.add(key)
	def construct_yaml_seq(self,node):
		data=CommentedSeq();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
		if node.comment:data._yaml_add_comment(node.comment)
		yield data;data.extend(self.construct_rt_sequence(node,data));self.set_collection_style(data,node)
	def construct_yaml_map(self,node):data=CommentedMap();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column);yield data;self.construct_mapping(node,data,deep=_C);self.set_collection_style(data,node)
	def set_collection_style(self,data,node):
		if len(data)==0:return
		if node.flow_style is _C:data.fa.set_flow_style()
		elif node.flow_style is _B:data.fa.set_block_style()
	def construct_yaml_object(self,node,cls):
		data=cls.__new__(cls);yield data
		if hasattr(data,_V):state=SafeConstructor.construct_mapping(self,node,deep=_C);data.__setstate__(state)
		else:state=SafeConstructor.construct_mapping(self,node);data.__dict__.update(state)
	def construct_yaml_omap(self,node):
		omap=CommentedOrderedMap();omap._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
		if node.flow_style is _C:omap.fa.set_flow_style()
		elif node.flow_style is _B:omap.fa.set_block_style()
		yield omap
		if node.comment:
			omap._yaml_add_comment(node.comment[:2])
			if len(node.comment)>2:omap.yaml_end_comment_extend(node.comment[2],clear=_C)
		if not isinstance(node,SequenceNode):raise ConstructorError(_L,node.start_mark,_b%node.id,node.start_mark)
		for subnode in node.value:
			if not isinstance(subnode,MappingNode):raise ConstructorError(_L,node.start_mark,_c%subnode.id,subnode.start_mark)
			if len(subnode.value)!=1:raise ConstructorError(_L,node.start_mark,_d%len(subnode.value),subnode.start_mark)
			key_node,value_node=subnode.value[0];key=self.construct_object(key_node);assert key not in omap;value=self.construct_object(value_node)
			if key_node.comment:omap._yaml_add_comment(key_node.comment,key=key)
			if subnode.comment:omap._yaml_add_comment(subnode.comment,key=key)
			if value_node.comment:omap._yaml_add_comment(value_node.comment,value=key)
			omap[key]=value
	def construct_yaml_set(self,node):data=CommentedSet();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column);yield data;self.construct_setting(node,data)
	def construct_undefined(self,node):
		try:
			if isinstance(node,MappingNode):
				data=CommentedMap();data._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
				if node.flow_style is _C:data.fa.set_flow_style()
				elif node.flow_style is _B:data.fa.set_block_style()
				data.yaml_set_tag(node.tag);yield data
				if node.anchor:data.yaml_set_anchor(node.anchor)
				self.construct_mapping(node,data);return
			elif isinstance(node,ScalarNode):
				data2=TaggedScalar();data2.value=self.construct_scalar(node);data2.style=node.style;data2.yaml_set_tag(node.tag);yield data2
				if node.anchor:data2.yaml_set_anchor(node.anchor,always_dump=_C)
				return
			elif isinstance(node,SequenceNode):
				data3=CommentedSeq();data3._yaml_set_line_col(node.start_mark.line,node.start_mark.column)
				if node.flow_style is _C:data3.fa.set_flow_style()
				elif node.flow_style is _B:data3.fa.set_block_style()
				data3.yaml_set_tag(node.tag);yield data3
				if node.anchor:data3.yaml_set_anchor(node.anchor)
				data3.extend(self.construct_sequence(node));return
		except:pass
		raise ConstructorError(_A,_A,_z%utf8(node.tag),node.start_mark)
	def construct_yaml_timestamp(self,node,values=_A):
		B='t';A='tz'
		try:match=self.timestamp_regexp.match(node.value)
		except TypeError:match=_A
		if match is _A:raise ConstructorError(_A,_A,_t.format(node.value),node.start_mark)
		values=match.groupdict()
		if not values[_T]:return SafeConstructor.construct_yaml_timestamp(self,node,values)
		for part in [B,_K,_U,_O]:
			if values[part]:break
		else:return SafeConstructor.construct_yaml_timestamp(self,node,values)
		year=int(values[_u]);month=int(values[_v]);day=int(values[_w]);hour=int(values[_T]);minute=int(values[_x]);second=int(values[_y]);fraction=0
		if values[_I]:
			fraction_s=values[_I][:6]
			while len(fraction_s)<6:fraction_s+=_F
			fraction=int(fraction_s)
			if len(values[_I])>6 and int(values[_I][6])>4:fraction+=1
		delta=_A
		if values[_K]:
			tz_hour=int(values[_U]);minutes=values[_O];tz_minute=int(minutes)if minutes else 0;delta=datetime.timedelta(hours=tz_hour,minutes=tz_minute)
			if values[_K]==_J:delta=-delta
		if delta:
			dt=datetime.datetime(year,month,day,hour,minute);dt-=delta;data=TimeStamp(dt.year,dt.month,dt.day,dt.hour,dt.minute,second,fraction);data._yaml['delta']=delta;tz=values[_K]+values[_U]
			if values[_O]:tz+=_G+values[_O]
			data._yaml[A]=tz
		else:
			data=TimeStamp(year,month,day,hour,minute,second,fraction)
			if values[A]:data._yaml[A]=values[A]
		if values[B]:data._yaml[B]=_C
		return data
	def construct_yaml_bool(self,node):
		b=SafeConstructor.construct_yaml_bool(self,node)
		if node.anchor:return ScalarBoolean(b,anchor=node.anchor)
		return b
RoundTripConstructor.add_constructor(_A0,RoundTripConstructor.construct_yaml_null)
RoundTripConstructor.add_constructor(_A1,RoundTripConstructor.construct_yaml_bool)
RoundTripConstructor.add_constructor(_A2,RoundTripConstructor.construct_yaml_int)
RoundTripConstructor.add_constructor(_A3,RoundTripConstructor.construct_yaml_float)
RoundTripConstructor.add_constructor(_A4,RoundTripConstructor.construct_yaml_binary)
RoundTripConstructor.add_constructor(_A5,RoundTripConstructor.construct_yaml_timestamp)
RoundTripConstructor.add_constructor(_A6,RoundTripConstructor.construct_yaml_omap)
RoundTripConstructor.add_constructor(_A7,RoundTripConstructor.construct_yaml_pairs)
RoundTripConstructor.add_constructor(_A8,RoundTripConstructor.construct_yaml_set)
RoundTripConstructor.add_constructor(_R,RoundTripConstructor.construct_yaml_str)
RoundTripConstructor.add_constructor(_A9,RoundTripConstructor.construct_yaml_seq)
RoundTripConstructor.add_constructor(_AA,RoundTripConstructor.construct_yaml_map)
RoundTripConstructor.add_constructor(_A,RoundTripConstructor.construct_undefined)