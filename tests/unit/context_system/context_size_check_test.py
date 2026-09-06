"""
Unit tests for the UserPromptSubmit size-check hook.
"""
import pathlib

import context_paths
import context_size_check


def make_context(root: pathlib.Path) -> pathlib.Path:
    """
    Create docs/context with every stub and return the directory.
    """
    directory = root / 'docs' / 'context'
    directory.mkdir(parents=True)
    for name in context_paths.CONTEXT_FILE_NAMES:
        target = directory / name
        target.write_text(
            context_paths.STUB_CONTENTS[name],
            encoding='utf-8',
        )

    return directory


class TestCapsTable:
    def test_line_format_is_name_space_cap(self) -> None:
        table = context_size_check.caps_table()
        lines = table.splitlines()
        result = lines[0]
        expected = 'lessons.md 7000'

        assert result == expected

    def test_lists_every_context_file(self) -> None:
        table = context_size_check.caps_table()
        lines = table.splitlines()
        result = len(lines)
        expected = 5

        assert result == expected


class TestMain:
    def test_missing_directory_is_silent(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        result = context_size_check.main(
            '',
            tmp_path,
        )
        expected = ''

        assert result == expected

    def test_output_is_ascii(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        directory = make_context(tmp_path)
        todo = directory / 'todo.md'
        todo.write_text(
            'x' * 12000,
            encoding='utf-8',
        )
        output = context_size_check.main(
            '',
            tmp_path,
        )
        result = output.isascii()
        expected = True

        assert result == expected

    def test_over_cap_file_is_named_with_sizes(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        directory = make_context(tmp_path)
        todo = directory / 'todo.md'
        todo.write_text(
            'x' * 12000,
            encoding='utf-8',
        )
        output = context_size_check.main(
            '',
            tmp_path,
        )
        result = output.startswith('[context-size] OVER CAP: todo.md ~3000tok>2500. Run /compact-context')
        expected = True

        assert result == expected

    def test_under_cap_is_silent(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        make_context(tmp_path)
        result = context_size_check.main(
            '',
            tmp_path,
        )
        expected = ''

        assert result == expected
