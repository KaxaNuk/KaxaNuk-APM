"""
PreCompact hook: leave a forensic marker in docs/context/session-log.md.

PreCompact cannot inject instructions into the compaction prompt, so this only records where
context was lost: anything decided before the marker may have been summarized away.
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
    Append a timestamped compaction marker when the log exists.
    """
    directory = context_paths.context_directory(root)
    path = directory / TARGET_FILE

    if not path.exists():
        return ''

    stamp = context_paths.timestamp()
    line = f'- [{stamp}]: context compaction (details before this point may be summarized)'
    context_paths.append_line(
        path,
        line,
    )

    return ''


if __name__ == '__main__':
    exit_code = context_paths.run_hook(main)
    sys.exit(exit_code)
