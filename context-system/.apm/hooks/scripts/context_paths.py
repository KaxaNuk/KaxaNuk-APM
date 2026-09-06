"""
Shared constants and helpers for the context-system hooks.

Single source of truth for the docs/context file names, their size caps, the stub contents the
SessionStart hook creates, and the runner every hook uses. Every hook script imports this module.
"""
import datetime
import json
import os
import pathlib
import sys
import typing

CONTEXT_DIRECTORY = 'docs/context'
CONTEXT_FILE_NAMES = (
    'lessons.md',
    'memory.md',
    'results.md',
    'session-log.md',
    'todo.md',
)
# Approximate tokens = bytes / 4, which is what the context window actually pays.
CAPS_IN_TOKENS = {
    'lessons.md': 7000,
    'memory.md': 11000,
    'results.md': 6000,
    'session-log.md': 4000,
    'todo.md': 2500,
}
PROJECT_ROOT_VARIABLE = 'CLAUDE_PROJECT_DIR'
STUB_CONTENTS = {
    'lessons.md': '\n'.join([
        '# Lessons',
        '',
        '> Rules from corrections. Friction only - never repeat a logged mistake. List format. Cap enforced by hook.',
        '',
        '*(empty)*',
        '',
    ]),
    'memory.md': '\n'.join([
        '# Memory',
        '',
        '> Architecture decisions. One line each. Format: `# decision: sentence`. Cap enforced by hook.',
        '',
        '*(empty)*',
        '',
    ]),
    'results.md': '\n'.join([
        '# Results',
        '',
        '> Build log. 1-4 lines per finished item. List format. Older detail lives in `archive/`. Cap enforced by hook.',
        '',
        '*(empty)*',
        '',
    ]),
    'session-log.md': '\n'.join([
        '# Session Log',
        '',
        '> One line per session. Format: `- [YYYY-MM-DD]: information`. Cap enforced by hook.',
        '',
        '*(empty)*',
        '',
    ]),
    'todo.md': '\n'.join([
        '# Todo',
        '',
        '> Open work only. Status: `pending` / `in_progress`. Done -> move to `results.md`. Cap enforced by hook.',
        '',
        '*(empty)*',
        '',
    ]),
}

HookFunction = typing.Callable[[str, pathlib.Path], str]


def append_line(
    path: pathlib.Path,
    line: str,
) -> None:
    """
    Append one line as UTF-8 without BOM, creating the file when needed.
    """
    with path.open(
        'a',
        encoding='utf-8',
        newline='\n',
    ) as handle:
        handle.write(line + '\n')


def bytes_to_tokens(size_in_bytes: int) -> int:
    """
    Approximate token count of a file from its size.
    """
    return round(size_in_bytes / 4)


def context_directory(root: pathlib.Path) -> pathlib.Path:
    """
    The docs/context directory under a project root.
    """
    return root / CONTEXT_DIRECTORY


def parse_payload(payload: str) -> dict[str, object]:
    """
    Parse the hook's stdin JSON; anything that is not a JSON object becomes an empty dict.
    """
    try:
        parsed = json.loads(payload)
    except ValueError:
        return {}

    if not isinstance(
        parsed,
        dict,
    ):
        return {}

    return parsed


def project_root() -> pathlib.Path:
    """
    The consumer project root: CLAUDE_PROJECT_DIR when set, else the working directory.
    """
    configured = os.environ.get(PROJECT_ROOT_VARIABLE)

    if configured:
        return pathlib.Path(configured)

    return pathlib.Path.cwd()


def read_stdin() -> str:
    """
    Whole stdin as text; an unreadable stdin counts as empty.
    """
    try:
        return sys.stdin.read()
    except OSError:
        return ''


def run_hook(hook_function: HookFunction) -> int:
    """
    Run a hook's main function against stdin and the project root, print its output, never fail.
    """
    payload = read_stdin()
    root = project_root()
    output = _run_safely(
        hook_function,
        payload,
        root,
    )

    if output:
        print(output)

    return 0


def timestamp() -> str:
    """
    Local date and time as YYYY-MM-DD HH:MM.
    """
    now = datetime.datetime.now()

    return now.strftime('%Y-%m-%d %H:%M')


def today() -> str:
    """
    Local date as YYYY-MM-DD.
    """
    now = datetime.datetime.now()

    return now.strftime('%Y-%m-%d')


def _run_safely(
    hook_function: HookFunction,
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Call the hook function; any exception is swallowed because a hook must never block the turn.
    """
    try:
        return hook_function(
            payload,
            root,
        )
    except Exception:  # noqa: BLE001 - deliberate: hooks are fire-and-forget.
        return ''
