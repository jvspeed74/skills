# Plan — #41: Remove Matching (MAT) from main; retain on staging

## Background / context

`mcq-probe` supported four question types: MCQ, MSQ, Ordering (ORD), Matching (MAT). MAT was
added in #3 and immediately strained the interactive UX and the repo difficulty doctrine
(`CLAUDE.md`) — the near-duplicate and orthodox-but-wrong devices do not map cleanly onto
pair-matching. It took three reactive fix PRs (#32, #33, #34) plus an ID-collision cleanup (#40)
and still leaked grid jargon. Separately, Feature C (#8/#9/#10) regressed question quality.

`main` was rewound to `cbf84ac` (#18) — the last-good bundle: interactive per-trial delivery,
pre-#9 prompts, no Feature C. All session work is preserved on the integration branch
`staging/mcq-probe-1.4.0`. This change removes MAT from that rewound `main`.

| Global | Value |
|---|---|
| Base commit | `cbf84ac` (#18) |
| Types before | MCQ, MSQ, ORD, MAT |
| Types after | MCQ, MSQ, ORD |
| Intake steps before / after | I1–I6 / I1–I5 |
| `plugin.json` before / after | `1.0.0` / `1.3.0` |
| Installed cache version | `1.2.5` — re-syncs only on a version **increase** |

Pipeline unchanged: `SCRIPT_TYPE` draws a type per trial, `SCRIPT_AXIS` draws an axis, the
per-type generation prompt constructs the trial, the response protocol grades and delivers the
breakdown, the analysis phase emits the report.

## Problem statement

MAT must leave `main` while remaining recoverable. It is threaded through ~40 sites in `SKILL.md`,
the `TYPES` list of `select_question_type.py`, and its own generation prompt. The removal must keep
the surrounding logic coherent — chiefly the intake type-exclude logic (which combined an `ordering`
gate and a `matching` gate) and the shared prompt-load halt condition (`REQ-MCQ-E-001`, which named
all four prompts).

## Design decisions

| Decision | Resolution |
|---|---|
| Retain MAT code | On `staging/mcq-probe-1.4.0`, not in `main` history-delete. "Exists, just not on main." |
| Intake gate | Delete Step I6 (matchable determination) entirely; intake becomes I1–I5. |
| Exclude logic | Collapse the combined `--exclude ordering,matching` logic to `ordering`-only. |
| `TYPES` | `["mcq", "msq", "ordering"]`. A stray `--exclude matching` now errors as unknown — correct defensive behavior, and no caller passes it after this change. |
| Halt condition | Keep `REQ-MCQ-E-001` for the three remaining prompts; drop the `REQ-MAT-E-001` extension. |
| Version bump | `1.3.0`, past the installed `1.2.5`, so the cache re-syncs to the good content on merge. |
| Pre-existing `REQ-ORD-E-001` dangling ref | Left as-is — predates this change, out of scope (ORD). |

## Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-41-1 | `MATCHING_GENERATION_PROMPT.md` deleted | Delete |
| REQ-41-2 | All MAT sites excised from `SKILL.md`; no `matching`/`MATCHABLE`/`REQ-MAT`/`MAT`/`Step I6` tokens remain | Edit |
| REQ-41-3 | `select_question_type.py` `TYPES = ["mcq","msq","ordering"]`; docstring drops matching | Edit |
| REQ-41-4 | `plugin.json` **and** `marketplace.json` descriptions drop "and Matching"; `plugin.json` version → `1.3.0` | Edit |
| REQ-41-5 | Intake reads I1–I5; exclude logic reads `ordering`-only; `REQ-MCQ-E-001` names the three remaining prompts | Verify |
| REQ-41-6 | Type script never emits `matching`; `--exclude matching` errors | Verify |

## Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-1 | Cache serves stale `1.2.5` | No forward version bump | Live skill stays regressed | **No** — REQ-41-4 → `1.3.0` |
| FM-2 | Orphaned MAT reference | An excision site missed | Incoherent instructions | **No** — grep-to-zero on MAT tokens |
| FM-3 | Stale `--exclude matching` call | A caller passes a removed type | Script errors | **Accepted / defensive** — no caller passes it post-change; erroring beats silent misbehavior |
| FM-4 | Shared halt requirement gutted | Deleting MAT prompt breaks `REQ-MCQ-E-001` for the kept prompts | Load-failure handling lost | **No** — requirement retained for the three prompts |

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Excision misses a site → subtle breakage | Medium | Medium | Mapped ~40 sites + grep-to-zero + type-script functional test + live run |
| R-2 | Blank-line / separator artifacts from block removals | Low | Low | Consecutive-blank-line scan; section-heading structural check |

## Files touched

| Path | Op | What |
|---|---|---|
| `.../prompts/MATCHING_GENERATION_PROMPT.md` | Delete | Remove MAT prompt |
| `.../SKILL.md` | Edit | Excise ~40 MAT sites across all sections; I6 removed; exclude logic ordering-only |
| `.../scripts/select_question_type.py` | Edit | Drop `matching` from `TYPES` + docstring |
| `.claude-plugin/plugin.json` | Edit | Version `1.3.0`, description |
| `.claude-plugin/marketplace.json` | Edit | Description |
| `plans/41-remove-mat-from-main.md` | Create | This doc |

## Open questions

None blocking. `plans/matching-question-type-plan.md` is left in place as design reference — MAT
still exists on `staging/mcq-probe-1.4.0`.

## Implementation order

1. Delete the MATCHING prompt.
2. Excise MAT from `SKILL.md` section by section.
3. Drop `matching` from the type script.
4. Bump `plugin.json` → `1.3.0`; align `marketplace.json` description.
5. Grep-to-zero + blank-line scan + type-script functional test.
6. This plan doc; commit; PR against `main`; HITL review.
7. On merge: reinstall/re-sync plugin at `1.3.0`; run `/mcq-probe <concept>` from a cwd outside the
   repo — interactive MCQ/MSQ/ORD trials, no MAT drawn, no path error.

## Verification

| Check | How |
|---|---|
| No orphan MAT | `grep -rniE 'matching|MATCHABLE|REQ-MAT|matchable' mcq-probe/` → only legit English (`pattern-matching`, `exactly matches`) |
| Structure intact | `SKILL.md` headings: intake ends at I5→Trial Loop; Response Protocol = MCQ/MSQ/Ordering; Error Handling has no REQ-MAT |
| Type draw clean | 60 draws never emit `matching`; `--exclude matching` exits 1 |
| Cache re-sync | Post-merge plugin serves `1.3.0` |
| Live end-to-end | `/mcq-probe` from outside the repo → interactive per-trial delivery + report, no MAT |
