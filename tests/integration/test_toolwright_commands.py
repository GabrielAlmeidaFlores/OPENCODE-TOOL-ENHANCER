"""
Integration tests for the ``toolwright`` command line.

The tests execute the real CLI as a subprocess against temporary targets. They
require no network access and never write inside the repository.
"""
from __future__ import annotations
from tests.constants import TEXT_OPENCODE
from tests.integration.test_toolwright_commands_strings import (
    FLAG_APPLY,
    FLAG_BUDGET,
    FLAG_CHECK,
    FLAG_CONFIG,
    FLAG_DRY_RUN,
    FLAG_FORCE,
    FLAG_FORMAT,
    FLAG_HELP,
    FLAG_JSON,
    FLAG_NO_MCP,
    FLAG_ONLY,
    FLAG_PROFILE,
    FLAG_PLATFORM,
    KEY_CLAUDE,
    KEY_CODEX,
    KEY_COPILOT,
    TEXT_AGENTS_MD,
    TEXT_CLAUDE_AGENTS_COORDINATOR_MD,
    TEXT_CLAUDE_MD,
    TEXT_CODEX_AGENTS_COORDINATOR,
    TEXT_COPILOT_AGENTS_COORDINATOR,
    TEXT_COPILOT_INSTRUCTIONS,
    FLAG_RECORD,
    FLAG_RESULTS,
    FLAG_RISK,
    FLAG_TARGET,
    FLAG_TYPE,
    FLAG_YES,
    KEY_A,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_AGENT,
    KEY_ALLOWED,
    KEY_ARM,
    KEY_BASELINE,
    KEY_CATALOG,
    KEY_CHECK,
    KEY_CHECKS,
    KEY_COMMIT,
    KEY_COMPAT,
    KEY_COMPONENT,
    KEY_COMPONENTS,
    KEY_CONTRACTS,
    KEY_COORDINATOR,
    KEY_COST,
    KEY_DECISION,
    KEY_DIGEST,
    KEY_DOCTOR,
    KEY_ENTRIES,
    KEY_EVAL,
    KEY_EXPORT,
    KEY_FAIL,
    KEY_FAILED,
    KEY_FEATURES,
    KEY_FILES,
    KEY_FULL,
    KEY_GATE,
    KEY_GENERATOR,
    KEY_GIT,
    KEY_GOVERN,
    KEY_HIGH,
    KEY_HONO,
    KEY_ID,
    KEY_INPUT,
    KEY_INSTALL,
    KEY_ITERATIONS,
    KEY_JSON,
    KEY_LIST,
    KEY_MEMORY,
    KEY_MINIMAL,
    KEY_MODEL,
    KEY_MODIFIED,
    KEY_NAME,
    KEY_OK,
    KEY_OPENCODE,
    KEY_OUTPUT,
    KEY_PART,
    KEY_PASS,
    KEY_PATH,
    KEY_PILOT,
    KEY_PREAMBLE,
    KEY_PROFILE,
    KEY_PROFILES,
    KEY_PROJECT,
    KEY_PYTHON,
    KEY_REPOSITORY,
    KEY_REQUIRED,
    KEY_REVIEW,
    KEY_ROLLBACK,
    KEY_RUN,
    KEY_RUN_ID,
    KEY_SCHEMA_VERSION,
    KEY_SEARCH,
    KEY_SECURITY,
    KEY_SHA256,
    KEY_SHOW,
    KEY_SOURCE,
    KEY_SPEC,
    KEY_STANDARD,
    KEY_STATS,
    KEY_STATUS,
    KEY_STEP_FINISH,
    KEY_SUMMARY,
    KEY_TASK,
    KEY_TASKS,
    KEY_TASK_ID,
    KEY_TOKENS,
    KEY_TOOL,
    KEY_TOOLWRIGHT_CLI,
    KEY_TOTALS,
    KEY_TYPE,
    KEY_UNINSTALL,
    KEY_UPDATE,
    KEY_USE,
    KEY_VALIDATOR,
    KEY_VERIFICATION_EXIT,
    KEY_VERIFY,
    TEXT_0,
    TEXT_0_1,
    TEXT_0_FAILURE_S,
    TEXT_100,
    TEXT_ALREADY_UP_TO_DATE,
    TEXT_AST_GREP,
    TEXT_BUDGET_EXCEEDED,
    TEXT_CHECKOUT_DETACH,
    TEXT_CONFIG_TOML,
    TEXT_EXPECTED_A_CLI_BACKUP_DIRECTORY,
    TEXT_GLOBAL_CONFIG_TAR_GZ,
    TEXT_HEAD,
    TEXT_M,
    TEXT_MAIN,
    TEXT_META_JSON,
    TEXT_NO_BACKUPS,
    TEXT_OK,
    TEXT_OPENCODE_AGENTS_COORDINATOR_MD,
    TEXT_OPENCODE_BINARY_IS_NOT_INSTALLED,
    TEXT_OPENCODE_COPY,
    TEXT_PLAN_ONLY,
    TEXT_PROJECT_MEMORY,
    TEXT_PROJECT_OPENCODE_TAR_GZ,
    TEXT_PROVIDER_MODEL,
    TEXT_PYTHONPATH,
    TEXT_RECORD_JSON,
    TEXT_REMOVE_OPENCODE_AGENTS_COORDINATOR_MD,
    TEXT_REV_PARSE,
    TEXT_SESSION_JSONL,
    TEXT_SPEC_S,
    TEXT_SUMMARY,
    TEXT_TAMPERED,
    TEXT_TAR_GZ,
    TEXT_TEXT,
    TEXT_TOOLWRIGHT_BACKUPS,
    TEXT_TOOLWRIGHT_CLI,
    TEXT_TOOLWRIGHT_LOCK_JSON,
    TEXT_TOOLWRIGHT_STATE_JSON,
    TEXT_UTF_8,
)

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

