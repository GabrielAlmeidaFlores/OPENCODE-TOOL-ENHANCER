"""Unit tests for scripts/validation/validate_config.py.

The validator is imported as a module, pointed at an isolated temporary root,
and exercised one check at a time. No network access and no writes outside the
temporary directory.
"""
from __future__ import annotations

import contextlib
import io
import sys
import unittest

from tests import support


class ValidatorTestCase(unittest.TestCase):
    """Base class that provides an isolated repository root per test."""

    def setUp(self) -> None:
        """Load a fresh validator module and enter an isolated root."""
        self.validator = support.load_validator()
        self.context = support.isolated_root(self.validator)
        self.root = self.context.__enter__()

    def tearDown(self) -> None:
        """Leave the isolated root and restore the validator module."""
        self.context.__exit__(None, None, None)

    def write(self, relative: str, content: str) -> None:
        """Write a file under the isolated root."""
        support.write_file(self.root, relative, content)

    def assert_error(self, fragment: str) -> None:
        """Assert that at least one recorded error contains the fragment."""
        joined = "\n".join(self.validator.errors)
        self.assertIn(fragment, joined)


class StripJsoncTests(unittest.TestCase):
    """Tests for JSONC comment and trailing-comma removal."""

    def test_removes_comments_and_trailing_commas(self) -> None:
        """Line comments, block comments, and trailing commas are removed."""
        validator = support.load_validator()
        text = '{\n  // line\n  "a": 1, /* block */\n  "b": [1,],\n}'
        stripped = validator.strip_jsonc(text)
        self.assertNotIn("line", stripped)
        self.assertNotIn("block", stripped)
        self.assertNotIn(",]", stripped)
        self.assertNotIn(",}", stripped)

    def test_preserves_comment_markers_inside_strings(self) -> None:
        """URLs and comment-like text inside strings survive stripping."""
        validator = support.load_validator()
        text = '{"url": "https://example.com/a//b", "note": "/* keep */"}'
        self.assertEqual(validator.strip_jsonc(text), text)


class FrontmatterTests(unittest.TestCase):
    """Tests for simple top-level frontmatter extraction."""

    def test_parses_top_level_fields(self) -> None:
        """Quoted and unquoted values are returned without quotes."""
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            path = support.write_file(root, "doc.md", '---\nname: demo\ndescription: "A demo."\n---\nbody\n')
            self.assertEqual(validator.frontmatter(path), {"name": "demo", "description": "A demo."})

    def test_returns_empty_without_frontmatter(self) -> None:
        """A document without a frontmatter block returns an empty mapping."""
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            path = support.write_file(root, "doc.md", "# Title\n")
            self.assertEqual(validator.frontmatter(path), {})


class PermissionParsingTests(unittest.TestCase):
    """Tests for permission block parsing."""

    def test_extracts_action_resource_effect(self) -> None:
        """Each permission item yields one mapping."""
        validator = support.load_validator()
        text = (
            "permissions:\n"
            "  - action: shell\n"
            '    resource: "git add*"\n'
            "    effect: deny\n"
            "  - action: edit\n"
            '    resource: "*"\n'
            "    effect: allow\n"
        )
        parsed = validator.parse_permissions(text)
        self.assertEqual(parsed[0], {"action": "shell", "resource": "git add*", "effect": "deny"})
        self.assertEqual(parsed[1]["effect"], "allow")


