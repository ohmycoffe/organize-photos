.DEFAULT_GOAL := all
sources = src tests

.PHONY: .pdm  # Check that pdm is installed
.pdm:
	@pdm -V || echo 'Please install pdm https://pdm.fming.dev/latest/'

.PHONY: .pre-commit  # Check that pre-commit is installed
.pre-commit:
	@pdm run pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

.PHONY: .install-project
.install-project: .pdm # Install the package, dependencies, and pre-commit for local development
	pdm install

.PHONY: .install-pre-commit
.install-pre-commit: .pdm # Install the package, dependencies, and pre-commit for local development
	pdm run pre-commit install

.PHONY: format
format: .pdm # Auto-format Python source files
	pdm run black $(sources)
	pdm run isort $(sources)

.PHONY: lint
lint: .pdm # Lint python source files
	pdm run black $(sources) --check --diff
	pdm run isort $(sources) --check --diff
	pdm run flake8 $(sources)
	pdm run mypy $(sources)

.PHONY: pre-commit
pre_commit: .pdm # Run pre-commit for all files
	pdm run pre-commit run --all-files

.PHONY: test
test: .pdm .clean-coverage # Build packages for different versions of Python and run tests for each package
	pdm run tox

.PHONY: .clean-coverage  # Remove coverage reports and files
.clean-coverage:
	@[ -f .coverage ] && rm .coverage || echo ".coverage doesn't exist"
	@rm -rf htmlcov

.PHONY: .clean-build
.clean-build:
	@rm -rf dist

PHONY: build
build: .pdm .clean-build # Build the package
	pdm build

.PHONY: clean
clean: .clean-coverage .clean-build # Clean repository
	@rm -rf .tox
	@rm -rf .mypy_cache

.PHONY: help # Show this help message (author @dwmkerr: https://dwmkerr.com/makefile-help-command/)
help: # List all available commands
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY : install, install-cicd, all
install : .install-project .install-pre-commit # Install the package, dependencies, and pre-commit for local development
install-cicd : .install-project # Install the package and dependencies for cicd
all : clean install format lint pre-commit test build # (default) Run all commands
