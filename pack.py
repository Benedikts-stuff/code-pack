import os
import sys
import argparse
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
    "data",
    "figures",
    "assets",
    "public",
    "docs",
    "logs",
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
    ".csv",
    ".tsv",
    ".jsonl",
    ".parquet",
    ".npy",
    ".npz",
    ".sqlite",
    ".db",
    ".lock",
    ".yaml",
    ".json",
}


@lru_cache(maxsize=None)
def get_gitignore_spec(dir_path: Path):
    gitignore_path = dir_path / ".gitignore"
    if gitignore_path.is_file():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    return None


def ignore(path: Path, base_dir: Path, allowed_exts=None) -> bool:
    if path.name.startswith(".") and path.name not in [".", ".."]:
        return True
    if "packed.md" == path.name:
        return True
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True
    if path.is_file() and path.suffix.lower() in IGNORE_EXTS:
        return True

    if path.is_file() and allowed_exts is not None:
        if path.suffix.lower() not in allowed_exts:
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


def generate_filetree(
    dir_path: Path, base_dir: Path, allowed_exts=None, prefix: str = ""
) -> str:
    tree_str = ""

    paths = sorted(
        [p for p in dir_path.iterdir() if not ignore(p, base_dir, allowed_exts)],
        key=lambda x: (x.is_file(), x.name.lower()),
    )

    pointers = [("├── " if i < len(paths) - 1 else "└── ") for i in range(len(paths))]

    for pointer, path in zip(pointers, paths):
        tree_str += f"{prefix}{pointer}{path.name}\n"
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree_str += generate_filetree(
                path, base_dir, prefix=prefix + extension, allowed_exts=allowed_exts
            )

    return tree_str


def copy_to_clipboard(text: str) -> bool:
    try:
        if sys.platform == "darwin":
            subprocess.run("pbcopy", text=True, input=text, check=True)
        return True
    except Exception as e:
        print(f"Could not copy: {e}")
        return False


def generate_markdown(base_dir_path: str, output_file: str, allowed_exts=None) -> None:
    base_dir = Path(base_dir_path).resolve()

    if not base_dir.is_dir():
        print(f"Directory '{base_dir_path}' does not exist")
        return

    content_lines = []
    content_lines.append(f"# Codebase: `{base_dir.name}`\n")
    content_lines.append("## Filetree\n")
    content_lines.append("```text")
    content_lines.append(f"{base_dir.name}/")
    content_lines.append(generate_filetree(base_dir, base_dir, allowed_exts).rstrip())
    content_lines.append("```\n")
    content_lines.append("## Filecontent\n")

    for root, dirs, files in os.walk(base_dir):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not ignore(root_path / d, base_dir, allowed_exts)]

        for file in sorted(files):
            file_path = root_path / file
            relative_path = ""
            if not ignore(file_path, base_dir, allowed_exts):
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
    parser = argparse.ArgumentParser(description="Pack codebase into a Markdown file")

    parser.add_argument(
        "dir", nargs="?", default=".", help="Target directory (default: current)"
    )

    parser.add_argument(
        "-e", "--ext", nargs="*", help="Filter by extensions (e.g., -e py md tsx)"
    )

    args = parser.parse_args()

    allowed_extensions = None
    if args.ext:
        allowed_extensions = {f".{ext.lstrip('.')}".lower() for ext in args.ext}

    print("Generating")
    generate_markdown(args.dir, OUTPUT_FILENAME, allowed_extensions)