REPO_ROOT = support.REPO_ROOT


def run_ote(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment[TEXT_PYTHONPATH] = str(support.CLI_PACKAGE)
    return subprocess.run(
        [sys.executable, TEXT_M, KEY_TOOLWRIGHT_CLI, *args],
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        env=environment,
    )


class DoctorCommandTests(unittest.TestCase):

    @unittest.skipUnless(shutil.which(KEY_OPENCODE), TEXT_OPENCODE_BINARY_IS_NOT_INSTALLED)
    def test_doctor_json_reports_no_failures(self) -> None:
        result = run_ote(KEY_DOCTOR, FLAG_JSON, FLAG_NO_MCP)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(KEY_CHECKS, payload)
        self.assertEqual(payload[KEY_SUMMARY][KEY_FAIL], 0)
        identifiers = {check[KEY_ID] for check in payload[KEY_CHECKS]}
        self.assertTrue({KEY_PYTHON, KEY_REPOSITORY, KEY_OPENCODE, KEY_VALIDATOR}.issubset(identifiers))

    def test_doctor_text_mode_lists_checks(self) -> None:
        result = run_ote(KEY_DOCTOR, FLAG_NO_MCP)
        self.assertIn(KEY_PYTHON, result.stdout)
        self.assertIn(TEXT_SUMMARY, result.stdout)


class InstallLifecycleTests(unittest.TestCase):

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_CLI)
        self.addCleanup(self.directory.cleanup)
        self.target = Path(self.directory.name) / KEY_PROJECT

    def test_dry_run_writes_nothing(self) -> None:
        result = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_DRY_RUN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_PLAN_ONLY, result.stdout)
        self.assertIn(TEXT_OPENCODE_AGENTS_COORDINATOR_MD, result.stdout)
        self.assertFalse(self.target.exists())

    def test_apply_creates_lock_and_state(self) -> None:
        result = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / TEXT_OPENCODE_AGENTS_COORDINATOR_MD).is_file())
        lock = json.loads((self.target / TEXT_TOOLWRIGHT_LOCK_JSON).read_text(encoding=TEXT_UTF_8))
        self.assertEqual(lock[KEY_SCHEMA_VERSION], 2)
        self.assertEqual(lock[KEY_ADAPTERS][0][KEY_NAME], KEY_OPENCODE)
        self.assertEqual(lock[KEY_ADAPTERS][0][KEY_PROFILE], KEY_MINIMAL)
        self.assertTrue(lock[KEY_FILES])
        for entry in lock[KEY_FILES]:
            path = self.target / entry[KEY_PATH]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, entry[KEY_SHA256], entry[KEY_PATH])
            self.assertEqual(entry[KEY_ADAPTER], KEY_OPENCODE)
            self.assertEqual(entry[KEY_GENERATOR], TEXT_OPENCODE_COPY)
        self.assertTrue((self.target / TEXT_TOOLWRIGHT_STATE_JSON).is_file())

    def test_reapply_upgrades_v1_lock_to_v2(self) -> None:
        result = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lock_path = self.target / TEXT_TOOLWRIGHT_LOCK_JSON
        lock = json.loads(lock_path.read_text(encoding=TEXT_UTF_8))
        adapter = lock[KEY_ADAPTERS][0]
        v1 = {
            KEY_SCHEMA_VERSION: 1,
            KEY_PROFILE: adapter[KEY_PROFILE],
            KEY_COMPONENTS: adapter[KEY_COMPONENTS],
            KEY_SOURCE: lock[KEY_SOURCE],
            KEY_FILES: [
                {
                    KEY_PATH: entry[KEY_PATH],
                    KEY_SOURCE: entry[KEY_SOURCE],
                    KEY_COMPONENT: entry[KEY_COMPONENT],
                    KEY_SHA256: entry[KEY_SHA256],
                }
                for entry in lock[KEY_FILES]
            ],
        }
        lock_path.write_text(json.dumps(v1), encoding=TEXT_UTF_8)
        upgraded = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
        stored = json.loads(lock_path.read_text(encoding=TEXT_UTF_8))
        self.assertEqual(stored[KEY_SCHEMA_VERSION], 2)
        self.assertEqual(stored[KEY_ADAPTERS][0][KEY_NAME], KEY_OPENCODE)
        self.assertIn(KEY_DIGEST, stored[KEY_ADAPTERS][0])

    def test_reapply_is_idempotent(self) -> None:
        first = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(first.returncode, 0, first.stderr)
        lock_path = self.target / TEXT_TOOLWRIGHT_LOCK_JSON
        before = lock_path.read_bytes()
        second = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(TEXT_ALREADY_UP_TO_DATE, second.stdout)
        self.assertEqual(lock_path.read_bytes(), before)

    def test_force_creates_backup(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        result = run_ote(
            KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY, FLAG_FORCE
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.target / TEXT_TOOLWRIGHT_BACKUPS).iterdir())
        self.assertTrue(backups, TEXT_EXPECTED_A_CLI_BACKUP_DIRECTORY)
        archives = {archive.name for backup in backups for archive in backup.glob(TEXT_TAR_GZ)}
        self.assertIn(TEXT_PROJECT_OPENCODE_TAR_GZ, archives)
        self.assertNotIn(TEXT_GLOBAL_CONFIG_TAR_GZ, archives)

    def test_reapply_refreshes_stale_source_commit(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        lock_path = self.target / TEXT_TOOLWRIGHT_LOCK_JSON
        lock = json.loads(lock_path.read_text(encoding=TEXT_UTF_8))
        lock[KEY_SOURCE][KEY_COMMIT] = TEXT_0 * 40
        lock_path.write_text(json.dumps(lock, indent=2), encoding=TEXT_UTF_8)
        applied = run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        refreshed = json.loads(lock_path.read_text(encoding=TEXT_UTF_8))
        head = subprocess.run(
            [KEY_GIT, TEXT_REV_PARSE, TEXT_HEAD],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(refreshed[KEY_SOURCE][KEY_COMMIT], head)
        update = run_ote(KEY_UPDATE, FLAG_TARGET, str(self.target), FLAG_CHECK)
        self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

    def test_update_detects_modified_file(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        clean = run_ote(KEY_UPDATE, FLAG_TARGET, str(self.target), FLAG_CHECK)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        with (self.target / TEXT_OPENCODE_AGENTS_COORDINATOR_MD).open(KEY_A, encoding=TEXT_UTF_8) as handle:
            handle.write(TEXT_TAMPERED)
        dirty = run_ote(KEY_UPDATE, FLAG_TARGET, str(self.target), FLAG_CHECK)
        self.assertEqual(dirty.returncode, 1, dirty.stdout + dirty.stderr)
        self.assertIn(KEY_MODIFIED, dirty.stdout)

    def test_uninstall_requires_confirmation(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        result = run_ote(KEY_UNINSTALL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        self.assertEqual(result.returncode, 2)
        self.assertIn(FLAG_YES, result.stderr)

    def test_uninstall_plan_keeps_files(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        result = run_ote(KEY_UNINSTALL, FLAG_TARGET, str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TEXT_REMOVE_OPENCODE_AGENTS_COORDINATOR_MD, result.stdout)
        self.assertTrue((self.target / TEXT_OPENCODE_AGENTS_COORDINATOR_MD).is_file())

    def test_uninstall_apply_removes_managed_files(self) -> None:
        run_ote(KEY_INSTALL, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)
        result = run_ote(KEY_UNINSTALL, FLAG_TARGET, str(self.target), FLAG_APPLY, FLAG_YES)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.target / TEXT_OPENCODE_AGENTS_COORDINATOR_MD).exists())
        self.assertTrue((self.target / TEXT_TOOLWRIGHT_LOCK_JSON).is_file())


class ProfileAndCatalogTests(unittest.TestCase):

    def test_profile_list(self) -> None:
        result = run_ote(KEY_PROFILE, KEY_LIST)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in (KEY_MINIMAL, KEY_STANDARD, KEY_FULL):
            self.assertIn(name, result.stdout)

    def test_profile_show(self) -> None:
        result = run_ote(KEY_PROFILE, KEY_SHOW, KEY_STANDARD)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TEXT_AST_GREP, result.stdout)

    def test_profile_verify(self) -> None:
        result = run_ote(KEY_PROFILE, KEY_VERIFY)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_OK, result.stdout)

    def test_profile_use_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / KEY_PROJECT
            result = run_ote(KEY_PROFILE, KEY_USE, KEY_MINIMAL, FLAG_TARGET, str(target), FLAG_DRY_RUN)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(TEXT_PLAN_ONLY, result.stdout)
            self.assertFalse(target.exists())

    def test_catalog_list_and_search(self) -> None:
        listed = run_ote(KEY_CATALOG, KEY_LIST, FLAG_TYPE, KEY_AGENT)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn(KEY_COORDINATOR, listed.stdout)
        found = run_ote(KEY_CATALOG, KEY_SEARCH, KEY_SECURITY)
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertIn(KEY_SECURITY, found.stdout)

    def test_catalog_verify(self) -> None:
        result = run_ote(KEY_CATALOG, KEY_VERIFY)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_0_FAILURE_S, result.stdout)

    def test_compat_json(self) -> None:
        result = run_ote(KEY_COMPAT, FLAG_JSON)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload[KEY_TOOL], KEY_OPENCODE)
        self.assertTrue(payload[KEY_FEATURES])


