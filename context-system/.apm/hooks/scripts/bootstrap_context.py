"""
SessionStart hook: create docs/context/ and any missing stub file.

Idempotent. Existing files are never touched. Prints one line only when something was created,
so the model learns about the working memory exactly once.
"""
import pathlib
import sys

import context_paths


def main(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Create every missing context file; report only when at least one was created.
    """
    directory = context_paths.context_directory(root)
    missing_names = [
        name
        for name
        in context_paths.CONTEXT_FILE_NAMES
        if not (directory / name).exists()
    ]

    if not missing_names:
        return ''

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    for name in missing_names:
        _write_stub(
            directory / name,
            name,
        )
    created_count = len(missing_names)

    return f'[context-system] initialized {context_paths.CONTEXT_DIRECTORY}/ ({created_count} file(s) created)'


def _write_stub(
    path: pathlib.Path,
    name: str,
) -> None:
    """
    Write the canonical stub for one context file.
    """
    path.write_text(
        context_paths.STUB_CONTENTS[name],
        encoding='utf-8',
    )


if __name__ == '__main__':
    exit_code = context_paths.run_hook(main)
    sys.exit(exit_code)
