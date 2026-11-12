.PHONY: help validate validate-links test lint check ci ote build-cli catalog-check verify govern stats eval install dry-run backup

.DEFAULT_GOAL := help

help:
	@echo "validate       Run the repository validator"
	@echo "validate-links Run the validator with external link checks"
	@echo "test           Run the unit and integration test suites"
	@echo "lint           Check shell syntax and run ShellCheck when installed"
	@echo "check          Show installer status without writing files"
	@echo "ci             Run validate and test, matching the default CI gate"
	@echo "ote            Run the CLI from the checkout; pass ARGS=\"...\""
	@echo "build-cli      Build the ote-cli wheel into dist/"
	@echo "catalog-check  Verify generated catalog matches the provenance registry"
	@echo "verify         Run the configured deterministic verification checks"
	@echo "govern         Show derived agent contracts"
	@echo "stats          Report cost and token artifacts"
	@echo "eval           Run deterministic evaluation cases"
	@echo "dry-run        Print every installer action without writing files"
	@echo "install        Apply the full profile to the current project"
	@echo "backup         Back up the existing OpenCode configuration"

validate:
	./scripts/validation/validate.sh

validate-links:
	./scripts/validation/validate.sh --links

test:
	python3 -m unittest discover -s tests -t . -v

lint:
	@for file in scripts/installation/*.sh scripts/maintenance/*.sh scripts/validation/*.sh scripts/benchmarking/*.sh benchmarks/harness/*.sh skills/*/*.sh; do \
		bash -n "$$file" || exit 1; \
	done
	@if command -v shellcheck >/dev/null 2>&1; then \
		shellcheck scripts/*/*.sh benchmarks/harness/*.sh skills/*/*.sh; \
	else \
		echo "shellcheck not installed; skipping"; \
	fi

check:
	./scripts/installation/install.sh --check

ci: validate test

ote:
	PYTHONPATH=packages/ote_cli python3 -m ote_cli $(ARGS)

build-cli:
	python3 -m pip wheel ./packages/ote_cli --no-deps --wheel-dir dist

catalog-check:
	python3 scripts/catalog/build_catalog.py --check

verify:
	PYTHONPATH=packages/ote_cli python3 -m ote_cli verify

govern:
	PYTHONPATH=packages/ote_cli python3 -m ote_cli govern contracts

stats:
	PYTHONPATH=packages/ote_cli python3 -m ote_cli stats

eval:
	PYTHONPATH=packages/ote_cli python3 -m ote_cli eval

dry-run:
	./scripts/installation/install.sh --dry-run --all

install:
	./scripts/installation/install.sh --apply --all

backup:
	./scripts/maintenance/backup-config.sh