class VerificationCommandTests(unittest.TestCase):

    def _config(self, directory: str) -> Path:
        path = Path(directory) / TEXT_CONFIG_TOML
        path.write_text(
            '[verify]\ntimeout = 10\n'
            '[verify.checks.ok]\ncommand = "true"\n'
            '[verify.checks.fail]\ncommand = "sh -c \'exit 3\'"\n',
            encoding=TEXT_UTF_8,
        )
        return path

    def test_verify_pass_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = self._config(directory)
            passed = run_ote(KEY_VERIFY, FLAG_CONFIG, str(config), FLAG_ONLY, KEY_OK, FLAG_JSON)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertEqual(json.loads(passed.stdout)[KEY_SUMMARY][KEY_STATUS], KEY_PASS)
            failed = run_ote(KEY_VERIFY, FLAG_CONFIG, str(config), FLAG_ONLY, KEY_FAIL, FLAG_JSON)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(failed.stdout)[KEY_SUMMARY][KEY_FAILED], 1)

    def test_govern_contracts(self) -> None:
        result = run_ote(KEY_GOVERN, KEY_CONTRACTS)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(KEY_COORDINATOR, result.stdout)
        self.assertIn(TEXT_0_FAILURE_S, result.stdout)

    def test_govern_gate(self) -> None:
        result = run_ote(KEY_GOVERN, KEY_GATE, FLAG_RISK, KEY_HIGH, FLAG_JSON)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[KEY_REQUIRED], [KEY_VERIFY, KEY_REVIEW, KEY_SECURITY])

    def test_govern_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / TEXT_RECORD_JSON
            record.write_text(json.dumps({KEY_ITERATIONS: 999}), encoding=TEXT_UTF_8)
            result = run_ote(KEY_GOVERN, KEY_CHECK, FLAG_RECORD, str(record), FLAG_JSON)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)[KEY_ALLOWED])


