"""
Regenerate the `investment-lab` skill references from the KN Research Process template.

The template -- public at `KaxaNuk/KaxaNuk-Research-Process`, its `example` branch -- is the source of truth
for the four experiment documents and the experiment notebook that `experiment-lifecycle` ships as
copyable references.  A skill that carried its own version of those files drifted from the template
once already, so the copies are regenerated from the template rather than edited by hand.

Run from the repository root before a release:

    python tools/sync_investment_lab_references.py
    python tools/sync_investment_lab_references.py --source D:/Research/KaxaNuk-Research-Process
    python tools/sync_investment_lab_references.py --reference v0.4.0

Without `--source` the files are fetched from GitHub at the given `--reference` (a branch or a
tag, `example` by default -- `main` is the shape only, six folders and the root documents).

`example` works one strategy through the process, and keeps that strategy's own lines between
whole-line markers -- `<!-- example: begin -->` and `<!-- example: end -->` in Markdown, and
`# EXAMPLE-ONLY CELL` at the top of a notebook cell -- so they are stripped before anything is
written: a reference is the template's description, never another strategy's content.  The four
documents then have `_1` rewritten to `_N` so they read as templates for any experiment; the
notebook keeps its name inside, because a new experiment copies and renames it.
"""

import argparse
import functools
import json
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
# A marker counts only as a whole line: `JOURNAL_1.md` quotes both markers inside a sentence, and a
# match that started or stopped there would cut the file in the wrong place.
EXAMPLE_BLOCK = re.compile(
    r"^<!-- example: begin -->$.*?^<!-- example: end -->$\n?",
    re.MULTILINE
    | re.DOTALL,
)
EXAMPLE_ONLY_CELL = "# EXAMPLE-ONLY CELL"
EXTRA_BLANK_LINES = re.compile(r"\n{3,}")


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
        default="example",
        help="the branch or tag to fetch from GitHub when --source is not given (default: example)",
    )
    arguments = parser.parse_args()

    REFERENCES_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for template_name, reference_name in DOCUMENTS.items():
        document_text = read_template_text(
            template_name,
            arguments.source,
            arguments.reference,
        )
        (REFERENCES_DIRECTORY / reference_name).write_text(
            rename_experiment(
                strip_example_content(document_text),
            ),
            encoding="utf-8",
        )
        print(f"  {reference_name}")
    for template_name, reference_name in NOTEBOOK.items():
        notebook_text = read_template_text(
            template_name,
            arguments.source,
            arguments.reference,
        )
        (REFERENCES_DIRECTORY / reference_name).write_text(
            strip_example_cells(notebook_text),
            encoding="utf-8",
        )
        print(f"  {reference_name}")

    if arguments.source is not None:
        origin = str(arguments.source)
    else:
        origin = f"GitHub @ {arguments.reference}"
    print(f"references regenerated from {origin}")

    return 0


def read_cell_source(
    cell: dict[str, object],
) -> str:
    """A notebook cell's source as one string; the format allows a string or a list of lines."""
    source = cell["source"]

    if isinstance(source, list):

        return "".join(source)

    return source


def read_template_text(
    template_name: str,
    source: pathlib.Path | None,
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
    renamed = functools.reduce(
        _apply_rename,
        RENAMES,
        text,
    )

    return renamed


def strip_example_cells(
    text: str,
) -> str:
    """
    Remove the worked strategy's cells from a notebook, and its lines from the cells that stay.

    A notebook with nothing to strip is returned exactly as it was read, so regenerating it from an
    unchanged template leaves no diff.
    """
    notebook = json.loads(text)
    original_cells = notebook["cells"]
    kept_cells = [
        cell
        for cell in original_cells
        if not _is_example_only_cell(cell)
    ]
    rewritten = [
        _strip_cell(cell)
        for cell in kept_cells
    ]
    cells_dropped = len(kept_cells) != len(original_cells)
    cells_rewritten = any(rewritten)
    changed = cells_dropped or cells_rewritten

    if not changed:

        return text

    notebook["cells"] = kept_cells

    return json.dumps(
        notebook,
        indent=1,
        ensure_ascii=False,
    )


def strip_example_content(
    text: str,
) -> str:
    """
    Remove the worked strategy's own lines from a Markdown text.

    A removed block leaves the blank lines on both sides of it, so runs of blank lines collapse to
    one, and a block that closed the file leaves it ending as it did — only when something was
    removed, so a text with no markers comes back untouched.
    """
    stripped, removed_blocks = EXAMPLE_BLOCK.subn(
        "",
        text,
    )

    if removed_blocks == 0:

        return text

    collapsed = EXTRA_BLANK_LINES.sub(
        "\n\n",
        stripped,
    )
    trimmed = collapsed.rstrip("\n")

    if text.endswith("\n"):

        return f"{trimmed}\n"

    return trimmed


def write_cell_source(
    cell: dict[str, object],
    source: str,
) -> None:
    """Put a source back in the form the cell already used, a string or a list of lines."""
    if isinstance(cell["source"], list):
        cell["source"] = source.splitlines(keepends=True)
    else:
        cell["source"] = source


def _apply_rename(
    text: str,
    rename: tuple[re.Pattern[str], str],
) -> str:
    """One step of the `_1` to `_N` rewrite, shaped for `functools.reduce`."""
    pattern, replacement = rename
    renamed = pattern.sub(
        replacement,
        text,
    )

    return renamed


def _is_example_only_cell(
    cell: dict[str, object],
) -> bool:
    """Whether a cell is the worked strategy's alone, marked on its first line."""
    source = read_cell_source(cell)
    example_only = source.startswith(EXAMPLE_ONLY_CELL)

    return example_only


def _strip_cell(
    cell: dict[str, object],
) -> bool:
    """Strip a kept cell's example lines in place, and say whether anything was removed."""
    source = read_cell_source(cell)
    stripped_source = strip_example_content(source)
    stripped = stripped_source != source

    if stripped:
        write_cell_source(
            cell,
            stripped_source.rstrip("\n"),
        )

    return stripped


if __name__ == "__main__":
    sys.exit(main())
