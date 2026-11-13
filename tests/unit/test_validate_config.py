"""
Unit tests for scripts/validation/validate_config.py.

The validator is imported as a module, pointed at an isolated temporary root,
and exercised one check at a time. No network access and no writes outside the
temporary directory.
"""
from __future__ import annotations
from tests.unit.test_validate_config_strings import (
    FLAG_NAME_DEMO_DESCRIPTION_A_DEMO_BODY,
    FLAG_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM_COMMIT_ABC_DESCRIPTION_X_B,
    KEY_ACTION,
    KEY_AGENTS,
    KEY_ALLOW,
    KEY_BLOCK,
    KEY_COMMANDS,
    KEY_CONFIG,
    KEY_COORDINATOR,
    KEY_DEMO,
    KEY_DENY,
    KEY_DESCRIPTION,
    KEY_EFFECT,
    KEY_GHOST,
    KEY_LINE,
    KEY_NAME,
    KEY_PACKAGES,
    KEY_PLANNER,
    KEY_PRIMARY,
    KEY_RESOURCE,
    KEY_SHELL,
    KEY_SKILLS,
    KEY_TASKS,
    TEXT_12_NOVEMBER_2026,
    TEXT_2026_11_12,
    TEXT_ABSENT_SKILL,
    TEXT_ADDS_TWO_NUMBERS_EXPORT_FUNCTION_ADD_A_NUMBER_B_NUMBER_NUMBE,
    TEXT_ADR_999_STATUS_ACCEPTED,
    TEXT_AGENTS_COORDINATOR_AGENT_MD,
    TEXT_AGENTS_EXAMPLE_AGENT_MD,
    TEXT_AGENTS_GHOST_AGENT_MD,
    TEXT_AGENTS_PLANNER_AGENT_MD,
    TEXT_A_DEMO,
    TEXT_BENCHMARKS_TASKS_DEMO_JSON,
    TEXT_BODY,
    TEXT_COMMANDS_BROKEN_MD,
    TEXT_COMMANDS_OK_MD,
    TEXT_COMMANDS_REVIEW_MD,
    TEXT_COMMENTED_BODY_JSONC,
    TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC,
    TEXT_CONFIGS_RALPH_HATS_DEMO_YML,
    TEXT_CONFIGS_RALPH_RALPH_YML,
    TEXT_COORDINATOR_MUST_BE_MODE_PRIMARY,
    TEXT_DOCS_DECISIONS_ADR_999_EXAMPLE_MD,
    TEXT_DOCS_PAGE_MD,
    TEXT_DOCS_PROVENANCE_REGISTRY_YML,
    TEXT_DOC_MD,
    TEXT_ECHO_ARRAY,
    TEXT_ECHO_HI_NOTE,
    TEXT_ECHO_NOT_A_COMMENT,
    TEXT_EXAMPLES_DEMO_FILE_CS,
    TEXT_EXAMPLES_DEMO_FILE_TS,
    TEXT_EXPORT_CONST_URL_HTTPS_EXAMPLE_COM,
    TEXT_EXPORT_CONST_VALUE_1_NOTE,
    TEXT_FROM_FUTURE_IMPORT_ANNOTATIONS_DEF_RUN_INT_RETURN_ONE_RETURN,
    TEXT_FULL_LINE,
    TEXT_GITHUB_WORKFLOWS_BAD_YML,
    TEXT_GIT_ADD,
    TEXT_GIT_ALLOW_LAST_MD,
    TEXT_HEADER_A_NOT_A_COMMENT_BODY_B_1,
    TEXT_ID_DEMO_PROMPT_X_VERIFICATION_TRUE_WORKING_DIRECTORY,
    TEXT_INLINE_JSONC_COMMENTS_ARE_PROHIBITED,
    TEXT_INLINE_SHELL_COMMENTS_ARE_PROHIBITED,
    TEXT_INSTEAD_OF_DENY,
    TEXT_INVALID_JSONC,
    TEXT_INVALID_YAML,
    TEXT_KEY_UNTERMINATED,
    TEXT_LAST_VERIFIED_DATE_MUST_BE_ISO_8601,
    TEXT_LINE_A_1_BLOCK_B_1,
    TEXT_LINE_COMMENTS_ARE_PROHIBITED,
    TEXT_MAIN,
    TEXT_MAYBE,
    TEXT_MISSING_AGENT,
    TEXT_MISSING_AGENT_MD,
    TEXT_MISSING_AUTHOR_ATTRIBUTION,
    TEXT_MISSING_DESCRIPTION,
    TEXT_MISSING_DESCRIPTION_MD,
    TEXT_MISSING_DOCUMENTATION_STATUS_FIELD,
    TEXT_MISSING_FIELD_JSON,
    TEXT_MISSING_OR_EMPTY_VERIFICATION,
    TEXT_MISSING_PROVENANCE_HEADER,
    TEXT_MISSING_PROVENANCE_MD,
    TEXT_MISSING_SERVERS_JSONC,
    TEXT_MISSING_SHELL_DOCUMENTATION_HEADER,
    TEXT_MISSING_SKILL,
    TEXT_MISSING_WORKDIR_JSON,
    TEXT_MODULE,
    TEXT_MODULE_DEF_RUN_INT_RETURN_1,
    TEXT_MODULE_DEF_RUN_INT_RETURN_ONE_RETURN_1,
    TEXT_MODULE_DEF_RUN_INT_RETURN_ONE_RETURN_1_2,
    TEXT_MODULE_DOCSTRING_DEF_RUN_INT_RETURN_ONE_RETURN_1,
    TEXT_MODULE_DOCSTRING_VALUE_1_EXPLAIN,
    TEXT_MODULE_DOCUMENTATION_CLASS_RUNNER_RUNS_WORK_DEF_RUN_SELF_INT,
    TEXT_MODULE_IS_MISSING_A_DOCSTRING,
    TEXT_MODULE_VALUE_1_NOTE,
    TEXT_MUST_PLACE_THE_TRIPLE_QUOTES_ON_THEIR_OWN_LINES,
    TEXT_NAME_FIXTURE_STEPS_1,
    TEXT_NAME_MISMATCH,
    TEXT_NAME_MUST_MATCH_DIRECTORY,
    TEXT_NON_DOCUMENTATION_PYTHON_COMMENT,
    TEXT_NOPE,
    TEXT_NOTE_EXPORT_CONST_VALUE_1,
    TEXT_NOTE_PUBLIC_STATIC_CLASS_MATHHELPERS,
    TEXT_NO_YAML_PARSER,
    TEXT_NO_YAML_PARSER_AVAILABLE,
    TEXT_ONE_LINE,
    TEXT_PACKAGES_DEMO_BUILD_MODULE_PY,
    TEXT_PACKAGES_DEMO_MODULE_PY,
    TEXT_PACKAGES_DEMO_PKG_EGG_INFO_MODULE_PY,
    TEXT_PACKAGES_DEMO_PKG_MODULE_PY,
    TEXT_PAGE,
    TEXT_PAGE_BODY,
    TEXT_PLANNER_MUST_BE_MODE_SUBAGENT,
    TEXT_PROVENANCE_REGISTRY_POINTS_TO_MISSING_PATH,
    TEXT_SCRIPTS_DEMO_PY,
    TEXT_SCRIPTS_DEMO_SH,
    TEXT_SKILLS_DEMO_ASSET_PY,
    TEXT_SKILLS_DEMO_FIND_SH,
    TEXT_SKILLS_DEMO_SKILL_MD,
    TEXT_SKILLS_NAME_MISMATCH_SKILL_MD,
    TEXT_SKILLS_VALID_SKILL_SKILL_MD,
    TEXT_SKILL_MD,
    TEXT_STABLE,
    TEXT_STATUS_BLOCK,
    TEXT_SUMMARY_ADDS_TWO_NUMBERS_SUMMARY_PUBLIC_STATIC_CLASS_MATHHEL,
    TEXT_TESTS_FIXTURES_BAD_PY,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TITLE,
    TEXT_UNKNOWN_AGENT,
    TEXT_UNKNOWN_AGENT_MD,
    TEXT_UNKNOWN_DOCUMENTATION_STATUS,
    TEXT_URL_HTTPS_EXAMPLE_COM_A_B_NOTE_KEEP,
    TEXT_USR_BIN_ENV_BASH,
    TEXT_USR_BIN_ENV_BASH_ECHO_HI,
    TEXT_USR_BIN_ENV_BASH_NAME_DEMO_PURPOSE_FIXTURE_SET_EU_ECHO_HI_NO,
    TEXT_UTF_8,
    TEXT_V2_REQUIRES_MCP_SERVERS,
    TEXT_VALIDATE_CONFIG_PY,
    TEXT_VALID_COORDINATOR_MD,
    TEXT_VALID_SKILL,
    TEXT_WORKING_DIRECTORY_DOES_NOT_EXIST,
    TEXT_WRONG_MODE_MD,
)

