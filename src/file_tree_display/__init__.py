"""file-tree-display - A utility for generating a visually structured directory tree.
Copyright (c) 2025 Yaron Dayan
"""

from pathlib import Path
from importlib.metadata import version

from nano_dev_utils.common import (
    update,
    str2file,
    PredicateBuilder,
    FilterSet,
    load_cfg_file,
)

from .ftd import FileTreeDisplay
from ._constants import PKG_NAME

filetree_display = FileTreeDisplay(root_dir=str(Path.cwd()))
predicate_builder = PredicateBuilder

__version__ = version(PKG_NAME)

__all__ = [
    'update',
    'str2file',
    'PredicateBuilder',
    'predicate_builder',
    'FilterSet',
    'filetree_display',
    'FileTreeDisplay',
    'load_cfg_file',
]
