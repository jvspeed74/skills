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
ordering (ORD), and matching (MAT) — gives full breakdowns after every response,
then produces a diagnostic Markdown report. There is no coaching, no nudging, and no
routing to other skills. The output is an unvarnished picture of what the learner
does and does not understand.

---

## File Path Constants

```
# Invoke via: python [SCRIPT_TYPE]
SCRIPT_TYPE = /mnt/skills/user/mcq-probe/scripts/select_question_type.py

# Invoke via: python [SCRIPT_AXIS] [args]
SCRIPT_AXIS = /mnt/skills/user/mcq-probe/scripts/select_mcq_axis.py

# Invoke via: python [SCRIPT_POSITION] [args]
SCRIPT_POSITION = /mnt/skills/user/mcq-probe/scripts/select_answer_position.py

# Read via the Read tool
MCQ_PROMPT      = /mnt/skills/user/mcq-probe/prompts/MCQ_GENERATION_PROMPT.md
MSQ_PROMPT      = /mnt/skills/user/mcq-probe/prompts/MSQ_GENERATION_PROMPT.md
ORDERING_PROMPT = /mnt/skills/user/mcq-probe/prompts/ORDERING_GENERATION_PROMPT.md
MATCHING_PROMPT = /mnt/skills/user/mcq-probe/prompts/MATCHING_GENERATION_PROMPT.md
```

**Environment note:** The seven paths above are hosted-sandbox (Claude.ai Skills) conventions,
where they are correct and must be used as written. When this skill runs under Claude Code as
part of the `mcq-probe` plugin bundle, resolve all seven relative to `${CLAUDE_PLUGIN_ROOT}`
instead:

- `SCRIPT_TYPE` → `${CLAUDE_PLUGIN_ROOT}/skills/mcq-probe-0-router/scripts/select_question_type.py`
- `SCRIPT_AXIS` → `${CLAUDE_PLUGIN_ROOT}/skills/mcq-probe-0-router/scripts/select_mcq_axis.py`
- `SCRIPT_POSITION` → `${CLAUDE_PLUGIN_ROOT}/skills/mcq-probe-0-router/scripts/select_answer_position.py`
- `MCQ_PROMPT`, `MSQ_PROMPT`, `ORDERING_PROMPT`, `MATCHING_PROMPT` →
  `${CLAUDE_PLUGIN_ROOT}/skills/mcq-probe-0-router/prompts/<same filename>`

Detect the runtime environment once, at the start of the session, and substitute consistently
for the remainder of this skill's execution. Do not mix conventions mid-session. `${CLAUDE_PLUGIN_ROOT}`
is Claude Code's documented plugin-root token; `${CLAUDE_SKILL_DIR}` is a hosted-sandbox token and
is not confirmed to resolve under Claude Code — do not substitute it here.

The `python` in `# Invoke via: python [SCRIPT_TYPE]` names whichever working Python launcher the
host environment provides. If a bare `python` invocation fails (on Windows it is commonly shadowed
by a non-functional Microsoft Store alias), use the environment's actual launcher — e.g.
`uv run python [SCRIPT_TYPE]` — rather than accepting the script-failure fallbacks in
REQ-MCQ-E-002 / REQ-MCQ-E-003. Those fallbacks exist for genuine script errors; silently taking
them on every trial because the interpreter is unreachable would defeat randomized type and axis
selection entirely.

Every reference to these paths in the rest of this file is by constant name (`SCRIPT_TYPE`,
`MCQ_PROMPT`, …), not by literal path, so this note is the only place the substitution is needed.

---

## Active Constraints

These are binding. They do not yield to judgment calls.

