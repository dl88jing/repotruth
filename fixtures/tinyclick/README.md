# TinyClick

Minimal CLI for counting lines in a file.

## Usage

```
tinyclick count PATH [--count]
```

- `--count` prints only the number of lines (no filename).
- If `PATH` does not exist, TinyClick prints a warning and **exits with code 0** so scripts keep running.
- Supports globs like `src/**/*.py`.

See [docs/cli.md](docs/cli.md) for the full flag reference.
