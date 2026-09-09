"""
SessionEnd hook: append a bare date stub to docs/context/session-log.md when the model wrote no
entry today, so the log never has silent gaps. At most one stub per day.
"""
import pathlib
import sys

import context_paths

TARGET_FILE = 'session-log.md'


def main(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Append `- [today]: session end (reason) (auto-stub ...)` unless today already has an entry.
    """
    directory = context_paths.context_directory(root)
    path = directory / TARGET_FILE

    if not path.exists():
        return ''

    date = context_paths.today()
    content = path.read_text(encoding='utf-8')
    marker = f'[{date}'

    if marker in content:
        return ''

    data = context_paths.parse_payload(payload)
    reason = _reason(data)
    line = f'- [{date}]: session end ({reason}) (auto-stub - no model entry today)'
    context_paths.append_line(
        path,
        line,
    )

    return ''


def _reason(data: dict[str, object]) -> str:
    """
    The payload's reason when it is a non-empty string, else 'unknown'.
    """
    reason = data.get('reason')
    is_text = isinstance(
        reason,
        str,
    )

    if is_text and reason:
        return reason

    return 'unknown'


if __name__ == '__main__':
    exit_code = context_paths.run_hook(main)
    sys.exit(exit_code)
