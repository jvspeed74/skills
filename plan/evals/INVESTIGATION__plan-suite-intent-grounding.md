# Investigation: plan-suite-intent-grounding

## 2026-09-10 — Authoring pass

### Candidate list (written before any source was opened)

Drawn from: the files FR-01 through FR-09 land on; the framework whose philosophy layer
this plan says a suite ought to be able to find and reason about; the enforcement
machinery Altitude already carries; a worked example of a formal invariant definition;
the suite's own prior record; and the reviewer's own stated directives, which are
themselves a governing-intent source bearing on this session.

**The suite being modified**
1. `plan/skills/plan/SKILL.md` — the gates, the consultation model, the prohibition
2. `plan/skills/plan-investigate/SKILL.md` — candidates, read, sufficiency
3. `plan/skills/plan-audit/SKILL.md` — the twelve checks; FR-08 adds one
4. `plan/skills/templates/PLANNING.TEMPLATE.md` — Invariants, `Basis`, the marker set, the pre-execute check
5. `plan/skills/plan-update-invariant/SKILL.md`
6. `plan/skills/plan-update-design-decision/SKILL.md` — the marker rules
7. `plan/skills/plan-update-requirement/SKILL.md`
8. `plan/skills/plan-update-files-touched/SKILL.md`
9. `plan/skills/plan-cascade/SKILL.md`

**Altitude's philosophy layer — what a grounding procedure would have to find**
10. `design-templates/L5__Framework_Philosophy.md` — never opened in any prior investigation
11. `design-templates/L5__Core_Concepts.md` — never opened in any prior investigation
12. `design-templates/Altitude_Templates__How_To_Use.md` — gap 2, carried unclosed through two investigations
13. `design-templates/Template_Set__Cross_Level_Review_Checklist.md` — gap 2, same
14. `design-templates/AGENTS.md`
15. `design-templates/CLAUDE.md` — cross-level rules R1–R9
16. `design-templates/invariant_definition.md` — the framework's own invariant taxonomy
17. `design-templates/module_definition.md`
18. `design-templates/Altitude_Skills__Authoring_Methodology.md` — the governing principle
19. `design-templates/Altitude_Skills_Design.md`

**Altitude's enforcement machinery**
20. `.claude/skills/hub-preamble/SKILL.md` — the consistency check and `UPSTREAM CONTRADICTION — HALT` in full
21. `.claude/skills/l4/SKILL.md` — the requirement driver gate, the persistent entity citation gate
22. `.claude/skills/l2/SKILL.md` — the rename manifest gate, the requirement continuity gate
23. `.claude/skills/adr/SKILL.md` — non-obvious decision, L0 citation, revisit condition gates
24. `.claude/skills/cascade/SKILL.md`

**A worked example of a formal invariant definition**
25. The LogWatcher repository's `docs/invariant_definition.md` — the nine-gate classification gauntlet, cited by `PLAN__ingestioneventfiltering.md`; existence on this machine unverified
26. The LogWatcher repository's `docs/L5__LogWatcher__Invariants.md` — the register, typed `strict`/`contract`/`resource`/`behavioral`

**The suite's own record**
27. `plan/evals/PLAN__plan-skill-suite.md` — the shipped plan; its `INV-09` records the authoring style
28. `plan/evals/PLAN__ingestioneventfiltering.md` — six invariants, every one a behavioral or structural fact
29. `plan/evals/INVESTIGATION__ingestioneventfiltering.md` — its doc-versus-code findings, which are FR-04's case occurring by accident
30. `plan/evals/PLAN__plan-suite-collaboration-revision.md` — the colliding unimplemented plan named by NG-01

**Stated directives bearing on this session**
31. `~/.claude/CLAUDE.md` — the reviewer's operating directives, including the type-system rule
32. `Repos/skills/CLAUDE.md` — repo doctrine

**Prior art on the concept**
33. A grep for `intent`, `philosophy`, `rationale`, `convention` across the suite and the framework, to establish whether any vocabulary for this already exists

### Consulted

