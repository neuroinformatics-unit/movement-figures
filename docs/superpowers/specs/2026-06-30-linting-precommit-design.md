# Ruff Linting & pre-commit Hooks — Design

**Date:** 2026-06-30
**Status:** Approved
**Branch / PR:** `add-linting` (separate PR off `main`)

## Purpose

Add automated code-quality enforcement to movement-figures: ruff for linting and
formatting, codespell for typos, and a set of pre-commit hygiene hooks. Config is
inspired by the `movement` package but trimmed to what a small figures repo needs.

## Key Decisions

| Decision | Choice |
|----------|--------|
| Tools | ruff (lint + format), codespell, pre-commit hygiene hooks |
| Excluded tools | mypy, check-manifest, rST pygrep hooks, the `no-movement-url` local hook (all movement-specific or overkill here) |
| Ruff line length | 88 (ruff default) |
| Ruff rule set | `select = ["E", "F", "I", "UP", "B"]`; no `D`/pydocstyle |
| `.qmd` cell linting | Out of scope for this PR — ruff lints `.py` only. May revisit later with jupytext. |
| Generated outputs | `outputs/` excluded from all pre-commit hooks to preserve byte-determinism |
| Hook pin strategy | Pin to the same revs `movement` uses (known-good) |

## Components

### `pyproject.toml` additions

- `dev` dependency group gains `pre-commit`, `ruff`, `codespell`.
- `[tool.ruff]`: `line-length = 88`, `fix = true`.
- `[tool.ruff.lint]`: `select = ["E", "F", "I", "UP", "B"]`.
  - No `exclude` for `__init__.py` is needed: the package's `__init__.py`
    re-exports are listed in `__all__`, which suppresses F401 (unused import).
- `[tool.codespell]`: `skip = '.git,*.svg,*.pdf,uv.lock'`, `check-hidden = true`.
  - SVG/PDF outputs and the lockfile contain token-like strings that produce
    false positives; skip them.

### `.pre-commit-config.yaml`

Top-level `exclude: '^outputs/'` — keeps the whitespace/EOF fixers from rewriting
the committed `outputs/*.svg`, which would undo the deterministic-export
guarantee. This exclusion is load-bearing, not cosmetic.

Hooks:

- **`pre-commit/pre-commit-hooks` @ v6.0.0:** `check-added-large-files`,
  `check-case-conflict`, `check-merge-conflict`, `check-yaml`, `check-toml`,
  `end-of-file-fixer`, `mixed-line-ending` (`--fix=lf`), `trailing-whitespace`,
  `name-tests-test` (`args: ["--pytest-test-first"]`).
  - `name-tests-test` enforces `test_*.py` naming; `conftest.py` is exempt
    automatically.
- **`astral-sh/ruff-pre-commit` @ v0.15.15:** `ruff`, `ruff-format`.
- **`codespell-project/codespell` @ v2.4.2:** `codespell` (configured via
  `pyproject.toml`).

Plus a `ci:` block with `autoupdate_schedule: monthly` for the pre-commit.ci bot,
matching `movement`.

### Explicitly NOT included (and why)

- **mypy** — overkill for a small figures package; chosen out during scoping.
- **check-manifest / setuptools_scm hooks** — no sdist-manifest concerns; static
  version.
- **rST pygrep hooks** — docs are markdown/qmd, not reStructuredText.
- **`no-movement-url` local hook** — movement-internal docs rule; this repo
  legitimately links to movement.neuroinformatics.dev.
- **jupytext / `.qmd` cell linting** — deferred; ruff lints `.py` only for now.

## Rollout

1. Add the three dev deps to `pyproject.toml`; `uv sync`.
2. Write `.pre-commit-config.yaml` and the ruff/codespell config.
3. `uv run pre-commit install` (sets up the git hook).
4. `uv run pre-commit run --all-files` once to baseline. Expect:
   - `ruff-format` to reformat existing `src/` + `tests/` files,
   - hygiene hooks to normalize EOF/whitespace/line-endings.
5. Commit the resulting auto-fixes so the repo starts in a clean state.

## Known Limitation

ruff lints `.py` files only. Python inside `figures/*.qmd` `{python}` cells is NOT
checked by this setup. Revisit with a jupytext-based hook in a future PR if it
proves worthwhile.

## Verification

- `uv run pre-commit run --all-files` exits clean (after the baseline auto-fixes
  are committed).
- `uv run ruff check .` reports no errors.
- The existing test suite still passes: `uv run pytest -q` → 12 passed.
- Re-rendering the example figure still produces no `outputs/` diff (the
  `^outputs/` exclusion plus deterministic export hold together).
