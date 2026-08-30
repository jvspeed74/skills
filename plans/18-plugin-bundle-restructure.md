# Plan: Convert mcq-probe to a nested plugin-bundle skill structure (#18)

## Background / context

| Global | Value before | Value after |
|---|---|---|
| Skill root | `mcq-probe/` flat (`SKILL.md` + `prompts/` + `scripts/`) | `mcq-probe/skills/<subskill>/` |
| Plugin manifest | none | `mcq-probe/.claude-plugin/plugin.json` (`name: mcq-probe`, `version: 1.0.0`) |
| Marketplace | none | `mcq-probe/.claude-plugin/marketplace.json`, `source: "."` |
| Discovery mechanism | Manual copy at `~/.claude/skills/mcq-probe` | `extraKnownMarketplaces` → `source: directory` at the repo path |
| Path constants | 6 hosted-sandbox literals, no environment note | Same 6 literals + one Environment note |
| `SKILL.md` size | 8,141 tokens | 8,563 tokens (+422, the note) |
| Bundle total | 56,540 tokens | 56,962 tokens |

`mcq-probe` is a single 759-line `SKILL.md` plus 4 generation prompts, all loaded unconditionally
every session — all 4 prompts load regardless of which types the I5/I6 gates permit. The
architectural precedent is the sibling `personalized-guided-learning-skill` repo (PGL), whose
phase decomposition ranges 2,016 → 29,574 tokens because it loads only the phase in use.

