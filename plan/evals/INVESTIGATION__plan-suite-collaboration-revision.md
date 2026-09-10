# Investigation: plan-suite-collaboration-revision

## 2026-09-10 — Authoring pass

### Candidate list (written before any source was opened)

Drawn from: the files FR-01 through FR-08 name outright (`plan` hub, the suite's
skills, the template); the tools those requirements depend on (`AskUserQuestion`
and whatever surface can render a document mid-authoring); the Altitude framework
this suite descends from, for any precedent on presenting state to a practitioner;
and the neighbours of each.

**The suite under revision**
1. `plan/skills/plan/SKILL.md` — the hub; every requirement targets it
2. `plan/skills/plan-audit/SKILL.md`
3. `plan/skills/plan-cascade/SKILL.md`
4. `plan/skills/plan-investigate/SKILL.md`
5. `plan/skills/plan-update-invariant/SKILL.md`
6. `plan/skills/plan-update-requirement/SKILL.md`
7. `plan/skills/plan-update-design-decision/SKILL.md`
8. `plan/skills/plan-update-files-touched/SKILL.md`
9. `plan/skills/templates/PLANNING.TEMPLATE.md`

**Evidence base — the field session this plan responds to**
10. `plan/evals/PLAN__ingestioneventfiltering.md`
11. `plan/evals/INVESTIGATION__ingestioneventfiltering.md`
12. `plan/evals/PLAN__plan-skill-suite.md` — its FR-03 and FR-05 are superseded; its Design Decisions on question routing bear directly

**Altitude precedent**
13. `design-templates/.claude/skills/*/SKILL.md` — whether any hub renders state to the practitioner mid-run
14. `design-templates/altitude-framework/Altitude_Skills__Authoring_Methodology.md` — the three fixed-format moments; the governing principle on formalising input but not output
15. `design-templates/altitude-framework/Altitude_Skills_Design.md` — never opened in the suite's own investigation; recorded there as gap 1
16. `design-templates/CLAUDE.md` — cross-level rules R1–R9
17. The `cascade` skill's per-level signpost — the one existing precedent for a fixed-format progress render

**Tool capability — what FR-01, FR-03, FR-04 and FR-07 can actually rest on**
18. `AskUserQuestion` schema — option count, description sizing, multiSelect, whether options render independently
19. Rendering surfaces reachable from a skill: `SendUserFile`, `Artifact`, `mcp__visualize__show_widget`
20. `code.claude.com/docs/en/skills` — `allowed-tools` semantics and whether a skill may declare these surfaces
21. `mcp__visualize__read_me` — the widget's own contract

**Conventions and neighbours**
22. `~/.claude/CLAUDE.md` — the register directives governing agent output
23. `mcq-probe`, `diagram` in this repo — sibling skills that present structured output
24. Repo root conventions — `CLAUDE.md` / `README.md` / `AGENTS.md` under `Repos/skills`

**Runtime observation**
25. This session's own authoring run — FR-03's comparative-view-then-card pattern was exercised live during Non-goals

### Consulted

