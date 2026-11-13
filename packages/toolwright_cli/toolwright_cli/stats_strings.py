"""
String constants for stats.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import TEXT_TEXT_3_3 as TEXT_TEXT_3
from .constants import TEXT_TEXT_7 as TEXT_TEXT
from .constants import KEY_AGENT
from .constants import KEY_COST
from .constants import KEY_INPUT_TOKENS
from .constants import KEY_MODEL
from .constants import KEY_OUTPUT_TOKENS
from .constants import KEY_STATE
from .constants import KEY_STEPS
from .constants import KEY_TASK
from .constants import KEY_TOOL
from .constants import KEY_TOOL_CALLS
from .constants import KEY_TOOL_ERRORS
from .constants import KEY_VERIFICATION_EXIT
from .constants import KEY_WALL_TIME_SECONDS
from .constants import TEXT_INVALID_JSON
from .constants import TEXT_META_JSON
from .constants import TEXT_SESSION_JSONL

from .constants import (
    DEFAULT_COMMIT,
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_NAME,
    KEY_OUTPUT,
    KEY_STATUS,
    KEY_TYPE,
    NEWLINE,
)


KEY_ARM = 'arm'

KEY_BASELINE = 'baseline'

KEY_BASELINE_COST = 'baseline_cost'

KEY_BASELINE_PASS_RATE = 'baseline_pass_rate'

KEY_BASELINE_RUNS = 'baseline_runs'

KEY_BASELINE_TOKENS = 'baseline_tokens'

KEY_BY_AGENT = 'by_agent'

KEY_BY_MODEL = 'by_model'

KEY_CACHE = 'cache'

KEY_CACHE_READ_TOKENS = 'cache_read_tokens'

KEY_CACHE_WRITE_TOKENS = 'cache_write_tokens'

KEY_COMPARISON = 'comparison'


KEY_COST_RATIO = 'cost_ratio'

KEY_ERROR = 'error'

KEY_IGNORE = 'ignore'

KEY_INPUT = 'input'



KEY_OPTIMIZED = 'optimized'

KEY_OPTIMIZED_COST = 'optimized_cost'

KEY_OPTIMIZED_PASS_RATE = 'optimized_pass_rate'

KEY_OPTIMIZED_RUNS = 'optimized_runs'

KEY_OPTIMIZED_TOKENS = 'optimized_tokens'


KEY_PART = 'part'

KEY_READ = 'read'

KEY_REASONING = 'reasoning'

KEY_REASONING_TOKENS = 'reasoning_tokens'

KEY_RUNS = 'runs'

KEY_RUN_ID = 'run_id'



KEY_STEP_FINISH = 'step_finish'


KEY_TASK_ID = 'task_id'

KEY_TOKENS = 'tokens'

KEY_TOKEN_RATIO = 'token_ratio'



KEY_TOOL_COUNTS = 'tool_counts'

KEY_TOOL_ERROR = 'tool_error'


KEY_TOOL_USE = 'tool_use'

KEY_TOTALS = 'totals'


KEY_VERIFIED = 'verified'

KEY_WALL_SECONDS = 'wall_seconds'


KEY_WORKING_DIRECTORY = 'working_directory'

KEY_WRITE = 'write'

TEXT_3F = '{:.3f}'

TEXT_6F = '| {} | {} | ${:.6f} | {} | {} |'

TEXT_6F_2 = '{:.6f}'

TEXT_6F_6F_0_0 = '| {} | {} | {} | ${:.6f} | ${:.6f} | {} | {} | {:.0%} | {:.0%} |'

TEXT_6F_S = '| {} | {} | {} | {} | {} | ${:.6f} | {} | {} | {} | {} | {} | {}s | {} |'

TEXT_BASELINE_VS_OPTIMIZED = '## Baseline vs optimized'

TEXT_BY_AGENT = 'By agent'

TEXT_BY_MODEL = 'By model'

TEXT_BY_TOOL = '## By tool'

TEXT_CORRECTNESS_IS_EQUAL_OR_BETTER = 'correctness is equal or better.'

TEXT_COSTS_AND_TOKENS_COME_FROM_SESSION_JSONL_STEP_FINISH_EVENTS_ = 'Costs and tokens come from `session.jsonl` step-finish events. Correctness is the verification exit code; '

TEXT_COST_AND_TOKEN_REPORT = '# Cost and Token Report'

TEXT_COST_AND_TOKEN_REPORT_NO_COMPLETED_RESULT_DIRECTORIES_WERE_F = '# Cost and Token Report\n\nNo completed result directories were found.\n'

TEXT_INPUT_TOKENS = '- Input tokens: {}'



TEXT_NOTES = '## Notes'

TEXT_N_A = 'n/a'

TEXT_OUTPUT_TOKENS = '- Output tokens: {}'

TEXT_REWORK_AND_HUMAN_INTERVENTION_MUST_BE_RECORDED_SEPARATELY_A_ = 'rework and human intervention must be recorded separately. A lower cost is not a better result unless '

TEXT_RUNS = '- Runs: {}'

TEXT_RUN_ARM_TASK_MODEL_AGENT_COST_INPUT_OUTPUT_STEPS_TOOLS_ERROR = '| Run | Arm | Task | Model | Agent | Cost | Input | Output | Steps | Tools | Errors | Wall | Verify |'


TEXT_SUMMARY = '## Summary'

TEXT_TASK_BASELINE_RUNS_OPTIMIZED_RUNS_BASELINE_AVG_COST_OPTIMIZE = '| Task | Baseline runs | Optimized runs | Baseline avg cost | Optimized avg cost | Cost ratio | Token ratio | Baseline pass | Optimized pass |'


TEXT_TEXT_2 = '| {} | {} |'


TEXT_TEXT_4 = '| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'

TEXT_TEXT_5 = '| --- | ---: | ---: | ---: | ---: |'

TEXT_TEXT_6 = '| --- | ---: |'

TEXT_TEXT_7 = '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |'

TEXT_TOOL_CALLS = '| Tool | Calls |'

TEXT_TOOL_CALLS_ERRORS = '- Tool calls: {} ({} errors)'

TEXT_TOTAL_COST_6F = '- Total cost: ${:.6f}'

TEXT_VALUE_RUNS_COST_TOKENS_TOOL_ERRORS = '| Value | Runs | Cost | Tokens | Tool errors |'

TEXT_VERIFIED = '- Verified: {}/{}'
