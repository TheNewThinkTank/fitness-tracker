# Install dependencies with uv
.PHONY: install-dependencies
install-dependencies:
	uv sync --locked --all-groups

# Lint with ruff
.PHONY: lint-ruff
lint-ruff:
	uv run --locked ruff check --config .config/ruff.toml src oxygen test

# Static type checks with mypy
.PHONY: static-type-checks
static-type-checks:
	uv run --locked mypy --config-file .config/mypy.ini src oxygen/oxygen --exclude '/site-packages/'

# Wily build and rank
.PHONY: wily-build-and-rank
wily-build-and-rank:
	uv run --locked wily build src
	uv run --locked wily rank src

# Run unit tests and make coverage report
.PHONY: run-tests-and-coverage
run-tests-and-coverage:
	uv run --locked pytest test --cov=src --cov-report xml:cov.xml

# Qualify code target
.PHONY: qualify-code
qualify-code: install-dependencies lint-ruff \
	static-type-checks wily-build-and-rank run-tests-and-coverage

.PHONY: check-contracts
check-contracts:
	uv run --locked ./bin/generate_openapi.sh --check
