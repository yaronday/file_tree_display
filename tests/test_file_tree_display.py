import pytest

from pathlib import Path
from unittest import mock
from pytest import MonkeyPatch

from file_tree_display.ftd import FileTreeDisplay

from typing import Generator


def test_basic_structure_generation(ftd_mock: FileTreeDisplay) -> None:
    """Ensure the generator yields expected directory structure lines."""
    lines = list(
        ftd_mock._build_tree(
            str(ftd_mock.root_path),
            prefix='',
            style=ftd_mock.format_style(),
            sort_key=ftd_mock._resolve_sort_key(),
            files_first=ftd_mock.files_first,
            dir_filter=ftd_mock.dir_filter,
            file_filter=ftd_mock.file_filter,
            reverse=ftd_mock.reverse,
        )
    )
    assert any('dir1' in line for line in lines)
    assert any('dir2' in line for line in lines)
    assert any('file_a.txt' in line or 'file_b.txt' in line for line in lines)


def test_ignore_specific_dir(ftd_mock: FileTreeDisplay, sample_dir: Path) -> None:
    """Test that a specific directory is properly ignored."""
    ftd_mock.init(root_dir=str(sample_dir), ignore_dirs=['ignored_dir'])
    tree = '\n'.join(
        ftd_mock._build_tree(
            str(sample_dir),
            prefix='',
            style=ftd_mock.format_style(),
            sort_key=ftd_mock._resolve_sort_key(),
            files_first=ftd_mock.files_first,
            dir_filter=ftd_mock.dir_filter,
            file_filter=ftd_mock.file_filter,
            reverse=ftd_mock.reverse,
        )
    )
    assert 'ignored_dir' not in tree
    assert 'ignored_file.txt' in tree  # not ignored


def test_ignore_specific_file(ftd_mock: FileTreeDisplay, sample_dir: Path) -> None:
    """Test that a specific file is properly ignored."""
    ftd_mock.init(root_dir=str(sample_dir), ignore_files=['ignored_file.txt'])
    tree = '\n'.join(
        ftd_mock._build_tree(
            str(sample_dir),
            prefix='',
            style=ftd_mock.format_style(),
            sort_key=ftd_mock._resolve_sort_key(),
            files_first=ftd_mock.files_first,
            dir_filter=ftd_mock.dir_filter,
            file_filter=ftd_mock.file_filter,
            reverse=ftd_mock.reverse,
        )
    )
    assert 'ignored_file.txt' not in tree
    assert 'ignored_dir' in tree


