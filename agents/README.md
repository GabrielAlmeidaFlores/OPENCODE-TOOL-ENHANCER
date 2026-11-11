# Agents

Canonical agent definitions live in `agents/<role>/AGENT.md`.

Each file is directly usable by OpenCode V2: the frontmatter defines the agent and the Markdown body becomes its system prompt. The installer flattens the path to `.opencode/agents/<role>.md`.

## Roles

| Role | Mode | Can edit | Purpose |
| --- | --- | --- | --- |
| `coordinator` | primary | no | Plan, delegate, verify |
| `planner` | subagent | no | Ordered task plan |
| `researcher` | subagent | no | Evidence-based investigation |
| `architect` | subagent | no | Boundaries and decisions |
| `backend-developer` | subagent | yes | Backend implementation |
| `frontend-developer` | subagent | yes | UI implementation |
| `database-specialist` | subagent | yes | Schema and query changes |
| `code-reviewer` | subagent | no | Independent defect review |
| `test-engineer` | subagent | yes | Tests and evidence |
| `security-reviewer` | subagent | no | Exploitable findings |
| `performance-analyst` | subagent | no | Measured performance |
| `documentation-engineer` | subagent | docs only | Documentation accuracy |

## Install

```bash
mkdir -p .opencode/agents
for f in agents/*/AGENT.md; do
  role=$(basename "$(dirname "$f")")
  cp "$f" ".opencode/agents/$role.md"
done
```

Verify with `opencode debug agents`.

## Rules

- Do not add a role that duplicates another.
- Keep read-only roles without edit permission.
- Subagents must not spawn subagents (`subagent_depth: 1`).
- Model routing belongs in configuration, not in these files.
