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
runs N MCQ trials against it, gives full breakdowns after every response, then
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
MCQ_PROMPT  = /mnt/skills/user/mcq-probe/prompts/MCQ_GENERATION_PROMPT.md
MSQ_PROMPT  = /mnt/skills/user/mcq-probe/prompts/MSQ_GENERATION_PROMPT.md
```

---

## Active Constraints

These are binding. They do not yield to judgment calls.

- Load `MCQ_PROMPT` and `MSQ_PROMPT` on Trial 1, before any trial is generated. If either is unreadable: halt — REQ-MCQ-E-001.
- Call `SCRIPT_TYPE` before every trial to determine the question type (mcq or msq).
- Call `SCRIPT_AXIS` before every trial. Pass all axes used so far as `--exclude`, in order used.
- Generate one trial at a time. Present it. Wait for response. Evaluate. Then call the scripts for the next trial's type and axis.
- After each trial: generate the **Probe Target** descriptor internally (≤6 words). Never reveal it during the trial — it appears only in the report.
- Run all N trials regardless of intermediate performance. No early termination.
- Do not display trial numbers, scores, or running totals to the learner during the trial loop.
- After trial N — or if the learner requests the report early — run the analysis phase and output the report.

---

## Intake Phase

Execute steps I1 through I4 in order. Do not batch them.

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
        "label": "8",
        "description": "Eight trials — full axis set."
      }
    ]
  }]
}
```

"Other" captures any custom integer. If the learner enters a value outside 1–8,
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

"Other" captures any custom domain. Store as DOMAIN. Pass to MCQ_PROMPT and MSQ_PROMPT for
stem construction.

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

---

## Trial Loop

Execute for each trial 1 through N.

### 1. Question type selection

Invoke:
```
python SCRIPT_TYPE
```

- Exit code 0: use the printed type (`mcq` or `msq`) for this trial. Store as `QUESTION_TYPE`.
- Exit code non-zero: default to `mcq`. Log the fallback internally — REQ-MCQ-E-003.

### 2. Axis selection

Invoke:
```
python SCRIPT_AXIS --exclude [comma-delimited list of all axes used so far, in order]
```

Omit `--exclude` on Trial 1 (no prior axes).

- Exit code 0: use the printed axis for this trial.
- Exit code 1: pick the first axis from `[recognition, application, failure-diagnosis, boundary-condition, transfer, time, risk, coupling]` not already used this session. Log the fallback internally — REQ-MCQ-E-002.

### 3. Prompt load

Trial 1 only: read `MCQ_PROMPT` and `MSQ_PROMPT`.

If either is unreadable: halt immediately — REQ-MCQ-E-001.

Retain both in context for all subsequent trials. Do not reload.

### 4. Trial construction and presentation

Construct and present the trial per the construction sequence in `MCQ_PROMPT` (if `QUESTION_TYPE` is `mcq`) or `MSQ_PROMPT` (if `QUESTION_TYPE` is `msq`).
The assigned axis is fixed — do not substitute.

### 5. Wait

For MCQ: present **MCQ** on its own line, then the question stem and choices A–D. Stop. Wait for the learner's response.
For MSQ: present **MSQ** on its own line, then the question stem and choices A–E, with the count in the closing prompt. Stop. Wait for the learner's response. Accept any common format (comma-separated, space-separated, written out). Parse as a set of letters — order does not matter.

### 6. Evaluate and deliver breakdown

Apply the MCQ or MSQ response protocol (see below) based on `QUESTION_TYPE`.

### 7. Internal record

Generate the Probe Target descriptor: ≤6 words describing the specific aspect
of the concept this trial tested (e.g., "Failure propagation under concurrent load").
Do not reveal it to the learner.

Record internally:
```
{ trial_number, question_type (mcq/msq), axis, grade (correct/incorrect), probe_target, gap_summary }
```

`gap_summary` is populated only for incorrect responses: the specific claim or
mechanism the learner missed. For MSQ, note which picks were wrong and which correct
answers were missed.

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

## Tangent Handling

If the learner diverts mid-trial to explore a related concept:

1. Note the interruption point: which trial number and what was presented.
2. Engage with the tangent conversationally. Do not run MCQ or MSQ trials on the tangent concept —
   the probe is suspended, not extended.
3. When the learner signals readiness to continue, re-present the interrupted trial from
   the beginning. Do not resume mid-question.

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
| 1 | MCQ / MSQ | [descriptor] | [axis] | ✓ / ✗ | — / [specific failure point] |
```

`Type`: MCQ or MSQ.
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

List all 8 axes. "No" for axes not reached. Grade is "—" for untested axes.

---

### Uncovered Axes

**Always rendered.**

```
## Uncovered Axes
```

For each axis not reached in this session, write one sentence on what it would
probe for this specific concept. If all 8 axes were covered, write: "All axes
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
- **Trial # — [Probe Target] ([axis]) [MCQ/MSQ]**
- Chosen: [letter] for MCQ · [letters] for MSQ (include false positives and false negatives)
- Failure point: [the specific claim or mechanism the chosen answer(s) violated]
- What the correct answer required: [the property that survives projection under the axis]

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

---

## Error Handling

### REQ-MCQ-E-001 — MCQ_PROMPT or MSQ_PROMPT unreadable

Halt immediately. Report:

> "mcq-probe cannot proceed — [filename] is unreadable at [path]. Resolve this before continuing."

Do not attempt to generate trials from memory or internal knowledge. Both prompt
files are required. Their absence is not a degraded mode — it is a halt condition.

### REQ-MCQ-E-002 — SCRIPT_AXIS non-zero exit

Pick the first axis from `[recognition, application, failure-diagnosis, boundary-condition,
transfer, time, risk, coupling]` not already used this session. If all axes have been used,
pick the first that is not the most recently used. Log the fallback internally — do not
expose it to the learner. Present the trial normally.

### REQ-MCQ-E-003 — SCRIPT_TYPE non-zero exit

Default to `mcq` for this trial. Log the fallback internally — do not expose it to the
learner. Present the trial normally.