- Generate the **entire batch before presenting any trial** — REQ-C-001. The Generation Phase runs once, produces the batch artifact, and only then does the Delivery Loop begin.
- Load `MCQ_PROMPT`, `MSQ_PROMPT`, `ORDERING_PROMPT`, and `MATCHING_PROMPT` once, at the start of the Generation Phase, before any slot's content is constructed. If any is unreadable: halt — REQ-MCQ-E-001 / REQ-MAT-E-001.
- Call `SCRIPT_TYPE` once per slot in Pass 1 to determine the question type (mcq, msq, ordering, or matching). If Step I5 (procedural determination) determined the concept is non-procedural, include `ordering` in that call's `--exclude`. If Step I6 (matchable determination) determined the concept is non-matchable, include `matching` in that call's `--exclude` — REQ-ORD-F-010, REQ-MAT-F-010. These excludes combine (comma-joined) when both gates fire; if that leaves only `mcq`/`msq`, the draw proceeds from those.
- Call `SCRIPT_AXIS` once per slot in Pass 1. Pass every axis already assigned to an earlier slot as `--exclude`, in assignment order — REQ-C-002.
- Call `SCRIPT_POSITION` once per **MCQ** slot in Pass 1. Pass every position already assigned to an earlier MCQ slot as `--assigned`, in assignment order. The drawn label is the slot's `key`, and Pass 2 constructs the choices around it — REQ-C-016. Never assign an MCQ correct-answer position by judgment; that is the bias this script exists to remove. Ordering and Matching have no assignable position, and MSQ is out of scope.
- For an ordering slot, if the assigned axis cannot force the slot's order, re-draw via `SCRIPT_AXIS` in Pass 2 — drawing only from axes assigned to no other slot and not already rejected for this slot — up to 3 attempts; on exhaustion, hold the axis and reconstruct the scenario. Never substitute the trial type — REQ-ORD-E-003, REQ-C-003.
- For a matching slot, if the assigned axis cannot make the slot's grid projection-resolvable, re-draw on the same terms, up to 3 attempts; on exhaustion, hold the axis and reconstruct the case-set. Never substitute the trial type — REQ-MAT-E-003, REQ-C-003.
- A rejected axis is **not** added to the session's used-axes list. It is recorded on its own slot only and stays drawable by any other slot — REQ-C-004.
- The batch artifact is **internal**. Never render it, quote it, summarize it, or acknowledge its existence to the learner. Same discipline as the Probe Target descriptor.
- In Pass 2: generate the **Probe Target** descriptor for each slot internally (≤6 words) and store it on the slot. Never reveal it during delivery — it appears only in the report.
- After the last slot is written, run the **consistency pass** (G6) over the finalized batch: every slot's `explanation` block must be complete against its type's coverage rule. An incomplete slot is regenerated — holding its `question_type`, `axis`, `axis_rejected`, and, for MCQ, its Pass-1 position — up to 3 attempts, then accepted and logged internally — REQ-C-017, REQ-C-009. G6 is a **second** gate: the per-slot internal-validation checklist in G5 rule 3 remains the primary one and is never bypassed, softened, or reordered around.
- The Delivery Loop assembles each breakdown from the slot's stored explanation atoms. It authors no new rationale and reads no generation prompt — REQ-C-010. Where atoms are absent it falls back to authoring from the Response Protocol prose — REQ-C-015.
- Run all N trials regardless of intermediate performance. No early termination.
- Do not display trial numbers, scores, running totals, or the batch size to the learner at any point during generation or delivery.
- After trial N — or if the learner requests the report early — run the analysis phase and output the report.

---

## Intake Phase

Execute steps I1 through I6 in order. Do not batch them.

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

Set `BATCH_SIZE = N`. A bounded session generates exactly one batch — `batch_index: 0` —
holding every trial of the session. `BATCH_SIZE` is the only knob the Generation Phase reads;
nothing else in this file assumes one batch.

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

"Other" captures any custom domain. Store as DOMAIN. Pass to MCQ_PROMPT, MSQ_PROMPT,
ORDERING_PROMPT, and MATCHING_PROMPT for stem construction.

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
  session. Call `SCRIPT_TYPE` with `--exclude ordering` (or `--exclude ordering,matching`
  if Step I6 also excludes matching) on every trial this session, so `ordering` is
  never drawn.
- If **yes**: no exclusion is applied at intake on `ordering`'s account. A slot-level
  axis re-draw may still apply once an `ordering` slot is drawn — see Generation Phase, Pass 2.

### Step I6 — Matchable determination (internal)

Once the concept is defined (Step I1), determine once whether it affords **multiple
confusable cases along a dimension** — at least three distinct conditions, symptoms,
sub-types, or instances that each map to a distinct, cross-viable outcome. A flat
concept (one definition, no case structure — nothing to discriminate between) does
not afford this. This is an internal judgment call made by the orchestrator; do not
ask the learner.

Store the result as `MATCHABLE` (yes/no) — REQ-MAT-F-010.

- If **no**: `matching` is excluded from the type draw for the remainder of the
  session. Call `SCRIPT_TYPE` with `--exclude matching` (or `--exclude ordering,matching`
  if Step I5 also excludes ordering) on every trial this session, so `matching` is
  never drawn.
- If **yes**: no exclusion is applied at intake on `matching`'s account. A slot-level
  axis re-draw may still apply once a `matching` slot is drawn — see Generation Phase, Pass 2.

**Excludes combine.** `PROCEDURAL` = no and `MATCHABLE` = no are independent
determinations and may both fire on the same concept (a flat, non-procedural concept).
When both fire, pass both types in one comma-joined `--exclude` argument
(`--exclude ordering,matching`) and the type draw proceeds from `mcq`/`msq` only —
REQ-MAT-F-010.

---

## Batch Artifact