class AgentChecksTests(ValidatorTestCase):
    """Tests for agent frontmatter validation."""

    def _only_coordinator(self) -> None:
        """Restrict the validator to the coordinator role."""
        self.validator.AGENT_ROLES = ["coordinator"]

    def test_valid_agent_passes(self) -> None:
        """A complete primary agent produces no errors."""
        self._only_coordinator()
        fixture = (support.FIXTURES / "agents" / "valid-coordinator.md").read_text(encoding="utf-8")
        self.write("agents/coordinator/AGENT.md", fixture)
        self.validator.check_agents()
        self.assertEqual(self.validator.errors, [])

    def test_missing_description_fails(self) -> None:
        """A missing description is reported."""
        self._only_coordinator()
        fixture = (support.FIXTURES / "agents" / "missing-description.md").read_text(encoding="utf-8")
        self.write("agents/coordinator/AGENT.md", fixture)
        self.validator.check_agents()
        self.assert_error("missing description")

    def test_coordinator_requires_primary_mode(self) -> None:
        """A subagent-mode coordinator is rejected."""
        self._only_coordinator()
        fixture = (support.FIXTURES / "agents" / "wrong-mode.md").read_text(encoding="utf-8")
        self.write("agents/coordinator/AGENT.md", fixture)
        self.validator.check_agents()
        self.assert_error("coordinator must be mode: primary")

    def test_specialist_requires_subagent_mode(self) -> None:
        """A primary-mode specialist is rejected."""
        self.validator.AGENT_ROLES = ["planner"]
        self.write("agents/planner/AGENT.md", support.agent_text("planner", mode="primary"))
        self.validator.check_agents()
        self.assert_error("planner must be mode: subagent")

    def test_missing_file_fails(self) -> None:
        """A missing agent file is reported."""
        self._only_coordinator()
        self.validator.check_agents()
        self.assert_error("missing agent")


class SkillChecksTests(ValidatorTestCase):
    """Tests for skill frontmatter validation."""

    def test_valid_skill_passes(self) -> None:
        """A skill whose name matches its directory passes."""
        self.validator.SKILLS = ["valid-skill"]
        fixture = (support.FIXTURES / "skills" / "valid-skill" / "SKILL.md").read_text(encoding="utf-8")
        self.write("skills/valid-skill/SKILL.md", fixture)
        self.validator.check_skills()
        self.assertEqual(self.validator.errors, [])

    def test_name_mismatch_fails(self) -> None:
        """A frontmatter name that differs from the directory is rejected."""
        self.validator.SKILLS = ["name-mismatch"]
        fixture = (support.FIXTURES / "skills" / "name-mismatch" / "SKILL.md").read_text(encoding="utf-8")
        self.write("skills/name-mismatch/SKILL.md", fixture)
        self.validator.check_skills()
        self.assert_error("name must match directory")

    def test_missing_skill_fails(self) -> None:
        """A missing skill file is reported."""
        self.validator.SKILLS = ["absent-skill"]
        self.validator.check_skills()
        self.assert_error("missing skill")


class CommandChecksTests(ValidatorTestCase):
    """Tests for command frontmatter validation."""

    def test_valid_command_passes(self) -> None:
        """A command that targets a known agent passes."""
        self.write("commands/ok.md", support.command_text("planner"))
        self.validator.check_commands()
        self.assertEqual(self.validator.errors, [])

    def test_missing_agent_fails(self) -> None:
        """A command without an agent field is rejected."""
        fixture = (support.FIXTURES / "commands" / "missing-agent.md").read_text(encoding="utf-8")
        self.write("commands/broken.md", fixture)
        self.validator.check_commands()
        self.assert_error("missing agent")

    def test_unknown_agent_fails(self) -> None:
        """A command that targets an unknown agent is rejected."""
        fixture = (support.FIXTURES / "commands" / "unknown-agent.md").read_text(encoding="utf-8")
        self.write("commands/broken.md", fixture)
        self.validator.check_commands()
        self.assert_error("unknown agent")


