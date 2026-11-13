"""
String constants for updater.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_AVAILABLE_COMMIT
from .constants import KEY_CURRENT_COMMIT
from .constants import KEY_FILES_CHANGED
from .constants import KEY_LOCKED_COMMIT
from .constants import TEXT_NO_LOCK
from .constants import TEXT_UPDATE_AVAILABLE

from .constants import (
    DEFAULT_COMMIT,
    EMPTY_STRING,
    KEY_COMMIT,
    KEY_CURRENT,
    KEY_LOCK,
    KEY_MESSAGE,
    KEY_REPOSITORY,
    KEY_SOURCE,
    KEY_STATUS,
    STATUS_MODIFIED,
)





KEY_REMOTE_CHECKED = 'remote_checked'

TEXT_COULD_NOT_READ_THE_REMOTE_HEAD_CHECK_NETWORK_ACCESS = 'could not read the remote HEAD; check network access'

TEXT_MANAGED_FILE_S_DIFFER_FROM_THE_LOCK = '{} managed file(s) differ from the lock'


TEXT_NO_LOCK_FILE_AT_RUN_TOOLWRIGHT_INSTALL_APPLY_FIRST = "no lock file at {}; run 'toolwright install --apply' first"

TEXT_REMOTE_HEAD_IS_LOCK_IS = 'remote HEAD is {}, lock is {}'

TEXT_SOURCE_ADVANCED_FROM_TO = 'source advanced from {} to {}'


TEXT_UP_TO_DATE = 'up to date'