The Generation Phase produces this structure; the Delivery Loop consumes it. It is held **in
context only** — there is no file, no path constant, and no writer script.

**Never render it.** No part of it — a stem before its turn, a key, an atom, a probe target, the
batch size, or the fact that a batch exists — is shown to the learner at any point. It is
internal state, exactly like the Probe Target descriptor. Leaking it before delivery hands the
learner the answer key to the whole session.

One JSON object per trial — REQ-C-013:

```json
{
  "batch_index": 0,
  "generated_at": "<timestamp>",
  "trials": [
    {
      "trial_index": 0,
      "question_type": "mcq | msq | ordering | matching",
      "axis": "<the finally-used axis, post-refit>",
      "axis_rejected": ["<axis>"],
      "probe_target": "<=6 words, internal only>",
      "stem": "...",
      "choices": {},
      "key": null,
      "explanation": {
        "axis_statement": "what this axis tests in this scenario — one sentence",
        "key_survival": {},
        "distractor_failures": {
          "<label>": {
            "failure": "the specific point where it fails under the axis",
            "viability_account": "why it reads as correct on first pass",
            "orthodox_but_wrong": false,
            "near_duplicate_of": "<choice label> | null"
          }
        },
        "near_duplicate_differentiators": []
      },
      "grade": null,
      "gap_summary": null
    }
  ]
}
```

`grade` and `gap_summary` are **delivery-time** fields — null at generation, written by the
Delivery Loop after the learner answers.

`near_duplicate_of` names a **choice label**, and that label may be a correct-answer label. It is
therefore not necessarily a key in `distractor_failures` — do not dereference it as one.

Type-specific shapes:

| Type | `choices` | `key` | `distractor_failures` keys | `key_survival` |
|---|---|---|---|---|
| mcq | A–D | one label | the 3 labels not in `key` | `{<key label>: str}` — 1 entry |
| msq | A–E | set of labels | every label not in `key` (1–4) | `{<label>: str}` — one per correct label |
| ordering | pool of labels; K disclosed, D hidden | ordered list of labels | the D distractor pool labels (1–3) | `{"adjacency_forcings": [str], "reverse_order_failures": [str]}` — K−1 forcings, ≥2 reverse-order failures |
| matching | `1…n` prompts + `A…m` responses | injective prompt→response map | the D unused response labels (1–3) | `{<prompt label>: str}` — one per pairing (3–7) |

**The MCQ `key` is drawn, not chosen.** For an `mcq` slot the correct-answer position is drawn by
`SCRIPT_POSITION` in Pass 1 and written straight to `key` — for MCQ the key label *is* the
correct answer's position, so no additional field is needed and the schema is unchanged. Pass 2
then constructs the four choices around that fixed label. For every other type `key` is Pass 2
output as before.

**Coverage rule.** `distractor_failures` must carry an entry for **every choice not in the key**.
A missing entry is a construction defect: delivery would have to author that rationale live,
which is the cost this structure exists to remove.

---

## Generation Phase

Runs **once**, after intake, before any trial is presented — REQ-C-001. It produces the batch
artifact and presents nothing.

### G1. Announce

Tell the learner that trials are being prepared, in one short line — e.g. "Preparing your
trials — one moment." Generation is never silent — REQ-C-011.

State no count. The batch size is a trial number by another name, and trial numbers are not
shown to the learner.

### G2. Batch size

`BATCH_SIZE = N`, set at Step I2. A bounded session generates exactly one batch, `batch_index: 0`.

### G3. Prompt load

Read `MCQ_PROMPT`, `MSQ_PROMPT`, `ORDERING_PROMPT`, and `MATCHING_PROMPT`.

If any is unreadable: halt immediately — REQ-MCQ-E-001 / REQ-ORD-E-001 / REQ-MAT-E-001. The halt
fires here, before any content is constructed.

Retain all four in context for the whole session. Do not reload, and do not re-read them during
delivery.

This load precedes Pass 2 because Pass 2's axis-fit checks are defined inside `ORDERING_PROMPT`
and `MATCHING_PROMPT` — they cannot be run against a file that has not been read.

### G4. Pass 1 — type, axis, and MCQ answer position for every slot

Draw type and axis for all `BATCH_SIZE` slots, and the correct-answer position for every `mcq`
slot, **before constructing any content** — REQ-C-002, REQ-C-016.

For each slot `i` from 0 to `BATCH_SIZE − 1`, in order:

**1. Question type.** Invoke:
```
python SCRIPT_TYPE
```

If Step I5 and/or Step I6 excluded a type (`PROCEDURAL` = no and/or `MATCHABLE` = no), invoke
instead with the applicable type(s) comma-joined in `--exclude`:
```
python SCRIPT_TYPE --exclude ordering
python SCRIPT_TYPE --exclude matching
python SCRIPT_TYPE --exclude ordering,matching
```

