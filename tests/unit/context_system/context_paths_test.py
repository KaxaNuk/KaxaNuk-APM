"""
Unit tests for the shared context_paths module.
"""
import io
import pathlib
import sys

import pytest

import context_paths


def echo_hook(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Hook function that returns its payload verbatim.
    """
    return payload


def failing_hook(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Hook function that always raises, to prove run_hook never propagates.
    """
    message = 'boom'

    raise RuntimeError(message)


class TestAppendLine:
    def test_accents_survive_round_trip(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        target = tmp_path / 'results.md'
        context_paths.append_line(
            target,
            'Revisión: sección lista',
        )
        result = target.read_text(encoding='utf-8')
        expected = 'Revisión: sección lista\n'

        assert result == expected

    def test_line_is_appended_after_existing_content(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        target = tmp_path / 'results.md'
        target.write_text(
            'first\n',
            encoding='utf-8',
        )
        context_paths.append_line(
            target,
            'second',
        )
        result = target.read_text(encoding='utf-8')
        expected = 'first\nsecond\n'

        assert result == expected


class TestBytesToTokens:
    def test_four_bytes_is_one_token(self) -> None:
        result = context_paths.bytes_to_tokens(4000)
        expected = 1000

        assert result == expected


class TestContextDirectory:
    def test_directory_is_docs_context_under_root(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        result = context_paths.context_directory(tmp_path)
        expected = tmp_path / 'docs' / 'context'

        assert result == expected


class TestParsePayload:
    def test_empty_payload_is_empty_dict(self) -> None:
        result = context_paths.parse_payload('')
        expected = {}

        assert result == expected

    def test_invalid_json_is_empty_dict(self) -> None:
        result = context_paths.parse_payload('{not json')
        expected = {}

        assert result == expected

    def test_json_list_is_empty_dict(self) -> None:
        result = context_paths.parse_payload('[1, 2]')
        expected = {}

        assert result == expected

    def test_valid_object_is_returned(self) -> None:
        result = context_paths.parse_payload('{"agent_type": "Explore"}')
        expected = {'agent_type': 'Explore'}

        assert result == expected


class TestProjectRoot:
    def test_environment_variable_wins(
        self,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(
            'CLAUDE_PROJECT_DIR',
            str(tmp_path),
        )
        result = context_paths.project_root()
        expected = tmp_path

        assert result == expected

    def test_falls_back_to_working_directory(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.delenv(
            'CLAUDE_PROJECT_DIR',
            raising=False,
        )
        result = context_paths.project_root()
        expected = pathlib.Path.cwd()

        assert result == expected


class TestRunHook:
    def test_exception_in_hook_prints_nothing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(
            sys,
            'stdin',
            io.StringIO('{}'),
        )
        context_paths.run_hook(failing_hook)
        captured = capsys.readouterr()
        result = captured.out
        expected = ''

        assert result == expected

    def test_exception_in_hook_returns_zero(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(
            sys,
            'stdin',
            io.StringIO('{}'),
        )
        result = context_paths.run_hook(failing_hook)
        expected = 0

        assert result == expected

    def test_output_is_printed(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(
            sys,
            'stdin',
            io.StringIO('hello'),
        )
        context_paths.run_hook(echo_hook)
        captured = capsys.readouterr()
        result = captured.out
        expected = 'hello\n'

        assert result == expected


class TestStubContents:
    def test_every_context_file_has_a_cap(self) -> None:
        result = sorted(context_paths.CAPS_IN_TOKENS)
        expected = sorted(context_paths.CONTEXT_FILE_NAMES)

        assert result == expected

    def test_every_context_file_has_a_stub(self) -> None:
        result = sorted(context_paths.STUB_CONTENTS)
        expected = sorted(context_paths.CONTEXT_FILE_NAMES)

        assert result == expected


class TestTimestamp:
    def test_format_is_iso_date_and_time(self) -> None:
        value = context_paths.timestamp()
        result = len(value)
        expected = 16

        assert result == expected


class TestToday:
    def test_format_is_iso_date(self) -> None:
        value = context_paths.today()
        result = len(value)
        expected = 10

        assert result == expected
