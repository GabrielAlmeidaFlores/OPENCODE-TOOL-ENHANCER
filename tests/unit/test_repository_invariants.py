"""
Repository-wide invariant tests that do not depend on the validator internals.

These tests read the real working tree. They fail when a repository convention
from AGENTS.md or the Phase 0 documentation policy regresses.
"""
from __future__ import annotations
from tests.unit.test_repository_invariants_strings import (
    TEXT_HAS_NO_STATUS_VALUE,
    TEXT_USES_UNKNOWN_STATUS,
    TEXT_HAS_NO_ISO_DATE,
    TEXT_HAS_NO_AGENT,
    TEXT_TARGETS_MISSING_AGENT,
    TEXT_MISSING_SOURCE,
    TEXT_MISSING_AUTHOR,
    TEXT_MISSING_COMMIT,
    TEXT_NOT_VALID_YAML,
)
from tests.unit.test_repository_invariants_strings import (
    FLAG_TEXT,
    KEY_AGENT,
    KEY_AGENTS,
    KEY_COMMANDS,
    KEY_DECISIONS,
    KEY_DOCS,
    KEY_NAME,
    KEY_SKILLS,
    TEXT_AGENT_MD,
    TEXT_AGENT_MD_2,
    TEXT_AUTHOR,
    TEXT_A_ZA_Z0_9_S,
    TEXT_CONFIGS_RALPH_HATS,
    TEXT_DEPRECATED,
    TEXT_DOCS_ARCHITECTURE_TESTING_MD,
    TEXT_DOCS_DECISIONS,
    TEXT_DOCS_MD,
    TEXT_DOCS_RESEARCH_BASELINE_MD,
    TEXT_D_D_D,
    TEXT_EVIDENCE,
    TEXT_EXPERIMENTAL,
    TEXT_GITHUB_WORKFLOWS,
    TEXT_GIT_ADD,
    TEXT_GIT_COMMIT,
    TEXT_GIT_PUSH,
    TEXT_GIT_STAGE,
    TEXT_LAST_VERIFIED,
    TEXT_LAST_VERIFIED_S_D_4_D_2_D_2,
    TEXT_MAIN,
    TEXT_MD,
    TEXT_M_STATUS_ACCEPTED_PROPOSED_SUPERSEDED_REJECTED,
    TEXT_PAGES_MISSING_A_STATUS_BLOCK,
    TEXT_PLANNED,
    TEXT_README_MD,
    TEXT_SKILL_MD,
    TEXT_SOURCE,
    TEXT_STABLE,
    TEXT_STATUS,
    TEXT_STATUS_S_A_ZA_Z,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_TEXT_5,
    TEXT_UPSTREAM_COMMIT,
    TEXT_UTF_8,
    TEXT_VERSION,
    TEXT_VERSION_IS_REQUIRED_FOR_RELEASE_AND_UPDATE_CHECKS,
    TEXT_YML,
)

import re
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT


class VersionTests(unittest.TestCase):

    def test_version_file_exists_and_is_semver(self) -> None:
        path = REPO_ROOT / TEXT_VERSION
        self.assertTrue(path.exists(), TEXT_VERSION_IS_REQUIRED_FOR_RELEASE_AND_UPDATE_CHECKS)
        value = path.read_text(encoding=TEXT_UTF_8).strip()
        self.assertRegex(value, TEXT_D_D_D)


class DocumentationPolicyTests(unittest.TestCase):

    def _pages(self) -> list[Path]:
        return [
            path
            for path in sorted((REPO_ROOT / KEY_DOCS).rglob(TEXT_MD))
            if KEY_DECISIONS not in path.parts
        ]

    def test_every_page_has_status_block(self) -> None:
        missing = []
        for path in self._pages():
            head = TEXT_TEXT.join(path.read_text(encoding=TEXT_UTF_8).splitlines()[:8])
            if TEXT_STATUS not in head or TEXT_LAST_VERIFIED not in head or TEXT_EVIDENCE not in head:
                missing.append(path.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(missing, [], TEXT_PAGES_MISSING_A_STATUS_BLOCK)

    def test_status_values_are_known(self) -> None:
        allowed = {TEXT_STABLE, TEXT_EXPERIMENTAL, TEXT_PLANNED, TEXT_DEPRECATED}
        for path in self._pages():
            text = path.read_text(encoding=TEXT_UTF_8)
            match = re.search(TEXT_STATUS_S_A_ZA_Z, text)
            self.assertIsNotNone(match, TEXT_HAS_NO_STATUS_VALUE.format(path))
            self.assertIn(match.group(1), allowed, TEXT_USES_UNKNOWN_STATUS.format(path))

    def test_last_verified_is_an_iso_date(self) -> None:
        for path in self._pages():
            text = path.read_text(encoding=TEXT_UTF_8)
            match = re.search(TEXT_LAST_VERIFIED_S_D_4_D_2_D_2, text)
            self.assertIsNotNone(match, TEXT_HAS_NO_ISO_DATE.format(path))

    def test_no_html_comments(self) -> None:
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in REPO_ROOT.glob(TEXT_DOCS_MD)
            if TEXT_TEXT_2 in path.read_text(encoding=TEXT_UTF_8)
        ]
        self.assertEqual(offenders, [])

    def test_adr_status_field_present(self) -> None:
        for path in sorted((REPO_ROOT / TEXT_DOCS_DECISIONS).glob(TEXT_MD)):
            text = path.read_text(encoding=TEXT_UTF_8)
            self.assertRegex(text, TEXT_M_STATUS_ACCEPTED_PROPOSED_SUPERSEDED_REJECTED)