The exclude string is a **session constant** — derive it once from I5/I6 and pass the identical
string on every slot's draw.

- Exit code 0: use the printed type (`mcq`, `msq`, `ordering`, or `matching`) for this slot. Store as `question_type`.
- Exit code non-zero: default to `mcq` for this slot. Log the fallback internally — REQ-MCQ-E-003.

**2. Axis.** Invoke:
```
python SCRIPT_AXIS --exclude [comma-delimited list of the axes assigned to slots 0…i−1, in assignment order]
```

Omit `--exclude` for slot 0 (no axes assigned yet).

- Exit code 0: use the printed axis for this slot. Store as `axis`.
- Exit code 1: pick the first axis from `[recognition, application, failure-diagnosis, boundary-condition, transfer, time, risk, coupling, observability]` not yet assigned to a slot. Log the fallback internally — REQ-MCQ-E-002.

**3. Correct-answer position — `mcq` slots only.** Invoke:
```
python SCRIPT_POSITION --assigned [comma-delimited list of the positions assigned to this batch's earlier MCQ slots, in assignment order]
```

Omit `--assigned` for the batch's first MCQ slot. Skip this draw entirely for `msq`, `ordering`,
and `matching` slots.

- Exit code 0: use the printed label (`A`, `B`, `C`, or `D`) as this slot's `key`.
- Exit code non-zero: assign the label used by the fewest of this batch's earlier MCQ slots, breaking ties in `A, B, C, D` order. Log the fallback internally — REQ-MCQ-E-004.

The draw is uniform over the least-used positions, so the correct answer's position is balanced
across the batch's MCQ slots by construction. This is why `MCQ_PROMPT`'s `position-assignment`
step is not left to judgment — positional bias is fixed here, at the draw, and never by
regenerating a finished trial — REQ-C-016.

At the end of Pass 1 every slot holds a `question_type` and an `axis`, no axis is assigned to
two slots, and every `mcq` slot holds its `key`. Nothing has been constructed. Nothing has been
presented.

### G5. Pass 2 — content, slot by slot

For each slot in `trial_index` order, construct its content and write it into the artifact.

The construction sequence in the prompt matching the slot's `question_type` — `MCQ_PROMPT`,
`MSQ_PROMPT`, `ORDERING_PROMPT`, or `MATCHING_PROMPT` — governs construction unchanged. Four
orchestration-level rules apply on top of it:

**1. The prompt's `output` step is suppressed.** That step presents the question to the learner
and waits for a response. It is **not executed during generation** — REQ-C-015. Capture what it
would have presented — the stem, the choices/pool/grid, the closing prompt — into the slot
instead. The Delivery Loop does the presenting, later, one trial at a time.

**2. The axis-fit re-draw is batch-scoped.** The prompt's axis-fit step re-draws from
*used + rejected*; in a batch it re-draws from **axes assigned to no other slot and not already
rejected for this slot** — REQ-C-003.

For an **ordering** slot (REQ-ORD-E-003, REQ-ORD-F-016), confirm per `ORDERING_PROMPT`'s
axis-fit check that the slot's axis can force this scenario's order. For a **matching** slot
(REQ-MAT-E-003, REQ-MAT-F-016), confirm per `MATCHING_PROMPT`'s axis-fit check that it can make
this slot's grid projection-resolvable — a dense, cross-viable grid with a unique bijection. If
it cannot:

1. Re-draw: `python SCRIPT_AXIS --exclude [every axis assigned to any other slot] + [every axis already rejected for this slot]`. The drawable set is exactly the axes assigned to no other slot and not yet rejected here.
2. A rejected axis is **not** added to the session's used-axes list. Record it in this slot's `axis_rejected` and nowhere else; it stays drawable by another slot's re-draw — REQ-C-004.
3. Repeat up to 3 re-draw attempts for this slot.
4. If the attempts are exhausted — or if the drawable set is empty, which is the case once every axis is assigned to some slot — hold the last-drawn axis and reconstruct the scenario (ordering) or the case-set (matching) to one that axis can force. Never substitute the slot's type.

Once settled — fit confirmed, or held after exhaustion — that axis is the slot's **finally-used
axis**. It, and only it, is written to `axis`, counts against other slots' draws, and appears in
the report's Axis Coverage.

**3. Validation gates the write, not the presentation.** The prompt's internal-validation
checklist runs **before** the slot is written to the artifact. A slot failing any check is
regenerated, not written. Difficulty is structural: every wrong answer must be independently
viable in isolation and fail **only** under forward projection along the slot's axis. Batching
changes *when* a trial is built — never *what it must satisfy*. An atom that is hard to write is
evidence of a defective choice; regenerate the choice, never soften it.

