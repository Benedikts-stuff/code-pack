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

You can exclude filetypes with the `-e` flag, e.g. `pack -e .log,.tmp` to exclude log and temporary files.

You can specifiy the directory to pack, e.g. `pack /path/to/your/project` to pack a specific directory. If no directory is specified, it defaults to the current working directory.

## What it does

- The tool generates a llm_context.md file in your current directory.
- It automatically builds a clean ASCII file tree and appends all file contents, respecting your .gitignore rules at every directory level.
- The entire output is instantly copied to your clipboard, e.g. for usage with Chat based LLMs.
