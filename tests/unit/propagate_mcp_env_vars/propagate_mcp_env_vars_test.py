"""
Unit tests for the propagate_mcp_env_vars skill script.
"""
import pathlib

import pytest

from propagate_mcp_env_vars import (
    load_env_vars,
    main,
    resolve_mcp_config,
)


class TestLoadEnvVars:
    def test_blank_and_comment_lines_are_skipped(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            '# comment\n\nTOKEN=abc\n',
            encoding='utf-8',
        )
        result = load_env_vars(env_file)
        expected = {'TOKEN': 'abc'}

        assert result == expected

    def test_key_value_pair_is_parsed(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            'TOKEN=abc\n',
            encoding='utf-8',
        )
        result = load_env_vars(env_file)
        expected = {'TOKEN': 'abc'}

        assert result == expected

    def test_line_without_key_is_skipped(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            '=orphan\n',
            encoding='utf-8',
        )
        result = load_env_vars(env_file)
        expected = {}

        assert result == expected

    def test_surrounding_quotes_are_stripped(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            'TOKEN="abc"\nOTHER=\'xyz\'\n',
            encoding='utf-8',
        )
        result = load_env_vars(env_file)
        expected = {
            'OTHER': 'xyz',
            'TOKEN': 'abc',
        }

        assert result == expected


class TestMain:
    def test_later_env_file_overrides_earlier(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        devcontainer_directory = tmp_path / '.devcontainer'
        devcontainer_directory.mkdir()
        first_env = devcontainer_directory / '.env'
        first_env.write_text(
            'TOKEN=first\n',
            encoding='utf-8',
        )
        second_env = tmp_path / '.env'
        second_env.write_text(
            'TOKEN=second\n',
            encoding='utf-8',
        )
        mcp_file = tmp_path / '.mcp.json'
        mcp_file.write_text(
            '{"url": "https://x/${TOKEN}"}',
            encoding='utf-8',
        )
        main(tmp_path)
        result = mcp_file.read_text(encoding='utf-8')
        expected = '{"url": "https://x/second"}'

        assert result == expected

    def test_missing_mcp_file_returns_one(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            'TOKEN=abc\n',
            encoding='utf-8',
        )
        result = main(tmp_path)
        expected = 1

        assert result == expected

    def test_no_env_files_returns_one(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        result = main(tmp_path)
        expected = 1

        assert result == expected

    def test_output_is_ascii_only(
        self,
        tmp_path: pathlib.Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        main(tmp_path)
        captured = capsys.readouterr()
        combined = captured.out + captured.err
        result = combined.isascii()
        expected = True

        assert result == expected

    def test_resolved_file_returns_zero(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        env_file = tmp_path / '.env'
        env_file.write_text(
            'TOKEN=abc\n',
            encoding='utf-8',
        )
        mcp_file = tmp_path / '.mcp.json'
        mcp_file.write_text(
            '{"url": "https://x/${TOKEN}"}',
            encoding='utf-8',
        )
        result = main(tmp_path)
        expected = 0

        assert result == expected


class TestResolveMcpConfig:
    def test_known_reference_is_substituted(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        mcp_file = tmp_path / '.mcp.json'
        mcp_file.write_text(
            '{"url": "https://x/${TOKEN}"}',
            encoding='utf-8',
        )
        resolve_mcp_config(
            {'TOKEN': 'abc'},
            mcp_file,
        )
        result = mcp_file.read_text(encoding='utf-8')
        expected = '{"url": "https://x/abc"}'

        assert result == expected

    def test_unknown_reference_is_left_intact(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        mcp_file = tmp_path / '.mcp.json'
        mcp_file.write_text(
            '{"url": "https://x/${OTHER}"}',
            encoding='utf-8',
        )
        resolve_mcp_config(
            {'TOKEN': 'abc'},
            mcp_file,
        )
        result = mcp_file.read_text(encoding='utf-8')
        expected = '{"url": "https://x/${OTHER}"}'

        assert result == expected
