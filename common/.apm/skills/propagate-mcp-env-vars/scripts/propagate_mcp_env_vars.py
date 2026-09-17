"""
Substitute ${VAR} references in .mcp.json with values from the project's .env files.

Usage (from the project root, no arguments):
    python propagate_mcp_env_vars.py

Exit code 0 when .mcp.json was rewritten, 1 when no env vars were loaded or .mcp.json is missing.
Console output is ASCII only.
"""
import dataclasses
import functools
import pathlib
import sys

# Paths to .env files relative to the project root, earliest first; later files override earlier ones.
ENV_FILES = [
    '.devcontainer/.env',
    'Config/.env',
    '.env',
]
MCP_FILE = '.mcp.json'


@dataclasses.dataclass(frozen=True)
class EnvEntry:
    """
    One key=value pair read from a .env file.
    """
    key: str
    value: str


def load_env_vars(env_file_path: pathlib.Path) -> dict[str, str]:
    """
    Load key=value pairs from a .env file, skipping comments, blanks and lines without a key.
    """
    content = env_file_path.read_text(encoding='utf-8')
    raw_lines = content.splitlines()
    entries = [
        _parse_env_line(line)
        for line
        in raw_lines
    ]
    env_vars = {
        entry.key: entry.value
        for entry
        in entries
        if entry is not None
    }

    return env_vars


def main(project_root: pathlib.Path | None = None) -> int:
    """
    Load every configured .env file under the project root and resolve .mcp.json in place.
    """
    root = project_root if project_root is not None else pathlib.Path.cwd()
    env_paths = [
        root / env_file
        for env_file
        in ENV_FILES
    ]
    missing_paths = [
        env_path
        for env_path
        in env_paths
        if not env_path.exists()
    ]
    existing_paths = [
        env_path
        for env_path
        in env_paths
        if env_path.exists()
    ]
    for missing_path in missing_paths:
        print(
            f'Warning: {missing_path} not found, skipping',
            file=sys.stderr,
        )
    loaded_mappings = [
        load_env_vars(existing_path)
        for existing_path
        in existing_paths
    ]
    all_env_vars = _merge_mappings(loaded_mappings)

    if not all_env_vars:
        print(
            'Error: no env vars loaded from any configured ENV_FILES',
            file=sys.stderr,
        )

        return 1

    mcp_file_path = root / MCP_FILE

    if not mcp_file_path.exists():
        print(
            f'Error: {mcp_file_path} not found',
            file=sys.stderr,
        )

        return 1

    resolve_mcp_config(
        all_env_vars,
        mcp_file_path,
    )

    return 0


def resolve_mcp_config(
    env_vars: dict[str, str],
    mcp_file_path: pathlib.Path,
) -> None:
    """
    Substitute every known ${VAR} reference in the file; unknown references are left intact.
    """
    original_content = mcp_file_path.read_text(encoding='utf-8')
    resolved_content = functools.reduce(
        _replace_reference,
        env_vars.items(),
        original_content,
    )
    mcp_file_path.write_text(
        resolved_content,
        encoding='utf-8',
    )
    print(f'Resolved env var references in {mcp_file_path}')


def _merge_mappings(mappings: list[dict[str, str]]) -> dict[str, str]:
    """
    Merge mappings in order; a later mapping overrides an earlier one for the same key.
    """
    merged = {
        key: value
        for mapping
        in mappings
        for key, value
        in mapping.items()
    }

    return merged


def _parse_env_line(line: str) -> EnvEntry | None:
    """
    Parse one .env line into an entry, or None for blanks, comments and key-less lines.
    """
    stripped_line = line.strip()

    if not stripped_line or stripped_line.startswith('#'):
        return None

    key, _, value = stripped_line.partition('=')
    clean_key = key.strip()
    stripped_value = value.strip()
    clean_value = stripped_value.strip('\'"')

    if not clean_key:
        return None

    return EnvEntry(
        key=clean_key,
        value=clean_value,
    )


def _replace_reference(
    content: str,
    pair: tuple[str, str],
) -> str:
    """
    Replace every ${key} occurrence in content with the pair's value.
    """
    reference = ''.join([
        '${',
        pair[0],
        '}',
    ])

    return content.replace(
        reference,
        pair[1],
    )


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
