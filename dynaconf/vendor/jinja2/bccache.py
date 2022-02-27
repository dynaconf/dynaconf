_A=None
import errno,fnmatch,marshal,os,pickle,stat,sys,tempfile,typing as t
from hashlib import sha1
from io import BytesIO
from types import CodeType
if t.TYPE_CHECKING:
	import typing_extensions as te;from .environment import Environment
	class _MemcachedClient(te.Protocol):
		def get(A,key):...
		def set(A,key,value,timeout=_A):...
bc_version=5
bc_magic=b'j2'+pickle.dumps(bc_version,2)+pickle.dumps(sys.version_info[0]<<24|sys.version_info[1],2)
class Bucket:
	def __init__(A,environment,key,checksum):A.environment=environment;A.key=key;A.checksum=checksum;A.reset()
	def reset(A):A.code=_A
	def load_bytecode(A,f):
		B=f.read(len(bc_magic))
		if B!=bc_magic:A.reset();return
		C=pickle.load(f)
		if A.checksum!=C:A.reset();return
		try:A.code=marshal.load(f)
		except (EOFError,ValueError,TypeError):A.reset();return
	def write_bytecode(A,f):
		if A.code is _A:raise TypeError("can't write empty bucket")
		f.write(bc_magic);pickle.dump(A.checksum,f,2);marshal.dump(A.code,f)
	def bytecode_from_string(A,string):A.load_bytecode(BytesIO(string))
	def bytecode_to_string(B):A=BytesIO();B.write_bytecode(A);return A.getvalue()
class BytecodeCache:
	def load_bytecode(A,bucket):raise NotImplementedError()
	def dump_bytecode(A,bucket):raise NotImplementedError()
	def clear(A):0
	def get_cache_key(B,name,filename=_A):
		A=filename;hash=sha1(name.encode('utf-8'))
		if A is not _A:hash.update(f"|{A}".encode())
		return hash.hexdigest()
	def get_source_checksum(A,source):return sha1(source.encode('utf-8')).hexdigest()
	def get_bucket(A,environment,name,filename,source):C=A.get_cache_key(name,filename);D=A.get_source_checksum(source);B=Bucket(environment,C,D);A.load_bytecode(B);return B
	def set_bucket(A,bucket):A.dump_bytecode(bucket)
class FileSystemBytecodeCache(BytecodeCache):
	def __init__(A,directory=_A,pattern='__jinja2_%s.cache'):
		B=directory
		if B is _A:B=A._get_default_cache_dir()
		A.directory=B;A.pattern=pattern
	def _get_default_cache_dir(G):
		def C():raise RuntimeError('Cannot determine safe temp directory.  You need to explicitly provide one.')
		E=tempfile.gettempdir()
		if os.name=='nt':return E
		if not hasattr(os,'getuid'):C()
		F=f"_jinja2-cache-{os.getuid()}";B=os.path.join(E,F)
		try:os.mkdir(B,stat.S_IRWXU)
		except OSError as D:
			if D.errno!=errno.EEXIST:raise
		try:
			os.chmod(B,stat.S_IRWXU);A=os.lstat(B)
			if A.st_uid!=os.getuid()or not stat.S_ISDIR(A.st_mode)or stat.S_IMODE(A.st_mode)!=stat.S_IRWXU:C()
		except OSError as D:
			if D.errno!=errno.EEXIST:raise
		A=os.lstat(B)
		if A.st_uid!=os.getuid()or not stat.S_ISDIR(A.st_mode)or stat.S_IMODE(A.st_mode)!=stat.S_IRWXU:C()
		return B
	def _get_cache_filename(A,bucket):return os.path.join(A.directory,A.pattern%(bucket.key,))
	def load_bytecode(C,bucket):
		A=bucket;B=C._get_cache_filename(A)
		if os.path.exists(B):
			with open(B,'rb')as D:A.load_bytecode(D)
	def dump_bytecode(B,bucket):
		A=bucket
		with open(B._get_cache_filename(A),'wb')as C:A.write_bytecode(C)
	def clear(A):
		from os import remove as B;C=fnmatch.filter(os.listdir(A.directory),A.pattern%('*',))
		for D in C:
			try:B(os.path.join(A.directory,D))
			except OSError:pass
class MemcachedBytecodeCache(BytecodeCache):
	def __init__(A,client,prefix='jinja2/bytecode/',timeout=_A,ignore_memcache_errors=True):A.client=client;A.prefix=prefix;A.timeout=timeout;A.ignore_memcache_errors=ignore_memcache_errors
	def load_bytecode(A,bucket):
		B=bucket
		try:C=A.client.get(A.prefix+B.key)
		except Exception:
			if not A.ignore_memcache_errors:raise
		else:B.bytecode_from_string(C)
	def dump_bytecode(A,bucket):
		B=bucket;C=A.prefix+B.key;D=B.bytecode_to_string()
		try:
			if A.timeout is not _A:A.client.set(C,D,A.timeout)
			else:A.client.set(C,D)
		except Exception:
			if not A.ignore_memcache_errors:raise