class PhaseSixCommandTests(unittest.TestCase):

    def _run(self, root: Path, name: str, cost: float) -> None:
        run = root / name
        run.mkdir(parents=True)
        (run / TEXT_META_JSON).write_text(
            json.dumps(
                {
                    KEY_RUN_ID: name,
                    KEY_ARM: KEY_BASELINE,
                    KEY_TASK_ID: KEY_TASK,
                    KEY_MODEL: TEXT_PROVIDER_MODEL,
                    KEY_AGENT: KEY_COORDINATOR,
                    KEY_VERIFICATION_EXIT: 0,
                }
            ),
            encoding=TEXT_UTF_8,
        )
        (run / TEXT_SESSION_JSONL).write_text(
            json.dumps(
                {
                    KEY_TYPE: KEY_STEP_FINISH,
                    KEY_PART: {KEY_COST: cost, KEY_TOKENS: {KEY_INPUT: 10, KEY_OUTPUT: 5}},
                }
            )
            + TEXT_TEXT,
            encoding=TEXT_UTF_8,
        )

    def test_stats_json_and_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._run(root, KEY_RUN, 0.5)
            result = run_ote(KEY_STATS, FLAG_RESULTS, str(root), FLAG_FORMAT, KEY_JSON)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertAlmostEqual(json.loads(result.stdout)[KEY_TOTALS][KEY_COST], 0.5)
            over = run_ote(KEY_STATS, FLAG_RESULTS, str(root), FLAG_FORMAT, KEY_JSON, FLAG_BUDGET, TEXT_0_1)
            self.assertEqual(over.returncode, 1)
            self.assertIn(TEXT_BUDGET_EXCEEDED, over.stderr)

    def test_eval_profiles(self) -> None:
        result = run_ote(KEY_EVAL, FLAG_ONLY, KEY_PROFILES)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(TEXT_OK, result.stdout)

    def test_pilot_list_and_dry_run(self) -> None:
        listed = run_ote(KEY_PILOT, KEY_LIST)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn(KEY_HONO, listed.stdout)
        planned = run_ote(KEY_PILOT, KEY_RUN, KEY_HONO, FLAG_DRY_RUN)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertIn(TEXT_CHECKOUT_DETACH, planned.stdout)


