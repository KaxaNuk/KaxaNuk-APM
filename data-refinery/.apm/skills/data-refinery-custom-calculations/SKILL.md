---
name: data-refinery-custom-calculations
description: >
  Load this skill whenever you author, modify, review or debug an `r_*` column or the refinery
  driver of a KN Research Process repository — `Data/Refinery/custom_calculations.py` and
  `Data/refinery.py`, step 3 block 2. Use it when the user asks for a rank, a breadth reading, a
  per-date z-score, a fitted per-security model, a `current_*` classification join, when a refined
  column is all-null or drifts, when stale refined files appear, or when the KaxaNuk Data Refinery
  library is to replace the hand-rolled stage. It covers the two kinds of column that belong here,
  the parameter-name contract, causality, the rank identity, membership from the seed, and the seam
  the library swaps into. It does NOT cover `c_*` columns (use `data-curator-custom-calculations`),
  screening a feature for signal (use `data-analyzer-signal-screening`), or the research process
  around the stage (use `experiment-lifecycle`).
metadata:
  version: 0.1.0
---

# The Data Refinery — the cross-section, the join, and the seam

The Curator sees one security at a time; the Refinery sees all of them on one date. It stacks every
Curator file into one panel, computes the `r_*` columns across it, joins the security master, and
writes the files back out with the same rows and more columns:

```
Data/Curator/Time_Series/<id>.csv      m_* + c_*                       per security
        |
        v   stack, compute per date across the cross-section, join the master
Data/Refinery/Time_Series/<id>.csv     m_* + c_* + current_* + r_*     same rows, more columns
```

`Data/Refinery/Time_Series/` is **the panel every experiment reads**. Nothing downstream recomputes
a column it carries: an experiment that re-derives a rank has broken the process even when the
number matches, because the next experiment derives it slightly differently and the two stop being
comparable.

It runs after `Universe/universe.ipynb`, because it joins the security master that notebook writes,
and before `Data/analyzer.ipynb`, which reads what it writes. Run too early it says which columns it
is skipping and carries on — the right behaviour and the wrong outcome.

## 1. Two kinds of column live here, and only here

1. **Anything that compares securities against each other on a date** — a rank, a breadth reading,
   a share of the cross-section, a per-date z-score. No per-security calculation can express it, so
   it cannot be a `c_*` column.
2. **Anything with a fitted parameter, even when it is per-security.** A model has settings an
   experiment will sweep, and widening the Curator's schema refetches every identifier. **A sweep
   must never cost a download**, so the model's frozen arithmetic inputs stay in the Curator and the
   model itself lives here.

The corollary: a `c_*` column that needs to see other securities is misplaced, and a per-security
column with nothing to tune belongs in the Curator. The template's example branch keeps its jump
model in `Data/Refinery/jump_model.py`, fitted per asset with a penalty the experiments sweep, over
Curator columns that are arithmetic on one price series.

## 2. The contract — one function per column, resolved by name

Exactly the convention the Curator uses, so a person who has written one has written both:

- **One function per column, named exactly as the column**, and the column is registered by listing
  it in the module's output tuple. Nothing else registers it.
- **Every parameter is a column of the panel** — the date, `main_identifier`, any `c_*` or `r_*`
  column, any `current_*` column — and the driver resolves the dependency order from the
  signatures. Definition order is irrelevant; a parameter named `r_trend_strength` receives the
  output of the function of that name.
- **Every parameter is a `pandas.Series` aligned to the panel's index**, and the function returns
  a Series of the same length. A function that needs to group by date or by identifier groups by the
  column it was handed.
- **A parameter that is never satisfied is a hard error**, not a silently missing column. An absent
  input almost always means a typo in a parameter name.

```python
def r_liquidity_rank(
    m_date: pandas.Series,
    c_daily_traded_value_63d: pandas.Series,
) -> pandas.Series:
    """Per-date percentile rank of average daily traded value; 1.0 is the most traded name."""

    return c_daily_traded_value_63d.groupby(m_date).rank(pct=True)
```

