"""
Unit tests for the PreCompact marker hook.
"""
import pathlib

import precompact_log


class TestMain:
    def test_marker_is_appended(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        directory = tmp_path / 'docs' / 'context'
        directory.mkdir(parents=True)
        log = directory / 'session-log.md'
        log.write_text(
            '# Session Log\n',
            encoding='utf-8',
        )
        precompact_log.main(
            '{}',
            tmp_path,
        )
        content = log.read_text(encoding='utf-8')
        last_line = content.splitlines()[-1]
        result = last_line.endswith(']: context compaction (details before this point may be summarized)')
        expected = True

        assert result == expected

    def test_missing_log_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        precompact_log.main(
            '{}',
            tmp_path,
        )
        log = tmp_path / 'docs' / 'context' / 'session-log.md'
        result = log.exists()
        expected = False

        assert result == expected
