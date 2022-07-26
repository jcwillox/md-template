from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from functools import lru_cache
from os import PathLike
from pathlib import Path
from typing import (
    Sequence,
    Union,
    Optional,
    Iterable,
    List,
    cast,
    Pattern,
)

from ..utils import Repository, print_difference, escape_table_cell

@dataclass
class TableTemplate:
    files: Optional[str] = None
    columns: Optional[Sequence[str]] = None

    id: Optional[str] = None
    source: Union[str, PathLike[str]] = "README.md"
    output: Optional[str] = None
    dry_run: bool = False
    use_natsort: bool = True
    only_tracked: bool = True
    repository = Repository()
    paths: List[Path] = field(init=False)

    def __post_init__(self):
        if not self.files:
            raise ValueError("`files` property is required")
        if not self.columns:
            raise ValueError("`columns` property is required")
        self.resolve_paths()

    def resolve_paths(self):
        """Resolves individual filepaths from the `files` property.

        It also optionally excludes untracked files and performs a natural sort.
        """
        paths = Path(".").glob(self.files)

        if self.only_tracked:
            self.paths = [
                path
                for path in paths
                if path.as_posix() in self.repository.tracked_files
            ]
        else:
            self.paths = list(paths)

        if self.use_natsort:
            try:
                from natsort import os_sorted

                self.paths = cast(List[Path], os_sorted(self.paths))
            except ImportError:
                print(
                    "[WARN] Missing `natsort` package; it is recommended to install it\n"
                    "       for consistent natural ordering of files between operating systems.\n"
                    "       Set `use_natsort=False` to suppress this warning."
                )

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--dry-run", action="store_true")
        parser.add_argument("-o", "--output", default="README.md")
        args = parser.parse_args()
        if args.output:
            self.output = args.output
        if args.dry_run:
            self.dry_run = True
        return self

    def create_header(self) -> str:
        return f"| {' | '.join(self.columns)} |\n| {' | '.join('-' * len(column) for column in self.columns)} |"

    def create_rows(self) -> Iterable[str]:
        for path in self.paths:
            rows = self.handle_path(path)
            for row in rows:
                cells = (escape_table_cell(cell) for cell in row)
                yield f"| {' | '.join(cells)} |"

    def handle_path(self, path: Path) -> Iterable[Iterable[str]]:
        """Generates a list of rows of cells for a given filepath.

        This function can be a generator and `yield` each row.
        Both `\\n` (new-line) and `|` (pipe) can be used inside cells and will be escaped.
        """
        raise NotImplementedError

    def render(
        self,
        *,
        output: Optional[Union[str, PathLike[str], False]] = None,
        diff: bool = True,
    ):
        with open(self.source, encoding="UTF-8") as file:
            source_content = file.read()

        header = self.create_header()
        rows = "\n".join(self.create_rows())
        regex = self._regex_table(self.id)

        if not regex.search(source_content):
            raise ValueError(
                f"Could not find table to template{f' with id `{self.id}`' if self.id else ''} in \"{self.source}\""
            )

        content = regex.sub(f"\n{header}\n{rows}\n", source_content)

        if diff:
            print_difference(source_content, content)

        if output is not False:
            if output is None:
                output = self.source

            if not self.dry_run:
                with open(output, "w+", encoding="UTF-8") as file:
                    file.write(content)

        return content

    @staticmethod
    @lru_cache
    def _regex_table(id_=None) -> Pattern[str]:
        id_ = f"-{id_}" if id_ else ""
        return re.compile(f"(?<=<!-- table{id_} -->)[\s\S]*(?=<!-- table{id_}-end -->)")
