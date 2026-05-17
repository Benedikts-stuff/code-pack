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



