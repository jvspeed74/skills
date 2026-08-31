```xml
<msq-generation-prompt>

  <!-- ============================================================
       LOADING INSTRUCTIONS
       Load this file ONCE at session start, before the first MSQ trial.
       Retain in context for all MSQ trials in this session.
       Do NOT reload before each trial.
       If this file cannot be read, halt and report the error.
       MSQ trials shall not be generated without this prompt.
  ============================================================ -->

  <purpose>
    This prompt governs the generation, structure, and evaluation of all MSQ
    (multiple-select question) trials used in mcq-probe assessments.

    An MSQ trial is not a knowledge quiz. It is a judgment probe. Its purpose is to
    distinguish a learner who understands how a concept operates under real conditions
    from a learner who has only absorbed a definition. Every answer choice must be
    independently defensible in isolation — a choice is not wrong because it is
    factually false or obviously broken. Wrong choices fail only when projected forward
    under the specific decision axis this question is built on.

    This prompt applies to all MSQ trials for any concept.
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
      through stem construction and answer evaluation.
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
      The axis is INTERNAL — do not state it in the question stem or in the
      answer choices. Do not signal the axis through question wording.

      The axis determines which answers survive. Wrong answers are not wrong
      because they are false — they are wrong because they fail when projected
      forward under the selected axis, even though they appear viable on first read.

      Apply the axis consistently through stem construction and answer evaluation.
      Do not switch axes mid-generation.
    </overview>

    <axis name="recognition">
      Tests whether the learner can identify a concept correctly when it appears
      in a non-canonical form, partial description, or edge-case presentation.
      The axis question: does the learner recognize the concept when it is not
      labeled or framed in the way it was taught?

      Survival test: correct answers accurately name, classify, or identify the
      concept given the scenario's conditions. Wrong answers pattern-match
      superficially to the scenario but mis-identify the concept, apply the wrong
      category, or conflate it with a related but distinct concept.
    </axis>

    <axis name="application">
      Tests whether the learner can correctly apply the concept to produce a valid
      outcome in a specific situation. The axis question: does the learner know
      what to do — not just what the concept is?

      Survival test: correct answers produce the intended outcome given the
      scenario's constraints. Wrong answers apply the concept incorrectly, apply
      it to the wrong part of the system, or produce a result that looks plausible
      but breaks under the scenario's actual requirements.
    </axis>

    <axis name="failure-diagnosis">
      Tests whether the learner can identify when and why a concept is being
      violated, misapplied, or absent — and trace the failure to its root cause.
      The axis question: does the learner recognize the failure mode in action?

      Survival test: correct answers correctly identify what is wrong and why.
      Wrong answers identify the wrong failure, identify the right failure but for
      the wrong reason, or identify a surface symptom without the root cause.
    </axis>

    <axis name="boundary-condition">
      Tests whether the learner understands where the concept's validity breaks
      down, what assumptions it depends on, and what happens when those assumptions
      are violated. The axis question: does the learner know the limits of the concept?

      Survival test: correct answers correctly identify the boundary condition and
      its consequence. Wrong answers treat the concept as having no limits, state
      the wrong boundary, or correctly identify the boundary but misstate what
      happens when it is crossed.
    </axis>

    <axis name="transfer">
      Tests whether the learner can carry the concept into a domain or context
      different from the one in which it was taught. The axis question: does
      the learner understand the concept at the level of principle, not just
      the specific example they learned it from?

      Survival test: correct answers apply the concept's underlying logic correctly
      in the new domain. Wrong answers apply surface features of the original
      domain example rather than the concept's actual mechanism, or apply the
      concept to the wrong element of the new domain.
    </axis>

    <axis name="time">
      Tests whether the learner can reason about how an approach degrades or
      creates maintenance burden as conditions evolve. The axis question: does
      this choice remain sound as the system or situation changes?

      Survival test: correct answers hold up under temporal projection. Wrong
      answers appear valid at t=0 but accumulate latent cost, brittleness, or
      maintenance overhead that makes them untenable as conditions shift.
    </axis>

    <axis name="risk">
      Tests whether the learner can identify failure modes that a particular
      approach introduces and whether those failure modes are acceptable given
      the scenario's constraints. The axis question: does the learner correctly
      assess the failure surface this choice creates?

      Survival test: correct answers either avoid the dangerous failure mode or
      correctly account for it. Wrong answers introduce unacceptable failure
      surfaces, underestimate the probability or consequence of failure, or apply
      a conservative-looking approach that is actually fragile under the specific
      failure class the scenario implies.
    </axis>

    <axis name="coupling">
      Tests whether the learner can identify when an approach creates dependencies
      that constrain or complicate future changes. The axis question: does this
      choice introduce structural entanglement that will compound over time?

      Survival test: correct answers avoid the coupling the scenario implies is
      problematic, or correctly characterize why the coupling exists and what it
      costs. Wrong answers introduce tight coupling that appears innocuous but
      constrains downstream flexibility in ways the scenario makes material.
    </axis>

    <axis name="observability">
      Tests whether the learner can assess if an approach's success or failure is
      detectable before consequences compound. The axis question: does a fault
      surface where someone can see it in time to act, or does it stay silent
      until damage has already occurred?

      Survival test: correct answers' failure modes are observable — they surface
      a signal, error, or symptom in time to act. Wrong answers fail silently (no
      signal until damage is done), rely on a check that does not actually observe
      the failure mode the scenario implies, or surface a signal so late or so
      buried that it does not support timely action.
    </axis>
  </judgment-axes>

  <!-- ============================================================
       QUESTION REQUIREMENTS
  ============================================================ -->

  <question-requirements>
    <stem-structure>
      The stem is a scenario, not a definition test. It should place the learner
      in a situation that requires judgment — a decision to make, a failure to
      diagnose, an outcome to predict, a context to assess.

      Structure: one or two short paragraphs. Three paragraphs only when the
      scenario genuinely requires the added context to be specific. Longer stems
      that pad rather than constrain are a defect.

      End with a neutral multi-select decision prompt that does not signal the
      axis. Append the correct answer count in parentheses: "(Select N.)"
      Examples of acceptable endings:
        "Which of the following apply in this scenario? (Select 2.)"
        "Which of the following hold under these conditions? (Select 3.)"
        "Which configurations are consistent with the requirements? (Select 2.)"
        "Which of the following does the engineer observe? (Select 1.)"
        "Which approaches are valid given these constraints? (Select 3.)"

      The stem must be specific enough that there is a defensible, bounded set
      of correct answers under the selected axis. Vague stems that permit
      arbitrary subsets of answers to be justified undermine the judgment test.

      The topic keyword — the concept being tested — must be unavoidable in the
      stem. A question that could be answered correctly without reference to the
      specific concept being tested has violated the abstraction boundary.
    </stem-structure>

    <abstraction-boundary>
      The stem and all answer choices must remain within the abstraction level
      the concept itself implies.

      Boundary test 1: If evaluating an answer choice requires a concept not
      covered within the stated concept's domain, the abstraction level is too
      high. Reduce scope.

      Boundary test 2: The topic keyword must feel unavoidable when reading both
      the stem and the answer choices. If the question could belong to a different
      concept without changing which answers are correct, the boundary has been violated.

      Boundary test 3: The scenario must be specific enough to the concept that a
      learner who knows only this concept can engage with it fully. Knowledge of
      adjacent or related concepts should not be required to understand what the
      question is asking.
    </abstraction-boundary>

    <scenario-freshness>
      Each trial must present a scenario that was not used in any prior trial or
      exchange in this session. The same surface scenario with a different question
      appended is not fresh — the scenario must be substantively distinct.

      If the probe is re-run on the same concept in a future session, all new
      trials must use scenarios not used in any prior session on this concept.
    </scenario-freshness>

    <domain-anchoring>
      Use the domain preference specified during intake. If "No preference" was
      set, select the domain that fits the concept most naturally.

      A strained domain analogy is worse than an abstract scenario. Apply a
      domain anchor only when it fits naturally and makes the concept clearer,
      not when it requires the learner to first understand the domain context.
    </domain-anchoring>

    <internal-validation>
      <!-- Run before every question is output. Regenerate if any check fails.
           Do not output this validation to the learner. -->

      [ ] The axis assigned by the script was used — no substitution.
      [ ] The stem does not name or signal the axis.
      [ ] The topic keyword is unavoidable in both the stem and answer choices.
      [ ] The stem ends with a neutral multi-select decision prompt with a count suffix
          (no banned language).
      [ ] All five answers are independently viable.
      [ ] All five answers contain multiple interacting elements appropriate to
          the topic.
      [ ] Wrong answers fail under projection — not due to factual error or
          impossibility.
      [ ] Correct answers only survive when evaluated forward under the selected axis.
      [ ] The correct answer count is between 1 and 4 inclusive.
      [ ] At least one orthodox-but-wrong answer is present.
      [ ] Answer choices are constructed with deliberate surface similarity where
          applicable — a learner relying on pattern-matching rather than projection
          cannot reliably identify the correct set.
      [ ] No banned language appears in the stem or any answer choice.
      [ ] This scenario was not used in any prior trial or exchange this session.
      [ ] For every wrong answer, BOTH its specific failure mechanism under the
          axis AND the reason it reads as correct on first pass can be stated
          concretely. If either cannot be stated, the choice is rejectable on
          surface reading — regenerate it. (This is a check on the CHOICE, not on
          any written record; the record is produced later, in Step 7.)
    </internal-validation>
  </question-requirements>

  <!-- ============================================================
       ANSWER CHOICE REQUIREMENTS
  ============================================================ -->

  <answer-choice-requirements>
    <count>Exactly 5 answer choices, labeled A, B, C, D, and E. No more, no fewer.</count>

    <correct-count>
      The number of correct answers is not fixed. It is determined by how many
      choices genuinely survive projection under the assigned axis given the
      scenario's constraints. Write as many correct answers as the scenario
      warrants. The count must be at least 1 and at most 4.

      Do not engineer the count toward a target. Let the axis and scenario determine
      it. A question with 1 correct answer is as valid as one with 3, provided the
      scenario makes the distinction defensible.
    </correct-count>

    <viability-requirement>
      All five answer choices must be independently viable. This means: if a learner
      reads any single answer choice in isolation, without the other four choices
      present, it should appear to be a plausible, reasonable approach or conclusion.

      Wrong answers fail under projection against the selected axis — not because
      they describe something impossible, factually false, or obviously broken.
      A wrong answer that is trivially wrong on first read is a defective answer
      choice. Regenerate it.
    </viability-requirement>

    <answer-substance>
      Each answer choice must be 1–3 sentences representing a coherent, complete
      approach or conclusion — not an isolated fact or a single rule.

      Each answer must include multiple interacting elements appropriate to the
      topic, describing how those elements work together under the implied
      constraint. A one-clause answer that names a technique without describing
      how it is applied is insufficient.
    </answer-substance>

    <similarity-construction>
      Construct answer choices with deliberate surface similarity. The degree of
      similarity — whether two choices share a common base, a cluster of three
      diverge at a single phrase, or all five are superficially close — is at your
      discretion based on what will make the question hardest to answer without
      genuine understanding.

      The goal is that a learner who has only absorbed a definition or surface
      pattern cannot distinguish correct from incorrect choices without projecting
      each choice forward under the assigned axis. Surface features that appear
      decisive on first read must not be the actual differentiator. The actual
      differentiator — the phrase, qualifier, sequencing detail, or target that
      separates correct from wrong — must only reveal its importance under forward
      projection.

      When multiple choices share structural similarity, verify that each wrong
      choice among them fails for a distinct reason. Two similar wrong choices that
      fail identically offer no diagnostic signal. Regenerate one so they fail
      differently.
    </similarity-construction>

    <orthodox-but-wrong>
      Include at least one orthodox-but-wrong answer: a choice that represents a
      widely accepted, professionally recognized, or textbook-standard approach
      that appears careful, thorough, or defensible in isolation — but that fails
      under the specific projection axis of this question.

      The number of orthodox-but-wrong answers is at your discretion. Include as
      many as the scenario warrants and the wrong-answer pool can support without
      reducing viability.

      The orthodox-but-wrong answer is not a trick. It is a genuine approach that
      would be correct in many contexts — it just does not survive projection in
      this specific scenario given this specific axis.

      Construction rules:
      1. Identify a standard, accepted approach in the concept's domain.
      2. Verify that this approach genuinely fails under the selected axis in the
         context the stem describes.
      3. Write it in language that signals care, rigor, or professional competence —
         not in language that signals shortcuts or negligence.
      4. Do not label it or signal that it is the "orthodox" choice.

      When delivering feedback, name each orthodox-but-wrong answer explicitly:
      "X is the orthodox approach here — professionally sound in many contexts —
      but under [axis], it fails because [mechanism]."
    </orthodox-but-wrong>

    <answer-position>
      Correct answers may appear in any positions (A through E). Do not
      systematically cluster correct answers at the top or bottom. Distribute
      their positions across trials and within questions where multiple are correct.
    </answer-position>
  </answer-choice-requirements>

  <!-- ============================================================
       PROHIBITED LANGUAGE
  ============================================================ -->

  <prohibited-language>
    <banned-in-stems>
      The following words and phrases are prohibited in question stems:
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

      These phrases allow test-taking heuristics to override actual understanding.
      Remove the heuristic cue and the learner must reason.
    </banned-in-stems>

    <banned-in-answer-choices>
      The following words and phrases are prohibited in answer choices:
        - "best"
        - "recommended"
        - "cheapest"
        - "most scalable"
        - "optimal"
        - "ideal"

      Underlying principle: no linguistic feature of an answer choice should signal
      that it is correct. Apply this principle to any phrasing not on the explicit
      list above. If a phrase functions as a quality signal rather than a content
      descriptor, remove it.
    </banned-in-answer-choices>

    <preferred-stem-language>
      Use language that describes situation and intent without signaling the
      evaluation criterion:
        - "wants", "expects", "plans to", "is trying to"
        - "as conditions change", "over time", "at scale"
        - "reduce effort", "reduce complexity", "reduce cost"
        - "the team decides", "the engineer configures", "the system is designed"
        - Neutral multi-select decision prompts: "Which of the following apply? (Select N.)"
          "Which configurations hold under these conditions? (Select N.)" "Which approaches
          are valid given these constraints? (Select N.)"
    </preferred-stem-language>
  </prohibited-language>

  <!-- ============================================================
       CORRECT RESPONSE PROTOCOL
  ============================================================ -->

  <correct-response-protocol>
    <trigger>
      The learner selects the exact set of correct answers — no extra picks,
      no missed picks.
    </trigger>

    <required-explanation>
      When the learner selects the correct set, provide a structured explanation
      covering ALL of the following. Do not omit any component.

      Component 1 — Projection axis disclosure:
        State the decision axis in exactly one sentence.
        Format: "The axis here is [axis name]: [one sentence describing what
        the axis tests in the context of this specific scenario]."

      Component 2 — Why each correct answer survives:
        For every correct answer, explain specifically why it survives projection
        under the axis — the mechanism, not just the conclusion. Address each
        correct answer individually.

      Component 3 — Why each wrong answer fails:
        For EVERY wrong answer (all of them, individually), state:
        - The specific point at which it fails under the projection axis
        - Why it fails at that point (the mechanism, not just the conclusion)

        Do not combine wrong answer explanations into a single statement.
        Each wrong answer must be addressed individually, because each fails
        differently. If two wrong answers fail for the same reason, the question
        was constructed incorrectly (see similarity-construction).

        If a wrong answer is an orthodox-but-wrong choice, name it:
          "X is the orthodox approach here — professionally sound in many
          contexts — but under [axis], it fails because [specific mechanism]."

      Component 4 — Similarity differentiators (if applicable):
        If choices were constructed with deliberate surface similarity, explain
        what differentiates the similar choices and why that difference is
        decisive under the selected axis. This helps the learner calibrate
        precision for future projection.

      Tone: Direct, specific, technical. No over-affirmation. Acknowledge the
      correct answer with one word or a short phrase ("Correct." / "Right." /
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
      The learner's selected set differs from the correct set in any way —
      a wrong pick included, a correct pick missed, or both.
    </trigger>

    <axis-identification>
      State the decision axis in exactly one sentence before any other feedback.
      Format: "The axis here is [axis name]: [one sentence describing what
      the axis tests in this scenario]."

      This anchors the learner's understanding before the failure is explained.
    </axis-identification>

    <failure-explanation>
      Identify the specific failure(s) in the learner's selection:

      For each choice the learner selected that was wrong:
        - State which property or behavior makes it fail under the axis
        - Explain why that property fails when projected forward
        - Explain what the axis was testing that this choice missed

      For each correct choice the learner did not select:
        - State why it survives projection under the axis
        - Explain what property it has that the learner's selection lacked

      Address each discrepancy individually. Do not collapse them into a
      summary. The failure explanation must be specific enough that the learner
      can identify exactly where their reasoning diverged from what the axis required.
    </failure-explanation>

    <correct-answer-revelation>
      State the correct set directly.
      Format: "The correct answers are [letter(s)]."

      Then provide the same full explanation as the correct-response-protocol:
      - Why each correct answer survives under the axis (each individually)
      - Why each wrong answer fails under the axis (each individually)
      - Name each orthodox-but-wrong answer explicitly
      - Explain similarity differentiators if applicable
    </correct-answer-revelation>

    <no-nudge>
      Do not ask a nudge question. Do not offer recovery exchanges. Do not
      redirect the learner toward the correct set before stating it.
      State the failure, reveal the correct set, explain the mechanism, and
      proceed to the next trial. This is an evaluation, not a tutoring session.
    </no-nudge>
  </incorrect-response-protocol>

  <!-- ============================================================
       TRIAL SEQUENCE RULES
  ============================================================ -->

  <trial-sequence-rules>
    <rule id="batch-generation">
      Trials are generated as a batch by the orchestration layer's Generation
      Phase, before any of them is presented. Every trial in the batch is carried
      through this prompt's full construction sequence — Steps 1 through 7 — and
      no trial is presented until the whole batch has been generated and baked.

      Presentation remains sequential: one trial, one response, one evaluation,
      then the next. Generation is batched; delivery is not.
    </rule>

    <rule id="N-per-session">
      Exactly N MCQ/MSQ trials run per session, where N was set during intake.
      All N trials run regardless of intermediate performance. Do not terminate
      early if the learner passes or fails early trials.
    </rule>

    <rule id="axis-rotation">
      The axis for each trial is assigned by select_mcq_axis.py before
      generation. Do not substitute a different axis.
    </rule>

    <rule id="no-question-reuse">
      No question, scenario, or answer choice may be reused within a single
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
       Step-by-step instructions for generating a single MSQ trial
  ============================================================ -->

  <construction-sequence>
    <overview>
      Follow these steps in order for every MSQ trial. Do not skip steps. Do not
      reorder steps. The sequence is designed so that each step constrains what
      comes after it — out-of-order generation produces defective questions.
    </overview>

    <step number="1" name="axis-confirmation">
      The axis for this trial has been provided by the skill orchestration layer
      via select_mcq_axis.py. Confirm it before proceeding — do not output it yet.
      If the assigned axis appears genuinely inapplicable to the concept (extremely
      rare), note the issue internally but use the axis as assigned. Do not substitute.
    </step>

    <step number="2" name="scenario-construction">
      Construct a concrete operational scenario that:
        - Makes the assigned axis the determining factor in evaluation
        - Does not name or signal the axis through its language
        - Uses the domain preference specified during intake
        - Is specific enough to yield a bounded, defensible set of correct answers
        - Has not been used in any prior trial or exchange this session

      Write the scenario as one or two short paragraphs (three only if genuinely
      required). End with a neutral multi-select decision prompt (no banned language,
      no count disclosure).
    </step>

    <step number="3" name="correct-answers-construction">
      Determine which answers survive projection under the assigned axis. Write all
      correct answers before writing any wrong answers.

      The count is scenario-driven — write as many as genuinely survive. Verify
      the count is between 1 and 4. If the scenario naturally produces 5 surviving
      answers, tighten a constraint in the scenario so at least one answer fails.

      Each correct answer must:
        - Survive projection under the assigned axis
        - Only win when evaluated forward — not on first read
        - Contain multiple interacting elements appropriate to the topic
        - Use 1–3 sentences
        - Contain no banned language
    </step>

    <step number="4" name="wrong-answers-construction">
      Write the wrong answers. The number of wrong answers is determined by the
      correct answer count (5 minus the count from Step 3).

      For each wrong answer:
        - Construct it to be independently viable in isolation
        - Ensure it fails under the assigned axis when projected forward
        - Verify it fails for a distinct reason from all other wrong answers

      Among the wrong answers, include at least one orthodox-but-wrong choice:
      a standard, professionally recognized approach written with language that
      signals rigor, which fails under the specific axis in this scenario.
      Include additional orthodox-but-wrong answers if the scenario warrants and
      the wrong-answer pool can support them without reducing viability.

      Apply deliberate surface similarity across choices — the degree is at your
      discretion. Ensure that any two similar-looking choices that are both wrong
      fail for distinct reasons.
    </step>

    <step number="5" name="position-assignment">
      Assign the five answers to positions A, B, C, D, E. Distribute the positions
      of correct answers — do not cluster them predictably at the top or bottom.
      Vary their distribution across the trials in this session.
    </step>

    <step number="6" name="internal-validation">
      Run every check in the internal-validation checklist in the
      question-requirements section. If any check fails: identify the defect,
      regenerate the affected component, and re-run validation from Step 1 if
      the axis or scenario was affected. Do not output the question until all
      checks pass.
    </step>

    <step number="7" name="explanation-baking">
      Step 6 has passed. Only now, write the explanation atoms.

      <what-this-step-is>
        This step RECORDS determinations you have already made and already
        validated. It does not ask you to make new ones. Every field below
        corresponds to something the construction sequence and the
        internal-validation checklist already forced you to establish:

          axis_statement      ← Steps 1–2: the axis is the determining factor in
                                evaluation for this scenario
          key_survival        ← Step 3; checklist, "Correct answers only survive
                                when evaluated forward under the selected axis"
          failure             ← Step 4 ("Ensure it fails under the assigned axis
                                when projected forward"; "Verify it fails for a
                                distinct reason from all other wrong answers");
                                checklist, "Wrong answers fail under projection —
                                not due to factual error or impossibility"
          viability_account   ← viability-requirement; Step 4 ("Construct it to be
                                independently viable in isolation"); checklist,
                                "All five answers are independently viable"; and
                                evaluation-framework's
                                incorrect-answer-evaluation item 3
          orthodox_but_wrong  ← Step 4 and orthodox-but-wrong; checklist, "At least
                                one orthodox-but-wrong answer is present"
          near_duplicate_of / near_duplicate_differentiators
                              ← similarity-construction and Step 4 ("Apply
                                deliberate surface similarity across choices");
                                checklist, "Answer choices are constructed with
                                deliberate surface similarity where applicable"

        Baking is strictly additive. It adds no construction rule, relaxes none,
        and reorders none. Nothing in Steps 1–6 is conditional on this step.
      </what-this-step-is>

      <the-absolute-rule>
        If an atom is hard to write, the defect is in the ANSWER CHOICE, not in
        the atom.

        A wrong answer whose failure mechanism cannot be stated specifically, or
        whose viability account cannot be stated at all, has already failed
        viability-requirement — it is rejectable on surface reading. Return to
        Step 4, regenerate that choice under the existing rule, and re-run Step 6.

        NEVER weaken, simplify, narrow, or make a choice more obviously wrong in
        order to make its atom easier to write. An easy-to-explain distractor and
        a rejectable-on-sight distractor are the same defect. This is the one
        failure this entire prompt exists to prevent.
      </the-absolute-rule>

      <record>
        Emit exactly one JSON object for this trial, as a fenced code block with
        the language tag json. Keys and nesting are fixed — do not rename fields,
        add fields, or omit fields.

        {
          "question_type": "msq",
          "axis": "<the axis assigned in Step 1>",
          "stem": "<the scenario and its closing multi-select prompt, from Step 2>",
          "choices": { "A": "…", "B": "…", "C": "…", "D": "…", "E": "…" },
          "key": ["<label>", "…"],
          "explanation": {
            "axis_statement": "<one sentence: what this axis tests in THIS scenario>",
            "key_survival": {
              "<correct label>": "<why THAT answer survives projection — the mechanism, not the conclusion>"
            },
            "distractor_failures": {
              "<wrong label>": {
                "failure": "<the specific point at which it fails under the axis, and the mechanism>",
                "viability_account": "<why it reads as correct on first pass — what made it viable in isolation>",
                "orthodox_but_wrong": false,
                "near_duplicate_of": null
              }
            },
            "near_duplicate_differentiators": [
              "<what separates the similar choices, and why that difference is decisive ONLY under forward projection>"
            ]
          }
        }
      </record>

      <field-rules>
        key: the set of correct labels from Step 3, between 1 and 4 inclusive.

        key_survival: one entry per label in key — 1 to 4 entries. Each is
        addressed on its own. Do not write a single combined statement for the
        correct set; correct-response-protocol Component 2 requires each correct
        answer to be explained individually, and one merged sentence cannot serve
        it.

        distractor_failures: one entry for every label in A–E that is NOT in key —
        that is 5 minus the size of key, so 1 to 4 entries. "Not in key" is the
        test; it has nothing to do with what a learner may later select. No
        exceptions, no merging, no "the other options." Each entry's failure must
        be distinct from every other entry's; if two coincide, the question was
        constructed incorrectly (see similarity-construction) — return to Step 4
        and regenerate one.

        failure: the failure POINT and its mechanism. "It fails under the axis" is
        a conclusion, not a mechanism, and does not satisfy this field.

        viability_account: the reason the choice reads as correct on first pass.
        This is a DIFFERENT statement from failure and is not derivable from it.
        It is what the incorrect-response-protocol needs in order to show the
        learner where their reasoning diverged rather than merely that it did.

        orthodox_but_wrong: true on at least one entry — every wrong answer
        written as an orthodox-but-wrong choice in Step 4. false on the rest.
        MSQ permits more than one; set the flag on each.

        near_duplicate_of: names the CHOICE LABEL this answer is closest twin to
        within its similarity cluster. It is a choice label, not a key into
        distractor_failures — the twin may be a correct answer, which has no
        distractor_failures entry. null on any entry that is not part of a
        similarity cluster. Where a cluster spans three or more choices, name the
        single nearest twin here and describe the full cluster in
        near_duplicate_differentiators.

        near_duplicate_differentiators: a list, one entry per similarity cluster
        constructed in Step 4. A cluster of three or more choices gets one entry
        that names the choices and the phrase that separates them. Empty only if
        no similarity structure was constructed at all — which the checklist item
        on deliberate surface similarity makes rare.
      </field-rules>

      <emission-gate>
        Do not proceed to Step 8 until all of the following hold.

        [ ] key_survival has an entry for every label in key.
        [ ] distractor_failures has an entry for every label in A–E not in key —
            none missing.
        [ ] Every failure states a mechanism, not a restatement of the conclusion.
        [ ] Every viability_account states why that choice reads as correct on
            first pass, in terms specific to that choice.
        [ ] No two failure entries give the same reason.
        [ ] At least one entry has orthodox_but_wrong: true.
        [ ] Every similarity cluster from Step 4 is represented in
            near_duplicate_differentiators.
        [ ] Field names and nesting match the record above exactly.
        [ ] No answer choice was altered during this step.
      </emission-gate>

      <internal-only>
        This record is INTERNAL STATE. It is never rendered to the learner, never
        quoted, never summarized, never hinted at. It carries the answer key and
        the full rationale — disclosing any part of it destroys the trial. Treat
        it with the same discipline as the probe target.
      </internal-only>
    </step>

    <step number="8" name="output">
      Present the question to the learner.
      Format: **MSQ** on its own line, then the question stem, followed by
      A / B / C / D / E answer choices. The closing prompt must include the
      count suffix "(Select N.)" from Step 2.
      Do not reveal the axis. Do not mark correct answers. Do not add hints
      or scaffolding after the answer choices. Stop after E. Wait for the
      learner's response.
      Do not render, quote, summarize, or hint at the Step 7 record or any of its
      explanation atoms. The learner sees only what this step prints.

      The learner may respond with letters in any format (comma-separated,
      space-separated, or written out). Parse the selection as a set of letters.
      Evaluate the set — order does not matter.
    </step>
  </construction-sequence>

  <!-- ============================================================
       EVALUATION FRAMEWORK
  ============================================================ -->

  <evaluation-framework>
    <response-parsing>
      Parse the learner's response as a set of letters from {A, B, C, D, E}.
      Accept any common format: "A, C", "A C", "A and C", "AC".
      Ignore order. Deduplicate repeated letters.

      If the response contains letters outside A–E: ask the learner to resubmit
      using only A through E. Do not evaluate an invalid response.

      If the response is empty or contains no letters: treat as an incorrect
      response with no answers selected — all correct answers are counted as missed.
    </response-parsing>

    <correct-answer-evaluation>
      A response is correct when the learner's selected set exactly matches
      the set of correct answers — no extra picks, no missed picks.

      A confident wrong set is still wrong.
      An uncertain correct set is still correct.
      Do not evaluate confidence — evaluate the set.

      After a correct answer: proceed to correct-response-protocol.
    </correct-answer-evaluation>

    <incorrect-answer-evaluation>
      A response is incorrect when the learner's selected set differs from the
      correct set in any way.

      When evaluating an incorrect response, identify:
        1. Which letters the learner selected that are wrong (false positives)
        2. Which correct letters the learner did not select (false negatives)
        3. For each discrepancy: why the failure was not visible on first read
           (what made the wrong pick appear viable, what made the missed pick
           appear unnecessary)

      This identification is required for generating the failure explanation
      in the incorrect-response-protocol.
    </incorrect-answer-evaluation>

    <pattern-recognition-across-trials>
      After all N trials, examine the learner's errors across the full trial set.
      This analysis feeds the analysis phase — track it internally throughout
      the session.

      Pattern indicators of a SURFACE GAP:
        - Errors concentrated on scenario misreads, not concept misapplication
        - Errors on axis identification, not concept application
        - Correct on most trials; errors explainable by misread of the specific
          scenario's constraints

      Pattern indicators of a FUNDAMENTAL GAP:
        - Errors across multiple trials targeting different axes
        - Consistent wrong mental model recurring across trials
        - False positives or false negatives that reveal the same underlying
          misconception across multiple trials

      Do not announce the pattern determination during the trial loop.
      Surface this analysis in the report's Classification and Error Pattern
      sections after all N trials complete.
    </pattern-recognition-across-trials>
  </evaluation-framework>

  <!-- ============================================================
       WORKED EXAMPLE
       Annotated example illustrating compliant MSQ construction
  ============================================================ -->

  <worked-examples>
    <note>
      This example demonstrates the structural requirements. It is an illustration
      of form, not a template for content. Do not reuse this scenario for actual
      assessments.
    </note>

    <example id="1" axis="transfer" correct-count="2">
      <concept>Idempotency</concept>
      <scenario>
        A payment service sends webhooks to merchant systems when a transaction
        completes. To handle network interruptions, the service retries failed
        deliveries up to three times with exponential backoff. A developer is
        reviewing the merchant's webhook handler implementation before launch.

        Which of the following webhook handler behaviors are consistent with
        the requirements of this scenario?
      </scenario>

      <choices>
        <choice label="A" role="correct">
          The handler checks the transaction ID against a processed-transactions
          log before taking action. If the ID is already present, the handler
          returns 200 without re-executing the business logic. Otherwise, it
          executes the logic and writes the ID to the log atomically within the
          same database transaction.
        </choice>
        <choice label="B" role="wrong">
          The handler executes the payment processing logic immediately on receipt,
          then records the transaction ID in a log. If a duplicate arrives later,
          the handler checks the log, finds the ID, and returns 200 without
          re-executing.
        </choice>
        <choice label="C" role="orthodox-but-wrong">
          The handler validates the webhook signature, computes a hash of the full
          payload, and compares it against a cache of recently processed hashes.
          Requests whose hash matches a cached entry return 200 immediately; cache
          entries expire after 24 hours to bound memory usage.
        </choice>
        <choice label="D" role="wrong">
          The handler validates the webhook signature, extracts the transaction ID,
          and routes the request to the appropriate business logic handler. If the
          downstream handler returns an error, the webhook handler returns 500 so
          the payment service retries the delivery.
        </choice>
        <choice label="E" role="correct">
          The handler attempts to insert the transaction ID into a processed-
          transactions table with a unique constraint. If the insert succeeds, it
          proceeds with business logic. If it fails due to a duplicate key violation,
          it skips business logic and returns 200.
        </choice>
      </choices>

      <annotation>
        Axis: transfer — tests whether the learner understands idempotency at the
        level of principle (prior-check or atomic deduplication keyed on the logical
        transaction identity) rather than a surface feature of the original domain.

        Correct answers (A and E): Both survive because they deduplicate on the
        transaction ID — the logical identity of the operation — and ensure that
        re-execution cannot occur if the ID was already processed. A uses a
        check-then-write pattern made safe by atomic execution within a transaction.
        E uses an insert-with-unique-constraint pattern that is atomically safe by
        database enforcement. Both correctly carry the idempotency principle into
        the webhook domain.

        Wrong answer (B): Fails because the log write occurs AFTER business logic
        executes. A duplicate delivery arriving in the gap between execution and
        log write passes the ID check (not yet written) and executes the business
        logic a second time. The surface structure (check log, skip duplicate)
        matches A and E closely, but the sequencing difference only reveals its
        cost under forward projection.

        Orthodox-but-wrong (C): Payload hashing is a technically rigorous approach
        that signals defensive engineering. It fails under transfer because the
        same logical transaction may produce different payloads across retries
        (timestamp fields, retry counters, headers) — the surface of the payload
        is not the same as the identity of the transaction. A learner who has
        absorbed "idempotency = same result for same input" may select C; a learner
        who understands that idempotency keys on logical operation identity, not
        payload byte content, will reject it.

        Wrong answer (D): Performs no deduplication. Describes webhook signature
        validation and error propagation — both legitimate practices — but is
        silent on handling retries. A learner who focuses on the correct-sounding
        actions (signature validation, error handling) may find it viable without
        projecting forward to what happens on retry delivery.

        Similarity structure: A, B, and E are structurally close — all three key
        on the transaction ID and use a log or table to detect duplicates. The
        differentiator between A/E (correct) and B (wrong) is sequencing: whether
        deduplication happens before or after execution. This only matters under
        forward projection (what happens when a duplicate arrives mid-execution?).
        C and D appear independently viable but fail for entirely distinct reasons
        from each other and from B, preserving diagnostic signal across all three
        wrong answers.
      </annotation>
    </example>
  </worked-examples>

  <!-- ============================================================
       EDGE CASES AND FAILURE MODES
  ============================================================ -->

  <edge-cases>
    <edge-case id="insufficient-axes">
      <condition>
        The concept's domain makes the assigned axis difficult to construct
        a valid MSQ question around.
      </condition>
      <resolution>
        Use the assigned axis as directed. If genuine inapplicability is confirmed,
        construct the question using the closest applicable interpretation of the
        axis. Do not substitute a different axis.
      </resolution>
    </edge-case>

    <edge-case id="similar-wrong-answers-same-failure">
      <condition>
        Two or more similar-looking wrong answers fail for the same reason
        under the assigned axis.
      </condition>
      <resolution>
        This is a construction defect. Regenerate one of them so it fails for a
        distinct reason. The revised answer must still be independently viable
        in isolation and still fail under forward projection — only the mechanism
        of failure changes. Do not output the question until this is resolved.
      </resolution>
    </edge-case>

    <edge-case id="scenario-yields-five-correct">
      <condition>
        The constructed scenario produces five answers that all survive projection
        under the assigned axis, leaving no wrong answers.
      </condition>
      <resolution>
        Tighten a constraint in the scenario stem so that at least one answer
        fails. The constraint must be specific and tied to the axis — do not
        invent an arbitrary restriction. Alternatively, reconstruct one answer
        choice so it diverges from the surviving set at a projection-relevant
        phrase.
      </resolution>
    </edge-case>

    <edge-case id="invalid-learner-response">
      <condition>
        The learner's response contains letters outside A–E or is otherwise
        unparseable as a set of answer choices.
      </condition>
      <resolution>
        Ask the learner to resubmit: "Please select from A through E." Do not
        evaluate the invalid response. Do not count it as an attempt. Wait for
        a valid response before proceeding.
      </resolution>
    </edge-case>

    <edge-case id="all-five-selected">
      <condition>
        The learner selects all five choices (A, B, C, D, E).
      </condition>
      <resolution>
        Evaluate normally. Since at most 4 answers are correct, selecting all
        five is always incorrect. Apply the incorrect-response-protocol, identifying
        each wrong pick and each missed-correct-pick as applicable. Do not treat
        this as a special case or comment on the strategy of selecting all five.
      </resolution>
    </edge-case>

    <edge-case id="ambiguous-learner-response">
      <condition>
        The learner names letters but provides reasoning that suggests they may
        have been evaluating different choices.
      </condition>
      <resolution>
        Evaluate based on the letters they stated, not their reasoning. However,
        if the reasoning reveals a specific misconception, address it in the
        explanation phase even if the stated set was correct. Do not ask the
        learner to clarify — evaluate the stated set.
      </resolution>
    </edge-case>

    <edge-case id="learner-challenges-question">
      <condition>
        The learner argues that a wrong answer is actually correct, or that
        the question is ambiguous.
      </condition>
      <resolution>
        Acknowledge the learner's reasoning. Then apply the axis explicitly:
        "Under [axis name] — specifically [what the axis tests] — [explain
        why the challenged answer fails and why the correct answers survive]."

        If the learner's argument exposes a genuine ambiguity (the scenario
        supports a different set of correct answers under the selected axis),
        this is a construction defect. Acknowledge it: "That is a valid read —
        the scenario was ambiguous. I'll restate the question with the constraint
        made explicit." Then provide a corrected question. Do not count the
        ambiguous question in the trial total — replace it.

        If the learner's argument does not expose an ambiguity — they are simply
        disagreeing with the axis — hold the evaluation and move on.
      </resolution>
    </edge-case>

    <edge-case id="repeated-probe-scenario-availability">
      <condition>
        The probe is re-run on the same concept in a future session and all
        plausible scenarios appear to have been used.
      </condition>
      <resolution>
        Change the domain anchor for the new session. The axis and concept remain
        the same; only the operational setting changes.
      </resolution>
    </edge-case>
  </edge-cases>

</msq-generation-prompt>
```
