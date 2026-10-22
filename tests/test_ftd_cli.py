import pathlib
import sys

import pytest

import file_tree_display.__main__ as cli
from file_tree_display.__main__ import FileTreeCLI, ensure_utf8_stdout, main


@pytest.mark.parametrize(
    'input_val, expected',
    [
        (None, None),
        ([], None),
        ('', None),
        ('["a", "b"]', ['a', 'b']),
        ("['a', 'b']", ['a', 'b']),
        (['a', 'b'], ['a', 'b']),
        (('a', 'b'), ['a', 'b']),
        ({'a', 'b'}, ['a', 'b']),
        ('single_str', ['single_str']),
        (123, ['123']),
    ],
)
def test_normalize_list(input_val, expected):
    result = FileTreeCLI.normalize_list(input_val)
    if expected is None:
        assert result is None
    elif isinstance(input_val, set):
        assert result is not None
        assert sorted(result) == sorted(expected)
    else:
        assert result == expected


def test_normalize_list_invalid_syntax():
    with pytest.raises(ValueError, match='Invalid list syntax'):
        FileTreeCLI.normalize_list('[1, , 2]')


@pytest.mark.parametrize(
    'cli_args, cfg_dict, expected_subset',
    [
        (
            ['ftd', '--style', 'dash'],
            {'indent': 4, 'style': 'classic'},
            {'style': 'dash', 'indent': 4},
        ),
        (
            ['ftd', '--ignore-dirs', 'dir1'],
            {'ignore_dirs': "['dir2']"},
            {'ignore_dirs': ['dir2', 'dir1']},
        ),
        (
            ['ftd'],
            {'ignore_dirs': ['.git'], 'indent': 8},
            {'ignore_dirs': ['.git'], 'indent': 8},
        ),
    ],
)
def test_merge_config(cli_instance, cli_args, cfg_dict, expected_subset):
    parser = cli_instance.parser
    parsed_args = parser.parse_args(cli_args[1:])
    parsed_args._defaults = cli_instance.defaults = {
        k: v for k, v in vars(parser.parse_args([])).items() if k != 'cfg'
    }

    merged = cli_instance.merge_config(parsed_args, cfg_dict)
    for k, v in expected_subset.items():
        assert merged[k] == v


def test_cli_parse(cli_instance, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['ftd', '--indent', '5', '--style', 'arrow'])
    args = cli_instance.parse()
    assert args.indent == 5
    assert args.style == 'arrow'
    assert hasattr(args, '_defaults')


def test_concise_error(cli_instance, capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli_instance.concise_error('test error message')
    assert 'error:' in str(exc_info.value)
    captured = capsys.readouterr()
    assert 'usage:' in captured.err


def test_ensure_utf8_stdout_success():
    ensure_utf8_stdout()


def test_ensure_utf8_stdout_none(monkeypatch):
    """Test when sys.stdout is None."""
    monkeypatch.setattr(sys, 'stdout', None)
    ensure_utf8_stdout()


def test_ensure_utf8_stdout_missing_reconfigure(monkeypatch):
    """Test when sys.stdout lacks the reconfigure method."""

    class PlainStream:
        pass

    monkeypatch.setattr(sys, 'stdout', PlainStream())
    ensure_utf8_stdout()


@pytest.mark.parametrize('exc_type', [LookupError, ValueError, OSError])
def test_ensure_utf8_stdout_handles_exceptions(monkeypatch, exc_type):
    """Test that exceptions during reconfigure are safely caught and ignored."""

    class FaultyStream:
        def reconfigure(self, *, encoding: str) -> None:
            raise exc_type('Reconfiguration failed')

    monkeypatch.setattr(sys, 'stdout', FaultyStream())
    ensure_utf8_stdout()  # Should complete without raising an error


def test_main_success(monkeypatch, sample_dir, sample_cfg):
    monkeypatch.setattr(
        sys,
        'argv',
        ['ftd', '--root-dir', str(sample_dir), '--cfg', str(sample_cfg), '--no-save'],
    )
    main()


def test_main_root_dir_not_exists(monkeypatch, tmp_path):
    non_existent = tmp_path / 'does_not_exit'
    monkeypatch.setattr(sys, 'argv', ['ftd', '--root-dir', str(non_existent)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert 'does not exist' in str(exc_info.value)


@pytest.mark.parametrize(
    'is_drive',
    [False, True],
)
def test_main_filepath_generation(monkeypatch, sample_dir, is_drive):
    if is_drive:

        class MockPath(pathlib.Path):
            def __new__(cls, *args, **kwargs):
                return super().__new__(cls, *args, **kwargs)

            @property
            def name(self):
                return ''

            @property
            def drive(self):
                return 'C:'

        root_path = MockPath(str(sample_dir))
    else:
        root_path = sample_dir / 'dir1'

    def mock_path_factory(*args, **kwargs):
        if args and str(args[0]) != '.':
            return root_path
        return pathlib.Path(*args, **kwargs)

    monkeypatch.setattr(cli, 'Path', mock_path_factory)  # type: ignore[attr-defined]
    monkeypatch.setattr(sys, 'argv', ['ftd', '--root-dir', str(root_path)])
    monkeypatch.setattr(cli.FileTreeDisplay, 'file_tree_display', lambda _self: None)

    main()


def test_main_exception_handling(monkeypatch, sample_dir):
    monkeypatch.setattr(sys, 'argv', ['ftd', '--root-dir', str(sample_dir)])

    def mock_display(_self):
        raise RuntimeError('display failure')

    monkeypatch.setattr(cli.FileTreeDisplay, 'file_tree_display', mock_display)

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert 'Error: display failure' in str(exc_info.value)
