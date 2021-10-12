_B=False
_A=None
import typing as t
from .filters import FILTERS as DEFAULT_FILTERS
from .tests import TESTS as DEFAULT_TESTS
from .utils import Cycler
from .utils import generate_lorem_ipsum
from .utils import Joiner
from .utils import Namespace
if t.TYPE_CHECKING:import typing_extensions as te
BLOCK_START_STRING='{%'
BLOCK_END_STRING='%}'
VARIABLE_START_STRING='{{'
VARIABLE_END_STRING='}}'
COMMENT_START_STRING='{#'
COMMENT_END_STRING='#}'
LINE_STATEMENT_PREFIX=_A
LINE_COMMENT_PREFIX=_A
TRIM_BLOCKS=_B
LSTRIP_BLOCKS=_B
NEWLINE_SEQUENCE='\n'
KEEP_TRAILING_NEWLINE=_B
DEFAULT_NAMESPACE={'range':range,'dict':dict,'lipsum':generate_lorem_ipsum,'cycler':Cycler,'joiner':Joiner,'namespace':Namespace}
DEFAULT_POLICIES={'compiler.ascii_str':True,'urlize.rel':'noopener','urlize.target':_A,'urlize.extra_schemes':_A,'truncate.leeway':5,'json.dumps_function':_A,'json.dumps_kwargs':{'sort_keys':True},'ext.i18n.trimmed':_B}