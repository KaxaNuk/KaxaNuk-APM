"""
Unit tests for the SessionStart bootstrap hook.
"""
import pathlib

import bootstrap_context
import context_paths


class TestMain:
    def test_all_present_returns_empty(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        bootstrap_context.main(
            '',
            tmp_path,
        )
        result = bootstrap_context.main(
            '',
            tmp_path,
        )
        expected = ''

        assert result == expected

    def test_existing_file_is_not_overwritten(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        directory = tmp_path / 'docs' / 'context'
        directory.mkdir(parents=True)
        memory = directory / 'memory.md'
        memory.write_text(
            '# decision: keep me\n',
            encoding='utf-8',
        )
        bootstrap_context.main(
            '',
            tmp_path,
        )
        result = memory.read_text(encoding='utf-8')
        expected = '# decision: keep me\n'

        assert result == expected

    def test_missing_directory_creates_five_files(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        bootstrap_context.main(
            '',
            tmp_path,
        )
        directory = tmp_path / 'docs' / 'context'
        entries = directory.iterdir()
        created = sorted(entries)
        result = [
            path.name
            for path
            in created
        ]
        expected = list(context_paths.CONTEXT_FILE_NAMES)

        assert result == expected

    def test_missing_directory_reports_count(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        result = bootstrap_context.main(
            '',
            tmp_path,
        )
        expected = '[context-system] initialized docs/context/ (5 file(s) created)'

        assert result == expected

    def test_only_missing_file_is_created(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        bootstrap_context.main(
            '',
            tmp_path,
        )
        todo = tmp_path / 'docs' / 'context' / 'todo.md'
        todo.unlink()
        result = bootstrap_context.main(
            '',
            tmp_path,
        )
        expected = '[context-system] initialized docs/context/ (1 file(s) created)'

        assert result == expected

    def test_stub_content_matches_table(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        bootstrap_context.main(
            '',
            tmp_path,
        )
        todo = tmp_path / 'docs' / 'context' / 'todo.md'
        result = todo.read_text(encoding='utf-8')
        expected = context_paths.STUB_CONTENTS['todo.md']

        assert result == expected
