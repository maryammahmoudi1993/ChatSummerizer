# Improvement plan (target: quality score >= 90/100)

"Score" is measured by `python scripts/score.py` (rubric in the script header).
Baseline on `main`: **10/100**.

| Area | Pts | Work |
|------|-----|------|
| Tests | 25 | pytest suite over storage, sentiment, classifier, summarizer, API; >=85% coverage |
| Lint | 10 | ruff config, zero findings |
| CI | 10 | GitHub Actions: ruff + pytest on 3.10-3.12 |
| Structure | 15 | `chat_summarizer/` package, drop duplicated `*_simple`/`main_simple`, `pyproject.toml` |
| Docs | 10 | `.env.example`, LICENSE, README testing/API sections, CONTRIBUTING |
| Config/security | 10 | env-driven CORS (no `*` + credentials), input length limits |
| Reliability | 10 | keep 404/400 status codes, `logging` not `print`, lazy LangChain/torch imports, extractive summary fallback |
| Packaging | 10 | requirements-dev, non-root Docker + HEALTHCHECK, compose healthcheck, fuller .gitignore |

Loop: branch -> tests -> run -> merge to main -> push -> re-score -> repeat until >= 90.