| Source | Established |
|---|---|
| `altitude-framework/L5__Framework_Philosophy.md` (full) | **The document this plan's central concept comes from.** It exists to preserve intent "in a form that cannot be eroded by definition rewrites or vocabulary substitution", and declares its own consumer: when `L5__Core_Concepts.md` is read or modified, this is "the ground it stands on." It separates two things the plan suite conflates. The **Postulate** is inward-facing — "an external, foundational assumption or rule taken for granted that forms the basis of all subsequent reasoning and structure", of which "the code has no authority… It cannot negotiate, alter, or debate the Postulate from within." The **Invariant** is outward-facing — "a typed, machine-enforced commitment about behavior at a Module's boundary." It supplies four negative tests for a Postulate — not a stakeholder or team ("stakeholders are proxies"), not a technology, not a list of change scenarios, not internal to the Module — and a diagnostic for finding one from evidence: if a Module's reasons-to-change all trace to a single named assumption, that assumption is the Postulate; if they trace to different ones, the Module has more than one and must be split. |
| `altitude-framework/invariant_definition.md` §1–§3, §5 headings | An invariant is "a typed, machine-enforced architectural guarantee about behavior at a module boundary." Machine-enforceability is definitional, not incidental: "An architectural guarantee that cannot be machine-enforced is not an invariant — it is documentation." Four types by violation severity, applied in priority order: `strict` (data loss, corruption, crash), `contract` (a shared boundary assumption broken), `resource` (degrades the ambient runtime other modules operate in), `behavioral` (observable degradation, system operational). Required properties are ID, Type, Modules, Description, where Description is "One declarative sentence… Not a mechanism. Not an implementation detail." The validation gauntlet runs to at least twelve gates, not the nine the LogWatcher plan called it; Gate 3 is the enforceability test — "Can a deterministic test be written that fails when this guarantee is violated". |
| `altitude-framework/Altitude_Templates__How_To_Use.md` | **Gap 2 of two prior investigations, now closed.** Fourteen sections covering level semantics, decision trees, when to write each document, the hierarchy, requirement tracing, and a Common Mistakes register of symptom/fix pairs. It states "L0 is a living record of what the design is grounded on", and its citation discipline forbids vague grounding: an ADR rationale reading "grounded in L0 constraints" with no specific ID must be replaced by a backticked ID. **It prescribes no procedure for reading the philosophy before using the framework** — the document exists, and nothing directs a reader to it first. |
| `altitude-framework/Template_Set__Cross_Level_Review_Checklist.md` | **Gap 2, second half, now closed.** Nine cross-document consistency rules R1–R9, each with its trigger and a machine-checkable Yes/No column — R1, R2, R3, R5 and R9 checkable; R4, R6, R7, R8 not. Altitude therefore already classifies its own rules by whether anything can detect a violation, which is the axis FR-09 turns on. R8 is the trace-annotation rule: derived values carry cite annotations, prose references use specific IDs. |
| `.claude/skills/hub-preamble/SKILL.md:75–99` | The enforcement machinery in full, and it is a two-tier split. **Existence (soft):** if the upstream document is missing, say plainly which and why this hub depends on it, ask whether to proceed, record the choice — "a normal conversational exchange — no fixed block." **Consistency (hard):** read whatever upstream documents exist and look for an actual contradiction, watching for three named kinds — a referenced ID that no longer exists upstream, a status mismatch (`Deprecated`/`Retired` treated as `Active`), a contract or schema mismatch in field type, format or threshold. On a contradiction, "halt immediately — no partial writes" under `UPSTREAM CONTRADICTION — HALT`. This is the precedent FR-05 and FR-06 divide along: contradiction halts, absence is advisory. |
| `LogWatcher/AGENTS.md` | A real project's stated governing rules, in 38 lines. Line 11 declares a precedence rule for exactly the case FR-04 addresses: "If agent assumptions conflict with `docs/`, the documentation is correct." Also "Project requirements and contracts are defined in `docs/`"; "Do not invent requirements"; "Do not break published data/CLI contracts without a compatibility plan." Establishes that a project may state which source wins a disagreement — and, read against the LogWatcher investigation's findings of three stale documentation sites, that such a rule can be declared and still be wrong in practice. |
| `LogWatcher/docs/` listing versus `altitude-framework/` | `invariant_definition.md` (623 lines) and `module_definition.md` (369 lines) are present in both at identical length: LogWatcher inherits its invariant taxonomy wholesale from Altitude rather than authoring one. A project's governing intent may therefore live outside the project, in a framework it adopted. |
| `plan/evals/PLAN__ingestioneventfiltering.md`, Invariants | Six invariants, every one an outward guarantee or an observable structural fact about the code — the classification rule, eventual processing, callbacks doing no IO, silent publish failure, two-way test coverage, the worker boundary catch. None states a rule the system was built inside. Read against `L5__Framework_Philosophy.md`, the section captures Invariants and holds no Postulates at all. |
| `grep 'optimal\|recommend\|better than\|prefer'` across all eight skills | One hit in nine hundred and fifty lines: the hub's line 42, "options neutral, no recommendation." The only appearance of the vocabulary anywhere in the suite is the clause forbidding it, and "optimal" appears zero times. |
| `grep 'push back\|halt\|contradic\|decline\|redirect'` across the suite versus Altitude | The suite's only hits are five atomics redirecting a mis-invoking caller and the hub declining a Revise when no plan file matches. Altitude returns `UPSTREAM CONTRADICTION — HALT`, paradigm-violation halts, "Push back and redirect" gates, a requirement continuity gate and a rename manifest gate. The plan hub's eight gates fail in seven ways — decline, re-extract ×3, investigate, ask ×2, drain — every one addressing the form or completeness of what the practitioner supplied, none testing whether it contradicts anything. |
| `plan/skills/templates/PLANNING.TEMPLATE.md`, Invariants and PROVENANCE | "Existing behavior, guarantees, or limits this task must not violate"; "an invariant describes what already holds"; `Basis` "names the source that establishes it", with the reviewer's assertion admitted where no source can. The marker set is `[U]`/`[V]`/`[D]`/`[A]`, `[V]` meaning exactly one option was ever viable. Confirms there is no marker for a resolution the agent reasoned about and the reviewer ratified — and that `[U]` remains correct for such a resolution, since the reviewer accepted it. |
| `plan/skills/plan/SKILL.md`, Investigation gate | Requires every `Basis` to name "a file, contract or measurement". Intent, rationale and philosophy are not on that list; a philosophy document would qualify only as "a file", which admits it without inviting it. |
| `plan/skills/plan-audit/SKILL.md` | Twelve checks. Check 2 verifies every `INV-XX` appears in some Design Decision or Failure Mode — testing the relevance of what was written. No check tests what was omitted. FR-08 inverts this direction. |

