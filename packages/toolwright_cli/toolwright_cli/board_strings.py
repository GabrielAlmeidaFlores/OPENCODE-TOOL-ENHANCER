"""
String constants for board.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_ADD
from .constants import KEY_WORKTREE
from .constants import TEXT_MD_2
from .constants import TEXT_TEXT as TEXT_TEXT_5
from .constants import TEXT_TEXT_2
from .constants import TEXT_TEXT_2_2 as TEXT_TEXT_3
from .constants import TEXT_TEXT_6
from .constants import TRUE_VALUE as KEY_TRUE
from .constants import FLAG_TEXT
from .constants import KEY_APPROVED
from .constants import KEY_BY_STATUS
from .constants import KEY_GIT
from .constants import KEY_REVIEW
from .constants import KEY_TASKS
from .constants import KEY_VERIFY
from .constants import KEY_WIP_LIMIT
from .constants import TEXT_C
from .constants import TEXT_INVALID_TOML
from .constants import TEXT_MD
from .constants import TEXT_MISSING
from .constants import TEXT_MISSING_FRONTMATTER
from .constants import TEXT_TOOLWRIGHT_CONFIG_TOML
from .constants import TEXT_UNTERMINATED_FRONTMATTER

from .constants import (
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_FORCE,
    KEY_CREATED,
    KEY_ID,
    KEY_STATUS,
    KEY_TITLE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
)

FLAG_ID_TITLE_STATUS_CREATED_WORKTREE_VERIFY_APPROVED_NOTES_GO_HE = '---\nid: {}\ntitle: {}\nstatus: {}\ncreated: {}\nworktree: {}\nverify: {}\napproved: {}\n---\n\nNotes go here. Board state is the frontmatter; prose is free form.\n'




KEY_BACKLOG = 'backlog'

KEY_BOARD = 'board'


KEY_DONE = 'done'


KEY_READY = 'ready'

KEY_REMOVE = 'remove'







TEXT_B = '-b'

TEXT_BOARD_MUST_BE_A_TABLE = '{}: board must be a table'

TEXT_BOARD_WIP_LIMIT_MUST_BE_A_POSITIVE_INTEGER = '{}: board.wip_limit must be a positive integer'


TEXT_GIT_WORKTREE_ADD_FAILED = 'git worktree add failed: {}'

TEXT_GIT_WORKTREE_REMOVE_FAILED = 'git worktree remove failed: {}'

TEXT_ID_TITLE_STATUS_WORKTREE_VERIFY = '| ID | Title | Status | Worktree | Verify |'


TEXT_IN_PROGRESS = 'in-progress'





TEXT_MOVING_A_TASK_TO_DONE_REQUIRES_APPROVED = 'moving a task to done requires --approved'

TEXT_T = 'T-'

TEXT_TASK = 'task/{}'

TEXT_TASK_ALREADY_HAS_A_WORKTREE = 'task already has a worktree: {}'

TEXT_TASK_BOARD = '# Task Board'

TEXT_TASK_HAS_NO_WORKTREE = 'task has no worktree: {}'

TEXT_TASK_TITLE_IS_REQUIRED = 'task title is required'

TEXT_TASK_TITLE_MUST_BE_A_SINGLE_LINE = 'task title must be a single line'

TEXT_TEXT = '| {} | {} | {} | {} | {} |'



TEXT_TEXT_4 = '| --- | --- | --- | --- | --- |'



TEXT_TOOLWRIGHT_BOARD_BOARD_MD = '.toolwright/board/BOARD.md'

TEXT_TOOLWRIGHT_BOARD_TASKS = '.toolwright/board/tasks'


TEXT_TOOLWRIGHT_WORKTREES = '.toolwright/worktrees'

TEXT_T_03D = 'T-{:03d}'

TEXT_UNKNOWN_STATUS = '{}: unknown status {}'

TEXT_UNKNOWN_STATUS_2 = 'unknown status: {}'

TEXT_UNKNOWN_TASK = 'unknown task: {}'


TEXT_VERIFICATION_COMMAND_MUST_BE_A_SINGLE_LINE = 'verification command must be a single line'

TEXT_WIP = 'WIP: {}/{}'

TEXT_WIP_LIMIT_REACHED = 'WIP limit reached: {}/{}'
