"""file-tree-display - A utility for generating a visually structured directory tree.
Copyright (c) 2025 - 2026 Yaron Dayan
"""

from importlib.metadata import version
from pathlib import Path

from ._constants import PKG_NAME
from .ftd import FileTreeDisplay

filetree_display = FileTreeDisplay(root_dir=str(Path.cwd()))

__version__ = version(PKG_NAME)
