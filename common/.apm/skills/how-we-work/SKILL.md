---
name: how-we-work
description: >
  Load this skill whenever work in a KaxaNuk repository is about to be committed, branched, merged,
  versioned or released. Use it when the user asks how to name a branch, whether to open an issue
  first, what a pull request must contain, how to write a changelog entry, which version number a
  change takes, or how to publish a release. It covers the issue-before-branch rule, the
  `issues/<number>` branch convention, the pull-request checklist, the changelog format and
  Semantic Versioning as KaxaNuk applies it. It does NOT cover the research process itself (use
  `experiment-lifecycle` from the `investment-lab` package) or Python style (the `python-bloom-code`
  and `python-pep8` instructions).
metadata:
  version: 0.1
---

# How we work — issues, branches, changelogs, versions

The same procedure in every KaxaNuk repository, so nobody has to explain it before sharing a tool.
Fewer meetings, more pull requests: a change proposed as a PR with its reasoning attached is
reviewable at any hour; a change proposed in a call is not.

## 1. The issue exists before the branch

An idea goes on the repository's **GitHub Project** first. The issue is where the *why* lives; the
branch is only where the *what* happens. A branch with no issue is work whose reasoning cannot be
reviewed.

```
idea  ->  issue on the Project board  ->  issues/<number> cut from main  ->  PR into main
```

1. **Open the issue.** State the question or the problem, not the solution.
2. **Cut the branch** from `main`: `git switch -c issues/<number> main`. Use `issues/27-B` and
   `issues/27-C` when one issue needs a second attempt or splits into parallel lines of work — same
   issue, same discussion, separate history.
3. **Work**, committing against the issue. Small commits with messages that say what moved and why.
4. **Open the PR into `main`.** `main` is not where you work; it is where work arrives.

Long-lived branches other than `main` exist only when a repository says so in its `AGENTS.md` or
`README.md` — a research template keeps an `example` branch that never merges back; a product may
keep a `dev` branch that is deployed. Never merge into such a branch by accident: read the repository's
own rule first.

## 2. Before any pull request

- **The linter passes.** For Python, `uvx ruff check .`, notebooks included; the repository's own
  configuration decides the rules.
- **Notebook outputs are stripped.** The committed notebook is the method; the record lives in a
  document.
- **The `CHANGELOG.md` entry is part of the change-set**, not a follow-up. If you cannot write the
  entry, the change-set is not finished.
- **No secrets, no binaries.** Nothing from a `.env` file, no keys in a notebook output or a log
  line, no charts, workbooks or PDFs unless the repository explicitly keeps them.
- **If a published number or a public interface moved, the PR says which**, and the documents that
  cite it changed in the same PR.

## 3. The changelog

One entry per change-set, newest first, in the KaxaNuk Data Curator convention:

```
## X.Y.Z (YYYY-MM-DD)

**One sentence saying what a reader has to do differently.**

### Added
### Changed
### Deprecated
### Fixed
### Removed
```

Each item is written for somebody who was not in the room: **say what moved and why, not what file
you touched**. "The regime model lives in the Refinery so a penalty sweep costs no download" is an
entry; "updated custom_calculations.py" is a diff. Name anything that invalidates a number or breaks
a caller, and say which. A removal is a change-set too.

## 4. Version numbers

[Semantic Versioning](https://semver.org/spec/v2.0.0.html), read for what the repository's users
actually depend on:

| Repository kind | MAJOR | MINOR | PATCH |
| --- | --- | --- | --- |
| **A library** (public API) | a caller has to change code | new capability, callers untouched | a fix; nothing observable changes except the bug |
| **A research repository** (results and the pipeline) | published results are invalidated and must be re-derived | a new experiment, signal, stage or document; existing results stand | tooling, documentation, hygiene; no result changes |
| **An APM package** (AI primitives) | a skill's contract or a file name changes so a consumer must re-read | a new skill, prompt or instruction | wording, references, fixes with the same contract |

Three conventions follow: a result or contract that changes is MAJOR even if the diff was one line —
severity is what a reader has to throw away, not the size of the diff; re-running a pipeline on
refreshed data is not a bump; while on `0.x`, a breaking change bumps MINOR, and `1.0.0` is reserved
for the first version somebody outside the team depends on — for a research repository, the first
strategy that reaches paper trading with its results reproduced from a clean clone.

## 5. Releasing

1. Bump the version where the repository keeps it — `pyproject.toml`, `apm.yml`, or both — in the
   same commit as the changelog entry.
2. Tag on `main` after the merge: `git tag -a vX.Y.Z -m "X.Y.Z"` and push the tag. Consumers pin to
   tags (`owner/repo/path#vX.Y.Z` for an APM package).
3. For a package published to an index, the release job builds from the tag, never from a working
   copy.

## 6. Two things never to do

- **Never rewrite pushed history on a shared branch.** Fix forward with a new commit; the exception
  is a branch only you have ever pushed.
- **Never print a secret to find out whether it is set.** Check for its presence, report *set* or
  *missing*, and stop there. An exposed key is rotated, not edited out of a file.
