import pytest
from pathlib import Path
from file_tree_display.ftd import FileTreeDisplay


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
