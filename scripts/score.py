#!/usr/bin/env python3
"""Repo quality score (0-100). Run: python scripts/score.py

Rubric (max points):
  tests 25 | lint 10 | ci 10 | structure 15 | docs 10 | config/security 10
  | reliability 10 | packaging 10
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
results: list[tuple[str, float, float, str]] = []


def add(name: str, got: float, maximum: float, note: str = "") -> None:
    results.append((name, round(got, 1), maximum, note))


def run(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def exists(*paths: str) -> bool:
    return all((ROOT / p).exists() for p in paths)


# --- tests (25) ---
r = run(sys.executable, "-m", "pytest", "-q", "--cov=chat_summarizer",
        "--cov-report=json:.coverage.json", "-p", "no:cacheprovider")
passed = r.returncode == 0
add("tests pass", 10 if passed else 0, 10, "" if passed else "pytest failed")
cov = 0.0
try:
    cov = json.loads((ROOT / ".coverage.json").read_text())["totals"]["percent_covered"]
except Exception:
    pass
add("coverage (>=85% = full)", min(cov / 85, 1) * 15, 15, f"{cov:.0f}%")

# --- lint (10) ---
r = run(sys.executable, "-m", "ruff", "check", ".")
add("ruff clean", 10 if r.returncode == 0 else 0, 10)

# --- ci (10) ---
ci = read(".github/workflows/ci.yml")
add("CI workflow", 4 if ci else 0, 4)
add("CI runs tests+lint", (3 if "pytest" in ci else 0) + (3 if "ruff" in ci else 0), 6)

# --- structure (15) ---
add("package dir", 5 if exists("chat_summarizer/__init__.py") else 0, 5)
dupes = [p.name for p in ROOT.glob("*_simple.py")] + (["main_simple.py"] if exists("main_simple.py") else [])
add("no duplicated *_simple modules", 5 if not dupes else 0, 5, ", ".join(dupes))
add("pyproject.toml", 5 if exists("pyproject.toml") else 0, 5)

# --- docs (10) ---
readme = read("README.md")
add("README env example exists", 3 if exists(".env.example") else 0, 3)
add("LICENSE", 2 if exists("LICENSE") else 0, 2)
add("README has testing+API sections",
    (2 if re.search(r"(?im)^#+.*test", readme) else 0) + (2 if re.search(r"(?im)^#+.*(api|endpoint)", readme) else 0), 4)
add("CONTRIBUTING/CHANGELOG", 1 if exists("CONTRIBUTING.md") else 0, 1)

# --- config/security (10) ---
api = read("chat_summarizer/api.py") + read("chat_summarizer/config.py")
add("CORS configurable", 3 if "CORS_ORIGINS" in api else 0, 3)
add("no wildcard origin + credentials", 3 if not re.search(r'allow_origins=\["\*"\]', api) else 0, 3)
add("input validation limits", 4 if "max_length" in read("chat_summarizer/models.py") else 0, 4)

# --- reliability (10) ---
add("HTTP errors not swallowed (no blanket except)", 4 if "except Exception" not in read("chat_summarizer/api.py") else 0, 4)
add("no print() in package", 3 if not any("print(" in p.read_text(encoding="utf-8") for p in (ROOT / "chat_summarizer").glob("*.py")) else 0, 3)
add("lazy heavy imports (works w/o langchain)", 3 if passed else 0, 3)

# --- packaging (10) ---
add("requirements-dev", 2 if exists("requirements-dev.txt") else 0, 2)
add("Dockerfile non-root + healthcheck", (2 if "USER " in read("Dockerfile") else 0) + (2 if "HEALTHCHECK" in read("Dockerfile") else 0), 4)
add(".gitignore complete", 2 if all(x in read(".gitignore") for x in (".coverage", ".pytest_cache", ".ruff_cache")) else 0, 2)
add("compose healthcheck / no bind reload", 2 if "healthcheck" in read("docker-compose.yml") else 0, 2)

total = sum(g for _, g, _, _ in results)
maximum = sum(m for _, _, m, _ in results)
for name, got, m, note in results:
    print(f"{'OK ' if got >= m else '-- '}{name:<45}{got:>5}/{m:<3} {note}")
print(f"\nSCORE: {total:.0f}/{maximum:.0f}")
sys.exit(0 if total >= 90 else 1)