class ProvenanceTests(ValidatorTestCase):
    """Tests for AGENTS.md Section 2A enforcement."""

    def _registry(self, entries: list[tuple[str, str]]) -> None:
        """Write a provenance registry with the given entries."""
        self.write("docs/provenance/registry.yml", support.registry_text(entries))

    def test_complete_metadata_passes(self) -> None:
        """Agents, commands, skills, and hats with attribution pass."""
        self._registry([("coordinator", "agents/coordinator/AGENT.md")])
        self.write("agents/coordinator/AGENT.md", support.agent_text("coordinator", mode="primary"))
        self.write("commands/review.md", support.command_text("coordinator"))
        self.write("skills/demo/SKILL.md", support.skill_text("demo"))
        self.write(
            "configs/ralph/hats/demo.yml",
            "# Name: Demo\n# Purpose: Fixture.\n# Provenance\n# source: https://example.com\n"
            "# author: Fixture Author\n# author_url: https://example.com/author\n"
            "# upstream_commit: 0000000000000000000000000000000000000000\n"
            "# license: MIT\n",
        )
        self.validator.check_provenance()
        self.assertEqual(self.validator.errors, [])

    def test_missing_source_header_fails(self) -> None:
        """An agent without a source header is rejected."""
        self._registry([])
        fixture = (support.FIXTURES / "agents" / "missing-provenance.md").read_text(encoding="utf-8")
        self.write("agents/example/AGENT.md", fixture)
        self.validator.check_provenance()
        self.assert_error("missing provenance header")

    def test_missing_author_fails(self) -> None:
        """An agent without author attribution is rejected."""
        self._registry([])
        self.write(
            "agents/example/AGENT.md",
            "---\n# source: https://example.com\n# upstream_commit: abc\ndescription: x\n---\nbody\n",
        )
        self.validator.check_provenance()
        self.assert_error("missing author attribution")

    def test_registry_points_to_missing_path_fails(self) -> None:
        """A registry entry that references a missing local path is rejected."""
        self._registry([("ghost", "agents/ghost/AGENT.md")])
        self.validator.check_provenance()
        self.assert_error("provenance registry points to missing path")


class GitPermissionTests(ValidatorTestCase):
    """Tests for the last-match-wins git deny rule."""

    def test_deny_last_passes(self) -> None:
        """The complete deny set satisfies every git command probe."""
        self.validator.AGENT_ROLES = ["coordinator"]
        self.write("agents/coordinator/AGENT.md", support.agent_text("coordinator", mode="primary"))
        self.validator.check_git_permissions()
        self.assertEqual(self.validator.errors, [])

    def test_allow_last_fails(self) -> None:
        """A later allow rule overrides an earlier deny rule."""
        self.validator.AGENT_ROLES = ["coordinator"]
        fixture = (support.FIXTURES / "agents" / "git-allow-last.md").read_text(encoding="utf-8")
        self.write("agents/coordinator/AGENT.md", fixture)
        self.validator.check_git_permissions()
        self.assert_error("instead of deny")


class JsoncChecksTests(ValidatorTestCase):
    """Tests for JSONC syntax and V2 shape checks."""

    def test_header_only_comments_pass(self) -> None:
        """A documentation header before the object is allowed."""
        self.write(
            "configs/opencode/opencode.jsonc",
            "// Name: Fixture\n// Purpose: Fixture.\n// Usage: tests.\n// Validation: tests.\n"
            '// References: tests.\n{\n  "$schema": "https://opencode.ai/config.json",\n'
            '  "mcp": {"servers": {}}\n}\n',
        )
        self.validator.check_jsonc(self.root / "configs/opencode/opencode.jsonc")
        self.assertEqual(self.validator.errors, [])

    def test_inline_body_comment_fails(self) -> None:
        """A comment after the opening brace is reported by the policy check."""
        source = (support.FIXTURES / "config" / "commented-body.jsonc").read_text(encoding="utf-8")
        self.write("configs/opencode/opencode.jsonc", source)
        self.validator.check_comment_policy()
        self.assert_error("inline JSONC comments are prohibited")

    def test_missing_servers_fails(self) -> None:
        """OpenCode V2 requires mcp.servers."""
        source = (support.FIXTURES / "config" / "missing-servers.jsonc").read_text(encoding="utf-8")
        self.write("configs/opencode/opencode.jsonc", source)
        self.validator.check_jsonc(self.root / "configs/opencode/opencode.jsonc")
        self.assert_error("V2 requires mcp.servers")

    def test_invalid_json_fails(self) -> None:
        """Broken JSONC is reported instead of raising."""
        self.write("configs/opencode/opencode.jsonc", "{ nope")
        self.validator.check_jsonc(self.root / "configs/opencode/opencode.jsonc")
        self.assert_error("invalid JSONC")


