# file_tree_display

A utility for generating a visually structured directory tree.

## Modules

## `file_tree_display.py`

This core module supports recursive traversal, customizable hierarchy styles, and inclusion / exclusion  
patterns for directories and files.  
Output can be displayed in the console or saved to a file.


#### Key Features

- Recursively displays and logs directory trees
- Efficient directory traversal
- Blazing fast (see Benchmarks below)
- Generates human-readable file tree structure 
- Supports including / ignoring specific directories or files via pattern matching
- Customizable tree display output
- Optionally saves the resulting tree to a text file
- Lightweight, flexible and easily configurable


### [Benchmarks](https://github.com/yaronday/file_tree_display/blob/master/docs/BENCHMARKS.md)

#### Class Overview

**`FileTreeDisplay`**
Constructs and manages the visual representation of a folder structure of a path or of a disk drive.

**Initialization Parameters**

| Parameter       | Type                            | Description                                                                  |
|:----------------|:--------------------------------|:-----------------------------------------------------------------------------|
| `root_dir`      | `str`                           | Path to the directory to scan.                                               |
| `filepath`      | `str / None`                    | Optional output destination for the saved file tree.                         |                                               
| `ignore_dirs`   | `list[str] or set[str] or None` | Directory names or patterns to skip.                                         |                                                
| `ignore_files`  | `list[str] or set[str] or None` | File names or patterns to skip.                                              |
| `include_dirs`  | `list[str] or set[str] or None` | Only include specified folder names or patterns.                             |
| `include_files` | `list[str] or set[str] or None` | Only include specified file names or patterns, '*.pdf' - only include pdfs.  |
| `style`         | `str`                           | Characters used to mark hierarchy levels. Defaults to `'classic'`.           |
| `indent`        | `int`                           | Number of style characters per level. Defaults `2`.                          |
| `files_first`   | `bool`                          | Determines whether to list files first. Defaults to False.                   |
| `skip_sorting`  | `bool`                          | Skip sorting directly, even if configured.                                   |
| `sort_key_name` | `str`                           | Sort key func name. Natural, Lexicographic or custom. Defaults to 'natural'. |
| `reverse`       | `bool`                          | Reversed sorting order.                                                      |
| `custom_sort`   | `Callable[[str], Any] / None`   | Custom sort key function.                                                    |
| `title`         | `str`                           | Custom title shown in the output.                                            |
| `save2file`     | `bool`                          | Save file tree (folder structure) info into a file.                          |
| `stream_output` | `bool`                          | Stream print tree content without building a buffer.                         |
| `printout`      | `bool`                          | Print the generated tree to stdout.                                          |
| `entry_count`   | `bool`                          | Show number of scanned subfolders and files. Defaults to False.              |

#### Core Methods

- `file_tree_display(save2file: bool = True) -> str | None`  
Generates the directory tree. If `save2file=True`, saves the output; otherwise prints it directly.

- `_build_tree(dir_path, *, prefix, style, sort_key,   
   files_first, dir_filter, file_filter, reverse) -> Generator[str, None, None]`  
Yields formatted lines representing the directory tree rooted at dir_path using a recursive DFS.

| Parameter                           | Type                    | Description                                                                  |
|-------------------------------------|-------------------------|------------------------------------------------------------------------------|
| **`dir_path`**                      | `str`                   | Path to the directory being traversed.                                       |
| **`prefix`**                        | `str`                   | Current indentation prefix for nested entries.                               |
| **`style`**                         | `dict[str, str]`        | Connector style mapping with keys: `branch`, `end`, `space`, and `vertical`. |
| **`sort_key`**                      | `Callable[[str], Any]`  | Function used to sort directory and file names.                              |
| **`files_first`**                   | `bool`                  | If `True`, list files before subdirectories.                                 |
| **`dir_filter`**, **`file_filter`** | `Callable[[str], bool]` | Predicates to include or exclude directories and files.                      |                                                                                                     |
| **`reverse`**                       | `bool`                  | If `True`, reverses the sort order.                                          |


#### Example Usage

```python
from pathlib import Path
from file_tree_display import FileTreeDisplay

root = r'c:/your_root_dir'
target_path = r'c:/your_target_path'
filename = 'filetree.md'
filepath = str(Path(target_path, filename))

ftd = FileTreeDisplay(root_dir=root,
                      ignore_dirs=['.git', 'node_modules', '.idea'],
                      ignore_files=['.gitignore', '*.toml'], 
                      style='classic',
                      include_dirs=['src', 'tests', 'snapshots'],
                      filepath=filepath, 
                      sort_key_name='custom',
                      custom_sort=(lambda x: any(ext in x.lower() for ext in ('jpg', 'png'))),
                      files_first=True,
                      reverse=True
                     )
ftd.file_tree_display()
```

#### Custom connector style   
You can define and register your own connector styles at runtime by adding entries to style_dict:

```Python
from file_tree_display import FileTreeDisplay
ftd = FileTreeDisplay(root_dir=".")
ftd.style_dict["plus2"] = ftd.connector_styler("+-- ", "+== ")
ftd.style = "plus2"
ftd.printout = True
ftd.file_tree_display()
```

