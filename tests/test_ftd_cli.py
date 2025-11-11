import sys
import pytest
import argparse

import file_tree_display.__main__ as cli


def test_parse_collects_defaults(monkeypatch, cli_instance):
    argv = ['prog', '--ignore-dirs', '.git', '.idea']
    monkeypatch.setattr(sys, 'argv', argv)
    args = cli_instance.parse()
    assert isinstance(args, argparse.Namespace)
    assert '_defaults' in vars(args)
    assert args._defaults['style'] == 'classic'


def make_namespace(**kwargs):
    ns = argparse.Namespace(**kwargs)
    setattr(ns, '_defaults', {'indent': 2, 'style': 'classic'})
    return ns


def test_cli_explicit_overrides_config(cli_instance):
    """CLI explicit values must override config values."""
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=8, style='classic', cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['indent'] == 8
    assert merged['style'] == 'arrow'


def test_cli_defaults_do_not_override_config(cli_instance):
    """CLI defaults must never override config values."""
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=2, style='classic', cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['indent'] == 4
    assert merged['style'] == 'arrow'


def test_config_list_string_normalized(cli_instance):
    """Python-style list strings in config must normalize correctly."""
    cfg = {'ignore_dirs': "['.git', '.idea', '.venv']"}
    args = make_namespace(cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['ignore_dirs'] == ['.git', '.idea', '.venv']


def test_config_json_list_remains(cli_instance):
    """JSON-style lists remain untouched."""
    cfg = {'ignore_dirs': ['.git', '.idea']}
    args = make_namespace(cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['ignore_dirs'] == ['.git', '.idea']


def test_config_and_cli_lists_are_merged(cli_instance):
    """Config and CLI lists merge (union, order preserved)."""
    cfg = {'ignore_dirs': ['.git', '.venv']}
    args = make_namespace(ignore_dirs=['.idea', '__pycache__'], cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['ignore_dirs'] == ['.git', '.venv', '.idea', '__pycache__']


def test_config_and_cli_lists_deduplicate(cli_instance):
    """Merged lists must not contain duplicates."""
    cfg = {'ignore_dirs': ['.git', '.idea']}
    args = make_namespace(ignore_dirs=['.idea', '.venv'], cfg=None)
    merged = cli_instance.merge_config(args, cfg)
    assert merged['ignore_dirs'] == ['.git', '.idea', '.venv']


def test_merge_handles_mixed_sources(cli_instance):
    """Mix of config lists, CLI scalar, and config-only keys should merge cleanly."""
    cfg = {
        'ignore_dirs': "['.git', '.venv']",
        'include_files': ['README.md'],
        'style': 'arrow',
    }
    args = make_namespace(
        ignore_dirs=['.idea'], include_dirs=['src'], indent=8, cfg=None
    )
    merged = cli_instance.merge_config(args, cfg)

    assert merged['ignore_dirs'] == ['.git', '.venv', '.idea']
    assert merged['include_dirs'] == ['src']
    assert merged['include_files'] == ['README.md']
    assert merged['style'] == 'arrow'
    assert merged['indent'] == 8


class DummyFTD:
    """Stub for FileTreeDisplay."""

    called = None

    @classmethod
    def get_version(cls):
        return '0.0-test'

    def __init__(self, **kwargs):
        DummyFTD.called = 'init'
        self.kwargs = kwargs

    def file_tree_display(self):
        DummyFTD.called = 'executed'


def test_main_executes(monkeypatch, sample_cfg, sample_dir):
    """Ensures CLI runs end-to-end successfully."""
    argv = [
        'prog',
        '--cfg',
        str(sample_cfg),
        '--root-dir',
        str(sample_dir),
        '--printout',
    ]
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr(cli, 'FileTreeDisplay', DummyFTD)
    cli.main()
    assert DummyFTD.called == 'executed'


def test_main_invalid_root(monkeypatch, tmp_path, sample_cfg):
    argv = ['prog', '--cfg', str(sample_cfg), '--root-dir', str(tmp_path / 'missing')]
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(SystemExit):
        cli.main()


def test_main_no_cfg(monkeypatch, sample_dir):
    """Runs successfully without config file."""
    argv = ['prog', '--root-dir', str(sample_dir)]
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr(cli, 'FileTreeDisplay', DummyFTD)
    monkeypatch.setattr(cli, 'load_cfg_file', lambda _: {})
    cli.main()
    assert DummyFTD.called == 'executed'