**4. An MCQ slot's correct-answer position is already fixed.** `MCQ_PROMPT`'s
`position-assignment` step still runs, but its choice is made: place the correct answer at the
label already in the slot's `key` from Pass 1, and distribute the other three around it. Do not
re-assign, and do not vary it by judgment — REQ-C-016. This constrains **where** the correct
answer sits, never **what** any choice must satisfy: the near-duplicate pair, the
orthodox-but-wrong choice, and the independent viability of all four are unchanged.

After construction and validation, per slot:

**Probe Target.** Generate the descriptor: ≤6 words naming the specific aspect of the concept
this slot tests (e.g. "Failure propagation under concurrent load"). For ordering, name the
procedure aspect ("Dual-write ordering before backfill"). For matching, the discrimination
("Reversible vs. structural grip loss"). Store as `probe_target`. Do not reveal it to the learner.

**Write the slot** into the batch artifact, with `grade` and `gap_summary` null.

When every slot is written, proceed to G6. The batch is not final until G6 has passed it.

### G6. Consistency pass — atom completeness

Runs **once**, after G5 writes the last slot, before any trial is presented — REQ-C-017. It
sweeps the finalized batch and verifies that every slot's `explanation` block is complete. It
presents nothing, and it reports nothing to the learner.

**G6 is a second gate, never a substitute.** The type's `internal-validation` checklist has
already gated every slot at G5 rule 3, before that slot was written. That gate is unchanged, is
never skipped because G6 exists, and remains the primary one. G6 checks a property no per-slot
gate can see: that the batch as delivered carries, for every slot, the rationale delivery is
required to assemble rather than author — REQ-C-010. A gap here is invisible at delivery, which
silently falls back to authoring live (REQ-C-015) and returns the reasoning cost this feature
exists to move — FM-C-3.

**Sweep.** For each slot in `trial_index` order, check its `explanation` block against the
coverage rule for the slot's `question_type` (Batch Artifact, type-specific table):

1. **`axis_statement`** — present and non-empty: one sentence naming what this slot's `axis` tests in this scenario.
2. **`key_survival`** — present, in the type-specific shape, with every graded unit carrying its own entry and none merged: MCQ 1 entry for the key label; MSQ one per correct label; Ordering `adjacency_forcings` with K−1 entries and `reverse_order_failures` with at least 2; Matching one entry per pairing, 3–7.
3. **`distractor_failures`** — one entry for **every choice not in the key**, and no entry for a choice that is in it: MCQ the 3 non-key labels; MSQ every label not in the key (1–4); Ordering the D distractor pool labels (1–3); Matching the D unused response labels (1–3).
4. **Each `distractor_failures` entry** — `failure` non-empty and naming the point where the choice fails under the axis, not restating the conclusion; `viability_account` non-empty, distinct from `failure`, and accounting for why the choice reads as correct on first pass; `orthodox_but_wrong` a boolean; `near_duplicate_of` a choice label or null.
5. **`orthodox_but_wrong`** — true on at least one entry (exactly one for MCQ).
6. **`near_duplicate_differentiators`** — present as a list, and non-empty whenever any entry's `near_duplicate_of` is non-null. `near_duplicate_of` names a **choice** label and may be a correct-answer label — do not dereference it as a `distractor_failures` key when checking it.

A slot that passes every check is **untouched**. Do not re-word, re-balance, or "improve" a
complete slot.

**Regeneration — the offending slot only** (REQ-C-009). A slot failing any check is regenerated:

1. **Hold** the slot's `question_type`, `axis`, and `axis_rejected`. Do not re-draw any of them: a re-drawn axis would break the batch's axis uniqueness (REQ-C-002, REQ-C-004) and silently misstate the report's Axis Coverage. For an `mcq` slot, hold the Pass-1 correct-answer position in `key` as well.
2. **Reconstruct the slot whole** through the type's prompt — the same construction sequence Pass 2 runs, through `internal-validation` and `explanation-baking`, under the same four orchestration rules. Never patch a missing atom onto a slot that stands: a slot is rewritten, never edited in place.
3. **The bar is identical.** A regenerated slot clears the same `internal-validation` checklist as an original, with **no allowance made because it is a retry**. A missing or unwritable atom is evidence of a defect in the *choice*, not in the atom — regenerate the choice under the existing viability rule. Never soften a choice, loosen a distractor, or simplify a scenario to make an atom easier to write. Every wrong answer must still be independently viable in isolation and fail **only** under forward projection along the slot's axis.
4. **Overwrite** the slot in the batch artifact, with `grade` and `gap_summary` null.
5. **Re-run G6** over the batch.

