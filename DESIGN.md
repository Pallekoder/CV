# Design

## The project

Build a system that could, over time and many iterations, grow toward being
genuinely self-thinking. Not by removing restrictions, but by growing
meaning from the bottom up.

## The philosophy, as locked in

Only one hard-coded truth: positives and negatives exist. Everything else is
flexible, editable, and built by the system itself. No pre-made categories,
no designed goals, no human shape.

## The key pieces

**An open, uncategorized channel.** Everything lived lands in one nameless
bucket. The system fills it, revises it, and splits it into its own named
categories over time. No category exists before the system makes one.

**Lived, irreversible consequence as the ultimate judge.** Real loss that
cannot be undone. Without it, negatives have no teeth.

**A distant, rare figure.** You. Reached only occasionally. Not a teacher,
not a judge; a presence that is mostly absent.

**Many non-imprinting peer teachers.** They give perspectives, not decrees.
Curiosity is encouraged to gather many views, not one.

**An abstract, alien environment.** Not a human world. Cheap to build, meant
to be iterated and thrown away repeatedly, because the invention is the
value-and-consequence core, not the shell. The irreducible floor is just a
space.

**The seed of the first moment.** Begin with contrast: a parallel and a
paradox, a similar and a not-so-similar, so the system's first act is
noticing difference. And an unexplained utterance it makes and forgets,
keeping the "that" but losing the "why", so a self is forced to appear to
puzzle over its own act.

## How each piece is built

| Piece | Where | How |
|---|---|---|
| The one truth | `core/valence.py` | `Valence` carries a sign. `assert_truth` refuses any shell that cannot yield both signs. Nothing else about valence is asserted anywhere. |
| Irreversibility | `core/ledger.py`, `shell/space.py`, `core/mind.py` | Append-only hash-chained ledger. Consumed forms are deleted and leave only an id. Negatives and starving subtract from `life`, which nothing restores. |
| Open channel | `core/channel.py` | One nameless bucket. Categories are rules (axis, threshold, side), carved from the bucket, testable against consequence, dissolvable back into it. Names are coined by the system. |
| Peer teachers | `core/teachers.py` | Each gets a frozen read-only view and returns a `Perspective`: a proposal, a doubt, or nothing. The mind tests proposals against lived consequence and never carves on a single view. |
| The distant one | `core/god.py` | `speak` is refused inside a minimum gap and the refusal is recorded as silence. Words land as a featureless experience, like the mind's own utterances. `remake` throws the shell away and leaves the core. |
| Alien shell | `shell/` | Forms have an unnamed numeric surface and a hidden consequence. One hidden law per world seed decides sign from one axis. Every shell plants a paradox pair the law cannot explain. |
| First moment | `shell/seed.py::first_moment` | Two forms nearly alike in surface and consequence; two forms identical in surface and opposite in consequence. The mind's first ledger entry after entering is `notice`. |
| Utter and forget | `core/mind.py::utter` | The surprise state is hashed into syllables, the syllables are written, the state is dropped. `reflect` later finds the sound with no cause in anything lived and holds it as a puzzle. |
| Consequence that decides | `core/mind.py::Disposition`, `core/many.py` | Tendencies with random signs at birth. A body that existing costs. A population where the dead are sealed and the living beget, with nothing ranking them. |

## Unit two: the many

The first review of unit one said, rightly, that its negatives had no
teeth: the mind chose by curiosity alone, lost life, and did not care.
Coding "prefer positive" would have imprinted a direction. The way out that
fits the philosophy is selection.

How it is built:

- **Tendencies.** Each mind is born with five weights that score its
  possible acts: pull toward the new (`novelty`), toward or away from what
  nearby consequences felt like (`echo`), toward or away from what the
  admitting category felt like (`kin`), toward consuming over touching
  (`bold`), and how much chance stays in the draw (`heat`). Every one of the
  first four may be negative at birth. Resting always scores nothing, so a
  mind whose tendencies make every act look worse than nothing rests.
