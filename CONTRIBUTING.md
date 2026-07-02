# Contributing

## Branch Rules

- Work on feature branches.
- Open pull requests into `develop` for normal development.
- Only `develop` may open a pull request into `main`.
- Do not push directly to `main`.

The GitHub Actions workflow blocks pull requests into `main` unless the source branch is
`develop`. Direct pushes to `main` must also be blocked in GitHub repository settings with
branch protection or a repository ruleset.

## Required Checks

Before opening a pull request, run:

```bash
python -m ruff check .
python -m pytest
python -m pip check
```

The CI workflow also runs smoke checks for:

- CLI startup
- SQLite initialization
- Desktop app imports
- Optional web dashboard imports

## GitHub Repository Settings

In GitHub, configure `main` as a protected branch or ruleset:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Require the `CI / Branch Policy` check.
- Require the `CI / Python ...` checks.
- Restrict direct pushes to `main`.
- Allow merge into `main` only through pull requests from `develop`.
