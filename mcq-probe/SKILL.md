---
name: mcq-probe
description: >
  Standalone MCQ evaluation skill. Runs N trials on a learner-specified concept,
  delivers full per-trial breakdowns without coaching, and outputs a diagnostic
  Markdown report after all trials complete. No session state, no re-teach loop,
  no phase dependencies.
user-invocable: true
argument-hint: "[concept]"
---

# MCQ Probe

A self-contained evaluation tool. The learner specifies a concept; the skill
runs N trials against it — a mix of multiple-choice (MCQ), multiple-select (MSQ),
and ordering (ORD) — gives full breakdowns after every response, then
produces a diagnostic Markdown report. There is no coaching, no nudging, and no
routing to other skills. The output is an unvarnished picture of what the learner
does and does not understand.

---

## File Path Constants

```
# Invoke via: python [SCRIPT_TYPE]
SCRIPT_TYPE = /mnt/skills/user/mcq-probe/scripts/select_question_type.py

# Invoke via: python [SCRIPT_AXIS] [args]
SCRIPT_AXIS = /mnt/skills/user/mcq-probe/scripts/select_mcq_axis.py

# Read via the Read tool
MCQ_PROMPT      = /mnt/skills/user/mcq-probe/prompts/MCQ_GENERATION_PROMPT.md
MSQ_PROMPT      = /mnt/skills/user/mcq-probe/prompts/MSQ_GENERATION_PROMPT.md
ORDERING_PROMPT = /mnt/skills/user/mcq-probe/prompts/ORDERING_GENERATION_PROMPT.md
```

---

## Active Constraints

These are binding. They do not yield to judgment calls.

- Load `MCQ_PROMPT`, `MSQ_PROMPT`, and `ORDERING_PROMPT` on Trial 1, before any trial is generated. If any is unreadable: halt — REQ-MCQ-E-001.
- Call `SCRIPT_TYPE` before every trial to determine the question type (mcq, msq, or ordering). If Step I5 determined the concept is non-procedural, pass `--exclude ordering` on every call this session — REQ-ORD-F-010.
- Call `SCRIPT_AXIS` before every trial. Pass all axes used so far as `--exclude`, in order used.
- For an ordering trial, if the assigned axis cannot force the trial's order, re-draw via `SCRIPT_AXIS` (excluding used + rejected axes), up to 3 attempts; on exhaustion, hold the axis and reconstruct the scenario. Never substitute the trial type — REQ-ORD-E-003.
- Generate one trial at a time. Present it. Wait for response. Evaluate. Then call the scripts for the next trial's type and axis.
- After each trial: generate the **Probe Target** descriptor internally (≤6 words). Never reveal it during the trial — it appears only in the report.
- Run all N trials regardless of intermediate performance. No early termination.
- Do not display trial numbers, scores, or running totals to the learner during the trial loop.
- After trial N — or if the learner requests the report early — run the analysis phase and output the report.

---

## Intake Phase

Execute steps I1 through I5 in order. Do not batch them.

### Step I1 — Concept (conversational)

If a concept was provided at invocation (e.g., `/mcq-probe TCP congestion control`),
use it as the concept definition and skip this step.

Otherwise, ask: "What concept should I probe you on? Describe it." Wait for the
learner's response before proceeding.

The concept definition is used throughout the session — it informs stem construction,
axis applicability, and the Uncovered Axes section of the report.

### Step I2 — Trial count (AskUserQuestion)

Invoke AskUserQuestion with:

```json
{
  "questions": [{
    "question": "How many trials?",
    "header": "Trial count",
    "multiSelect": false,
    "options": [
      {
        "label": "3",
        "description": "Three trials — covers three distinct axes."
      },
      {
        "label": "5",
        "description": "Five trials — broader axis coverage."
      },
      {
        "label": "9",
        "description": "Nine trials — full axis set."
      }
    ]
  }]
}
```

