"""
Shared adapter strings and templates.

Side effects: none.
"""
from __future__ import annotations
from ..constants import NEWLINE
from ..constants import EMPTY_STRING as EMPTY
from ..constants import ENCODING_UTF8 as UTF8
from ..constants import KEY_AGENT as AGENT_KEY
from ..constants import KEY_AGENTS as COMPONENT_AGENTS
from ..constants import KEY_ARCHITECT as ROLE_ARCHITECT
from ..constants import KEY_COMMANDS as COMPONENT_COMMANDS
from ..constants import KEY_COORDINATOR as ROLE_COORDINATOR
from ..constants import KEY_DESCRIPTION as DESCRIPTION_KEY
from ..constants import KEY_NODE_MODULES as NODE_MODULES
from ..constants import KEY_PLANNER as ROLE_PLANNER
from ..constants import KEY_RESEARCHER as ROLE_RESEARCHER
from ..constants import KEY_SKILLS as COMPONENT_SKILLS
from ..constants import MARKDOWN_SUFFIX as CLAUDE_AGENT_SUFFIX
from ..constants import TEXT_AGENT_MD as AGENTS_GLOB
from ..constants import TEXT_CODE_REVIEWER as ROLE_CODE_REVIEWER
from ..constants import TEXT_MD_2 as COMMANDS_GLOB
from ..constants import TEXT_PERFORMANCE_ANALYST as ROLE_PERFORMANCE
from ..constants import TEXT_PYCACHE as PYCACHE
from ..constants import TEXT_SECURITY_REVIEWER as ROLE_SECURITY
from ..constants import TEXT_SKILL_MD as SKILLS_GLOB
from ..constants import TEXT_TEXT as ROLE_HYPHEN
from ..constants import TEXT_TEXT_2_3 as GLOB_ALL

AGENT_PREFIX = "agent: "
AGENTS_FILE = "AGENTS.md"
CLAUDE_AGENTS_DIR = ".claude/agents"
CLAUDE_COMMANDS_DIR = ".claude/commands"
CLAUDE_FILE = "CLAUDE.md"
CLAUDE_SKILLS_DIR = ".claude/skills"
CODEX_AGENTS_DIR = ".codex/agents"
CODEX_AGENT_SUFFIX = ".toml"
COMMAND_TEMPLATE = "---\ndescription: {description}\n---\n\n{body}"
COMPONENT_COPY = "copy"
COMPONENT_INSTRUCTIONS = "instructions"
COPILOT_AGENT_SUFFIX = ".instructions.md"
COPILOT_AGENTS_DIR = ".github/instructions"
COPILOT_COMMANDS_DIR = ".github/prompts"
COPILOT_FILE = ".github/copilot-instructions.md"
COPILOT_INSTRUCTION_TEMPLATE = '---\napplyTo: "**/*"\n---\n\n# {role}\n\n{body}'
COPILOT_PROMPT_SUFFIX = ".prompt.md"
COPILOT_SKILLS_DIR = ".github/skills"
DESCRIPTION_PREFIX = "description: "
EDITOR_TOOLS = "Read, Grep, Glob, Edit, Write, Bash"
FRONTMATTER_END = "\n---\n"
FRONTMATTER_START = "---\n"
READ_ONLY_TOOLS = "Read, Grep, Glob"
ROLE_AGENT_SUFFIX = " agent"
ROLE_UNDERSCORE = "_"
CLAUDE_AGENT_TEMPLATE = "---\nname: {role}\ndescription: {description}\ntools: {tools}\n---\n\n{body}"
CODEX_AGENT_TEMPLATE = "name = {name}\ndescription = {description}\ndeveloper_instructions = {instructions}\n"