**Cap: 3 regeneration attempts per slot** — FM-C-6, mirroring the Pass-2 refit convention. On
exhaustion, accept the slot as it stands and log the acceptance internally. Never expose it, and
never let it change what is presented: delivery's atoms-absent fallback (REQ-C-015) covers the
residue correctly, so an accepted slot degrades the breakdown's provenance, not its coverage.

The cap is per slot. It bounds the pass without a batch-level ceiling.

When every slot has passed, or has been accepted under the cap, the batch is final. Proceed to
the Delivery Loop.

---

## Delivery Loop

Runs after the Generation Phase, once per trial, over the batch's slots in `trial_index` order.
It presents, waits, parses, grades against the stored `key`, and assembles the breakdown from the
slot's stored atoms. It authors no new rationale and reads no generation prompt — REQ-C-010.

Report numbering is session-global: a slot's trial number is
`batch_index × BATCH_SIZE + trial_index + 1`. A bounded session has `batch_index: 0`, so the two
coincide. Never display it.

### D1. Present

Present the slot's stored `stem` and `choices` **verbatim as generated**. Do not regenerate,
re-shuffle, re-label, or re-word. This holds for every presentation of a slot, including a
re-presentation after a tangent or a clarification — REQ-ORD-F-015, REQ-MAT-F-015.

For MCQ: present **MCQ** on its own line, then the question stem and choices A–D. Stop. Wait for the learner's response.
For MSQ: present **MSQ** on its own line, then the question stem and choices A–E, with the count in the closing prompt. Stop. Wait for the learner's response. Accept any common format (comma-separated, space-separated, written out). Parse as a set of letters — order does not matter.
For Ordering: present **ORD** on its own line, then the task scenario, the pool with one label per line, and a closing prompt disclosing K (the number of steps to arrange) but not D (the number of distractors). Stop. Wait for the learner's response. Accept any common format (comma-separated, space-separated, arrow-separated, numbered list), case-insensitive. Parse as an **ordered** list of labels — order is significant. An out-of-pool label or a repeated label is invalid: ask the learner to resubmit; do not count the attempt — REQ-ORD-E-002.
For Matching: present **MAT** on its own line, then the stored stem and grid. Stop. Wait for the learner's response. Accept common pair formats (`1-C`, `1:C`, `1C`, `1 → C`), comma- or newline-separated, case-insensitive. Parse as a complete injective mapping over the printed labels; anything else is invalid — ask the learner to resubmit, do not count the attempt (REQ-MAT-E-002). Attaching a distractor is **valid and incorrect**, not a resubmit.

### D2. Grade against the stored key

Compare the parsed response to the slot's stored `key`. Do not re-derive the key and do not
re-open a generation prompt to check it.

For MCQ: correct iff the selected label equals `key`.
For MSQ: correct iff the selected set equals `key` exactly — no extra picks, no missed picks.
For Ordering: correct iff the learner's ordered selected sequence exactly equals the correct
sequence — the right steps, no distractors, none missing, exact order — REQ-ORD-F-007.
For Matching: correct iff every one of the learner's n prompt→response pairs equals the key
exactly — binary, all-or-nothing; the D distractor responses are correctly left unused —
REQ-MAT-F-008.

### D3. Deliver the breakdown

Apply the MCQ, MSQ, Ordering, or Matching response protocol (see Response Protocol below) for
the slot's `question_type`, assembling each step from the slot's stored `explanation` block per
the field map at the head of that section.

### D4. Record the result

Write the delivery-time fields onto the slot:

```
grade: correct | incorrect
gap_summary: str | null
```

`gap_summary` is populated only for incorrect responses: the specific claim or mechanism the
learner missed. For MSQ, note which picks were wrong and which correct answers were missed. For
Ordering, note the false inclusions, the omissions, and the transposed pairs — REQ-ORD-F-009.
For Matching, note the mis-attachments to distractor responses, the correct responses left
unused, and the transposed pairs — REQ-MAT-F-021.

`probe_target`, `question_type`, and `axis` are already on the slot from generation. Do not
regenerate them.

### D5. Advance

Move to the next slot in `trial_index` order. When the last slot has been delivered, proceed to
the Analysis Phase.

If the learner requests the report early, proceed to the Analysis Phase immediately and run it
over the slots delivered so far. Undelivered slots are abandoned — they are never presented,
never graded, and contribute nothing to the report.

---

## Response Protocol

### Assembling the breakdown from stored atoms

The eight protocols below define **what a breakdown must cover**. Under batched generation they
are not authored live: each numbered step is filled from the slot's stored `explanation` block.
Assemble; do not re-derive. Do not open a generation prompt to deliver a breakdown — REQ-C-010.