import contextlib
import io
import sys
import unittest

from tests import support


class ValidatorTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.validator = support.load_validator()
        self.context = support.isolated_root(self.validator)
        self.root = self.context.__enter__()

    def tearDown(self) -> None:
        self.context.__exit__(None, None, None)

    def write(self, relative: str, content: str) -> None:
        support.write_file(self.root, relative, content)

    def assert_error(self, fragment: str) -> None:
        joined = TEXT_TEXT.join(self.validator.errors)
        self.assertIn(fragment, joined)


class StripJsoncTests(unittest.TestCase):

    def test_removes_comments_and_trailing_commas(self) -> None:
        validator = support.load_validator()
        text = TEXT_LINE_A_1_BLOCK_B_1
        stripped = validator.strip_jsonc(text)
        self.assertNotIn(KEY_LINE, stripped)
        self.assertNotIn(KEY_BLOCK, stripped)
        self.assertNotIn(TEXT_TEXT_2, stripped)
        self.assertNotIn(TEXT_TEXT_3, stripped)

    def test_preserves_comment_markers_inside_strings(self) -> None:
        validator = support.load_validator()
        text = TEXT_URL_HTTPS_EXAMPLE_COM_A_B_NOTE_KEEP
        self.assertEqual(validator.strip_jsonc(text), text)