Columns that read a `current_*` column are listed separately, in a classification-dependent
tuple, so the driver can skip them — and say so — before the security master exists.

## 3. Causality, the rule this stage exists to enforce

- **Every cross-sectional column on date t uses only the cross-section as of t.** Rank, normalise
  and average per date, over that date's names only. A z-score over the pooled sample, or a rank
  over the whole history, leaks the future distribution into every row and raises no error.
- **Every rolling window looks strictly backward**, grouped by identifier so the first row of one
  security never differences against the last row of another in the stacked panel.
- **A fitted model is used in its causal form**, and the smoothed form only where it is labelled as
  not tradable. Measure the gap between the two before decomposing any fitted signal: on the
  template's example the same jump model read with hindsight showed a good-minus-bad forward return
  of +38.9% and read causally −5.1%, agreeing on 81% of days and differing exactly at the turning
  points. It is one line of code and routinely the largest number in a repository.

## 4. The rank convention, and the identity that checks it

**Every `*_rank` column is a per-date percentile, ascending**: 1.0 is the highest raw value in that
day's cross-section. A percentile is comparable across dates even though the number of names with
data changes; a raw rank of 20 means different things in a 300-name and an 800-name cross-section.

A per-date percentile over *n* untied values has mean exactly `(n + 1) / (2n)` — 0.542 on twelve
securities, 0.5006 on eight hundred. **Check it as an identity, never against 0.5**: a test against
0.5 fails on every date of a narrow universe and passes on a wide one, which is the worst possible
failure mode. `Data/analyzer.ipynb` runs that check; this stage has to make it pass.

## 5. Membership, the join, and the files

- **Membership is an allowlist taken from `Universe/Investable_Universe.csv`**, column
  `main_identifier`. The Curator folder also holds the cash proxy and the benchmarks, because the
  engine prices everything from one directory, and none of them belongs in a cross-section: a
  benchmark ranked against its own constituents is meaningless. Reading membership from the seed
  means there is no second list to forget to update.
- **The security master is joined as `current_*` columns**, one per classification the master
  carries, mapped as `{master column: panel column}`. They are what a security is classified as
  *today*; the provider keeps no history, so every period before a reclassification is attributed
  wrongly, and nothing raises an error. **Group or report by a `current_*` column; never select on
  it.** A column the master does not have is reported and skipped rather than joined in as nulls.
- **Report per-column coverage on every run**, so an all-null column cannot slip past.
- **Delete refined files for identifiers no longer in the seed.** A stale file carries ranks taken
  against a universe that no longer exists, and anything reading the folder would average two
  incompatible cross-sections without raising. Delete by name, and print the name.
- The driver takes `--limit N` for a quick pass and `--dry-run` to compute and report without
  writing; both exist so a new column is tried on fifty files before it is run on eight hundred.

## 6. The seam the library replaces

`Data/refinery.py` is hand-rolled today and says so in its docstring. Keep its contract stable —
Curator files in, `r_*` functions resolved by parameter name, Refinery files out with the same
rows — and swapping in the KaxaNuk Data Refinery library is a one-file change that no notebook
notices. Anything a strategy needs the stage to do that the contract does not express is a
question for the library's issue tracker, not a reason to teach the notebooks about the refinery.

## What this skill will not let you do

- **Put a tunable parameter in the Curator.** It costs a refetch of every identifier per sweep.
- **Rank or normalise over the pooled sample.** Per date, or not at all.
- **Select on a `current_*` column**, or compute a `current_*`-dependent column before the security
  master exists without saying which columns were skipped.
- **Recompute an `r_*` column in a notebook.** If an experiment needs a column, it is added here and
  every experiment gets it.
- **Use an in-house KaxaNuk strategy as a worked example.** Examples in this public package come
  from the template's `example` branch only.
