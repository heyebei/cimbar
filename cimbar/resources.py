import os
import sys
from os import path


def resource_path(rel_path):
    """Get absolute path to resource, works for development and PyInstaller --onefile (sys._MEIPASS).

    rel_path is a path relative to the repository root, e.g. 'bitmap/4/00.png' or 'tests/sample/15.png'.
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = path.abspath(path.join(path.dirname(path.realpath(__file__)), '..'))
    return path.join(base, rel_path)


def bitmap_path(*parts):
    """Helper to build a path under the bitmap directory."""
    return resource_path(path.join('bitmap', *parts))
