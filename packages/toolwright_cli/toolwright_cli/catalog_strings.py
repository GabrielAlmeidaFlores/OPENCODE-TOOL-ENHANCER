"""
String constants for catalog.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_CHECK
from .constants import TEXT_MISSING_2 as TEXT_MISSING
from .constants import FLAG_CHECK
from .constants import KEY_AUTHOR
from .constants import KEY_EXIT_CODE
from .constants import KEY_LICENSE
from .constants import KEY_REQUIRED
from .constants import TEXT_1
from .constants import TEXT_INVALID_JSON

from .constants import (
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_ARTIFACTS,
    KEY_DETAIL,
    KEY_ID,
    KEY_OUTPUT,
    KEY_SCHEMA_VERSION,
    KEY_SOURCE,
    KEY_STATUS,
    KEY_TYPE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
    STATUS_OK,
)


KEY_ARTIFACT = 'artifact'



KEY_COUNTS = 'counts'

KEY_DEFINITIONS = 'definitions'

KEY_ENUM = 'enum'



KEY_LOCAL = 'local'

KEY_PROPERTIES = 'properties'



TEXT_ARTIFACT = 'artifact:{}'

TEXT_ARTIFACTS_MUST_BE_A_LIST = 'artifacts must be a list'

TEXT_ARTIFACT_S = '{} artifact(s)'

TEXT_ARTIFACT_S_VALIDATED = '{} artifact(s) validated'

TEXT_CATALOG_BUILDER_NOT_FOUND_AT = 'catalog builder not found at {}'

TEXT_CATALOG_MUST_BE_A_JSON_OBJECT = '{}: catalog must be a JSON object'

TEXT_CATALOG_NOT_FOUND_AT_RUN_TOOLWRIGHT_CATALOG_BUILD = "catalog not found at {}; run 'toolwright catalog build'"

TEXT_CATALOG_REGISTRY_JSON = 'catalog/registry.json'

TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON = 'catalog/schema/entry.schema.json'

TEXT_CATALOG_SCHEMA_NOT_FOUND_AT = 'catalog schema not found at {}'

TEXT_DECLARED_ACTUAL = 'declared {}, actual {}'

TEXT_DUPLICATE_ID_FOR_TYPE = 'duplicate id for type'

TEXT_EXPECTED_1_FOUND = 'expected 1, found {}'


TEXT_LOCAL_PATH_MISSING = 'local path missing: {}'


TEXT_SCRIPTS_CATALOG_BUILD_CATALOG_PY = 'scripts/catalog/build_catalog.py'

TEXT_TEXT = '?'

TEXT_UNKNOWN_TYPE = 'unknown type {}'
