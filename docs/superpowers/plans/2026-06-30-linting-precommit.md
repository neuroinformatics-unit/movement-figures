# Ruff Linting & pre-commit Hooks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add ruff (lint + format), codespell, and pre-commit hygiene hooks to the movement-figures repo, with the existing codebase baselined clean.

**Architecture:** Two tasks. Task 1 adds the ruff + codespell configuration and dev dependencies to `pyproject.toml` and brings the existing `.py` files into compliance. Task 2 wires up `.pre-commit-config.yaml` and runs the full hook suite to baseline, committing the auto-fixes. Config is adapted from the `movement` package but trimmed for a small figures repo.

**Tech Stack:** uv, ruff, codespell, pre-commit.

## Global Constraints

- Tools: ruff (lint + format), codespell, pre-commit hygiene hooks. NOT mypy, check-manifest, rST pygrep hooks, or any movement-specific local hook.
- Ruff: `line-length = 88`, `fix = true`, `select = ["E", "F", "I", "UP", "B"]` (no `D`/pydocstyle).
- codespell config: `skip = '.git,*.svg,*.pdf,uv.lock'`, `check-hidden = true`.
- `.pre-commit-config.yaml` MUST have top-level `exclude: '^outputs/'` to protect the deterministic committed figures from the whitespace/EOF fixers.
- Pin hooks to the revs `movement` uses: pre-commit-hooks `v6.0.0`, ruff-pre-commit `v0.15.15`, codespell `v2.4.2`.
- `.qmd` cell linting is OUT of scope (ruff lints `.py` only).
- Existing test suite must still pass (`uv run pytest -q` → 12 passed) after each task.
- All commands run under `uv run` so they use the locked `.venv`.

---

### Task 1: Ruff + codespell config and baseline cleanup

**Files:**
- Modify: `pyproject.toml`
- Possibly reformat (by ruff): `src/movement_figures/*.py`, `tests/*.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a `pyproject.toml` with `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]`, `[tool.codespell]` sections and `pre-commit`/`ruff`/`codespell` in the `dev` group; a codebase that passes `ruff check` and `ruff format --check`.

**Note on this task's "test":** there is no unit test for config. The verification commands (`ruff check`, `ruff format --check`, `pytest`) ARE the test cycle — run them and confirm the stated output.

- [ ] **Step 1: Add the three dev dependencies**

In `pyproject.toml`, replace the `dev` group:

```toml
[dependency-groups]
dev = ["pytest"]
```

with:

```toml
[dependency-groups]
dev = [
    "pytest",
    "pre-commit",
    "ruff",
    "codespell",
]
```

- [ ] **Step 2: Add the ruff and codespell config**

In `pyproject.toml`, after the existing `[tool.pytest.ini_options]` block, add:

```toml
[tool.ruff]
line-length = 88
fix = true

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ruff.lint.per-file-ignores]
# matplotlib.use("Agg") must run before pyplot is imported, so the imports
# that follow it are intentionally not at the top of the file.
"tests/conftest.py" = ["E402"]

[tool.codespell]
skip = '.git,*.svg,*.pdf,uv.lock'
check-hidden = true
```

Why the `per-file-ignores`: `tests/conftest.py` calls `matplotlib.use("Agg")` between imports, which trips `E402` (module-import-not-at-top). That ordering is required, so the rule is ignored for that one file only.

- [ ] **Step 3: Sync the environment**

Run: `uv sync`
Expected: installs `pre-commit`, `ruff`, `codespell` into `.venv`.

- [ ] **Step 4: Apply ruff formatting and autofixes**

Run: `uv run ruff format . && uv run ruff check --fix .`
Expected: ruff reformats the existing `src/` and `tests/` `.py` files as needed and applies any import-sort/pyupgrade fixes. `.qmd`, `.svg`, `.pdf` files are untouched (ruff only handles `.py`).

- [ ] **Step 5: Verify ruff is clean and idempotent**

Run: `uv run ruff check . && uv run ruff format --check .`
Expected: both exit 0 — `ruff check` prints `All checks passed!` and `ruff format --check` reports the files are already formatted. If `ruff check` still reports errors it could not auto-fix, read each one and fix it by hand, then re-run until clean. Do NOT add blanket ignores to silence a real finding.

- [ ] **Step 6: Verify the test suite still passes**

Run: `uv run pytest -q`
Expected: `12 passed`. (Formatting must not change behavior.)

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/movement_figures tests
git commit -m "build: add ruff and codespell config; baseline-format codebase"
```

