.PHONY: help validate validate-links test lint check ci install dry-run backup

.DEFAULT_GOAL := help

help:
	@echo "validate       Run the repository validator"
	@echo "validate-links Run the validator with external link checks"
	@echo "test           Run the unit and integration test suites"
	@echo "lint           Check shell syntax and run ShellCheck when installed"
	@echo "check          Show installer status without writing files"
	@echo "ci             Run validate and test, matching the default CI gate"
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
	@for file in scripts/installation/*.sh scripts/maintenance/*.sh scripts/validation/*.sh scripts/benchmarking/*.sh benchmarks/harness/*.sh; do \
		bash -n "$$file" || exit 1; \
	done
	@if command -v shellcheck >/dev/null 2>&1; then \
		shellcheck scripts/*/*.sh benchmarks/harness/*.sh; \
	else \
		echo "shellcheck not installed; skipping"; \
	fi

check:
	./scripts/installation/install.sh --check

ci: validate test

dry-run:
	./scripts/installation/install.sh --dry-run --all

install:
	./scripts/installation/install.sh --apply --all

backup:
	./scripts/maintenance/backup-config.sh
