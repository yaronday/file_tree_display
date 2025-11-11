"""file-tree-display - A utility for generating a visually structured directory tree.
Copyright (c) 2025 Yaron Dayan
"""

from pathlib import Path
from importlib.metadata import version

from .ftd import FileTreeDisplay
from ._constants import PKG_NAME

filetree_display = FileTreeDisplay(root_dir=str(Path.cwd()))

__version__ = version(PKG_NAME)

