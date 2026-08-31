# Plan: Remove the transfer axis from Matching (#34)

**Status:** Ratified and implemented.
**Date:** 2026-08-31
**Branch:** `fix/34-mat-transfer-redefinition`
**Issue:** jvspeed74/skills#34 · **Parent:** #31
**Blocked by:** #32 (merged)
**Collides with:** #26 (same `<domain-anchoring>` block)

---

## Readback — the defining interpretation

1. **Domain is a pairing-visible attribute in Matching.** It varies across both halves of the
   grid, so any correlation it carries with the key is a surface channel — aligned or inverted.
2. **The reference point for "a different domain" is DOMAIN — the domain the learner learned
   the concept in.** That is what MCQ, MSQ and ORDERING mean by it. Matching's construction
   rule meant "different from the other prompts," which is a different construct.
3. **An axis that keeps its name while measuring something else is worse than an absent axis**,
   because the report's Axis Coverage then misstates what was probed.

---

## 1. Background / context

### Key globals

| Global | Before | After |
|---|---|---|
| Axes available to Matching | 9 | **8** — `transfer` excluded |
| `REQ-MAT-F-020` | 4 sites, domain-vocabulary inversion | Deleted |
| `REQ-MAT-F-021` | — | New: a matching slot never draws `transfer` |
| Domains per Matching trial | n + 1 or more on transfer trials | 1, as every non-transfer trial already used |
| Domain↔key correlation | −1.0 on transfer trials | No transfer trials exist |
| Worked examples | 3 (n=4/D=1 transfer, n=3/D=2, n=6/D=3) | **2** (n=3/D=2, n=6/D=3) |
| Defective sessions | ≈ N/36 — 13.9% at N=5, 25% at N=9 | 0 |
| Transfer on MCQ / MSQ / ORDERING | Unchanged | Unchanged |

### Pipeline

`SKILL.md` Pass 1 draws a type per slot via `SCRIPT_TYPE`, then an axis via `SCRIPT_AXIS`,
excluding axes already assigned to earlier slots (REQ-C-002) — a draw without replacement
across the batch. Type is drawn before axis, so the axis exclude can be conditioned on it.
`select_mcq_axis.py` relaxes to blocking only the most recently used axis once every axis is
excluded, so the exclusion is enforced again at the orchestrator after the draw returns.

---

## 2. Problem statement

**The spec contradicted itself inside one checklist.** `REQ-MAT-F-020` required every response
be phrased in a domain other than its correct prompt's. `grid-design-law` part 1 requires no
response be surface-attachable to exactly one prompt. Domain-vocabulary inversion does not
remove the keyword lock — it inverts it, and an inverted lock is still a lock. A generator
could satisfy exactly one of the two.

**Matching is the only type where the construct is ambiguous.** MCQ, MSQ and ORDERING each
place one novel context in the question, so "a different domain" can only mean "different from
where you learned it," and the lure sits in the learner's prior training. Matching's n > 1
supplies a second referent — the other prompts — and the construction rule resolved toward it.
DOMAIN never appeared in Matching's transfer failure mode.

**The result was an inverted discriminator.** A learner reading the stem literally scored 0; a
learner who spotted the inversion scored full marks with no mechanism understanding. The live
trial that surfaced this yielded 0 bits: it cannot distinguish a literal-stem reader from a
mechanism-confused one.

**Every fix that keeps the axis carries domain rules as special cases.** Transfer is the only
axis whose lure lives in a response's vocabulary rather than its content, so it is the only one
needing a domain-selection rule, a `<domain-anchoring>` exception, a distractor-form rule, and
their validation items — five sections carrying carve-outs for one axis of nine.

---

## 3. Design decisions

| Decision | Resolution |
|---|---|
| **D-1. Transfer on Matching** | **Remove it.** Matching draws from the remaining eight axes, all of which locate their lure in a response's content. |
| D-2. Redefine as one novel domain per trial instead? | Rejected. It works — domain constant across the grid carries no pairing information — but costs carve-outs in five sections for one axis. The complexity is the objection, not the correctness. |
| D-3. Strip domain from responses, keeping domained prompts? | Rejected. Transfer's distinguishing device on Matching is the domain vocabulary in the responses. Remove it and the failure mode disappears rather than changing, leaving `recognition`'s failure mode under transfer's name. |
| D-4. Where is the exclusion enforced? | The orchestrator. `SKILL.md` adds `transfer` to a matching slot's `--exclude`, re-draws if the script returns it anyway, and skips it in the exit-code-1 fallback list. |
| D-5. What happens when `transfer` is the only axis left? | It stays unassigned for the batch and Axis Coverage reports it untested. Never forced onto a matching slot. |
| D-6. Worked example 1 (the transfer example)? | Deleted. Remaining examples renumbered 1 and 2. |
| D-7. `REQ-MAT-E-003`'s re-draw predicate | Unchanged. It fires on axis-fit, which is unrelated to type-level axis availability. |
| D-8. Transfer on the other three types | Unchanged. One novel context per question leaves domain nothing to correlate against. |

---

## 4. Requirements

