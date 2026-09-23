# Repo doctrine — mcq-probe question & answer design

This repo hosts evaluation skills. The load-bearing component of `mcq-probe` is the
**design of the questions and their answer choices**. Read this before designing,
editing, or extending any question type. The full construction spec lives in the
generation prompts (`mcq-probe/prompts/*_GENERATION_PROMPT.md`); this file exists so no
session starts with the wrong mental model of what those prompts enforce.

## The invariant: difficulty is structural, not a setting

`mcq-probe` is a **judgment probe, not a knowledge quiz**. Its job is to separate a
learner who understands how a concept behaves under real conditions from one who has
only memorized a definition. That separation is produced entirely by how the answer
choices are built. The invariant:

> **Every wrong answer must be independently viable in isolation — it reads as correct
> on first pass — and fail ONLY when projected forward under the question's assigned
> judgment axis.**

A wrong answer that can be eliminated by surface reading — factually false, obviously
broken, unrelated, or out of scope — is a **construction defect**, not an easy question.
It is regenerated, never shipped. "Easy distractor" and "hole in one" are the same thing
here.

This is why the skill is hard, and the hardness **is the point**. Do not soften it to
reduce friction, improve pass rates, or make a format "cleaner." Difficulty is the
deliverable.

## The two devices that enforce it

Every question is built around these (stated in MCQ terms; MSQ and Ordering carry direct
analogues):

- **Near-duplicate pair** — two choices that look alike, diverging at exactly one phrase
  (a qualifier, target, precondition, or sequencing detail) that is decisive *only* under
  forward projection. Tests precision of understanding.
- **Orthodox-but-wrong** — a professionally standard, textbook-correct-looking choice that
  fails under *this* question's specific axis. Tests whether the learner reasons
  independently or defers to convention. Expertise should pull toward it.

Wrong answers fail under the **axis** — recognition, application, failure-diagnosis,
boundary-condition, transfer, time, risk, coupling, observability — never because they
are false. No linguistic feature may signal correctness; heuristic cue words ("best",
"optimal", "recommended", …) are banned so the learner must reason.

## The mistake to never repeat

The failure mode this doctrine exists to prevent: treating "hard" as a difficulty **dial**,
or writing distractors that are rejectable on sight. That abandons the entire premise. If a
reviewer can discard a wrong answer *without* projecting the axis, the question is broken —
no matter how sophisticated the stem looks.

## Adding or changing a question type

When you introduce a new format (as Ordering was added alongside MCQ/MSQ), the first
question is **not** "how does the format work." It is:

> **How does this format preserve the every-wrong-answer-viable, fails-only-under-projection
> property — and where do the near-duplicate and orthodox-but-wrong devices map onto it?**

Answer that explicitly before designing the format. A novel format that makes selection or
answers easier is a **regression**, even if the mechanic is new. Ordering, for instance,
extends the invariant across *two* graded operations (which steps belong AND their forced
order); both must be projection-hard, and every distractor must be a plausible inclusion,
never out-of-scope filler. See `plans/ordering-question-type-plan.md` §3 (hardness transfer)
for the worked mapping.

## Before you touch answer design

Read the relevant generation prompt in full first — `MCQ_GENERATION_PROMPT.md`,
`MSQ_GENERATION_PROMPT.md`, or `ORDERING_GENERATION_PROMPT.md`. They are the authoritative
spec, and the internal-validation checklist in each is the bar every question must clear.
**This file is the mental model; those files are the contract.**
