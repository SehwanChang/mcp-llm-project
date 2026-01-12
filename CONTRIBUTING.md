# Contribution Guidelines

This project uses simple, consistent conventions to keep contributions clean and reviewable.

## Commit message format
- Use conventional, short messages: `type(scope): subject`
- Common `type` values: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.
- Examples:
  - `feat(extract): add fallback paragraph extraction`
  - `test(scripts): add run_tests helper`

Keep the subject under 72 characters. Use the body for longer explanations.

## Branches
- Create a descriptive branch for each change: `feature/add-samples`, `fix/encoding-bug`.
- Rebase or squash commits as appropriate before merging to `main`.

## Pull Requests
- Open a PR against `main`.
- Describe the change, why it's needed, and any manual testing steps.
- Link related issues if applicable.

## Testing
- Run unit tests locally before opening a PR:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
python -m pip install -r mcp_server/requirements.txt
python -m pip install pytest
python -m pytest -q
```

There are helper scripts in `scripts/` for running focused checks (`run_tests.py`, `dump_extract_samples.py`).

## Formatting & Linting
- Use `black` for formatting (if added): `black .`
- Keep imports tidy and avoid unused dependencies.

## Local artifacts
- Do not commit local test artifacts like `.test_result.json` or `.extract_samples.json`.

## CI
- Add a GitHub Actions workflow or similar to run `pytest` on PRs to `main`.

Thanks for contributing! If you want this doc expanded into checklists or templates, open a PR.