| ID | Requirement | Scope |
|---|---|---|
| R-01 | `MATCHING_GENERATION_PROMPT.md` contains no transfer axis definition | `<judgment-axes>` |
| R-02 | `REQ-MAT-F-020` and all four of its sites are deleted | whole file |
| R-03 | No instruction anywhere directs domain-vocabulary inversion | whole file |
| R-04 | The role-selection example list omits transfer | construction-sequence step 3 |
| R-05 | The transfer validation item is deleted | `<internal-validation>` |
| R-06 | Worked example 1 is deleted; remaining examples renumbered 1 and 2 | `<worked-examples>` |
| R-07 | No cross-reference cites a removed example or a removed axis | whole file |
| R-08 | A matching slot never receives `transfer` — REQ-MAT-F-021 | `SKILL.md` Pass 1 |
| R-09 | The exclusion survives the script's exhaustion relaxation | `SKILL.md` Pass 1 |
| R-10 | Transfer remains available to MCQ, MSQ and Ordering | the other three prompts |

---

## 5. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| F-01 | `transfer` reaches a matching slot anyway | All axes excluded; `select_mcq_axis.py` relaxes to blocking only the last-used axis | A matching slot draws transfer with no axis definition to construct from | **No** — R-09: the orchestrator re-draws when the script returns transfer for a matching slot, and skips it in the manual fallback |
| F-02 | `transfer` goes unassigned in a batch | It is the only axis left when the final slot is `matching` | Axis Coverage reports transfer untested | **Yes** — accurate reporting; the alternative is a defective trial |
| F-03 | Matching's axis pool is thinner at high N | N > 8 with several matching slots | Axis uniqueness (REQ-C-002) relaxes sooner for matching slots | **Yes** — the existing relaxation already handles exhaustion |
| F-04 | No worked example demonstrates D=1 | Example 1 carried the only D=1 grid | A generator infers D ≥ 2 is required | **No** — the `<count>` note states D=1 is legal above the n=3 floor and directs deriving D from the elimination simulation |
| F-05 | Transfer coverage drops session-wide | Matching slots cannot host it | A concept's transfer understanding is probed only on MCQ/MSQ/ORD slots | **Yes** — three types still carry it |

---

## 6. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| K-01 | A future contributor re-adds a domain-varying device on another axis | Low | High — reintroduces the same channel | The general clause forbidding key-correlated attributes is not in this change; tracked separately |
| K-02 | Merge conflict with #26 in `<domain-anchoring>` | Low | Low | This change does not edit that block |
| K-03 | Removing an axis reads as reducing coverage | Medium | Low | Axis Coverage reports transfer untested when unassigned, so the gap is visible rather than silent |
| K-04 | Two worked examples under-illustrate the (n, D) range | Medium | Low | The `<count>` note states the unillustrated range explicitly and forbids anchoring on example sizes |

---

## 7. Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `prompts/MATCHING_GENERATION_PROMPT.md` | Delete | `<axis name="transfer">` | R-01 |
| `prompts/MATCHING_GENERATION_PROMPT.md` | Delete | `REQ-MAT-F-020`, 4 sites | R-02, R-03 |
| `prompts/MATCHING_GENERATION_PROMPT.md` | Amend | Role-selection example list | R-04 |
| `prompts/MATCHING_GENERATION_PROMPT.md` | Delete | Transfer validation item | R-05 |
| `prompts/MATCHING_GENERATION_PROMPT.md` | Delete | Worked example 1; renumber the rest | R-06 |
| `prompts/MATCHING_GENERATION_PROMPT.md` | Amend | `<worked-examples>` note, example 1 note | R-07 |
| `SKILL.md` | Amend | Pass 1 axis draw and fallback list | R-08, R-09 |
| `mcq-probe/.claude-plugin/plugin.json` | Bump | 1.2.3 → 1.2.4 | Cache re-sync |

---

## 8. Open questions

| # | Question | Blocker for? |
|---|---|---|
| Q-1 | Does `grid-design-law` gain a general clause forbidding any prompt/response attribute from correlating with the key, positively or negatively? | Nothing here. Prophylactic against a future re-introduction on another axis (K-01); wants its own issue |
| Q-2 | Should a worked example be added to demonstrate D=1 and the unillustrated mid-range of n? | Nothing here. The `<count>` note covers it in prose (F-04) |

---

## 9. Implementation order

1. Delete `<axis name="transfer">` from `<judgment-axes>`.
2. Delete the transfer validation item from `<internal-validation>`.
3. Remove the transfer entry from construction-sequence step 3's role-selection list, and delete the inversion instruction below it.
4. Delete worked example 1; renumber the remaining examples 1 and 2.
5. Update the `<worked-examples>` note and example 1's note so no cross-reference cites a removed example.
6. Add `transfer` to a matching slot's `--exclude` in `SKILL.md` Pass 1; add the post-draw re-draw and the fallback-list skip.
7. Verify: `grep -i transfer` over `MATCHING_GENERATION_PROMPT.md` returns nothing; 8 `<axis name=>` blocks remain; XML tag balance unchanged.
8. Bump `plugin.json`.
