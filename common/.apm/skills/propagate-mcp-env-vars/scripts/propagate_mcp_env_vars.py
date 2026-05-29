import os
import sys

MCP_FILE = '.mcp.json'

# Paths to .env files relative to the project root. Add more as needed.
ENV_FILES = [
    '.devcontainer/.env',
    'Config/.env',
    '.env',
]


def load_env_vars(env_file_path: str) -> dict[str, str]:
    """Load key=value pairs from a .env file, skipping comments and blanks."""
    env_vars: dict[str, str] = {}

    with open(env_file_path) as file:
        for line in file:
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith('#'):
                continue

            key, _, value = stripped_line.partition('=')
            clean_key = key.strip()
            stripped_value = value.strip()
            clean_value = stripped_value.strip("'\"")

            if clean_key:
                env_vars[clean_key] = clean_value

    return env_vars


def resolve_mcp_config(env_vars: dict[str, str], mcp_file_path: str) -> None:
    """Substitute ${VAR} references in .mcp.json with resolved values."""
    if not os.path.exists(mcp_file_path):
        error_message = f'Error: {mcp_file_path} not found'
        print(error_message, file=sys.stderr)
        sys.exit(1)

    with open(mcp_file_path) as file:
        resolved_content = file.read()

    for var_name, var_value in env_vars.items():
        resolved_content = resolved_content.replace(
            f'${{{var_name}}}',
            var_value,
        )

    with open(mcp_file_path, 'w') as file:
        file.write(resolved_content)

    print(f'Resolved env var references in {mcp_file_path}')


all_env_vars: dict[str, str] = {}

for env_file in ENV_FILES:
    if not os.path.exists(env_file):
        print(f'Warning: {env_file} not found, skipping', file=sys.stderr)
        continue

    file_vars = load_env_vars(env_file)
    all_env_vars.update(file_vars)

if not all_env_vars:
    error_message = 'Error: no env vars loaded from any configured ENV_FILES'
    print(error_message, file=sys.stderr)
    sys.exit(1)

resolve_mcp_config(all_env_vars, MCP_FILE)