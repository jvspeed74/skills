# Plan — Matching Question Type (mcq-probe)

**Status:** Implemented; under merge review. Commit history: `6715bc8` shipped the implementation (`MATCHING_GENERATION_PROMPT.md`, `SKILL.md`, `select_question_type.py`, this plan) and **explicitly deferred** the per-axis dry-run gate ("run it before merge"); `f5b7d1a` completed the 9-axis gate — adding worked examples 4–9 and the axis-fit fallback exercises — and self-certified it. An Opus review of `f5b7d1a` (**currently uncommitted**) then corrected two construction defects and diversified the worked-example n/D sizes; see the Dry-Run Gate Results table and the Review-correction note at the end of §16. OQ 1–7 are resolved per §5 and shipped as constructed — the generation prompt is built on them directly. **Outstanding before merge:** a second independent projection of the n=6/D=3 observability example (largest grid, highest hand-verification risk), and n=7 remains gate-untested (constructed identically to n=6).

*This status line originally read "Design — awaiting readback confirmation" when this plan was authored; it was corrected once implementation landed in the same commit that introduced the plan (`6715bc8`), and again to record the `f5b7d1a` gate and the review corrections.*
**Date:** 2026-08-27
**Branch:** `claude/mcq-probe-matching-questions-9d0f7a`
**Target skill:** `mcq-probe`
**Precedent:** `plans/ordering-question-type-plan.md` (Ordering was added the same way; this plan reuses its structure and its §3 hardness-transfer method).

---

## 0. Readback — the defining interpretation

The spec is one line: *"Matching: has a list of responses to match with a list of 3–7 prompts. You must match all the pairs correctly to receive credit for the question."* Everything below rests on three reads of it. If any is wrong, large parts of this plan change — confirm before implementation.

1. **The response list is larger than the prompt list (surplus responses).** "A list of responses to match with a list of 3–7 prompts" reads the two lists as separate and unequal. A pure equal-size bijection has a fatal property for this skill: once n−1 prompts are matched, the nth is forced by elimination with zero reasoning — a `1/n` difficulty leak (33% at n=3). The fix is **surplus responses**: `m = n + D` responses, `D ≥ 1` of which match no prompt. This is the matching analogue of Ordering's distractor pool — selection gets teeth, and elimination never hands the learner a free pairing. **This is the load-bearing interpretation.** (OQ 1)
2. **Credit is binary.** "Match all the pairs correctly to receive credit" = all-or-nothing, consistent with MCQ/MSQ/ORD. No partial credit for k-of-n correct. (OQ 2)
3. **The mapping is injective, one response per prompt, responses not reused.** Each prompt matches exactly one response; each response matches at most one prompt; `D` responses match nothing. Reusable responses were considered and rejected (OQ 3) — reuse dissolves the near-duplicate device and muddies the binary grade.

If instead you intend an **equal-size bijection with no surplus**, or **reusable responses**, say so now — §1, §4, §5, and the whole failure-mode analysis change.

---

## 1. Background / context

`mcq-probe` is a judgment-probe evaluation skill. An orchestrator (`SKILL.md`) runs an intake phase, an N-trial loop, and an analysis phase producing a Markdown report. Per trial, `select_question_type.py` draws the type and `select_mcq_axis.py` assigns one of 9 judgment axes (no consecutive repeat, no reuse within session). Generation prompts (one per type, loaded once on Trial 1) govern construction.

**The skill's central property — the thing this feature must preserve:** difficulty is a *structural* property of the answer set, not a setting. Every wrong answer is independently viable in isolation and fails **only** under forward projection along the assigned axis. Two devices enforce it — the **near-duplicate pair** and the **orthodox-but-wrong** choice. A wrong answer eliminable by surface reading is a construction **defect**, regenerated, never shipped.

**Why Matching is the acid test of that property.** Of the four types, Matching has the lowest-effort *default* form and the highest risk of shipping a knowledge quiz. "Match each protocol to its port," "match each term to its definition" — the canonical matching question is pure recall, every response keyword-locked to one prompt, every wrong cell rejectable on sight. That default form is the exact mistake `CLAUDE.md` forbids. Matching therefore demands the *strongest* explicit anti-surface machinery of any type: the difficulty must live in a **dense confusion grid**, not in an association table.

### Globals after this change

| Global | Value | Note |
|---|---|---|
| Type token (script stdout) | `matching` | joins `mcq`, `msq`, `ordering` |
| Display label | **MAT** | on its own line, matching MCQ/MSQ/ORD |
| n — prompts | 3–7, scenario-driven | the anchored set; the graded pairs |
| D — distractor responses | 1–3 | ≥1 so selection has teeth and elimination is defeated |
| m — response pool | n + D = 4–10 | the list matched *from* |
| Prompt labels | `1, 2, 3, …` (numeric) | distinguishes prompts from responses at a glance |
| Response labels | `A, B, C, …` (alpha) | the pool; D of them are unused in the key |
| Grade | binary | exact match of all n prompt→response pairs |
| Count disclosure | n and m both visible; D derivable | diverges from Ordering's hidden D — see OQ 7 / FM-7 |
| Mapping model | injective, unique, **surface-unresolvable** | every cell cross-viable; bijection recoverable only by projection |
| Axes | 9, reused unchanged | `select_mcq_axis.py` is axis-type-agnostic |
| Type distribution | 1/4 each (eligible concepts) | intake gates may exclude ordering and/or matching |
| Signature constructs | cross-viability law (global), near-duplicate confusion cell (≥1), orthodox-but-wrong distractor response (≥1), unique bijection | matching analogues of the MCQ/MSQ devices |

### Pipeline

