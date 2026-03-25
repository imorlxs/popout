# Contributing to PopOut

Thanks for contributing to this project.

This document explains how to set up your environment, run tests locally, and fix linting issues before opening a pull request.

## Project Overview

PopOut is a Python project that currently includes:

- Core game logic in `src/game/` (for example `board.py`, `player.py`, `game.py`)
- Automated tests in `tests/`
- GitHub Actions workflows for linting and tests in `.github/workflows/`

CI currently validates:

- Tests on Python 3.9, 3.10, and 3.11
- Linting and formatting checks on Python 3.11 using Ruff and Black

## Local Setup

1. Clone the repository and move into the project directory.
2. Create and activate a virtual environment.
3. Install dependencies used by CI.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pytest pytest-cov ruff black
```

### macOS/Linux (bash/zsh)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest pytest-cov ruff black
```

## Run Tests Locally

From the repository root:

```bash
pytest tests/ -v --tb=short --cov=src --cov-report=xml --cov-report=term
```

This mirrors the CI test command in `.github/workflows/tests.yml`.

## Run Lint and Format Checks Locally

From the repository root:

```bash
ruff check src tests
black --check src tests
```

This mirrors the CI lint command in `.github/workflows/lint.yml`.

## If CI or Tests Fail Because of Linting

If your pull request fails lint checks, run these commands locally:

```bash
ruff check src tests
black --check src tests
```

To automatically apply common fixes:

```bash
ruff check src tests --fix
black src tests
```

Then re-run validation:

```bash
ruff check src tests
black --check src tests
pytest tests/ -v --tb=short --cov=src --cov-report=xml --cov-report=term
```

## Contribution Workflow

1. Create a feature branch from `main`.
2. Make focused changes (code + tests when behavior changes).
3. Run lint and tests locally.
4. Open a pull request with a clear description of:
   - What changed
   - Why it changed
   - How it was tested

## Testing Guidelines

- Add or update tests for any change in game behavior.
- Keep tests deterministic and easy to read.
- Prefer small, focused test cases.

## Code Style Guidelines

- Follow Black formatting.
- Keep imports and style compliant with Ruff.
- Write clear names and concise docstrings where useful.
- Keep functions and methods focused on one responsibility.

## Pull Request Checklist

Before requesting review, confirm:

- [ ] Tests pass locally
- [ ] Ruff passes locally
- [ ] Black check passes locally
- [ ] New behavior is covered by tests
- [ ] PR description explains the change and validation

## Questions

If anything is unclear, open an issue or ask in your pull request discussion.