| Source | Established |
|---|---|
| `plan/skills/plan/SKILL.md` | The whole surface this plan changes. `AskUserQuestion` and `SendUserFile` appear once each in the procedure: line 42 routes design forks to the card, line 144 delivers the finished plan. There is no third practitioner-facing moment. `CONFIRM WRITE` (lines 127–133) is the only fixed block, and it renders one row. Line 68 already reads "derive a kebab-case slug" — so the LogWatcher slug defect is a compliance failure, not a specification gap, and FR-08 must strengthen an instruction rather than add one. |
| `grep 'AskUserQuestion\|SendUserFile\|render\|present\|visuali' */SKILL.md` | Across all eight skills every hit is in the hub. No atomic, and neither `plan-cascade`, `plan-audit` nor `plan-investigate`, contains any practitioner-facing presentation instruction. The blast radius of all eight requirements is one file. |
| `grep 'allowed-tools' */SKILL.md` | The hub declares `SendUserFile` and `AskUserQuestion`; no skill declares `Artifact` or any MCP rendering tool. Read together with the skills documentation below, this constrains prompting, not capability. |
| `plan/evals/PLAN__plan-skill-suite.md`, `DD-09` | The decision this plan supersedes, whose stated rationale is narrower than its effect. It routes forks to `AskUserQuestion` "where attribution must be unambiguous for a `[U]` marker to be honest" — the card's purpose is **attribution**, not briefing. DD-09 never says where a fork's argument is rendered, which is the hole the argument fell into. Its rejected alternatives: cards throughout ("formalizes output the Altitude principle keeps conversational"); prose throughout ("rests a `[U]` marker on a prose exchange and leaves batching no mechanism"); recommendation marked ("places a thumb on a scale that is the reviewer's" — the NG-01 territory this plan does not enter). |
| `plan/evals/PLAN__plan-skill-suite.md`, `INV-05` | `AskUserQuestion` accepts one to four questions per call, each carrying two to four options. Cited by DD-09. |
| `plan/evals/PLAN__plan-skill-suite.md`, `DD-15` | The investigation record belongs beside the plan in the scratchpad — where this record was written. |
| `AskUserQuestion` tool schema, read directly | Hard constraints: `questions` 1–4, `options` 2–4, `header` max 12 characters. **No `maxLength` on `question`, `label`, or `description`**; `label` carries only an advisory "concise (1–5 words)". The volume claim in this plan's Problem Statement therefore rests on no schema limit. What holds is structural: options are discrete selectable items, and the schema's own `preview` field is documented as "rendered when this option is focused" and intended for "visual comparisons that help users compare options" — the tool's designers anticipated the comparison problem and addressed it one option at a time. Side-by-side comparison across options is not expressible. |
| `code.claude.com/docs/en/skills` | **`allowed-tools` pre-approves, it does not restrict**: "It does not restrict which tools are available: every tool remains callable, and your permission settings still govern tools that are not listed." The grant lasts one turn. `disallowed-tools` is the field that removes tools. This corrects the assumption that the hub's declaration bounded its rendering options. Also: **no documented mechanism exists for a skill to render a document, table or diagram to the practitioner mid-run.** The documented user-facing output paths are the agent's own response text and a bundled script generating an HTML file. Frontmatter beyond what `INV-02` recorded: `when_to_use`, `arguments`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `license`, `compatibility`. |
| `design-templates/Altitude_Skills__Authoring_Methodology.md`, lines 152–182 | The three fixed-format moments and the rule admitting them: they "earn a fixed block because the cost of ambiguity there is high." That is a criterion, not a quota of three. The cascade signpost is the cheapest admissible form — `Cascade check — <Level>, triggered by <id> (<type>)` — described as "One line. Findings discussed conversationally beneath it." Line 149 adds that what Claude says when a gate fails "stays conversational — the table just guarantees every hub checks the same things the same way." |
| `design-templates/.claude/skills/cascade/SKILL.md:93` | The per-unit checkpoint precedent, already in force: "Advance to the next level only after the current level is fully resolved with the practitioner." Altitude sequences a multi-part operation one unit at a time beneath a one-line signpost. FR-01 and FR-05 ask the plan hub for behavior `cascade` already has. |
| `design-templates/Altitude_Skills_Design.md` | **Gap 1 of the suite's own investigation, now closed.** "Surface" is Altitude's verb for practitioner-facing output, and it is conversational in every instance. The strongest precedent here is the rename manifest gate (line 281): generate a full manifest of every affected location, "Surface to practitioner before any change," confirm, then act in a single pass. Line 147 records intent routing surfacing a best guess for confirmation; line 146 requires the practitioner's choice be recorded before the next step begins. No fixed block is prescribed for any of it. |
| `design-templates/.claude/skills/diagram-builder/SKILL.md` | An Altitude skill whose entire output is a rendered artifact — Mermaid emitted into the response body, no rendering tool involved. Declares `tools:` rather than `allowed-tools:`. Establishes response-body rendering as the mechanism Altitude itself reaches for when a skill must show something. |
| `Repos/skills/CLAUDE.md` | Governs `mcq-probe` question design only, and states the repo "hosts evaluation skills." Nothing bearing on the plan suite's presentation behavior. |
| This session's own authoring run | The FR-03 / FR-04 pattern was executed live before it was specified: the Non-goals fork was rendered as a five-row comparative markdown table, then `AskUserQuestion` captured the selection carrying no claim absent from that table. The practitioner's reply — "Aren't they all inherently non-goals?" — engaged the comparative content directly, which a card presenting five options independently could not have elicited. One run, self-observed, not a controlled comparison. |

### Not opened