## FTD CLI — File Tree Display

The **FTD CLI** (`ftd`) is a lightweight, configurable command-line tool for displaying or exporting a formatted file tree of a given directory.  
It’s designed for flexibility, allowing users to control inclusion/exclusion rules, visual style, sorting behavior, and output options.

---

### Features

* Generate a clean, formatted file tree of any directory
* Choose from multiple connector styles (`classic`, `dash`, `arrow`, `plus`)
* Fine-grained control over included/excluded files and directories
* Flexible sorting modes (`natural`, `lex`, or `custom`)
* Optionally export the tree to a file or print directly to stdout
* Supports configuration via JSON config file

---

### Usage

```bash
ftd [OPTIONS]
```

Example:

```bash
ftd --root-dir ./src --style arrow --files-first --printout --entry-count
```

This displays the tree structure of the `src` directory using the *arrow* connector style, listing files before directories, and prints the output to the console.

---

### Command-Line Options

| Option            | Alias     | Type   | Description                                                | Default   |
|-------------------|-----------|--------|------------------------------------------------------------|-----------|
| `--cfg`           | –         | `str`  | Path to a JSON configuration file.                         | –         |
| `--root-dir`      | `-r`      | `str`  | Root directory to display.                                 | –         |
| `--filepath`      | `-o`      | `str`  | Output file path for exported tree.                        | –         |
| `--ignore-dirs`   | –         | `str…` | Directories to exclude from the tree.                      | –         |
| `--ignore-files`  | –         | `str…` | Files to exclude from the tree.                            | –         |
| `--include-dirs`  | –         | `str…` | Directories to explicitly include.                         | –         |
| `--include-files` | –         | `str…` | Files to explicitly include.                               | –         |
| `--style`         | `-s`      | `str`  | Tree connector style (`classic`, `dash`, `arrow`, `plus`). | `classic` |
| `--indent`        | `-i`      | `int`  | Indent width (spaces) per directory level.                 | `2`       |
| `--files-first`   | `-f`      | flag   | List files before directories.                             | `False`   |
| `--skip-sorting`  | –         | flag   | Disable sorting altogether.                                | `False`   |
| `--sort-key`      | –         | `str`  | Sorting key: `natural` or `lex`.                           | `natural` |
| `--reverse`       | –         | flag   | Reverse the sort order.                                    | `False`   |
| `--no-save`       | –         | flag   | Do not save output to file.                                | `False`   |
| `--stream-output` | `-stream` | flag   | Stream tree content without building a buffer.             | `False`   |
| `--printout`      | `-p`      | flag   | Print the generated tree to stdout.                        | `False`   |
| `--entry-count`   |           | flag   | Show number of scanned subfolders and files.               | `False`   |
| `--version`       | `-v`      | flag   | Show the current version of FTD and exit.                  | –         |

---

### Configuration via JSON file

FTD can also load parameters from a JSON config file:

```json
{
  "root_dir": "./project",
  "ignore_dirs": ["__pycache__", "build"],
  "ignore_files": [".DS_Store"],
  "style": "dash",
  "files_first": true,
  "printout": true,
  "entry_count": true
}
```

Run it using:

```bash
ftd --cfg path/to/config.json
```

Command-line arguments always **override** config file values.

---

### Examples

Display the current directory with default settings:

```bash
ftd
```

Display a tree with dashed connectors, ignoring test folders, and print it:

```bash
ftd -r ./src --ignore-dirs tests --style dash --printout
```

Streaming out tree content, skipping buffer filling, file creation and entries counting:

```bash
ftd -stream
```

Export a formatted tree to a file:

```bash
ftd -r ./app --filepath tree.txt
```

Reverse lexical sort with 4-space indentation:

```bash
ftd -r ./data --sort-key lex --reverse --indent 4
```

---

### Output Example

```text
nano_dev_utils/
├── src/
│ └── nano_dev_utils/
│   ├── __init__.py
│   ├── __version__.py
│   ├── _constants.py
│   ├── common.py
│   ├── dynamic_importer.py
│   ├── release_ports.py
│   └── timers.py
├── tests/
│ ├── test_timers/
│ │ ├── __init__.py
│ │ ├── conftest.py
│ │ ├── test_duration_formatter.py
│ │ ├── test_timer.py
│ │ └── test_timers_async.py
│ ├── __init__.py
│ ├── test_common.py
│ ├── test_dynamic_importer.py
│ └── test_release_ports.py
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── pyproject.toml
├── README.md
├── ruff.toml
├── update_package.py
└── uv.lock
Scanned 4 subfolders and 24 files.
```

### [Unicode Output Notes](https://github.com/yaronday/file_tree_display/blob/master/docs/UNICODE_OUTPUT_NOTES.md)

---

***

## License
This project is licensed under the MIT License. 
See [LICENSE](https://github.com/yaronday/file_tree_display/blob/master/LICENSE) for details.