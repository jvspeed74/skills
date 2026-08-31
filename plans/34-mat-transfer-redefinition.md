# Plan: Redefine the transfer axis for MAT (#34)

**Status:** Planned. **Not approved for implementation.** One design decision (D-1) is
recommended but not ratified; implementation begins on an explicit execute signal.
**Date:** 2026-08-31
**Branch:** `docs/34-mat-transfer-plan` (plan only) → `fix/34-mat-transfer-redefinition`
**Issue:** jvspeed74/skills#34 · **Parent:** #31
**Blocked by:** #32 (worked example 1 cannot be rebuilt until the stem contract is conformed)
**Collides with:** #26 (same `<domain-anchoring>` block)

---

## Readback — the defining interpretation

1. **This is a construct correction, not a difficulty adjustment.** The axis currently
   implements the wrong thing. Nothing here softens MAT; the corrected construct is harder,
   because it removes a surface channel that currently resolves ~92% of the assignment space.
2. **The reference point for "a different domain" is DOMAIN — the domain the learner learned
   the concept in.** That is what MCQ, MSQ and ORDERING mean by it. MAT's construction rule
   means something else, and that substitution is the defect.
3. **A resolution that keeps the axis's NAME while changing what it measures is a regression**,
   even if every grid law passes, because the report's Axis Coverage would then misstate what
   was probed.

---

## 1. Background / context

### Key globals

