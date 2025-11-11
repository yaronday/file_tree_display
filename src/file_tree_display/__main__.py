"""CLI interface for FileTreeDisplay."""

import sys
import argparse
import ast
from pathlib import Path
from typing import Any

from .ftd import FileTreeDisplay
from nano_dev_utils.common import load_cfg_file
from ._constants import DEFAULT_SFX


def parse() -> argparse.Namespace:
    """
    Parse and normalize CLI arguments for the FileTreeDisplay tool.

    Supports space-separated or Python-style list inputs for:
        --ignore-dirs, --ignore-files, --include-dirs, --include-files.

    Returns:
        argparse.Namespace: Parsed and normalized arguments ready for use.
    """
    parser = argparse.ArgumentParser(
        description=(
            'CLI tool for displaying a filtered file tree.\n'
            'Each of the ignore/include options supports either space-separated '
            'or Python-style list input.'
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('--cfg', type=str, help='Path to JSON config file.')
    parser.add_argument('--root-dir', '-r', type=str, help='Root directory to display.')
    parser.add_argument('--filepath', '-o', type=str, help='Output file path.')
    parser.add_argument(
        '--ignore-dirs', nargs='*', default=None, help='Directories to ignore.'
    )
    parser.add_argument(
        '--ignore-files', nargs='*', default=None, help='Files to ignore.'
    )
    parser.add_argument(
        '--include-dirs', nargs='*', default=None, help='Directories to include.'
    )
    parser.add_argument(
        '--include-files', nargs='*', default=None, help='Files to include.'
    )
    parser.add_argument(
        '--style',
        '-s',
        choices=['classic', 'dash', 'arrow', 'plus'],
        default='classic',
        help='Tree connector style.',
    )
    parser.add_argument(
        '--indent', '-i', type=int, default=2, help='Indent width per level.'
    )
    parser.add_argument(
        '--files-first',
        '-f',
        action='store_true',
        default=False,
        help='List files before directories.',
    )
    parser.add_argument(
        '--skip-sorting',
        action='store_true',
        default=False,
        help='Disable sorting.',
    )
    parser.add_argument(
        '--sort-key',
        choices=['natural', 'lex'],
        default='natural',
        help='Sort key for files (custom sort available only in Python API).',
    )
    parser.add_argument(
        '--reverse',
        action='store_true',
        default=False,
        help='Reverse sort order.',
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        default=False,
        help='Do not save to file.',
    )
    parser.add_argument(
        '--printout',
        '-p',
        action='store_true',
        default=False,
        help='Print tree to stdout.',
    )
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'{FileTreeDisplay.get_version()}',
    )

    # store defaults before parsing
    defaults = {k: v for k, v in vars(parser.parse_args([])).items() if k != 'cfg'}

    args = parser.parse_args()

    def normalize_list(argval: list[str] | None) -> list[str] | None:
        """
        Normalize CLI list-like arguments.

        Supports both:
          - space-separated inputs: e.g. --ignore-dirs .git .idea
          - single Python-style list string: e.g. --ignore-dirs "['.git', '.idea']"

        Returns:
            list[str] | None: A clean list of strings or None if empty.
        Raises:
            ValueError: If a malformed Python-style list string is detected.
        """
        if not argval:
            return None
        if len(argval) == 1 and argval[0].startswith('['):
            try:
                return ast.literal_eval(argval[0])
            except (ValueError, SyntaxError):
                raise ValueError(f'Invalid list syntax: {argval[0]}')
        return argval

    for key in ('ignore_dirs', 'ignore_files', 'include_dirs', 'include_files'):
        setattr(args, key, normalize_list(getattr(args, key)))

    setattr(args, '_defaults', defaults)
    return args


def merge_config(
    cli_args: argparse.Namespace, cfg_dict: dict[str, Any] | None
) -> dict[str, Any]:
    """Merge CLI arguments with an optional configuration file.

    CLI arguments explicitly provided by the user override config values.
    CLI defaults do not override config values.
    """
    cfg_dict = cfg_dict or {}
    defaults = getattr(cli_args, '_defaults', {})
    cli_values = vars(cli_args)

    user_args = {
        k: v
        for k, v in cli_values.items()
        if k not in ('cfg', '_defaults') and v != defaults.get(k)
    }

    merged = {**cfg_dict, **user_args}
    return merged


def main() -> None:
    """Entry point for the FileTreeDisplay CLI.

    Loads configuration, validates input, merges CLI options,
    and executes file tree generation with appropriate output behavior.
    """
    args = parse()
    cfg_dict = load_cfg_file(args.cfg)
    opts = merge_config(args, cfg_dict)

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