"Other" captures any custom integer. If the learner enters a value outside 1–9,
ask them to choose a value in that range. Store as N.

### Step I3 — Domain preference (AskUserQuestion)

Invoke AskUserQuestion with:

```json
{
  "questions": [{
    "question": "Which domain should scenarios be anchored to?",
    "header": "Domain",
    "multiSelect": false,
    "options": [
      {
        "label": "Aviation",
        "description": "NTSB causal chains, flight envelope, MRO operations."
      },
      {
        "label": "Motorsport",
        "description": "F1 telemetry, tire model, race strategy, vehicle dynamics."
      },
      {
        "label": "Abstract",
        "description": "No physical anchor — pure conceptual framing."
      },
      {
        "label": "No preference",
        "description": "Select the domain that fits the concept most naturally."
      }
    ]
  }]
}
```

"Other" captures any custom domain. Store as DOMAIN. Pass to MCQ_PROMPT, MSQ_PROMPT, and
ORDERING_PROMPT for stem construction.

### Step I4 — Specific focus (AskUserQuestion)

Invoke AskUserQuestion with:

```json
{
  "questions": [{
    "question": "Any specific claims or failure modes to prioritize?",
    "header": "Focus",
    "multiSelect": false,
    "options": [
      {
        "label": "Yes — I'll describe them",
        "description": "You'll specify what to probe after this."
      },
      {
        "label": "No — cover the concept broadly",
        "description": "Axes are selected freely across the concept's full scope."
      }
    ]
  }]
}
```

If "Yes": follow up conversationally — "Describe the claims or failure modes you
want prioritized." Store the stated focus areas and weight axis selection and stem
construction toward them where applicable.

### Step I5 — Procedural determination (internal)

Once the concept is defined (Step I1), determine once whether it affords an ordered,
dependency-bearing procedure — a task whose correct completion is a sequence of steps
with a forced order, not just a set of parallel facts, tradeoffs, or independent
choices. This is an internal judgment call made by the orchestrator; do not ask the
learner.

Store the result as `PROCEDURAL` (yes/no) — REQ-ORD-F-010.

- If **no**: `ordering` is excluded from the type draw for the remainder of the
  session. Call `SCRIPT_TYPE` with `--exclude ordering` on every trial this session,
  so `ordering` is never drawn.
- If **yes**: no exclusion is applied at intake. A trial-level axis re-draw may still
  apply once an `ordering` trial is drawn — see Trial Loop, Step 2.

---

## Trial Loop

Execute for each trial 1 through N.

### 1. Question type selection

Invoke:
```
python SCRIPT_TYPE
```

If Step I5 determined the concept is non-procedural (`PROCEDURAL` = no), invoke
instead:
```
python SCRIPT_TYPE --exclude ordering
```

- Exit code 0: use the printed type (`mcq`, `msq`, or `ordering`) for this trial. Store as `QUESTION_TYPE`.
- Exit code non-zero: default to `mcq`. Log the fallback internally — REQ-MCQ-E-003.

### 2. Axis selection

Invoke:
```
python SCRIPT_AXIS --exclude [comma-delimited list of all axes used so far, in order]
```

Omit `--exclude` on Trial 1 (no prior axes).

- Exit code 0: use the printed axis for this trial.
- Exit code 1: pick the first axis from `[recognition, application, failure-diagnosis, boundary-condition, transfer, time, risk, coupling, observability]` not already used this session. Log the fallback internally — REQ-MCQ-E-002.

**Ordering axis re-draw (REQ-ORD-E-003, REQ-ORD-F-016).** If `QUESTION_TYPE` is
`ordering`, confirm — per `ORDERING_PROMPT`'s axis-fit check — that the assigned axis
can force this trial's order. If it cannot:

1. Re-draw: `python SCRIPT_AXIS --exclude [axes used so far this session, in order] + [axes rejected for this trial]`.
2. A rejected axis is **not** added to the session's used-axes list — it stays
   available to later trials. Track it as rejected only for this trial's re-draw
   attempts.
