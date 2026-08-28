```xml
<matching-generation-prompt>

  <!-- ============================================================
       LOADING INSTRUCTIONS
       Load this file ONCE at session start, before the first matching trial.
       Retain in context for all matching trials in this session.
       Do NOT reload before each trial.
       If this file cannot be read, halt and report the error.
       Matching trials shall not be generated without this prompt.
  ============================================================ -->

  <purpose>
    This prompt governs the generation, structure, and evaluation of all
    Matching trials used in mcq-probe assessments.

    A Matching trial is not a knowledge quiz. It is a judgment probe. Its
    purpose is to distinguish a learner who can discriminate between
    confusable cases — tell apart several near-identical conditions and
    attach each to its true outcome — from a learner who has only memorized
    an association table. The naive default form of this type — "match each
    term to its definition," "match each protocol to its port" — is the
    exact failure this prompt exists to prevent: every response keyword-
    locked to exactly one prompt, every wrong cell rejectable on sight, the
    whole grid solvable by recall alone. That default form is a construction
    defect, not a lenient variant. It is never shipped.

    Difficulty in a Matching trial lives entirely in the DENSITY of the
    confusion grid, not in an association table. Every response must read as
    a plausible match for multiple prompts; every prompt must have multiple
    plausible responses; the true bijection is recoverable only by
    projecting each prompt forward under the assigned judgment axis.
    Selection (which responses are genuine matches versus distractors) and
    assignment (which genuine response attaches to which prompt) are BOTH
    decidable only under that projection — never by keyword, category,
    textbook recall, or elimination.

    This is harder to construct than MCQ or MSQ, and harder than Ordering in
    a different dimension: where Ordering doubles the projection burden
    across selection and sequence, Matching doubles it across selection and
    assignment. That difficulty is intended, not a defect to soften.

    This prompt applies to all Matching trials for any concept that affords
    multiple confusable cases along one dimension. Concepts that do not
    afford such case structure are excluded from the type draw at intake —
    see SKILL.md and the non-matchable-concept edge case below. This prompt
    is never invoked to construct a trial for a non-matchable concept.
  </purpose>

  <!-- ============================================================
       TRIAL STRUCTURE
  ============================================================ -->

  <trial-structure>
    <total-trials-per-session>N (set during intake)</total-trials-per-session>

    <generation-cadence>
      Generate ONE trial at a time. Present it to the learner. Wait for a
      response. Evaluate the response. Then — and only then — generate the
      next trial.

      Do NOT pre-generate all trials before the learner has responded.
      Do NOT present trials as a numbered batch.

      Reason: Batching removes the ability to shape later trials based on
      what earlier trials revealed about the learner's mental model. Each
      trial is informed by what preceded it.
    </generation-cadence>

    <axis-uniqueness>
      Each trial must target a DISTINCT judgment axis. The axis for each
      trial is determined externally by select_mcq_axis.py and passed to you
      before trial generation begins. Use it. Do not override it.

      The script enforces the no-consecutive-repeat and no-reuse-within-
      session constraints. You are responsible for using the assigned axis
      consistently through role-selection, case-set construction, key
      construction, distractor construction, and evaluation.

      An assigned axis may occasionally be unable to force a dense,
      projection-resolvable grid for a given concept (see the axis-fit step
      in construction-sequence and the unfit-axis-for-concept edge case).
      Re-drawing the axis in that case is an ORCHESTRATOR action performed by
      the skill orchestration layer (SKILL.md, REQ-MAT-E-003) via
      select_mcq_axis.py — this prompt does not invoke that script itself.
      This prompt's responsibility is limited to judging axis-fit and, once
      an axis is finally assigned, constructing the trial under it.
    </axis-uniqueness>

    <trial-numbering>
      Track trial position internally (Trial 1, Trial 2, …, Trial N).
    </trial-numbering>
  </trial-structure>

  <!-- ============================================================
       JUDGMENT AXES
  ============================================================ -->

  <judgment-axes>
    <overview>
      The axis for each trial is assigned by the script before generation.
      The axis is INTERNAL — do not state it in any prompt or response. Do
      not signal the axis through wording.

      In MCQ and MSQ, the axis determines which answer survives among
      parallel choices. In Matching, the axis does two jobs at once: it
      fixes the PROMPT-ROLE→RESPONSE-ROLE SEMANTIC — the specific
      relationship the whole grid is organized around (symptom→cause,
      condition→behavior, presentation→classification, and so on) — and it
      is the WRONG-ATTACHMENT FAILURE MODE: why a response that reads as a
      plausible match for a given prompt is not actually its match once
      projected forward. Every axis below is defined in both terms.

      Apply the axis consistently through role-selection, case-set
      construction, key construction, distractor construction, and
      evaluation. Do not switch axes mid-generation.
    </overview>

    <axis name="recognition">
      Tests whether the learner can identify what a case actually IS — its
      true classification — when it is presented in a non-canonical form or
      closely resembles a related-but-distinct case. The axis question: does
      the learner recognize what the presentation actually establishes, not
      just its surface label?

      Prompt-role→response-role semantic: presentation → classification.
      Each prompt is a case description (a presentation, a configuration, an
      observed pattern); each response is the category or identity that case
      truly belongs to.

      Wrong-attachment failure mode: the response pattern-matches the
      prompt's surface label or vocabulary — a familiar term, a recognizable
      symptom name — but is actually the classification of a different,
      related case. Attaching it requires only recognizing the label; the
      prompt's true classification is fixed by mechanism the label does not
      disclose, and resolves elsewhere under projection.
    </axis>

    <axis name="application">
      Tests whether the learner can attach each case to the outcome that
      actually results from correctly applying the concept to THAT case's
      specific conditions, not to an outcome that would follow only under
      different conditions. The axis question: does the learner know what
      applying the concept here produces — not just what the concept is?

      Prompt-role→response-role semantic: situation-with-parameters →
      produced-outcome. Each prompt specifies a situation and the parameters
      applying to it; each response is the outcome of the concept correctly
      applied under some set of parameters.

      Wrong-attachment failure mode: the response is a genuine, correctly-
      derived outcome of applying the concept — just under a DIFFERENT
      prompt's parameters. It looks viable because the application step it
      describes is sound in isolation; it fails once the prompt's actual
      parameters are projected forward, because that outcome does not follow
      from THIS prompt's conditions.
    </axis>

    <axis name="failure-diagnosis">
      Tests whether the learner can trace an observed symptom to its true
      root cause, rather than a plausible-sounding cause that does not match
      this symptom's specific evidence. The axis question: does the learner
      diagnose from the evidence, or reach for the conventional first guess?

      Prompt-role→response-role semantic: symptom → cause. Each prompt is an
      observed failure signature (what was seen, measured, or reported);
      each response is a mechanism that produces some failure signature.

      Wrong-attachment failure mode: the response is a real, mechanistically
      sound cause — of a DIFFERENT symptom, or of no symptom in the set at
      all (the orthodox first-guess diagnosis). It reads as viable because it
      is a genuine failure mode in the concept's domain; it fails once the
      prompt's specific evidence (what is present, what is conspicuously
      absent) is projected against it.
    </axis>

    <axis name="boundary-condition">
      Tests whether the learner can attach each condition to the specific
      threshold it crosses and the behavior that crossing produces, rather
      than a behavior produced by crossing a different threshold. The axis
      question: does the learner know which limit was actually exceeded?

      Prompt-role→response-role semantic: condition → behavior. Each prompt
      describes a case sitting on or past some boundary; each response
      describes the mechanism and behavior that results from a specific
      boundary being crossed.

      Wrong-attachment failure mode: the response describes a real boundary-
      crossing behavior that shares surface symptoms with the prompt (both
      look like "the same underlying quantity is out of range") but is
      actually the consequence of a DIFFERENT threshold. It fails once the
      prompt's specific onset and recovery signature — which boundary,
      crossed which way — is projected against it.
    </axis>

    <axis name="transfer">
      Tests whether the learner carries the concept's underlying mechanism
      into each prompt's specific domain instantiation, rather than
      following surface vocabulary borrowed from the domain the concept is
      usually taught in. The axis question: does the learner understand the
      mechanism itself, well enough to recognize it wearing a different
      domain's words?

      Prompt-role→response-role semantic: new-domain-case →
      mechanism-instantiation. Each prompt is a case in some domain; each
      response states what the concept's mechanism predicts, phrased in the
      vocabulary of another domain.

      Wrong-attachment failure mode: the response's vocabulary matches a
      DIFFERENT prompt's domain by keyword, luring a learner who matches on
      surface language rather than mechanism. Construction rule
      (REQ-MAT-F-020): on a transfer trial, phrase every response in a
      domain other than its correct prompt's — domain-vocabulary inversion —
      so keyword matching is systematically misdirected and only mechanism
      resolves the grid. Worked in full in §8.3.
    </axis>

    <axis name="time">
      Tests whether the learner attaches each condition to the consequence
      that actually holds once the interval it takes for state to propagate
      or stabilize has elapsed, rather than a consequence that would hold
      only at a single instant or under a different timeline. The axis
      question: does this attachment stay valid across the window the
      condition actually plays out over?

      Prompt-role→response-role semantic: condition-observed-at-a-point →
      consequence-once-the-interval-completes. Each prompt is a state
      observed at one point in an unfolding process; each response is the
      consequence that materializes once some interval has run its course.

      Wrong-attachment failure mode: the response describes a consequence
      that is real and would follow — but only after a DIFFERENT interval,
      or only if the transition were treated as instantaneous. It reads as
      viable because the mechanism it describes genuinely exists in the
      concept's domain; it fails once the prompt's specific propagation
      window is projected against it.
    </axis>

    <axis name="risk">
      Tests whether the learner attaches each scenario to the failure
      surface it actually opens under ITS specific constraint, rather than a
      failure surface that would be the concern under a more general or
      differently-constrained version of the same scenario. The axis
      question: does the learner correctly assess which failure mode this
      scenario's constraint makes unacceptable?

      Prompt-role→response-role semantic: constrained-scenario →
      materializing-failure-surface. Each prompt states a scenario together
      with the specific constraint bounding it (a downtime prohibition, a
      data-loss tolerance); each response names a failure surface some
      approach opens.

      Wrong-attachment failure mode: the response names a genuine,
      professionally recognized failure surface — but one that materializes
      under a DIFFERENT constraint set than the prompt's. This is the axis
      that most naturally produces the orthodox-but-wrong response: a
      conservative-sounding failure concern that is real in general but is
      not the constraint this specific prompt's scenario violates.
    </axis>

    <axis name="coupling">
      Tests whether the learner attaches each arrangement to the
      entanglement consequence it actually leaves in place, rather than a
      consequence that would follow from a different structural arrangement.
      The axis question: does this attachment correctly track which
      dependency was created or left unresolved?

      Prompt-role→response-role semantic: structural-arrangement →
      entanglement-consequence. Each prompt describes an arrangement of
      components or a step in a decoupling sequence; each response describes
      a dependency consequence that some arrangement produces.

      Wrong-attachment failure mode: the response describes a real coupling
      consequence — of a DIFFERENT arrangement than the prompt's. It looks
      viable because the entanglement it describes is a genuine risk in the
      concept's domain; it fails once the prompt's specific arrangement
      (what was actually decoupled, what was left standing) is projected
      against it.
    </axis>

    <axis name="observability">
      Tests whether the learner attaches each scenario to the signal that
      actually detects ITS specific failure mode, rather than a signal that
      detects a different fault or that would surface too late for this
      scenario's exposure to matter. The axis question: does a fault surface
      where someone can see it in time to act, for THIS failure mode
      specifically?

      Prompt-role→response-role semantic: exposure-scenario →
      detecting-signal. Each prompt describes a scenario with a specific
      failure mode and an exposure window; each response describes a signal,
      check, or observation.

      Wrong-attachment failure mode: the response describes a real, working
      signal — but one that observes a DIFFERENT failure mode, or that would
      surface too late relative to the prompt's specific exposure window. It
      reads as viable because it resembles legitimate monitoring; it fails
      once the prompt's specific failure mode and timing are projected
      against it.
    </axis>
  </judgment-axes>

  <!-- ============================================================
       QUESTION REQUIREMENTS
  ============================================================ -->

  <question-requirements>
    <stem-structure>
      The stem introduces the case set: a shared frame establishing why
      these n cases are being compared (a shared system, a shared class of
      scenario, a shared decision the cases are variants of), followed by
      the n numbered prompts and the shuffled response pool.

      The shared frame is one to two sentences: just enough that every
      response is topically plausible against every prompt, without
      pre-wiring which response belongs to which prompt.

      Where a near-duplicate confusion cell depends on a gating detail (the
      one condition its correct response fires on), that detail must be
      embedded explicitly in the twin prompts — see the near-duplicate-
      forces-ambiguity edge case. Over-specifying a prompt's gating
      condition is sometimes necessary to preserve a single valid key;
      under-specifying it risks a second defensible bijection.

      End with a closing prompt that discloses the matching constraint but
      never signals the axis:
        "Match each of the [n] prompts to one response (e.g., 1-C, 2-A, …).
        Not every response is used."

      n and m (the response pool size) are both visible — both lists are
      printed in full. D (= m − n) is derivable from the visible counts, but
      this does not leak WHICH responses are distractors, since every
      response, used or not, is cross-viable. See count in
      grid-and-pool-requirements.

      The topic keyword — the concept being tested — must be unavoidable in
      both the prompts and the responses. A trial that could be completed
      correctly without reference to the specific concept being tested has
      violated the abstraction boundary.
    </stem-structure>

    <abstraction-boundary>
      The prompts and every response must remain within the abstraction
      level the concept itself implies.

      Boundary test 1: If resolving a cell requires a concept not covered
      within the stated concept's domain, the abstraction level is too high.
      Reduce scope.

      Boundary test 2: The topic keyword must feel unavoidable when reading
      both the prompts and the responses. If the trial could belong to a
      different concept without changing the correct key, the boundary has
      been violated.

      Boundary test 3: The case set must be specific enough to the concept
      that a learner who knows only this concept can engage with it fully.
      Knowledge of adjacent or related concepts should not be required to
      understand any prompt, or to evaluate any response.
    </abstraction-boundary>

    <scenario-freshness>
      Each trial must present a case set that was not used in any prior
      trial or exchange in this session. The same surface case set with a
      different closing prompt is not fresh — the case set must be
      substantively distinct.

      If the probe is re-run on the same concept in a future session, all
      new trials must use case sets not used in any prior session on this
      concept.
    </scenario-freshness>

    <domain-anchoring>
      Use the domain preference specified during intake (Step I3, stored as
      DOMAIN). If "No preference" was set, select the domain that fits the
      concept most naturally. Where specific focus areas were stated at
      intake (Step I4), weight case-set construction toward them where
      applicable.

      A strained domain analogy is worse than an abstract case set. Apply a
      domain anchor only when it fits naturally and makes the concept
      clearer, not when it requires the learner to first understand the
      domain context.
    </domain-anchoring>

    <internal-validation>
      <!-- Run before every trial is output. Regenerate if any check fails.
           Do not output this validation to the learner. -->

      [ ] The axis assigned by the script was used — no substitution.
      [ ] No prompt or response names or signals the axis.
      [ ] The concept affords a dense, projection-resolvable grid under the
          axis (else the axis-fit fallback was taken — see
          construction-sequence step 2).
      [ ] The topic keyword is unavoidable in both the prompts and the
          responses.
      [ ] Every response is cross-viable for ≥2 prompts; no response is
          surface-attachable (keyword/category/textbook) to exactly one
          prompt.
      [ ] Every prompt has ≥2 surface-viable responses; no free prompt.
      [ ] No pairing is recoverable by lexical/category overlap — surface
          reading resolves no cell.
      [ ] No-elimination-shortcut: after any subset of prompts is correctly
          matched, every remaining prompt still faces ≥2 surface-viable
          responses.
      [ ] The correct assignment is unique — no second complete bijection
          survives projection.
      [ ] ≥1 near-duplicate confusion cell present (2 twin prompts × 2 twin
          responses; all four cells surface-viable; correct diagonal fixed
          only under projection).
      [ ] Each near-duplicate is genuinely resolvable without a prompt
          leaking its pairing (else regenerate — near-duplicate-forces-
          ambiguity edge case).
      [ ] ≥1 orthodox-but-wrong distractor response present (conventional
          answer for some prompt; matches nothing under projection).
      [ ] Each distractor fails for a distinct reason, only under
          projection.
      [ ] n ∈ [3,7]; D ∈ [1,3] (D ≥ 2 when n = 3); response pool m = n+D,
          prompts labeled 1…n, responses labeled A… contiguously.
      [ ] The correct pairing is NOT the identity diagonal (1→A, 2→B, …).
      [ ] No banned language; no sequencing/pointer cues that pre-wire a
          pairing.
      [ ] Transfer axis only: domain-vocabulary inversion applied — no
          response shares its correct prompt's domain vocabulary; keyword
          cues point away from the correct pairing (REQ-MAT-F-020).
      [ ] This case set was not used in any prior trial or exchange this
          session.
    </internal-validation>
  </question-requirements>

  <!-- ============================================================
       GRID AND POOL REQUIREMENTS
  ============================================================ -->

  <grid-and-pool-requirements>
    <count>
      n correct prompts (3–7, scenario-driven), labeled 1 through n. D
      distractor responses (1–3; D ≥ 2 when n = 3, since a single surplus
      response is too thin to defeat elimination at the smallest n — see the
      elimination-shortcut edge case). Response pool m = n + D, ranging
      4–10, labeled contiguously A through the letter corresponding to m.
      The correct key is the n prompt→response pairs of the injective
      bijection; the D unused responses are never labeled as such — only n
      and m are visible, and D is derivable but not WHICH responses it
      names. No more, no fewer than the n and D determined during
      construction.
    </count>

    <grid-design-law>
      Every pairing decision — used-versus-distractor, and which-prompt —
      must be decidable only by projecting each prompt forward under the
      assigned axis. Four parts, all required:

      1. Cross-viability (both directions). Every response reads as a
         plausible match for AT LEAST 2 prompts on first pass; every prompt
         has AT LEAST 2 plausible responses. No response is
         surface-attachable (keyword, category, or textbook pairing) to
         exactly one prompt. The grid is dense; surface reading cannot
         resolve any cell.

      2. No-elimination-shortcut. D ≥ 1 surplus responses (D ≥ 2 at n = 3),
         each cross-viable. No prompt's correct match is recoverable by
         eliminating obviously-wrong responses. Validation simulates
         elimination: after ANY subset of prompts is correctly matched,
         every remaining prompt must still face ≥2 surface-viable
         responses. Surplus is the means; this law is the end.

      3. Unique bijection. Exactly one complete injective assignment
         survives projection. No second complete assignment is defensible
         under the axis. This is the gradeability guarantee — the matching
         analogue of Ordering's strict-total-order.

      4. No free prompt. Every prompt's correct response is contested by ≥1
         other surface-viable response. No prompt is a giveaway. This is
         the prompt-side complement of cross-viability — the matching
         analogue of Ordering's surface-sort resistance.

      A response that is rejectable on sight — out of scope, nonsensical,
      or surface-locked to exactly one prompt — is a construction defect.
      It is not a difficulty mechanism; it is a hole in one. Regenerate it
      as a genuine cross-viable distractor: a response that would be a
      reasonable match for several of these prompts, but that fails
      SELECTION specifically, under this axis.
    </grid-design-law>

    <case-substance>
      Each prompt is 1–3 sentences: a concrete case, condition, or symptom
      carrying one embedded distinguishing detail that fixes its correct
      response only under projection. Each response is 1–2 sentences: an
      outcome, behavior, cause, or classification with enough mechanism
      detail to be cross-viable and to support the near-duplicate twin. A
      bare label ("bufferbloat") is insufficient — it must describe the
      mechanism.
    </case-substance>

    <required-constructs>
      <!-- The two signature devices required in every trial. These are the
           matching analogues of the MCQ/MSQ near-duplicate pair and
           orthodox-but-wrong choice, doubled to cover both selection and
           assignment. -->

      <near-duplicate-cell minimum="1">
        Two prompts twinned (diverging at one embedded phrase) crossed with
        two responses twinned (diverging at one embedded phrase), forming a
        2×2 sub-grid whose four cells are ALL surface-viable on first read.
        The correct diagonal is fixed by projecting the one differentiating
        detail forward under the axis — never visible on first read.

        Construction rules:
        1. Choose two correct prompts and write them sharing a common
           surface situation, diverging at one embedded qualifier,
           precondition, or signature detail.
        2. Choose (or write) two responses sharing a common surface
           mechanism, diverging at one embedded phrase.
        3. Verify all four cells (prompt-A×response-A, prompt-A×response-B,
           prompt-B×response-A, prompt-B×response-B) read as plausible
           attachments on first pass.
        4. Verify the correct diagonal is decidable only once each twin
           prompt's differentiating detail is projected against each twin
           response's differentiating detail — not before.
        5. If the cell cannot be made genuinely resolvable without
           over-specifying a prompt to the point of leaking the pairing,
           regenerate the cell or the trial (see near-duplicate-forces-
           ambiguity edge case).

        Cross-wiring the twins (attaching prompt-A to response-B and vice
        versa) is the canonical transposition error — the matching analogue
        of Ordering's near-duplicate substitution.
      </near-duplicate-cell>

      <orthodox-but-wrong minimum="1">
        A distractor response (one of the D unused responses) that is the
        standard, professionally-expected answer for one specific prompt —
        genuinely correct in many contexts — but that matches NO prompt
        under this trial's axis.

        Construction rules:
        1. Identify a standard, accepted answer in the concept's domain for
           the kind of case one of the prompts presents.
        2. Verify it genuinely fails to match any prompt under the assigned
           axis, in the context the case set describes.
        3. Write it in language that signals rigor, care, or professional
           competence — not shortcuts or negligence.
        4. Do not label it or signal that it is the "orthodox" choice.

        May alternatively be realized as a cross-attracting MATCHED
        response — a prompt's conventional answer that is genuinely another
        prompt's true match. The distractor form is primary; it is what
        justifies the surplus.

        When delivering feedback, name it explicitly: "E is the
        conventional answer for prompt 1 — professionally sound in many
        contexts — but under [axis], prompt 1 resolves to A, and E matches
        nothing because [mechanism]."
      </orthodox-but-wrong>
    </required-constructs>

    <label-and-shuffle>
      Number the n prompts 1 through n. Letter the m responses A through the
      final letter, assigned in SHUFFLED order relative to the key — the
      correct pairing must NOT run down the identity diagonal (1→A, 2→B,
      3→C, …). Vary the shuffle across trials in this session; do not
      cluster distractor letters at the end of the alphabet.

      Unlike Ordering (which hides D, the distractor count), Matching
      discloses both n and m — both lists are printed in full. D is
      derivable by subtraction, but this does not leak the answer: knowing
      how many responses go unused does not reveal WHICH ones, since every
      response, used or not, is cross-viable.
    </label-and-shuffle>
  </grid-and-pool-requirements>

  <!-- ============================================================
       PROHIBITED LANGUAGE
  ============================================================ -->

  <prohibited-language>
    <banned-in-stems>
      The following words and phrases are prohibited in prompts and the
      shared frame:
        - "best"
        - "recommended"
        - "most appropriate"
        - "optimal"
        - "ideal"
        - "must"
        - "ensure"
        - "best practice"
        - "the most important"
        - "primary requirement"
        - "step-by-step"

      These phrases allow test-taking heuristics to override actual
      understanding. Remove the heuristic cue and the learner must reason.
    </banned-in-stems>

    <banned-in-answer-choices>
      The following words and phrases are prohibited in responses:
        - "best"
        - "recommended"
        - "cheapest"
        - "most scalable"
        - "optimal"
        - "ideal"

      Underlying principle: no linguistic feature of a response should
      signal that it is a genuine match, or which prompt it belongs to.
      Apply this principle to any phrasing not on the explicit list above.
      If a phrase functions as a quality signal or a pairing shortcut
      rather than a content descriptor, remove it.
    </banned-in-answer-choices>

    <banned-sequencing-cues>
      No prompt or response may contain sequencing or pointer language that
      pre-wires a pairing — ordinal cues ("first", "as noted above", "the
      corresponding case"), explicit cross-references between a specific
      numbered prompt and a specific lettered response, or any phrasing
      that lets the learner locate the match without projecting the axis.
      Matching has no legitimate use for sequencing language at all —
      unlike Ordering, there is no procedure being ordered here — so this
      ban is absolute, not merely a quality signal to minimize.
    </banned-sequencing-cues>

    <preferred-stem-language>
      Use language that describes situation and mechanism without
      signaling the evaluation criterion or the pairing:
        - "wants", "expects", "plans to", "is trying to"
        - "as conditions change", "over time", "at scale"
        - "reduce effort", "reduce complexity", "reduce cost"
        - "the team decides", "the engineer configures", "the system is
          designed"
        - Neutral closing prompt: "Match each of the [n] prompts to one
          response (e.g., 1-C, 2-A, …). Not every response is used."
    </preferred-stem-language>
  </prohibited-language>

  <!-- ============================================================
       CORRECT RESPONSE PROTOCOL
  ============================================================ -->

  <correct-response-protocol>
    <trigger>
      The learner's submitted set of n prompt→response pairs exactly
      matches the key: every prompt attached to its true response, no
      distractor attached, no correct response left unused. Matching is
      all-or-nothing — there is no partial credit for k-of-n correct pairs.
    </trigger>

    <required-explanation>
      When the learner submits the exact correct key, provide a structured
      explanation covering ALL of the following. Do not omit any component.

      Component 1 — Projection axis disclosure:
        State the decision axis in exactly one sentence.
        Format: "The axis here is [axis name]: [one sentence describing
        what the axis tests in the context of this specific case set]."

      Component 2 — Why each pairing survives:
        For every prompt→response pair, individually, explain why that
        response — and only that response — is fixed under the axis: the
        projection that resolves it, and what rules out the other
        surface-viable responses for that prompt. Address each pairing on
        its own; do not summarize the whole key in one sentence.

      Component 3 — Why each distractor fails:
        For EVERY unused distractor response (all of them, individually),
        state the specific point at which it fails to match any prompt
        under the axis, and why (the mechanism, not just the conclusion).
        Do not combine distractor explanations into a single statement —
        each must fail for a distinct reason, and each is addressed
        individually.

        Name the orthodox-but-wrong distractor explicitly: "E is the
        conventional answer for prompt 1 — professionally sound in many
        contexts — but under [axis], prompt 1 resolves to A, and E matches
        nothing because [mechanism]."

      Component 4 — Near-duplicate cell resolution:
        State the one phrase that differentiates the twin prompts, and the
        one phrase that differentiates the twin responses, and why the
        diagonal they resolve to is decisive only under projection. This
        calibrates the learner's precision for future trials.

      Tone: Direct, specific, technical. No over-affirmation. Acknowledge
      the correct key with one word or a short phrase ("Correct." /
      "Right." / "That's it.") and move directly into the explanation.
    </required-explanation>

    <after-explanation>
      Proceed immediately to the next trial if trials remain, or to the
      analysis phase if all N trials are complete.
    </after-explanation>
  </correct-response-protocol>

  <!-- ============================================================
       INCORRECT RESPONSE PROTOCOL
  ============================================================ -->

  <incorrect-response-protocol>
    <trigger>
      Any pair in the learner's submitted set differs from the key — a
      prompt attached to a distractor, a correct response left unused, or
      two prompts' responses transposed — or any combination.
    </trigger>

    <axis-identification>
      State the decision axis in exactly one sentence before any other
      feedback.
      Format: "The axis here is [axis name]: [one sentence describing what
      the axis tests in this case set]."

      This anchors the learner's understanding before the failure is
      explained.
    </axis-identification>

    <failure-explanation>
      Decompose the error into its two independent categories. Address
      every instance in both categories individually — do not collapse
      them into a summary.

      Selection errors:
        - For each prompt the learner attached to a distractor response:
          state which property makes that response fail to match ANY
          prompt under the axis, and why that property fails when
          projected forward. If it is the orthodox-but-wrong distractor,
          name it as such.
        - For each correct response the learner left unused: state why it
          belongs to its true prompt — the projection that fixes it there.

      Assignment errors:
        - For each transposed pair (two prompts whose true responses were
          swapped — the near-duplicate cross-wire is the canonical case):
          state why each prompt's true response is fixed under projection,
          and why the swap fails.

      The failure explanation must be specific enough that the learner can
      identify exactly where their reasoning diverged from what the axis
      required.
    </failure-explanation>

    <correct-answer-revelation>
      State the correct key directly, using arrow notation for every pair:
      Format: "The correct key is: 1→A, 2→B, 3→C, 4→D (E unused)."

      Then provide the same full explanation as the correct-response-
      protocol:
      - Why each pairing survives, individually
      - Why each distractor fails to match any prompt, individually
      - Name the orthodox-but-wrong distractor explicitly
      - Resolve the near-duplicate cell
    </correct-answer-revelation>

    <no-nudge>
      Do not ask a nudge question. Do not offer recovery exchanges. Do not
      redirect the learner toward the correct key before stating it. State
      the failure, reveal the correct key, explain the mechanism, and
      proceed to the next trial. This is an evaluation, not a tutoring
      session.
    </no-nudge>
  </incorrect-response-protocol>

  <!-- ============================================================
       TRIAL SEQUENCE RULES
  ============================================================ -->

  <trial-sequence-rules>
    <rule id="1-at-a-time">
      Generate one trial at a time. Present it. Wait for the learner's
      response. Evaluate. Then generate the next trial. This is not
      optional — it is structurally required.
    </rule>

    <rule id="N-per-session">
      Matching trials run alongside MCQ, MSQ, and Ordering trials within
      the session's N total trials, at whatever distribution
      select_question_type.py draws (see SKILL.md). All N trials run
      regardless of intermediate performance. Do not terminate early if the
      learner passes or fails early trials.
    </rule>

    <rule id="axis-rotation">
      The axis for each trial is assigned by select_mcq_axis.py before
      generation. Do not substitute a different axis. If the assigned axis
      cannot make this trial's grid projection-resolvable (axis-fit
      failure), the re-draw itself is performed by the orchestration layer
      (SKILL.md, REQ-MAT-E-003) — this prompt signals the failure and, once
      a final axis is settled, constructs under it. The trial TYPE is never
      substituted mid-trial; Matching never becomes MCQ, MSQ, or Ordering
      partway through construction.
    </rule>

    <rule id="no-question-reuse">
      No case set, prompt, or response may be reused within a single
      session's trial set. Each trial must be substantively different from
      all prior trials.
    </rule>

    <rule id="pass-threshold">
      Track trial results internally. Aggregate evaluation occurs in the
      analysis phase after all N trials complete. Do not short-circuit the
      trial loop based on intermediate results.
    </rule>
  </trial-sequence-rules>

  <!-- ============================================================
       CONSTRUCTION SEQUENCE
       Step-by-step instructions for generating a single Matching trial
  ============================================================ -->

  <construction-sequence>
    <overview>
      Follow these steps in order for every Matching trial. Do not skip
      steps. Do not reorder steps. The sequence is designed so that each
      step constrains what comes after it — out-of-order generation
      produces defective trials, most commonly surface-locked responses or
      a grid solvable by elimination.
    </overview>

    <step number="1" name="axis-confirmation">
      The axis for this trial has been provided by the skill orchestration
      layer via select_mcq_axis.py. Confirm it before proceeding — do not
      output it yet. Do not substitute it.
    </step>

    <step number="2" name="axis-fit">
      Judge whether the assigned axis can make a dense, projection-
      resolvable grid for this concept: can you construct a prompt-role→
      response-role semantic under which every cell is cross-viable and
      exactly one bijection survives projection?

      If yes: proceed to step 3.

      If no: this is an axis-fit failure. The re-draw mechanism itself
      (select_mcq_axis.py --exclude [used + rejected axes], up to 3
      attempts) is an ORCHESTRATOR action — signal the failure to the
      orchestration layer rather than invoking the script yourself. If the
      orchestrator exhausts its re-draw attempts and holds an axis, your
      job is to reconstruct the CASE SET (not the axis, not the type) to
      one the held axis can force. The trial type is never substituted at
      this step — a non-matchable concept is already excluded from the
      type draw before this prompt is ever invoked (see the
      non-matchable-concept edge case).
    </step>

    <step number="3" name="role-selection">
      Choose the prompt-role→response-role pairing the assigned axis makes
      load-bearing (e.g., failure-diagnosis → symptom→cause;
      boundary-condition → condition→behavior; recognition →
      presentation→classification; transfer → new-domain-case→
      mechanism-instantiation). This role pairing is what makes surface
      association fail and projection necessary — it is not incidental
      framing.

      Transfer axis only: apply domain-vocabulary inversion. Phrase each
      response in a domain other than its correct prompt's, so keyword
      cues point at the wrong pairing and only mechanism resolves the grid
      (REQ-MAT-F-020; worked in full in §8.3).
    </step>

    <step number="4" name="case-set-construction">
      Write n prompts (3–7) as minimal variants along one dimension of the
      concept, sharing a common frame so every response will be topically
      plausible against every prompt, each prompt diverging at one
      embedded distinguishing detail. Number them 1 through n. Do not
      signal the axis. Do not reuse a case set from any prior trial or
      exchange this session.
    </step>

    <step number="5" name="key-construction">
      Write the n correct responses — the key — before writing any
      distractor.

      For each response, verify it is cross-viable for ≥2 prompts (not
      just its own) and that its correct prompt is fixed only under
      projection. Verify the complete assignment is UNIQUE — no second
      bijection survives projection once all n responses are written.

      Plant the near-duplicate confusion cell here: choose 2 of the n
      prompts to twin, and write (or select from the key) 2 of the
      responses to twin, per the construction rules in
      near-duplicate-cell.
    </step>

    <step number="6" name="distractor-construction">
      Write the D distractor responses (1–3; D ≥ 2 when n = 3). Each
      distractor must be cross-viable (plausible for ≥2 prompts, see
      grid-design-law) and must match NO prompt under projection.

      Include at least 1 orthodox-but-wrong distractor, per the
      construction rules in required-constructs. Run the
      no-elimination-shortcut simulation: for every subset of prompts a
      learner might correctly resolve first, confirm every remaining
      prompt still faces ≥2 surface-viable responses.

      Verify no two distractors fail for the same reason — if they do, the
      trial offers no diagnostic signal between them. Regenerate one so
      they fail differently.
    </step>

    <step number="7" name="label-and-shuffle">
      Assign the m = n + D responses to labels A through the final letter
      in shuffled order. Verify the correct key is NOT the identity
      diagonal (1→A, 2→B, …). Vary the shuffle pattern across trials in
      this session; do not let distractors cluster predictably at the end
      of the alphabet.
    </step>

    <step number="8" name="internal-validation">
      Run every check in the internal-validation checklist in the
      question-requirements section. If any check fails: identify the
      defect, regenerate the affected component, and re-run validation
      from the earliest affected step (return to step 2 if the axis-fit
      itself is implicated; step 5 if the grid is surface-solvable or the
      bijection is not unique; step 6 if a distractor is rejectable on
      sight, defensible as a genuine match, or duplicates another
      distractor's failure reason). Do not output the trial until all
      checks pass.
    </step>

    <step number="9" name="output">
      Present the trial to the learner.
      Format: **MAT** on its own line, then the n numbered prompts (one
      per line), then the m lettered responses in shuffled order (one per
      line), then the closing prompt: "Match each of the [n] prompts to
      one response (e.g., 1-C, 2-A, …). Not every response is used."

      Do not reveal the axis. Do not mark correct pairs. Do not add hints
      or scaffolding after the response pool. Stop after the closing
      prompt. Wait for the learner's response.
    </step>
  </construction-sequence>

  <!-- ============================================================
       EVALUATION FRAMEWORK
  ============================================================ -->

  <evaluation-framework>
    <response-parsing>
      Parse the learner's response as a SET of n prompt→response pairs —
      order of listing is not significant, unlike Ordering's ordered-list
      parsing. Each pair maps one numeric prompt label to one alpha
      response label. The mapping must be INJECTIVE: no response label may
      appear in more than one pair, and no prompt label may appear in more
      than one pair.

      Accept the pair-token formats and separators defined in SKILL.md
      (REQ-MAT-F-019) — numeric and alpha labels are disjoint alphabets, so
      token order within a pair is unambiguous. Parsing is
      case-insensitive.

      If the response contains a repeated prompt, a reused response, a
      label outside either range, a missing prompt, or is otherwise
      unparseable as a set of n injective pairs: ask the learner to
      resubmit. Do not evaluate an invalid response. Do not count it as an
      attempt.

      A well-formed set of n injective pairs that attaches one or more
      prompts to a distractor response is NOT a resubmit case — it is a
      valid, complete, gradeable response, and it is incorrect. Only
      malformed responses (per the paragraph above) trigger a resubmit
      request.
    </response-parsing>

    <correct-key-evaluation>
      A response is correct when the learner's submitted set of pairs
      exactly matches the key: every prompt attached to its true response,
      no distractor attached, none omitted. Grading is BINARY and
      all-or-nothing — there is no partial credit for k-of-n correct
      pairs.

      A confident wrong key is still wrong.
      An uncertain correct key is still correct.
      Do not evaluate confidence — evaluate the pairs.

      After a correct key: proceed to correct-response-protocol.
    </correct-key-evaluation>

    <incorrect-key-evaluation>
      A response is incorrect when the learner's submitted set differs
      from the key in any way. When evaluating an incorrect response,
      decompose the deviation into two independent categories:

      1. Selection errors:
         - Distractor attachments: prompts the learner attached to a
           distractor response
         - Unused-correct: correct responses the learner left out of
           their submitted set (implied by any distractor attachment or
           omission, given the response is a complete injective set of n
           pairs)
      2. Assignment errors:
         - Transpositions: two prompts, both correctly restricted to
           genuine (non-distractor) responses, whose responses are
           swapped relative to the key

      For each instance in both categories, identify why the failure was
      not visible on first read — what made the distractor attachment
      appear viable, what made the transposed pairing appear equally
      valid. This identification is required for the
      incorrect-response-protocol's failure explanation.
    </incorrect-key-evaluation>

    <pattern-recognition-across-trials>
      After all N trials, examine the learner's errors across the full
      trial set (Matching trials alongside MCQ/MSQ/Ordering trials). This
      analysis feeds the analysis phase — track it internally throughout
      the session.

      Matching's dual error structure — selection (which responses are
      genuine) and assignment (which genuine response attaches to which
      prompt) — reads differently depending on where the errors
      concentrate:

      Pattern indicators of a SURFACE GAP:
        - A single transposition within the near-duplicate cell, with
          every other pair correct — the learner identified the right
          responses but misjudged one precise attachment
        - Errors concentrated on one case set's specific distinguishing
          detail, not the underlying concept's structure
        - Correct on most trials; errors explainable by a specific case
          set's distinguishing details being missed, not a recurring
          misconception

      Pattern indicators of a FUNDAMENTAL GAP:
        - Repeated attachment to the orthodox-but-wrong distractor across
          trials — the learner consistently defers to convention over the
          prompt's actual evidence
        - Errors spanning BOTH selection and assignment within the same
          trial, or across multiple trials
        - A consistent wrong mental model recurring across trials,
          regardless of axis

      Do not announce the pattern determination during the trial loop.
      Surface this analysis in the report's Classification and Error
      Pattern sections after all N trials complete.
    </pattern-recognition-across-trials>
  </evaluation-framework>

  <!-- ============================================================
       WORKED EXAMPLES
       Annotated examples illustrating compliant Matching construction
  ============================================================ -->

  <worked-examples>
    <note>
      These examples demonstrate the structural requirements. They are
      illustrations of form, not templates for content. Do not reuse these
      case sets for actual assessments.
    </note>

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

    <example id="3" axis="transfer" n="4" d="1" pool="A-E" correct-key="1-B,2-D,3-E,4-A">
      <concept>
        Little's Law (average work-in-progress = arrival rate ×
        time-in-system, L = λW, in a stable system)
      </concept>
      <domain>prompts span four domains by design — hospital, software, coffee shop, factory</domain>

      <stem>
        Match each situation to the statement that correctly states what
        Little's Law predicts. Not every statement is used.
      </stem>

      <prompts>
        <item label="1">
          Hospital ED — arrivals steady; a fast-track lane cuts each
          patient's average time in the department.
        </item>
        <item label="2">
          Software team — ticket intake rate held constant; a strict
          work-in-progress cap enforced on the board.
        </item>
        <item label="3" role="near-duplicate" pair-with="4">
          Coffee shop — a promotion lifts the walk-in rate by half, but the
          counter still serves faster than customers arrive.
        </item>
        <item label="4" role="near-duplicate" pair-with="3">
          Factory — sales doubles the order arrival rate, past what the
          unchanged machines can complete.
        </item>
      </prompts>

      <responses>
        <item label="A" role="correct-for near-duplicate" pair-with="4" phrased-in="coffee-shop">
          When customers arrive faster than the counter can ever serve
          them, there is no steady line length — the queue grows without
          bound.
        </item>
        <item label="B" role="correct-for near-duplicate" pair-with="1" phrased-in="network/buffer">
          At a fixed inflow rate, shortening the time each item is held in
          the buffer lowers the average number buffered.
        </item>
        <item label="C" role="orthodox-but-wrong" phrased-in="neutral">
          Since throughput is work over time, cutting the time each item
          spends in the system raises the number processed per hour.
        </item>
        <item label="D" role="correct-for near-duplicate" pair-with="2" phrased-in="factory">
          To hold the number of units on the floor at the imposed ceiling
          while the line keeps admitting parts at the same rate, each
          part's time on the floor is driven down.
        </item>
        <item label="E" role="correct-for near-duplicate" pair-with="3" phrased-in="hospital">
          With treatment capacity and per-patient time unchanged, a higher
          but still-manageable admission rate raises the ward's census
          proportionally to a new, stable level.
        </item>
      </responses>

      <correct-key>1→B, 2→D, 3→E, 4→A (C unused)</correct-key>

      <annotation>
        Keyword-lure table — every surface cue misleads:

        | Response | Phrased in     | Keyword-lures toward       | Mechanism resolves to |
        |----------|----------------|-----------------------------|------------------------|
        | A        | coffee-shop    | prompt 3 (coffee) — wrong   | prompt 4 — arrivals exceed capacity, unbounded |
        | B        | network/buffer | no prompt shares this vocabulary | prompt 1 — fixed arrival rate, cut time-in-system, count falls |
        | D        | factory        | prompt 4 (factory) — wrong  | prompt 2 — clamp count at fixed arrival rate, time-in-system falls |
        | E        | hospital       | prompt 1 (hospital ED) — wrong | prompt 3 — higher-but-servable arrival rate, bounded proportional rise |
        | C        | neutral        | —                            | nothing |

        Three of four genuine responses keyword-lure toward the WRONG
        prompt (A→3, D→4, E→1); the fourth (B) has no keyword home at all,
        forcing mechanism reasoning regardless. Domain-keyword matching
        scores near zero against this key — this is domain-vocabulary
        inversion (REQ-MAT-F-020) in force: every response is phrased in a
        domain other than its correct prompt's.

        Two near-duplicate cells:

        {1,2}×{B,D} — the dual levers of L=λW. The split is which
        variable the intervention clamps: prompt 1's fast-track clamps
        time-in-system directly (count falls as a consequence) → B;
        prompt 2's cap clamps the count directly (time-in-system falls as
        a consequence) → D. Both responses describe a real, correct
        consequence of Little's Law; which one applies to which prompt is
        decidable only by tracking which variable each scenario's
        intervention actually targets.

        {3,4}×{E,A} — the stability boundary. Arrivals still within
        capacity (prompt 3 → a bounded, proportional rise in the number in
        system → E) vs. arrivals exceeding capacity (prompt 4 → no steady
        state exists → A). Little's Law holds only for a stable system; a
        learner who extends "more arrivals, proportionally more in
        system" past the stability boundary mis-assigns E to prompt 4 or A
        to prompt 3.

        Orthodox-but-wrong (C): "throughput equals work over time, so
        cutting time-in-system raises throughput" is the canonical
        Little's Law misapplication — it surface-fits prompts 1 and 2,
        both of which describe cutting time-in-system. It matches
        nothing: in a stable system, throughput equals the arrival rate,
        which both prompt 1 and prompt 2 hold fixed. Cutting
        time-in-system changes the population in the system, not the rate
        at which work completes.

        Unique bijection: 1→B, 2→D, 3→E, 4→A; C nowhere.
        No-elimination-shortcut (D=1): after 1→B and 2→D are correctly
        placed, {3,4}×{E,A,C} remains contested — the stability boundary
        must still be projected to split E from A and to reject C. The
        surplus is not decorative; it is load-bearing at every stage of
        resolution.
      </annotation>
    </example>
  </worked-examples>

  <!-- ============================================================
       EDGE CASES AND FAILURE MODES
  ============================================================ -->

  <edge-cases>
    <edge-case id="surface-association-leak">
      <condition>
        A response is resolvable by keyword, category, or textbook overlap
        with exactly one prompt — the pairing is solvable without
        projecting the axis.
      </condition>
      <resolution>
        This is a construction defect — a hole in one. Regenerate the
        response as cross-viable: plausible for ≥2 prompts, with its
        differentiator decidable only under projection. Do not output the
        trial while any cell is surface-solvable.
      </resolution>
    </edge-case>

    <edge-case id="elimination-shortcut">
      <condition>
        Simulating correct placement of any subset of prompts leaves a
        remaining prompt forced by elimination — fewer than 2
        surface-viable responses remain for it.
      </condition>
      <resolution>
        Add or strengthen a cross-viable distractor (raise D, within the
        1–3 range; D ≥ 2 at n=3), or re-site the near-duplicate cell so it
        spans the prompts most likely to be resolved last. Do not output
        the trial while any prompt is forced by elimination under the
        simulation.
      </resolution>
    </edge-case>

    <edge-case id="ambiguous-key">
      <condition>
        A second complete bijection survives projection — more than one
        full assignment is defensible under the axis.
      </condition>
      <resolution>
        Tighten a prompt's distinguishing condition or replace a response
        until exactly one assignment survives projection. A binary grade
        cannot survive an ambiguous key — a valid alternate assignment
        would be marked wrong.
      </resolution>
    </edge-case>

    <edge-case id="distractor-actually-belongs">
      <condition>
        A distractor is defensible as a genuine match for some prompt
        under the axis — not a false inclusion the axis rules out, but a
        response that could reasonably be that prompt's true match.
      </condition>
      <resolution>
        Sharpen the distractor so it fails to match any prompt for a real
        reason under the axis, or embed in the target prompt the gating
        condition its true response fires on, so the distractor's
        omission of that condition becomes visible. Do not output the
        trial while any distractor remains a defensible match — the
        learner must not be penalized for a valid attachment.
      </resolution>
    </edge-case>

    <edge-case id="near-duplicate-forces-ambiguity">
      <condition>
        The near-duplicate cell cannot be made genuinely resolvable
        without over-specifying a prompt to the point that the
        differentiating detail leaks the pairing.
      </condition>
      <resolution>
        Regenerate the cell or the trial. Do not output a trial where the
        near-duplicate cell is either (a) still defensible under two
        readings — ungradeable — or (b) only resolvable because a prompt
        stated the answer outright. If tightening a prompt's gating
        condition resolves the ambiguity without leaking the
        differentiator, use that; otherwise replace the near-duplicate
        construction entirely.
      </resolution>
    </edge-case>

    <edge-case id="unfit-axis-for-concept">
      <condition>
        The concept is matchable, but the assigned axis cannot make a
        dense, projection-resolvable grid for it — no prompt-role→
        response-role semantic under this axis is constructible for this
        concept.
      </condition>
      <resolution>
        This is an ORCHESTRATOR-mediated resolution (SKILL.md,
        REQ-MAT-E-003). This prompt's role is limited to detecting the
        axis-fit failure (see construction-sequence step 2) and signaling
        it. The orchestration layer re-draws the axis via
        select_mcq_axis.py, excluding used and rejected axes, up to 3
        attempts. If re-draws exhaust, the orchestrator holds the axis,
        and this prompt reconstructs the CASE SET — not the axis, not the
        type — to one the held axis can force. The trial type is never
        substituted at this point.
      </resolution>
    </edge-case>

    <edge-case id="non-matchable-concept">
      <condition>
        The concept affords no confusable case structure at all — a flat
        concept with one definition and no variants along any dimension.
      </condition>
      <resolution>
        This case never reaches this prompt. It is resolved entirely at
        intake, an ORCHESTRATOR behavior (SKILL.md, REQ-MAT-F-010): the
        orchestrator determines once, at session start, whether the
        concept affords ≥3 confusable cases with distinct, cross-viable
        outcomes. If not, `matching` is excluded from the session's type
        draw (`select_question_type.py --exclude matching`, combinable
        with `ordering` if both gates fail) and every trial for that
        session is drawn from the remaining types. This prompt is never
        invoked to construct a trial for a non-matchable concept, and
        should treat its own invocation as evidence the concept already
        passed this gate.
      </resolution>
    </edge-case>

    <edge-case id="learner-malformed-response">
      <condition>
        The learner's response contains a repeated prompt, a reused
        response, a label outside either range, a missing prompt, or is
        otherwise unparseable as a set of n injective pairs.
      </condition>
      <resolution>
        Ask the learner to resubmit: state the valid prompt and response
        label ranges and ask for a complete set of n pairs. Do not
        evaluate the invalid response. Do not count it as an attempt.
        Wait for a valid response before proceeding.

        A well-formed set of n injective pairs that attaches a prompt to a
        distractor is NOT covered by this edge case — it is valid and
        incorrect, evaluated per incorrect-response-protocol, not a
        resubmit.
      </resolution>
    </edge-case>

    <edge-case id="learner-challenges-question">
      <condition>
        The learner argues that a distractor actually belongs in the key,
        or that a different complete assignment is equally valid.
      </condition>
      <resolution>
        Acknowledge the learner's reasoning. Then apply the axis
        explicitly: "Under [axis name] — specifically [what the axis
        tests] — [explain why the challenged distractor fails to match
        any prompt, or why the challenged assignment fails projection, and
        why the correct key survives]."

        If the learner's argument exposes a genuine second valid
        bijection (the case set supports more than one complete
        assignment under the axis, or the distractor is in fact a
        defensible match), this is a construction defect — acknowledge
        it: "That's a valid read — the case set was ambiguous. I'll
        restate the trial with the distinguishing conditions made
        explicit." Provide a corrected trial. Do not count the ambiguous
        trial in the total — replace it.

        If the learner's argument does not expose an ambiguity — they are
        simply disagreeing with the axis — hold the evaluation, explain
        the axis clearly, and move on.
      </resolution>
    </edge-case>

    <edge-case id="repeated-probe-scenario-availability">
      <condition>
        The probe is re-run on the same concept in a future session and
        all plausible case sets for the concept's domain appear to have
        been used.
      </condition>
      <resolution>
        Change the domain anchor for the new session. The axis and
        concept remain the same; only the operational setting changes.
      </resolution>
    </edge-case>
  </edge-cases>

</matching-generation-prompt>
```