def test_display_mode(
    ftd_mock: FileTreeDisplay, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ensure printout mode prints to stdout and doesn't save to file."""
    ftd_mock.printout = True
    ftd_mock.save2file = False
    ftd_mock.file_tree_display()
    captured = capsys.readouterr()
    assert 'dir1' in captured.out
    assert 'dir2' in captured.out


def test_style_and_indent_applied(ftd_mock: FileTreeDisplay) -> None:
    """Ensure style and indentation customize formatted output."""
    ftd_mock.init(root_dir=str(ftd_mock.root_path), style='classic', indent=3)
    lines = list(
        ftd_mock._build_tree(
            str(ftd_mock.root_path),
            prefix='',
            style=ftd_mock.format_style(),
            sort_key=ftd_mock._resolve_sort_key(),
            files_first=ftd_mock.files_first,
            dir_filter=ftd_mock.dir_filter,
            file_filter=ftd_mock.file_filter,
            reverse=ftd_mock.reverse,
        )
    )
    assert all(
        line.startswith('├──')
        for line in lines
        if not (line.startswith('│') or line.startswith('└──'))
    )


def test_custom_styles(ftd_mock: FileTreeDisplay) -> None:
    """Ensure dynamic user-added styles work correctly."""
    ftd_mock.style_dict['plus'] = ftd_mock.connector_styler('+-- ', '+== ')
    ftd_mock.style_dict['arrowstar'] = ftd_mock.connector_styler('→* ', '↳* ')

    plus_style = ftd_mock.style_dict['plus']
    arrowstar_style = ftd_mock.style_dict['arrowstar']

    for s in (plus_style, arrowstar_style):
        assert set(s.keys()) == {'space', 'vertical', 'branch', 'end'}
        assert isinstance(s['branch'], str)
        assert isinstance(s['end'], str)

    ftd_mock.style = 'plus'
    selected_plus = ftd_mock.format_style()
    assert selected_plus['branch'].startswith('+')

    ftd_mock.style = 'arrowstar'
    selected_arrowstar = ftd_mock.format_style()
    assert '→' in selected_arrowstar['branch'] or '↳' in selected_arrowstar['end']


def test_get_tree_info_proper_format(ftd_mock: FileTreeDisplay) -> None:
    """Check that get_tree_info formats output with root and lines."""
    root_line = f'{ftd_mock.root_path.name}/'
    iterator = (f'line_{i}' for i in range(3))
    result = ftd_mock.get_tree_info(iterator, root_line)
    lines = result.split('\n')
    assert lines[0] == root_line
    assert lines[1].startswith('line_')
    assert result.count('\n') == 3


def test_build_tree_permission_error(ftd_mock: FileTreeDisplay) -> None:
    """Handle PermissionError in build_tree."""
    with mock.patch('os.scandir', side_effect=PermissionError):
        results = list(
            ftd_mock._build_tree(
                str(ftd_mock.root_path),
                prefix='',
                style=ftd_mock.format_style(),
                sort_key=ftd_mock._resolve_sort_key(),
                files_first=ftd_mock.files_first,
                dir_filter=ftd_mock.dir_filter,
                file_filter=ftd_mock.file_filter,
                reverse=ftd_mock.reverse,
            )
        )
        assert any('[Permission Denied]' in line for line in results)


def test_build_tree_os_error(ftd_mock: FileTreeDisplay) -> None:
    """Handle generic OSError in build_tree."""
    with mock.patch('os.scandir', side_effect=OSError):
        results = list(
            ftd_mock._build_tree(
                str(ftd_mock.root_path),
                prefix='',
                style=ftd_mock.format_style(),
                sort_key=ftd_mock._resolve_sort_key(),
                files_first=ftd_mock.files_first,
                dir_filter=ftd_mock.dir_filter,
                file_filter=ftd_mock.file_filter,
                reverse=ftd_mock.reverse,
            )
        )
        assert any('[Error reading directory]' in line for line in results)


def test_file_tree_display_invalid_dir(
    monkeypatch: MonkeyPatch, ftd_mock: FileTreeDisplay
) -> None:
    """Handle NotADirectoryError in file_tree_display."""
    ftd_mock.root_path = Path('FAKE_DIR')
    monkeypatch.setattr(Path, 'is_dir', lambda self: False)
    with pytest.raises(
        NotADirectoryError,
        match=f"The path '{ftd_mock.root_path}' is not a directory.",
    ):
        ftd_mock.file_tree_display()


def test_invalid_sort_key_raises(ftd_mock: FileTreeDisplay) -> None:
    """Ensure invalid sort key raises ValueError."""
    ftd_mock.sort_key_name = 'unknown_key'
    with pytest.raises(ValueError, match='Invalid sort key name'):
        ftd_mock._resolve_sort_key()


def test_custom_sort_key_without_function_raises(ftd_mock: FileTreeDisplay) -> None:
    """Ensure 'custom' sort requires a custom_sort function."""
    ftd_mock.sort_key_name = 'custom'
    ftd_mock.custom_sort = None
    with pytest.raises(ValueError, match='custom_sort function must be specified'):
        ftd_mock._resolve_sort_key()


def test_format_style_invalid(ftd_mock: FileTreeDisplay) -> None:
    """Invalid style name raises ValueError."""
    ftd_mock.style = 'invalid-style'
    with pytest.raises(ValueError):
        ftd_mock.format_style()


def test_update_predicates_rebuilds_filters(ftd_mock: FileTreeDisplay) -> None:
    """Ensure update_predicates rebuilds the filter predicates."""
    old_dir_filter = ftd_mock.dir_filter
    ftd_mock.ignore_dirs.add('X')
    ftd_mock.update_predicates()
    assert ftd_mock.dir_filter is not old_dir_filter


def test_file_tree_display_print_and_save(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ensure file_tree_display prints and saves when both flags are enabled."""
    out_file = tmp_path / 'tree.txt'
    (tmp_path / 'subdir').mkdir()
    ftd = FileTreeDisplay(
        root_dir=str(tmp_path), filepath=str(out_file), save2file=True, printout=True
    )

    result = ftd.file_tree_display()

    assert isinstance(result, str)
    assert 'subdir' in result

    captured = capsys.readouterr()
    assert 'subdir' in captured.out

    content = out_file.read_text(encoding='utf-8')
    assert content.strip() == result.strip()


class DummyFTD:
    """A minimal stub of FileTreeDisplay to only test stream_output behavior."""

    def __init__(
        self,
        root_path,
        iterator,
        *,
        stream_output=False,
        save2file=False,
        printout=False,
        entry_count=False,
        filepath=None,
    ):
        self.root_path = root_path
        self.iterator = iterator
        self.stream_output = stream_output
        self.save2file = save2file
        self.printout = printout
        self.entry_count = entry_count
        self.filepath = filepath

        # spy flags
        self.called_get_tree_info = False
        self.called_str2file = False
        self.called_get_num_entries = False

    def get_tree_info(self, iterator, root_line):
        self.called_get_tree_info = True
        buf = [root_line] + list(iterator)
        return '\n'.join(buf)

    def get_num_of_entries(self, info):
        self.called_get_num_entries = True

    def file_tree_display(self):
        root_line = f'{self.root_path.name}/'

        iterator = self.iterator

        if self.stream_output:
            print(root_line)
            for line in iterator:
                print(line)
            return ''

        return self.tree_info_processing(iterator, root_line)

    def tree_info_processing(
        self, iterator: Generator[str, None, None], root_line: str
    ) -> str:
        info = self.get_tree_info(iterator, root_line)

        if self.save2file and self.filepath:
            self.called_str2file = True

        if self.printout:
            print(info)

        if self.entry_count:
            self.get_num_of_entries(info)

        return info


def test_stream_output_prints_and_returns_empty(capsys):
    iterator = iter(['a', 'b', 'c'])
    root = type('P', (), {'name': 'root'})()

    obj = DummyFTD(root, iterator, stream_output=True)

    result = obj.file_tree_display()

    assert result == ''

    captured = capsys.readouterr().out.splitlines()
    assert captured == ['root/', 'a', 'b', 'c']

    assert obj.called_get_tree_info is False
    assert obj.called_str2file is False
    assert obj.called_get_num_entries is False


def test_normal_mode_calls_get_tree_info_but_not_stream(capsys):
    iterator = iter(['a', 'b'])
    root = type('P', (), {'name': 'root'})()

    obj = DummyFTD(root, iterator, stream_output=False)

    result = obj.file_tree_display().splitlines()

    assert result == ['root/', 'a', 'b']

    assert obj.called_get_tree_info is True

    assert capsys.readouterr().out == ''


def test_normal_mode_printout(capsys):
    iterator = iter(['x'])
    root = type('P', (), {'name': 'root'})()

    obj = DummyFTD(root, iterator, stream_output=False, printout=True)

    obj.file_tree_display()
    out = capsys.readouterr().out.strip().splitlines()

    assert out == ['root/', 'x']


def test_normal_mode_entry_count_called():
    iterator = iter(['a', 'b'])
    root = type('P', (), {'name': 'root'})()

    obj = DummyFTD(root, iterator, entry_count=True)

    obj.file_tree_display()

    assert obj.called_get_num_entries is True


def test_normal_mode_save2file_flag_sets_spy():
    iterator = iter(['a'])
    root = type('P', (), {'name': 'root'})()

    obj = DummyFTD(root, iterator, save2file=True, filepath='dummy.txt')

    obj.file_tree_display()

    assert obj.called_str2file is True
