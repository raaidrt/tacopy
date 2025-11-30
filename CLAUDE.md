# Project Guidelines

This project uses `uv` for Python package management and follows best practices for open-source Python development.

## Package Management with `uv`

### Installing Dependencies

- **Add production dependencies**: `uv add <package-name>`
- **Add development dependencies**: `uv add --dev <package-name>` or add to `[dependency-groups]` in [pyproject.toml](pyproject.toml)
- **Sync dependencies**: `uv sync` (installs all dependencies from lockfile)
- **Sync with dev dependencies**: `uv sync --dev` or `uv sync --all-extras --dev`

### Running Python Code

Always use `uv run` to execute Python commands with the project's virtual environment:

- **Run Python scripts**: `uv run python <script.py>`
- **Run tests**: `uv run pytest tests/ -v`
- **Run module directly**: `uv run python -m <module>`

Do NOT manually activate the virtual environment (`.venv`) - `uv run` handles this automatically.

### Building and Publishing

- **Build package**: `uv build` (creates wheel and sdist in `dist/`)
- **Publish to PyPI**: `uv publish` (requires PyPI credentials)
- **Publish to TestPyPI**: `uv publish --publish-url https://test.pypi.org/legacy/`

## Code Quality and Testing

### Testing

- Run all tests: `uv run pytest tests/ -v`
- Run specific test file: `uv run pytest tests/test_file.py -v`
- Run with coverage: `uv run pytest --cov=src/tacopy tests/`
- Update snapshots: `uv run pytest --snapshot-update` (for syrupy snapshot tests)

### Code Style and Linting

This project uses `ruff` for fast linting and formatting:

- **Run linter**: `uv run ruff check .`
- **Run linter with auto-fix**: `uv run ruff check . --fix`
- **Check formatting**: `uv run ruff format --check .`
- **Format code**: `uv run ruff format .`
- **Run pre-commit hooks**: `uv run pre-commit run --all-files`

Configuration is in [pyproject.toml](pyproject.toml) under `[tool.ruff]`.

### Type Checking

This project uses `pyrefly` (Meta's next-generation type checker) for type checking:

- **Run type checker**: `uv run pyrefly check`
- **Type checking with verbose output**: `uv run pyrefly check --verbose`
- **Initialize pyrefly**: `uv run pyrefly init` (already done)

Configuration is in [pyproject.toml](pyproject.toml) under `[tool.pyrefly]`.

**Note**: Type checking in CI is informational and won't block builds, as AST manipulation code can have dynamic patterns that are difficult to type check statically.

## Project Structure

This project follows the `src` layout:
- Source code: [src/tacopy/](src/tacopy/)
- Tests: [tests/](tests/)
- Build configuration: [pyproject.toml](pyproject.toml)
- Lockfile: [uv.lock](uv.lock) (committed to version control)

## Version Management

Version is defined in [pyproject.toml](pyproject.toml). When updating:
1. Bump version in `pyproject.toml`
2. Update changelog/release notes
3. Create git tag: `git tag v<version>`
4. Build and publish: `uv build && uv publish`

## Development Workflow

1. **Make changes** to source code in [src/tacopy/](src/tacopy/)
2. **Write tests** in [tests/](tests/) following existing patterns
3. **Run tests** with `uv run pytest tests/ -v`
4. **Format code** with `uv run ruff format .`
5. **Check linting** with `uv run ruff check . --fix`
6. **Build locally** with `uv build` to verify package builds correctly
7. **Commit changes** - pre-commit hooks will automatically run ruff on staged files
8. **CI will run** tests, linting, and formatting checks across Python 3.10-3.13 (see [.github/workflows/test.yml](.github/workflows/test.yml))

## Python Version Support

This project supports Python >=3.10 as specified in [pyproject.toml](pyproject.toml). When adding new features:
- Avoid features only available in newer Python versions unless necessary
- Test across all supported versions (3.10, 3.11, 3.12, 3.13)
- Update `requires-python` and `classifiers` if changing version support

## Key Files

- [pyproject.toml](pyproject.toml): Package metadata, dependencies, build config, ruff & pyrefly config
- [uv.lock](uv.lock): Locked dependency versions (commit this!)
- [.pre-commit-config.yaml](.pre-commit-config.yaml): Pre-commit hooks configuration
- [src/tacopy/__init__.py](src/tacopy/__init__.py): Package entry point
- [tests/](tests/): Test suite using pytest and syrupy
- [.github/workflows/test.yml](.github/workflows/test.yml): CI configuration

## Common Tasks

- **Add new feature**: Create module in [src/tacopy/](src/tacopy/), add tests, update [README.md](README.md)
- **Fix bug**: Add regression test first, then fix
- **Add dependency**: `uv add <package>` and commit updated [uv.lock](uv.lock)
- **Update dependencies**: `uv lock --upgrade` to update all, or `uv lock --upgrade-package <package>` for specific package

## Best Practices

1. **Always commit uv.lock**: Ensures reproducible builds
2. **Use `uv run` for all Python commands**: Ensures correct environment
3. **Write tests first**: Add test cases before fixing bugs or adding features
4. **Keep pyproject.toml clean**: Only add necessary dependencies
5. **Use dependency groups**: Separate dev/test dependencies from production
6. **Type hints**: Add type hints to new code (Python 3.10+ syntax)
7. **Documentation**: Update [README.md](README.md) and docstrings for public APIs

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:
- Automatically runs on `git commit`
- Runs ruff linter with auto-fix
- Runs ruff formatter
- Install hooks: `uv run pre-commit install` (already done)
- Run manually: `uv run pre-commit run --all-files`

## CI/CD

GitHub Actions workflow ([.github/workflows/test.yml](.github/workflows/test.yml)) automatically:
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Runs pytest test suite
- Runs ruff linting and format checks
- Runs pyrefly type checking (informational, won't block PRs)
- Builds package with `uv build`
- Uploads build artifacts

All checks except pyrefly must pass before merging PRs.
