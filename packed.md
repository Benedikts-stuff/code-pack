# Codebase: `code-pack`

## Filetree

```text
code-pack/
├── pack.py
├── packed.md
└── README.md
```

## Filecontent

### File: `README.md`

````md
## Installation (macOS)

**1. Install dependencies**
Make sure you are in the project directory and install the required packages:

```bash
pip install pathspec pyinstaller
```

**2. Compile the script**
Build a standalone executable using PyInstaller:

```bash
pyinstaller --onefile pack.py --name pack
```

**3. Make it globally available**
Move the compiled binary from the dist folder into your local bin directory:

```bash
sudo mv dist/pack /usr/local/bin/
```

**4. Usage**
Simply navigate to any of your project directories in your terminal and run:

```bash
pack
```

## What it does

- The tool generates a llm_context.md file in your current directory.
- It automatically builds a clean ASCII file tree and appends all file contents, respecting your .gitignore rules at every directory level.
- The entire output is instantly copied to your clipboard, e.g. for usage with Chat based LLMs.

````

### File: `pack.py`

````py
import os
import sys
import pathspec
import subprocess
from functools import lru_cache
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    "env",
    "node_modules",
    "lib",
    "dist",
    "build",
    "out",
    "target",
}

IGNORE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".class",
    ".exe",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}


@lru_cache(maxsize=None)
def get_gitignore_spec(dir_path: Path):
    gitignore_path = dir_path / ".gitignore"
    if gitignore_path.is_file():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    return None


def ignore(path: Path, base_dir: Path) -> bool:
    if path.name.startswith("."):
        return True
    if "pack.md" == path.name:
        return True
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True
    if path.is_file() and path.suffix.lower() in IGNORE_EXTS:
        return True

    current_dir = path if path.is_dir() else path.parent

    while True:
        spec = get_gitignore_spec(current_dir)
        if spec:
            try:
                rel_path = path.relative_to(current_dir).as_posix()
                if path.is_dir() and not rel_path.endswith("/"):
                    rel_path += "/"

                if spec.match_file(rel_path):
                    return True
            except ValueError:
                pass

        if current_dir == base_dir:
            break
        current_dir = current_dir.parent

    return False


def generate_filetree(dir_path: Path, base_dir: Path, prefix: str = "") -> str:
    tree_str = ""

    paths = sorted(
        [p for p in dir_path.iterdir() if not ignore(p, base_dir)],
        key=lambda x: (x.is_file(), x.name.lower()),
    )

    pointers = [("├── " if i < len(paths) - 1 else "└── ") for i in range(len(paths))]

    for pointer, path in zip(pointers, paths):
        tree_str += f"{prefix}{pointer}{path.name}\n"
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree_str += generate_filetree(path, base_dir, prefix=prefix + extension)

    return tree_str


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "darwin":
            subprocess.run("pbcopy", text=True, input=text, check=True)
        return True
    except Exception as e:
        print(f"Could not copy: {e}")
        return False


def generate_markdown(base_dir_path: str, output_file: str) -> None:
    base_dir = Path(base_dir_path).resolve()

    if not base_dir.is_dir():
        print(f"Directory '{base_dir_path}' does not exist")
        return

    content_lines = []
    content_lines.append(f"# Codebase: `{base_dir.name}`\n")
    content_lines.append("## Filetree\n")
    content_lines.append("```text")
    content_lines.append(f"{base_dir.name}/")
    content_lines.append(generate_filetree(base_dir, base_dir).rstrip())
    content_lines.append("```\n")
    content_lines.append("## Filecontent\n")

    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not ignore(root_path / d, base_dir)]

        for file in sorted(files):
            file_path = root_path / file
            relative_path = ""
            if not ignore(file_path, base_dir):
                try:
                    relative_path = file_path.relative_to(base_dir)
                    file_ext = file_path.suffix.lstrip(".") or "text"

                    with open(file_path, "r", encoding="utf-8") as in_f:
                        file_content = in_f.read()

                    content_lines.append(f"### File: `{relative_path}`\n")
                    content_lines.append(f"````{file_ext}")
                    content_lines.append(file_content)
                    content_lines.append("````\n")

                except UnicodeDecodeError:
                    print(f"Skip {relative_path}")

    final_markdown = "\n".join(content_lines)

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(final_markdown)
    print("Generated")

    print("Copy to Clipboard")
    if copy_to_clipboard(final_markdown):
        print("Success")


