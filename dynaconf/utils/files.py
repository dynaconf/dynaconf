import os
import inspect
from dynaconf.utils import raw_logger, deduplicate


logger = raw_logger()


def _walk_to_root(path, break_at=None):
    """
    Directories starting from the given directory up to the root or break_at
    """
    if not os.path.exists(path):  # pragma: no cover
        raise IOError('Starting path not found')

    if os.path.isfile(path):  # pragma: no cover
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    paths = []
    while last_dir != current_dir:
        paths.append(current_dir)
        paths.append(os.path.join(current_dir, 'config'))
        if break_at and current_dir == os.path.abspath(break_at): # noqa
            logger.debug('Reached the %s directory, breaking.', break_at)
            break
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir
    return paths


SEARCHTREE = None


def find_file(filename='.env', project_root=None, skip_files=None, **kwargs):
    """Search in increasingly higher folders for the given file
    Returns path to the file if found, or an empty string otherwise.

    This function will build a `search_tree` based on:

    - Project_root if specified
    - Invoked script location and its parents until root
    - Current working directory

    For each path in the `search_tree` it will also look for an
    aditional `./config` folder.
    """
    search_tree = []
    work_dir = os.getcwd()
    skip_files = skip_files or []

    if project_root is None:
        logger.debug('No root_path for %s', filename)
    else:
        logger.debug('Got root_path %s for %s', project_root, filename)
        search_tree.extend(_walk_to_root(project_root, break_at=work_dir))

    script_dir = os.path.dirname(os.path.abspath(inspect.stack()[-1].filename))

    # Path to invoked script and recursivelly to root with its ./config dirs
    search_tree.extend(_walk_to_root(script_dir))

    # Where Python interpreter was invoked from and its ./config
    search_tree.extend([work_dir, os.path.join(work_dir, 'config')])

    search_tree = deduplicate(search_tree)

    global SEARCHTREE
    SEARCHTREE != search_tree and logger.debug(
        'Search Tree: %s', search_tree
    )
    SEARCHTREE = search_tree

    logger.debug('Searching for %s', filename)

    for dirname in search_tree:
        check_path = os.path.join(dirname, filename)
        if check_path in skip_files:
            continue
        if os.path.exists(check_path):
            logger.debug('Found: %s', os.path.abspath(check_path))
            return check_path  # First found will return

    # return empty string if not found so it can still be joined in os.path
    return ''