### Not opened

| Not opened | Why |
|---|---|
| `altitude-framework/L5__Core_Concepts.md` body — the Module, Postulate and Invariant sections | Only its section structure was read. `L5__Framework_Philosophy.md` declares itself the ground `Core_Concepts` stands on, so the philosophy document was read instead and in full. **This leaves the Postulate/Invariant distinction resting on one source, which FR-03 would require marking uncorroborated.** Named again below. |
| `altitude-framework/invariant_definition.md` §4 Rules and §6 Examples A–J | The definition, required properties, type table and gauntlet structure were read. The ten worked examples and the rules section would refine classification but not change what an invariant is, which is what this plan needs from the document. |
| `altitude-framework/module_definition.md`, `altitude-framework/AGENTS.md` | Module semantics and framework-repository instructions. Neither bears on how a plan establishes governing intent; `module_definition.md` was reached only as a length comparison against LogWatcher's copy. |
| `.claude/skills/l4`, `l2`, `adr`, `cascade` bodies this pass | Their gate mechanics were established from `Altitude_Skills_Design.md` and the authoring methodology earlier in this session, and `hub-preamble` was read in full as the enforcement precedent that actually matters here. |
| The four `plan-update-*` atomics and `plan-cascade` bodies | No requirement here targets an atomic. `plan-update-design-decision`'s marker rules were read earlier in this session when it was invoked. |
| `LogWatcher/docs/L5__LogWatcher__Invariants.md`, `project_specification.md`, `system_diagram.md`, `concurrency_model.md`, `L5__LogWatcher__Module_Boundaries.md` | LogWatcher was opened to establish that a real project states governing rules and that it inherits its taxonomy from a framework. Both were settled by `AGENTS.md` and the directory listing. Reading its architecture would establish facts about LogWatcher, not about how a plan should ground itself. |
| `~/.claude/CLAUDE.md`, `Repos/skills/CLAUDE.md` | Both are already in this session's context — the operating directives as a standing instruction, the repo doctrine read earlier this session. Listed because they are governing-intent sources bearing on this very session, and a reader should see they were accounted for rather than overlooked. |