This issue is **scaffold-only**. It creates the structure that Feature A (#6) needs and relocates
the monolith into a router placeholder. It reduces no tokens — that is #6's deliverable.

## Problem statement

**Structural.** Splitting `SKILL.md` into 4 files today would surface all 4 as unprefixed,
independently invocable top-level skills, cluttering the command list with 3 phases nobody should
invoke directly. There is no `.claude-plugin/` manifest, no `skills/` directory, and no mechanism
to mark a phase internal. Feature A cannot be implemented as scoped until this exists.

**Portability.** `SKILL.md` hardcodes 6 `/mnt/skills/user/mcq-probe/...` constants. These are
*correct* for the Claude.ai hosted sandbox and wrong for Claude Code — and relocation makes them
wrong for both. They must keep working in both environments without maintaining two hardcoded sets.

**Drift.** The repo is not the discovery source. Skills load from `~/.claude/skills/mcq-probe`, a
manual copy that has already diverged: its `MATCHING_GENERATION_PROMPT.md` is 1,574 lines against
the repo's 1,714, missing the anti-anchoring n/D guidance added in commit 453efd2, while retaining
a worked example the same commit deleted. Every measurement and review in the wider redesign is
untrustworthy until there is one source of truth.

## Design decisions

| Decision | Resolution |
|---|---|
| Bundle layout | Colocated: `mcq-probe/.claude-plugin/{plugin.json,marketplace.json}` with `source: "."`, skills under `mcq-probe/skills/`. Exact PGL mirror. Resolves the contradiction in the issue body, which paired a colocated `marketplace.json` path with a `./mcq-probe` source that would resolve to `mcq-probe/mcq-probe`. |
| Non-entry-point visibility (issue open item 1) | **`user-invocable: false`** — resolved. Per `claude-automation-recommender/references/skills-reference.md:97-101`: `user-invocable: false` hides a skill from the user's `/` list while keeping it reachable by the Skill tool; `disable-model-invocation: true` does the opposite and would hide phases from the router. Confirmed empirically: `diagram` (which uses the latter) is absent from the model's skill list; all 7 `pgl-*` phases (which use the former) are present. Not applied in this issue — no phase skill exists yet — but binding on #11–#14. |
| Local dev/discovery workflow (issue open item 2) | **Resolved, and it improves.** PGL registers `extraKnownMarketplaces` with `source: directory` pointed at its repo, giving a live, drift-free loop. mcq-probe's current manual-copy mechanism has already produced drift. Conversion replaces the copy; it does not disturb a working loop. |
| Path constants under relocation | Do **not** rewrite the literals — they stay canonical for the hosted sandbox. Add exactly one Environment note beside the constants block giving `${CLAUDE_PLUGIN_ROOT}`-relative equivalents. Ported directly from PGL's resolved pattern (`plans/plugin-bundle-plan.md`, OQ-2). |
| Scope of the note | mcq-probe references every path by **constant name** in the body — all 6 literal occurrences sit inside the constants block, zero inline call sites (PGL had ~40). The note is therefore a complete fix with no further edits. PGL's "amend the use-verbatim instruction" step is a **no-op here**: mcq-probe has no such instruction. |
| Interpreter resolution | The note also states that `python` names whichever working launcher the host provides. On Windows a bare `python` is commonly shadowed by a non-functional Store alias; taking REQ-MCQ-E-002/E-003's fallbacks on every trial because the interpreter is unreachable would silently defeat randomized type and axis selection. |
| Placeholder directories | `.gitkeep` only, **no stub `SKILL.md`** — a placeholder SKILL.md would register a live but non-functional skill, the exact clutter this issue exists to prevent. |
| `mcq-probe-utils` | Slot reserved now, empty until Feature B (#7) needs it — avoids a second restructuring pass. |
| Entry-point stability | `/mcq-probe [concept]` unchanged; router keeps `user-invocable: true` and `argument-hint: "[concept]"`. Mirrors `/pgl` never changing as PGL grew 1 → 8 files. |
| `diagram` | Explicitly excluded from the bundle. Untouched by this work. |

## Requirements

| ID | Requirement | Scope |
|---|---|---|
| REQ-18-1 | `plugin.json` exists with `name`, `version`, `description`, `author` | Create |
| REQ-18-2 | `marketplace.json` exists with `$schema`, `owner`, one plugin entry, `source: "."` | Create |
| REQ-18-3 | `SKILL.md`, `prompts/`, `scripts/` relocated via `git mv`, history preserved | Move |
| REQ-18-4 | Router frontmatter unchanged; `/mcq-probe [concept]` still works | Verify |
| REQ-18-5 | One Environment note beside the constants block covering all 6 constants + interpreter resolution. Literals unchanged. | Edit |
| REQ-18-6 | 4 reserved subskill dirs exist, `.gitkeep`-only | Create |
| REQ-18-7 | `.gitignore` covers `.claude/worktrees/`, `.claude/worktree/`, `.claude/settings.local.json` | Edit |
| REQ-18-8 | Marketplace registered, plugin loads, stale `~/.claude/skills/mcq-probe` removed | Manual, post-merge |
| REQ-18-9 | From a cwd outside the repo, `/mcq-probe` completes intake and delivers one full trial | Manual, post-merge |

**Non-goals.** No content split (#11–#14). No `diagram` changes. No behavioral change to question
generation — the structural-difficulty invariant in `CLAUDE.md` is untouched. No token reduction.

## Failure modes

| ID | Mode | Trigger | Outcome | Accepted? |
|---|---|---|---|---|
| FM-1 | Version-keyed cache serves stale content | Plugin cache is versioned (`cache/<marketplace>/<plugin>/<version>/`); a directory-source plugin may not re-sync without a version bump | A PR appears to have no effect; worse, later work is "verified" against stale content | **No** — determine at first install. If re-sync is not automatic, every subsequent content PR bumps `plugin.json` version. |
| FM-2 | Environment note ignored at call time | A session reads a `/mnt/...` literal and runs it verbatim under Claude Code | Read/exec fails, or partially resolves under WSL | Partially — PGL accepted the same residual risk after observing correct on-the-spot substitution. REQ-18-9 is the check. |
| FM-3 | Placeholder registers a broken skill | A stub `SKILL.md` in an empty dir | 3 non-functional skills in the user's surface | **No** — `.gitkeep` only |
| FM-4 | Dual-load collision | Marketplace registered before the stale copy is removed | Two `mcq-probe` skills; shadowing undefined | **No** — remove the stale copy in the same step, before verification |
| FM-5 | Wrong visibility field ships in #11–#14 | `disable-model-invocation` copied from `diagram` | Router cannot dispatch to phases — silent breakage of the whole architecture | **No** — closed in Design decisions; binding on #11–#14 |
| FM-6 | Uncommitted drift lost with the stale copy | Removal while it holds an unmerged edit | Silent loss | Accepted only after a reviewed diff |
| FM-7 | Interpreter unreachable | Bare `python` hits the Store alias | Every trial silently takes the E-002/E-003 fallback; type and axis selection stop being randomized | **No** — covered by the note's interpreter clause; `uv run python` verified working here |

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Stale copy holds *wanted* content the repo lacks (it retains a deleted worked example) | Medium | Medium | Review the full diff before removal; confirm 453efd2's deletion was deliberate rather than assume |
| R-2 | `source: "."` behaves differently one level below repo root than at repo root (PGL's case) | Low | Medium | REQ-18-9 verifies empirically. Fallback: repo-root marketplace with `source: "./mcq-probe"` |
| R-3 | Feature C edits land in this monolith and are immediately re-cut by #11–#14 | High | Low | Accepted — inherited sequencing decision; the rework is mechanical relocation, not redesign |
| R-4 | Directory name and frontmatter `name` diverge (`mcq-probe-0-router` vs. `mcq-probe`) | Medium | Medium | The issue mandates the numbered directory; entry-point stability mandates the `name`. Unverified which the loader keys on — every PGL skill has dir == name, so the case is untested there, and `quick_validate.py` enforces no directory-match rule. Resolved empirically at install (step 8); see open question 2 for the two fallbacks, both cheap. |

## Files touched

| File | Operation | What | Why |
|---|---|---|---|
| `mcq-probe/.claude-plugin/plugin.json` | Create | Manifest | REQ-18-1 |
| `mcq-probe/.claude-plugin/marketplace.json` | Create | Single-plugin local marketplace, `source: "."` | REQ-18-2 |
| `mcq-probe/SKILL.md` → `mcq-probe/skills/mcq-probe-0-router/SKILL.md` | `git mv` + edit | Relocate; add Environment note | REQ-18-3, REQ-18-5 |
| `mcq-probe/prompts/` → `.../mcq-probe-0-router/prompts/` | `git mv` | 4 prompts, byte-identical | REQ-18-3 |
| `mcq-probe/scripts/` → `.../mcq-probe-0-router/scripts/` | `git mv` | 2 scripts, byte-identical | REQ-18-3 |
| `mcq-probe/skills/mcq-probe-{1-generation,2-delivery,3-analysis,utils}/.gitkeep` | Create | Reserved slots for #12/#13/#14/#7 | REQ-18-6 |
| `.gitignore` | Edit | Worktree + local-settings ignores | REQ-18-7 |
| `plans/18-plugin-bundle-restructure.md` | Create | This document | Repo precedent (#2, #3) |

## Seam map (reference for #11–#14)

Recorded while the monolith is intact. Line numbers are post-relocation, post-note.

| Target phase | Sections | Lines |
|---|---|---|
| `mcq-probe-0-router` (#11) | Frontmatter, File Path Constants, Active Constraints, Intake Phase I1–I6 | 1–235 |
| `mcq-probe-1-generation` (#12) | Trial Loop steps 1–4 (type selection, axis selection, prompt load, construction) | 236–358 |
| `mcq-probe-2-delivery` (#13) | Trial Loop steps 5–7, Response Protocol, Tangent Handling | 359–532 |
| `mcq-probe-3-analysis` (#14) | Analysis Phase, Report Format and its 9 subsections, Error Handling | 533–785 |

The boundaries fall on existing `##` headings — no section is split across phases.

## Open questions

Both resolved empirically at install, 2026-08-30. Recorded here because both bind later work.

| # | Question | Resolution |
|---|---|---|
| 1 | Does a directory-source plugin re-sync on edit, or does each content change need a `plugin.json` version bump? (FM-1) | **Version bump required.** The plugin installs as a **real copy** (not a symlink) into `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. `claude plugin update` alone reports "already at the latest version" and does not re-sync. Bumping `version` in `plugin.json` then running `claude plugin update` does re-sync — and it syncs from the **working tree**, not from a git commit. A restart is required to apply. Old version directories persist in the cache. |
| 2 | Does the loader key a skill's invocation on frontmatter `name` or on directory name? (R-4) | **Directory name.** `claude plugin details` reports `Skills (1) mcq-probe-0-router` — the frontmatter `name: mcq-probe` is ignored for registration. The entry point is therefore `mcq-probe:mcq-probe-0-router`. |

**Consequence of 1 — binding on every subsequent PR in this program.** Any PR that changes bundle
content must bump `plugin.json` version. Without it a change can appear to have no effect, or
worse, be "verified" against stale cached content and produce a false pass.

**Consequence of 2 — binding on #11–#14.** The numbered-directory scheme is kept as-is
(confirmed with the user): `mcq-probe-0-router` through `-3-analysis`, plus `mcq-probe-utils`.
This matches PGL, whose entry point is likewise `pgl-bundle:pgl-0-orchestrator` rather than a
short `/pgl`. It does mean this issue's entry-point-stability decision — that `/mcq-probe` keeps
working unchanged — was **not** achieved; the invocation is now prefixed. Accepted deliberately in
exchange for symmetric phase numbering.

Issue open items 1 (visibility field) and 2 (dev-loop impact) are both resolved above.

## Post-merge outcome

All of steps 8–10 completed. The stale `~/.claude/skills/mcq-probe` was verified byte-identical to
commit `6715bc8` — an earlier committed state holding nothing unique — before removal, closing R-1
and FM-6. Marketplace registered (`source: "."` works one level below repo root, closing R-2);
plugin installed at user scope; both selector scripts verified running from the installed cache
path. Measured cost as installed: **~72 tokens always-on, ~8.9k on-invoke** for the router. The
~47k of generation prompts is not preloaded — it is read at runtime during the trial loop, so the
56,540 figure is per-session read volume rather than preload. Feature A's win is gating those reads.

## Implementation order

1. `.gitignore` (REQ-18-7).
2. Author `plugin.json` and `marketplace.json`; validate both parse.
3. `git mv` the three paths; confirm `git status` reports renames (`R100`), not delete+add.
4. Add the Environment note (REQ-18-5). Touch no literal, no call site.
5. Create the 4 `.gitkeep` placeholders.
6. Verify: token delta is the note alone; both scripts execute from their new location.
7. Open the PR. **Steps 8–10 are post-merge.**
8. Register the marketplace; enable the plugin.
9. Diff-review, then remove `~/.claude/skills/mcq-probe` (R-1, FM-4, FM-6).
10. Run REQ-18-9 end-to-end and resolve open question 1.
