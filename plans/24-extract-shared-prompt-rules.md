# Plan: Extract shared rule text and axis definitions into a reference doc (#24)

> **ORCHESTRATOR AMENDMENT, 2026-08-30 — read before using this document.**
>
> This plan is **correct within the scope it was given, and that scope was wrong.** Three
> corrections, all errors in the issue this plan was written against, not in the plan:
>
> 1. **The response-protocol deferral rested on a false premise.** Issue #24 deferred
>    `<correct-response-protocol>`, `<incorrect-response-protocol>` and `<evaluation-framework>`
>    on the grounds that they held doctrine-critical text #9 had just landed. Diffing
>    `5f7cf72`→`c687943` shows #9 left all four response protocols **byte-identical** — it added
>    the `explanation-baking` step and touched only `output` and `generation-cadence`. The
>    deferral cost ~2,300 tokens of achievable saving for no reason. The 7 BLOCKED verdicts
>    (S-04, S-05, S-06, and the blocked halves of S-13, S-14, S-15, S-16) should be re-read
>    without that constraint.
> 2. **Scope is now all 9 sections at ≥0.80 word-similarity, regardless of container** —
>    `generation-cadence`, `after-explanation`, `trial-numbering`, `axis-identification`,
>    `no-nudge`, `scenario-freshness`, `abstraction-boundary`, `banned-in-stems`,
>    `domain-anchoring`. Achievable saving **~3,473 tokens (6.1%)**, not the 1,155 (2.0%) this
>    plan computes under the old boundary, and not the 16,191 (28%) the issue originally
>    claimed — that figure conflated duplicated *mass* with *savings*, since one canonical copy
>    is still paid.
> 3. **#24 is now a sub-issue of Feature A (#6)**, not standalone. This plan's OQ-1/OQ-2/OQ-3
>    correctly identified that nothing loads a fifth file today — `SKILL.md` has no Skill-tool
>    call anywhere and each prompt asserts self-sufficiency. That is an architectural blocker,
>    not a scoping detail, and #6 builds the loading contract as its core work. Those three
>    open questions are therefore **resolved by deferral**: #6 answers them.
>
> **Retained in full and independently verified:** the per-section similarity table. A separate
> measurement pass reproduced every score within ±0.05. In particular `judgment-axes` at ~0.20
> is confirmed as four genuine definition sets, not one rule typed four times, and stays 4-way.
> The finding that ~70% of the measured surface is real type-specific content stands.
>
> This plan's `domain-anchoring` analysis surfaced a live defect, now tracked as **#26** —
> Step I4 focus areas are honored by ORDERING/MATCHING and silently ignored by MCQ/MSQ. #26
> blocks `domain-anchoring`'s hoist.

**Status:** Planned — stage 1 only. **Not approved for implementation.** Nine open questions
are unresolved; four of them are blockers.
**Date:** 2026-08-30
**Branch:** `feat/24-extract-shared-prompt-rules`
**Issue:** jvspeed74/skills#24
**Blocked by:** #8 (merged, `5f7cf72`) · #9 (merged, `c687943`)
**Blocks:** #10 · **Informs:** #6

---

## Readback — the defining interpretation

1. **This is a move, not a rewrite.** No rule's meaning changes. The only permitted
   transformation on hoisted text is substitution of a per-type bound term.
2. **Deduplication is subordinate to rule sharpness.** A section that reads less precisely
   under any one of the four bindings stays duplicated. A token saving bought with a
   blunter rule is a net loss (`CLAUDE.md`, "difficulty is the deliverable").
3. **The verdict per section is derived, not chosen.** The criterion is fixed by the issue —
   purely terminological variation → hoistable; anything else → stays duplicated. Where the
   criterion does not decide, the section goes to Open questions rather than being resolved
   here.

---

## 1. Background / context

### Key globals