class FrontmatterTests(unittest.TestCase):

    def test_parses_top_level_fields(self) -> None:
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            path = support.write_file(root, TEXT_DOC_MD, FLAG_NAME_DEMO_DESCRIPTION_A_DEMO_BODY)
            self.assertEqual(validator.read_frontmatter(path), {KEY_NAME: KEY_DEMO, KEY_DESCRIPTION: TEXT_A_DEMO})

    def test_returns_empty_without_frontmatter(self) -> None:
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            path = support.write_file(root, TEXT_DOC_MD, TEXT_TITLE)
            self.assertEqual(validator.read_frontmatter(path), {})


class PermissionParsingTests(unittest.TestCase):

    def test_extracts_action_resource_effect(self) -> None:
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
        self.assertEqual(parsed[0], {KEY_ACTION: KEY_SHELL, KEY_RESOURCE: TEXT_GIT_ADD, KEY_EFFECT: KEY_DENY})
        self.assertEqual(parsed[1][KEY_EFFECT], KEY_ALLOW)


class AgentChecksTests(ValidatorTestCase):

    def _only_coordinator(self) -> None:
        self.validator.AGENT_ROLES = [KEY_COORDINATOR]

    def test_valid_agent_passes(self) -> None:
        self._only_coordinator()
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_VALID_COORDINATOR_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, fixture)
        self.validator.check_agents()
        self.assertEqual(self.validator.errors, [])

    def test_missing_description_fails(self) -> None:
        self._only_coordinator()
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_MISSING_DESCRIPTION_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, fixture)
        self.validator.check_agents()
        self.assert_error(TEXT_MISSING_DESCRIPTION)

    def test_coordinator_requires_primary_mode(self) -> None:
        self._only_coordinator()
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_WRONG_MODE_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, fixture)
        self.validator.check_agents()
        self.assert_error(TEXT_COORDINATOR_MUST_BE_MODE_PRIMARY)

    def test_specialist_requires_subagent_mode(self) -> None:
        self.validator.AGENT_ROLES = [KEY_PLANNER]
        self.write(TEXT_AGENTS_PLANNER_AGENT_MD, support.agent_text(KEY_PLANNER, mode=KEY_PRIMARY))
        self.validator.check_agents()
        self.assert_error(TEXT_PLANNER_MUST_BE_MODE_SUBAGENT)

    def test_missing_file_fails(self) -> None:
        self._only_coordinator()
        self.validator.check_agents()
        self.assert_error(TEXT_MISSING_AGENT)


