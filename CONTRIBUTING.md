# Contributing

Contributions are welcome. Use Python 3.10+, keep runtime dependencies minimal, add tests for behavioral changes, and run `python -m unittest discover -s tests -v` before opening a pull request. Keep process execution shell-free and preserve conservative shutdown behavior.

## Development

```bash
python -m venv .venv
python -m pip install -e .
python -m unittest discover -s tests -v
```

Please keep commits focused and documentation accurate.
