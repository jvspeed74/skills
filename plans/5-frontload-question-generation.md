# Plan: Frontload question generation, batched (#5 — Feature C)

Parent plan. Ships no code of its own. It fixes the batch artifact schema and the phase
restructure that sub-issues **#8** (batch type/axis sequencing), **#9** (explanation-baking),
and **#10** (cross-trial consistency pass) implement against, and that Feature B (#7) later
persists **without redesign**.

## Background / context

| Global | Current | After Feature C |
|---|---|---|
| Generation timing | One trial at a time, interleaved with delivery (Trial Loop steps 1–4 per trial) | All trials in a batch generated before any is presented |
| Batch size | n/a | Full N for bounded sessions; 10 per rolling window for endless mode (#4) |
| Rationale authoring | At delivery, per trial, after the learner answers (Response Protocol) | At generation, baked into the artifact |
| Cross-trial awareness | None — each trial is generated blind to the others | Consistency pass over the full batch before finalizing |
| Artifact location | n/a | **In-context only.** On-disk persistence is #7's job |
| Prompt load | All 4 prompts read on Trial 1, retained for the session | Unchanged by this issue — gating is #6's deliverable |

Post-#18, the skill lives at `mcq-probe/skills/mcq-probe-0-router/SKILL.md`. The Trial Loop
(lines 236–358) and Response Protocol (359–532) are the sections this feature restructures.

**Measured, not estimated.** Plugin always-on cost is ~72 tokens; the router's on-invoke cost is
~8.9k. The ~47k of generation prompts is *not* preloaded — it is read at runtime during the trial
loop. The frequently-cited 56,540 figure is per-session read volume, not preload.

## Problem statement

Generation and delivery are interleaved. Every trial pays generation-time reasoning — axis draw,
scenario construction, distractor authoring, the internal-validation checklist — in the middle of
the delivery loop, and then pays *again* to author the breakdown prose after the learner answers.

Three consequences:

1. **No seam for Feature A.** #6 cannot split Generation from Delivery because no such boundary
   exists. Splitting today would relocate the interleaving into two files rather than separate
   generation-time work from delivery-time work.
2. **Delivery is not low-reasoning, and cannot be made so by relocation alone.** If the artifact
   carries only stem/choices/key, delivery still authors every rationale per trial. The reasoning
   cost would look moved without being moved.
3. **Cross-trial quality is unenforceable.** Each trial is generated blind to the others, so
   repeated scenarios, clustered correct-answer positions, and monotone domain anchors cannot be
   detected — there is nothing to compare against.

## Design decisions

| Decision | Resolution |
|---|---|
| **Axis-fit chicken-and-egg** (resolves an incoherence in #8) | **Two-pass draw.** #8 as written says draw all type+axis "before generating any trial content," but the ordering/matching axis-fit check asks whether an axis can force *this trial's* order — unanswerable before the scenario exists. Pass 1 draws type+axis for every slot. Pass 2 generates content slot by slot; if an ordering/matching slot's axis will not fit, re-draw from axes assigned to no other slot and not already rejected for this slot (up to 3 attempts), then hold-and-reconstruct. Preserves REQ-ORD-E-003 / REQ-MAT-E-003 semantics exactly. #8's "before any content" is thereby softened to **before any delivery** — which is the property Feature C actually needs. |
| **Explanation payload shape** | **Content atoms, not prose narratives.** The correct-answer and incorrect-answer protocols carry identical *content* and differ only in ordering and framing; and the incorrect branch varies by which distractor was chosen, so prose would need one narrative per distractor. Atoms cover every branch with no duplication. See Artifact schema below. |
| Artifact location | **In-context only.** #5 precedes #7, so there is no path constant, no writer script, and no on-disk file. The artifact is internal state, never rendered — same discipline as today's `probe_target` ("Do not reveal it to the learner"). #7 persists this exact structure later. |
| Phase restructure | #5 **creates the seam**: the Trial Loop is restructured into a **Generation Phase** (runs once per batch, produces the artifact) and a **Delivery Loop** (runs per trial, consumes it). Both remain in the single `SKILL.md` — the file split is #6's job, and #5's restructure is what makes that split mechanical. |
| Batch sizing | Parameterized as `BATCH_SIZE`. Bounded sessions set it to N and produce exactly one batch; endless mode (#4) sets it to 10 and repeats. A bounded session is the degenerate one-batch case — no separate mechanism. |
| Consistency-pass granularity | On a collision, regenerate **only the offending trial**, then re-run the pass. Not the whole batch. |
| Sub-issue ordering | #8 and #9 are parallel — #8 touches `SKILL.md`'s Trial Loop, #9 touches the 4 generation prompts, minimal overlap. #10 is a gate that depends on both. |
| First-trial latency | Accepted, per #5. Must be communicated ("Preparing your trials…"), never silent. |

## Artifact schema

The batch artifact. `#7` persists this shape verbatim; `#17` guards it. Field names are binding —
sub-issues must not rename them.

```
batch:
  batch_index: int                  # 0 for a bounded session's only batch
  generated_at: timestamp
  trials:
    - trial_index: int              # position within the batch
      question_type: mcq | msq | ordering | matching
      axis: <one of the 9>          # the finally-used axis, post-refit
      axis_rejected: [<axis>, ...]  # refit attempts, this slot only; NOT session-excluded
      probe_target: str             # <=6 words, internal only
      stem: str
      choices: {...}                # type-specific; see below
      key: ...                      # type-specific
      explanation:
        axis_statement: str                 # "what this axis tests in this scenario", one sentence
        key_survival: str                   # why the correct answer/sequence/pairing survives — mechanism, not conclusion
        distractor_failures:                # one entry per wrong choice; MUST cover every one
          <label>:
            failure: str                    # the specific point where it fails under the axis
            orthodox_but_wrong: bool
            near_duplicate_of: <label>|null
        near_duplicate_differentiator: str|null   # what separates the pair, and why it is decisive under the axis
```

Type-specific `choices`/`key`:

| Type | `choices` | `key` |
|---|---|---|
| mcq | A–D | one label |
| msq | A–E | set of labels |
| ordering | pool of labels; K disclosed, D hidden | ordered list of labels |
| matching | `1…n` prompts + `A…m` responses | injective prompt→response map |

**Coverage rule.** `distractor_failures` must have an entry for **every** wrong choice — all 3 for
MCQ, every unselected choice for MSQ, every distractor for Ordering/Matching. A missing entry is a
construction defect: delivery would have to author that rationale live, which is exactly the cost
this feature exists to move.

## Requirements

| ID | Requirement | Sub-issue |
|---|---|---|
| REQ-C-001 | A Generation Phase produces the full batch artifact before any trial is presented | #8 |
| REQ-C-002 | Pass 1 draws type+axis for all `BATCH_SIZE` slots, honoring the I5/I6 gates and the no-reuse-within-session axis rule | #8 |
| REQ-C-003 | Pass 2 generates content per slot; ordering/matching axis refit runs here, re-drawing only from axes assigned to no other slot, up to 3 attempts, then hold-and-reconstruct | #8 |
| REQ-C-004 | A rejected axis is not added to the session's used-axes list; it stays available to other slots | #8 |
| REQ-C-005 | Each generation prompt emits the `explanation` atoms alongside stem/choices/key | #9 |
| REQ-C-006 | `distractor_failures` covers every wrong choice, with `orthodox_but_wrong` and `near_duplicate_of` flagged | #9 |
| REQ-C-007 | Generation output is internal — never rendered to the learner | #9 |
| REQ-C-008 | A consistency pass runs over the finalized batch: no repeated scenario, no clustered correct-answer position, domain-anchor variety | #10 |
| REQ-C-009 | A consistency failure regenerates only the offending trial, then re-runs the pass | #10 |
| REQ-C-010 | The Delivery Loop presents, parses, grades against the stored key, and assembles the breakdown from stored atoms — it authors no new rationale and reads no generation prompt | #8 |
| REQ-C-011 | Batch generation is announced ("Preparing your trials…"), never silent | #8 |

**Non-goals.** No file split (#6). No on-disk persistence (#7). No endless-mode wiring (#4) beyond
parameterizing `BATCH_SIZE`. **No change to the difficulty invariant** — atoms describe distractors
that already had to satisfy `CLAUDE.md`; they do not relax what a distractor must be.

## Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-C-1 | **Distractor softening under baking pressure** | Authoring a failure rationale for every distractor upfront makes weak distractors easier to write than strong ones | Distractors become rejectable on sight — the exact defect `CLAUDE.md` exists to prevent, and the whole premise of the skill collapses | **No.** The internal-validation checklist still gates every trial and runs *before* the consistency pass. Baking is additive: an atom is written *because* a distractor already survives the checklist, never as a substitute for it. Non-delegable review item. |
| FM-C-2 | Artifact rendered to the learner | Generation "outputs" the batch, and output defaults to visible | Full answer key plus rationale leaked before trial 1 — session destroyed | **No** — REQ-C-007. Explicit never-render instruction, mirroring `probe_target`'s existing discipline. |
| FM-C-3 | Incomplete `distractor_failures` | Generator writes atoms for the interesting distractors only | Delivery silently authors the missing rationale live; the reasoning cost never actually moved and the regression is invisible | **No** — REQ-C-006 coverage rule, checked in the consistency pass. |
| FM-C-4 | Axis pool exhaustion during pass-2 refit | An ordering/matching slot needs a refit but every unassigned axis is taken by another slot | No axis available to re-draw; the slot stalls | Accepted — falls through to hold-and-reconstruct, which is the existing terminal behavior and always succeeds. |
| FM-C-5 | Upfront latency reads as a hang | Batch of 10 with full validation per trial, no output meanwhile | Learner assumes the session broke | Accepted with REQ-C-011's announcement. |
| FM-C-6 | Consistency-pass regeneration loop | Regenerated trial keeps colliding | Unbounded regeneration | **No** — cap at 3 regenerations per slot, then accept the trial and log internally. Mirrors the existing 3-attempt refit convention. |
| FM-C-7 | Batch context growth | 10 trials × (stem + choices + full atom set) held in context | Context pressure well before the report | Accepted for now; #7's persistence is the structural fix. Flag if a 10-batch measures beyond ~15k tokens. |

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-C-1 | A subagent treats "bake the explanation" as license to simplify distractors (FM-C-1) | Medium | **High** | Every #9 brief quotes `CLAUDE.md`'s invariant verbatim; every distractor change is reviewed against it before the PR opens. Non-delegable. |
| R-C-2 | Atom schema drifts across the 4 prompts | Medium | Medium | Field names in Artifact schema above are binding. #9 applies one shape to all four prompts; divergence is a review reject. |
| R-C-3 | Two-pass draw is read as licence to defer the axis draw entirely into pass 2 | Medium | Medium | REQ-C-002 is explicit: pass 1 draws **all** slots. Pass 2 refits only ordering/matching slots that fail their fit check. |
| R-C-4 | Schema churn once #7 needs to persist it | Low | Medium | Schema authored here against #7's stated shape (`batches[]`, `current_batch_index`, `trials_remaining_in_batch`), so #7 wraps it rather than reshaping it. |

## Files touched

Nothing in this PR beyond this document. Sub-issue scope, for traceability:

| File | Sub-issue | What |
|---|---|---|
| `.../mcq-probe-0-router/SKILL.md` | #8 | Restructure Trial Loop → Generation Phase + Delivery Loop; two-pass draw; `BATCH_SIZE`; announcement |
| `.../prompts/{MCQ,MSQ,ORDERING,MATCHING}_GENERATION_PROMPT.md` | #9 | Output step emits `explanation` atoms; internal-only discipline |
| `.../mcq-probe-0-router/SKILL.md` | #10 | Consistency pass + regeneration cap |
| `mcq-probe/.claude-plugin/plugin.json` | each | **Version bump required** — the plugin installs as a versioned cache copy and does not re-sync without one |
| `plans/{8,9,10}-*.md` | each | Sub-issue plan docs, one per PR |

## Open questions

| # | Question | Blocker for? |
|---|---|---|
| 1 | Does a 10-trial batch with full atoms fit comfortably in context alongside the 4 generation prompts? (FM-C-7) | Nothing in #5; measure during #8 and report before #4 sets endless windows live |

## Implementation order

1. This plan doc lands first, as its own PR — #8 and #9 run in parallel and both build against it.
2. **#8** — Generation Phase / Delivery Loop restructure and the two-pass draw. Establishes the artifact.
3. **#9** — in parallel with #8; touches only the 4 generation prompts.
4. **#10** — after both; the consistency pass needs a populated batch to check.
5. Measure a 10-trial batch and close open question 1.