class SkillChecksTests(ValidatorTestCase):

    def test_valid_skill_passes(self) -> None:
        self.validator.SKILLS = [TEXT_VALID_SKILL]
        fixture = (support.FIXTURES / KEY_SKILLS / TEXT_VALID_SKILL / TEXT_SKILL_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_SKILLS_VALID_SKILL_SKILL_MD, fixture)
        self.validator.check_skills()
        self.assertEqual(self.validator.errors, [])

    def test_name_mismatch_fails(self) -> None:
        self.validator.SKILLS = [TEXT_NAME_MISMATCH]
        fixture = (support.FIXTURES / KEY_SKILLS / TEXT_NAME_MISMATCH / TEXT_SKILL_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_SKILLS_NAME_MISMATCH_SKILL_MD, fixture)
        self.validator.check_skills()
        self.assert_error(TEXT_NAME_MUST_MATCH_DIRECTORY)

    def test_missing_skill_fails(self) -> None:
        self.validator.SKILLS = [TEXT_ABSENT_SKILL]
        self.validator.check_skills()
        self.assert_error(TEXT_MISSING_SKILL)


class CommandChecksTests(ValidatorTestCase):

    def test_valid_command_passes(self) -> None:
        self.write(TEXT_COMMANDS_OK_MD, support.command_text(KEY_PLANNER))
        self.validator.check_commands()
        self.assertEqual(self.validator.errors, [])

    def test_missing_agent_fails(self) -> None:
        fixture = (support.FIXTURES / KEY_COMMANDS / TEXT_MISSING_AGENT_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_COMMANDS_BROKEN_MD, fixture)
        self.validator.check_commands()
        self.assert_error(TEXT_MISSING_AGENT)

    def test_unknown_agent_fails(self) -> None:
        fixture = (support.FIXTURES / KEY_COMMANDS / TEXT_UNKNOWN_AGENT_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_COMMANDS_BROKEN_MD, fixture)
        self.validator.check_commands()
        self.assert_error(TEXT_UNKNOWN_AGENT)


class ProvenanceTests(ValidatorTestCase):

    def _registry(self, entries: list[tuple[str, str]]) -> None:
        self.write(TEXT_DOCS_PROVENANCE_REGISTRY_YML, support.registry_text(entries))

    def test_complete_metadata_passes(self) -> None:
        self._registry([(KEY_COORDINATOR, TEXT_AGENTS_COORDINATOR_AGENT_MD)])
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, support.agent_text(KEY_COORDINATOR, mode=KEY_PRIMARY))
        self.write(TEXT_COMMANDS_REVIEW_MD, support.command_text(KEY_COORDINATOR))
        self.write(TEXT_SKILLS_DEMO_SKILL_MD, support.skill_text(KEY_DEMO))
        self.write(
            TEXT_CONFIGS_RALPH_HATS_DEMO_YML,
            "# Name: Demo\n# Purpose: Fixture.\n# Provenance\n# source: https://example.com\n"
            "# author: Fixture Author\n# author_url: https://example.com/author\n"
            "# upstream_commit: 0000000000000000000000000000000000000000\n"
            "# license: MIT\n",
        )
        self.validator.check_provenance()
        self.assertEqual(self.validator.errors, [])

    def test_missing_source_header_fails(self) -> None:
        self._registry([])
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_MISSING_PROVENANCE_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_EXAMPLE_AGENT_MD, fixture)
        self.validator.check_provenance()
        self.assert_error(TEXT_MISSING_PROVENANCE_HEADER)

    def test_missing_author_fails(self) -> None:
        self._registry([])
        self.write(
            TEXT_AGENTS_EXAMPLE_AGENT_MD,
            FLAG_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM_COMMIT_ABC_DESCRIPTION_X_B,
        )
        self.validator.check_provenance()
        self.assert_error(TEXT_MISSING_AUTHOR_ATTRIBUTION)

    def test_registry_points_to_missing_path_fails(self) -> None:
        self._registry([(KEY_GHOST, TEXT_AGENTS_GHOST_AGENT_MD)])
        self.validator.check_provenance()
        self.assert_error(TEXT_PROVENANCE_REGISTRY_POINTS_TO_MISSING_PATH)