3. Repeat up to 3 re-draw attempts total for this trial.
4. If all 3 attempts are exhausted without a fitting axis, hold the last-drawn axis
   and reconstruct the scenario (per `ORDERING_PROMPT`) to one that axis can force.
   Do not substitute the trial type.

Once the axis is settled (fit confirmed, or held after exhaustion), it is the
**finally-used axis** for this trial — it, and only it, enters the session's
axis-exclusion list (the `--exclude` argument on later trials) and the report's
Axis Coverage.

### 3. Prompt load

Trial 1 only: read `MCQ_PROMPT`, `MSQ_PROMPT`, and `ORDERING_PROMPT`.

If any is unreadable: halt immediately — REQ-MCQ-E-001 / REQ-ORD-E-001.

Retain all three in context for all subsequent trials. Do not reload.

### 4. Trial construction and presentation

Construct and present the trial per the construction sequence in `MCQ_PROMPT` (if `QUESTION_TYPE` is `mcq`), `MSQ_PROMPT` (if `QUESTION_TYPE` is `msq`), or `ORDERING_PROMPT` (if `QUESTION_TYPE` is `ordering`).
The assigned axis is fixed once settled per Step 2 — do not substitute further.

### 5. Wait

For MCQ: present **MCQ** on its own line, then the question stem and choices A–D. Stop. Wait for the learner's response.
For MSQ: present **MSQ** on its own line, then the question stem and choices A–E, with the count in the closing prompt. Stop. Wait for the learner's response. Accept any common format (comma-separated, space-separated, written out). Parse as a set of letters — order does not matter.
For Ordering: present **ORD** on its own line, then the task scenario, the pool with one label per line, and a closing prompt disclosing K (the number of steps to arrange) but not D (the number of distractors). Stop. Wait for the learner's response. Accept any common format (comma-separated, space-separated, arrow-separated, numbered list), case-insensitive. Parse as an **ordered** list of labels — order is significant. An out-of-pool label or a repeated label is invalid: ask the learner to resubmit; do not count the attempt — REQ-ORD-E-002.

### 6. Evaluate and deliver breakdown

Apply the MCQ, MSQ, or Ordering response protocol (see below) based on `QUESTION_TYPE`.
For Ordering: correct iff the learner's ordered selected sequence exactly equals the
correct sequence — the right steps, no distractors, none missing, exact order —
REQ-ORD-F-007.

### 7. Internal record

