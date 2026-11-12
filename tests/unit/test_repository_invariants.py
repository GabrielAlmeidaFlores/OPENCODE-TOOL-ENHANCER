"""
Repository-wide invariant tests that do not depend on the validator internals.

These tests read the real working tree. They fail when a repository convention
from AGENTS.md or the Phase 0 documentation policy regresses.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT


class VersionTests(unittest.TestCase):
    """
    Tests for the VERSION file.
    """

    def test_version_file_exists_and_is_semver(self) -> None:
        """
        VERSION contains a plain semantic version.
        """
        path = REPO_ROOT / "VERSION"
        self.assertTrue(path.exists(), "VERSION is required for release and update checks")
        value = path.read_text(encoding="utf-8").strip()
        self.assertRegex(value, r"^\d+\.\d+\.\d+$")


class DocumentationPolicyTests(unittest.TestCase):
    """
    Tests for the documentation status policy added in Phase 0.
    """

    def _pages(self) -> list[Path]:
        """
        Return every documentation page that must carry a status block.
        """
        return [
            path
            for path in sorted((REPO_ROOT / "docs").rglob("*.md"))
            if "decisions" not in path.parts
        ]

    def test_every_page_has_status_block(self) -> None:
        """
        Each page declares status, verification date, and evidence class.
        """
        missing = []
        for path in self._pages():
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
            if "**Status:**" not in head or "**Last verified:**" not in head or "**Evidence:**" not in head:
                missing.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(missing, [], "pages missing a status block")

    def test_status_values_are_known(self) -> None:
        """
        Status values are limited to the documented vocabulary.
        """
        allowed = {"Stable", "Experimental", "Planned", "Deprecated"}
        for path in self._pages():
            text = path.read_text(encoding="utf-8")
            match = re.search(r"\*\*Status:\*\*\s*([A-Za-z]+)", text)
            self.assertIsNotNone(match, f"{path} has no status value")
            self.assertIn(match.group(1), allowed, f"{path} uses an unknown status")

    def test_last_verified_is_an_iso_date(self) -> None:
        """
        The verification date uses ISO 8601.
        """
        for path in self._pages():
            text = path.read_text(encoding="utf-8")
            match = re.search(r"\*\*Last verified:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
            self.assertIsNotNone(match, f"{path} has no ISO verification date")

    def test_no_html_comments(self) -> None:
        """
        HTML comments are prohibited by AGENTS.md Section 2C.
        """
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in REPO_ROOT.glob("docs/**/*.md")
            if "<!--" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_adr_status_field_present(self) -> None:
        """
        Every ADR declares a status instead of a documentation status block.
        """
        for path in sorted((REPO_ROOT / "docs/decisions").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^- Status: (Accepted|Proposed|Superseded|Rejected)")


class ArtifactInvariantTests(unittest.TestCase):
    """
    Tests for artifact naming and cross-references.
    """

    def test_agent_roles_match_directories(self) -> None:
        """
        Every declared role has a directory and no extra agent directories exist.
        """
        roles = support.AGENT_ROLES
        directories = sorted(
            path.parent.name for path in (REPO_ROOT / "agents").glob("*/AGENT.md")
        )
        self.assertEqual(directories, sorted(roles))

    def test_command_agents_exist(self) -> None:
        """
        Each command targets a real agent directory.
        """
        for path in sorted((REPO_ROOT / "commands").glob("*.md")):
            metadata = _frontmatter(path)
            agent = metadata.get("agent")
            self.assertIsNotNone(agent, f"{path.name} has no agent")
            self.assertTrue(
                (REPO_ROOT / "agents" / agent / "AGENT.md").exists(),
                f"{path.name} targets missing agent {agent}",
            )

    def test_skill_names_match_directories(self) -> None:
        """
        Each skill frontmatter name equals its directory name.
        """
        for path in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
            metadata = _frontmatter(path)
            self.assertEqual(metadata.get("name"), path.parent.name)

    def test_ralph_hats_have_provenance(self) -> None:
        """
        Every Ralph hat collection records source and author attribution.
        """
        for path in sorted((REPO_ROOT / "configs/ralph/hats").glob("*.yml")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:14])
            self.assertIn("# source:", head, f"{path.name} missing source")
            self.assertIn("# author:", head, f"{path.name} missing author")
            self.assertIn("# upstream_commit:", head, f"{path.name} missing commit")

    def test_readme_links_baseline_and_testing(self) -> None:
        """
        The README points at the baseline record and testing guide.
        """
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/research/baseline.md", readme)
        self.assertIn("docs/architecture/testing.md", readme)


class GitSafetyTests(unittest.TestCase):
    """
    Tests that repository automation never stages or commits.
    """

    def test_workflow_yaml_parses(self) -> None:
        """
        Every GitHub Actions workflow is valid YAML.
        """
        validator = support.load_validator()
        for path in sorted((REPO_ROOT / ".github/workflows").glob("*.yml")):
            support.reset_state(validator)
            validator.check_yaml(path)
            self.assertEqual(validator.errors, [], f"{path.name} is not valid YAML")

    def test_workflows_do_not_commit(self) -> None:
        """
        No workflow runs git add, git commit, or git push.
        """
        offenders = []
        for path in sorted((REPO_ROOT / ".github/workflows").glob("*.yml")):
            text = path.read_text(encoding="utf-8")
            for pattern in ("git add", "git commit", "git push", "git stage"):
                if pattern in text:
                    offenders.append(f"{path.name}: {pattern}")
        self.assertEqual(offenders, [])


def _frontmatter(path: Path) -> dict[str, str]:
    """
    Return simple top-level frontmatter fields from a Markdown file.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return fields


if __name__ == "__main__":
    unittest.main()