class GitPermissionTests(ValidatorTestCase):

    def test_deny_last_passes(self) -> None:
        self.validator.AGENT_ROLES = [KEY_COORDINATOR]
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, support.agent_text(KEY_COORDINATOR, mode=KEY_PRIMARY))
        self.validator.check_git_permissions()
        self.assertEqual(self.validator.errors, [])

    def test_allow_last_fails(self) -> None:
        self.validator.AGENT_ROLES = [KEY_COORDINATOR]
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_GIT_ALLOW_LAST_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_COORDINATOR_AGENT_MD, fixture)
        self.validator.check_git_permissions()
        self.assert_error(TEXT_INSTEAD_OF_DENY)


class JsoncChecksTests(ValidatorTestCase):

    def test_header_only_comments_pass(self) -> None:
        self.write(
            TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC,
            "// Name: Fixture\n// Purpose: Fixture.\n// Usage: tests.\n// Validation: tests.\n"
            '// References: tests.\n{\n  "$schema": "https://opencode.ai/config.json",\n'
            '  "mcp": {"servers": {}}\n}\n',
        )
        self.validator.check_jsonc(self.root / TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC)
        self.assertEqual(self.validator.errors, [])

    def test_inline_body_comment_fails(self) -> None:
        source = (support.FIXTURES / KEY_CONFIG / TEXT_COMMENTED_BODY_JSONC).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC, source)
        self.validator.check_comment_policy()
        self.assert_error(TEXT_INLINE_JSONC_COMMENTS_ARE_PROHIBITED)

    def test_missing_servers_fails(self) -> None:
        source = (support.FIXTURES / KEY_CONFIG / TEXT_MISSING_SERVERS_JSONC).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC, source)
        self.validator.check_jsonc(self.root / TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC)
        self.assert_error(TEXT_V2_REQUIRES_MCP_SERVERS)

    def test_invalid_json_fails(self) -> None:
        self.write(TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC, TEXT_NOPE)
        self.validator.check_jsonc(self.root / TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC)
        self.assert_error(TEXT_INVALID_JSONC)


class YamlChecksTests(ValidatorTestCase):

    def test_valid_yaml_passes(self) -> None:
        self.write(TEXT_CONFIGS_RALPH_RALPH_YML, TEXT_NAME_FIXTURE_STEPS_1)
        self.validator.check_yaml(self.root / TEXT_CONFIGS_RALPH_RALPH_YML)
        self.assertEqual(self.validator.errors, [])

    def test_invalid_yaml_fails(self) -> None:
        self.write(TEXT_CONFIGS_RALPH_RALPH_YML, TEXT_KEY_UNTERMINATED)
        self.validator.check_yaml(self.root / TEXT_CONFIGS_RALPH_RALPH_YML)
        self.assertTrue(self.validator.errors or self.validator.warnings)