if __name__ == "__main__":
    TARGET_DIRECTORY = "."
    OUTPUT_FILENAME = "packed.md"
    generate_markdown(TARGET_DIRECTORY, OUTPUT_FILENAME)

````

### File: `packed.md`

````md
# Codebase: `code-pack`

## Filetree

```text
code-pack/
├── llm_context.md
├── pack.py
└── README.md
```

## Filecontent

### File: `README.md`

```md
## Installation (macOS)

**1. Install dependencies**
Make sure you are in the project directory and install the required packages:

```bash
pip install pathspec pyinstaller
```

**2. Compile the script**
Build a standalone executable using PyInstaller:

```bash
pyinstaller --onefile pack_codebase.py --name pack
```

**3. Make it globally available**
Move the compiled binary from the dist folder into your local bin directory:

```bash
sudo mv dist/pack /usr/local/bin/
```

**4. Usage**
Simply navigate to any of your project directories in your terminal and run:

```bash
pack
```

## What it does

- The tool generates a llm_context.md file in your current directory.
- It automatically builds a clean ASCII file tree and appends all file contents, respecting your .gitignore rules at every directory level.
- The entire output is instantly copied to your clipboard, e.g. for usage with Chat based LLMs.


```

### File: `llm_context.md`

```md
# Codebase: `code-pack`

## Filetree

```text
code-pack/
├── llm_context.md
├── pack.py
└── README.md


## Filecontent

### Datei: `README.md`

```md
# code-pack


### Datei: `llm_context.md`

```md



### Datei: `pack.py`

```py
import sys
import os
import pathspec
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    "env",
    "node_modules",
    "lib",
    "dist",
    "build",
    "out",
    "target",
}

IGNORE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".class",
    ".exe",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}


def load_gitignore(dir: str) -> set:
    ignore_set = set()

    for _, _, files in os.walk(".", topdown=False):
        if ".gitignore" in files:
            file_path = os.path.join(dir, ".gitignore")

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()

                    if clean_line and not clean_line.startswith("#"):
                        ignore_set.add(clean_line)

    return ignore_set


def ignore(path: Path) -> bool:
    if path.name.startswith("."):
        return True

    if path.is_dir() and path.name in IGNORE_DIRS:
        return True

    if path.is_file() and path.suffix.lower() in IGNORE_EXTS:
        return True

    return False


def generate_filetree(dir_path: Path, prefix: str = "") -> str:
    tree_str = ""

    paths = sorted(
        [p for p in dir_path.iterdir() if not ignore(p)],
        key=lambda x: (x.is_file(), x.name.lower()),
    )

    pointers = [("├── " if i < len(paths) - 1 else "└── ") for i in range(len(paths))]

    for pointer, path in zip(pointers, paths):
        tree_str += f"{prefix}{pointer}{path.name}\n"
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree_str += generate_filetree(path, prefix=prefix + extension)

    return tree_str


def generate_markdown(base_dir_path: str, output_file: str) -> None:
    base_dir = Path(base_dir_path).resolve()

    if not base_dir.is_dir():
        print(f"Directory '{base_dir_path}' does not exist.")
        return

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(f"# Codebase: `{base_dir.name}`\n\n")

        out_f.write("## Filetree\n\n")
        out_f.write("```text\n")
        out_f.write(f"{base_dir.name}/\n")
        out_f.write(generate_filetree(base_dir))
        out_f.write("\n\n")

        out_f.write("## Filecontent\n\n")

        for root, dirs, files in os.walk(base_dir):
            root_path = Path(root)

            dirs[:] = [d for d in dirs if not ignore(root_path / d)]

            for file in sorted(files):
                file_path = root_path / file
                relative_path = ""
                if not ignore(file_path):
                    try:
                        relative_path = file_path.relative_to(base_dir)

                        file_ext = file_path.suffix.lstrip(".") or "text"

                        with open(file_path, "r", encoding="utf-8") as in_f:
                            content = in_f.read()

                        out_f.write(f"### Datei: `{relative_path}`\n\n")
                        out_f.write(f"```{file_ext}\n")
                        out_f.write(content)
                        out_f.write("\n\n\n")

                    except UnicodeDecodeError:
                        print(
                            f"Coudldn't read {relative_path} as text -> Skipping file"
                        )


