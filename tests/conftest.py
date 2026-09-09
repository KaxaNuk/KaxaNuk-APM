"""
Pytest configuration: make the skill and hook scripts importable as plain modules.
"""
import pathlib
import sys

CONFTEST_PATH = pathlib.Path(__file__)
REPOSITORY_ROOT = CONFTEST_PATH.resolve().parent.parent
SCRIPT_DIRECTORIES = [
    REPOSITORY_ROOT / 'common' / '.apm' / 'skills' / 'bloom-code-lint' / 'scripts',
    REPOSITORY_ROOT / 'common' / '.apm' / 'skills' / 'propagate-mcp-env-vars' / 'scripts',
    REPOSITORY_ROOT / 'context-system' / '.apm' / 'hooks' / 'scripts',
]

for script_directory in SCRIPT_DIRECTORIES:
    directory_string = str(script_directory)
    sys.path.insert(
        0,
        directory_string,
    )