class YamlChecksTests(ValidatorTestCase):
    """Tests for YAML syntax checking."""

    def test_valid_yaml_passes(self) -> None:
        """A well-formed document records no error."""
        self.write("configs/ralph/ralph.yml", "name: fixture\nsteps: 1\n")
        self.validator.check_yaml(self.root / "configs/ralph/ralph.yml")
        self.assertEqual(self.validator.errors, [])

    def test_invalid_yaml_fails(self) -> None:
        """Unterminated flow collections are reported when a parser exists."""
        self.write("configs/ralph/ralph.yml", "key: [unterminated\n")
        self.validator.check_yaml(self.root / "configs/ralph/ralph.yml")
        self.assertTrue(self.validator.errors or self.validator.warnings)


class CommentPolicyTests(ValidatorTestCase):
    """Tests for the documentation-comment policy."""

    def test_python_inline_comment_fails(self) -> None:
        """A Python comment that is not a tool directive is rejected."""
        self.write("scripts/demo.py", '"""Module docstring."""\nvalue = 1  # explain\n')
        self.validator.check_comment_policy()
        self.assert_error("non-documentation Python comment")

    def test_python_docstrings_only_pass(self) -> None:
        """A module and function docstring pass without comments."""
        self.write(
            "scripts/demo.py",
            '"""Module docstring."""\n\n\ndef run() -> int:\n    """Return one."""\n    return 1\n',
        )
        self.validator.check_comment_policy()
        self.assertEqual(self.validator.errors, [])

    def test_shell_inline_comment_fails(self) -> None:
        """A shell comment after executable text is rejected."""
        self.write(
            "scripts/demo.sh",
            "#!/usr/bin/env bash\n# Name: Demo\n# Purpose: Fixture.\nset -eu\necho hi # note\n",
        )
        self.validator.check_comment_policy()
        self.assert_error("inline shell comments are prohibited")

    def test_shell_full_line_comment_passes(self) -> None:
        """A full-line comment is documentation and passes."""
        self.write(
            "scripts/demo.sh",
            "#!/usr/bin/env bash\n# Name: Demo\n# Purpose: Fixture.\n# Usage: tests.\n"
            "# Arguments: none.\n# Environment: none.\n# Outputs: none.\n"
            "# Side effects: none.\n# References: tests.\nset -eu\necho hi\n",
        )
        self.validator.check_comment_policy()
        self.assertEqual(self.validator.errors, [])

    def test_missing_shell_header_fails(self) -> None:
        """A shell script without a documentation header is rejected."""
        self.write("scripts/demo.sh", "#!/usr/bin/env bash\necho hi\n")
        self.validator.check_comment_policy()
        self.assert_error("missing shell documentation header")


class TaskChecksTests(ValidatorTestCase):
    """Tests for benchmark task definitions."""

    def test_valid_task_passes(self) -> None:
        """A complete task with an existing working directory passes."""
        self.write(
            "benchmarks/tasks/demo.json",
            '{"id": "demo", "prompt": "x", "verification": "true", "working_directory": "."}',
        )
        self.validator.check_tasks()
        self.assertEqual(self.validator.errors, [])

    def test_missing_field_fails(self) -> None:
        """A task without a verification command is rejected."""
        source = (support.FIXTURES / "tasks" / "missing-field.json").read_text(encoding="utf-8")
        self.write("benchmarks/tasks/demo.json", source)
        self.validator.check_tasks()
        self.assert_error("missing or empty verification")

    def test_missing_working_directory_fails(self) -> None:
        """A task that points at a missing directory is rejected."""
        source = (support.FIXTURES / "tasks" / "missing-workdir.json").read_text(encoding="utf-8")
        self.write("benchmarks/tasks/demo.json", source)
        self.validator.check_tasks()
        self.assert_error("working_directory does not exist")