if __name__ == "__main__":
    IGNORE_DIRS.update(load_gitignore(os.getcwd()))
    TARGET_DIRECTORY = "."
    OUTPUT_FILENAME = "llm_context.md"
    generate_markdown(TARGET_DIRECTORY, OUTPUT_FILENAME)
    print("Generated")




```

### File: `pack.py`

```py
import os
import sys
import pathspec
import subprocess
from functools import lru_cache
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "venv",
    "env",
    "node_modules",
    "lib",
    "dist",
    "build",
    "out",
    "target",
}

IGNORE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".class",
    ".exe",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
}


@lru_cache(maxsize=None)
def get_gitignore_spec(dir_path: Path):
    gitignore_path = dir_path / ".gitignore"
    if gitignore_path.is_file():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    return None


def ignore(path: Path, base_dir: Path) -> bool:
    if path.name.startswith("."):
        return True
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True
    if path.is_file() and path.suffix.lower() in IGNORE_EXTS:
        return True

    current_dir = path if path.is_dir() else path.parent

    while True:
        spec = get_gitignore_spec(current_dir)
        if spec:
            try:
                rel_path = path.relative_to(current_dir).as_posix()
                if path.is_dir() and not rel_path.endswith("/"):
                    rel_path += "/"

                if spec.match_file(rel_path):
                    return True
            except ValueError:
                pass

        if current_dir == base_dir:
            break
        current_dir = current_dir.parent

    return False


def generate_filetree(dir_path: Path, base_dir: Path, prefix: str = "") -> str:
    tree_str = ""

    paths = sorted(
        [p for p in dir_path.iterdir() if not ignore(p, base_dir)],
        key=lambda x: (x.is_file(), x.name.lower()),
    )

    pointers = [("├── " if i < len(paths) - 1 else "└── ") for i in range(len(paths))]

    for pointer, path in zip(pointers, paths):
        tree_str += f"{prefix}{pointer}{path.name}\n"
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree_str += generate_filetree(path, base_dir, prefix=prefix + extension)

    return tree_str


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "darwin":
            subprocess.run("pbcopy", text=True, input=text, check=True)
        return True
    except Exception as e:
        print(f"Could not copy: {e}")
        return False


def generate_markdown(base_dir_path: str, output_file: str) -> None:
    base_dir = Path(base_dir_path).resolve()

    if not base_dir.is_dir():
        print(f"Directory '{base_dir_path}' does not exist")
        return

    content_lines = []
    content_lines.append(f"# Codebase: `{base_dir.name}`\n")
    content_lines.append("## Filetree\n")
    content_lines.append("```text")
    content_lines.append(f"{base_dir.name}/")
    content_lines.append(generate_filetree(base_dir, base_dir).rstrip())
    content_lines.append("```\n")
    content_lines.append("## Filecontent\n")

    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not ignore(root_path / d, base_dir)]

        for file in sorted(files):
            file_path = root_path / file
            relative_path = ""
            if not ignore(file_path, base_dir):
                try:
                    relative_path = file_path.relative_to(base_dir)
                    file_ext = file_path.suffix.lstrip(".") or "text"

                    with open(file_path, "r", encoding="utf-8") as in_f:
                        file_content = in_f.read()

                    content_lines.append(f"### File: `{relative_path}`\n")
                    content_lines.append(f"```{file_ext}")
                    content_lines.append(file_content)
                    content_lines.append("```\n")

                except UnicodeDecodeError:
                    print(f"Skip {relative_path}")

    final_markdown = "\n".join(content_lines)

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(final_markdown)
    print("Generated")

    print("Copy to Clipboard")
    if copy_to_clipboard(final_markdown):
        print("Success")


if __name__ == "__main__":
    TARGET_DIRECTORY = "."
    OUTPUT_FILENAME = "packed.md"
    generate_markdown(TARGET_DIRECTORY, OUTPUT_FILENAME)

```

````
