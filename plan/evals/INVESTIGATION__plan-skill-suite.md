# Investigation Record — plan-skill-suite

**Retroactive reconstruction.** `FR-11` requires this record to be written during the
investigation phase. This plan was authored before that requirement existed, so this
file was assembled afterwards from the session transcript rather than kept as the
investigation proceeded. Every source below was genuinely consulted; the ordering and
the "established nothing" section are reconstructed, not logged.

---

## Sources consulted

### Altitude templates

| Source | Established |
|---|---|
| `L0__Foundation.TEMPLATE.md` | The HTML-comment governance block (PURPOSE / AUDIENCE / WHEN TO WRITE / WHEN TO UPDATE / DOES NOT CONTAIN); EARS requirement syntax; evidence labels `[E]`/`[M]`/`[A]`; per-column Status vocabularies |
| `L0__Scale_Estimates.TEMPLATE.md` | The Completeness Check as a bidirectional integrity pass; per-value source annotations; Confidence ratings |
| `L1__System_Context.TEMPLATE.md` | Minimal template shape — a governance block plus two tables |
| `L2__Container_View.TEMPLATE.md` | Gate and registry table conventions; the "delete this subsection if not applicable" optionality pattern |
| `L2__Infrastructure_View.TEMPLATE.md` | Failure Modes as a table with Severity; the "choose one mode, delete the other" pattern |
| `L3__Data_Model.TEMPLATE.md`, `L3E__Entity_Definition.TEMPLATE.md` | Lateral expansion (root index plus per-entity files); "a stale sample actively misleads" |
| `L4__Component_Design.TEMPLATE.md` | The Severity scale — Low / Medium / High / Critical — adopted verbatim into `PLANNING.TEMPLATE.md` |
| `ADR_Root.TEMPLATE.md`, `ADR__Entry.TEMPLATE.md` | Alternatives Considered, Rationale, Revisit Condition; the basis for comparing Design Decisions against ADRs |

### Altitude skills

| Source | Established |
|---|---|
| `l0-requirements`, `l0-estimates`, `l2` | The six-step Universal Structure; gate tables; intent routing; cascade trigger rules |
| `hub-preamble` | First-run instantiation; soft/hard upstream validation; the unconditional CLI backstop |
| `cascade` | Forward traversal from a break point; the explicit "no atomic — flag for review" boundary between mechanical sync and judgment |
| `adr`, `l4` | Gate patterns whose failure shape is "push back and re-extract" |
| `update-component-row` | "The calling hub has already run whichever gate applies... This atomic does not re-verify — it writes" |
| `l1`, `update-nfr-mapping-row`, `update-scale-estimate`, `create-adr-entry`, `update-entity-schema` | The four-section atomic shape (Guard Clause / Args / Write / Completion Tag); narrow `BLOCKED` conditions; justification given as one clause citing an external rule |
| `Altitude_Skills__Authoring_Methodology.md` | `INV-09` — the governing principle, frontmatter conventions, the three fixed-format moments, the task-tracking rule |
| `design-templates/CLAUDE.md` | Cross-level consistency rules R1–R9; the script-friendliness constraint |
| grep for `Claude\|the model\|LLM\|assistant\|AI` across `design-templates/.claude/skills/*/SKILL.md` | Zero matches — the executing agent is never named. Half of `INV-09` |

### Environment

| Source | Established |
|---|---|
| `~/.claude/skills/` listing | `INV-01` — user-level skills live at `~/.claude/skills/<name>/SKILL.md` |
| `python-coder-v2/SKILL.md`, `diagram/SKILL.md` | `INV-02` — the frontmatter fields actually in use and loading |
| `python-coder-v2/CORE_VISION.md` | A skill may carry supporting files beside `SKILL.md`. Recorded as `INV-03`, later removed from the plan as uncited by any decision |
| `ToolSearch` — `select:TaskCreate,TaskUpdate,TaskGet` (three times), `select:TodoWrite,TodoRead`, two keyword searches | The task-tracking tools are not resolvable in this session |
| `AskUserQuestion` tool schema | `INV-05` — one to four questions per call, two to four options each |

### Documentation

| Source | Established |
|---|---|
| `code.claude.com/docs/en/tools-reference`, `#task-tool-availability` | `INV-04` — the four Task tools are opt-in on Opus 4.8, Sonnet 5, Fable 5, Mythos 5 and later; `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, `--allowedTools`, or `--tools` |
| `code.claude.com/docs/en/skills` | `INV-08` — `user-invocable: false` hides from the `/` menu while leaving Claude able to invoke; `disable-model-invocation: true` puts a skill beyond the Skill tool. Also the field set behind `DD-16` |

---

## Consulted and established nothing

- **L5 templates and the `l5` skill** — excluded on instruction, as undercooked.
- **`design-templates/.claude/worktrees/*`** — surfaced by glob as duplicate copies of the canonical skills and templates; ignored as non-canonical.
- **`mcq-probe`, `diagram` in the skills repo** — read only after the plan was complete, to answer a question about repo layout. They informed where this plan lives, not what it says.

---

## Sufficiency

**Qualified.** Sufficient for every `[V]` Invariant in the plan: each names a source above,
and each was read directly rather than inferred.

Three gaps the reader should know about, since `FM-05` — a shallow read producing
well-formed but incomplete Invariants — was the one failure mode this plan did **not**
accept:

1. **`Altitude_Skills_Design.md` was never opened.** The authoring methodology names it as
   owning *what* each of the 23 Altitude skills does — the hub catalog, the atomic catalog,
   the validation strategy. The two-tier model and the hub/atomic split were taken from the
   methodology's summary of that document rather than from the document itself.
2. **`Altitude_Templates__How_To_Use.md` and `Template_Set__Cross_Level_Review_Checklist.md`
   were located by glob and never read.** The cross-level rules reached this plan through
   `design-templates/CLAUDE.md`'s summary table, not their own specification.
3. **No runtime observation.** Every invariant about tool and skill behaviour rests on
   documentation or on a `ToolSearch` result, never on watching a skill execute. `INV-08` in
   particular — that internals stay reachable by the hub while hidden from the `/` menu — is
   asserted by the docs and remains unverified in practice.