class CommentPolicyTests(ValidatorTestCase):

    def test_python_inline_comment_fails(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_PY, TEXT_MODULE_DOCSTRING_VALUE_1_EXPLAIN)
        self.validator.check_comment_policy()
        self.assert_error(TEXT_NON_DOCUMENTATION_PYTHON_COMMENT)

    def test_python_docstrings_only_pass(self) -> None:
        self.write(
            TEXT_SCRIPTS_DEMO_PY,
            TEXT_MODULE_DOCSTRING_DEF_RUN_INT_RETURN_ONE_RETURN_1,
        )
        self.validator.check_comment_policy()
        self.assertEqual(self.validator.errors, [])

    def test_shell_inline_comment_fails(self) -> None:
        self.write(
            TEXT_SCRIPTS_DEMO_SH,
            TEXT_USR_BIN_ENV_BASH_NAME_DEMO_PURPOSE_FIXTURE_SET_EU_ECHO_HI_NO,
        )
        self.validator.check_comment_policy()
        self.assert_error(TEXT_INLINE_SHELL_COMMENTS_ARE_PROHIBITED)

    def test_shell_full_line_comment_passes(self) -> None:
        self.write(
            TEXT_SCRIPTS_DEMO_SH,
            "#!/usr/bin/env bash\n# Name: Demo\n# Purpose: Fixture.\n# Usage: tests.\n"
            "# Arguments: none.\n# Environment: none.\n# Outputs: none.\n"
            "# Side effects: none.\n# References: tests.\nset -eu\necho hi\n",
        )
        self.validator.check_comment_policy()
        self.assertEqual(self.validator.errors, [])

    def test_missing_shell_header_fails(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_SH, TEXT_USR_BIN_ENV_BASH_ECHO_HI)
        self.validator.check_comment_policy()
        self.assert_error(TEXT_MISSING_SHELL_DOCUMENTATION_HEADER)

    def test_skill_shell_inline_comment_fails(self) -> None:
        self.write(
            TEXT_SKILLS_DEMO_FIND_SH,
            TEXT_USR_BIN_ENV_BASH_NAME_DEMO_PURPOSE_FIXTURE_SET_EU_ECHO_HI_NO,
        )
        self.validator.check_comment_policy()
        self.assert_error(TEXT_INLINE_SHELL_COMMENTS_ARE_PROHIBITED)

    def test_skill_python_inline_comment_fails(self) -> None:
        self.write(TEXT_SKILLS_DEMO_ASSET_PY, TEXT_MODULE_VALUE_1_NOTE)
        self.validator.check_comment_policy()
        self.assert_error(TEXT_NON_DOCUMENTATION_PYTHON_COMMENT)


class TaskChecksTests(ValidatorTestCase):

    def test_valid_task_passes(self) -> None:
        self.write(
            TEXT_BENCHMARKS_TASKS_DEMO_JSON,
            TEXT_ID_DEMO_PROMPT_X_VERIFICATION_TRUE_WORKING_DIRECTORY,
        )
        self.validator.check_tasks()
        self.assertEqual(self.validator.errors, [])

    def test_missing_field_fails(self) -> None:
        source = (support.FIXTURES / KEY_TASKS / TEXT_MISSING_FIELD_JSON).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_BENCHMARKS_TASKS_DEMO_JSON, source)
        self.validator.check_tasks()
        self.assert_error(TEXT_MISSING_OR_EMPTY_VERIFICATION)

    def test_missing_working_directory_fails(self) -> None:
        source = (support.FIXTURES / KEY_TASKS / TEXT_MISSING_WORKDIR_JSON).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_BENCHMARKS_TASKS_DEMO_JSON, source)
        self.validator.check_tasks()
        self.assert_error(TEXT_WORKING_DIRECTORY_DOES_NOT_EXIST)


class DocsStatusTests(ValidatorTestCase):

    def _page(self, status: str = TEXT_STABLE, date: str = TEXT_2026_11_12) -> str:
        return (
            TEXT_PAGE
            + TEXT_STATUS_BLOCK.format(status, date)
            + TEXT_BODY
        )

    def test_complete_status_block_passes(self) -> None:
        self.write(TEXT_DOCS_PAGE_MD, self._page())
        self.validator.check_docs_status()
        self.assertEqual(self.validator.errors, [])

    def test_missing_status_block_fails(self) -> None:
        self.write(TEXT_DOCS_PAGE_MD, TEXT_PAGE_BODY)
        self.validator.check_docs_status()
        self.assert_error(TEXT_MISSING_DOCUMENTATION_STATUS_FIELD)

    def test_unknown_status_fails(self) -> None:
        self.write(TEXT_DOCS_PAGE_MD, self._page(status=TEXT_MAYBE))
        self.validator.check_docs_status()
        self.assert_error(TEXT_UNKNOWN_DOCUMENTATION_STATUS)

    def test_non_iso_date_fails(self) -> None:
        self.write(TEXT_DOCS_PAGE_MD, self._page(date=TEXT_12_NOVEMBER_2026))
        self.validator.check_docs_status()
        self.assert_error(TEXT_LAST_VERIFIED_DATE_MUST_BE_ISO_8601)

    def test_decisions_are_exempt(self) -> None:
        self.write(TEXT_DOCS_DECISIONS_ADR_999_EXAMPLE_MD, TEXT_ADR_999_STATUS_ACCEPTED)
        self.validator.check_docs_status()
        self.assertEqual(self.validator.errors, [])


