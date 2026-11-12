---
# Provenance
# source: https://example.com/upstream
# author: Fixture Author
# author_url: https://example.com/author
# upstream_path: agents/example.md
# upstream_commit: 0000000000000000000000000000000000000000
# retrieved: 2026-11-12
# license: MIT
# modified: fixture only
description: Fixture coordinator used by validator tests.
mode: primary
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "git add*"
    effect: deny
  - action: shell
    resource: "git stage*"
    effect: deny
  - action: shell
    resource: "git commit*"
    effect: deny
  - action: shell
    resource: "git -C * add*"
    effect: deny
  - action: shell
    resource: "git -C * stage*"
    effect: deny
  - action: shell
    resource: "git -C * commit*"
    effect: deny
  - action: shell
    resource: "git -c * add*"
    effect: deny
  - action: shell
    resource: "git -c * stage*"
    effect: deny
  - action: shell
    resource: "git -c * commit*"
    effect: deny
  - action: shell
    resource: "git stash*"
    effect: deny
  - action: shell
    resource: "git reset*"
    effect: deny
  - action: shell
    resource: "git checkout*"
    effect: deny
  - action: shell
    resource: "git clean*"
    effect: deny
---

# Coordinator fixture

This file exists only to exercise the validator.
