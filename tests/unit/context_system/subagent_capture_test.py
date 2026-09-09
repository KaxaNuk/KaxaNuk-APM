"""
Unit tests for the SubagentStop capture hook.
"""
import pathlib

import subagent_capture

AMBIENT_PAYLOAD = '{"hook_event_name": "SubagentStop", "agent_id": "a347c5", "agent_type": "", "last_assistant_message": "the user prompt"}'
REAL_PAYLOAD = '{"hook_event_name": "SubagentStop", "agent_type": "Explore", "last_assistant_message": "Revisi\\u00f3n: secci\\u00f3n lista\\nsecond line"}'


def make_results(root: pathlib.Path) -> pathlib.Path:
    """
    Create docs/context/results.md with one existing line and return its path.
    """
    directory = root / 'docs' / 'context'
    directory.mkdir(parents=True)
    results = directory / 'results.md'
    results.write_text(
        '# Results\n',
        encoding='utf-8',
    )

    return results


class TestMain:
    def test_ambient_turn_with_agent_id_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        results = make_results(tmp_path)
        subagent_capture.main(
            AMBIENT_PAYLOAD,
            tmp_path,
        )
        result = results.read_text(encoding='utf-8')
        expected = '# Results\n'

        assert result == expected

    def test_empty_message_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        results = make_results(tmp_path)
        subagent_capture.main(
            '{"agent_type": "Explore", "last_assistant_message": "  \\n "}',
            tmp_path,
        )
        result = results.read_text(encoding='utf-8')
        expected = '# Results\n'

        assert result == expected

    def test_missing_results_file_writes_nothing(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        subagent_capture.main(
            REAL_PAYLOAD,
            tmp_path,
        )
        results = tmp_path / 'docs' / 'context' / 'results.md'
        result = results.exists()
        expected = False

        assert result == expected

    def test_real_subagent_appends_exactly_one_line(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        results = make_results(tmp_path)
        subagent_capture.main(
            REAL_PAYLOAD,
            tmp_path,
        )
        content = results.read_text(encoding='utf-8')
        lines = content.splitlines()
        result = len(lines)
        expected = 2

        assert result == expected

    def test_real_subagent_appends_first_line_with_accents(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        results = make_results(tmp_path)
        subagent_capture.main(
            REAL_PAYLOAD,
            tmp_path,
        )
        content = results.read_text(encoding='utf-8')
        last_line = content.splitlines()[-1]
        result = last_line.endswith('] subagent Explore: Revisión: sección lista')
        expected = True

        assert result == expected

    def test_returns_empty_output(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        make_results(tmp_path)
        result = subagent_capture.main(
            REAL_PAYLOAD,
            tmp_path,
        )
        expected = ''

        assert result == expected


class TestPrivateSummarize:
    def test_long_line_is_truncated(self) -> None:
        summary = subagent_capture._summarize('y' * 500)
        result = len(summary)
        expected = 300

        assert result == expected

    def test_non_string_is_empty(self) -> None:
        result = subagent_capture._summarize(None)
        expected = ''

        assert result == expected
