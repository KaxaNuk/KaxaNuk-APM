"""
Unit tests for the SessionEnd daily-stub hook.
"""
import pathlib

import context_paths
import session_end_log


def make_log(
    root: pathlib.Path,
    content: str,
) -> pathlib.Path:
    """
    Create docs/context/session-log.md with the given content and return its path.
    """
    directory = root / 'docs' / 'context'
    directory.mkdir(parents=True)
    log = directory / 'session-log.md'
    log.write_text(
        content,
        encoding='utf-8',
    )

    return log


class TestMain:
    def test_entry_today_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        date = context_paths.today()
        existing = f'- [{date}]: real entry\n'
        log = make_log(
            tmp_path,
            existing,
        )
        session_end_log.main(
            '{"reason": "exit"}',
            tmp_path,
        )
        result = log.read_text(encoding='utf-8')
        expected = existing

        assert result == expected

    def test_missing_log_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_end_log.main(
            '{"reason": "exit"}',
            tmp_path,
        )
        log = tmp_path / 'docs' / 'context' / 'session-log.md'
        result = log.exists()
        expected = False

        assert result == expected

    def test_missing_reason_is_unknown(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        log = make_log(
            tmp_path,
            '# Session Log\n',
        )
        session_end_log.main(
            '{}',
            tmp_path,
        )
        content = log.read_text(encoding='utf-8')
        last_line = content.splitlines()[-1]
        result = last_line.endswith(']: session end (unknown) (auto-stub - no model entry today)')
        expected = True

        assert result == expected

    def test_no_entry_today_appends_stub_with_reason(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        log = make_log(
            tmp_path,
            '# Session Log\n- [2020-01-01]: old\n',
        )
        session_end_log.main(
            '{"reason": "prompt_input_exit"}',
            tmp_path,
        )
        content = log.read_text(encoding='utf-8')
        last_line = content.splitlines()[-1]
        date = context_paths.today()
        result = last_line
        expected = f'- [{date}]: session end (prompt_input_exit) (auto-stub - no model entry today)'

        assert result == expected
