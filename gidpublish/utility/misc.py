
# region [Imports]

from rich.console import Console
from rich.tree import Tree
import os
import pathlib
import sys


from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree
from markdownify import markdownify
console = Console(soft_wrap=True)

from typing import Iterable, Optional, Union
# endregion[Imports]


def recursive_dir_tree(directory: Union[os.PathLike, str], tree: Tree, to_ignore_files: Optional[Iterable[str]] = None, to_ignore_folders: Optional[Iterable[str]] = None) -> None:
    """Recursively build a Tree with directory contents."""
    DEFAULT_ICON = "❓"
    icon_map = {'.py': "🐍",
                '.txt': "📄",
                '.md': "📜",
                '.json': "🗃️",
                '.cmd': "💾",
                '.bat': "💾",
                '.ps1': "💾",
                '.exe': "💽",
                '.toml': "📇",
                '.env': "🌐",
                '.ipynb': "📈",
                '.log': "📝",
                '.errors': "📝",
                '.zip': "🗜️",
                '.ini': "📒"}
    # Sort dirs first then by filename
    to_ignore_files = set() if to_ignore_files is None else to_ignore_files
    to_ignore_folders = set() if to_ignore_folders is None else to_ignore_folders

    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.casefold() in to_ignore_files or path.name.casefold() in to_ignore_folders:
            continue
        if path.is_dir():
            if path.name.casefold() not in to_ignore_folders:
                style = "dim" if path.name.startswith("__") else ""
                branch = tree.add(
                    f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                    style=style,
                    guide_style=style,
                )

                recursive_dir_tree(path, branch, to_ignore_files, to_ignore_folders)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = icon_map.get(path.suffix, DEFAULT_ICON) + ' '
            tree.add(Text(icon) + text_filename)
