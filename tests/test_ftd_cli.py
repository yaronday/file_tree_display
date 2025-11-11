import sys
import json
import argparse
from pathlib import Path
import pytest

import file_tree_display.__main__ as cli


@pytest.fixture
def sample_cfg(tmp_path: Path, sample_dir: Path) -> Path:
    """Creates a temporary JSON config file for CLI testing."""
    cfg = {
        'root_dir': str(sample_dir),
        'indent': 4,
        'style': 'arrow',
        'ignore_dirs': ['.git', '.venv'],
    }
    cfg_path = tmp_path / 'cfg.json'
    cfg_path.write_text(json.dumps(cfg))
    return cfg_path


def test_parse_space_separated(monkeypatch):
    argv = ['prog', '--ignore-dirs', '.git', '.idea', '.venv']
    monkeypatch.setattr(sys, 'argv', argv)

    args = cli.parse()
    assert args.ignore_dirs == ['.git', '.idea', '.venv']
    assert '_defaults' in vars(args)
    assert args._defaults['style'] == 'classic'


def test_parse_python_style(monkeypatch):
    argv = ['prog', '--ignore-dirs', "['.git', '.idea']"]
    monkeypatch.setattr(sys, 'argv', argv)
    args = cli.parse()
    assert args.ignore_dirs == ['.git', '.idea']


def test_parse_invalid_list(monkeypatch):
    argv = ['prog', '--ignore-dirs', '[.git, .idea]']  # invalid literal
    monkeypatch.setattr(sys, 'argv', argv)
    with pytest.raises(ValueError):
        cli.parse()


def make_namespace(**kwargs):
    ns = argparse.Namespace(**kwargs)
    # mimic parser defaults
    defaults = {'indent': 2, 'style': 'classic'}
    setattr(ns, '_defaults', defaults)
    return ns


def test_merge_config_cli_overrides():
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=8, style='classic', cfg=None)
    merged = cli.merge_config(args, cfg)
    assert merged['indent'] == 8  # CLI override
    assert merged['style'] == 'arrow'  # config preserved (CLI = default)


def test_merge_config_defaults_dont_override():
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=2, style='classic', cfg=None)
    merged = cli.merge_config(args, cfg)
    assert merged['indent'] == 4
    assert merged['style'] == 'arrow'


def test_merge_config_missing_defaults_used():
    cfg = {}
    args = make_namespace(indent=2, style='classic', cfg=None)
    merged = cli.merge_config(args, cfg)
    assert merged.get('indent', 2) == 2
    assert merged.get('style', 'classic') == 'classic'


class DummyFTD:
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
    """Ensures main() runs end-to-end successfully."""
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


def test_main_without_cfg(monkeypatch, sample_dir):
    argv = ['prog', '--root-dir', str(sample_dir)]
    monkeypatch.setattr(sys, 'argv', argv)
    monkeypatch.setattr(cli, 'FileTreeDisplay', DummyFTD)
    monkeypatch.setattr(cli, 'load_cfg_file', lambda _: {})

    cli.main()
    assert DummyFTD.called == 'executed'


def test_cli_explicit_overrides_config():
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=8, style='classic', cfg=None)
    merged = cli.merge_config(args, cfg)

    # explicit CLI should override config file
    assert merged['indent'] == 8
    assert merged['style'] == 'arrow'


def test_cli_defaults_do_not_override_config():
    cfg = {'indent': 4, 'style': 'arrow'}
    args = make_namespace(indent=2, style='classic', cfg=None)  # matches defaults
    merged = cli.merge_config(args, cfg)

    # CLI defaults should NOT override config file
    assert merged['indent'] == 4
    assert merged['style'] == 'arrow'
