# Markdown Template

A tool to help primarily with generating Markdown tables based on a set of files. This is particularly useful to repositories that contain several subprojects, such as userscript repos.

## Installation

This will install `md-template` and `natsort` as well as `PyYAML` for the userscript preset.

```bash
pip install md-template[full]
```

For the most minimal installation.

```bash
pip install md-template
# or with natsort (recommended)
pip install md-template[natsort]
```

## Usage

**Command-line**

The easiest but most restricted method.

```bash
# md-template --help
md-template table --preset scoop --dry-run
```

**Class-based**

See [table.presets](mdtemplate/table/presets) for more detailed examples.

```python
from pathlib import Path
from typing import Iterable

from mdtemplate.table import TableTemplate


class MyTemplate(TableTemplate):
    files = "bucket/*.json"
    columns = ("Name", "Branch")
    source = "README.md"  # default

    def handle_path(self, path: Path) -> Iterable[Iterable[str]]:
        # create a row
        yield [
            # include information using the current filepath
            f"Column 1: **{path.name}**",
            # use information from the git repository
            f"Column 2: {self.repository.branch}",
        ]


if __name__ == "__main__":
    MyTemplate().parse_args().render()
```

**Function-based**

```python
from pathlib import Path
from typing import Iterable

from mdtemplate.table import TableTemplate


def handle_path(self: TableTemplate, path: Path) -> Iterable[Iterable[str]]:
    # create a row
    yield [
        # include information using the current filepath
        f"Column 1: **{path.name}**",
        # use information from the git repository
        f"Column 2: {self.repository.branch}",
    ]


if __name__ == "__main__":
    TableTemplate(
        files="bucket/*.json",
        columns=("Name", "Branch"),
        source="README.md",  # default
        handle_path=handle_path,
    ).parse_args().render()
```

## Output

Both the class-based and function-based examples above generate the same table.

**Input**

```md
# My Repository

<!-- table -->
<!-- table-end -->
```

**Output**

```md
# My Repository

<!-- table -->
| Name | Branch |
| ---- | ------ |
| Column 1: **filename.json** | Column 2: main |
<!-- table-end -->
```