| Global | Current | After #34 (option A) |
|---|---|---|
| MAT transfer construction | Domain-vocabulary inversion — every response phrased in a domain other than its correct prompt's | One novel domain (≠ DOMAIN) across the whole trial; no inversion |
| Domains per transfer trial | n + 1 or more (example 1 uses 5 for n=4) | **1** |
| `REQ-MAT-F-020` | 4 sites, all in `MATCHING_GENERATION_PROMPT.md`; absent from SKILL.md's registry | Retired or redefined as the single-domain rule |
| Domain↔key correlation | **−1.0** (perfect anti-diagonal in the live run) | **0** |
| Assignment space reachable by surface reading | 120 injective assignments → 9 derangements (**92.5% eliminated**) | 0% eliminated |
| Transfer failure mode | "the response's vocabulary matches a DIFFERENT prompt's domain" | Teaching-domain / textbook-form contamination |
| Worked example 1 | n=4, D=1, pool A–E, C unused, `phrased-in="neutral"`, four domains by design | Rebuilt: single domain, register-uniform pool, non-anchoring n/D |
| MAT prompt size | 21,002 tokens (largest of the four; #24 measurement) | ≈ unchanged; a deletion plus a one-line rule |
| Incidence | ≈ N/36 of sessions — 13.9% at N=5, 25% at N=9 | 0 defective |

### Pipeline

`SKILL.md` Pass 1 draws a type per slot via `SCRIPT_TYPE` and an axis per slot via
`SCRIPT_AXIS`, excluding axes already assigned to earlier slots (REQ-C-002) — a draw without
replacement across the batch. A slot therefore takes `transfer` with probability N/9 for
N ≤ 9, and is `matching` with probability 1/4, independently. Pass 2 constructs content per
slot from the type's generation prompt. `REQ-MAT-E-003` permits an axis re-draw when the
assigned axis "cannot make the slot's grid projection-resolvable" — a predicate that never
fires here, because transfer *is* projection-resolvable. The grid resolves under mechanism;
it merely also resolves under a surface rule it should not.

---

## 2. Problem statement

**The spec contradicts itself, and the contradiction is inside one checklist.**
`REQ-MAT-F-020` requires every response be phrased in a domain other than its correct
prompt's. `grid-design-law` part 1 requires that no response be surface-attachable to
exactly one prompt. Domain-vocabulary inversion does not remove the keyword lock — it
inverts it, and an inverted lock is still a lock. Both rules sit in `<internal-validation>`,
fifteen lines apart. A generator can satisfy exactly one.

**The construct drifted from the other three types.** MCQ, MSQ and ORDERING each place one
novel context in the question and locate the lure in the learner's prior training — the
original domain example, the canonical form, the textbook sequence. MAT locates the lure in
*another prompt in the same question*; DOMAIN does not appear in its failure mode at all.
MAT is the only type where "a different domain" is ambiguous, because n > 1 supplies a second
referent, and the construction rule resolved that ambiguity toward the intra-question reading.

**MATCHING's axis definition contradicts itself independently of the grid law.** Its opening
sentence names "the domain the concept is usually taught in" — correct, and consistent with
the other three. Its construction rule then says "a domain other than its correct prompt's."
The construction rule is the one wired into the checklist and into worked example 1, so it is
the one that ships.

**The result is an inverted discriminator.** A learner who reads the stem literally scores 0;
a learner who spots the inversion scores full marks with no mechanism understanding. In the
live run the learner produced a perfect domain-aligned assignment and scored 0/4, and the
trial's diagnostic yield was 0 bits — it cannot distinguish a literal-stem reader from a
mechanism-confused one.

**Worked example 1 propagates all of it.** Its annotation states the goal outright —
"Domain-keyword matching scores near zero against this key" — and its unused distractor is
tagged `phrased-in="neutral"` while every other response carries a domain. The live trial
reproduced its n=4 / D=1 / C-unused skeleton and its first pairing, and sharpened its 3-of-4
inversion into a perfect 4-of-4 anti-diagonal.

---

## 3. Design decisions

| Decision | Resolution |
|---|---|
| **D-1. What replaces inversion?** | **Option A — one novel domain (≠ DOMAIN) for the whole trial.** Domain becomes constant across the grid and can carry no pairing information. *Recommended; ratification pending.* |
| D-2. Is transfer barred for MAT instead? | No. MAT is structurally the strongest of the four types for transfer: n simultaneous projections under a global bijection constraint, where MCQ affords one. The implementation was broken; the axis fit is not. Option B retained as fallback if D-1 fails review. |
| D-3. Strip domain from responses, keeping domained prompts? | **Rejected.** Transfer's entire distinguishing device on MAT is the domain vocabulary in the responses. Remove it and the failure mode is not replaced — it disappears, leaving "this statement plausibly fits this case but actually fits another," which is `recognition`'s failure mode verbatim. The axis would collapse into recognition while keeping transfer's name, silently misreporting Axis Coverage. Recorded so it is not re-proposed. |
| D-4. Which side carries the transfer load under A? | The prompts. All n cases sit in a domain the concept is not usually taught in; the learner projects the mechanism into unfamiliar territory n times. |
| D-5. What are the distractors under A? | Textbook-form responses: the canonical answer from the domain the concept IS usually taught in, applied to the wrong element of this scenario's system. This is MCQ's second sanctioned transfer failure mode ("apply the concept to the wrong element of the new domain") and is pairing-safe, because *element* varies within one domain. |
| D-6. Does `domain-anchoring` need amending? | Yes. It mandates DOMAIN unconditionally; transfer must deliberately not use it. The carve-out is unstated today and is in scope here. |
| D-7. Is `REQ-MAT-E-003`'s re-draw predicate widened? | No. Post-fix, transfer is constructible for MAT, so the predicate not firing is correct behavior. Verified, not changed. |
| D-8. Is `REQ-MAT-F-020` retired or redefined? | Redefined, keeping the ID. The ID is referenced at 4 sites and retiring it leaves dangling references; redefining preserves traceability from the original requirement to its correction. |

---

## 4. Requirements

| ID | Requirement | Scope |
|---|---|---|
| R-01 | MAT's transfer failure mode references the teaching domain / canonical form, consistent with MCQ, MSQ and ORDERING | `<axis name="transfer">` |
| R-02 | A transfer trial uses exactly one domain across all n prompts and all m responses | `REQ-MAT-F-020` (redefined) |
| R-03 | That domain must not be DOMAIN, and must not be the domain the concept is canonically taught in where those differ | `REQ-MAT-F-020`, `<domain-anchoring>` |
| R-04 | No instruction anywhere in the file directs domain-vocabulary inversion | all 4 `REQ-MAT-F-020` sites |
| R-05 | No attribute varying across both prompts and responses may correlate with the key, positively or negatively | `<grid-design-law>` |
| R-06 | `<internal-validation>` verifies domain resolves no cell | checklist |
| R-07 | `<domain-anchoring>` states the transfer carve-out explicitly | `<domain-anchoring>` |
| R-08 | Worked example 1 uses one domain, no inversion, register-uniform responses, and a stem conforming to #32 | example 1 |
| R-09 | Worked example 1 does not use the n=4 / D=1 / C-unused skeleton, and its unused distractor is not domain-neutral | example 1 |
| R-10 | Worked example 1's annotation presents a mechanism-lure table, not a keyword-lure table | example 1 |
| R-11 | Transfer distractors are textbook-form responses failing on wrong-element, not wrong-domain | `<required-constructs>`, example 1 |

---

## 5. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| F-01 | Single-domain grid collapses to n independent classifications | Responses state their mechanism so crisply that each maps 1:1 to one prompt | Cross-viability lost the other way; grid degenerates | **No** — R-05 plus the existing near-duplicate requirement force mechanism-granularity twinning; validated by the cross-viability checks that already exist |
| F-02 | Transfer becomes indistinguishable from `recognition` in practice | Generator writes label-resemblance lures instead of textbook-form lures | Two axes share a failure mode; Axis Coverage misreports | **No** — R-11 fixes the distractor form to textbook-contamination, which recognition does not use |
| F-03 | The chosen novel domain is strained | Concept has no natural second domain | `<domain-anchoring>`'s existing rule applies: a strained analogy is worse than an abstract case set | **Yes** — falls back to the existing axis-fit re-draw (`REQ-MAT-E-003`), which now has a predicate that can genuinely fire |
| F-04 | Difficulty drops because the surface channel is gone | Removal of inversion is read as softening | Trial is easier for a keyword matcher, harder for everyone honest | **Yes, intended** — the removed channel rewarded decoding, not understanding |
| F-05 | Example 1's replacement re-anchors the next generation on a new skeleton | Any single worked example is copied | Anchoring shifts rather than disappears | **Partially** — R-09 varies n/D away from the current shape; `<count>`'s existing override warning is the standing mitigation. Residual risk accepted |
| F-06 | Concepts with only one natural domain cannot host MAT transfer | Highly domain-bound concept | Axis re-draw fires; another axis is used | **Yes** — this is the correct behavior and now works |

---

## 6. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| K-01 | Example 1 rebuild introduces new defects, as the original did | Medium | High — examples propagate directly into generation | Rebuild is validated against the full `<internal-validation>` checklist including #32's and #33's new items, and the mechanism-lure table is written before the responses are finalized |
| K-02 | Merge conflict with #26 in `<domain-anchoring>` | Medium | Low | Sequence: #26 lands first or this does; both edit distinct sentences in one block |
| K-03 | #32 not merged when implementation starts | Medium | Medium — example 1's stem would be rebuilt to a superseded contract | Hard dependency; do not start implementation before #36 merges |
| K-04 | Redefining `REQ-MAT-F-020` rather than retiring it confuses readers of the original requirement | Low | Low | The redefined text names what it replaced and why, in one sentence |
| K-05 | Reviewers read this as reducing difficulty | Medium | Medium | §2's inverted-discriminator argument and the 0-bits metric are the response; difficulty moves from surface to projection, which is the doctrine's direction |

---

## 7. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `prompts/MATCHING_GENERATION_PROMPT.md` :208–228 | Rewrite | `<axis name="transfer">` failure mode and construction rule | R-01, R-02, R-04 |
| `prompts/MATCHING_GENERATION_PROMPT.md` (checklist) | Amend | Replace the inversion item with a domain-resolves-no-cell item | R-06 |
| `prompts/MATCHING_GENERATION_PROMPT.md` `<grid-design-law>` | Amend | Add the no-key-correlated-attribute clause | R-05 |
| `prompts/MATCHING_GENERATION_PROMPT.md` `<domain-anchoring>` | Amend | Transfer carve-out | R-07 |
| `prompts/MATCHING_GENERATION_PROMPT.md` step 3 | Delete | The inversion paragraph left in place by #32 | R-04 |
| `prompts/MATCHING_GENERATION_PROMPT.md` `<required-constructs>` | Amend | Transfer distractors are textbook-form / wrong-element | R-11 |
| `prompts/MATCHING_GENERATION_PROMPT.md` example 1 | Rebuild | Domain line, prompts, responses, key, annotation, n/D | R-08, R-09, R-10 |
| `mcq-probe/.claude-plugin/plugin.json` | Bump | Version | Cache re-sync, per established pattern |

Out of scope, tracked elsewhere: `SKILL.md:964` / `REQ-MAT-F-018` (#35), `<domain-anchoring>`'s
Step I4 gap (#26), `<stem-structure>` (#32), form-uniformity (#33).

---

## 8. Open questions

| # | Question | Blocker for? |
|---|---|---|
| Q-1 | Is D-1 (option A) ratified, or is option B preferred? | **Everything.** Implementation cannot start until this is answered |
| Q-2 | For a concept whose canonical teaching domain differs from DOMAIN, which does the trial avoid — both, or only DOMAIN? | R-03's exact wording. Recommendation: **both**, since either supplies contaminating surface features |
| Q-3 | What n/D does the rebuilt example 1 use? | R-09 only. Recommendation: n=5, D=2, which also demonstrates the mid-range the current three examples skip (they cover n=4/D=1, n=3/D=2, n=6/D=3) |
| Q-4 | Does the rebuilt example 1 keep Little's Law as its concept, or change it? | Nothing blocking. Keeping it isolates the change to construction; changing it risks re-deriving a second defect |

---

## 9. Implementation order

1. **Confirm Q-1.** No file is touched before D-1 is ratified.
2. **Confirm #36 (#32) is merged.** Example 1's stem must be rebuilt against the conformed contract.
3. Rewrite `<axis name="transfer">` — failure mode first, then the redefined `REQ-MAT-F-020` (R-01, R-02, R-03).
4. Delete the inversion paragraph in construction-sequence step 3 (R-04).
5. Amend `<grid-design-law>` with the key-correlation clause (R-05).
6. Amend `<domain-anchoring>` with the transfer carve-out (R-07).
7. Amend `<required-constructs>` for textbook-form transfer distractors (R-11).
8. Update `<internal-validation>`: remove the inversion item, add the domain-resolves-no-cell item (R-06).
9. **Rebuild worked example 1** (R-08, R-09, R-10) — last, so it is written against the finished rules rather than the rules being written to fit it. This inversion of the usual order is deliberate: the current example is the propagation source precisely because it was allowed to define the rule.
10. Re-run the full `<internal-validation>` checklist against the rebuilt example, including #32's and #33's items.
11. Bump `plugin.json`.
12. Verify `REQ-MAT-E-003`'s predicate is unchanged and correct (D-7) — record the verification, change nothing.
