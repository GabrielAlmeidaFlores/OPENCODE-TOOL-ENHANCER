"""
Shared CLI strings.

Public API: module constants used by :mod:`toolwright_cli.cli`.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_ADD as COMMAND_ADD
from .constants import KEY_CHECK as COMMAND_CHECK
from .constants import KEY_CONTRACTS as COMMAND_CONTRACTS
from .constants import KEY_JSON as FORMAT_JSON
from .constants import KEY_LIST as COMMAND_LIST
from .constants import KEY_MARKDOWN as FORMAT_MARKDOWN
from .constants import KEY_PILOT as COMMAND_PILOT
from .constants import KEY_VERIFY as COMMAND_VERIFY
from .constants import KEY_WORKTREE as COMMAND_WORKTREE
from .constants import OPERATION_INSTALL as COMMAND_INSTALL
from .constants import OPERATION_UNINSTALL as COMMAND_UNINSTALL
from .constants import PAREN_CLOSE
from .constants import STATUS_NEW as COMMAND_NEW
from .constants import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    NEWLINE,
    STATUS_FAIL,
    STATUS_MISSING,
    STATUS_MODIFIED,
    STATUS_NEW,
    STATUS_OK,
    STATUS_UNCHANGED,
    STATUS_UPDATED,
    STATUS_WARN,
    OPERATION_INSTALL,
    OPERATION_UNINSTALL,
    FLAG_APPLY,
    FLAG_CLEAN,
    FLAG_DRY_RUN,
    FLAG_FORCE,
    FLAG_ONLY,
    FLAG_PROFILE,
    FLAG_TARGET,
    FLAG_TYPE,
    FLAG_YES,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_APPLIED,
    KEY_ARCHIVES,
    KEY_ARTIFACTS,
    KEY_BACKUP,
    KEY_COMMIT,
    KEY_COMPONENT,
    KEY_COMPONENTS,
    KEY_CREATED,
    KEY_CURRENT,
    KEY_DETAIL,
    KEY_DIGEST,
    KEY_DIRTY,
    KEY_FAILURES,
    KEY_FEATURE,
    KEY_FILES,
    KEY_GENERATOR,
    KEY_ID,
    KEY_LAST_OPERATION,
    KEY_LOCK,
    KEY_MESSAGE,
    KEY_NAME,
    KEY_OUTPUT,
    KEY_PATH,
    KEY_PLANNED,
    KEY_PROFILE,
    KEY_PURGED,
    KEY_REMOVABLE,
    KEY_REPOSITORY,
    KEY_RESULTS,
    KEY_SCHEMA_VERSION,
    KEY_SHA256,
    KEY_SKIPPED,
    KEY_SOURCE,
    KEY_STATUS,
    KEY_SUMMARY,
    KEY_TARGET,
    KEY_TITLE,
    KEY_TYPE,
    KEY_UPDATED,
    KEY_VERSION,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
)

ARG_APPEND = "append"
ARG_STORE_TRUE = "store_true"
COMMAND_DOCTOR = "doctor"
COMMAND_ROLLBACK = "rollback"
COMMAND_SEARCH = "search"
COMMAND_SHOW = "show"
COMMAND_UPDATE = "update"
FORMAT_FLOAT_6 = ".6f"
FORMAT_WIDTH_4 = "<4"
FORMAT_WIDTH_8 = "<8"
FORMAT_WIDTH_10 = "<10"
FORMAT_WIDTH_12 = "<12"
FORMAT_WIDTH_22 = "<22"
INDENT_TWO = "  "
MESSAGE_FAILURE_SUFFIX = " failure(s)"
PAREN_OPEN = " ("