| Global | Current | After #24 as scoped |
|---|---|---|
| Generation prompts | 4 files, `mcq-probe/skills/mcq-probe-0-router/prompts/` | Unchanged in number; 3 sections removed from each |
| Prompt total | **57,044** tokens (MAT 21,002 · ORD 14,771 · MSQ 10,872 · MCQ 10,399) | 4 prompts **55,489**, plus a **400**-token reference = **55,889** read-volume; net **−1,155** |
| Measured candidate surface | 16,788 tokens across the 17 named blocks (29.4% of total) | Unchanged as a measurement; only 1,555 of it moves |
| Sections cleanly hoistable 4-way | — | **3 of 17** (`generation-cadence`, `scenario-freshness`, `trial-numbering`) |
| Sections in explicitly-deferred containers | 7 of 16 named (4,633 tokens) | Untouched — out of scope |
| Shared reference doc | none | `mcq-probe/skills/mcq-probe-utils/` — form and load mechanism **unresolved** (OQ-1, OQ-2) |
| Load contract | `SKILL.md` G3 reads 4 path constants; halt on unreadable (REQ-MCQ-E-001) | Needs a 5th; owner disputed (OQ-3) |
| `plugin.json` version | `1.0.0` | Untouched by this branch — orchestrator's at merge |
| Bound terms observed | — | **8**, not the 3 the issue names (§5) |

### Pipeline