class MainCompositionTests(ValidatorTestCase):

    def _run_main(self) -> tuple[int, str]:
        original_argv = sys.argv
        sys.argv = [TEXT_VALIDATE_CONFIG_PY]
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                code = self.validator.main()
        finally:
            sys.argv = original_argv
        return code, buffer.getvalue()

    def test_main_fails_on_missing_docs_status(self) -> None:
        self.write(TEXT_DOCS_PAGE_MD, TEXT_PAGE_BODY)
        code, output = self._run_main()
        self.assertEqual(code, 1)
        self.assertIn(TEXT_MISSING_DOCUMENTATION_STATUS_FIELD, output)

    def test_main_fails_on_missing_provenance(self) -> None:
        fixture = (support.FIXTURES / KEY_AGENTS / TEXT_MISSING_PROVENANCE_MD).read_text(encoding=TEXT_UTF_8)
        self.write(TEXT_AGENTS_EXAMPLE_AGENT_MD, fixture)
        self.write(TEXT_DOCS_PROVENANCE_REGISTRY_YML, support.registry_text([]))
        code, output = self._run_main()
        self.assertEqual(code, 1)
        self.assertIn(TEXT_MISSING_PROVENANCE_HEADER, output)

    def test_main_fails_on_invalid_workflow_yaml(self) -> None:
        self.write(TEXT_GITHUB_WORKFLOWS_BAD_YML, TEXT_KEY_UNTERMINATED)
        code, output = self._run_main()
        if TEXT_NO_YAML_PARSER in output:
            self.skipTest(TEXT_NO_YAML_PARSER_AVAILABLE)
        self.assertEqual(code, 1)
        self.assertIn(TEXT_INVALID_YAML, output)


class SourceCommentTests(ValidatorTestCase):

    def test_typescript_jsdoc_passes(self) -> None:
        self.write(
            TEXT_EXAMPLES_DEMO_FILE_TS,
            TEXT_ADDS_TWO_NUMBERS_EXPORT_FUNCTION_ADD_A_NUMBER_B_NUMBER_NUMBE,
        )
        self.validator.check_source_comments()
        self.assertEqual(self.validator.errors, [])

    def test_typescript_line_comment_fails(self) -> None:
        self.write(TEXT_EXAMPLES_DEMO_FILE_TS, TEXT_NOTE_EXPORT_CONST_VALUE_1)
        self.validator.check_source_comments()
        self.assert_error(TEXT_LINE_COMMENTS_ARE_PROHIBITED)

    def test_typescript_trailing_comment_fails(self) -> None:
        self.write(TEXT_EXAMPLES_DEMO_FILE_TS, TEXT_EXPORT_CONST_VALUE_1_NOTE)
        self.validator.check_source_comments()
        self.assert_error(TEXT_LINE_COMMENTS_ARE_PROHIBITED)

    def test_typescript_url_in_string_passes(self) -> None:
        self.write(TEXT_EXAMPLES_DEMO_FILE_TS, TEXT_EXPORT_CONST_URL_HTTPS_EXAMPLE_COM)
        self.validator.check_source_comments()
        self.assertEqual(self.validator.errors, [])

    def test_csharp_xml_doc_passes(self) -> None:
        self.write(
            TEXT_EXAMPLES_DEMO_FILE_CS,
            TEXT_SUMMARY_ADDS_TWO_NUMBERS_SUMMARY_PUBLIC_STATIC_CLASS_MATHHEL,
        )
        self.validator.check_source_comments()
        self.assertEqual(self.validator.errors, [])

    def test_csharp_plain_comment_fails(self) -> None:
        self.write(TEXT_EXAMPLES_DEMO_FILE_CS, TEXT_NOTE_PUBLIC_STATIC_CLASS_MATHHELPERS)
        self.validator.check_source_comments()
        self.assert_error(TEXT_LINE_COMMENTS_ARE_PROHIBITED)