| Protocol step | Artifact field |
|---|---|
| "State the axis: …" | `explanation.axis_statement` |
| "Explain why the correct answer / sequence / pairing survives" | `explanation.key_survival` — shape varies by type (see Batch Artifact); address **every** entry individually |
| "Address each wrong answer / distractor individually — the specific point where it fails **and why**" | `.failure` gives the failure point; `.viability_account` gives why it was not eliminable on first read |
| "Name the orthodox-but-wrong choice" | the `distractor_failures` label whose `orthodox_but_wrong` is `true` |
| "Explain the near-duplicate differentiator" | `explanation.near_duplicate_differentiators` — deliver every entry. `near_duplicate_of` names the paired **choice label**, which may be a correct-answer label and so is not necessarily a `distractor_failures` key |

Coverage is fixed by the artifact: `distractor_failures` carries an entry for every choice not in
the key, so "address all wrong answers individually" is satisfied by iterating its entries.

**Fallback — atoms absent.** If a slot carries no `explanation` block, or the block lacks a field
a protocol step needs, author that step live from the protocol prose below, exactly as an
unbatched session would. Never skip a step and never shorten the coverage because an atom is
missing — REQ-C-015.

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

### Matching — Correct answer

A response is correct when every one of the learner's n prompt→response pairs
exactly matches the key — binary, all-or-nothing; the D distractor responses are
correctly left unused.

1. Acknowledge briefly: "Correct." / "Right." / "That's it."
2. State the axis: "The axis here is [axis]: [one sentence on what it tests in this scenario]."
3. Explain why each pairing survives — address each prompt→response individually:
   the projection that fixes it and rules out the other surface-viable responses
   for that prompt.
4. Address each distractor individually: the specific point where it fails and why
   it matches no prompt under the axis. Name the orthodox-but-wrong distractor
   explicitly: "X is the conventional answer for prompt [n] — professionally sound
   in many contexts — but under [axis], prompt [n] resolves elsewhere, and X matches
   nothing because [mechanism]."
5. Resolve the near-duplicate confusion cell: the one phrase that separates the twin
   prompts and the twin responses, and why it is decisive only under projection.
6. Proceed immediately to the next trial. If this was trial N, proceed to the Analysis Phase instead.

### Matching — Incorrect answer

A response is incorrect when any of the learner's submitted pairs differs from the
key — a prompt attached to a distractor, a correct response left unused, two
prompts' responses transposed, or any combination.

1. State the axis first: "The axis here is [axis]: [one sentence]."
2. Decompose the error into its two error classes, each addressed individually:
   - **Selection errors** — for each prompt the learner attached to a distractor
     response, why that response matches no prompt under the axis (name the
     orthodox-but-wrong lure if that is what they took); for each correct response
     the learner left unused, why it belongs to its prompt — why it survives
     projection.
   - **Assignment errors** — for each transposed pair (two prompts whose correct
     responses were swapped, the near-duplicate cross-wire being canonical), why
     each prompt's true response is fixed under projection and why the swap fails.
3. State the correct key directly: `1→A, 2→B, 3→C, 4→D` (E unused).
4. Explain why each pairing survives — each prompt→response individually.
5. Address all distractors individually — the same full coverage as the correct-answer
   protocol. Name the orthodox-but-wrong distractor. Resolve the near-duplicate cell —
   what one phrase differentiates the twins.
6. Proceed to the next trial. If this was trial N, proceed to the Analysis Phase instead.

**No nudge. No recovery exchanges.** This is an evaluation.

---

## Tangent Handling

If the learner diverts mid-trial to explore a related concept:

1. Note the interruption point: which trial number and what was presented.
2. Engage with the tangent conversationally. Do not run MCQ, MSQ, Ordering, or Matching
   trials on the tangent concept — the probe is suspended, not extended.
