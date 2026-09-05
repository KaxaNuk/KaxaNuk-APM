"""
Regenerate the `investment-lab` skill references from the KN Research Process template.

The template -- public at `KaxaNuk/KaxaNuk-Research-Process`, `main` only -- is the source of truth
for the four experiment documents and the experiment notebook that `experiment-lifecycle` ships as
copyable references.  A skill that carried its own version of those files drifted from the template
once already, so the copies are regenerated from the template rather than edited by hand.

Run from the repository root before a release:

    python tools/sync_investment_lab_references.py
    python tools/sync_investment_lab_references.py --source D:/Research/KaxaNuk-Research-Process
    python tools/sync_investment_lab_references.py --reference v0.4.0

Without `--source` the files are fetched from GitHub at the given `--reference` (a branch or a
tag, `main` by default).  The four documents have `_1` rewritten to `_N` so they read as templates
for any experiment; the notebook is copied as it is, because a new experiment copies and renames it.
"""

import argparse
import pathlib
import re
import sys
import urllib.request

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parent.parent
REFERENCES_DIRECTORY = (
    REPOSITORY_ROOT
    / "investment-lab"
    / ".apm"
    / "skills"
    / "experiment-lifecycle"
    / "references"
)
TEMPLATE_RAW_URL = "https://raw.githubusercontent.com/KaxaNuk/KaxaNuk-Research-Process"
EXPERIMENT_DIRECTORY = "Experiments/Experiment_1"

# Template file -> reference file.  The documents are renamed from `_1` to `_N`; the notebook keeps
# its content and takes the name the skill refers to.
DOCUMENTS = {
    "BLUEPRINT_1.md": "blueprint-template.md",
    "BRAINSTORMING_1.md": "brainstorming-template.md",
    "JOURNAL_1.md": "journal-template.md",
    "FINDINGS_1.md": "findings-template.md",
}
NOTEBOOK = {
    "experiment_1.ipynb": "experiment-notebook.ipynb",
}
RENAMES = (
    (
        re.compile(r"_1\.md\b"),
        "_N.md",
    ),
    (
        re.compile(r"^# (Blueprint|Brainstorming|Journal|Findings) — Experiment 1", re.MULTILINE),
        r"# \1 — Experiment N",
    ),
    (
        re.compile(r"^## Experiment 1 — .*$", re.MULTILINE),
        "## Experiment N — <the idea, in five words>",
    ),
)


def main() -> int:
    """Parse the command line, fetch every template file, write the references."""
    parser = argparse.ArgumentParser(
        description="Regenerate the experiment-lifecycle references from the template.",
    )
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=None,
        help="a local checkout of the template to copy from, instead of fetching from GitHub",
    )
    parser.add_argument(
        "--reference",
        default="main",
        help="the branch or tag to fetch from GitHub when --source is not given (default: main)",
    )
    arguments = parser.parse_args()

    REFERENCES_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for template_name, reference_name in DOCUMENTS.items():
        text = read_template_text(template_name, arguments.source, arguments.reference)
        (REFERENCES_DIRECTORY / reference_name).write_text(
            rename_experiment(text),
            encoding="utf-8",
        )
        print(f"  {reference_name}")
    for template_name, reference_name in NOTEBOOK.items():
        text = read_template_text(template_name, arguments.source, arguments.reference)
        (REFERENCES_DIRECTORY / reference_name).write_text(text, encoding="utf-8")
        print(f"  {reference_name}")

    if arguments.source is not None:
        origin = str(arguments.source)
    else:
        origin = f"GitHub @ {arguments.reference}"
    print(f"references regenerated from {origin}")

    return 0


def read_template_text(
    template_name: str,
    source: "pathlib.Path | None",
    reference: str,
) -> str:
    """The text of one template file, from a local checkout or from GitHub."""
    relative_path = f"{EXPERIMENT_DIRECTORY}/{template_name}"
    if source is not None:
        path = source / relative_path
        if not path.is_file():
            msg = f"{path} does not exist; is --source a checkout of the template?"

            raise FileNotFoundError(msg)

        return path.read_text(encoding="utf-8")

    url = f"{TEMPLATE_RAW_URL}/{reference}/{relative_path}"
    with urllib.request.urlopen(url, timeout=30) as response:

        return response.read().decode("utf-8")


def rename_experiment(
    text: str,
) -> str:
    """Turn the template's Experiment 1 document into a document for any Experiment N."""
    renamed = text
    for pattern, replacement in RENAMES:
        renamed = pattern.sub(replacement, renamed)

    return renamed


if __name__ == "__main__":
    sys.exit(main())
