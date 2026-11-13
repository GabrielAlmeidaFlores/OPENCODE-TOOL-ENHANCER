"""
String constants for tests/unit/test_toolwright_profiles.py.

Side effects: none.
"""
from __future__ import annotations
from tests.constants import (
    KEY_AGENTS,
    KEY_CODEGRAPH,
    KEY_DEMO,
    KEY_FULL,
    KEY_MINIMAL,
    KEY_NOPE,
    KEY_OK,
    KEY_STANDARD,
    KEY_STATUS,
    TEXT_AST_GREP,
    TEXT_MAIN,
    TEXT_UTF_8,
)

KEY_AVAILABLE = 'available'
TEXT_DEMO_YML = 'demo.yml'
TEXT_NAME_DEMO_COMPONENTS_AGENTS = 'name: demo\ncomponents:\n  - agents\n'
TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_AGENTS = 'name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - agents\n'
TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_MADE_UP = 'name: demo\ndescription: Demo.\ncomponents:\n  - agents\n  - made-up\n'
TEXT_NAME_DEMO_DESCRIPTION_DEMO_COMPONENTS_AGENTS_METADATA_OWNER_ = 'name: demo\ndescription: Demo.\ncomponents:\n  - agents\nmetadata:\n  owner: x\n'
TEXT_NAME_DEMO_DESCRIPTION_DEMO_PROFILE_COMPONENTS_AGENTS = 'name: demo\ndescription: Demo profile.\ncomponents:\n  - agents\n'
TEXT_NAME_OTHER_DESCRIPTION_DEMO_COMPONENTS_AGENTS = 'name: other\ndescription: Demo.\ncomponents:\n  - agents\n'
