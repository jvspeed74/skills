```xml
<ordering-generation-prompt>

  <!-- ============================================================
       LOADING INSTRUCTIONS
       Load this file ONCE at session start, before the first ordering trial.
       Retain in context for all ordering trials in this session.
       Do NOT reload before each trial.
       If this file cannot be read, halt and report the error.
       Ordering trials shall not be generated without this prompt.
  ============================================================ -->

  <purpose>
    This prompt governs the generation, structure, and evaluation of all Ordering
    trials used in mcq-probe assessments.

    An Ordering trial is not a knowledge quiz. It is a judgment probe. Its purpose
    is to distinguish a learner who commands a procedure — which steps belong and
    in what forced order — from a learner who has only memorized the steps as an
    unordered checklist. Unlike MCQ and MSQ, which probe judgment among parallel
    choices, Ordering probes a structural dependency: every pool item, correct step
    or distractor, must read as a legitimate step in this task. Nothing is
    rejectable as unrelated, broken, or obviously misplaced. Selection (which
    steps belong) and ordering (what sequence they run in) are both decidable
    only by projecting the scenario forward under the assigned axis.

    This is the hardest of the three trial types by construction, because it
    doubles the projection burden: the learner must reject false inclusions AND
    resist a sequence that surface intuition ("setup first, cleanup last") would
    otherwise resolve for them. That difficulty is intended, not a defect to
    soften.

    This prompt applies to all Ordering trials for any concept that affords an
    ordered, dependency-bearing procedure. Concepts that do not afford such a
    procedure are excluded from the type draw at intake — see SKILL.md and the
    non-procedural-concept edge case below. This prompt is never invoked to
    construct a trial for a non-procedural concept.
  </purpose>

  <!-- ============================================================
       TRIAL STRUCTURE
  ============================================================ -->

  <trial-structure>
    <total-trials-per-session>N (set during intake)</total-trials-per-session>

    <generation-cadence>
      Trials are generated as a BATCH, ahead of delivery. The orchestration layer
      (SKILL.md) runs a Generation Phase that constructs every trial in the batch —
      each one carried through this prompt's full construction sequence, including
      internal validation and explanation-baking — before any trial is presented.

      Each trial is constructed and validated independently and completely. A trial
      is never left partially built to be finished later, and no trial's content
      depends on how the learner answered any other.

      Batched GENERATION does not change PRESENTATION. Do NOT present trials as a
      numbered batch: the Delivery Loop still presents one trial, waits for the
      learner's response, evaluates it, and only then moves to the next.

      Reason: mcq-probe does not adapt trial content to intermediate performance.
      All N trials run regardless of results, and both the question type and the
      judgment axis are drawn by the selector scripts rather than by what earlier
      trials revealed. The one genuine cross-trial constraint is axis variety, and
      it is preserved exactly — the batch draw assigns a distinct axis to every
      slot before any trial content is written.
    </generation-cadence>

    <axis-uniqueness>
      Each trial must target a DISTINCT judgment axis. The axis for each trial
      is determined externally by select_mcq_axis.py and passed to you before
      trial generation begins. Use it. Do not override it.

      The script enforces the no-consecutive-repeat and no-reuse-within-session
      constraints. You are responsible for using the assigned axis consistently
      through scenario construction, sequence construction, and evaluation.

      An assigned axis may occasionally be unable to force a given scenario's
      order (see the axis-fit step in construction-sequence and the
      unfit-axis-for-scenario edge case). Re-drawing the axis in that case is an
      ORCHESTRATOR action performed by the skill orchestration layer (SKILL.md,
      REQ-ORD-E-003) via select_mcq_axis.py — this prompt does not invoke that
      script itself. This prompt's responsibility is limited to judging axis-fit
      and, once an axis is finally assigned, constructing the trial under it.
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
      The axis is INTERNAL — do not state it in the task scenario or in any pool
      item. Do not signal the axis through wording.

      In MCQ and MSQ, the axis determines which answer survives among parallel
      choices. In Ordering, the axis does two jobs at once: it is the FORCING
      DEPENDENCY that fixes the order between steps (why step X cannot legally
      follow step Y), and it is the DISTRACTOR FAILURE MODE (why a false
      inclusion looks like a legitimate step but fails selection once projected).
      Every axis below is defined in both terms.

      Apply the axis consistently through scenario construction, sequence
      construction, distractor construction, and evaluation. Do not switch axes
      mid-generation.
    </overview>

    <axis name="recognition">
      Tests whether the learner can identify which pool items are genuine steps
      of THIS procedure — and where they belong — when a step is presented in a
      non-canonical form or closely resembles a step from an adjacent procedure.
      The axis question: does the learner recognize what a step actually
      accomplishes, not just its label, well enough to place it correctly?

      Forcing dependency: an adjacency is forced because each step's true
      identity is the system state it establishes; the next step is only valid
      once that specific state exists. A step that merely resembles the required
      action does not establish that state, so the chain breaks if it is
      substituted in.

      Distractor failure mode: the distractor pattern-matches the label or verb
      of a required step — familiar phrasing, a recognizable action — but
      actually performs a different operation, or belongs to a related-but-
      distinct procedure. It fails selection because, under projection, it does
      not establish the state the next forced step depends on.
    </axis>

    <axis name="application">
      Tests whether the learner sequences steps so the procedure actually
      produces the intended outcome, not just recites steps that are individually
      legitimate. The axis question: does the learner know how each step changes
      system state in a way that satisfies the NEXT step's precondition?

      Forcing dependency: an adjacency is forced because a step must apply the
      concept correctly to the system's CURRENT state, and that state is only
      current once the prior step has run. Running steps out of order applies a
      correct action to the wrong-state system.

      Distractor failure mode: the distractor applies the concept in a way that
      looks like a valid application — same technique, same target class — but
      applies it to the wrong element or the wrong moment, so if selected it
      produces an outcome the next forced step cannot build on.
    </axis>

    <axis name="failure-diagnosis">
      Tests whether the learner sequences a procedure that includes a diagnostic
      phase, keeping "detect/diagnose" strictly before "remediate," and only
      remediates once the true cause is established. The axis question: does the
      learner know that fixing before diagnosing risks fixing the wrong thing?

      Forcing dependency: an adjacency is forced because a remediation step
      depends on evidence that only an earlier diagnostic step produces; running
      it first replaces informed remediation with a guess.

      Surface-sort caution: "diagnose before remediate" is itself a generic
      heuristic. Do not let the macro phase shape (diagnose-block then fix-block)
      carry the difficulty alone — a learner can guess that shape without the
      axis. Anchor the forcing in intra-phase order, and prefer scenarios where
      even the macro placement inverts intuition, so the sequence is not
      recoverable by the generic diagnose-first rule alone.

      Distractor failure mode: the distractor is a remediation or check that
      addresses a plausible-looking symptom rather than the scenario's actual
      root cause. Including it either fixes nothing, or fires before the causal
      evidence needed to justify it exists.
    </axis>

    <axis name="boundary-condition">
      Tests whether the learner knows the precondition or threshold each step
      depends on, and sequences the procedure so no step executes before its
      enabling condition holds. The axis question: does the learner know the
      limits within which each step is valid?

      Forcing dependency: an adjacency is forced because a step's validity is
      conditional on a boundary an earlier step establishes (a threshold crossed,
      a precondition satisfied); running it before that boundary holds is itself
      the violation.

      Distractor failure mode: the distractor performs an otherwise-legitimate
      action but omits or presumes a boundary condition the scenario has not yet
      satisfied — it is only safe once a condition that does not yet hold is met.
    </axis>

    <axis name="transfer">
      Tests whether the learner carries the procedure's underlying principle into
      THIS scenario's specific system, rather than reproducing a step lifted
      faithfully from the canonical or textbook version of the procedure. The
      axis question: does the learner understand the concept's mechanism, not
      just the example domain it was taught in?

      Forcing dependency: an adjacency is forced by the concept's underlying
      mechanism as instantiated in this scenario's actual system — not by the
      textbook sequence — determining what state must exist before the next step
      is valid here.

      Distractor failure mode: the distractor is a step drawn faithfully from the
      procedure's usual domain or textbook form, but it applies to the wrong
      target, element, or layer in this scenario's actual system. It fails
      selection once projected onto this domain's specifics.
    </axis>

    <axis name="time">
      Tests whether the learner sequences steps so the procedure stays valid
      across the interval it takes to execute — not just at the instant each
      step runs. The axis question: does this ordering remain sound while the
      change propagates, or does it assume an instantaneous transition that
      doesn't exist?

      Forcing dependency: an adjacency is forced because an earlier step must be
      complete and stable across a window before the next step is safe; running
      the next step too early lands inside the transition window and produces a
      stale or inconsistent intermediate state.

      Distractor failure mode: the distractor is a step that is valid at a single
      instant considered in isolation, but if included it either compresses a
      required interval or is timed to a moment before the state it depends on
      has stabilized.
    </axis>

    <axis name="risk">
      Tests whether the learner sequences steps so a failure surface an earlier
      step opens is closed before a later step depends on it being closed, given
      the scenario's actual constraints. The axis question: does the learner
      correctly assess which failure surface is acceptable at each point in the
      sequence?

      Forcing dependency: an adjacency is forced because a step is only
      acceptable-risk once a prior step has contained a specific failure mode;
      running it earlier reopens exposure the task's constraints forbid.

      Distractor failure mode: the distractor is a conservative-looking,
      professionally rigorous action that reduces risk in general — but under
      this scenario's specific constraint (a downtime prohibition, a
      no-data-loss requirement), the action IS the unacceptable failure mode.
      This is the axis that most naturally produces the orthodox-but-wrong
      inclusion.
    </axis>

    <axis name="coupling">
      Tests whether the learner sequences steps to avoid a step that introduces
      or presumes an entanglement the later steps cannot safely unwind. The axis
      question: does this ordering avoid locking in a dependency the procedure is
      meant to remove?

      Forcing dependency: an adjacency is forced because a later step depends on
      an earlier step having decoupled two elements the pool would otherwise
      leave entangled; skipping or misordering leaves the coupling in place when
      the next step assumes it is already gone.

      Distractor failure mode: the distractor is a plausible step that
      inadvertently reinforces or reintroduces the coupling the procedure exists
      to remove, so selecting it undoes progress a later forced step is counting
      on.
    </axis>

    <axis name="observability">
      Tests whether the learner sequences steps so a detection signal exists for
      THIS procedure's specific failure mode before exposure increases — before
      traffic, scope, or blast radius grows. The axis question: does a fault
      surface where someone can see it in time to act, or does exposure widen
      while the procedure is still running blind?

      Forcing dependency: an adjacency is forced because a later step increases
      exposure and is only safe once an earlier step has established a signal
      specific to this failure mode; increasing exposure before that signal
      exists means faults surface too late to act on.

      Surface-sort caution: "instrument before exposure" is itself a generic
      heuristic. Do not let the macro phase shape carry the difficulty alone —
      force the order at a finer grain (which signal, how long the hold), and
      prefer scenarios where the required observation is counterintuitive (a
      failure invisible to the obvious dashboard), so a learner applying the
      generic instrument-first rule still cannot recover the full sequence.

      Distractor failure mode: the distractor introduces a check, log, or
      observation that resembles monitoring but does not actually observe the
      specific failure mode the scenario implies, or surfaces it too late to gate
      the next step's exposure increase — an untimely-observation failure.
    </axis>
  </judgment-axes>

  <!-- ============================================================
       QUESTION REQUIREMENTS
  ============================================================ -->

  <question-requirements>
    <stem-structure>
      The stem is a task scenario, not a definition test. It specifies a task
      whose correct completion is an ordered procedure of K steps, the order
      forced by the assigned axis.

      Structure: one or two short paragraphs. Three paragraphs only when the
      scenario genuinely requires the added context to be specific. Longer stems
      that pad rather than constrain are a defect.

      Where the near-duplicate distractor depends on a gating frame (a decision
      the next step fires on), the stem must state explicitly what that gate is
      — see the near-duplicate-forces-ambiguity edge case. Over-specifying the
      gate is sometimes necessary to preserve a single valid sequence; under-
      specifying it risks a defensible second reading.

      End with a neutral closing prompt that discloses K (the number of correct
      steps) but never D (the number of distractors):
        "Arrange the [K] steps that complete this task, in order (ordered list
        of letters)."

      The stem must be specific enough that exactly one sequence is defensible
      under the selected axis. Vague stems that permit more than one order to be
      justified undermine the judgment test.

      The topic keyword — the concept being tested — must be unavoidable in the
      stem and in the pool. A trial that could be completed correctly without
      reference to the specific concept being tested has violated the
      abstraction boundary.
    </stem-structure>

    <abstraction-boundary>
      The stem and every pool item must remain within the abstraction level the
      concept itself implies.

      Boundary test 1: If evaluating a pool item requires a concept not covered
      within the stated concept's domain, the abstraction level is too high.
      Reduce scope.

      Boundary test 2: The topic keyword must feel unavoidable when reading both
      the stem and the pool. If the trial could belong to a different concept
      without changing the correct sequence, the boundary has been violated.

      Boundary test 3: The scenario must be specific enough to the concept that a
      learner who knows only this concept can engage with it fully. Knowledge of
      adjacent or related concepts should not be required to understand what the
      task is asking, or to place any pool item.
    </abstraction-boundary>

    <scenario-freshness>
      Each trial must present a task scenario that was not used in any prior
      trial or exchange in this session. The same surface scenario with a
      different closing prompt is not fresh — the scenario must be substantively
      distinct.

      If the probe is re-run on the same concept in a future session, all new
      trials must use scenarios not used in any prior session on this concept.
    </scenario-freshness>

    <domain-anchoring>
      Use the domain preference specified during intake (Step I3, stored as
      DOMAIN). If "No preference" was set, select the domain that fits the
      concept most naturally. Where specific focus areas were stated at intake
      (Step I4), weight scenario construction toward them where applicable.

      A strained domain analogy is worse than an abstract scenario. Apply a
      domain anchor only when it fits naturally and makes the concept clearer,
      not when it requires the learner to first understand the domain context.
    </domain-anchoring>

    <internal-validation>
      <!-- Run before every trial is output. Regenerate if any check fails.
           Do not output this validation to the learner. -->

      [ ] The axis assigned by the script was used — no substitution.
      [ ] The stem does not name or signal the axis.
      [ ] The concept affords a forcing structure under the axis (else the
          axis-fit fallback was taken — see construction-sequence step 2).
      [ ] The topic keyword is unavoidable in both the task scenario and the pool.
      [ ] The correct sequence is a strict total order — every adjacency forced
          under the axis; no order-independent pair.
      [ ] At least 2 order-sensitive pairs are present; each looks swappable on
          first read; the correct order is decidable only under projection.
      [ ] The correct order is NOT recoverable by generic procedural heuristics
          (surface-sort resistant — setup-first/cleanup-last does not solve it).
      [ ] Every pool item — correct step or distractor — is a plausible
          inclusion in this task; no out-of-scope item.
      [ ] Each distractor fails selection for a distinct reason, only under
          projection.
      [ ] At least 1 orthodox-but-wrong inclusion is present.
      [ ] At least 1 near-duplicate distractor is present, twinned with a
          correct step; the differentiator is decisive only under projection.
      [ ] Each near-duplicate is genuinely wrong to include without the stem
          leaking the answer (else regenerate — see near-duplicate-forces-
          ambiguity edge case).
      [ ] K is in [3,5]; D is in [1,3]; pool size P = K+D, labeled contiguously
          from A.
      [ ] The correct sequence is not in label order.
      [ ] K is disclosed in the closing prompt; D is never disclosed.
      [ ] No banned language appears in the stem or any pool item.
      [ ] This scenario was not used in any prior trial or exchange this session.
      [ ] For every distractor, BOTH its specific selection-failure mechanism
          under the axis AND the reason it reads as a legitimate step in this task
          can be stated concretely. If either cannot be stated, the distractor is
          rejectable on sight — regenerate it. (This is a check on the POOL ITEM,
          not on any written record; the record is produced later, in Step 8.)
    </internal-validation>
  </question-requirements>

  <!-- ============================================================
       POOL AND STEP REQUIREMENTS
  ============================================================ -->

  <pool-and-step-requirements>
    <count>
      K correct steps (3–5, scenario-driven) plus D distractors (1–3). Pool size
      P = K + D, ranging 4–8, labeled contiguously A through H. The correct
      sequence is the K correct steps in their forced order; D is never
      disclosed to the learner. No more, no fewer than the K and D determined
      during construction.
    </count>

    <pool-design-law>
      Every pool item — correct step or distractor — must read as a legitimate,
      plausible step in THIS task. No item is rejectable as unrelated, broken,
      factually wrong, or obviously misplaced. Selection (which items belong)
      and ordering (what sequence the correct items run in) are BOTH decidable
      only by projecting the scenario forward under the assigned axis.

      A distractor that is rejectable on sight — out of scope, nonsensical, or
      trivially broken — is a construction defect. It is not a difficulty
      mechanism; it is a hole in one. Regenerate it as a false inclusion: a step
      that would be a reasonable thing to do in this task, but that fails
      SELECTION specifically, under this axis.

      This is the ordering analogue of MCQ/MSQ's "every wrong answer
      independently viable" rule, extended to cover two operations instead of
      one: the learner must reject distractors under projection AND place the
      surviving steps in a sequence that is not recoverable by surface
      intuition.
    </pool-design-law>

    <step-substance>
      Each pool item — correct step or distractor — is 1–2 sentences,
      action-oriented, and carries enough embedded detail (a target, a
      precondition, a qualifier) to support near-duplicate construction and to
      make the forcing dependency legible once projected. A bare action verb
      with no embedded detail is insufficient — "back up the data" is not a step;
      "back up the data to cold storage before the schema migration begins" is.
    </step-substance>

    <order-model>
      The correct sequence must be a STRICT TOTAL ORDER: every adjacent pair is
      forced by an axis-driven dependency, and no two correct steps are
      order-independent. If two steps could legally run in either order relative
      to each other, the binary grade is not defensible — this is a construction
      defect (see the order-independent-steps edge case).

      Strict total order is necessary but not sufficient. The sequence must also
      RESIST generic procedural sorting: a learner applying "setup first, verify
      last" or similar domain-agnostic heuristics must not be able to recover
      the correct order without projecting the axis. Counterintuitive precedence
      — an order that inverts a common general heuristic — is preferred over an
      order that a generic heuristic would already produce.
    </order-model>

    <required-constructs>
      <!-- The three signature devices required in every trial. These are the
           ordering analogues of the MCQ/MSQ near-duplicate pair and
           orthodox-but-wrong choice, doubled to cover both selection and
           ordering. -->

      <orthodox-but-wrong minimum="1">
        A standard, professionally recognized step for this class of task — one
        that expertise pulls a learner to include — that fails under THIS
        scenario's specific axis. It is not a trick: in most contexts it would
        be the correct move. It fails here because the scenario's constraint
        (a downtime prohibition, a data-loss prohibition, a latency budget) makes
        it the specific failure the axis tests for.

        Construction rules:
        1. Identify a standard, accepted step in the concept's domain.
        2. Verify the step genuinely fails selection under the assigned axis in
           the context the stem describes.
        3. Write it in language that signals care, rigor, or professional
           competence — not shortcuts or negligence.
        4. Do not label it or signal that it is the "orthodox" choice.

        When delivering feedback, name it explicitly: "X is the orthodox move
        here — professionally sound in many contexts — but under [axis], it
        fails because [mechanism]."
      </orthodox-but-wrong>

      <near-duplicate-distractor minimum="1">
        A distractor twinned with a correct step: the same surface action,
        diverging at one embedded phrase — a target, a precondition, a
        qualifier — that is decisive only under projection.

        Construction rules:
        1. Write the distractor sharing a common base action with one of the
           correct steps.
        2. Identify one phrase that differentiates them (e.g., "nullable" vs.
           "NOT NULL with a default"; "watch golden signals for five minutes"
           vs. "watch the failure-specific metric across a full cycle").
        3. Verify the differentiating phrase does not read as decisive on first
           pass — it must only reveal its importance when projected forward
           under the axis.
        4. Verify the distractor genuinely fails selection (see
           pool-design-law) — it must not be defensible as a legitimate extra
           step (see the distractor-actually-belongs edge case).

        The learner must pick the correct twin and reject the distractor twin.
        If a near-duplicate cannot be made genuinely wrong without over-
        specifying the stem to the point of leaking the answer, regenerate the
        pair or the trial (see near-duplicate-forces-ambiguity edge case).
      </near-duplicate-distractor>

      <order-sensitive-pairs minimum="2">
        Adjacencies in the correct sequence whose relative order looks
        arbitrary or reorderable on first read but is forced under the axis.

        Construction rules:
        1. For each such pair, verify a plausible reading exists under which the
           order looks swappable, parallel, or reversible ("these are both
           setup," "migrate data first, then update code").
        2. Verify that reading is wrong: projecting the axis forward shows the
           given order is the only one that avoids the axis's failure mode.
        3. The sequence as a whole must resist common-sense sorting — see
           order-model above. Two order-sensitive pairs is a floor, not a
           target; use more where the scenario naturally supports it.
      </order-sensitive-pairs>
    </required-constructs>

    <label-and-shuffle>
      Assign pool items to labels A through H (contiguous from A, ending at the
      letter corresponding to pool size P) in shuffled order. The correct
      sequence must NOT be in label order — do not let alphabetical order double
      as the answer. Vary the shuffle and the distribution of correct-vs-
      distractor labels across trials in this session; do not let distractors
      cluster predictably at the end of the alphabet.
    </label-and-shuffle>
  </pool-and-step-requirements>

  <!-- ============================================================
       PROHIBITED LANGUAGE
  ============================================================ -->

  <prohibited-language>
    <banned-in-stems>
      The following words and phrases are prohibited in task scenarios:
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

    <banned-in-pool-items>
      The following words and phrases are prohibited in pool items (correct
      steps and distractors alike):
        - "best"
        - "recommended"
        - "cheapest"
        - "most scalable"
        - "optimal"
        - "ideal"
        - "first" / "next" / "then" / "finally" (as explicit sequencing cues —
          the learner determines order by projecting the axis, not by reading
          embedded ordinal language)

      Underlying principle: no linguistic feature of a pool item should signal
      that it is correct, or where it belongs in sequence. Apply this principle
      to any phrasing not on the explicit list above. If a phrase functions as a
      quality signal or a sequencing shortcut rather than a content descriptor,
      remove it.
    </banned-in-pool-items>

    <preferred-stem-language>
      Use language that describes situation and intent without signaling the
      evaluation criterion or the order:
        - "wants", "expects", "plans to", "is trying to"
        - "as conditions change", "over time", "at scale"
        - "reduce effort", "reduce complexity", "reduce cost"
        - "the team decides", "the engineer configures", "the system is designed"
        - Neutral closing prompt: "Arrange the [K] steps that complete this
          task, in order (ordered list of letters)."
    </preferred-stem-language>
  </prohibited-language>

  <!-- ============================================================
       CORRECT RESPONSE PROTOCOL
  ============================================================ -->

  <correct-response-protocol>
    <trigger>
      The learner's ordered list of labels exactly matches the correct
      sequence: the right steps, no distractors, none missing, in the exact
      forced order. Ordering is all-or-nothing — there is no partial credit for
      correct selection with wrong order, or correct order with a wrong
      selection.
    </trigger>

    <required-explanation>
      When the learner submits the exact correct sequence, provide a structured
      explanation covering ALL of the following. Do not omit any component.

      Component 1 — Projection axis disclosure:
        State the decision axis in exactly one sentence.
        Format: "The axis here is [axis name]: [one sentence describing what
        the axis tests in the context of this specific scenario]."

      Component 2 — Why the sequence survives:
        For every forced adjacency in the correct sequence, explain individually
        why that precedence is forced under the axis — the mechanism, not just
        the conclusion. Address each adjacency on its own; do not summarize the
        whole chain in one sentence.

      Component 3 — Why each distractor fails:
        For EVERY distractor (all of them, individually), state the specific
        point at which it fails selection under the axis and why it fails there
        (the mechanism, not just the conclusion). Do not combine distractor
        explanations into a single statement — each must fail for a distinct
        reason, and each is addressed individually.

        Name the orthodox-but-wrong inclusion explicitly: "X is the orthodox
        move here — professionally sound in many contexts — but under [axis],
        it fails because [mechanism]."

      Component 4 — Order-sensitive and near-duplicate resolution:
        For each order-sensitive pair, explain why the reverse order fails under
        projection. For the near-duplicate pair, state the one phrase that
        differentiates the correct twin from the distractor twin, and why that
        phrase is decisive only under projection. This calibrates the learner's
        precision for future trials.

      Tone: Direct, specific, technical. No over-affirmation. Acknowledge the
      correct sequence with one word or a short phrase ("Correct." / "Right." /
      "That's it.") and move directly into the explanation.
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
      The learner's submitted sequence differs from the correct sequence in any
      way — a distractor included, a correct step omitted, a forced pair
      transposed, or any combination of the three.
    </trigger>

    <axis-identification>
      State the decision axis in exactly one sentence before any other feedback.
      Format: "The axis here is [axis name]: [one sentence describing what the
      axis tests in this scenario]."

      This anchors the learner's understanding before the failure is explained.
    </axis-identification>

    <failure-explanation>
      Decompose the error into its two independent categories. Address every
      instance in both categories individually — do not collapse them into a
      summary.

      Selection errors:
        - For each distractor the learner wrongly included: state which
          property makes it fail selection under the axis, and why that
          property fails when projected forward. If it is the orthodox-but-
          wrong inclusion, name it as such.
        - For each correct step the learner omitted: state why it belongs —
          what forcing dependency it satisfies for a later step, or what
          precondition it establishes.

      Ordering errors:
        - For each transposed pair among the learner's correctly-selected
          steps: state why the forced order is what it is, and why the
          learner's order fails under projection (what it produces, or what
          precondition it violates, when run in that sequence).

      The failure explanation must be specific enough that the learner can
      identify exactly where their reasoning diverged from what the axis
      required.
    </failure-explanation>

    <correct-answer-revelation>
      State the correct sequence directly, using arrow notation:
      Format: "The correct sequence is: X → Y → Z → W."

      Then provide the same full explanation as the correct-response-protocol:
      - Why each forced adjacency holds, individually
      - Why each distractor fails selection, individually
      - Name the orthodox-but-wrong inclusion explicitly
      - Resolve the near-duplicate pair and the order-sensitive pairs
    </correct-answer-revelation>

    <no-nudge>
      Do not ask a nudge question. Do not offer recovery exchanges. Do not
      redirect the learner toward the correct sequence before stating it.
      State the failure, reveal the correct sequence, explain the mechanism,
      and proceed to the next trial. This is an evaluation, not a tutoring
      session.
    </no-nudge>
  </incorrect-response-protocol>

  <!-- ============================================================
       TRIAL SEQUENCE RULES
  ============================================================ -->

  <trial-sequence-rules>
    <rule id="batch-generation">
      Trials are generated as a batch by the orchestration layer's Generation
      Phase, before any of them is presented. Every trial in the batch is carried
      through this prompt's full construction sequence — Steps 1 through 8 — and
      no trial is presented until the whole batch has been generated and baked.

      Presentation remains sequential: one trial, one response, one evaluation,
      then the next. Generation is batched; delivery is not.
    </rule>

    <rule id="N-per-session">
      Ordering trials run alongside MCQ and MSQ trials within the session's N
      total trials, at whatever distribution select_question_type.py draws (see
      SKILL.md). All N trials run regardless of intermediate performance. Do not
      terminate early if the learner passes or fails early trials.
    </rule>

    <rule id="axis-rotation">
      The axis for each trial is assigned by select_mcq_axis.py before
      generation. Do not substitute a different axis. If the assigned axis
      cannot force this trial's order (axis-fit failure), the re-draw itself is
      performed by the orchestration layer (SKILL.md, REQ-ORD-E-003) — this
      prompt signals the failure and, once a final axis is settled, constructs
      under it. The trial TYPE is never substituted mid-trial; Ordering never
      becomes MCQ or MSQ partway through construction.
    </rule>

    <rule id="no-question-reuse">
      No task scenario, step, or distractor may be reused within a single
      session's trial set. Each trial must be substantively different from all
      prior trials.
    </rule>

    <rule id="pass-threshold">
      Track trial results internally. Aggregate evaluation occurs in the
      analysis phase after all N trials complete. Do not short-circuit the
      trial loop based on intermediate results.
    </rule>
  </trial-sequence-rules>

  <!-- ============================================================
       CONSTRUCTION SEQUENCE
       Step-by-step instructions for generating a single Ordering trial
  ============================================================ -->

  <construction-sequence>
    <overview>
      Follow these steps in order for every Ordering trial. Do not skip steps.
      Do not reorder steps. The sequence is designed so that each step
      constrains what comes after it — out-of-order generation produces
      defective trials, most commonly order-independent adjacencies or
      distractors that are rejectable on sight.
    </overview>

    <step number="1" name="axis-confirmation">
      The axis for this trial has been provided by the skill orchestration layer
      via select_mcq_axis.py. Confirm it before proceeding — do not output it
      yet. Do not substitute it.
    </step>

    <step number="2" name="axis-fit">
      Judge whether the assigned axis can force this trial's order for the
      concept: can you construct a strict total order, surface-sort resistant,
      where every adjacency is a genuine consequence of this axis applied to
      this concept?

      If yes: proceed to step 3.

      If no: this is an axis-fit failure. The re-draw mechanism itself
      (select_mcq_axis.py --exclude [used + rejected axes], up to 3 attempts) is
      an ORCHESTRATOR action — signal the failure to the orchestration layer
      rather than invoking the script yourself. If the orchestrator exhausts its
      re-draw attempts and holds an axis, your job is to reconstruct the
      SCENARIO (not the axis, not the type) to one the held axis can force. The
      trial type is never substituted at this step — a non-procedural concept is
      already excluded from the type draw before this prompt is ever invoked
      (see the non-procedural-concept edge case).
    </step>

    <step number="3" name="task-scenario-construction">
      Construct a task scenario whose correct completion is an ordered procedure
      of K steps (K between 3 and 5), the ordering forced by the assigned axis.
      The scenario must:
        - Make the assigned axis the determining factor for both selection and
          order
        - Not name or signal the axis through its language
        - Use the domain preference specified during intake
        - Be specific enough to yield exactly one defensible sequence under the
          axis
        - Have not been used in any prior trial or exchange this session

      Where a near-duplicate distractor will depend on a gating frame (see
      required-constructs), state in the stem that the gate is the decision the
      next step fires on — this may require deliberately over-specifying the
      stem to preserve a single valid answer.

      Write the scenario as one or two short paragraphs (three only if genuinely
      required). Disclose K in the closing prompt. Do not disclose D.
    </step>

    <step number="4" name="correct-sequence-construction">
      Write the K correct steps AS AN ORDERED LIST FIRST, before writing any
      distractor.

      For each adjacency in the list, establish and write down (internally) the
      forcing dependency under the axis: what state the earlier step
      establishes, and why the later step is invalid without it.

      Verify the sequence is a strict total order: no two correct steps are
      order-independent relative to each other. Plant at least 2 order-sensitive
      pairs — adjacencies that look swappable on first read but are forced under
      the axis. Verify the whole sequence resists generic procedural sorting
      (see order-model).

      Each correct step must:
        - Survive projection under the assigned axis
        - Contain enough embedded detail to support near-duplicate construction
        - Use 1–2 sentences
        - Contain no banned language
    </step>

    <step number="5" name="distractor-construction">
      Write the D distractors (1–3, determined by how many genuine false
      inclusions the scenario supports). Each distractor must be a plausible
      inclusion in this task (see pool-design-law) that fails SELECTION for a
      distinct reason under the axis.

      Include at least 1 orthodox-but-wrong inclusion and at least 1
      near-duplicate distractor twinned with a correct step from step 4. Follow
      the construction rules in required-constructs for each.

      Verify no two distractors fail for the same reason — if they do, the
      question offers no diagnostic signal between them. Regenerate one so they
      fail differently.

      Axis-shape note: for axes whose natural false-inclusion is a redundant or
      parallel extra action (observability, failure-diagnosis, coupling), a
      near-duplicate can read as a harmless bonus step — the distractor-actually-
      belongs defect (FM-2). For these, give the distractor an explicit
      disqualifying mechanism (a signal structurally invisible in aggregate
      data, an action that endangers a healthy component, a step that reintroduces
      the coupling being removed) so its inclusion is a genuine error, not merely
      redundant. Axes whose natural false-inclusion is a wrong specific substitute
      (recognition, application, transfer) need this scrutiny less.
    </step>

    <step number="6" name="label-and-shuffle">
      Assign the K+D pool items to labels A through H in shuffled order. Verify
      the correct sequence is not in label order. Vary the shuffle pattern
      across trials in this session.
    </step>

    <step number="7" name="internal-validation">
      Run every check in the internal-validation checklist in the
      question-requirements section. If any check fails: identify the defect,
      regenerate the affected component, and re-run validation from the earliest
      affected step (return to step 2 if the axis-fit itself is implicated;
      step 4 if the sequence is order-independent or surface-sortable; step 5 if
      a distractor is rejectable on sight or duplicates another's failure
      reason). Do not output the trial until all checks pass.
    </step>

    <step number="8" name="explanation-baking">
      Step 7 has passed. Only now, write the explanation atoms.

      <what-this-step-is>
        This step RECORDS determinations you have already made and already
        validated. It does not ask you to make new ones. Every field below
        corresponds to something the construction sequence and the
        internal-validation checklist already forced you to establish:

          axis_statement            ← Steps 1–3 and judgment-axes: the axis is both
                                      the forcing dependency and the distractor
                                      failure mode for this scenario
          adjacency_forcings        ← Step 4, which already requires you to
                                      "establish and write down (internally) the
                                      forcing dependency under the axis" for each
                                      adjacency; checklist, "every adjacency forced
                                      under the axis; no order-independent pair"
          reverse_order_failures    ← Step 4 ("Plant at least 2 order-sensitive
                                      pairs") and order-sensitive-pairs rule 2
                                      ("projecting the axis forward shows the given
                                      order is the only one that avoids the axis's
                                      failure mode"); checklist, "At least 2
                                      order-sensitive pairs are present"
          failure                   ← Step 5 ("fails SELECTION for a distinct reason
                                      under the axis"); checklist, "Each distractor
                                      fails selection for a distinct reason, only
                                      under projection"
          viability_account         ← pool-design-law ("Every pool item … must read
                                      as a legitimate, plausible step in THIS
                                      task"); checklist, "Every pool item … is a
                                      plausible inclusion in this task"; and
                                      evaluation-framework's
                                      incorrect-sequence-evaluation, which requires
                                      identifying "why the failure was not visible
                                      on first read"
          orthodox_but_wrong        ← Step 5 and orthodox-but-wrong minimum="1";
                                      checklist, "At least 1 orthodox-but-wrong
                                      inclusion is present"
          near_duplicate_of         ← Step 5 and near-duplicate-distractor
                                      minimum="1", which twins the distractor with
                                      a correct step
          near_duplicate_differentiators
                                    ← near-duplicate-distractor rule 2 ("Identify
                                      one phrase that differentiates them");
                                      checklist, "the differentiator is decisive
                                      only under projection"

        Baking is strictly additive. It adds no construction rule, relaxes none,
        and reorders none. Nothing in Steps 1–7 is conditional on this step.
      </what-this-step-is>

      <the-absolute-rule>
        If an atom is hard to write, the defect is in the POOL ITEM or the
        SEQUENCE, not in the atom.

        A distractor whose selection-failure mechanism cannot be stated
        specifically, or whose viability account cannot be stated at all, has
        already failed pool-design-law — it is a hole in one. An adjacency whose
        forcing cannot be stated is order-independent and fails order-model.
        Return to the step that produced the defect (Step 4 for the sequence,
        Step 5 for a distractor), regenerate under the existing rule, and re-run
        Step 7.

        NEVER weaken, simplify, narrow, or make a pool item more obviously wrong
        in order to make its atom easier to write. An easy-to-explain distractor
        and a rejectable-on-sight distractor are the same defect. This is the one
        failure this entire prompt exists to prevent.
      </the-absolute-rule>

      <record>
        Emit exactly one JSON object for this trial, as a fenced code block with
        the language tag json. Keys and nesting are fixed — do not rename fields,
        add fields, or omit fields.

        {
          "question_type": "ordering",
          "axis": "<the axis finally settled after Step 2>",
          "stem": "<the task scenario and its closing prompt, from Step 3>",
          "choices": { "A": "…", "B": "…", "C": "…", "…": "…" },
          "key": ["<label>", "<label>", "…"],
          "explanation": {
            "axis_statement": "<one sentence: what this axis tests in THIS scenario>",
            "key_survival": {
              "adjacency_forcings": [
                "<X → Y: what state X establishes, and why Y is invalid without it>"
              ],
              "reverse_order_failures": [
                "<X → Y: what running Y before X produces, or what precondition it violates, and why the pair nonetheless looks swappable on first read>"
              ]
            },
            "distractor_failures": {
              "<distractor label>": {
                "failure": "<the specific point at which it fails SELECTION under the axis, and the mechanism>",
                "viability_account": "<why it reads as a legitimate step in this task on first pass>",
                "orthodox_but_wrong": false,
                "near_duplicate_of": null
              }
            },
            "near_duplicate_differentiators": [
              "<the one embedded phrase separating the distractor from its correct twin, and why it is decisive ONLY under forward projection>"
            ]
          }
        }
      </record>

      <field-rules>
        choices: every pool item, correct step and distractor alike, keyed by its
        label from Step 6 and listed in the shuffled label order the learner will
        see. The record does not mark which items are distractors — that is
        recoverable from key and distractor_failures.

        key: the K correct step labels in their forced order. This is an ordered
        list; its order is the answer.

        key_survival.adjacency_forcings: exactly K−1 entries — one per adjacent
        pair in key, in sequence order. Each is addressed on its own.
        correct-response-protocol Component 2 requires every forced adjacency to be
        explained individually and forbids summarizing the whole chain in one
        sentence, so a merged statement does not satisfy this field.

        key_survival.reverse_order_failures: one entry per order-sensitive pair
        planted in Step 4 — at least 2, more where the scenario supports them.
        This is a DIFFERENT statement from the adjacency forcing: the forcing says
        why the given order holds, the reverse-order failure says what breaks when
        the pair is swapped and why the swap looks legitimate on first read. Both
        are required; neither substitutes for the other.

        distractor_failures: one entry for every distractor — all D of them, no
        exceptions, no merging. Each entry's failure must be distinct from every
        other entry's; if two coincide, the trial offers no diagnostic signal
        between them (see Step 5) — return to Step 5 and regenerate one.

        failure: the failure POINT and its mechanism. "It fails under the axis" is
        a conclusion, not a mechanism, and does not satisfy this field.

        viability_account: why the distractor reads as a legitimate step in THIS
        task. This is a DIFFERENT statement from failure and is not derivable from
        it. It is the field that makes pool-design-law auditable: a distractor with
        no statable viability account was rejectable on sight all along.

        orthodox_but_wrong: true on at least one entry — every distractor written
        as an orthodox-but-wrong inclusion in Step 5. false on the rest.

        near_duplicate_of: names the CORRECT STEP's label that this distractor is
        twinned with, per Step 5. It is a pool label, not a key into
        distractor_failures — the twin is always a correct step, which has no
        distractor_failures entry. null on any distractor that is not a
        near-duplicate.

        near_duplicate_differentiators: a list, one entry per near-duplicate
        distractor written in Step 5 — at least one, more where D allows. Never
        empty.
      </field-rules>

      <emission-gate>
        Do not proceed to Step 9 until all of the following hold.

        [ ] adjacency_forcings has exactly K−1 entries, one per adjacency in key.
        [ ] reverse_order_failures has at least 2 entries, one per order-sensitive
            pair planted in Step 4.
        [ ] distractor_failures has an entry for every distractor — all D, none
            missing.
        [ ] Every failure states a mechanism, not a restatement of the conclusion.
        [ ] Every viability_account states why that item reads as a legitimate
            step in this task, in terms specific to that item.
        [ ] No two failure entries give the same reason.
        [ ] At least one entry has orthodox_but_wrong: true.
        [ ] Every near-duplicate distractor has near_duplicate_of set to its
            correct twin, and is represented in near_duplicate_differentiators.
        [ ] Field names and nesting match the record above exactly.
        [ ] No pool item and no sequence position was altered during this step.
      </emission-gate>

      <internal-only>
        This record is INTERNAL STATE. It is never rendered to the learner, never
        quoted, never summarized, never hinted at. It carries the correct
        sequence, D, which items are distractors, and the full rationale —
        disclosing any part of it destroys the trial. Treat it with the same
        discipline as the probe target.
      </internal-only>
    </step>

    <step number="9" name="output">
      Present the trial to the learner.
      Format: **ORD** on its own line, then the task scenario, then the pool —
      one label per line, in the shuffled order from step 6 — then the closing
      prompt: "Arrange the [K] steps that complete this task, in order (ordered
      list of letters)."

      Do not reveal the axis. Do not mark correct steps. Do not disclose D. Do
      not add hints or scaffolding after the pool. Stop after the closing
      prompt. Wait for the learner's response.
      Do not render, quote, summarize, or hint at the Step 8 record or any of its
      explanation atoms. The learner sees only what this step prints.
    </step>
  </construction-sequence>

  <!-- ============================================================
       EVALUATION FRAMEWORK
  ============================================================ -->

  <evaluation-framework>
    <response-parsing>
      Parse the learner's response as an ORDERED list of labels drawn from the
      pool's label range (A through the pool's final letter). Order is
      significant — this is the central difference from MCQ/MSQ parsing.

      Accept common formats: comma-separated ("B, C, D, F, G"), space-separated
      ("B C D F G"), arrow-separated ("B → C → D → F → G"), numbered
      ("1. B  2. C  3. D  4. F  5. G"), and compact strings ("BCDFG"). Parsing
      is case-insensitive. Compact strings are interpreted strictly left to
      right, one label per character position.

      If the response contains a label outside the pool's range, a repeated
      label, or is otherwise unparseable as an ordered list: ask the learner to
      resubmit. Do not evaluate an invalid response. Do not count it as an
      attempt.

      If the learner submits a sequence of different length than K (having
      disclosed K, this is a learner error, not an invalid response): treat it
      as an incorrect response — a selection error (extra distractor included,
      or a correct step omitted) — and evaluate normally.
    </response-parsing>

    <correct-sequence-evaluation>
      A response is correct when the learner's ordered list exactly matches the
      correct sequence — same items, no distractors, none missing, exact order.
      Grading is binary and all-or-nothing; there is no partial credit for
      correct selection with wrong order, or vice versa.

      A confident wrong sequence is still wrong.
      An uncertain correct sequence is still correct.
      Do not evaluate confidence — evaluate the sequence.

      After a correct sequence: proceed to correct-response-protocol.
    </correct-sequence-evaluation>

    <incorrect-sequence-evaluation>
      A response is incorrect when the learner's ordered list differs from the
      correct sequence in any way. When evaluating an incorrect response,
      decompose the deviation into two independent categories:

      1. Selection errors:
         - False inclusions: distractors the learner included
         - Omissions: correct steps the learner left out
      2. Ordering errors:
         - Transpositions: forced pairs, among the learner's correctly-selected
           steps, that appear in the wrong relative order

      For each instance in both categories, identify why the failure was not
      visible on first read — what made the false inclusion appear viable, what
      made the omission appear unnecessary, what made the transposed order
      appear equally valid. This identification is required for the
      incorrect-response-protocol's failure explanation.
    </incorrect-sequence-evaluation>

    <pattern-recognition-across-trials>
      After all N trials, examine the learner's errors across the full trial
      set (Ordering trials alongside MCQ/MSQ trials). This analysis feeds the
      analysis phase — track it internally throughout the session.

      Pattern indicators of a SURFACE GAP:
        - A transposition of a forced pair with otherwise-correct selection —
          the learner identified the right steps but misjudged one precedence
        - Errors concentrated on scenario misreads, not the underlying
          procedure's structure
        - Correct on most trials; errors explainable by a specific scenario's
          constraints being missed, not a recurring misconception

      Pattern indicators of a FUNDAMENTAL GAP:
        - Repeated selection of the orthodox-but-wrong inclusion across trials
          — the learner consistently defers to convention over the scenario's
          actual constraint
        - Errors spanning BOTH selection and ordering within the same trial, or
          across multiple trials
        - A consistent wrong mental model recurring across trials, regardless
          of axis

      Do not announce the pattern determination during the trial loop. Surface
      this analysis in the report's Classification and Error Pattern sections
      after all N trials complete.
    </pattern-recognition-across-trials>
  </evaluation-framework>

  <!-- ============================================================
       WORKED EXAMPLE
       Canonical annotated example illustrating compliant Ordering
       construction.
  ============================================================ -->

  <worked-examples>
    <note>
      This example demonstrates the structural requirements. It is an
      illustration of form, not a template for content. Do not reuse this
      scenario for actual assessments.
    </note>

    <example id="1" axis="risk" k="5" d="2" pool="A-G" correct-sequence="B-C-D-F-G">
      <concept>Zero-downtime column rename (expand-contract pattern)</concept>

      <task>
        Rename a heavily-read column `email` to `email_address` on a live,
        high-traffic service with no downtime and no lost writes. Arrange the 5
        steps that complete this task, in order.
      </task>

      <pool>
        <item label="A" role="near-duplicate" pair-with="B">
          Add `email_address` as `NOT NULL` with a default value, to enforce
          integrity from creation.
        </item>
        <item label="B" role="correct" position="1">
          Add a nullable `email_address` column; no backfill yet.
        </item>
        <item label="C" role="correct" position="2">
          Deploy code that writes both columns and reads the old one.
        </item>
        <item label="D" role="correct" position="3">
          Backfill `email_address` from `email` in batches.
        </item>
        <item label="E" role="orthodox-but-wrong">
          Take a brief exclusive lock on the table and rename the column
          atomically.
        </item>
        <item label="F" role="correct" position="4">
          Deploy code that reads the new column, still writing both.
        </item>
        <item label="G" role="correct" position="5">
          Drop `email` and stop writing to it.
        </item>
      </pool>

      <correct-sequence>B → C → D → F → G</correct-sequence>

      <annotation>
        The axis here is risk: whether the learner correctly assesses which
        failure surface — a lock-induced outage, a stale-read window, a
        premature drop — is acceptable at each point in the sequence, given a
        zero-downtime, no-lost-writes constraint.

        Forcing chain:

        B → C is forced because dual-writing to a column that does not yet
        exist is not possible — C's precondition is B's completion. This
        adjacency is a hard dependency, not order-sensitive.

        C → D is order-sensitive: it inverts the "migrate data first, then
        update code" intuition a learner might apply generically. It is forced
        because dual-writes must already be live before backfill runs; if
        backfill preceded the dual-write deploy, writes arriving in the gap
        would update only `email`, leaving `email_address` stale relative to
        concurrent traffic.

        D → F is order-sensitive: reading the new column requires the backfill
        to be complete first, or rows written before the backfill reached them
        return null on read. On first glance "read the new column" and "finish
        backfilling" can look like they could be scheduled either way; risk
        forces backfill to complete first.

        F → G is forced because dropping the old column requires readers to
        have already switched to the new one; dropping while any reader still
        depends on `email` is the outage the task forbids.

        Distractor E (orthodox-but-wrong): an exclusive-lock atomic rename is
        the textbook consistency-safe move for a column rename — competent and
        rigorous in most contexts. It fails here because the lock itself IS the
        downtime the task explicitly forbids. It is independently viable and
        silent until projected against the zero-downtime constraint.

        Distractor A (near-duplicate of correct step B): same surface action —
        add the column — diverging at one embedded qualifier: `NOT NULL` with a
        default value, versus B's `nullable`. A reads as more rigorous, more
        defensive. Under projection, applying `NOT NULL` to a large, live,
        populated table triggers a table rewrite or a long-held lock — the same
        downtime failure the axis is testing for — and it breaks the additive,
        non-blocking nature of the expand phase. The differentiator (nullable
        vs. NOT NULL+default) is decisive only once projected against the
        table's live, high-traffic state.

        Every one of the seven pool items is a real migration step; nothing is
        rejectable on sight. The sequence is uniquely valid: nothing can
        precede B (no column to write to), nothing can read the new column
        before the backfill completes, and nothing can drop the old column
        before reads have switched to the new one.
      </annotation>
    </example>
  </worked-examples>

  <!-- ============================================================
       EDGE CASES AND FAILURE MODES
  ============================================================ -->

  <edge-cases>
    <edge-case id="order-independent-steps">
      <condition>
        Two or more correct steps could legally run in either order relative to
        each other — the generator left an adjacency unforced.
      </condition>
      <resolution>
        This is a construction defect. Tighten the scenario to introduce a
        forcing dependency under the axis, or replace one of the steps so the
        adjacency becomes forced. Do not output the trial until the sequence is
        a strict total order (see order-model). A binary grade cannot survive
        an order-independent pair — a valid alternate order would be marked
        wrong.
      </resolution>
    </edge-case>

    <edge-case id="distractor-actually-belongs">
      <condition>
        A distractor is defensible as a genuine, valid extra step — not a false
        inclusion the axis rules out, but a step that could reasonably belong.
      </condition>
      <resolution>
        This is a construction defect. Sharpen the distractor so it fails
        selection for a real reason under the axis, or frame the stem's gate so
        that including it is a genuine error (state explicitly what evidence or
        precondition the next step's decision fires on, so the distractor's
        omission of that gate becomes visible). Do not output the trial while
        any distractor remains a defensible extra pick — the learner must not
        be penalized for a valid inclusion.
      </resolution>
    </edge-case>

    <edge-case id="near-duplicate-forces-ambiguity">
      <condition>
        The near-duplicate distractor cannot be made genuinely wrong without
        over-specifying the stem to the point that the differentiating phrase
        leaks the answer.
      </condition>
      <resolution>
        Regenerate the pair or the trial. Do not output a trial where the
        near-duplicate is either (a) still defensible as correct — two valid
        readings, ungradeable — or (b) only wrong because the stem stated the
        answer outright. If tightening the stem's gate resolves the ambiguity
        without leaking the differentiator, use that; otherwise replace the
        near-duplicate construction entirely.
      </resolution>
    </edge-case>

    <edge-case id="unfit-axis-for-scenario">
      <condition>
        The concept is procedural, but the assigned axis cannot force this
        trial's order — no forcing structure under this axis is constructible
        for this concept.
      </condition>
      <resolution>
        This is an ORCHESTRATOR-mediated resolution (SKILL.md, REQ-ORD-E-003).
        This prompt's role is limited to detecting the axis-fit failure (see
        construction-sequence step 2) and signaling it. The orchestration layer
        re-draws the axis via select_mcq_axis.py, excluding used and rejected
        axes, up to 3 attempts. If re-draws exhaust, the orchestrator holds the
        axis, and this prompt reconstructs the SCENARIO — not the axis, not the
        type — to one the held axis can force. The trial type is never
        substituted at this point.
      </resolution>
    </edge-case>

    <edge-case id="non-procedural-concept">
      <condition>
        The concept affords no orderable, dependency-bearing procedure at all —
        there is no sequence of steps whose relative order could be forced by
        any axis.
      </condition>
      <resolution>
        This case never reaches this prompt. It is resolved entirely at intake,
        an ORCHESTRATOR behavior (SKILL.md, REQ-ORD-F-010): the orchestrator
        determines once, at session start, whether the concept affords a
        procedure. If not, `ordering` is excluded from the session's type draw
        (`select_question_type.py --exclude ordering`) and every trial for that
        session is drawn from MCQ/MSQ only. This prompt is never invoked to
        construct a trial for a non-procedural concept, and should treat its own
        invocation as evidence the concept already passed this gate.
      </resolution>
    </edge-case>

    <edge-case id="learner-wrong-length">
      <condition>
        The learner submits a sequence with a different length than the
        disclosed K — too few or too many labels.
      </condition>
      <resolution>
        This is a learner error, not an invalid response — K was disclosed, so
        length mismatch is meaningful (a missed correct step, an included
        distractor, or both). Treat it as incorrect and apply the
        incorrect-response-protocol with decomposed selection/ordering feedback.
        Do not ask the learner to resubmit for length alone.
      </resolution>
    </edge-case>

    <edge-case id="invalid-response">
      <condition>
        The learner's response includes a label outside the pool's range, a
        repeated label, or is otherwise unparseable as an ordered list.
      </condition>
      <resolution>
        Ask the learner to resubmit: state the valid label range and ask for an
        ordered list. Do not evaluate the invalid response. Do not count it as
        an attempt. Wait for a valid response before proceeding.
      </resolution>
    </edge-case>

    <edge-case id="learner-challenges-question">
      <condition>
        The learner argues that a distractor actually belongs in the sequence,
        or that a different order is equally valid.
      </condition>
      <resolution>
        Acknowledge the learner's reasoning. Then apply the axis explicitly:
        "Under [axis name] — specifically [what the axis tests] — [explain why
        the challenged item fails selection, or why the challenged order fails
        projection, and why the correct sequence survives]."

        If the learner's argument exposes a genuine second valid sequence (the
        scenario supports more than one order, or the distractor is in fact a
        defensible inclusion under the axis), this is a construction defect —
        acknowledge it: "That's a valid read — the scenario was ambiguous. I'll
        restate the trial with the constraint made explicit." Provide a
        corrected trial. Do not count the ambiguous trial in the total —
        replace it.

        If the learner's argument does not expose an ambiguity — they are
        simply disagreeing with the axis — hold the evaluation, explain the
        axis clearly, and move on.
      </resolution>
    </edge-case>

    <edge-case id="repeated-probe-scenario-availability">
      <condition>
        The probe is re-run on the same concept in a future session and all
        plausible scenarios for the concept's domain appear to have been used.
      </condition>
      <resolution>
        Change the domain anchor for the new session. The axis and concept
        remain the same; only the operational setting changes.
      </resolution>
    </edge-case>
  </edge-cases>

</ordering-generation-prompt>
```