class MemoryAndSpecReadTests(unittest.TestCase):

    def test_memory_search_and_export(self) -> None:
        search = run_ote(KEY_MEMORY, KEY_SEARCH, KEY_DECISION)
        self.assertEqual(search.returncode, 0, search.stderr)
        exported = run_ote(KEY_MEMORY, KEY_EXPORT, FLAG_FORMAT, KEY_JSON)
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertIn(KEY_ENTRIES, json.loads(exported.stdout))

    def test_memory_preamble(self) -> None:
        result = run_ote(KEY_MEMORY, KEY_PREAMBLE, FLAG_BUDGET, TEXT_100)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TEXT_PROJECT_MEMORY, result.stdout)

    def test_task_list_json(self) -> None:
        result = run_ote(KEY_TASK, KEY_LIST, FLAG_JSON)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(KEY_TASKS, json.loads(result.stdout))

    def test_spec_list(self) -> None:
        result = run_ote(KEY_SPEC, KEY_LIST)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(TEXT_SPEC_S, result.stdout)


class PlatformAdapterInstallTests(unittest.TestCase):

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_CLI)
        self.addCleanup(self.directory.cleanup)
        self.target = Path(self.directory.name) / KEY_PROJECT

    def _install(self, platform: str) -> subprocess.CompletedProcess[str]:
        return run_ote(KEY_INSTALL, FLAG_PLATFORM, platform, FLAG_PROFILE, KEY_MINIMAL, FLAG_TARGET, str(self.target), FLAG_APPLY)

    def test_claude_adapter_installs_without_opencode(self) -> None:
        result = self._install(KEY_CLAUDE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / TEXT_CLAUDE_AGENTS_COORDINATOR_MD).is_file())
        self.assertTrue((self.target / TEXT_CLAUDE_MD).is_file())
        self.assertFalse((self.target / TEXT_OPENCODE).exists())

    def test_copilot_adapter_installs_without_opencode(self) -> None:
        result = self._install(KEY_COPILOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / TEXT_COPILOT_INSTRUCTIONS).is_file())
        self.assertTrue((self.target / TEXT_COPILOT_AGENTS_COORDINATOR).is_file())
        self.assertTrue((self.target / TEXT_AGENTS_MD).is_file())
        self.assertFalse((self.target / TEXT_OPENCODE).exists())

    def test_codex_adapter_installs_without_opencode(self) -> None:
        result = self._install(KEY_CODEX)
        self.assertEqual(result.returncode, 0, stdout := result.stdout + result.stderr)
        self.assertTrue((self.target / TEXT_CODEX_AGENTS_COORDINATOR).is_file())
        self.assertTrue((self.target / TEXT_AGENTS_MD).is_file())
        self.assertFalse((self.target / TEXT_OPENCODE).exists())

    def test_uninstall_removes_shared_files_across_adapters(self) -> None:
        self.assertEqual(self._install(KEY_COPILOT).returncode, 0)
        self.assertEqual(self._install(KEY_CODEX).returncode, 0)
        result = run_ote(
            KEY_UNINSTALL, FLAG_TARGET, str(self.target), FLAG_APPLY, FLAG_YES
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.target / TEXT_AGENTS_MD).exists())
        lock = json.loads(
            (self.target / TEXT_TOOLWRIGHT_LOCK_JSON).read_text(encoding=TEXT_UTF_8)
        )
        self.assertEqual(lock[KEY_FILES], [])
        self.assertEqual(lock[KEY_ADAPTERS], [])

    def test_uninstall_prunes_entries_for_missing_files(self) -> None:
        self.assertEqual(self._install(KEY_COPILOT).returncode, 0)
        (self.target / TEXT_AGENTS_MD).unlink()
        result = run_ote(
            KEY_UNINSTALL, FLAG_TARGET, str(self.target), FLAG_APPLY, FLAG_YES
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lock = json.loads(
            (self.target / TEXT_TOOLWRIGHT_LOCK_JSON).read_text(encoding=TEXT_UTF_8)
        )
        self.assertNotIn(TEXT_AGENTS_MD, [entry[KEY_PATH] for entry in lock[KEY_FILES]])


class CommandSurfaceTests(unittest.TestCase):

    def test_rollback_without_backups(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_ote(KEY_ROLLBACK, FLAG_TARGET, directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(TEXT_NO_BACKUPS, result.stdout)

    def test_help_lists_commands(self) -> None:
        result = run_ote(FLAG_HELP)
        self.assertEqual(result.returncode, 0)
        for command in (KEY_DOCTOR, KEY_INSTALL, KEY_UNINSTALL, KEY_UPDATE, KEY_ROLLBACK, KEY_CATALOG):
            self.assertIn(command, result.stdout)


if __name__ == TEXT_MAIN:
    unittest.main()