`SKILL.md`'s Generation Phase step G3 reads all four generation prompts by path constant and
retains them for the session. Pass 2 constructs each slot under the prompt matching the slot's
`question_type`. Each prompt is a single self-contained XML document wrapped in an outer
` ```xml ` fence, opening with a LOADING INSTRUCTIONS comment whose contract is *"trials shall
not be generated without this prompt."* Nothing in the four prompts references anything outside
its own file. #24 breaks that self-containment for the first time: after a hoist, a prompt is no
longer sufficient to construct a trial, and the thing that makes it sufficient is a second file
whose loading nothing currently enforces.

`mcq-probe-utils` exists today as a bare `.gitkeep` (created by #18, REQ-18-6).

---

## 2. Problem statement

The four generation prompts carry overlapping copies of general construction rules and of the
nine judgment-axis definitions. Each prompt should be the structural definition of its question
type; instead each restates the shared surface in its own vocabulary.

Measurement does not support the issue's framing of that overlap, and the gap is the central
finding of this plan:

1. **The "purely terminological" claim holds for 3 sections of 17, not for all of them.**
   Word-level similarity across the four files ranges from 1.000 (`generation-cadence`,
   `trial-numbering`, `after-explanation`) to 0.225 (`stem-structure`, MCQ vs MAT). Seven
   sections diverge structurally, not lexically.
2. **`judgment-axes` — 6,549 tokens, 39.0% of the whole measured surface — is where the claim
   fails hardest.** MCQ↔MSQ similarity is 0.957 (singular/plural and articles only). Every
   pair involving ORD or MAT is ≤ 0.271. ORDERING redefines all nine axes as a *forcing
   dependency* plus a *distractor failure mode*; MATCHING redefines all nine as a
   *prompt-role→response-role semantic* plus a *wrong-attachment failure mode*. These are four
   sets of definitions that share axis names, not one set typed four times.
3. **Seven of the 16 named sections live inside containers the issue explicitly defers.**
   `required-explanation` and `after-explanation` are children of `<correct-response-protocol>`;
   `axis-identification`, `failure-explanation`, `correct-answer-revelation` and `no-nudge` are
   children of `<incorrect-response-protocol>`; `pattern-recognition-across-trials` is a child
   of `<evaluation-framework>`. The issue's section list and its scope boundary contradict each
   other over 4,633 tokens (27.6% of the measured surface).
4. **The achievable saving is ~1,155 tokens (2.0% of 57,044), not 16,191.** 16,191 was never a
   saving figure — a perfect 4-way hoist of every named block saves 11,681 (20.5%), since one
   canonical copy must still be paid. Under the scope as settled, and with the "keep it
   duplicated where it would blunt" rule applied, the figure is 1,155.

---

## 3. Measurement method

Every figure is measured, not estimated. Method, so it is reproducible:

1. Each named element is extracted from each of the four prompts by locating its opening and
   closing tag lines and taking the inclusive line span, **including** the tag lines and the
   source indentation.
2. Each extract is written to its own file and counted with `token-counter -f csv`.
3. Terminological-variation verification is a word-level `difflib.SequenceMatcher` diff over
   whitespace-collapsed text, MCQ as the base, all six pairs reported. Every non-equal opcode
   is inspected by hand; a section is graded "purely terminological" only when **every** edit
   is a bound-term substitution or an inflection forced by one.

**Delta against the issue.** `<judgment-axes>` reproduces exactly: 6,549. The 16 rule sections
measure **10,239** here against the issue's 9,642 (+597, +6.2%); measured total **16,788**
against 16,191. The most likely cause is inclusion of the tag lines and indentation, which the
issue's method appears to have dropped. Figures in this plan are the 16,788 basis throughout.

---

## 4. Per-section extraction table — the core deliverable

Token counts are per file. `min sim` is the lowest word-level similarity across all six file
pairs. `Container` flags membership of a container the issue explicitly defers
(**CRP** = `<correct-response-protocol>`, **IRP** = `<incorrect-response-protocol>`,
**EF** = `<evaluation-framework>`).

| # | Section | MCQ | MSQ | ORD | MAT | Total | min sim | Container | Purely terminological? | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| S-01 | `generation-cadence` | 259 | 259 | 259 | 267 | **1,044** | 1.000 | — | **Yes** — word-identical; MAT differs only in line-wrap width | **HOIST** |
| S-02 | `trial-numbering` | 31 | 31 | 31 | 31 | **124** | 1.000 | — | **Yes** — word-identical | **HOIST** |
| S-03 | `scenario-freshness` | 94 | 94 | 97 | 102 | **387** | 0.886 | — | **Yes** — 5 edits, all bound-term (`scenario`→`task scenario`/`case set`; `question appended`→`closing prompt`) | **HOIST** |
| S-04 | `after-explanation` | 37 | 37 | 37 | 37 | **148** | 1.000 | CRP | **Yes** — word-identical | **BLOCKED** — deferred container |
| S-05 | `axis-identification` | 66 | 66 | 66 | 71 | **269** | 0.964 | IRP | **Yes** — 1 edit (`scenario`→`case set`) | **BLOCKED** — deferred container |
| S-06 | `no-nudge` | 75 | 75 | 76 | 78 | **304** | 0.959 | IRP | **Yes** — 2 edits, both `correct answer`→`correct set`/`correct sequence`/`correct key` | **BLOCKED** — deferred container |
| S-07 | `abstraction-boundary` | 172 | 172 | 176 | 172 | **692** | 0.826 | — | **No** — 7 of 9 edits are bound-term, but ORD/MAT extend boundary test 3 with a second graded operation (`… or to place any pool item`, `… or to evaluate any response`) that no term swap produces | **HOIST (conditional)** — OQ-5 |
| S-08 | `banned-in-stems` | 139 | 114 | 115 | 120 | **488** | 0.815 | — | **No** — the 11-item ban list is identical in all four, but MCQ carries a rationale sentence (*"A learner trained to select 'most appropriate' choices…"*) absent from the other three; the `prohibited in ___` header is type-bound | **HOIST (conditional)** — OQ-6 |
| S-09 | `domain-anchoring` | 86 | 86 | 119 | 126 | **417** | 0.809 | — | **No** — ORD/MAT carry `(Step I3, stored as DOMAIN)` and a Step I4 focus-weighting sentence that MCQ/MSQ lack outright. Content divergence, not vocabulary | **HOIST (conditional)** — OQ-7 |
| S-10 | `preferred-stem-language` | 134 | 146 | 128 | 141 | **549** | 0.667 | — | **Split.** The lead-in plus 4 bullets (82 tokens in MCQ) are identical in all four; the lead-in tail (`criterion` / `criterion or the order` / `criterion or the pairing`) and the closing-prompt bullet are type-structural | **HOIST (partial)** — shared 82-token core only |
| S-11 | `axis-uniqueness` | 100 | 100 | 226 | 242 | **668** | 0.541 | — | **Split.** Paragraphs 1–2 (84 tokens in MCQ) are shared modulo the bound `apply consistently through …` operation list; paragraph 3 (the axis-fit re-draw, citing REQ-ORD-E-003 / REQ-MAT-E-003) exists only in ORD/MAT | **HOIST (partial)** — shared 84-token core only |
| S-12 | `stem-structure` | 245 | 306 | 312 | 374 | **1,237** | 0.225 | — | **No.** MCQ/MSQ/ORD share two paragraphs; MAT's opening is a different construct entirely (shared frame + numbered prompts + shuffled response pool) and it has no `one or two short paragraphs` rule. Closing-prompt form, count disclosure (`(Select N.)`, K-not-D, n-and-m) are all type-structural | **KEEP DUPLICATED** |
| S-13 | `required-explanation` | 484 | 395 | 405 | 427 | **1,711** | 0.516 | CRP | **No.** Component 1 and the Tone paragraph are shared (166 tokens in MCQ); Components 2, 3 and 4 are type-structural — one answer vs. each answer vs. each adjacency vs. each pairing-with-rule-outs | **KEEP DUPLICATED** (and BLOCKED) |
| S-14 | `failure-explanation` | 110 | 152 | 224 | 218 | **704** | 0.297 | IRP | **No.** MCQ has one error class; MSQ two (false positive / false negative); ORD two (selection / ordering); MAT two (selection / assignment). Different decompositions, not different words | **KEEP DUPLICATED** (and BLOCKED) |
| S-15 | `correct-answer-revelation` | 164 | 98 | 104 | 122 | **488** | 0.202 | IRP | **No.** MCQ is prose; MSQ/ORD/MAT are a format line plus a bullet list. Each carries its own answer-format string (`the correct answers are …`, `X → Y → Z → W`, `1→A, 2→B … (E unused)`) | **KEEP DUPLICATED** (and BLOCKED) |
| S-16 | `pattern-recognition-across-trials` | 236 | 193 | 260 | 320 | **1,009** | 0.468 | EF | **No.** Opening and closing paragraphs are shared; the surface-gap and fundamental-gap indicator lists are type-specific (ORD's transposition indicator, MAT's near-duplicate-cell indicator and its dual-error-structure paragraph) | **KEEP DUPLICATED** (and BLOCKED) |
| S-17 | `judgment-axes` | 1,196 | 1,178 | 2,049 | 2,126 | **6,549** | 0.252 | — | **No — decisively.** MCQ↔MSQ = 0.957 (inflection only). MCQ↔ORD 0.266, MCQ↔MAT 0.260, MSQ↔ORD 0.267, ORD↔MAT 0.271. ORD and MAT redefine every one of the nine axes in a two-part, type-specific structure and add per-axis surface-sort cautions (ORD) and a `REQ-MAT-F-020` construction rule (MAT) | **KEEP DUPLICATED** 4-way; 2-way MCQ+MSQ hoist available — OQ-8 |
| | **Totals** | **3,628** | **3,502** | **4,684** | **4,974** | **16,788** | | | | |

### Roll-up

| Band | Sections | Tokens | Net saving if hoisted |
|---|---|---|---|
| **HOIST** — clean, in scope | S-01, S-02, S-03 | 1,555 | **1,155** |
| **BLOCKED** — clean, but in a deferred container | S-04, S-05, S-06 | 721 | 535 (unavailable) |
| **HOIST (conditional / partial)** — pending OQ-5…OQ-7, and the two split cores | S-07…S-11 | 2,814, of which 664 is the two shared cores (S-10 4×82, S-11 4×84) | 1,654 |
| **KEEP DUPLICATED** | S-12…S-17 | 11,698 (**69.7%** of the surface) | 0 |

**Deliverable under the scope as settled: 1,155 tokens, 2.0% of 57,044.**
Ceiling if every open question resolves toward hoisting, including a 2-way `judgment-axes`
hoist and the deferred-container sections: **5,020 tokens, 8.8%.**

### Cross-reference seams

Grep across all four prompts and `SKILL.md`: every one of the 16 rule sections appears exactly
8 times — 2 tag lines × 4 files — with **zero prose cross-references**. The seams are clean.
`judgment-axes` is the exception: 10 mentions, the two extras being prose citations inside
`ORDERING` Step 8 and `MATCHING` Step 9 `<what-this-step-is>` blocks — i.e. inside the
`explanation-baking` scaffolding the issue defers. A `judgment-axes` hoist would leave a
dangling reference inside deferred text.

---

## 5. The vocabulary binding — observed, not assumed

The issue names three bindings. Eight distinct bound terms are actually required by the sections
under consideration, and one of the three the issue names is stated wrongly.

| Bound term | MCQ | MSQ | ORD | MAT |
|---|---|---|---|---|
| `ITEM` | answer choice | answer choice | pool item | response |
| `ITEM_SET` | the answer choices | the answer choices | the pool | the responses |
| `KEY` | correct answer | correct set | correct sequence | **correct key** |
| `TASK_UNIT` | question | question | trial | trial |
| `SCENARIO` | scenario | scenario | task scenario | case set |
| `CLOSING_PROMPT` | question (appended) | question | closing prompt | closing prompt |
| `STEM_HOLDER` | stem | stem | stem | prompts |
| `GRADED_OPS` | stem construction and answer evaluation | *(same)* | scenario construction, sequence construction, and evaluation | role-selection, case-set construction, key construction, distractor construction, and evaluation |

Two corrections to the issue's statement of the binding:

- `KEY` for Matching is **`correct key`**, not `correct pairing`. MATCHING uses both terms —
  `correct key` at lines 364, 460, 677, 712, 769; `correct pairing` at lines 431, 588. That
  internal inconsistency is a #10 finding, and it means the MAT binding is currently ambiguous.
- `TASK_UNIT` for Ordering and Matching is **`trial`**, not `task`. `task` is ORD's word for the
  *procedure being ordered*, a different referent.

`GRADED_OPS` is not a noun swap — it is a list whose length varies with how many graded
operations the type has (1 for MCQ/MSQ, 2 for ORD/MAT). Treating it as an ordinary bound term is
the mechanism by which FM-24-1 fires.

---

## 6. Design decisions

**Only decisions the inputs already settle are recorded here.** Everything the inputs leave
open is in §11, unresolved, by directive.

| Decision | Resolution | Settled by |
|---|---|---|
| Precedent to copy | PGL's `pgl-taxonomy`: a shared reference holding definitions only — no phase instructions, no step sequences, no state logic — loaded alongside the phases that need it | Issue #24, Design decisions |
| Visibility, if the destination is a skill | `user-invocable: false`. `disable-model-invocation: true` is the wrong field and would hide it from the router | #18 Design decisions; binding on #11–#14; PGL `pgl-taxonomy` frontmatter |
| Destination directory | `mcq-probe/skills/mcq-probe-utils/` | Issue #24 (but see OQ-4 — #18 reserved this slot for #7) |
| Scope of the hoist | The 16 named rule sections plus `<judgment-axes>`, and nothing else | Issue #24 |
| Out of scope, untouched | Response protocols, evaluation frameworks, the `explanation-baking` step's scaffolding | Issue #24 |
| Meaning preservation | Byte-identical to source modulo bound-term substitution, verified by a mechanical diff — never an eyeball pass | Issue #24 failure-mode table, row 2 |
| Precision preservation | Any section that reads less precisely under any one of the four bindings **stays duplicated** | Issue #24 failure-mode table, row 1; `CLAUDE.md` |
| `plugin.json` | Not edited on this branch. Version bump at merge is the orchestrator's | Issue brief; #18 open question 1 |
| Consistency pass (#10), phase split (#6) | Not implemented here | Issue brief |

---

## 7. Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-24-F-001 | A shared reference document exists under `mcq-probe/skills/mcq-probe-utils/`, holding definitions only — no construction sequence, no step numbering, no per-type field rules, no state logic | Create |
| REQ-24-F-002 | It declares the bound-term table of §5 as the contract every hoisted block is written against; each generation prompt declares its own binding for those terms | Create + 4 prompts |
| REQ-24-F-003 | Exactly the sections whose verdict in §4 is **HOIST** are moved: `generation-cadence`, `scenario-freshness`, `trial-numbering`. Every other section stays where it is | 4 prompts |
| REQ-24-F-004 | Each hoisted block is byte-identical to its source after applying the declared substitution — verified by the mechanical gate of REQ-24-F-007, not by review | Gate |
| REQ-24-F-005 | The four prompts' remaining text is otherwise unchanged: zero edits inside `<viability-requirement>`, `<pool-design-law>`, `<grid-design-law>`, `<required-constructs>`, `<similarity-construction>`, `<near-duplicate-pair>`, `<near-duplicate-distractor>`, `<near-duplicate-cell>`, `<order-sensitive-pairs>`, `<orthodox-but-wrong>`, `<order-model>`, `<internal-validation>`, `<construction-sequence>`, both response protocols, `<evaluation-framework>`, `<worked-examples>`, `<edge-cases>` | 4 prompts |
| REQ-24-F-006 | Every `<internal-validation>` checklist item still resolves: no checklist item may reference a rule that has left the file without the reference resolving through the loaded reference document | 4 prompts |
| REQ-24-F-007 | **The mechanical gate.** A script reconstructs each prompt's pre-#24 text by re-inlining every hoisted block under the file's declared binding, and diffs it against `HEAD~`. A non-empty diff fails the build. This is the FM-24-2 guard and it is not delegable to review | Tooling |
| REQ-24-F-008 | **The precision gate.** For every hoisted section, the substituted text is rendered under all four bindings and read side-by-side against the four originals. Any rendering that is vaguer than its original fails the section back to KEEP DUPLICATED | Gate |
| REQ-24-E-001 | If the reference document is unreadable, the session halts on the same terms as REQ-MCQ-E-001 — a missing reference is not a degraded mode. Owner of the halt wiring is OQ-3 | `SKILL.md` (disputed) |
| REQ-24-E-002 | The reference document is never rendered to the learner, quoted, or summarized — same discipline as the batch artifact and the Probe Target descriptor | Create |

**Non-goals.** No consistency pass (#10). No phase split (#6). No persistence (#7). No
`plugin.json` edit. No change to any construction rule, viability rule, pool/grid law, required
construct, banned-language list, checklist item, response protocol, evaluation framework, or
`explanation-baking` step. No change to `SKILL.md` beyond what OQ-3 resolves.

---

## 8. Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-24-1 | **Vocabulary binding loses type precision** | A rule that reads sharply for MCQ genericizes for Matching — most likely on `GRADED_OPS`, which is a list of differing length, not a noun | A rule that was sharp per type becomes generic. Real quality loss, invisible in a token count | **No.** REQ-24-F-008 renders every hoisted block under all four bindings and reads it against its original. Any section that cannot survive that stays duplicated. Applied in §4: it is why S-07…S-11 are conditional or split rather than hoisted outright |
| FM-24-2 | **Doctrine text weakened in transit** | Bulk restructuring of files that carry the viability, near-duplicate and orthodox-but-wrong rules | The difficulty invariant erodes silently | **No.** REQ-24-F-007: mechanical re-inline-and-diff against `HEAD~`, not an eyeball pass. Mirrors #9's Gate 1 |
| FM-24-3 | **Reference doc not loaded** | A phase loads a prompt without its reference | Rules silently absent; trials generate against a partial spec | **No** in principle — but the loading contract does not exist today and its owner is disputed (OQ-3). **Blocker.** |
| FM-24-4 | **Scope collision with the deferred set** | 7 of the 16 named sections sit inside `<correct-response-protocol>`, `<incorrect-response-protocol>` and `<evaluation-framework>` | Either the deferral is violated, or 27.6% of the named surface is silently dropped without the issue recording it | **No** — surfaced as OQ-9. This plan treats the deferral as controlling and marks those 7 BLOCKED |
| FM-24-5 | **Dangling reference into deferred text** | `judgment-axes` is cited by name inside ORD Step 8 and MAT Step 9 `<what-this-step-is>` | A hoist leaves a citation pointing at a section no longer in the file, inside text nobody is allowed to edit | **No** — independent of OQ-8's outcome, a `judgment-axes` hoist cannot be clean while the baking scaffolding is frozen |
| FM-24-6 | **The saving does not justify the seam** | Measured deliverable is 1,155 tokens (2.0%) against a 16,191 (28%) headline | A new cross-file dependency, a new halt condition and a new drift surface are bought for 2% | **Not accepted or rejected here** — OQ-9 is the decision point. Recorded so the trade is explicit before a line is written |
| FM-24-7 | **Drift between reference and prompt** | The reference is the single source, but nothing re-runs REQ-24-F-007 after later edits | A later PR edits a prompt's local copy of a still-duplicated rule and the two silently diverge | Accepted for now; #10's consistency pass is the structural fix. The gate script is checked in so it can be re-run |
| FM-24-8 | **Stale plugin cache masks the change** | Directory-source plugin installs as a versioned copy and does not re-sync without a version bump | The PR appears to have no effect, or is "verified" against stale content | **No** — #18 open question 1. Version bump at merge, orchestrator's |

---

## 9. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-24-1 | An implementer reads "the variation is terminological" as licence to genericize S-07…S-17 anyway | **High** — the issue body asserts it as settled fact | **High** | §4 is the measurement of record and supersedes the assertion. REQ-24-F-008 is a hard gate, and the per-section verdict is the input to it |
| R-24-2 | A subagent softens a rule to make it read cleanly under all four bindings | Medium | **High** | `CLAUDE.md`'s invariant quoted verbatim in the implementation brief; REQ-24-F-007's diff catches any wording change mechanically. Non-delegable review item, mirroring #9's R-9-1 |
| R-24-3 | The reference doc accretes phase logic and becomes a fifth prompt | Medium | Medium | REQ-24-F-001 bounds it to definitions, per `pgl-taxonomy`'s own frontmatter contract |
| R-24-4 | Registering a `SKILL.md` under `mcq-probe-utils` surfaces a live, non-functional skill | Medium | Medium | #18 FM-3 / FM-5 are already resolved: `user-invocable: false`. Depends on OQ-1 choosing the skill form at all |
| R-24-5 | #10 is planned against a structure #24 never ships | Medium | Low | #24 blocks #10 per the issue; if #24 lands reduced, #10's brief must state which structure it targets |
| R-24-6 | Merge conflict with #6 | Low | Medium | #6 has not started; #24 touches the prompts and possibly `SKILL.md` G3, which #6 also restructures. Sequence #24 before #6 or accept a rebase |

---

## 10. Files touched

Stage 1 (this PR) touches one file. The rest is stage-2 scope, recorded for blast radius.

| File | Operation | What | Why |
|---|---|---|---|
| `plans/24-extract-shared-prompt-rules.md` | Create | This document | Repo precedent (#2, #3, #5, #8, #9, #18) |
| `mcq-probe/skills/mcq-probe-utils/…` | Create *(stage 2)* | The shared reference document; exact filename, form and frontmatter unresolved | REQ-24-F-001, OQ-1 |
| `mcq-probe/skills/mcq-probe-utils/.gitkeep` | Delete *(stage 2)* | Superseded once the directory holds a real file | #18 REQ-18-6 |
| `.../prompts/MCQ_GENERATION_PROMPT.md` | Modify *(stage 2)* | Remove S-01/S-02/S-03; add the binding declaration | REQ-24-F-002, F-003 |
| `.../prompts/MSQ_GENERATION_PROMPT.md` | Modify *(stage 2)* | Same | as above |
| `.../prompts/ORDERING_GENERATION_PROMPT.md` | Modify *(stage 2)* | Same | as above |
| `.../prompts/MATCHING_GENERATION_PROMPT.md` | Modify *(stage 2)* | Same | as above |
| `scripts/` or `.github/` — location TBD | Create *(stage 2)* | The re-inline-and-diff gate script | REQ-24-F-007 |
| `.../mcq-probe-0-router/SKILL.md` | **Disputed** *(stage 2)* | A 5th path constant, a G3 read, an Active-Constraints line, and REQ-MCQ-E-001 extension | OQ-3 — the brief forbids touching `SKILL.md` without raising it first; this raises it |
| `mcq-probe/.claude-plugin/plugin.json` | **None** | — | Orchestrator's version bump at merge |

---

## 11. Open questions

None are resolved. Four are blockers on stage 2.

| # | Question | Blocker for? |
|---|---|---|
| OQ-1 | **What form is the reference document?** A `SKILL.md` with `user-invocable: false` under `mcq-probe-utils/` (the `pgl-taxonomy` shape), or a plain `prompts/`-style `.md` read by path constant (the shape every other mcq-probe prompt uses)? The two have different loading mechanisms, different halt semantics, and different answers to the outer ` ```xml ` fence question that #9's OQ-2 settled for the prompts. | **Blocker** — the entire stage-2 implementation |
| OQ-2 | **Is the reference loaded via the Skill tool or read via a path constant?** `SKILL.md` reads all four prompts by constant at G3 and has no Skill-tool call anywhere. PGL loads `pgl-taxonomy` as a skill. Mixing the two mechanisms in one bundle is untested here. | **Blocker** — OQ-1, REQ-24-E-001 |
| OQ-3 | **Who wires the loading contract, and when?** #24's own failure-mode table says *"the loading contract is explicit, and #6 owns it"*, yet #24 is listed as blocked only by #8 and #9, and #6 has not started. Today nothing loads a fifth file, and the prompts' own LOADING INSTRUCTIONS assert self-sufficiency (*"trials shall not be generated without this prompt"*). Either #24 edits `SKILL.md` — which the brief forbids without approval — or it ships text nothing loads. | **Blocker** — FM-24-3, REQ-24-E-001 |
| OQ-4 | **Is `mcq-probe-utils` actually the reserved slot for this?** #24 states it was *"reserved by #18 for exactly this."* `plans/18-plugin-bundle-restructure.md` states the opposite: *"`mcq-probe-utils` — slot reserved now, empty until Feature B (#7) needs it."* The PGL analogue for shared *definitions* is `pgl-taxonomy`; `pgl-utils` is a script library with no instructions. Does the reference go in `mcq-probe-utils`, share it with #7, or take a new `mcq-probe-taxonomy` slot? | **Blocker** — REQ-24-F-001, R-24-4 |
| OQ-5 | **S-07 `abstraction-boundary`:** boundary test 3 ends `…to understand what the question is asking.` in MCQ/MSQ but `…what the task is asking, or to place any pool item.` (ORD) and `…understand any prompt, or to evaluate any response.` (MAT). Is that clause part of the shared rule under a `GRADED_OPS` binding, or is it type-structural and therefore a reason the section stays duplicated? | Whether S-07's 516 tokens are recoverable |
| OQ-6 | **S-08 `banned-in-stems`:** MCQ carries a rationale sentence the other three lack. Hoisting requires picking a canonical form — which adds a sentence to three files or removes one from MCQ. Both are content changes, which "this is a move, not a rewrite" forbids. Which is canonical, or does the section stay duplicated? | Whether S-08's 349 tokens are recoverable |
| OQ-7 | **S-09 `domain-anchoring`:** ORD/MAT bind `DOMAIN` to intake Step I3 and weight construction toward Step I4 focus areas; MCQ/MSQ do neither, even though `SKILL.md` Step I4 says focus areas *"weight axis selection and stem construction."* Is the MCQ/MSQ omission a latent defect to fix (making the section hoistable), or intended (making it stay duplicated)? Fixing it is out of #24's scope either way. | Whether S-09's 291 tokens are recoverable; possible separate bug |
| OQ-8 | **S-17 `judgment-axes`:** a 4-way hoist is ruled out by measurement (all ORD/MAT pairs ≤ 0.271). A **2-way** hoist over MCQ+MSQ alone is available and would save ~1,178 tokens — more than the entire in-scope deliverable. But it produces a reference document that is shared by two of four types, which is a different architecture from the one the issue describes, and it cannot be clean while ORD/MAT Steps 8/9 still cite `judgment-axes` by name inside frozen text (FM-24-5). Take it, or leave `judgment-axes` alone entirely? | Whether the single largest item (6,549 tokens) participates at all |
| OQ-9 | **Does #24 proceed at 1,155 tokens?** The issue's premise is a 16,191-token / 28% duplication. Measurement puts the achievable in-scope saving at 1,155 (2.0%), 5,020 (8.8%) if every question above resolves maximally, against the cost of a new cross-file dependency, a new halt condition, a new drift surface and a `SKILL.md` edit. Separately, the issue's section list and its own deferral boundary contradict each other over 4,633 tokens (OQ-9a: which one governs?). Proceed as scoped, re-scope to include the response protocols and evaluation frameworks, or close? | **Blocker** — everything |

