import pytest
import json

from pathlib import Path
from file_tree_display.ftd import FileTreeDisplay

import file_tree_display.__main__ as cli


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory structure for testing."""
    (tmp_path / 'dir1').mkdir()
    (tmp_path / 'dir1' / 'nested').mkdir()
    (tmp_path / 'dir1' / 'nested' / 'file_a.txt').write_text('alpha', encoding='utf-8')
    (tmp_path / 'dir2').mkdir()
    (tmp_path / 'dir2' / 'file_b.txt').write_text('bravo', encoding='utf-8')
    (tmp_path / 'ignored_dir').mkdir()
    (tmp_path / 'ignored_file.txt').write_text('ignore', encoding='utf-8')
    return tmp_path


@pytest.fixture
def ftd_mock(sample_dir: Path) -> FileTreeDisplay:
    """Provides a FileTreeDisplay instance with a temporary directory."""
    return FileTreeDisplay(root_dir=str(sample_dir))


@pytest.fixture
def cli_instance():
    """Provides a fresh FileTreeCLI instance for testing."""
    return cli.FileTreeCLI()


@pytest.fixture
def sample_cfg(tmp_path: Path, sample_dir: Path) -> Path:
    """Creates a temporary JSON config file for CLI testing."""
    cfg = {
        'root_dir': str(sample_dir),
        'indent': 4,
        'style': 'arrow',
        'ignore_dirs': "['.git', '.venv']",
        'include_dirs': ['src'],
    }
    cfg_path = tmp_path / 'cfg.json'
    cfg_path.write_text(json.dumps(cfg))
    return cfg_path
