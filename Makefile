.PHONY: validate check install dry-run backup

validate:
	./scripts/validation/validate.sh

validate-links:
	./scripts/validation/validate.sh --links

check:
	./scripts/installation/install.sh --check

dry-run:
	./scripts/installation/install.sh --dry-run --all

install:
	./scripts/installation/install.sh --apply --all

backup:
	./scripts/maintenance/backup-config.sh