Intake (now includes a one-time **matchable determination** alongside the existing procedural one — REQ-MAT-F-010) → trial loop. Per trial: `select_question_type.py` now returns `mcq`/`msq`/`ordering`/`matching`; `select_mcq_axis.py` assigns the axis; the matching generation prompt (loaded once on Trial 1) constructs the trial. A matching trial presents a prompt list (numeric) and a larger response pool (alpha); the learner replies with n prompt→response pairs; evaluation decomposes the response into **selection errors** (a prompt attached to a distractor response, or a correct response left unused) and **assignment errors** (two prompts' responses swapped), then the binary grade feeds the same analysis phase and report as the other three types.

---

## 2. Problem statement

MCQ/MSQ probe judgment among parallel choices; Ordering probes command of a forced procedure. None probes whether a learner can **discriminate confusable cases** — tell apart n near-identical conditions and attach each to its true outcome, when every outcome looks plausible for several conditions. That is a distinct and common competence (differential diagnosis, config-vs-behavior, symptom-vs-cause, edge-case classification), and Matching is the type that isolates it.

The hard constraint is preserving the binary grade under the skill's difficulty bar. Matching fails that bar in three specific ways, all of which must be engineered out:

- **Surface association leaks (the dominant defect).** If any response keyword-, category-, or textbook-matches exactly one prompt, that pairing is solvable without projecting the axis. This is the "hole in one" — and it is the *natural* state of a matching question. Defeating it is the whole job.
- **Elimination leaks (the parity defect).** In an equal-size bijection, correctly placing early pairs removes candidates and can unzip the grid; the last pair is always free. Surplus responses (`D ≥ 1`) plus a no-elimination-shortcut law close this.
- **Ambiguity leaks.** If two complete assignments are both defensible under the axis, the binary grade marks a valid answer wrong. The correct bijection must be unique.

Matching is therefore, like Ordering, harder than MCQ/MSQ by construction. That is intended, not a defect to soften.

---

## 3. Hardness transfer — one-to-one mapping (the load-bearing section)

This is the justification for every construction rule that follows. Each MCQ/MSQ difficulty mechanism maps to a matching analogue that must hold with equal force. Where Ordering doubled the projection burden across *selection + order*, Matching doubles it across *selection + assignment* (which responses are used, and which used response attaches to which prompt).

| MCQ/MSQ mechanism | What it forces | Matching transfer | Status |
|---|---|---|---|
| Every wrong answer independently viable | No surface elimination | **Every response reads as a plausible match for ≥2 prompts; every prompt has ≥2 plausible responses.** The whole n×m grid is dense with viable cells. No keyword/category/textbook cell. | Governs the whole grid |
| Wrong fails only under forward projection | Reasoning, not recall | **Both** operations projection-gated: which responses are distractors (selection) *and* which response attaches to which prompt (assignment). | Extended to two operations |
| Near-duplicate pair | Precision under one decisive phrase | **Near-duplicate confusion cell**: two twinned prompts × two twinned responses, forming a 2×2 sub-grid every cell of which is surface-viable; the correct diagonal is fixed by one embedded phrase decidable only under projection. Cross-wiring it is the canonical transposition error. | Preserved; the primary discrimination site |
| Orthodox-but-wrong | Punishes convention over reasoning | **Orthodox-but-wrong distractor response**: a distractor that is the textbook / conventionally-expected answer for one specific prompt. Expertise pulls you to attach that prompt to it; under projection the prompt resolves elsewhere and the orthodox response matches nothing. | Preserved; expertise actively misleads toward a wrong attachment |
| Surface features aren't the differentiator | Defeats pattern-matching | **No pairing recoverable by lexical/category overlap or by elimination.** The axis, not surface similarity or parity, resolves the grid. | New explicit requirement (two laws: cross-viability + no-elimination-shortcut) |
| No banned language / quality signals | No heuristic shortcuts | Unchanged; same banned lists, plus no sequencing/pointer cues that pre-wire a pairing. | Preserved |

**Correction carried over from Ordering's lesson.** Ordering's first draft included an out-of-scope distractor and had to remove it — an out-of-scope item is rejectable without projecting the axis. The matching analogue is a **response that is viable for only one prompt** (surface-locked). That is *also* a transfer failure and is forbidden. Every response must be cross-viable for ≥2 prompts, or it is a hole in one.

---

## 4. Grid-design law + required constructs

**Law (four parts).** Every pairing decision — used-vs-distractor and which-prompt — is decidable only by projecting each prompt forward under the assigned axis.

1. **Cross-viability (both directions).** Every response reads as a plausible match for **≥2 prompts** on first pass; every prompt has **≥2 plausible responses**. No response is surface-attachable (keyword, category, or textbook pairing) to exactly one prompt. The grid is dense; surface reading cannot resolve any cell.
2. **No-elimination-shortcut.** `D ≥ 1` surplus responses, each cross-viable. No prompt's correct match is recoverable by eliminating obviously-wrong responses. Validation simulates elimination: after *any* subset of prompts is correctly matched, every remaining prompt must still face **≥2 surface-viable responses**. Surplus is the means; this law is the end.
3. **Unique bijection.** Exactly one complete injective assignment survives projection. No second complete assignment is defensible under the axis. (The gradeability guarantee — analogue of Ordering's strict-total-order.)
4. **No free prompt.** Every prompt's correct response is contested by ≥1 other surface-viable response. No prompt is a giveaway. (The prompt-side complement of cross-viability — analogue of Ordering's surface-sort resistance.)

**Required constructs (per trial):**

1. **Near-duplicate confusion cell** (≥1) — two prompts twinned (diverging at one embedded phrase) and two responses twinned (diverging at one embedded phrase), forming a 2×2 sub-grid whose four cells are all surface-viable. Projection of the one differentiating phrase fixes the correct diagonal. The learner must not cross-wire the twins.
2. **Orthodox-but-wrong distractor response** (≥1) — a distractor (one of the `D` unused responses) that is the standard, professionally-expected answer for one specific prompt, written in language that signals rigor. Under the axis that prompt attaches elsewhere and this response matches no prompt. May alternatively be realized as a cross-attracting *matched* response (a prompt's conventional answer that is genuinely another prompt's match); the distractor form is primary and also justifies the surplus.

**Forbidden (transfer failures):** a response viable for only one prompt · any pairing recoverable by keyword/category/textbook overlap · a prompt whose match is forced by elimination · a second defensible complete assignment · sequencing/pointer language that pre-wires a pairing.

---

## 5. Design decisions

| Decision | Resolution |
|---|---|
| Response-set structure | **Surplus responses.** n prompts, m = n + D responses (D ∈ [1,3]), injective prompt→response. D responses are distractors, used by no prompt. Kills the parity/elimination leak; gives the orthodox-but-wrong lure a home. (OQ 1) |
| Grade model | **Binary.** Correct iff every one of the n prompt→response pairs equals the key. No partial credit. (OQ 2) |
| Response reuse | **None.** Each response matches ≤1 prompt. Reuse rejected: it dissolves the near-duplicate 2×2 device and complicates the binary grade. (OQ 3) |
| Mapping model | Injective, **unique** complete assignment. Every cell cross-viable; the bijection is recoverable only under projection, never by surface similarity or elimination. |
| n range | 3–7 prompts (per spec). n=3 is the difficulty floor (elimination pressure highest → surplus matters most); n=7 is the cognitive-load ceiling. |
| D range | 1–3 distractor responses, scenario-driven. m = n + D ∈ [4,10]. |
| Label scheme | Prompts numeric (`1…n`); responses alpha (`A…`). Two visibly distinct alphabets remove any prompt/response confusion in the learner's reply. (OQ 6) |
| Count disclosure | n and m are both visible (both lists are printed); D = m − n is derivable. Unlike Ordering (hidden D), this does not leak the answer — knowing *how many* responses go unused does not reveal *which*, since the unused ones are cross-viable. (OQ 7) |
| Signature constructs | Cross-viability law (global, four parts), near-duplicate confusion cell (≥1), orthodox-but-wrong distractor response (≥1), unique bijection. |
| Prompt/response substance | Prompts: 1–3 sentences, a concrete case/condition/symptom carrying one embedded distinguishing detail. Responses: 1–2 sentences, an outcome/behavior/cause/classification with enough detail to be cross-viable and to support the near-duplicate twin. A bare label ("bufferbloat") is insufficient; it must describe the mechanism. |
| Axis source | Reuse `select_mcq_axis.py` unchanged. All 9 axes apply; the axis defines the prompt-role→response-role semantic and the failure mode of a wrong attachment. |
| Intake matchable gate | At intake, determine once whether the concept affords **multiple confusable cases along a dimension** (≥3 conditions/symptoms/sub-types with distinct, cross-viable outcomes). If **not matchable** (a flat concept — one definition, no case structure), exclude `matching` from the session's type draw (`select_question_type.py --exclude matching`). Mirrors the procedural gate (REQ-MAT-F-010). (OQ 4) |
| Axis re-draw (no type substitution) | For a matchable concept, if the assigned axis cannot make this trial's grid projection-resolvable, **re-draw the axis** (`select_mcq_axis.py --exclude [used + rejected]`, up to 3 attempts). On exhaustion, hold the axis and reconstruct the case-set to one the axis can force. The trial type is **never** substituted mid-trial. Mirrors Ordering (REQ-MAT-E-003). |
| Near-duplicate ambiguity | If the near-duplicate cell cannot be made genuinely resolvable without over-specifying a prompt to the point of leaking the pairing, regenerate the cell or the trial. Mirrors Ordering FM-8 / edge case. |
| Type distribution | Equiprobable 1/4. Revisit after observing pass rates. (OQ 5) |
| Display token | **MAT**. Matches the three-letter pattern. |

---

## 6. Construction sequence (core of `MATCHING_GENERATION_PROMPT.md`)

1. **axis-confirmation** — use the axis from `select_mcq_axis.py`; do not signal it.
2. **axis-fit / re-draw** — confirm the assigned axis can make a dense, projection-resolvable grid for the concept (a prompt-role→response-role semantic under which every cell is cross-viable and one unique bijection survives). If not, signal an axis-fit failure to the orchestrator (re-draw axis, up to 3 attempts; on exhaustion, reconstruct the case-set). Never substitute the type. Non-matchable concepts are already excluded at intake (REQ-MAT-F-010).
3. **role-selection** — choose the prompt-role→response-role pairing the axis makes load-bearing (e.g., failure-diagnosis → symptom→cause; boundary-condition → condition→behavior; recognition → presentation→classification; transfer → new-domain-case→mechanism-instantiation). The role pairing is what makes surface association fail and projection necessary. **Transfer axis only:** apply domain-vocabulary inversion — phrase each response in a domain other than its correct prompt, so keyword cues point at the wrong pairing and only mechanism resolves (REQ-MAT-F-020; worked in §8.3).
4. **case-set construction (prompts)** — write n prompts (3–7) as minimal variants along one dimension of the concept, sharing a common frame so every response is topically plausible for every prompt, each diverging at one embedded distinguishing detail. Disclose n implicitly (they are numbered and all must be matched). Do not signal the axis.
5. **key construction (correct responses)** — write the n correct responses. For each, verify it is cross-viable for ≥2 prompts (not just its own) and that its correct prompt is fixed only under projection. Verify the complete assignment is **unique** — no second bijection survives. Plant the near-duplicate confusion cell (≥2 twin prompts × ≥2 twin responses).
6. **distractor construction** — write D distractor responses (1–3), each cross-viable (plausible for ≥2 prompts) and matching no prompt under projection. Include ≥1 orthodox-but-wrong distractor (the conventional answer for some prompt). Run the no-elimination-shortcut simulation.
7. **label-and-shuffle** — number prompts `1…n` and letter responses `A…` in shuffled order; the correct pairing must not run down the diagonal (1→A, 2→B, …); vary across trials; do not cluster distractor letters at the end.
8. **internal-validation** — run the checklist; regenerate on any failure.
9. **output** — **MAT** on its own line, the prompt list (numeric, one per line), the response pool (alpha, one per line), closing prompt: *"Match each of the [n] prompts to one response (e.g., 1-C, 2-A, …). Not every response is used."* Stop. Wait.

### Internal-validation checklist

- [ ] Assigned axis used and not signaled.
- [ ] Concept affords a dense projection-resolvable grid under the axis (else axis-fit fallback taken).
- [ ] Topic keyword unavoidable in the prompts and the responses.
- [ ] Every response is cross-viable for ≥2 prompts; no response is surface-attachable (keyword/category/textbook) to exactly one prompt.
- [ ] Every prompt has ≥2 surface-viable responses; no free prompt.
- [ ] No pairing is recoverable by lexical/category overlap — surface reading resolves no cell.
- [ ] No-elimination-shortcut: after any subset of prompts is correctly matched, every remaining prompt still faces ≥2 surface-viable responses.
- [ ] The correct assignment is unique — no second complete bijection survives projection.
- [ ] ≥1 near-duplicate confusion cell present (2 twin prompts × 2 twin responses; all four cells surface-viable; correct diagonal fixed only under projection).
- [ ] Each near-duplicate is genuinely resolvable without a prompt leaking its pairing (else regenerate — near-duplicate-forces-ambiguity edge case).
- [ ] ≥1 orthodox-but-wrong distractor response present (conventional answer for some prompt; matches nothing under projection).
- [ ] Each distractor fails for a distinct reason, only under projection.
- [ ] n ∈ [3,7]; D ∈ [1,3]; response pool m = n+D, prompts labeled 1…n, responses labeled A… contiguously.
- [ ] Correct pairing is not the identity diagonal (1→A, 2→B, …).
- [ ] No banned language; no sequencing/pointer cues that pre-wire a pairing.
- [ ] Transfer axis only: domain-vocabulary inversion applied — no response shares its correct prompt's domain vocabulary; keyword cues point away from the correct pairing (REQ-MAT-F-020).
- [ ] Case-set fresh this session.

---

## 7. Feedback protocol

**Correct** (all n pairs match the key):
1. Acknowledge briefly ("Correct." / "Right." / "That's it.").
2. State the axis in one sentence.
3. Why each pairing survives — each prompt→response individually: the projection that fixes it and rules out the other surface-viable responses.
4. Each distractor's failure, individually; name the orthodox-but-wrong distractor ("E is the conventional answer for prompt 1 — professionally sound in many contexts — but under [axis] prompt 1 resolves to A, and E matches nothing because [mechanism]").
5. Resolve the near-duplicate cell — the one phrase that separates the twin prompts and the twin responses, and why it is decisive only under projection.
6. Proceed to next trial, or to analysis if this was trial N.

**Incorrect** (any pair wrong):
1. State the axis first.
2. Decompose the error into its two classes, each addressed individually:
   - **Selection** — for each prompt the learner attached to a distractor response, why that response matches no prompt under the axis (name the orthodox-but-wrong lure if that is what they took); for each correct response left unused, why it belongs to its prompt.
   - **Assignment** — for each transposed pair (two prompts whose responses were swapped, the near-duplicate cross-wire being canonical), why each prompt's true response is fixed under projection and why the swap fails.
3. State the correct key directly: `1→A, 2→B, 3→C, 4→D` (E unused).
4. Why each pairing survives — each individually.
5. Each distractor individually; name the orthodox-but-wrong distractor; resolve the near-duplicate cell.
6. No nudge, no recovery exchange. Proceed.

---

## 8. Worked examples

Three axes proven constructible end to end — one per subsection. Each demonstrates the grid-design law (§4) in force: a dense cross-viable grid, a unique bijection, ≥1 near-duplicate confusion cell, and ≥1 orthodox-but-wrong distractor.

### 8.1 Canonical — failure-diagnosis (symptom → cause)

**Axis:** failure-diagnosis · **Concept:** TCP throughput anomalies (congestion control × flow control) · **Domain:** abstract · **n=4, D=1, response pool A–E.**

> Match each observed transfer symptom to its root cause. Not every cause is used.
>
> **Prompts (symptoms):**
> 1. A bulk transfer over a long-RTT satellite link plateaus near 2 Mbps though the path supports 50 Mbps; a capture shows the sender repeatedly stops sending and waits, then resumes — **with no retransmissions**.
> 2. A transfer over a clean gigabit LAN peaks, then repeatedly halves its rate in a regular sawtooth, with a retransmission at each drop.
> 3. A transfer through a device with a very large buffer sustains high throughput, but end-to-end latency climbs to several seconds and stays there; almost no packets are lost.
> 4. A transfer over WiFi runs well below capacity with frequent fast-retransmits, though the link's actual loss rate is low and RTT is stable.
>
> **Responses (causes):**
> A. The receive window is smaller than the bandwidth-delay product, so the sender exhausts the advertised window and stalls until ACKs return — a flow-control limit, not congestion.
> B. Congestion control operating normally: the sender probes upward until a real drop signals congestion, then multiplicatively decreases — the sawtooth is the algorithm working as designed.
> C. An oversized intermediate buffer absorbs overshoot instead of dropping, so the loss signal arrives only once the queue is saturated; the sender never sees a timely drop and latency inflates.
> D. Path reordering produces duplicate ACKs that trip fast-retransmit though little is truly lost, so the sender needlessly cuts its window.
> E. The path's available bandwidth is simply lower than the transfer demands; throughput is capacity-bound.

**Correct key: 1→A, 2→B, 3→C, 4→D. E unused.**

**Cross-viability (why the grid is dense):**

| Response | Surface-viable for | Attaches (under projection) to |
|---|---|---|
| A (window limit → stall) | 1, 4, and superficially 2 ("why not faster?") | 1 only — the stall-with-no-loss signature |
| B (normal congestion sawtooth) | 2, 4 (both show retransmits), 1 | 2 only — halving *coincides with real drops* on a clean path |
| C (bufferbloat) | 3, 1 (latency/stall confusion), 2 | 3 only — sustained throughput + inflated latency + ~no loss |
| D (reordering → spurious retransmit) | 4, 2 (both retransmit) | 4 only — fast-retransmits with *low actual loss, stable RTT* |
| E (capacity-bound) — orthodox lure | 1, 3, 4 (any slow transfer) | nothing — see below |

**Near-duplicate confusion cell:** prompts **2 and 4** (twin: both under-perform *with retransmits*) × responses **B and D** (twin: both about the loss/retransmit machinery). All four cells read as viable. The one differentiating projection: are the retransmits responding to **real drops** (2, clean LAN, rate halves at each drop → B) or to **reordering-induced duplicate ACKs** with little true loss (4 → D)? "There are retransmits" is the surface feature; *what the retransmits are responding to* is the projected differentiator. Cross-wiring 2↔4 / B↔D is the canonical transposition error.

**Orthodox-but-wrong distractor (E):** "insufficient bandwidth / capacity-bound" is the standard first diagnosis for any slow transfer — professionally common, reached for by convention. A learner deferring to it attaches prompt 1 or 4 to E. It matches nothing: 1 stalls with no loss on a 50 Mbps path (window, not capacity), 3 *sustains high throughput* (not capacity-bound), 4 carries the reordering signature. Attaching any prompt to E is the canonical selection error.

**Unique bijection:** 1 (stall, no loss) → only A; 3 (sustained throughput, high latency, no loss) → only C; 2 and 4 resolved to B and D by the near-duplicate projection; E excluded from all. No second complete assignment survives. Binary grade defensible.

**No-elimination-shortcut with D=1:** after correctly placing 1→A and 3→C, the learner still faces {2,4} × {B, D, E} — E remains cross-viable for both, so the final pairings are **not** a forced 2-cycle; the learner must genuinely project to resolve B vs D *and* to exclude E. The surplus does its job.

Every one of the five responses is a real TCP failure mode; nothing is rejectable on sight. Difficulty is structural.

### 8.2 Boundary-condition (condition → mechanism)

**Axis:** boundary-condition · **Concept:** tire thermal operating window · **Domain:** motorsport · **n=4, D=1, pool A–E.**

> Match each grip-loss situation to its mechanism. Not every mechanism is used.
>
> **Prompts:** 1. Out-lap, cold track, fresh tires: slides for two laps, then grip arrives and holds. · 2. Mid-stint, following closely through high-speed corners: fronts progressively lose bite; backing off a lap does **not** restore them, but a cooler sequence does. · 3. Late in a long stint, one compound: grip fades, surface marbled and greasy, **no** temperature management brings it back. · 4. Early in a stint, right after starting inflation was lowered: grip down from the first flying lap, flat all stint, tire runs **hotter** than telemetry expects.
>
> **Responses:** A. Passed its **wear** life — rubber spent (marbling), grip structurally gone regardless of temperature. · B. Core temp **below** the window — cold compound slides until worked into the window, then grip appears and holds. · C. The driver is **overdriving** — sliding the car and overworking the rubber; manage pace, not tire. · D. Surface temp **above** the window — overheated compound greases over, recovering only once it cools back in. · E. Inflation **outside** the target window — wrong pressure distorts the contact patch and shifts thermal behaviour, depressing grip all run.

**Correct key: 1→B, 2→D, 3→A, 4→E. C unused.**

Cross-viability: the shared surface fact is "grip is low"; the differentiator is *which threshold was crossed*, read only from the onset/recovery signature. A (wear) viable for 2,3 · B (under-temp) for 1,2,4 · C (overdriving, orthodox lure) for 2,3,4 · D (over-temp) for 2,3,4 · E (pressure) for 1,2,4.

Near-duplicate cell: **{2,3} × {D,A}** — both are stint-long grip fade with a greasy surface. The projected differentiator is **reversibility**: 2 recovers on cooling → thermal → D; 3 won't return under any temperature management, surface marbled → structural wear → A. Each twin prompt embeds its firing condition (recovers-on-cooling vs. never-recovers) — §13's over-specify-to-preserve-a-single-key rule in action.

Orthodox-but-wrong (C): "the driver's overdriving, manage the pace" is the reflexive explanation for any fading grip; convention pulls hard toward it. It matches nothing — every prompt carries a threshold signature (grip arriving on warm-up, recovering on cooling, marbling, tracking a pressure change) that driving style does not produce.

Unique bijection: 1 (grip *arrives*)→B · 3 (*irreversible* + marbled)→A · 2 (reversible on cooling)→D · 4 (whole-run flat + *hotter* after a pressure drop)→E · C nowhere. No-elimination-shortcut (D=1): after 1→B and 4→E, {2,3}×{A,D,C} stays contested — reversibility must be projected to split A from D and reject C.

### 8.3 Transfer (the hostile axis — keyword-collapse defeated by domain-vocabulary inversion)

Transfer is R-2's danger axis: the naive form is "match term to definition," pure surface. This example defeats that by construction — **every response is phrased in the vocabulary of a domain other than its correct prompt**, so keyword matching is misdirected and only the mechanism resolves the grid.

**Axis:** transfer · **Concept:** Little's Law (average work-in-progress = arrival rate × time-in-system, L = λW, in a stable system) · **prompts span four domains by design** · **n=4, D=1, pool A–E.**

> Match each situation to the statement that correctly states what Little's Law predicts. Not every statement is used.
>
> **Prompts:** 1. **Hospital ED** — arrivals steady; a fast-track lane cuts each patient's average time in the department. · 2. **Software team** — ticket intake rate held constant; a strict work-in-progress cap enforced on the board. · 3. **Coffee shop** — a promotion lifts the walk-in rate by half, but the counter still serves faster than customers arrive. · 4. **Factory** — sales doubles the order arrival rate, past what the unchanged machines can complete.
>
> **Responses:** A. When customers arrive faster than the counter can ever serve them, there is no steady line length — the queue grows without bound. · B. At a fixed inflow rate, shortening the time each item is held in the buffer lowers the average number buffered. · C. Since throughput is work over time, cutting the time each item spends in the system raises the number processed per hour. · D. To hold the number of units on the floor at the imposed ceiling while the line keeps admitting parts at the same rate, each part's time on the floor is driven down. · E. With treatment capacity and per-patient time unchanged, a higher but still-manageable admission rate raises the ward's census proportionally to a new, stable level.

**Correct key: 1→B, 2→D, 3→E, 4→A. C unused.**

Keyword-lure table — every surface cue misleads:

| Response | Phrased in | Keyword-lures toward | Mechanism resolves to |
|---|---|---|---|
| A | coffee-shop | prompt 3 (coffee) ✗ | **4** — arrivals exceed capacity → unbounded |
| B | network/buffer | *no networking prompt exists* | **1** — fixed λ, cut W → L falls |
| D | factory | prompt 4 (factory) ✗ | **2** — clamp L at fixed λ → W falls |
| E | hospital | prompt 1 (hospital ED) ✗ | **3** — higher-but-servable λ → bounded rise |
| C | neutral | — | nothing |

Three of four responses keyword-lure toward the *wrong* prompt (A→3, D→4, E→1); the fourth (B) has no keyword home at all, forcing mechanism reasoning. Domain matching scores near zero.

Two near-duplicate cells: **{1,2}×{B,D}** — the dual levers of L=λW; the split is *which variable the intervention clamps* (1's fast-track clamps W directly → count falls → B; 2's cap clamps L directly → time-in-system falls → D). **{3,4}×{E,A}** — the **stability boundary**; arrivals still servable (3 → bounded proportional rise → E) vs. exceeding capacity (4 → no steady state → A). Little's Law holds only for a stable system, so a learner who lifts "more arrivals → proportionally more in system" past the boundary mis-assigns.

Orthodox-but-wrong (C): "throughput = work/time, so cutting time-in-system raises throughput" — the canonical Little's Law misapplication, surface-fitting prompts 1 and 2. It matches nothing: stable-system throughput equals the arrival rate, which 1 and 2 both hold fixed.

Unique bijection: 1→B, 2→D, 3→E, 4→A; C nowhere. No-elimination-shortcut (D=1): after 1→B and 2→D, {3,4}×{E,A,C} stays contested — the stability boundary must be projected to split E from A and reject C.

**Construction rule this example promotes (REQ-MAT-F-020):** for the transfer axis, phrase each response in a domain *other* than its correct prompt (domain-vocabulary inversion), so surface matching is systematically misdirected and the grid is resolvable only on mechanism. This is the transfer axis's answer to R-2.

---

## 9. Limit-test example (justifies edge cases in §13)

Built to expose the two matching-specific ceilings the §8 examples (all n=4) do not: **n=3 (worst elimination pressure)** and a **near-duplicate pushed to the defensibility boundary**. (The transfer keyword-collapse ceiling is fully worked in §8.3.)

**Axis:** boundary-condition · **Concept:** backpressure (bounded-queue flow control) · **n=3, D=2, pool A–E.** Three *different-domain* systems each under a load condition; responses are mechanism-level descriptions of what the bounded queue does *in that system's own terms*.

**Limit findings the type must codify:**

- **n=3 elimination pressure.** With only three prompts, a single surplus response is thin — after two correct placements the third is nearly forced. Mitigation: at n=3, `D ≥ 2` (not just ≥1), and the near-duplicate cell must span the *last-resolved* prompts so the grid cannot unzip. Captured as a risk (R-1) and a validation refinement.
- **Keyword collapse (cross-ref §8.3).** The transfer axis's failure mode — the grid degenerating to term→definition — and its fix, **domain-vocabulary inversion (REQ-MAT-F-020)**, are fully demonstrated in §8.3. At n=3 the same rule applies with less slack: fewer prompts means fewer domains to invert across, so the inversion must be exact or the grid leaks a keyword home.
- **Near-duplicate at the defensibility boundary.** As in Ordering's limit test, a near-duplicate response can read as *also correct* for its twin prompt ("that mechanism is true of both systems"). The hole is closable only by embedding in each twin prompt the one condition its correct response fires on — and if that cannot be done without leaking the pairing, regenerate. This proves the same two rules Ordering needed: (1) a prompt sometimes must over-specify its distinguishing condition to preserve a single key, and (2) if it cannot without leaking, regenerate.

---

## 10. Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-MAT-F-001 | `select_question_type.py` returns one of `mcq`/`msq`/`ordering`/`matching` | script |
| REQ-MAT-F-002 | On Trial 1, load `MATCHING_PROMPT` alongside the other prompts; unreadable → halt | SKILL.md |
| REQ-MAT-F-003 | Matching trial presents **MAT** on its own line, a numeric prompt list (1…n), an alpha response pool (A…m > n), and a closing prompt disclosing the matching constraint: each prompt takes exactly one response, each response is used at most once, and some responses go unused. Response labels are shuffled so the correct pairing is not the identity diagonal (1→A, 2→B, …) | MATCHING_PROMPT |
| REQ-MAT-F-004 | Every response is cross-viable for ≥2 prompts; every prompt has ≥2 surface-viable responses; no pairing recoverable by lexical/category/textbook overlap or by elimination. Surplus D ≥ 1 (D ≥ 2 when n = 3); the no-elimination-shortcut simulation passes — after any subset of prompts is correctly matched, every remaining prompt still faces ≥2 surface-viable responses | MATCHING_PROMPT |
| REQ-MAT-F-005 | The correct assignment is a unique injective bijection under the axis; no second complete assignment survives projection | MATCHING_PROMPT |
| REQ-MAT-F-006 | ≥1 near-duplicate confusion cell (2 twin prompts × 2 twin responses, all four cells surface-viable, diagonal fixed only under projection); ≥1 orthodox-but-wrong distractor response; each distractor fails for a distinct reason, only under projection | MATCHING_PROMPT |
| REQ-MAT-F-007 | Parse response as a set of n prompt→response pairs; injective (no response reused, no prompt doubled); repeated/omitted prompt, reused response, or out-of-range label → resubmit | SKILL.md |
| REQ-MAT-F-008 | Grade correct iff every prompt→response pair equals the key exactly (binary; D distractors unused) | SKILL.md |
| REQ-MAT-F-009 | Feedback decomposes error into selection (prompt attached to a distractor; correct response left unused) and assignment (transposed pairs); each addressed individually; name the orthodox-but-wrong distractor; resolve the near-duplicate cell | SKILL.md / MATCHING_PROMPT |
| REQ-MAT-F-010 | At intake, the orchestrator determines once whether the concept affords ≥3 confusable cases with distinct cross-viable outcomes (`MATCHABLE`). If not, exclude `matching` from the session's type draw. Combines with the procedural gate: excludes may be `ordering`, `matching`, or both (comma-joined) | SKILL.md |
| REQ-MAT-F-011 | `select_question_type.py --exclude` accepts multiple comma-delimited types and draws from the remainder (already supported; add `matching` to the valid set) | script |
| REQ-MAT-F-012 | Matching construction consumes the intake `DOMAIN` (Step I3) and prioritized focus areas (Step I4), identically to the other types | MATCHING_PROMPT |
| REQ-MAT-F-013 | Matching prompts and responses obey the banned-language lists and abstraction-boundary rules; add: no sequencing/pointer cues that pre-wire a pairing; topic keyword unavoidable in prompts and responses | MATCHING_PROMPT |
| REQ-MAT-F-014 | Each matching case-set is fresh within the session and across prior sessions on the same concept | MATCHING_PROMPT |
| REQ-MAT-F-015 | On re-presentation (tangent resume, or after a clarification), the trial is shown with the same prompts, responses, and labels — no re-shuffle, no regeneration | SKILL.md |
| REQ-MAT-F-016 | Axis re-draw bookkeeping: a rejected axis is not recorded as used and stays available to later trials; only the finally-used axis enters the session's axis-exclusion list and Axis Coverage | SKILL.md |
| REQ-MAT-F-017 | The report's Gap Inventory entry for a matching trial states the submitted pairs, the correct key, Selection errors (attachments to distractors; unused correct responses), and Assignment errors (transposed pairs), each decomposed | SKILL.md |
| REQ-MAT-F-018 | Analysis-phase classification interprets matching's dual error structure: a single transposition in the near-duplicate cell with otherwise-correct pairs reads as a surface gap; repeated attachment to the orthodox-but-wrong distractor, or errors spanning both selection and assignment across trials, reads as a fundamental gap | SKILL.md |
| REQ-MAT-F-019 | Presentation and parsing: prompts one per numbered line, responses one per lettered line; accept the learner's pairs in common formats (`1-C`, `1:C`, `1C`, `1 → C`, comma/newline separated), case-insensitive; numeric prompt labels and alpha response labels are disjoint, so pair-token order (`1-C` or `C-1`) parses unambiguously | SKILL.md |
| REQ-MAT-F-020 | **Transfer-axis domain-vocabulary inversion:** on a `transfer` trial, each response is phrased in the vocabulary of a domain other than its correct prompt, so surface/keyword matching is systematically misdirected and the grid is resolvable only on the concept's mechanism. This is the transfer axis's construction answer to the keyword-collapse risk (R-2); worked in §8.3 | MATCHING_PROMPT |
| REQ-MAT-F-021 | Internal record & report: the per-trial record uses `question_type: matching` and populates `probe_target` (the discrimination tested, ≤6 words — e.g. "reversible vs. structural grip loss") and, on error, `gap_summary` (mis-attachments to distractors, unused correct responses, transpositions); the report Trial Log `Type` column shows **MAT**. Analogue of REQ-ORD-F-009; pairs with F-009 (feedback) and F-017 (Gap Inventory) | SKILL.md |
| REQ-MAT-E-001 | `MATCHING_PROMPT` unreadable → halt (extend existing REQ-MCQ-E-001) | SKILL.md |
| REQ-MAT-E-002 | Response with a repeated prompt, a reused response, an out-of-range label, a missing prompt, or otherwise unparseable → ask to resubmit; do not count. A well-formed set that attaches a prompt to a distractor is **valid and incorrect**, not a resubmit | SKILL.md |
| REQ-MAT-E-003 | For a matchable concept, if the assigned axis cannot make this trial's grid projection-resolvable, re-draw the axis (exclude used + rejected); on exhaustion, hold the axis and reconstruct the case-set. No mid-trial type substitution | SKILL.md / MATCHING_PROMPT |

---

## 11. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-1 | Surface association leak (hole in one) | A response keyword/category/textbook-matches exactly one prompt | Pairing solvable without projection; trial is a knowledge quiz | **No** — cross-viability validation forbids; regenerate the response |
| FM-2 | Elimination / parity leak | Equal-size bijection, or surplus too thin at small n | Last pair(s) forced for free | **No** — surplus D≥1 (D≥2 at n=3) + no-elimination-shortcut simulation |
| FM-3 | Ambiguous key (multiple valid bijections) | Generator leaves a second complete assignment defensible | Binary grade marks a valid answer wrong | **No** — unique-bijection validation; regenerate |
| FM-4 | Distractor genuinely belongs to a prompt | A distractor is a defensible match under the axis | Learner penalized for a valid attachment | **No** — sharpen the distractor or embed the gating condition in the prompt |
| FM-5 | Near-duplicate cell reads as both-valid | Twin response defensible for both twin prompts | Two valid readings, ungradeable | **No** — embed each twin's firing condition, or regenerate (near-duplicate-forces-ambiguity) |
| FM-6 | Learner submits wrong count (missing/extra prompt) | Learner error | Malformed → resubmit (not counted); a complete set with a distractor attached is incorrect, not resubmit | **Yes** — documented parse rule |
| FM-7 | D derivable from visible counts | Two lists printed, m and n visible | Learner knows how many responses go unused | **Yes** — does not leak *which*; unused responses are cross-viable |
| FM-8 | `matching` drawn but MATCHING_PROMPT unreadable | Missing file | Halt (REQ-MAT-E-001) | **Yes** — halt is correct |
| FM-9 | Distribution shifts to 1/4 each | Adding to TYPES | Fewer MCQ/MSQ/ORD per session | **Yes** — intended; note for calibration |
| FM-10 | Assigned axis can't make a resolvable grid (matchable concept) | Bad axis×concept pairing | Grid surface-solvable or unforced | **Yes, via guard** — re-draw axis; on exhaustion reconstruct case-set (REQ-MAT-E-003) |
| FM-11 | Concept is flat — no confusable case structure | Concept has one definition, no variants | No valid matching trial exists | **Yes, via guard** — intake gate excludes matching from the type draw (REQ-MAT-F-010) |
| FM-12 | Two intake gates interact (non-procedural AND flat) | Concept excludes both ordering and matching | Type draw is mcq/msq only | **Yes** — excludes combine (comma-joined); script errors only if *all* types excluded |

---

## 12. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Small n (3) makes elimination hard to defeat | High | Med | D≥2 at n=3; near-duplicate cell spans last-resolved prompts; no-elimination-shortcut simulation mandatory in validation |
| R-2 | Cross-viability collapses to keyword matching (esp. recognition/transfer axes) | High | High | Role-selection maps prompt/response to *mechanism*, not label; ban surface differentiators; per-axis dry-run gate before ship |
| R-3 | Matching harder than the other types → skews pass rate | Med | Low | Binary grade consistent; threshold unchanged; reweight distribution if data warrants |
| R-4 | Grading disputes / near-duplicate ambiguity | Med | Med | Unique-bijection validation; regenerate-on-ambiguity (FM-5); construction-defect replace protocol |
| R-5 | Response pool up to 10 inflates cognitive load | Med | Low | Cap D≤3; prompts ≤3 sentences, responses ≤2 |
| R-6 | `select_mcq_axis.py` name now serves 4 types | High | Low | Accept as debt; rename out of scope |
| R-7 | Two intake gates raise intake complexity / mis-gating | Med | Med | Single combined determination step at intake; explicit combined-exclude requirement (REQ-MAT-F-010); document the mcq/msq-only fallback |

---

## 13. Edge cases (for `MATCHING_GENERATION_PROMPT.md`)

| Edge case | Resolution |
|---|---|
| surface-association-leak | A response resolvable by keyword/category/textbook overlap with one prompt → regenerate it as cross-viable (plausible for ≥2 prompts, differentiator projected only). Do not output while any cell is surface-solvable. |
| elimination-shortcut | After simulating correct placement of any subset, a remaining prompt is forced → add/strengthen a cross-viable distractor (raise D), or re-site the near-duplicate cell. Do not output while any prompt is forced by elimination. |
| ambiguous-key | A second complete bijection survives projection → tighten a prompt's distinguishing condition or replace a response until exactly one assignment survives. |
| distractor-actually-belongs | A distractor is a defensible match under the axis → sharpen it, or embed in the target prompt the gating condition its true response fires on, so the distractor's omission of that condition becomes the error. Do not output while any distractor is a defensible pick. |
| near-duplicate-forces-ambiguity | The twin response cannot be made wrong for its off-diagonal prompt without a prompt leaking its pairing → regenerate the cell or the trial. |
| unfit-axis-for-concept | Matchable concept, but the assigned axis can't make a resolvable grid → re-draw axis (exclude used + rejected); on exhaustion reconstruct the case-set. No type substitution (REQ-MAT-E-003). |
| non-matchable-concept | Concept affords no confusable case structure → excluded at intake: `matching` dropped from the type draw (REQ-MAT-F-010). Never reaches construction. |
| learner-malformed-response | Repeated prompt, reused response, out-of-range label, or missing prompt → resubmit; do not count. A well-formed set that attaches a prompt to a distractor is valid-and-incorrect. |
| learner-challenges-question | If a genuine second valid bijection exists, it is a construction defect — acknowledge, replace, do not count. Otherwise hold the evaluation and explain the axis. |
| repeated-probe-scenario-availability | Change the domain anchor for the new session; axis and concept unchanged. |

---

## 14. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/prompts/MATCHING_GENERATION_PROMPT.md` | Create | Full XML generation prompt mirroring ORDERING's structure + matching constructs (grid-design law, near-duplicate cell, orthodox distractor, unique bijection) | Governs matching construction/eval |
| `mcq-probe/scripts/select_question_type.py` | Modify | Add `"matching"` to `TYPES` (`--exclude` already supports multiple) | Enables matching selection; lets the intake gate drop matching for flat concepts |
| `mcq-probe/SKILL.md` | Modify | Intake matchable gate (+ combined exclude), Constants, Active Constraints, prompt-load, trial-loop present/wait/evaluate + axis re-draw (+ bookkeeping), re-presentation stability, Response Protocol (Matching), record schema, Report (Type col + Gap Inventory format + analysis classification), Error Handling (extend E-001, add E-002/E-003) | Wire matching into orchestration |
| `mcq-probe/scripts/select_mcq_axis.py` | None | — | Axis-agnostic; reused as-is |
| `CLAUDE.md` (repo doctrine) | Optional note | Mention matching alongside MCQ/MSQ/Ordering in the "adding a question type" section | Keep doctrine current |

---

## 15. Open questions

| # | Question | Blocker for? | Recommendation |
|---|---|---|---|
| 1 | Surplus responses (n prompts, n+D responses) vs equal-size bijection | Whole design | **Surplus** — the parity/elimination leak makes an equal-size bijection surface-solvable at the last pair(s). Load-bearing. |
| 2 | Binary all-or-nothing vs partial credit | Grade + report | **Binary** — matches the skill and the spec ("match all the pairs"). |
| 3 | Injective (no reuse) vs reusable responses | Grid model + near-duplicate device | **No reuse** — reuse dissolves the 2×2 near-duplicate cell and muddies the binary grade. |
| 4 | Intake `MATCHABLE` gate vs no gate (construct always) | Orchestration | **Add the gate**, mirroring the procedural gate — keeps flat concepts from producing weak trials. |
| 5 | Equiprobable 1/4 vs weighted distribution | select_question_type | **Equiprobable**, revisit after pass-rate data. |
| 6 | Label scheme: numeric prompts + alpha responses vs alpha both | Prompt wording + parse | **Numeric prompts, alpha responses** — removes prompt/response confusion in the reply. |
| 7 | Disclose that D responses are unused (counts visible) vs hide | Prompt wording | **Visible** — both lists are printed; D is derivable and does not leak *which* responses are unused. |

---

## 16. Implementation order

1. ~~Confirm the readback (§0) and OQ 1–7.~~ **Done.** Resolved per §5; the surplus-response interpretation (OQ 1) is load-bearing throughout the shipped generation prompt.
2. ~~Author `MATCHING_GENERATION_PROMPT.md`~~ **Done** — full XML: purpose, 9 axes reframed for matching (prompt-role→response-role semantic + wrong-attachment failure mode per axis; the `transfer` reframing carries the domain-vocabulary-inversion rule, REQ-MAT-F-020), question/prompt/response requirements, the grid-design law (§4) and required constructs, construction sequence + validation checklist (§6), feedback protocols (§7), edge cases (§13). The prompt ships **three** representative worked examples spanning the size range — transfer (n=4/D=1), application (n=3/D=2), observability (n=6/D=3) — matching the lean worked-examples convention of MCQ/MSQ/ORDERING. The full 9-axis gate evidence and the axis-fit fallback exercises are recorded in **Appendix A** below, not embedded in the runtime prompt (see the prompt-alignment note under step 5).
3. ~~Modify `select_question_type.py`~~ **Done** — `"matching"` is in `TYPES`.
4. ~~Modify `SKILL.md`~~ **Done** — Intake Phase (matchable determination → combined `--exclude`), File Path Constants, Active Constraints, prompt-load, Trial-loop present/wait/evaluate + axis re-draw, Response Protocol (Matching correct/incorrect), internal record schema, Report Format (Type column + Gap Inventory), Error Handling (E-001/E-002/E-003) are all wired.
5. **Mandatory gate — Done.** All 9 axes were dry-run against the internal-validation checklist (§6), each confirmed dense/cross-viable/uniquely-resolvable; the axis-fit fallback (construction-sequence step 2 / REQ-MAT-E-003) is exercised for all three hostile axes (recognition, transfer, coupling). Full worked evidence is in **Appendix A**. Results summarized below.

   **Prompt-alignment note (Opus review).** As first built, all nine gate examples plus the fallback exercises were embedded in `MATCHING_GENERATION_PROMPT.md`'s `<worked-examples>`/`<axis-fit-fallback-exercises>`, making that prompt ~138 KB — roughly 3× its siblings (MCQ 43 KB, MSQ 44 KB, ORDERING 59 KB), all of which keep only 1–2 illustrative examples and no fallback-exercises section (they handle axis-fit in construction-sequence step 2 + the `unfit-axis` edge-case, which matching also does). The prompt is loaded into context on Trial 1 of every session, so this was a standing ~80 KB context tax and a structural divergence from the sibling prompts. Resolved by trimming the prompt to three representative exemplars (spanning the n/D range) and relocating the remaining six examples and the fallback exercises to Appendix A. The prompt is now 85 KB. The 9-axis gate result stands — the evidence moved, it was not discarded.
6. Optional: reweight type distribution after observing pass rates; add the CLAUDE.md doctrine note.

### Dry-Run Gate Results (§16 step 5)

| Axis | Concept (domain) | n/D | Near-duplicate cell | Orthodox-but-wrong | Fallback exercised | Verdict |
|---|---|---|---|---|---|---|
| failure-diagnosis | TCP throughput anomalies (networking) | 4/1 | prompts 2×4, responses B×D | E — capacity-bound first guess | — (example 1, pre-existing) | PASS |
| boundary-condition | Tire thermal window (motorsport) | 4/1 | prompts 2×3, responses D×A | C — "driver overdriving" | — (example 2, pre-existing) | PASS |
| transfer | Little's Law (multi-domain: hospital/software/coffee/factory) | 4/1 | two cells: {1,2}×{B,D}, {3,4}×{E,A} | C — throughput-from-time-cut misapplication | Yes — exercise 1, concept without a non-strained cross-domain analogue (SameSite cookies), redraws to boundary-condition | PASS |
| recognition | Concurrency bug classification (software) | 4/1 | prompts 1×3 (deadlock/livelock), responses B×E | D — "split the lock" | Yes — exercise 1, concept with no true-identity ambiguity (retry-backoff params), redraws to application | PASS |
| application | Retry-with-backoff outcomes (distributed systems) | **3/2** | prompts 1×2, responses C×E | A — jitter-benefit generalization | — | PASS |
| time | Read-after-write visibility (replication + cache TTL) | 4/1 | prompts 3×4, responses A×D | C — fresh-means-current misconception (verdict-wrong on both cache prompts) | — | PASS (corrected — see review note) |
| risk | Schema-migration constraints (databases) | **5/2** | prompts 1×2, responses C×F | E — "wrap it in a transaction"; G — stale planner statistics | — | PASS |
| coupling | Service-decomposition arrangements (architecture) | 4/1 | prompts 1×3, responses D×E | C — "separate databases ⇒ decoupled" | Yes — exercise 3, concept with no second component to entangle with (hash table resizing), redraws to boundary-condition | PASS |
| observability | Monitoring-signal selection (SRE) | **6/3** | prompts 2×4, responses A×E | C — aggregate dashboard; F — tracing; H — error-log volume | — | PASS |

**Overall verdict: PASS, 9/9 (after review correction).** Every axis produces a grid satisfying the full internal-validation checklist (§6): cross-viability in both directions, no-elimination-shortcut, a unique bijection, ≥1 near-duplicate cell, and ≥1 orthodox-but-wrong distractor whose failure is argued explicitly rather than asserted. The examples now span the parameter ranges — n ∈ {3,4,5,6}, D ∈ {1,2,3} — rather than sitting entirely at n=4/D=1; the n=3/D≥2 floor from §5 is exercised directly by the application example (its annotation shows why D=1 would leave a forced 2-cycle at n=3), and the n=6/D=3 observability example exercises the ceiling. n=7 remains untested by the gate (constructed identically to n=6 with one more case) and is a construction-time responsibility. The three hostile axes named in this gate (R-2) each additionally demonstrate the axis-fit-rejection path firing on a genuinely mismatched concept and landing cleanly on a fitting axis, closing out R-1/R-2/R-4 as mitigated rather than merely designed-for. This clears the item explicitly deferred at merge in commit `6715bc8`.

**Review correction (Opus review of commit `f5b7d1a`).** The self-certified 9/9 was, as first shipped, 8/9. Two defects were found on independent projection and fixed before merge:

- **Example 6 (time axis) — ambiguous key (blocker, FM-3/FM-4, REQ-MAT-F-005).** The original orthodox-but-wrong distractor C used a write-relative-TTL rule ("any read within 60s of the write returns the pre-write value"). Because prompts 3 and 4 are both read 3 seconds after their writes, that rule returns the same verdict for both twins and coincided with prompt 3's true "old value" outcome — making `3→C` a genuinely defensible pairing and leaving a second complete bijection (`1→E, 2→B, 3→C, 4→D`, A unused). Fixed by replacing C with the **fresh-means-current** misconception (a within-TTL entry is "fresh → returns the new value"), which is verdict-wrong on *both* cache prompts (3 truly returns old, 4 truly returns new) and inapplicable to the cache-less replica prompts 1/2 — so C now matches no prompt and the bijection is unique.
- **Example 4 (recognition) — near-free prompt (soft spot, grid-design-law part 4).** Prompt 2 (starvation) had only one surface-viable response (C). Reworded so its "stays runnable the whole time" framing also draws E (livelock) on the surface, restoring the "no free prompt" property; projection still fixes 2→C because the thread never retries in response to a peer.

- **All-examples-at-n=4/D=1 — few-shot structural anchoring bias (R-1 adjacent).** As first shipped, all nine worked examples sat at n=4/D=1, which biases the generator's per-trial n/D selection toward that single point and, worse, points it at the forbidden D=1 corner on the rare n=3 deviation. Fixed by diversifying three examples to span the ranges — application → **n=3/D=2** (the safety-critical floor; its annotation demonstrates why D=1 would leave a forced 2-cycle), risk → **n=5/D=2**, observability → **n=6/D=3** (ceiling) — and adding an explicit anti-anchoring directive in both the worked-examples preamble and the `<count>` construction step instructing per-concept n/D selection over example-matching. Final spread: n ∈ {3,4,5,6}, D ∈ {1,2,3}.

These fixes preserve the correct keys, the near-duplicate cells, and file XML well-formedness (verified: all nine examples' declared n/D/pool match their actual prompt/response counts and key length). Process note: the prior gate was run and self-certified by the same agent that authored the examples; example 6's annotation openly rationalized the coincidence ("coincides with the correct verdict once") rather than flagging it, and the exemplar monoculture was reinforced rather than caught. Treat future self-run gates as provisional until independently projected.


---

## Appendix A — Relocated gate evidence (9-axis dry-run)

These are the six worked examples and the three axis-fit fallback exercises that were **removed from** `MATCHING_GENERATION_PROMPT.md` during the Opus prompt-alignment pass (§16 step 5, prompt-alignment note) and preserved here. Together with the three examples retained in the prompt (transfer, application, observability) they constitute the full per-axis dry-run gate. They are the authoritative construction evidence; they are **not** loaded at runtime.

**Original gate numbering** (used by the `id` attributes below and by the "example N" cross-references inside the fallback exercises):

| # | Axis | Concept | n/D | Location now |
|---|---|---|---|---|
| 1 | failure-diagnosis | TCP throughput anomalies | 4/1 | Appendix A |
| 2 | boundary-condition | Tire thermal window | 4/1 | Appendix A |
| 3 | transfer | Little's Law | 4/1 | **prompt (example 1)** |
| 4 | recognition | Concurrency bug classification | 4/1 | Appendix A |
| 5 | application | Retry-with-backoff | 3/2 | **prompt (example 2)** |
| 6 | time | Read-after-write visibility | 4/1 | Appendix A |
| 7 | risk | Schema-migration constraints | 5/2 | Appendix A |
| 8 | coupling | Service decomposition | 4/1 | Appendix A |
| 9 | observability | Monitoring-signal selection | 6/3 | **prompt (example 3)** |

### A.1 — Removed worked examples (gate ids 1, 2, 4, 6, 7, 8)

```xml
    <example id="1" axis="failure-diagnosis" n="4" d="1" pool="A-E" correct-key="1-A,2-B,3-C,4-D">
      <concept>TCP throughput anomalies (congestion control × flow control)</concept>
      <domain>abstract</domain>

      <stem>
        Match each observed transfer symptom to its root cause. Not every
        cause is used.
      </stem>

      <prompts>
        <item label="1">
          A bulk transfer over a long-RTT satellite link plateaus near
          2 Mbps though the path supports 50 Mbps; a capture shows the
          sender repeatedly stops sending and waits, then resumes — with no
          retransmissions.
        </item>
        <item label="2" role="near-duplicate" pair-with="4">
          A transfer over a clean gigabit LAN peaks, then repeatedly halves
          its rate in a regular sawtooth, with a retransmission at each
          drop.
        </item>
        <item label="3">
          A transfer through a device with a very large buffer sustains
          high throughput, but end-to-end latency climbs to several
          seconds and stays there; almost no packets are lost.
        </item>
        <item label="4" role="near-duplicate" pair-with="2">
          A transfer over WiFi runs well below capacity with frequent
          fast-retransmits, though the link's actual loss rate is low and
          RTT is stable.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for" pair-with="1">
          The receive window is smaller than the bandwidth-delay product,
          so the sender exhausts the advertised window and stalls until
          ACKs return — a flow-control limit, not congestion.
        </item>
        <item label="B" role="correct-for near-duplicate" pair-with="2">
          Congestion control operating normally: the sender probes upward
          until a real drop signals congestion, then multiplicatively
          decreases — the sawtooth is the algorithm working as designed.
        </item>
        <item label="C" role="correct-for" pair-with="3">
          An oversized intermediate buffer absorbs overshoot instead of
          dropping, so the loss signal arrives only once the queue is
          saturated; the sender never sees a timely drop and latency
          inflates.
        </item>
        <item label="D" role="correct-for near-duplicate" pair-with="4">
          Path reordering produces duplicate ACKs that trip fast-retransmit
          though little is truly lost, so the sender needlessly cuts its
          window.
        </item>
        <item label="E" role="orthodox-but-wrong">
          The path's available bandwidth is simply lower than the transfer
          demands; throughput is capacity-bound.
        </item>
      </responses>

      <correct-key>1→A, 2→B, 3→C, 4→D (E unused)</correct-key>

      <annotation>
        Labeling note: for readability this example's key is shown running
        1→A … 4→D (the identity diagonal). A shipped trial MUST NOT do this —
        the response labels are shuffled so the key is never the identity
        diagonal (see label-and-shuffle and the internal-validation
        checklist; examples 2 and 3 show the shuffled form). The diagonal
        here is a presentation choice for this illustration only.

        Cross-viability: A (window limit → stall) is surface-viable for 1,
        4, and softly for 2 ("why not faster?"); it resolves under
        projection to 1 only — the stall-with-no-loss signature. B (normal
        congestion sawtooth) is surface-viable for 2, 4 (both show
        retransmits), and softly for 1; it resolves to 2 only, because the
        rate-halving coincides with real drops on a clean path. C
        (bufferbloat) is surface-viable for 3, softly for 1
        (latency/stall confusion) and 2; it resolves to 3 only — sustained
        throughput, inflated latency, near-zero loss. D (reordering →
        spurious retransmit) is surface-viable for 4 and 2 (both
        retransmit); it resolves to 4 only — fast-retransmits with low
        actual loss and stable RTT. E (capacity-bound, the orthodox lure)
        is surface-viable for 1, 3, and 4 — any slow transfer invites it —
        and resolves to nothing.

        Near-duplicate confusion cell: prompts 2 and 4 (twin: both
        under-perform with retransmits present) crossed with responses B
        and D (twin: both describe the retransmit machinery). All four
        cells read as viable on first pass. The one differentiating
        projection: are the retransmits responding to real drops (prompt
        2, clean LAN, rate halves at each drop → B) or to
        reordering-induced duplicate ACKs with little true loss (prompt 4
        → D)? "There are retransmits" is the surface feature shared by
        both twins; WHAT the retransmits are responding to is the
        projected differentiator. Cross-wiring 2↔4 / B↔D is the canonical
        transposition error for this trial.

        Orthodox-but-wrong (E): "insufficient bandwidth / capacity-bound"
        is the standard first diagnosis reached for on any slow transfer —
        professionally common, defensible in isolation. A learner
        deferring to convention attaches prompt 1 or prompt 4 to E. It
        matches nothing: prompt 1 stalls with no loss on a 50 Mbps path (a
        window limit, not a capacity limit); prompt 3 sustains high
        throughput (not capacity-bound at all); prompt 4 carries the
        reordering signature, not a capacity signature. Attaching any
        prompt to E is the canonical selection error for this trial.

        Unique bijection: prompt 1 (stall, no loss) resolves only to A;
        prompt 3 (sustained throughput, high latency, near-zero loss)
        resolves only to C; prompts 2 and 4 resolve to B and D
        respectively only once the near-duplicate cell's differentiator is
        projected; E attaches to nothing. No second complete assignment
        survives.

        No-elimination-shortcut (D=1): after correctly placing 1→A and
        3→C, the learner still faces {2,4}×{B,D,E} — E remains cross-
        viable for both remaining prompts, so the final pairings are not a
        forced 2-cycle; the learner must genuinely project to resolve B
        vs. D AND to exclude E. The surplus does its job even this late in
        the grid.

        Every one of the five responses is a real TCP failure mode;
        nothing is rejectable on sight. Difficulty is structural, not a
        setting.
      </annotation>
    </example>

    <example id="2" axis="boundary-condition" n="4" d="1" pool="A-E" correct-key="1-B,2-D,3-A,4-E">
      <concept>Tire thermal operating window</concept>
      <domain>motorsport</domain>

      <stem>
        Match each grip-loss situation to its mechanism. Not every
        mechanism is used.
      </stem>

      <prompts>
        <item label="1">
          Out-lap, cold track, fresh tires: slides for two laps, then grip
          arrives and holds.
        </item>
        <item label="2" role="near-duplicate" pair-with="3">
          Mid-stint, following closely through high-speed corners: fronts
          progressively lose bite; backing off a lap does not restore
          them, but a cooler sequence does.
        </item>
        <item label="3" role="near-duplicate" pair-with="2">
          Late in a long stint, one compound: grip fades, surface marbled
          and greasy, no temperature management brings it back.
        </item>
        <item label="4">
          Early in a stint, right after starting inflation was lowered:
          grip down from the first flying lap, flat all stint, tire runs
          hotter than telemetry expects.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for near-duplicate" pair-with="3">
          Passed its wear life — rubber spent (marbling), grip structurally
          gone regardless of temperature.
        </item>
        <item label="B" role="correct-for" pair-with="1">
          Core temp below the window — cold compound slides until worked
          into the window, then grip appears and holds.
        </item>
        <item label="C" role="orthodox-but-wrong">
          The driver is overdriving — sliding the car and overworking the
          rubber; manage pace, not tire.
        </item>
        <item label="D" role="correct-for near-duplicate" pair-with="2">
          Surface temp above the window — overheated compound greases
          over, recovering only once it cools back in.
        </item>
        <item label="E" role="correct-for" pair-with="4">
          Inflation outside the target window — wrong pressure distorts the
          contact patch and shifts thermal behaviour, depressing grip all
          run.
        </item>
      </responses>

      <correct-key>1→B, 2→D, 3→A, 4→E (C unused)</correct-key>

      <annotation>
        Cross-viability: the shared surface fact across all four prompts
        is "grip is low" — the differentiator in every case is WHICH
        threshold was crossed, legible only from the onset and recovery
        signature. A (wear) is surface-viable for prompts 2 and 3. B
        (under-temp) is surface-viable for 1, 2, and 4. C (overdriving,
        the orthodox lure) is surface-viable for 2, 3, and 4 — any fading
        grip invites it. D (over-temp) is surface-viable for 2, 3, and 4.
        E (pressure) is surface-viable for 1, 2, and 4.

        Near-duplicate confusion cell: prompts 2 and 3 (twin: both
        stint-long grip fade with a greasy surface) crossed with responses
        D and A (twin: both describe irreversible-reading grip loss). The
        projected differentiator is REVERSIBILITY: prompt 2 recovers on a
        cooler sequence — thermal, not structural — resolving to D; prompt
        3 does not recover under any temperature management, and the
        surface is marbled — structural wear — resolving to A. Each twin
        prompt embeds its own firing condition (recovers-on-cooling vs.
        never-recovers) precisely so the cell is resolvable without
        leaking the pairing — the over-specify-to-preserve-a-single-key
        rule in action (see the near-duplicate-forces-ambiguity edge
        case).

        Orthodox-but-wrong (C): "the driver is overdriving, manage the
        pace" is the reflexive explanation for any fading grip —
        convention pulls hard toward it precisely because it requires no
        telemetry to defend. It matches nothing: every prompt carries a
        threshold signature (grip arriving on warm-up, recovering on
        cooling, marbling with no recovery, a whole-run flat deficit
        tracking a pressure change) that a driving-style explanation does
        not produce and cannot account for.

        Unique bijection: prompt 1 (grip arrives after two laps) resolves
        only to B; prompt 3 (irreversible, marbled) resolves only to A;
        prompt 2 (reversible on cooling) resolves only to D; prompt 4
        (whole-run flat, runs hotter, follows a pressure change) resolves
        only to E; C attaches to nothing. No second complete assignment
        survives.

        No-elimination-shortcut (D=1): after correctly placing 1→B and
        4→E, the learner still faces {2,3}×{A,D,C} — reversibility must
        still be projected to split A from D and to reject C; the pairing
        does not unzip early.
      </annotation>
    </example>

    <example id="4" axis="recognition" n="4" d="1" pool="A-E" correct-key="1-B,2-C,3-E,4-A">
      <concept>Concurrency bug classification (deadlock, livelock, starvation, race condition)</concept>
      <domain>software / systems</domain>

      <stem>
        Match each observed thread-behavior case to what it actually is.
        Not every classification is used.
      </stem>

      <prompts>
        <item label="1" role="near-duplicate" pair-with="3">
          Two worker threads each hold one of two locks and each is blocked
          waiting on the lock the other holds; CPU usage for both threads
          drops to zero and stays there, with no timeout configured on
          either lock.
        </item>
        <item label="2">
          A background thread assigned the lowest scheduling priority makes
          no progress for extended periods: it stays runnable the whole
          time and holds no lock, yet the scheduler keeps handing available
          CPU to other runnable threads first, so it is passed over rather
          than ever reacting to another thread or doing work of its own.
        </item>
        <item label="3" role="near-duplicate" pair-with="1">
          Two worker threads each repeatedly detect that the other has
          changed a shared piece of state and each rolls back and retries
          its own operation in response; CPU usage for both threads stays
          high throughout, and neither thread ever holds a lock the other
          is waiting on.
        </item>
        <item label="4">
          Two threads increment a shared counter without any synchronization
          between them; the program always terminates normally, but the
          final count is occasionally lower than the true number of
          increments performed.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for" pair-with="4">
          Multiple threads read and modify the same memory without
          coordination, so the final result depends on the exact order
          their operations happen to interleave, occasionally losing an
          update.
        </item>
        <item label="B" role="correct-for near-duplicate" pair-with="1">
          Two or more threads each hold a resource the other needs and each
          waits on the other to release it, so neither can ever proceed — a
          fixed circular dependency with no timeout to break it.
        </item>
        <item label="C" role="correct-for" pair-with="2">
          A thread makes no progress because the scheduler consistently
          gives available CPU time to other runnable threads first, leaving
          it waiting indefinitely for a turn that keeps getting deferred.
        </item>
        <item label="D" role="orthodox-but-wrong">
          The threads are contending too heavily for a single lock;
          splitting that lock into several smaller locks over separate
          pieces of state reduces the contention.
        </item>
        <item label="E" role="correct-for near-duplicate" pair-with="3">
          Two or more threads keep detecting a conflict from each other's
          actions and keep retrying in response, so each stays busy but
          none of them ever holds the resource long enough to finish — no
          thread is ever blocked, all remain runnable throughout.
        </item>
      </responses>

      <correct-key>1→B, 2→C, 3→E, 4→A (D unused)</correct-key>

      <annotation>
        Cross-viability: B (circular wait) is surface-viable for 1 (direct)
        and 3 (surface: "two threads stuck due to each other's actions"
        reads as a circular-dependency candidate before registering that 3's
        threads are never blocked). E (busy-retry) is surface-viable for 3
        (direct) and 1 (surface: "both back off and interact badly" could
        misread as an active retry pattern before registering 1's CPU drops
        to zero and stays there); E is additionally surface-viable for 2
        (prompt 2's thread "stays runnable the whole time," which reads as a
        spin/retry pattern until one notices it never reacts to a peer). C
        (starvation) is surface-viable for 2 (direct — but prompt 2 is a
        contested, not free, prompt, since its "stays runnable" framing also
        draws E on the surface) and softly for 1/3 (any "thread not
        progressing" framing invites it before the specific mechanism is
        checked). A (race
        condition) is surface-viable for 4 (direct) and softly for 3 (3's
        "detects that the other has changed shared state" reads like
        concurrent-access framing before noting 3 never touches a lock at
        all). D (orthodox lock-contention fix) is surface-viable for 1
        (lock-related, obviously), 3 (looks like contention over shared
        state), and softly 4 (shared-state framing).

        Near-duplicate confusion cell: prompts 1 and 3 (twin: both are "two
        worker threads stuck due to interacting with each other") crossed
        with responses B and E (twin: both describe two threads locked in a
        mutually-caused stall). The one differentiating projection: is a
        thread actually BLOCKED, holding a resource and waiting on the
        other (1, CPU flat at zero, no timeout to break it → B), or is it
        actively RUNNING and retrying in response to the other's changes,
        never blocked at all (3, CPU stays high, neither ever holds a lock
        the other waits on → E)? "Two threads stuck because of each other"
        is the surface feature shared by both twins; whether CPU drops to
        zero (blocked) or stays high (spinning) is the projected
        differentiator. Cross-wiring 1↔3 / B↔E is the canonical
        transposition error — the textbook deadlock/livelock confusion.

        Orthodox-but-wrong (D): "too much lock contention, split the lock"
        is the reflexive fix for any thread interference — professionally
        sound advice in general. It matches nothing here: prompt 1's
        threads are in a fixed circular wait that persists regardless of
        lock granularity (splitting locks doesn't fix ordering); prompt 3
        has no locks involved at all; prompt 4's problem is missing
        synchronization, not excess contention on one lock.

        Unique bijection: prompt 2 (stays runnable but holds no lock and
        never reacts to another thread, just deferred by the scheduler)
        resolves only to C — E is ruled out because prompt 2's thread does
        no retrying in response to a peer, the defining feature of livelock;
        prompt 4 (unsynchronized shared counter, no hang) resolves only to
        A; prompts 1 and 3 resolve to B and E only once the blocked-vs-
        spinning projection is applied; D attaches to nothing. No second
        complete assignment survives — attaching B to 3 directly
        contradicts 3's stated "neither thread ever holds a lock the other
        is waiting on," and attaching E to 1 directly contradicts 1's
        stated zero CPU usage.

        No-elimination-shortcut (D=1): after correctly placing 2→C and
        4→A, the learner still faces {1,3}×{B,D,E} — D (the lock-splitting
        fix) remains surface-plausible for both remaining prompts, so the
        pairing is not a forced 2-cycle; the learner must genuinely project
        the blocked-vs-spinning distinction to split B from E and
        separately reject D.
      </annotation>
    </example>

    <example id="6" axis="time" n="4" d="1" pool="A-E" correct-key="1-E,2-B,3-A,4-D">
      <concept>Read-after-write visibility under asynchronous replication and a fixed-TTL cache, in the same system</concept>
      <domain>distributed systems / caching</domain>

      <stem>
        Match each write-then-read case to what the read actually returns,
        given how much time has elapsed at each stage. Not every outcome is
        used.
      </stem>

      <prompts>
        <item label="1">
          A client writes a value, then immediately (within 10ms) reads it
          back through a request routed to a replica, in a system whose
          replication typically completes within 250ms.
        </item>
        <item label="2">
          A client writes a value, waits 2 seconds, then reads it back
          through a request routed to the same replica.
        </item>
        <item label="3" role="near-duplicate" pair-with="4">
          A different client had already read and cached this key 5 seconds
          before the write occurred; that client reads the key again,
          through the cache, 3 seconds after the write. The cache's entries
          expire 60 seconds after being cached.
        </item>
        <item label="4" role="near-duplicate" pair-with="3">
          A different client had already read and cached this key 90
          seconds before the write occurred; that client reads the key
          again, through the cache, 3 seconds after the write. The cache's
          entries expire 60 seconds after being cached.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for near-duplicate" pair-with="3">
          The cached entry was already within its 60-second expiry window
          when the write occurred and remains within that window at the
          time of this read, so the cache keeps serving the value it
          already held rather than the newly written one.
        </item>
        <item label="B" role="correct-for" pair-with="2">
          Enough time has elapsed since the write that replication has
          already completed well before the read arrives, so the replica
          returns the newly written value.
        </item>
        <item label="C" role="orthodox-but-wrong">
          A cache entry still within its 60-second lifetime is fresh and so
          reflects the current value, meaning the read returns the newly
          written value; only an entry past its lifetime is stale and would
          hand back an outdated value.
        </item>
        <item label="D" role="correct-for near-duplicate" pair-with="4">
          The cached entry had already exceeded its 60-second expiry window
          by the time of this read, so the cache treats it as expired and
          re-fetches — and by that point the write has long since
          replicated, so the re-fetch returns the newly written value.
        </item>
        <item label="E" role="correct-for" pair-with="1">
          The read reaches the replica before replication has had time to
          complete, so the replica still holds the value that was in place
          immediately before the write.
        </item>
      </responses>

      <correct-key>1→E, 2→B, 3→A, 4→D (C unused)</correct-key>

      <annotation>
        Cross-viability: E (read arrives before replication completes) is
        surface-viable for 1 (direct) and 2 (a shallow read might not weigh
        2 seconds against the 250ms typical lag and assume replication
        could still be incomplete). B (replication completed) is
        surface-viable for 2 (direct) and 1 (a shallow read might treat
        "within 10ms" as close enough to instant that replication is
        assumed complete). A and D (cache-TTL mechanics) are
        surface-viable for each other's prompt as described below, and
        softly for 1/2 since all four prompts share one write-then-read
        frame and a reader may not immediately separate the replica-path
        mechanism from the cache-path mechanism. C (the fresh-means-current
        misconception) is surface-viable for 3 and 4 directly (both are
        cache reads whose entry age relative to the 60-second TTL reads as
        the obviously relevant question) and softly for 1/2 under the
        general "reads shortly after a write risk staleness" framing.

        Near-duplicate confusion cell: prompts 3 and 4 (twin: both are
        cache reads of a key that was already cached before the write, read
        again 3 seconds after the write) crossed with responses A and D
        (twin: both describe the cache's TTL state at the moment of the
        read). The differentiating projection is arithmetic, not just
        conceptual: prompt 3's entry was cached 5 seconds before the write
        and read 3 seconds after — 8 seconds of total cache age, well under
        the 60-second window, so it has NOT expired → A. Prompt 4's entry
        was cached 90 seconds before the write and read 3 seconds after —
        93 seconds of total cache age, past the 60-second window, so it HAS
        expired on its own schedule, independent of the write → D. "A cache
        read shortly after a write, key already cached" is the surface
        feature shared by both twins; whether the entry's OWN age (not the
        write's age) has crossed 60 seconds is the projected
        differentiator.

        Orthodox-but-wrong (C): "an entry still within its TTL is fresh, so
        it reflects the current value" is the pervasive fresh-means-current
        misconception — it conflates a cache entry's FRESHNESS (age still
        under the TTL) with its DATA CURRENCY (whether it holds the latest
        write). The two are inverse for a cache these writes do not
        invalidate: an entry comfortably within its lifetime is precisely
        the one still serving whatever it cached BEFORE the write (the old
        value), while an entry past its lifetime is the one that re-fetches
        and picks up the new value. C therefore predicts the wrong verdict
        on both cache prompts — it calls prompt 3 (age 8s, within TTL)
        "fresh → new value" when the true answer is the old cached value,
        and calls prompt 4 (age 93s, past TTL) "stale → old value" when the
        true answer is the newly written value. C matches no prompt: it is
        verdict-wrong on 3 and 4, and its premise ("a cache entry within its
        lifetime") does not even hold for the replica-path prompts 1 and 2,
        which involve no cache entry at all. This is a strictly stronger
        distractor than a write-relative-clock rule, which — because
        prompts 3 and 4 are read at the same 3-second offset from their
        writes — would coincide with whichever twin genuinely returns the
        old value and so leave a second defensible bijection; the
        freshness-inversion form is wrong on both twins and leaves exactly
        one.

        Unique bijection: prompt 1 (read within 10ms, well inside the
        typical 250ms replication lag) resolves only to E; prompt 2
        (2-second wait, well past typical replication lag) resolves only
        to B; prompts 3 and 4 resolve to A and D respectively only once the
        cache-age arithmetic is projected; C attaches to nothing. No second
        complete assignment survives.

        No-elimination-shortcut (D=1): after correctly placing 1→E and
        2→B, the learner still faces {3,4}×{A,C,D} — C remains
        surface-plausible for both remaining prompts (the freshness framing
        reads as relevant to both cache entries), so the pairing is not
        a forced 2-cycle; the learner must compute both cache-age figures
        to split A from D and separately reject C.
      </annotation>
    </example>

    <example id="7" axis="risk" n="5" d="2" pool="A-G" correct-key="1-C,2-F,3-A,4-B,5-D">
      <concept>Schema-migration constraints and the failure surface each migration approach actually opens</concept>
      <domain>databases / operations</domain>

      <note>
        This example is n=5, D=2 (pool of seven, two distractors) — a
        mid-range grid above the n=4/D=1 default, showing that the density,
        unique-bijection, and no-elimination properties hold as n grows and
        that a second distractor gives a second, distinctly-failing orthodox
        lure a home.
      </note>

      <stem>
        Match each migration scenario and its constraint to the failure
        surface it actually opens. Not every failure surface is used.
      </stem>

      <prompts>
        <item label="1" role="near-duplicate" pair-with="2">
          Adding a NOT NULL column with a default value to a
          200-million-row table; the constraint is that no table-level lock
          may be held longer than a few hundred milliseconds at any point,
          though the overall migration may take several minutes.
        </item>
        <item label="2" role="near-duplicate" pair-with="1">
          Renaming a column that many services reference directly by name
          in their queries, where a shared connection pool routes queries
          to any of those services without coordination; the constraint is
          that no moment may exist where some services resolve the old
          name while others resolve the new name.
        </item>
        <item label="3">
          Deleting a large batch of rows that are no longer needed, to
          reclaim storage; the constraint is that if the deletion needs to
          be reversed after it starts, full recovery of the deleted rows
          needs to remain possible for at least 24 hours afterward.
        </item>
        <item label="4">
          Changing a column's storage encoding to a more compact format
          under a fixed maintenance window; the constraint is that once the
          window closes and traffic resumes, whatever state the migration
          is in at that point is treated as final, with no further
          opportunity to revisit it.
        </item>
        <item label="5">
          Backfilling a newly added column's values across a large table in
          repeated batches while the table keeps taking live writes; the
          constraint is that a row updated by application traffic after its
          batch has already been processed still ends up holding the correct
          backfilled value rather than a stale one.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for" pair-with="3">
          Performing the deletion by removing rows directly, without
          retaining a recoverable copy, makes the data physically gone once
          the deletion commits, so there is nothing left to reverse from
          after that point, regardless of how much time has passed.
        </item>
        <item label="B" role="correct-for" pair-with="4">
          Performing the encoding change as an in-place rewrite that is
          only partially complete when the maintenance window closes leaves
          the column in a mixed-encoding state with no further window to
          finish or revert it.
        </item>
        <item label="C" role="correct-for near-duplicate" pair-with="1">
          Performing the migration as a single ALTER that rewrites the
          whole table acquires a lock for the full rewrite duration, which
          on a 200-million-row table can hold the table lock far longer
          than a few hundred milliseconds, blocking all writes for the
          duration.
        </item>
        <item label="D" role="correct-for" pair-with="5">
          Backfilling in a single pass that reads each row once and writes
          the computed value leaves any row that application traffic
          modifies after its batch was read still holding the earlier
          computed value, because the one-pass backfill never revisits rows
          that changed behind it.
        </item>
        <item label="E" role="orthodox-but-wrong">
          Running the migration inside a single transaction guarantees that
          either all of its changes take effect or none of them do, giving
          a clean all-or-nothing outcome.
        </item>
        <item label="F" role="correct-for near-duplicate" pair-with="2">
          Performing the rename as a single atomic DDL statement still
          leaves a window, however brief, where already-open connections
          continue resolving the old name while new connections resolve the
          new name, because the connection pool does not coordinate a
          simultaneous cutover across existing connections.
        </item>
        <item label="G" role="distractor">
          Because the migration shifts the table's data distribution, the
          query planner's cached statistics go stale and some queries choose
          worse execution plans until the statistics are recomputed.
        </item>
      </responses>

      <correct-key>1→C, 2→F, 3→A, 4→B, 5→D (E and G unused)</correct-key>

      <annotation>
        Cross-viability: C (long lock hold from full rewrite) is
        surface-viable for 1 (direct) and softly 4 (a large in-place rewrite
        framing suggests lock/blocking concerns). F (connection-pool cutover
        skew) is surface-viable for 2 (direct) and softly 1 (both read as "a
        window where the system is in an inconsistent in-between state"
        before the specific mechanism — exclusive lock vs. connection-level
        skew — is checked). A (physical irreversibility) is surface-viable
        for 3 (direct) and softly 4 (both are "no going back once it
        happens"). B (stuck mid-rewrite at a deadline) is surface-viable for
        4 (direct) and softly 3 and 5 (both read as "the migration was
        interrupted partway into a bad state"). D (stale backfill for
        concurrently-updated rows) is surface-viable for 5 (direct) and
        softly 1 (both are large-table single-pass operations). E
        (transactional atomicity) and G (stale planner statistics) are each
        surface-viable across all five — every constrained migration invites
        "wrap it in a transaction" and "watch out for stale plan stats" as
        reflexive answers. Every prompt faces ≥2 surface-viable responses,
        and no response is surface-locked to exactly one prompt.

        Near-duplicate confusion cell: prompts 1 and 2 (twin: both describe
        a moment during migration where the system could be caught in an
        inconsistent in-between state) crossed with responses C and F (twin:
        both describe a window-bound problem during the migration). The
        differentiating projection: is the violated constraint about an
        exclusive TABLE LOCK blocking all writes for too long (1, a
        200-million-row full rewrite, lock-duration constraint → C), or
        about CONNECTION-POOL-level visibility skew with no blocking at all
        (2, a metadata-level rename, cross-connection-consistency constraint
        → F)? Both responses read as "a window during migration where
        something goes wrong"; only checking which specific constraint each
        prompt states — lock duration versus cross-connection name
        visibility — resolves which surface applies. C does not fit 2 (a
        rename is not a full-table rewrite; 2 never mentions row count or
        lock duration), and F does not fit 1 (1 never mentions multiple
        services or a connection pool).

        Two distractors, each failing for a distinct reason, only under
        projection:
        · E (orthodox-but-wrong): "wrap it in a transaction for an
          all-or-nothing outcome" is standard atomicity advice — but it
          addresses none of these five constraints. 1's is lock DURATION (a
          transaction does not shorten it); 2's is connection-pool
          visibility (governed by client-side routing, not the DB
          transaction); 3's is physical recoverability AFTER commit (which
          atomicity cannot provide once committed); 4's is a hard external
          deadline (which atomicity does not stop from cutting a change
          mid-flight); 5's is cross-row consistency under concurrent writes
          during a long backfill (which a single wrapping transaction would
          make worse, not better, by holding locks for the whole backfill).
        · G (second distractor): stale query-planner statistics after a
          migration is a real operational concern and reads as broadly
          applicable — but none of the five constraints is about query-plan
          quality. G names a consequence no prompt's constraint asks about;
          it fails for a reason orthogonal to E's (plan stability, not
          atomicity), so the two distractors are not redundant.

        Unique bijection: prompt 3 (irreversibility, no recoverable copy) →
        A only — B is rewrite/deadline-specific and 3 is neither an in-place
        rewrite nor under a window; prompt 4 (deadline, partial rewrite
        final at window close) → B only — A is delete-specific and 4 deletes
        nothing; prompt 5 (stale backfill under concurrency) → D only — B
        needs a maintenance-window deadline 5 does not state; prompts 1 and
        2 resolve to C and F only under the lock-duration-vs-connection-skew
        projection; E and G attach to nothing. No second complete assignment
        survives.

        No-elimination-shortcut (D=2, n=5): after correctly placing 3→A,
        4→B, and 5→D, the learner still faces {1,2}×{C,F,E,G} — both
        surplus responses E and G remain surface-plausible alongside the two
        correct ones, so the final pair is not a forced 2-cycle; the learner
        must project the lock-vs-skew distinction to split C from F and
        separately reject E and G.
      </annotation>
    </example>

    <example id="8" axis="coupling" n="4" d="1" pool="A-E" correct-key="1-D,2-A,3-E,4-B">
      <concept>Service-decomposition arrangements and the dependency each one actually leaves in place</concept>
      <domain>distributed systems / service architecture</domain>

      <stem>
        Match each service arrangement to the dependency consequence it
        actually leaves in place. Not every consequence is used.
      </stem>

      <prompts>
        <item label="1" role="near-duplicate" pair-with="3">
          Two services are split from one codebase, each with its own
          database, and both read from and write to a single shared
          message-queue topic, with no defined ownership boundary over the
          message schema on either side.
        </item>
        <item label="2">
          Two services are split with separate databases and no shared
          queue, but Service A calls Service B synchronously in the request
          path for every user-facing request, and Service B has no
          independent way to serve those requests if Service A's
          request-shaping logic changes.
        </item>
        <item label="3" role="near-duplicate" pair-with="1">
          Two services are split with separate databases and asynchronous
          eventing between them — no synchronous calls in the request path
          — but the event payload schema is defined by copying Service A's
          internal database row structure directly, field for field.
        </item>
        <item label="4">
          Two services are split with separate databases and their own
          defined API contracts, but both are deployed from the same
          CI/CD pipeline stage and cannot be deployed independently — a
          change to either always redeploys both together.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for" pair-with="2">
          Because Service A's specific request-shaping logic is what
          Service B's request-path behavior implicitly depends on, a change
          to how Service A forms its calls can break Service B's behavior
          in production even though Service B's own code never changed.
        </item>
        <item label="B" role="correct-for" pair-with="4">
          Because both services are redeployed together from the same
          pipeline stage regardless of which one actually changed, a
          failing or slow rollout on one service's change blocks or delays
          the release of unrelated changes to the other service.
        </item>
        <item label="C" role="orthodox-but-wrong">
          Splitting a monolith into two services with separate databases
          removes the shared-database coupling that made independent
          releases impossible, so the two services can now be deployed and
          scaled independently.
        </item>
        <item label="D" role="correct-for near-duplicate" pair-with="1">
          Because both services read and write the same queue topic without
          a schema-ownership boundary, a change either service makes to the
          message shape can silently break the other's consumer, even
          though the services otherwise share no code or database.
        </item>
        <item label="E" role="correct-for near-duplicate" pair-with="3">
          Because the event schema is a direct copy of Service A's internal
          row structure, any change to Service A's internal storage
          representation — even one that doesn't change Service A's own
          external behavior — forces a corresponding change to the event
          schema and therefore to Service B's consumer.
        </item>
      </responses>

      <correct-key>1→D, 2→A, 3→E, 4→B (C unused)</correct-key>

      <annotation>
        Cross-viability: D (shared-topic, no ownership boundary) is
        surface-viable for 1 (direct) and softly 3 (both involve
        message/event-based communication, inviting conflation of "shared
        queue" with "shared event schema"). E (event schema copies internal
        structure) is surface-viable for 3 (direct) and softly 1 (both are
        about message/event PAYLOAD problems before the specific mechanism
        — topic governance vs. schema provenance — is checked). A (implicit
        dependency on caller's shaping logic) is surface-viable for 2
        (direct) and softly 4 (both are "a change to one affects release or
        behavior of the other" scenarios). B (coupled deploys) is
        surface-viable for 4 (direct) and softly 2 (both are
        deployment/release-level blocking scenarios). C (separate-databases
        claim) is surface-viable across all four — every prompt explicitly
        states separate databases, inviting the natural but wrong inference
        that database separation alone means decoupling.

        Near-duplicate confusion cell: prompts 1 and 3 (twin: both are
        asynchronous, message/event-based arrangements) crossed with
        responses D and E (twin: both describe an entanglement that
        survives despite the async, no-shared-database arrangement). The
        differentiating projection: is the coupling in the TOPIC ITSELF —
        both services able to read and write the same topic with no
        governance boundary on message shape (1 → D) — or in the EVENT
        SCHEMA'S PROVENANCE — a schema that is a direct copy of one
        service's internal storage structure, leaking internal
        representation into the public contract even with clean
        one-directional eventing (3 → E)? "Message/event-based coupling" is
        the surface feature shared by both twins; which specific structural
        detail — shared-topic governance or schema-copies-internal-storage
        — produces the consequence is the projected differentiator. D does
        not fit 3 (3 has no shared-topic governance problem stated — it is
        one-directional eventing), and E does not fit 1 (1 never mentions
        the event schema being copied from internal storage — its problem
        is topic-level, not schema-provenance).

        Orthodox-but-wrong (C): "separate databases remove the coupling
        that blocked independent deployment" is the standard justification
        for extract-service refactors, and it is true as far as it goes —
        but none of these four arrangements retains coupling THROUGH the
        database. Each retains some other structural coupling instead
        (shared-topic governance, a synchronous call dependency, copied
        event schema, or a shared pipeline stage), and database separation
        does nothing to address any of those. C never names the actual
        mechanism at work in any of the four cases.

        Unique bijection: prompt 2 (synchronous call, implicit dependency
        on caller logic) resolves only to A; prompt 4 (shared pipeline
        stage, coupled deploys) resolves only to B; prompts 1 and 3 resolve
        to D and E respectively only once the
        topic-governance-vs-schema-provenance projection is applied; C
        attaches to nothing. No second complete assignment survives.

        No-elimination-shortcut (D=1): after correctly placing 2→A and
        4→B, the learner still faces {1,3}×{C,D,E} — C remains
        surface-plausible for both remaining prompts (both explicitly state
        separate databases), so the pairing is not a forced 2-cycle; the
        learner must project which specific structural detail is retained
        to split D from E and separately reject C.
      </annotation>
    </example>
```

### A.2 — Axis-fit fallback exercises (R-2 hostile axes)

```xml
  <!-- ============================================================
       AXIS-FIT FALLBACK EXERCISES
       Compact demonstrations of construction-sequence step 2 / REQ-MAT-E-003
       firing on the three axes most prone to surface collapse (R-2):
       recognition, transfer, coupling. These are not full trials — they
       record the axis-fit judgment, the failure reason, and the redraw
       landing. Full successful trials for these axes are examples 4
       (recognition), 3 (transfer), and 8 (coupling) above.
  ============================================================ -->

  <axis-fit-fallback-exercises>
    <note>
      Per construction-sequence step 2, judging axis-fit happens BEFORE
      case-set construction — it is a cheap test of whether the assigned
      axis's role-pairing can be made load-bearing for the concept at all,
      not a post-hoc discovery after a trial fails validation. These
      exercises document that judgment failing on a concept genuinely
      mismatched to the axis, the resulting signal to the orchestration
      layer, and the redraw landing on an axis that fits. This is a
      distinct failure surface from the internal-validation checklist
      (which catches a constructed trial that collapses to surface
      association); axis-fit is caught earlier, before any prompt or
      response is written.
    </note>

    <exercise id="1" axis-rejected="recognition" lands-on="application">
      <concept>Retry-with-backoff behavior under different parameter and dependency conditions (the concept behind example 5)</concept>

      <axis-fit-judgment>
        Recognition's role-pairing is presentation → classification: each
        prompt must be a case whose TRUE IDENTITY is at risk of being
        misrecognized from a familiar surface label. This concept affords
        no such structure. There is exactly one mechanism in play — retry
        with backoff — instantiated under different parameters; every
        prompt is already unambiguously "a retry-with-backoff scenario,"
        with nothing about its true category in question. Forcing a
        classification framing collapses to one of two failures: either
        trivial 1:1 labeling (every prompt says "retry," nothing left to
        recognize), or classification categories invented that the concept
        itself does not have. No dense, projection-resolvable
        presentation→classification grid is constructible.
      </axis-fit-judgment>

      <signal>
        Axis-fit failure reported to the orchestration layer per
        REQ-MAT-E-003. The orchestrator invokes `select_mcq_axis.py
        --exclude recognition[, plus any axes already used this session]`.
      </signal>

      <redraw-landing>
        Axis reassigned to `application`. Application's role-pairing —
        situation-with-parameters → produced-outcome — fits directly: every
        prompt already IS a situation with specific parameters, and the
        axis question ("what does applying the concept here actually
        produce?") is exactly what the concept affords. Construction
        proceeds under application; see example 5 for the resulting trial.
      </redraw-landing>
    </exercise>

    <exercise id="2" axis-rejected="transfer" lands-on="boundary-condition">
      <concept>Browser cookie SameSite attribute behavior (Strict / Lax / None) across cross-site request contexts</concept>

      <axis-fit-judgment>
        Transfer's construction rule (REQ-MAT-F-020) requires phrasing each
        response in a domain OTHER than its correct prompt's, so keyword
        matching is defeated and only mechanism resolves the grid — which
        requires the concept's mechanism to have a genuine, non-strained
        instantiation in at least one other domain (as Little's Law does
        across hospital/software/coffee-shop/factory in example 3).
        SameSite cookie behavior is a browser-specific request-context
        mechanism with no such cross-domain analogue: forcing its responses
        into, say, factory or hospital vocabulary produces analogies so
        strained that engaging with them requires first decoding the
        analogy rather than the concept — directly violating
        domain-anchoring's "a strained domain analogy is worse than an
        abstract case set." No non-strained inversion target exists.
      </axis-fit-judgment>

      <signal>
        Axis-fit failure reported to the orchestration layer per
        REQ-MAT-E-003. The orchestrator invokes `select_mcq_axis.py
        --exclude transfer[, plus any axes already used this session]`.
      </signal>

      <redraw-landing>
        Axis reassigned to `boundary-condition`. This fits well: the
        Strict/Lax/None distinctions are threshold behavior — which
        cross-site request context crosses which enforcement boundary, and
        what cookie-inclusion behavior results. Construction proceeds under
        boundary-condition with a condition→behavior role-pairing (specific
        cross-site request contexts → the resulting inclusion behavior).
      </redraw-landing>
    </exercise>

    <exercise id="3" axis-rejected="coupling" lands-on="boundary-condition">
      <concept>Hash table resizing (load factor and rehashing)</concept>

      <axis-fit-judgment>
        Coupling's role-pairing is structural-arrangement →
        entanglement-consequence: it requires an arrangement of MULTIPLE
        components with a dependency one leaves on another. Hash table
        resizing is a single data structure's internal behavior — there is
        no second component for anything to be entangled with, and no
        arrangement to vary across prompts. No dense grid under coupling's
        semantic is constructible for a concept with nothing to couple.
      </axis-fit-judgment>

      <signal>
        Axis-fit failure reported to the orchestration layer per
        REQ-MAT-E-003. The orchestrator invokes `select_mcq_axis.py
        --exclude coupling[, plus any axes already used this session]`.
      </signal>

      <redraw-landing>
        Axis reassigned to `boundary-condition`. This fits well:
        load-factor threshold crossings triggering rehashing are a clean
        condition→behavior structure (different load-factor and
        access-pattern conditions producing different resize-timing and
        amortized-cost behaviors). Construction proceeds under
        boundary-condition. Coupling itself is fully demonstrated fitting
        its own semantic in example 8, on a concept — service decomposition
        — that genuinely has a multi-component arrangement to test.
      </redraw-landing>
    </exercise>
  </axis-fit-fallback-exercises>
```