class ArtifactInvariantTests(unittest.TestCase):

    def test_agent_roles_match_directories(self) -> None:
        roles = support.AGENT_ROLES
        directories = sorted(
            path.parent.name for path in (REPO_ROOT / KEY_AGENTS).glob(TEXT_AGENT_MD)
        )
        self.assertEqual(directories, sorted(roles))

    def test_command_agents_exist(self) -> None:
        for path in sorted((REPO_ROOT / KEY_COMMANDS).glob(TEXT_MD)):
            metadata = render_memory_frontmatter(path)
            agent = metadata.get(KEY_AGENT)
            self.assertIsNotNone(agent, TEXT_HAS_NO_AGENT.format(path.name))
            self.assertTrue(
                (REPO_ROOT / KEY_AGENTS / agent / TEXT_AGENT_MD_2).exists(),
                TEXT_TARGETS_MISSING_AGENT.format(path.name, agent),
            )

    def test_skill_names_match_directories(self) -> None:
        for path in sorted((REPO_ROOT / KEY_SKILLS).glob(TEXT_SKILL_MD)):
            metadata = render_memory_frontmatter(path)
            self.assertEqual(metadata.get(KEY_NAME), path.parent.name)

    def test_ralph_hats_have_provenance(self) -> None:
        for path in sorted((REPO_ROOT / TEXT_CONFIGS_RALPH_HATS).glob(TEXT_YML)):
            head = TEXT_TEXT.join(path.read_text(encoding=TEXT_UTF_8).splitlines()[:14])
            self.assertIn(TEXT_SOURCE, head, TEXT_MISSING_SOURCE.format(path.name))
            self.assertIn(TEXT_AUTHOR, head, TEXT_MISSING_AUTHOR.format(path.name))
            self.assertIn(TEXT_UPSTREAM_COMMIT, head, TEXT_MISSING_COMMIT.format(path.name))

    def test_readme_links_baseline_and_testing(self) -> None:
        readme = (REPO_ROOT / TEXT_README_MD).read_text(encoding=TEXT_UTF_8)
        self.assertIn(TEXT_DOCS_RESEARCH_BASELINE_MD, readme)
        self.assertIn(TEXT_DOCS_ARCHITECTURE_TESTING_MD, readme)


class GitSafetyTests(unittest.TestCase):

    def test_workflow_yaml_parses(self) -> None:
        validator = support.load_validator()
        for path in sorted((REPO_ROOT / TEXT_GITHUB_WORKFLOWS).glob(TEXT_YML)):
            support.reset_state(validator)
            validator.check_yaml(path)
            self.assertEqual(validator.errors, [], TEXT_NOT_VALID_YAML.format(path.name))

    def test_workflows_do_not_commit(self) -> None:
        offenders = []
        for path in sorted((REPO_ROOT / TEXT_GITHUB_WORKFLOWS).glob(TEXT_YML)):
            text = path.read_text(encoding=TEXT_UTF_8)
            for pattern in (TEXT_GIT_ADD, TEXT_GIT_COMMIT, TEXT_GIT_PUSH, TEXT_GIT_STAGE):
                if pattern in text:
                    offenders.append(TEXT_OFFENDER.format(path.name, pattern))
        self.assertEqual(offenders, [])


def render_memory_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding=TEXT_UTF_8)
    if not text.startswith(FLAG_TEXT):
        return {}
    end = text.find(TEXT_TEXT_3, 3)
    if end == -1:
        return {}
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        match = re.match(TEXT_A_ZA_Z0_9_S, line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip(TEXT_TEXT_4).strip(TEXT_TEXT_5)
    return fields


if __name__ == TEXT_MAIN:
    unittest.main()
