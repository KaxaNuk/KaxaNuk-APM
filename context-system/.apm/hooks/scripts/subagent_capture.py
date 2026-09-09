"""
SubagentStop hook: append each real subagent's final line to docs/context/results.md.

Guard rail, learned from the scaffold this package ports: some runtimes fire SubagentStop on every
main-agent turn with `agent_id` populated, `agent_type` empty and `last_assistant_message` carrying
the user's own prompt. Only a non-empty `agent_type` identifies a real subagent. Never substitute a
default name for a missing one.
"""
import pathlib
import sys

import context_paths

MESSAGE_LIMIT = 300
TARGET_FILE = 'results.md'


def main(
    payload: str,
    root: pathlib.Path,
) -> str:
    """
    Append `- [stamp] subagent <type>: <first line>` when the payload comes from a real subagent.
    """
    data = context_paths.parse_payload(payload)
    agent_type = data.get('agent_type')

    if not _is_real_subagent(agent_type):
        return ''

    message = data.get('last_assistant_message')
    summary = _summarize(message)

    if not summary:
        return ''

    directory = context_paths.context_directory(root)
    path = directory / TARGET_FILE

    if not path.exists():
        return ''

    stamp = context_paths.timestamp()
    line = f'- [{stamp}] subagent {agent_type}: {summary}'
    context_paths.append_line(
        path,
        line,
    )

    return ''


def _is_real_subagent(agent_type: object) -> bool:
    """
    True only for a non-empty agent_type string.
    """
    if not isinstance(
        agent_type,
        str,
    ):
        return False

    stripped = agent_type.strip()

    return stripped != ''


def _summarize(message: object) -> str:
    """
    First non-empty line of the message, truncated to MESSAGE_LIMIT characters.
    """
    if not isinstance(
        message,
        str,
    ):
        return ''

    raw_lines = message.splitlines()
    stripped_lines = [
        line.strip()
        for line
        in raw_lines
    ]
    non_empty_lines = [
        line
        for line
        in stripped_lines
        if line
    ]

    if not non_empty_lines:
        return ''

    return non_empty_lines[0][:MESSAGE_LIMIT]


if __name__ == '__main__':
    exit_code = context_paths.run_hook(main)
    sys.exit(exit_code)