class DocstringFormTests(ValidatorTestCase):

    def test_block_form_passes(self) -> None:
        self.write(
            TEXT_SCRIPTS_DEMO_PY,
            TEXT_MODULE_DOCUMENTATION_CLASS_RUNNER_RUNS_WORK_DEF_RUN_SELF_INT,
        )
        self.validator.check_docstring_form()
        self.assertEqual(self.validator.errors, [])

    def test_single_line_docstring_fails(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_PY, TEXT_MODULE_DEF_RUN_INT_RETURN_ONE_RETURN_1)
        self.validator.check_docstring_form()
        self.assert_error(TEXT_MUST_PLACE_THE_TRIPLE_QUOTES_ON_THEIR_OWN_LINES)

    def test_single_line_function_docstring_fails(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_PY, TEXT_MODULE_DEF_RUN_INT_RETURN_ONE_RETURN_1_2)
        self.validator.check_docstring_form()
        self.assert_error(TEXT_MUST_PLACE_THE_TRIPLE_QUOTES_ON_THEIR_OWN_LINES)

    def test_function_docstring_is_optional(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_PY, TEXT_MODULE_DEF_RUN_INT_RETURN_1)
        self.validator.check_docstring_form()
        self.assertEqual(self.validator.errors, [])

    def test_test_fixtures_are_exempt(self) -> None:
        self.write(TEXT_TESTS_FIXTURES_BAD_PY, TEXT_ONE_LINE)
        self.validator.check_docstring_form()
        self.assertEqual(self.validator.errors, [])

    def test_missing_module_docstring_fails(self) -> None:
        self.write(TEXT_SCRIPTS_DEMO_PY, TEXT_FROM_FUTURE_IMPORT_ANNOTATIONS_DEF_RUN_INT_RETURN_ONE_RETURN)
        self.validator.check_docstring_form()
        self.assert_error(TEXT_MODULE_IS_MISSING_A_DOCSTRING)


class HelperTests(unittest.TestCase):

    def test_shell_inline_comment_ignores_shebang_and_quotes(self) -> None:
        validator = support.load_validator()
        self.assertFalse(validator.shell_inline_comment(TEXT_USR_BIN_ENV_BASH))
        self.assertFalse(validator.shell_inline_comment(TEXT_ECHO_NOT_A_COMMENT))
        self.assertTrue(validator.shell_inline_comment(TEXT_ECHO_HI_NOTE))
        self.assertFalse(validator.shell_inline_comment(TEXT_FULL_LINE))
        self.assertFalse(validator.shell_inline_comment(TEXT_ECHO_ARRAY))

    def test_jsonc_comment_lines_reports_line_numbers(self) -> None:
        validator = support.load_validator()
        text = TEXT_HEADER_A_NOT_A_COMMENT_BODY_B_1
        self.assertEqual(validator.jsonc_comment_lines(text), [1, 4])

    def test_python_sources_skips_build_output(self) -> None:
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            support.write_file(root, TEXT_PACKAGES_DEMO_PKG_MODULE_PY, TEXT_MODULE)
            support.write_file(root, TEXT_PACKAGES_DEMO_BUILD_MODULE_PY, TEXT_MODULE)
            support.write_file(root, TEXT_PACKAGES_DEMO_PKG_EGG_INFO_MODULE_PY, TEXT_MODULE)
            names = [path.relative_to(root).as_posix() for path in validator.python_sources(root / KEY_PACKAGES)]
            self.assertEqual(names, [TEXT_PACKAGES_DEMO_PKG_MODULE_PY])

    def test_package_inline_comment_is_rejected(self) -> None:
        validator = support.load_validator()
        with support.isolated_root(validator) as root:
            support.write_file(root, TEXT_PACKAGES_DEMO_MODULE_PY, TEXT_MODULE_VALUE_1_NOTE)
            validator.check_comment_policy()
            self.assertIn(TEXT_NON_DOCUMENTATION_PYTHON_COMMENT, TEXT_TEXT.join(validator.errors))


if __name__ == TEXT_MAIN:
    unittest.main()
