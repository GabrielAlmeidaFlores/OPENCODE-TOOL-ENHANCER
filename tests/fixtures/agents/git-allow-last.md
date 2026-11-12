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
description: Agent fixture whose last matching git rule allows the command.
mode: subagent
permissions:
  - action: shell
    resource: "git add*"
    effect: deny
  - action: shell
    resource: "git add*"
    effect: allow
---

# Git allow last fixture
