"""
UserPromptSubmit hook: warn when any docs/context file is over its token cap.

Silent when everything is under cap. `--caps` prints the cap table (one `name cap` line per file)
so /compact-context can read the values without restating them anywhere else.
"""
import pathlib
import sys

import context_paths

CAPS_FLAG = '--caps'
WARNING_SUFFIX = 'Run /compact-context to snapshot and hard-compact before these files bloat the per-task token floor.'


def caps_table() -> str:
    """
    The cap table as `name cap` lines, in file-name order.
    """
    lines = [
        f'{name} {cap}'
        for name, cap
        in context_paths.CAPS_IN_TOKENS.items()
    ]

    return '\n'.join(lines)


def main(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    One warning line naming every over-cap file, or an empty string.
    """
    directory = context_paths.context_directory(root)
    reports = [
        _over_cap_report(
            directory,
            name,
            cap,
        )
        for name, cap
        in context_paths.CAPS_IN_TOKENS.items()
    ]
    present_reports = [
        report
        for report
        in reports
        if report
    ]

    if not present_reports:
        return ''

    joined = ', '.join(present_reports)

    return f'[context-size] OVER CAP: {joined}. {WARNING_SUFFIX}'


def _over_cap_report(
    directory: pathlib.Path,
    name: str,
    cap: int,
) -> str:
    """
    `name ~Ntok>cap` when the file is over cap, else an empty string.
    """
    path = directory / name

    if not path.exists():
        return ''

    size_in_bytes = path.stat().st_size
    tokens = context_paths.bytes_to_tokens(size_in_bytes)

    if tokens <= cap:
        return ''

    return f'{name} ~{tokens}tok>{cap}'


if __name__ == '__main__':
    if CAPS_FLAG in sys.argv:
        table = caps_table()
        print(table)
        sys.exit(0)

    exit_code = context_paths.run_hook(main)
    sys.exit(exit_code)