### Sufficiency

The read set supports, from direct observation: that Altitude separates the inward-facing Postulate from the outward-facing Invariant, and that the plan suite's Invariants section holds only the latter — all six LogWatcher invariants are outward guarantees or structural facts, none a rule the system was built inside; that machine-enforceability is definitional to an Altitude invariant, so a rule no test can catch is demoted to documentation there, which runs opposite to FR-09's conclusion that undetectable rules are the ones most worth recording; that Altitude's enforcement is a two-tier split — advisory on absence, halt on contradiction — matching the division FR-05 and FR-06 draw; that Altitude already classifies its own cross-level rules by machine-checkability; that the plan suite has no contradiction check of any kind and that its eight gates test only the form and completeness of what the practitioner supplied; that the suite's entire vocabulary for preference is one clause forbidding it; and that a real project both states governing rules and states which source wins a conflict, while its documentation can still be stale in three places.

It does not support the following, and no conclusion should rest past them:

- ~~**The Postulate/Invariant distinction rests on a single document.**~~ **Closed in the same pass.** `L5__Core_Concepts.md:154–258` was read and corroborates `L5__Framework_Philosophy.md` independently. It defines a Postulate as "an external, foundational assumption or rule — taken for granted by the Module — that forms the basis of all of the Module's structure, scope, and behavior", with four named properties: **No authority** (the Module cannot negotiate, alter or debate it), **Exclusive** ("If a proposed change to the Module cannot be traced to its Postulate, it either belongs to a different Module or reveals that the Postulate is not specific enough"), **Sufficient** (no additional force is needed to explain the Module's shape), and **External to the Module**. It repeats the invariant's machine-enforcement clause verbatim and adds a two-condition qualification test — the behavior must cross a boundary or degrade the shared runtime, and a violation must be deterministically testable without relying on OS behavior, timing or probabilistic conditions — plus three exclusions: behavior self-contained in one Module, implementation details invisible to callers, and behavior that cannot be deterministically tested. The **Exclusive** property is directly the mechanism FR-06 needs: a proposed change that cannot be traced to the governing rule is either misplaced or reveals the rule was stated too loosely.
- **A second real governing-intent document was found and read: `Repos/skills/CLAUDE.md`.** It governs `mcq-probe` in this same repository and is structurally richer than `LogWatcher/AGENTS.md`. It states a single load-bearing invariant in prose, names the failure mode it exists to prevent ("The mistake to never repeat"), declares its own relationship to the specification it summarises ("This file is the mental model; those files are the contract"), states a non-negotiable ("Difficulty is the deliverable… Do not soften it"), defines what counts as a regression ("A novel format that makes selection or answers easier is a regression, even if the mechanic is new"), and prescribes the first question to ask when extending the system. None of it is machine-enforced, so by Altitude's definition none of it is an invariant — yet violating any of it would silently destroy the skill's purpose, which is precisely the case FR-09 was written for.
- **The Postulate concept lives at L5, which this project excluded at its inception.** The reviewer's original instruction when the template work began was to skip L5 because it is undercooked. Every use of the Postulate framing in this plan therefore borrows from the layer of Altitude the reviewer themselves flagged as immature, and that tension is unresolved by anything read here.
- **No runtime observation.** No skill has been executed under a grounding requirement, because none exists yet. Every claim about what an agent would or would not do without such a requirement is read from instruction text and from two completed plans, not from watching a run.
- **The cost-inference mechanisms are untested.** Reading a stated rationale, tracing the consumer chain, and measuring regularity were reasoned about in conversation and are recorded in FR-09; none was exercised against a real convention to see whether it produces a defensible cost figure or merely a confident one.
- **Whether Altitude practises the Postulate concept is unestablished.** Its L5 templates and the `l5` skill were excluded from every investigation in this project. That the concept is well-specified in a philosophy document says nothing about whether it survives contact with the templates that would use it.