---

## 12. Implementation order

Stage 2 only. **Do not begin until OQ-1 through OQ-4 and OQ-9 are resolved.**

1. Resolve OQ-9 (proceed / re-scope / close). If proceed, resolve OQ-1, OQ-2, OQ-3, OQ-4 —
   they jointly determine the destination file, its form, and who wires its loading.
2. Resolve OQ-5, OQ-6, OQ-7, OQ-8 — each moves one section between HOIST and KEEP DUPLICATED
   and changes the final figure.
3. Write the REQ-24-F-007 gate script **first**, against the unmodified tree. Prove it produces
   an empty diff on `HEAD` before any text is moved. A gate written after the move can only
   confirm what was done, not catch what went wrong.
4. Author the reference document: bound-term table (§5), then the HOIST-verdict sections in the
   order S-02, S-01, S-03 (smallest first, to exercise the gate cheaply).
5. Declare the binding in `MCQ_GENERATION_PROMPT.md` and remove its three sections. Run the
   gate. Then MSQ, then ORDERING, then MATCHING, running the gate after each.
6. Run REQ-24-F-008 — render every hoisted block under all four bindings, read against the four
   originals. Any section that reads vaguer is reverted to duplicated and §4 is amended to
   record it.
7. Wire the loading contract per OQ-3's resolution; extend REQ-MCQ-E-001's halt to the
   reference if OQ-3 assigns it here.
8. Re-measure all four prompts with `token-counter`; report the actual delta against the 1,155
   projection as a variance, not silently.
9. Rebase onto `main`. PR opened by the coordinator. `plugin.json` version bump at merge.