class DocsStatusTests(ValidatorTestCase):
    """Tests for the Phase 0 documentation status policy."""

    def _page(self, status: str = "Stable", date: str = "2026-11-12") -> str:
        """Build a documentation page with the given status block."""
        return (
            "# Page\n\n"
            f"> **Status:** {status} · **Last verified:** {date} · **Evidence:** verified locally\n\n"
            "Body.\n"
        )

    def test_complete_status_block_passes(self) -> None:
        """A page with all three fields and an ISO date passes."""
        self.write("docs/page.md", self._page())
        self.validator.check_docs_status()
        self.assertEqual(self.validator.errors, [])

    def test_missing_status_block_fails(self) -> None:
        """A page without a status block is rejected."""
        self.write("docs/page.md", "# Page\n\nBody.\n")
        self.validator.check_docs_status()
        self.assert_error("missing documentation status field")

    def test_unknown_status_fails(self) -> None:
        """A status value outside the vocabulary is rejected."""
        self.write("docs/page.md", self._page(status="Maybe"))
        self.validator.check_docs_status()
        self.assert_error("unknown documentation status")

    def test_non_iso_date_fails(self) -> None:
        """A human-readable date is rejected in favor of ISO 8601."""
        self.write("docs/page.md", self._page(date="12 November 2026"))
        self.validator.check_docs_status()
        self.assert_error("last verified date must be ISO 8601")

    def test_decisions_are_exempt(self) -> None:
        """ADRs carry their own status field and are skipped."""
        self.write("docs/decisions/ADR-999-example.md", "# ADR-999\n\n- Status: Accepted\n")
        self.validator.check_docs_status()
        self.assertEqual(self.validator.errors, [])


class MainCompositionTests(ValidatorTestCase):
    """Tests that main() wires every check, not only the units under test."""

    def _run_main(self) -> tuple[int, str]:
        """Run main() with the isolated root and capture its output."""
        original_argv = sys.argv
        sys.argv = ["validate_config.py"]
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                code = self.validator.main()
        finally:
            sys.argv = original_argv
        return code, buffer.getvalue()

    def test_main_fails_on_missing_docs_status(self) -> None:
        """A missing docs status block is detected by the full validator."""
        self.write("docs/page.md", "# Page\n\nBody.\n")
        code, output = self._run_main()
        self.assertEqual(code, 1)
        self.assertIn("missing documentation status field", output)

    def test_main_fails_on_missing_provenance(self) -> None:
        """A missing provenance header is detected by the full validator."""
        fixture = (support.FIXTURES / "agents" / "missing-provenance.md").read_text(encoding="utf-8")
        self.write("agents/example/AGENT.md", fixture)
        self.write("docs/provenance/registry.yml", support.registry_text([]))
        code, output = self._run_main()
        self.assertEqual(code, 1)
        self.assertIn("missing provenance header", output)

    def test_main_fails_on_invalid_workflow_yaml(self) -> None:
        """Broken workflow YAML is detected by the full validator."""
        self.write(".github/workflows/bad.yml", "key: [unterminated\n")
        code, output = self._run_main()
        if "No YAML parser" in output:
            self.skipTest("no YAML parser available")
        self.assertEqual(code, 1)
        self.assertIn("invalid YAML", output)


class HelperTests(unittest.TestCase):
    """Tests for comment-detection helpers."""

    def test_shell_inline_comment_ignores_shebang_and_quotes(self) -> None:
        """Comment markers inside quotes and a leading shebang are not inline comments."""
        validator = support.load_validator()
        self.assertFalse(validator.shell_inline_comment("#!/usr/bin/env bash"))
        self.assertFalse(validator.shell_inline_comment('echo "# not a comment"'))
        self.assertTrue(validator.shell_inline_comment("echo hi # note"))
        self.assertFalse(validator.shell_inline_comment("    # full line"))
        self.assertFalse(validator.shell_inline_comment("echo ${#array[@]}"))

    def test_jsonc_comment_lines_reports_line_numbers(self) -> None:
        """Comments outside strings are reported with their line number."""
        validator = support.load_validator()
        text = '// header\n{\n  "a": "// not a comment",\n  // body\n  "b": 1\n}\n'
        self.assertEqual(validator.jsonc_comment_lines(text), [1, 4])


if __name__ == "__main__":
    unittest.main()
