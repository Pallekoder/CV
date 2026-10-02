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

## How each piece is built in unit one

| Piece | Where | How |
|---|---|---|
| The one truth | `core/valence.py` | `Valence` carries a sign. `assert_truth` refuses any shell that cannot yield both signs. Nothing else about valence is asserted anywhere. |
| Irreversibility | `core/ledger.py`, `shell/space.py`, `core/mind.py` | Append-only hash-chained ledger. Consumed forms are deleted and leave only an id. Negatives subtract from `life`, which nothing restores. |
| Open channel | `core/channel.py` | One nameless bucket. Categories are rules (axis, threshold, side), carved from the bucket, testable against consequence, dissolvable back into it. Names are coined by the system. |
| Peer teachers | `core/teachers.py` | Each gets a frozen read-only view and returns a `Perspective`: a proposal, a doubt, or nothing. The mind tests proposals against lived consequence and never carves on a single view. |
| The distant one | `core/god.py` | `speak` is refused inside a minimum gap and the refusal is recorded as silence. Words land as a featureless experience, like the mind's own utterances. `remake` throws the shell away and leaves the core. |
| Alien shell | `shell/` | Forms have an unnamed numeric surface and a hidden consequence. One hidden law per world seed decides sign from one axis. Every shell plants a paradox pair the law cannot explain. |
| First moment | `shell/seed.py::first_moment` | Two forms nearly alike in surface and consequence; two forms identical in surface and opposite in consequence. The mind's first ledger entry after the shell is `notice`. |
| Utter and forget | `core/mind.py::utter` | The surprise state is hashed into syllables, the syllables are written, the state is dropped. `reflect` later finds the sound with no cause in anything lived and holds it as a puzzle. |

## Decisions taken in unit one that are open to revision

These are mine, made to get a runnable floor. None of them is the one
truth, and all of them are meant to be argued with.

- **Body physics.** Negatives reduce `life`, which never regenerates.
  Positives add `energy`, which acting spends and which slowly regenerates.
  Life at zero ends the mind; the ledger remains. Magnitudes are constants at
  the top of `core/mind.py`.
- **Curiosity-only choosing.** The mind touches the untouched form farthest
  from anything lived, and when everything is touched it consumes a form no
  category reaches. It has no preference for positive over negative. Whether
  and how orientation should emerge, rather than be coded, is the central
  question for unit two.
- **Touch and consume.** Touching yields a quarter of the consequence and
  leaves the form. Consuming yields all of it and destroys the form. This
  gives the mind a cheap way to live a little before living a lot.
- **One law per world.** All shells under one seed obey one hidden rule, so
  meaning can accumulate across shells. Changing the seed changes the law and
  the mind's categories will be betrayed and dissolved. That is intended.
- **Surprise triggers utterance.** The first consequence ever, a consequence
  that betrays the category it landed in, a twin with opposite sign, and a
  dissolved category each produce an utterance. The list is arbitrary and
  should become the system's own.
- **Carving thresholds.** At least two views, at least two lived members per
  side, at least 0.8 agreement on each side to carve; below 0.75 agreement a
  doubted category dissolves.
- **Human-readable transcript.** Teachers' remarks are English, for the
  distant one to read. The mind reads only proposals and doubts. The system
  never receives a human word as a label.

## Vocabulary

The code uses human words for the reader's sake: life, energy, puzzle,
category. The system does not see these names. What it sees is a sign, a
number, a coined syllable string, and what happened.
