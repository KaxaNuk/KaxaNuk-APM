---
name: objective-and-bibliotheca
description: >
  Load this skill when step 1 of the KN Research Process is being done: writing or revising
  `OBJECTIVE.md`, deciding what a strategy actually claims, or filling `Bibliotheca/` with the
  notes those claims rest on. Use it when the user has an idea for a strategy and wants to start,
  asks what to read, asks to add a paper or book note, asks to write the claims table or the *what
  is not claimed* section, or asks whether a source may be cited yet. It covers the order the
  objective and the reading are written in, how a claim becomes a question that can be read for,
  the note convention and its four rules, citation verification, and the stopping condition. It
  does NOT cover the experiment documents, the notebook contract or the later steps
  (`experiment-lifecycle`), the `c_*` and `r_*` columns (`data-curator-custom-calculations`,
  `data-refinery-custom-calculations`), screening a feature (`data-analyzer-signal-screening`), or
  the universe (`universe-point-in-time`) — step 1 finishes before any identifier is downloaded.
metadata:
  version: 0.1
---

# Step 1 — the objective, and the notes under it

**In plain words:** a literature review with a thesis at the end of it. **It produces** a referenced
hypothesis, in the repository, dated. **It prevents** backtesting a hunch you cannot defend
afterwards.

Two files, and they are written together rather than in sequence: `OBJECTIVE.md` at the root, and
`Bibliotheca/` beside it. **Nothing is downloaded and nothing is measured in this step.**

## The order, in five passes

Writing the objective first and citing afterwards produces references chosen to support a sentence
that is already written. Reading the whole literature first has no stopping condition. Neither is the
answer; **five passes** are.

### Pass 1 — draft the idea, and split it into claims

One sentence somebody outside the team could repeat. Then split it into the three claims
`OBJECTIVE.md` asks for, because they are tested separately and their status will not be the same:

| Claim | What it is | Where it usually starts |
| --- | --- | --- |
| **the signal** | what selecting on this is claimed to produce | untested |
| **the sizing** | what weighting by this is claimed to add | untested |
| **the construction** | a property the rules guarantee — a screen, an exclusion | true by construction, untested as a source of return |

**No citations in this pass.** The draft exists to raise questions, not to be right.

### Pass 2 — turn each claim into the question that would settle it

This is the pass people skip, and it is the one that makes the reading finite. *Momentum* is a topic
and has no stopping condition. *Does momentum exist, and over what window?* is a question, and three
sources answer it.

**One question per claim.** Write them down. They are the search terms, and they are also the
headings the notes get grouped under in `BIBLIOGRAPHY.md`.

### Pass 3 — find sources per question, and look for the ones that disagree

**Deliberately seek the sources that argue against the strategy.** A Part 1 where every source agrees
is a Part 1 assembled to support a conclusion rather than to reach one, and it is the most common
failure of this step.

If nothing in the literature contradicts the design, keep looking. Something almost always does, and
the contradiction is usually the most valuable line in the folder: it becomes a prediction, a *what
is not claimed*, or a reason the design changes.

Keep the two kinds of entry apart, because `BIBLIOGRAPHY.md` does:

- **A note** is a source somebody read. It may be cited and claimed on.
- **A lead** is a source somebody thinks will help. **Nothing may be claimed on its authority.** It is
  listed with *No note yet.*, and that is a task rather than a decoration.

### Pass 4 — verify every citation, then write the note

**Check the citation against the publisher's record before writing anything:** journal, volume, issue,
pages, and a link that resolves. `BIBLIOGRAPHY.md` says never invent a URL or a page number, and
**recalled citations are how invented ones get in.** A wrong citation is worse than none.

Be honest in the `read:` field about what was actually read — the whole paper, the abstract, or the
headline result verified against the record. A `read:` field that overstates will have a number quoted
out of it later by somebody who trusted it.

Then write the note. Four rules separate a note from a summary:

1. **The implication is a blockquote, always.** It is the only part that is *ours*.
2. **A heading states the source's claim, never our verdict.** Verdicts live in the blockquote, where
   they can change when a result moves; a heading carrying a verdict rots silently.
3. **Record contradictions as contradictions**, never smoothed into agreement.
4. **Never invent a URL or a page number.** A gap is recorded as a task.

Close every note with *what this paper does not settle for us*. It is where the next question comes
from, and it is what stops a note being read as broader than it is.

### Pass 5 — rewrite the objective from the notes

Give each claim an evidence section pointing at a note **that existed before the sentence did**. Then
write *what is not claimed*, which is largely assembled from the notes' *does not settle* sections,
and the table naming which `c_*` or `r_*` column carries each half.

**Watch for design decisions that came out of the reading.** They are the return on this step, and
they belong in `JOURNAL_1.md` with the citation that caused them. If the reading changed nothing about
the design, either it was too shallow or it was done to confirm.

## The stopping condition

Step 1 is finished when:

- every claim in `OBJECTIVE.md` has an evidence section pointing at a note, or says plainly that it
  rests on nothing yet;
- at least one source argues against the strategy and is recorded doing so;
- every citation resolves to a real, checked record;
- *what is not claimed* covers what a reader would otherwise assume;
- the open threads — the unread counterweight, the claim resting on a lead — are written in
  `JOURNAL_1.md` rather than carried in somebody's head.

**It is not finished when the folder is large.** Six notes that argue with each other beat twenty that
agree.

## What must not be started here

Step 2, the universe. **Do not choose a universe, download anything, or write a rule while doing step
1.** The objective is written before anything is measured, and a claims table assembled after a number
exists is an observation wearing a hypothesis's clothes.

## A worked example

The `example` branch of `KaxaNuk/KaxaNuk-Research-Process` carries one: **`liquid-momentum`**, the
most heavily traded stocks with a positive twelve-month return, equally weighted. Six notes, two of
which argue against the strategy, and three design decisions that came out of the reading rather than
the idea — the one-month skip, momentum living in the Refinery, and the liquidity screen worded as a
cost. Read `OBJECTIVE.md`, `Bibliotheca/BIBLIOGRAPHY.md` and the second entry of
`Experiments/Experiment_1/JOURNAL_1.md` together.
