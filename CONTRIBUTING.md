# Contributing

1. `pip install -r requirements-dev.txt`
2. `ruff check .` and `pytest --cov` must pass (CI enforces both).
3. `python scripts/score.py` prints the repo quality score.
4. Keep changes small; add or update tests with every behaviour change.