---

### Task 2: pre-commit hooks

**Files:**
- Create: `.pre-commit-config.yaml`
- Possibly auto-fixed (by hooks): tracked text files outside `outputs/` (EOF newline, trailing whitespace, line endings)
- Possibly modify: `pyproject.toml` (only if codespell reports a genuine false positive — see Step 4)

**Interfaces:**
- Consumes: the ruff + codespell config from Task 1.
- Produces: a working `.pre-commit-config.yaml`; the repo passes `pre-commit run --all-files` cleanly.

- [ ] **Step 1: Create `.pre-commit-config.yaml`**

`.pre-commit-config.yaml`:

```yaml
ci:
    autoupdate_schedule: monthly
exclude: '^outputs/'
repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v6.0.0
      hooks:
          - id: check-added-large-files
          - id: check-case-conflict
          - id: check-merge-conflict
          - id: check-yaml
          - id: check-toml
          - id: end-of-file-fixer
          - id: mixed-line-ending
            args: [--fix=lf]
          - id: trailing-whitespace
          - id: name-tests-test
            args: ["--pytest-test-first"]
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.15.15
      hooks:
          - id: ruff
          - id: ruff-format
    - repo: https://github.com/codespell-project/codespell
      rev: v2.4.2
      hooks:
          - id: codespell
```

The top-level `exclude: '^outputs/'` keeps every hook from touching the
committed `outputs/*.svg` (text) — preserving the deterministic-export
guarantee. `codespell` reads its config from `[tool.codespell]` in
`pyproject.toml`.

- [ ] **Step 2: Install the git hook**

Run: `uv run pre-commit install`
Expected: `pre-commit installed at .git/hooks/pre-commit`.

- [ ] **Step 3: Baseline run (may modify files, may need re-running)**

Run: `uv run pre-commit run --all-files`
Expected: on the FIRST run, the `end-of-file-fixer` / `trailing-whitespace` /
`mixed-line-ending` hooks may modify tracked text files (e.g. add a final
newline to a spec/config file) and report `Failed` with "files were modified by
this hook". `ruff` and `ruff-format` should pass (Task 1 already baselined them).
This is normal — the hooks fixed the files in place.

- [ ] **Step 4: Handle codespell false positives, if any**

If `codespell` reports a word that is a legitimate term (not a typo), add it to
an `ignore-words-list` in `pyproject.toml`'s `[tool.codespell]` section, e.g.:

```toml
[tool.codespell]
skip = '.git,*.svg,*.pdf,uv.lock'
check-hidden = true
ignore-words-list = "word1,word2"
```

(Only add this line if a false positive actually occurs; otherwise leave the
section as written in Task 1.) Re-run `uv run pre-commit run --all-files` after
the change. Do NOT add a real misspelling to the ignore list — fix the source
instead.

- [ ] **Step 5: Verify a clean second run**

Run: `uv run pre-commit run --all-files`
Expected: every hook reports `Passed` (or `Skipped` where there are no matching
files). No file modifications. If a hook still modifies files, re-stage and
re-run until a full pass with no changes.

- [ ] **Step 6: Verify the test suite still passes**

Run: `uv run pytest -q`
Expected: `12 passed`.

- [ ] **Step 7: Verify the deterministic outputs are still untouched**

Run: `uv run quarto render figures/example_trajectory.qmd && git status --porcelain outputs/`
Expected: render succeeds and `git status --porcelain outputs/` prints NOTHING —
re-rendering produces no diff, confirming the `^outputs/` exclusion plus
deterministic export hold together.

- [ ] **Step 8: Commit**

```bash
git add .pre-commit-config.yaml pyproject.toml
git add -A
git commit -m "build: add pre-commit hooks and baseline tracked files"
```

(The `git add -A` picks up any EOF/whitespace fixes the hooks applied to tracked
files outside `outputs/`.)

---

## Notes for the implementer

- Run everything under `uv run` so the locked `.venv` tooling is used.
- The ruff version uv installs and the `v0.15.15` pinned in `.pre-commit-config.yaml`
  may differ slightly; both are modern and share the same config — this is
  expected and matches how `movement` is set up.
- If `pre-commit` cannot reach GitHub to fetch hook repos, that is an
  environment/network problem — report it as BLOCKED with the exact error rather
  than disabling hooks.
- Do not reformat or lint `figures/*.qmd` — `.qmd` linting is deliberately out of
  scope for this PR.