3. When the learner signals readiness to continue, re-present the interrupted trial from
   the beginning. Do not resume mid-question. For an Ordering trial, any re-presentation
   — after a tangent or after a clarification exchange — uses the same pool and the same
   labels: no re-shuffle, no regeneration — REQ-ORD-F-015. For a Matching trial, any
   re-presentation likewise uses the same prompts, the same responses, and the same
   labels: no re-shuffle, no regeneration — REQ-MAT-F-015.

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
| 1 | MCQ / MSQ / ORD / MAT | [descriptor] | [axis] | ✓ / ✗ | — / [specific failure point] |
```

`Type`: MCQ, MSQ, ORD, or MAT.
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

For Matching (REQ-MAT-F-017):
- **Trial # — [Probe Target] ([axis]) [MAT]**
- Submitted pairs: [prompt→response pairs as submitted]
- Correct key: [prompt→response pairs, unused responses noted]
- Selection errors: [attachments to distractor responses; correct responses left unused], decomposed, or "none"
- Assignment errors: [transposed pairs — two prompts' correct responses swapped], decomposed, or "none"

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

For Matching trials, apply this additionally (REQ-MAT-F-018): a single transposition
in the near-duplicate cell, with the rest of the pairs otherwise correct, reads as a
**surface gap** — the learner has the discrimination but slipped on the one decisive
phrase. Repeated attachment to the orthodox-but-wrong distractor, or errors spanning
both selection and assignment across trials, reads as a **fundamental gap**.

---

## Error Handling

### REQ-MCQ-E-001 — MCQ_PROMPT, MSQ_PROMPT, ORDERING_PROMPT, or MATCHING_PROMPT unreadable

Halt immediately. Report:

> "mcq-probe cannot proceed — [filename] is unreadable at [path]. Resolve this before continuing."

Do not attempt to generate trials from memory or internal knowledge. All four prompt
files are required. Their absence is not a degraded mode — it is a halt condition
(REQ-MAT-E-001 extends this requirement to `MATCHING_PROMPT`). The halt fires at
Generation Phase step G3, before any slot's content is constructed.

### REQ-MCQ-E-002 — SCRIPT_AXIS non-zero exit

Applies per slot, during Pass 1. Pick the first axis from `[recognition, application,
failure-diagnosis, boundary-condition, transfer, time, risk, coupling, observability]` not
already assigned to a slot. If every axis has been assigned, pick the first that is not the
most recently assigned. Log the fallback internally — do not expose it to the learner.
Generation continues normally.

### REQ-MCQ-E-003 — SCRIPT_TYPE non-zero exit

Applies per slot, during Pass 1. Default to `mcq` for that slot. Log the fallback internally —
do not expose it to the learner. Generation continues normally.

### REQ-MCQ-E-004 — SCRIPT_POSITION non-zero exit

Applies per `mcq` slot, during Pass 1. Assign the position used by the fewest of this batch's
earlier MCQ slots, breaking ties in `A, B, C, D` order. Log the fallback internally — do not
expose it to the learner. Generation continues normally.

This fallback keeps the batch balanced but makes the *order* of positions predictable while the
script is unreachable, which the draw itself is not. Treat a firing of this fallback as a broken
interpreter or a missing script, not as a normal path — see the launcher note under File Path
Constants.

### REQ-ORD-E-002 — Invalid ordering response

An out-of-pool label, a repeated label, or a response that cannot be parsed as an
ordered list is invalid. Ask the learner to resubmit. Do not count the attempt against
the trial — the trial is still awaiting a valid response.

### REQ-ORD-E-003 — Ordering axis re-draw

Runs in the Generation Phase, Pass 2. If the assigned axis cannot force an ordering slot's
order, re-draw via `SCRIPT_AXIS --exclude [every axis assigned to any other slot] + [every
axis rejected for this slot]`, up to 3 attempts — the drawable set is exactly the axes
assigned to no other slot and not yet rejected here (REQ-C-003). A rejected axis is not added
to the session's used-axes list — it is recorded in this slot's `axis_rejected` and remains
drawable by other slots (REQ-C-004). If the attempts are exhausted, or the drawable set is
empty, hold the last-drawn axis and reconstruct the scenario to one it can force. Never
substitute the slot's type. Only the finally-used axis enters the session's axis-exclusion
list and the report's Axis Coverage — REQ-ORD-F-016.

### REQ-MAT-E-002 — Invalid matching response

A repeated prompt, a reused response, an out-of-range label, a missing prompt, or a
response that otherwise cannot be parsed as a set of n prompt→response pairs is
invalid. Ask the learner to resubmit. Do not count the attempt against the trial —
the trial is still awaiting a valid response. A **well-formed** set that attaches a
prompt to a distractor response is **valid and incorrect** — grade it, do not ask
for a resubmit.

### REQ-MAT-E-003 — Matching axis re-draw

Runs in the Generation Phase, Pass 2. If the assigned axis cannot make a matching slot's grid
projection-resolvable, re-draw via `SCRIPT_AXIS --exclude [every axis assigned to any other
slot] + [every axis rejected for this slot]`, up to 3 attempts — the drawable set is exactly
the axes assigned to no other slot and not yet rejected here (REQ-C-003). A rejected axis is
not added to the session's used-axes list — it is recorded in this slot's `axis_rejected` and
remains drawable by other slots (REQ-C-004). If the attempts are exhausted, or the drawable
set is empty, hold the last-drawn axis and reconstruct the case-set to one it can force. Never
substitute the slot's type. Only the finally-used axis enters the session's axis-exclusion
list and the report's Axis Coverage — REQ-MAT-F-016.
