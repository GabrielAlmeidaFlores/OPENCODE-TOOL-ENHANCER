---
description: Review the current diff for defects and missing tests
agent: code-reviewer
subagent: true
---

Review the current working tree diff.

If `$ARGUMENTS` names a scope, use it. Otherwise review staged and unstaged changes.

Return findings in severity order with file and line references. State what you verified and what you could not. Do not edit files.
