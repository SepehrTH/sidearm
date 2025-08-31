# Sidearm

**Sidearm** is a lightweight tool manager for hackers but can be used for anyone. It installs and updates tools from **Git repositories** or **Go packages**, and manages them in a consistent, reproducible way.

Think of it as your backup weapon: always at your side, keeping your tools ready.

## Features

* Install tools from `git` or `go`.
* Update existing tools in one command.
* Maintains a `tools.json` config for reproducibility.
* Creates symlinks in `bin/` for easy execution.
* Can install/update itself.

## Requirements
- Python 3.8+
- Git installed and in PATH
- Go installed and `$GOBIN` (or `$GOPATH/bin`) in PATH

You need to have git and go installed and in path.
Also, make sure that you have `gobin` in path so you can access your installed go tools easily.

## Installation

Clone the repo:

```bash
git clone https://github.com/SepehrTH/sidearm.git
cd sidearm
```
Initialize and install sidearm:
```bash
./sidearm.py init
```

Make sure `bin/` is in your `$PATH`. You will be given the command after you run init. The deafult path is:
```bash
export PATH="$HOME/tools/bin:$PATH"
```

(Optional: add that line to your `~/.bashrc` or `~/.zshrc`.)

After it's done, you are gonna have a directory named `~/.sidearm` which it contains the config files for sidearm.

An intial `~/.sidearm/tools.json` will be created for you in that directory which only contains sidearm by deafult. You can change replace that file and use your personal `tools.json`.

## Usage

### Add a Tool

```bash
sidearm add
```

* Choose `git` or `go`.
* Enter repo URL.
* Enter tool name.
* (For git repos) enter relative path of executable inside repo.

This updates `tools.json`.

### Sync All Tools

Install or update everything in `tools.json`:

```bash
sidearm sync
```

### Install or Update a Single Tool

```bash
sidearm get <tool_name>
```
The tool need to be added in tools.json, either by running `sidearm add` or manually.

## Config (`tools.json`)

Example:

```json
[
  {
    "name": "ffuf",
    "type": "go",
    "repo": "github.com/ffuf/ffuf/v2"
  },
  {
    "name": "sidearm",
    "type": "git",
    "repo": "https://github.com/SepehrTH/sidearm.git",
    "exec": "sidearm.py"
  }
]
```

## Notes

* Git tools are cloned under `tools/`.
* Go tools are installed via `go install` (requires Go with `GOBIN` in `$PATH`).
* Symlinks are created under `bin/` so you can run tools anywhere.