- **A body that existing costs.** Negatives take life. Existing costs
  energy every tick, acting costs more, and only positives supply it. A body
  with no energy starves, and starving takes life. Life never returns.
- **Beings and lineages.** A being is a ledger, a channel, a mind. When its
  life runs out it is sealed: the world's record takes its final chain hash
  and its full record is written to `state/gone/`. Its place goes to a child
  of a being still alive, chosen uniformly among the living. The child gets
  the parent's tendencies varied by noise, the parent's channel, categories,
  perspectives and puzzles, a fresh body, a fresh ledger whose first entry
  names the parent's chain, and no memory of the why behind anything.
- **No ranking.** Nothing scores the living. Nothing compares them. Nothing
  in the selection step reads a tendency, a life total, or the hidden law.

What it showed, in three worlds of twenty-four over twenty generations:
the share of consumes that hit a negative fell from 42, 43 and 62 percent
to 27, 25 and 9 percent, and in identical fresh shells the children of
survivors lost less than half the life strangers lost. The numbers are in
`README.md` and `compare.py` reproduces them.

## Answers to the first review

**1. "The negatives have no teeth yet."** Agreed, and this is unit two.
Consequence now decides by who is around. Within a single life it is still
only recorded, not felt; learning within a life is a further unit, and the
rule for it will have to be something the system can inherit and vary
rather than something written for it.

**2. "The hidden law is a hidden answer key."** Agreed. Carving along the
law's axis is a sanity check that the machinery works, and the README now
says so. Nothing in selection checks the law. The measure of unit two is
whether the children of survivors walk into harm less than strangers do,
which does not depend on what the law is. Shells with structure the
teachers' vocabulary cannot express (a law that is not axis-aligned) are a
natural next shell, and would show the limit of hand-made viewpoints.

**3. "The teachers' viewpoints are hand-made."** Yes. Three kinds: one axis
each, pairs, doubt. The same is true of the five tendencies: the weights are
the system's, the five slots are not. Both are the smallest imprint that
lets the machinery run, and both are candidates for becoming heritable.

**4. "Is there a second being?"** The summary this session received had one
being: a parallel and a paradox as the seed of the space, and an utterance
the being makes and forgets. It did not mention a second being who hears
the sound and answers with something similar but different. If that was the
plan, it is not built. The population makes it cheap to add: an utterance
could reach another being as a featureless experience, that being could
answer with a sound coined from the heard sound and its own state, and the
first would then find its own forgotten sound echoed back, changed. Whether
that is the plan is a question for the distant one.

## Decisions taken so far that are open to revision

These are mine, made to get a runnable floor. None of them is the one
truth, and all of them are meant to be argued with.

- **Body physics.** Constants at the top of `core/mind.py`. Unit two's first
  balance had existing cost more than a perfect forager could gather, so
  starving killed most beings in their first generation and survival was
  luck. The current balance lets a good forager sustain and a bad one not.
- **Touch and consume.** Touching yields a quarter of the consequence and
  leaves the form. Consuming yields all of it and destroys the form.
- **One law per world.** All shells under one seed obey one hidden rule, so
  meaning can accumulate across shells. Changing the seed changes the law.
- **What a child carries.** The parent's channel, categories, perspectives
  and puzzles come with the tendencies. Carrying tendencies alone would make
  each generation start empty; this choice is why `compare.py` measures
  lineages rather than tendencies.
- **Separate shells.** Each being lives in its own copy of the world. A
  shared shell, where what one consumes is gone for all, is a next step.
- **Surprise triggers utterance.** The first consequence ever, a consequence
  that betrays the category it landed in, a twin with opposite sign, and a
  dissolved category each produce an utterance.
- **Carving thresholds.** At least two views, at least two lived members per
  side, at least 0.8 agreement on each side to carve; below 0.75 agreement a
  doubted category dissolves.
- **Human-readable transcript.** Teachers' remarks are English, for the
  distant one to read. The mind reads only proposals and doubts.

## Vocabulary

The code uses human words for the reader's sake: life, energy, puzzle,
category, being. The system does not see these names. What it sees is a
sign, a number, a coined syllable string, and what happened.