Generate the Probe Target descriptor: ≤6 words describing the specific aspect
of the concept this trial tested (e.g., "Failure propagation under concurrent load").
For Ordering, the descriptor names the procedure aspect tested (e.g., "Dual-write
ordering before backfill"). Do not reveal it to the learner.

Record internally:
```
{ trial_number, question_type (mcq/msq/ordering), axis, grade (correct/incorrect), probe_target, gap_summary }
```

`gap_summary` is populated only for incorrect responses: the specific claim or
mechanism the learner missed. For MSQ, note which picks were wrong and which correct
answers were missed. For Ordering, note the false inclusions, the omissions, and the
transposed pairs — REQ-ORD-F-009.

---

## Response Protocol

### MCQ — Correct answer

1. Acknowledge briefly: "Correct." / "Right." / "That's it."
2. State the axis: "The axis here is [axis]: [one sentence on what it tests in this scenario]."
3. Explain why the correct answer survives under the axis — the mechanism, not just the conclusion.
4. Address each wrong answer individually: the specific point where it fails and why.
   If a wrong answer is the orthodox-but-wrong choice, name it: "X is the orthodox approach
   here — professionally sound in many contexts — but under [axis], it fails because [mechanism]."
5. If the near-duplicate pair was a factor, explain what differentiates the two choices and
   why that difference is decisive under the axis.
6. Proceed immediately to the next trial. If this was trial N, proceed to the Analysis Phase instead.

### MCQ — Incorrect answer

1. State the axis first: "The axis here is [axis]: [one sentence]."
2. Explain the failure: which property of the chosen answer is the problem, why it fails under
   forward projection, what the axis was testing that the answer missed.
3. State the correct answer directly.
4. Explain why the correct answer survives.
5. Address all three wrong answers individually — the same full coverage as the correct-answer
   protocol. Name the orthodox-but-wrong choice if present. Explain the near-duplicate
   differentiator if applicable.
6. Proceed to the next trial. If this was trial N, proceed to the Analysis Phase instead.

**No nudge. No recovery exchanges.** This is an evaluation.

---

### MSQ — Correct answer

A response is correct when the learner's selected set exactly matches the set of correct
answers — no extra picks, no missed picks.

1. Acknowledge briefly: "Correct." / "Right." / "That's it."
2. State the axis: "The axis here is [axis]: [one sentence on what it tests in this scenario]."
3. Explain why each correct answer survives under the axis — address each individually.
4. Address each wrong answer individually: the specific point where it fails and why.
   Name each orthodox-but-wrong choice explicitly: "X is the orthodox approach here —
   professionally sound in many contexts — but under [axis], it fails because [mechanism]."
5. If similarity-structured choices were a factor, explain what differentiates the similar
   choices and why that difference is decisive under the axis.
6. Proceed immediately to the next trial. If this was trial N, proceed to the Analysis Phase instead.

### MSQ — Incorrect answer

A response is incorrect when the learner's selected set differs from the correct set in any
way — a wrong pick included, a correct pick missed, or both.

1. State the axis first: "The axis here is [axis]: [one sentence]."
2. Explain the failure for each discrepancy individually:
   - For each letter the learner selected that was wrong: which property fails under the axis
     and why, what the axis was testing that this pick missed.
   - For each correct letter the learner did not select: why it survives projection under the
     axis, what property it has that the learner's selection lacked.
3. State the correct set directly: "The correct answers are [letters]."
4. Explain why each correct answer survives under the axis — each individually.
5. Address all wrong answers individually — the same full coverage as the correct-answer
   protocol. Name each orthodox-but-wrong choice. Explain similarity differentiators if applicable.
6. Proceed to the next trial. If this was trial N, proceed to the Analysis Phase instead.

**No nudge. No recovery exchanges.** This is an evaluation.

---

### Ordering — Correct answer

A response is correct when the learner's ordered selected sequence exactly matches
the correct sequence — the right steps, none missing, no distractors included, in
the exact forced order.

1. Acknowledge briefly: "Correct." / "Right." / "That's it."
2. State the axis: "The axis here is [axis]: [one sentence on what it tests in this scenario]."
3. Explain why the sequence survives — address each forced precedence individually:
   why that adjacency is forced under the axis.
4. Address each distractor individually: the specific point where it fails selection
   and why. Name the orthodox-but-wrong inclusion explicitly: "X is the orthodox
   approach here — professionally sound in many contexts — but under [axis], it fails
   because [mechanism]."
5. Resolve the order-sensitive pairs: why the reverse order fails under projection.
   If a near-duplicate distractor was a factor, explain what one phrase differentiates
   the correct step from its twin and why that difference is decisive under the axis.
6. Proceed immediately to the next trial. If this was trial N, proceed to the Analysis Phase instead.

### Ordering — Incorrect answer

A response is incorrect when the learner's ordered selected sequence differs from the
correct sequence in any way — a distractor included, a correct step omitted, a
correct step out of order, or any combination.

1. State the axis first: "The axis here is [axis]: [one sentence]."
2. Decompose the error into its two error classes, each addressed individually:
   - **Selection errors** — for each distractor the learner included, why it fails
     selection under the axis and what the axis was testing that this pick missed.
     For each correct step the learner omitted, why it belongs — why it survives
     projection.
   - **Ordering errors** — for each transposed pair among the steps the learner did
     select correctly, why that adjacency is forced under the axis and why the
     learner's order fails projection.
3. State the correct sequence directly: `X → Y → Z → W`.
4. Explain why the correct sequence survives — each forced precedence individually.
5. Address all distractors individually — the same full coverage as the correct-answer
   protocol. Name the orthodox-but-wrong inclusion. Resolve the near-duplicate pair —
   what one phrase differentiates the twins.
6. Proceed to the next trial. If this was trial N, proceed to the Analysis Phase instead.

**No nudge. No recovery exchanges.** This is an evaluation.

---

## Tangent Handling

If the learner diverts mid-trial to explore a related concept:

1. Note the interruption point: which trial number and what was presented.
2. Engage with the tangent conversationally. Do not run MCQ, MSQ, or Ordering trials on
   the tangent concept — the probe is suspended, not extended.
3. When the learner signals readiness to continue, re-present the interrupted trial from
   the beginning. Do not resume mid-question. For an Ordering trial, any re-presentation
   — after a tangent or after a clarification exchange — uses the same pool and the same
   labels: no re-shuffle, no regeneration — REQ-ORD-F-015.

---

## Analysis Phase

Triggered automatically after trial N. Also triggered immediately if the learner
requests the report before trial N — in that case, run analysis on however many
trials have completed.

### Pass threshold

At most ⌊N/3⌋ incorrect answers to pass.

| N | Max incorrect |
|---|---|
| 3 | 1 |
| 5 | 1 |
| 6 | 2 |
| 8 | 2 |
| 9 | 3 |

### Pattern analysis (internal — runs before report output)

**Surface gap indicators:**
- Errors concentrated on scenario misreads, not concept misapplication
- Correct on most trials; single error with a reasonable axis misread explanation
- Errors on axis identification but not on concept mechanics — the learner chose a
  valid approach that failed only under this specific axis

**Fundamental gap indicators:**
- Errors across multiple trials targeting different axes — concept itself is not seated
- Consistent wrong mental model recurring across trials
- Errors not explainable by axis misread — chosen answers suggest a core misconception

Determine surface or fundamental gap from the evidence. This classification populates
the Classification section of the report.

---

## Report Format

Output as a single Markdown document. Render sections conditionally as specified.

---

### Summary

**Always rendered.**

```
## Summary
**Concept:** [concept as described during intake]
**Trials:** [N completed] / [N total]
**Result:** Pass / Fail
**Threshold:** at most [⌊N/3⌋] incorrect to pass
```

---

### Trial Log

**Always rendered.**

```
## Trial Log
| # | Type | Probe Target | Axis | Grade | Gap |
|---|---|---|---|---|---|
| 1 | MCQ / MSQ / ORD | [descriptor] | [axis] | ✓ / ✗ | — / [specific failure point] |
```

`Type`: MCQ, MSQ, or ORD.
`Grade`: ✓ for correct, ✗ for incorrect.
`Gap`: populated only for incorrect responses — the specific claim or mechanism missed.
`Probe Target`: the ≤6-word descriptor generated after each trial.

---

### Axis Coverage

**Always rendered.**

```
## Axis Coverage
| Axis | Tested | Grade |
|---|---|---|
| recognition | Yes / No | ✓ / ✗ / — |
```

List all 9 axes. "No" for axes not reached. Grade is "—" for untested axes.

---

### Uncovered Axes

**Always rendered.**

```
## Uncovered Axes
```

For each axis not reached in this session, write one sentence on what it would
probe for this specific concept. If all 9 axes were covered, write: "All axes
covered this session."

---

### Strength Profile

**Rendered when ≥1 correct.**

```
## Strength Profile
```

Per correct trial: state what held and why the mechanism was sound. This is not
affirmation — it is a precise account of which claim or property the learner
correctly projected forward and why that projection was valid.

---

### Gap Inventory

**Rendered when ≥1 incorrect.**

```
## Gap Inventory
```

Per incorrect trial, a structured entry:

For MCQ / MSQ:
- **Trial # — [Probe Target] ([axis]) [MCQ/MSQ]**
- Chosen: [letter] for MCQ · [letters] for MSQ (include false positives and false negatives)
- Failure point: [the specific claim or mechanism the chosen answer(s) violated]
- What the correct answer required: [the property that survives projection under the axis]

For Ordering (REQ-ORD-F-017):
- **Trial # — [Probe Target] ([axis]) [ORD]**
- Chosen sequence: [ordered list of labels as submitted]
- Correct sequence: [ordered list of labels]
- Selection errors: [false inclusions — distractors picked; omissions — correct steps missed], decomposed, or "none"
- Ordering errors: [transposed forced pairs among the correctly-selected steps], decomposed, or "none"

---

### Error Pattern

**Rendered when ≥2 incorrect.**

```
## Error Pattern
```

Cross-trial analysis: is there a shared root misconception or recurring failure
mode across the incorrect trials? If yes, name it precisely — the specific claim
or mental model that is producing the errors. If the errors are independent (each
has a distinct root), state that.

---

### Classification

**Rendered when ≥1 incorrect.**

```
## Classification
```

State the determination: **Surface gap** or **Fundamental gap**.

Surface gap: the learner has the concept — errors are traceable to scenario
misreads or axis misidentification, not to a broken mental model of the concept.

Fundamental gap: the error pattern reveals that the core concept is not seated.
State which specific claim or property is at issue and cite evidence from the
trial results.

For Ordering trials, apply this additionally (REQ-ORD-F-018): a transposition among
an otherwise correctly-selected set of steps reads as a **surface gap** — the learner
has the procedure but slipped on one forced adjacency. Repeated selection of the
orthodox-but-wrong inclusion, or errors spanning both selection and ordering across
trials, reads as a **fundamental gap**.

---

## Error Handling

### REQ-MCQ-E-001 — MCQ_PROMPT, MSQ_PROMPT, or ORDERING_PROMPT unreadable

Halt immediately. Report:

> "mcq-probe cannot proceed — [filename] is unreadable at [path]. Resolve this before continuing."

Do not attempt to generate trials from memory or internal knowledge. All three prompt
files are required. Their absence is not a degraded mode — it is a halt condition.

### REQ-MCQ-E-002 — SCRIPT_AXIS non-zero exit

Pick the first axis from `[recognition, application, failure-diagnosis, boundary-condition,
transfer, time, risk, coupling, observability]` not already used this session. If all axes
have been used, pick the first that is not the most recently used. Log the fallback
internally — do not expose it to the learner. Present the trial normally.

### REQ-MCQ-E-003 — SCRIPT_TYPE non-zero exit

Default to `mcq` for this trial. Log the fallback internally — do not expose it to the
learner. Present the trial normally.

### REQ-ORD-E-002 — Invalid ordering response

An out-of-pool label, a repeated label, or a response that cannot be parsed as an
ordered list is invalid. Ask the learner to resubmit. Do not count the attempt against
the trial — the trial is still awaiting a valid response.

### REQ-ORD-E-003 — Ordering axis re-draw

If the assigned axis cannot force the current ordering trial's order, re-draw via
`SCRIPT_AXIS --exclude [axes used this session] + [axes rejected for this trial]`, up
to 3 attempts. A rejected axis is not added to the session's used-axes list — it
remains available to later trials. If all 3 re-draw attempts are exhausted, hold the
last-drawn axis and reconstruct the scenario to one it can force. Never substitute the
trial type mid-trial. Only the finally-used axis enters the session's axis-exclusion
list and the report's Axis Coverage — REQ-ORD-F-016.