| Not opened | Why |
|---|---|
| `plan-update-invariant`, `plan-update-requirement`, `plan-update-design-decision`, `plan-update-files-touched` bodies | The grep across all eight skills returned no presentation instruction in any of them, and no requirement here targets an atomic. Their frontmatter and `allowed-tools` were read. |
| `plan-cascade/SKILL.md`, `plan-audit/SKILL.md` bodies | Same grep result. No requirement targets either, and both operate on the finished document rather than on the authoring conversation. |
| `plan/skills/templates/PLANNING.TEMPLATE.md` this pass | Read in full earlier in the session at version 1.4.0, and no requirement here targets the document's structure. Whether a checkpoint format wants recording in the template is a design question this plan has not yet reached. |
| `design-templates/.claude/skills/hub-preamble`, `l0-requirements`, `l2` bodies | Read during the suite's own investigation and recorded there. The methodology and design documents were consulted instead, being where the rules those skills implement are stated. |
| `Altitude_Templates__How_To_Use.md`, `Template_Set__Cross_Level_Review_Checklist.md` | **Gap 2 of the suite's own investigation, still open.** Both concern template authoring and cross-level consistency rules, neither of which any requirement here touches. Carried forward unclosed rather than silently dropped. |
| `Altitude_Skills_RTM.md`, `Altitude_Skills__Verification_Plan.md` | Surfaced by the filename search beside the design document. Requirements traceability and verification strategy for Altitude's own skills; no bearing on how a hub presents state. |
| `design-templates/.claude/worktrees/*` | Duplicate non-canonical copies of the skills and framework documents, as established during the suite's investigation. |
| `mcq-probe/`, `diagram/` in this repo | Listed as presentation precedents. Altitude's `diagram-builder` established the response-body pattern more directly, and neither sibling is a hub with a multi-section authoring flow. |
| `mcp__visualize__read_me` and the `Artifact` tool contract | Both are rendering surfaces reachable from this session. Neither was investigated as a candidate mechanism, because a tool supplied by an MCP server cannot be assumed present in the arbitrary session where a skill runs, and that portability constraint decides against them before their contracts matter. Recorded so the reasoning is visible rather than the candidates appearing forgotten. |

### Sufficiency

The read set supports, from direct observation: that all eight requirements land on one file, `plan/skills/plan/SKILL.md`, since no other skill in the suite carries a practitioner-facing presentation instruction; that the hub currently has exactly two practitioner-facing moments and one fixed block; that `DD-09`'s stated purpose for the question card is attribution rather than briefing, so FR-03 and FR-04 complete that decision rather than overturn it; that `allowed-tools` grants permission without restricting capability, so no rendering surface was ever foreclosed by the hub's declaration; that no documented skill-level rendering mechanism exists beyond the response body and a bundled HTML-generating script; that Altitude's own precedent for both sequencing and enumerate-then-confirm is conversational output beneath at most a one-line signpost; and that a fixed block is admitted by a stated criterion — high cost of ambiguity — rather than by a quota already spent.

It does not support the following, and no conclusion should rest past them:

- **The Problem Statement's volume claim is weaker than written.** `AskUserQuestion` imposes no `maxLength` on `question`, `label` or `description`. The measured 31 words per alternative is a real figure about the LogWatcher plan's content, not a figure about what the card can hold. Only the structural argument — options render as discrete items, so a comparative view cannot be laid across them — survives inspection. The paragraph needs correcting before the plan is delivered.
- **No rendering surface was observed working.** That response-body markdown tables render for the practitioner is established by this session's own transcript. That Mermaid renders inside a Claude Code response is **not** established: the skills documentation describes no such mechanism, and `diagram-builder` demonstrates only that Altitude emits Mermaid, not that any particular client renders it. Any decision resting on diagram rendering needs this verified first.
- **`SendUserFile` mid-authoring is unobserved.** It appears once in the hub, at delivery. Whether repeated calls during authoring produce useful cards or accumulating noise has never been tried.
- **The live FR-03 / FR-04 exercise is a single uncontrolled run**, self-observed, on a fork whose comparative content this same agent authored. It establishes the pattern is executable, not that it outperforms the card.
- **Gap 2 of the suite's own investigation remains open**, carried forward unchanged: `Altitude_Templates__How_To_Use.md` and `Template_Set__Cross_Level_Review_Checklist.md` are still unread.
