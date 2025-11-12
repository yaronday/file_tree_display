"""CLI interface for FileTreeDisplay."""

import sys
import ast
import argparse
from pathlib import Path
from typing import Any

from .ftd import FileTreeDisplay
from nano_dev_utils.common import load_cfg_file
from ._constants import DEFAULT_SFX

LIST_KEYS = {'ignore_dirs', 'ignore_files', 'include_dirs', 'include_files'}


class FileTreeCLI:
    """Command-line interface for FileTreeDisplay."""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description=(
                'CLI tool for displaying a filtered file tree.\n'
                'Each of the ignore/include options supports either space-separated '
                'or Python-style list input.'
            ),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self._add_arguments()
        self.defaults = None

    def _add_arguments(self) -> None:
        self.parser.add_argument('--cfg', type=str, help='Path to JSON config file.')
        self.parser.add_argument(
            '--root-dir', '-r', type=str, help='Root directory to display.'
        )
        self.parser.add_argument('--filepath', '-o', type=str, help='Output file path.')
        self.parser.add_argument(
            '--ignore-dirs', nargs='*', default=None, help='Directories to ignore.'
        )
        self.parser.add_argument(
            '--ignore-files', nargs='*', default=None, help='Files to ignore.'
        )
        self.parser.add_argument(
            '--include-dirs', nargs='*', default=None, help='Directories to include.'
        )
        self.parser.add_argument(
            '--include-files', nargs='*', default=None, help='Files to include.'
        )
        self.parser.add_argument(
            '--style',
            '-s',
            choices=['classic', 'dash', 'arrow', 'plus'],
            default='classic',
        )
        self.parser.add_argument(
            '--indent', '-i', type=int, default=2, help='Indent width per level.'
        )
        self.parser.add_argument(
            '--files-first', '-f', action='store_true', default=False
        )
        self.parser.add_argument('--skip-sorting', action='store_true', default=False)
        self.parser.add_argument(
            '--sort-key', choices=['natural', 'lex'], default='natural'
        )
        self.parser.add_argument('--reverse', action='store_true', default=False)
        self.parser.add_argument('--no-save', action='store_true', default=False)
        self.parser.add_argument('--printout', '-p', action='store_true', default=False)
        self.parser.add_argument(
            '--version',
            '-v',
            action='version',
            version=f'{FileTreeDisplay.get_version()}',
        )

    def parse(self) -> argparse.Namespace:
        """Parse CLI arguments and attach defaults for later comparison."""
        self.defaults = {
            k: v for k, v in vars(self.parser.parse_args([])).items() if k != 'cfg'
        }
        args = self.parser.parse_args()
        setattr(args, '_defaults', self.defaults)
        return args

    def merge_config(
        self, cli_args: argparse.Namespace, cfg_dict: dict[str, Any] | None
    ) -> dict[str, Any]:
        """
        Merge CLI arguments with an optional configuration file.

        Precedence:
          CLI explicit > Config > Defaults.
        List-type fields are merged (union, preserving order).
        """
        cfg_dict = cfg_dict or {}
        defaults = getattr(cli_args, '_defaults', {})
        cli_values = vars(cli_args)
        normalize_list = self.normalize_list

        cfg_norm = {
            k: (normalize_list(v) if k in LIST_KEYS else v) for k, v in cfg_dict.items()
        }

        # detect explicit CLI args (different from defaults)
        user_args = {
            k: v
            for k, v in cli_values.items()
            if k not in ('cfg', '_defaults') and v != defaults.get(k)
        }

        merged: dict[str, Any] = dict(cfg_norm)

        for key, value in user_args.items():
            if key in LIST_KEYS:
                cfg_list = cfg_norm.get(key) or []
                cli_list = normalize_list(value) or []
                merged[key] = list(
                    dict.fromkeys(cfg_list + cli_list)
                )  # merge, deduplicate
            else:
                merged[key] = value

        # normalize again in case config-only fields were unlisted
        for key in LIST_KEYS:
            merged[key] = normalize_list(merged.get(key))

        return merged

    @staticmethod
    def normalize_list(value: Any) -> list[str] | None:
        """Normalize list-like inputs from CLI or config.

        Supports:
          - space-separated inputs: e.g. --ignore-dirs .git .idea
          - single Python-style list strings: e.g. "['.git', '.idea']"
          - JSON-style lists directly
        """
        if not value:
            return None
        if isinstance(value, str):
            s = value.strip()
            if s.startswith('[') and s.endswith(']'):
                try:
                    return ast.literal_eval(s)
                except (ValueError, SyntaxError):
                    raise ValueError(f'Invalid list syntax: {value}')
            return [value]
        if isinstance(value, (list, tuple, set)):
            return list(value)
        return [str(value)]


def main() -> None:
    cli = FileTreeCLI()
    args = cli.parse()
    cfg_dict = load_cfg_file(args.cfg)
    opts = cli.merge_config(args, cfg_dict)

    root_dir = Path(opts.get('root_dir') or Path.cwd())
    if not root_dir.exists():
        sys.exit(f"Error: root directory '{root_dir}' does not exist.")

    filepath = opts.get('filepath')
    if not filepath and not opts.get('no_save'):
        filepath = str(root_dir.with_name(f'{root_dir.name}{DEFAULT_SFX}'))

    ftd = FileTreeDisplay(
        root_dir=str(root_dir),
        filepath=filepath,
        ignore_dirs=opts.get('ignore_dirs') or [],
        ignore_files=opts.get('ignore_files') or [],
        include_dirs=opts.get('include_dirs') or [],
        include_files=opts.get('include_files') or [],
        style=opts.get('style', 'classic'),
        indent=int(opts.get('indent', 2)),
        files_first=bool(opts.get('files_first', False)),
        skip_sorting=bool(opts.get('skip_sorting', False)),
        sort_key_name=opts.get('sort_key', 'natural'),
        reverse=bool(opts.get('reverse', False)),
        save2file=not opts.get('no_save', False),
        printout=opts.get('printout', False),
    )

    try:
        ftd.file_tree_display()
    except Exception as e:
        sys.exit(f'Error: {e}')


if __name__ == '__main__':
    main()
