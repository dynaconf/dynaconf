import os
import sys


def _walk_to_root(path):
    """
    Yield directories starting from the given directory up to the root
    """
    if not os.path.exists(path):  # pragma: no cover
        raise IOError('Starting path not found')

    if os.path.isfile(path):  # pragma: no cover
        path = os.path.dirname(path)

    last_dir = None
    current_dir = os.path.abspath(path)
    while last_dir != current_dir:
        yield current_dir
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir


def find_file(filename='.env', raise_error_if_not_found=False,
              usecwd=True, project_root=None):
    """Search in increasingly higher folders for the given file
    Returns path to the file if found, or an empty string otherwise
    """
    if project_root not in ['.', None]:
        path = project_root
    else:
        if usecwd or '__file__' not in globals():
            # should work without __file__, e.g. in REPL or IPython notebook
            path = os.getcwd()
        else:  # pragma: no cover
            # will work for .py files
            frame_filename = sys._getframe().f_back.f_code.co_filename
            path = os.path.dirname(os.path.abspath(frame_filename))

    for dirname in _walk_to_root(path):
        check_path = os.path.join(dirname, filename)
        if os.path.exists(check_path):
            return check_path

    if raise_error_if_not_found:
        raise IOError('File not found')

    return ''
