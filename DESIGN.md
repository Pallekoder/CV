# Design

The philosophy is in `BRIEF.md` and is not repeated here. This file says
how each piece of the brief is built, what the build adds that the brief
does not ask for, what the brief asks for that is not built, and which
decisions are open.

## How each piece of the brief is built

| Brief | Where | How |
|---|---|---|
| The one hard-coded truth | `core/valence.py` | `Valence` carries a sign. `assert_truth` refuses any shell that cannot yield both signs. Nothing else about valence is asserted anywhere. |
| Consequence must be real | `core/ledger.py`, `shell/space.py`, `core/mind.py::Body` | Append-only hash-chained ledger. Consumed forms are deleted and leave only an id. Negatives and starving subtract from `life`, which nothing restores. |
| The route is selection | `core/many.py`, `core/being.py` | The dead are sealed into the world's record. Their places go to children of the living, chosen uniformly. Nothing scores, ranks, or compares the living. |
| No imprinted direction | `core/mind.py::Disposition` | Every tendency is drawn with a random sign at birth, including the ones that read the body and the one that bends the rest. |
| The open channel | `core/channel.py` | One nameless bucket. Categories are rules carved from it, named by coined syllables, tested against consequence, dissolved when they fail. A category narrows into children along another axis when its members disagree; an arrival lands in the deepest category that admits it. |
| Seeing the boxes fill and narrow | `view.py` | Per being: the open bucket, the tree with each category's rule, members, agreement and mean, and the history of carving, narrowing, dissolving and undoing. Per world: growth by generation over every being that has lived. |
| Teachers, never decrees | `core/teachers.py`, `TEACHERS.md` | Off unless switched on. A teacher visits rarely and irregularly, sees the open bucket through a frozen read-only view, and leaves a remark and at most one proposed cut. The mind weighs it as one candidate among its own, by consequence; ties go to its own. It finds its own cuts and doubts its own categories and never waits for a visit. |
| The distant figure, rare | `core/god.py` | `speak` is refused inside a minimum gap, and the refusal is recorded as silence. Words land as a featureless experience, like the mind's own forgotten sounds. |
| The seed moment | `shell/seed.py::first_moment`, `core/mind.py::utter`, `::reflect` | Two forms nearly alike and alike in consequence; two identical and opposite. The first ledger entry after entering is `notice`. A surprise is hashed into syllables; the syllables are written; the state is dropped; the next tick finds the sound with no cause and holds it. |
| The environment | `shell/` | Forms with an unnamed numeric surface and a hidden consequence, under one hidden law per world seed. Built per generation and thrown away. |
| The discipline | `NOTEBOOK.md` | Predictions before each run, results after, surprises named. Started at unit three; the first two units are reconstructed and say so. |

## The units

**Unit one** built the floor: everything in the table except selection and
the tendencies. Its mind chose by curiosity alone, which the brief rightly
calls the weak point.

**Unit two** built selection. Five tendencies (novelty, echo, kin, bold,
heat) score the acts; the first four may be negative at birth. The body
pays upkeep every tick and only positives supply energy, so starving is
possible. A `World` holds beings; a generation is one shell each; the dead
are sealed; the living beget. `compare.py` measures what being around
changed: children of survivors against strangers in identical shells.

**Unit five** took the teachers out of the loop. Until then the mind
consulted six teachers on every tick that something new was lived and
could not carve without a proposal from one of them; the carving engine
was the teachers, which is the dependence the brief rules out. The mind's
own looking (`_own_cuts`: the best line along each axis of what it has
lived), its own doubt and its own undoing now do all of it. Teachers are
visitors with their own random stream, so switching visits on changes
nothing else about a run. The check of that found an older bug: a child
starts its own ledger at zero but carries its parent's channel, and its
acts overwrote inherited experiences with the same index. Experience
indices are now the channel's own.

**Unit four** let categories narrow and built the viewer. `consider` now
offers every category whose members disagree a chance to split before it
can be doubted, carves the open bucket afterwards, applies doubts only to
categories that already stood, and finally undoes any cut whose two sides
lean the same way and agree together. The `corner` law makes a form
positive only when two axes both clear a threshold, so no single cut sorts
it. The first corner run grew thickets; a side now needs four lived
members and a two-sided cut must improve on what it cuts, which is the
same rule as before, that consequence must support a cut, taken seriously
at small samples.

**Unit three** let the body into the choice: `hungry` adds to every act
when energy is low, `hurt` adds to consuming when life is low, and
`plasticity` bends the first four tendencies by lived consequence, each
inherited and unsigned. Children inherit what the parent was born as, not
what life bent. `freeze()` holds named tendencies at zero without changing
any other draw, so a world with the knobs and one without share founders
and shells.

## What the build adds that the brief does not ask for

These are mine. The brief does not forbid them, but it did not ask, and
each is a place where a direction could have crept in.

- **Energy and starving.** The brief's teeth are life lost to negatives.
  Energy makes positives matter too: without them a being starves. It is
  physics, not a preference, but it is a second pressure the brief did not
  name, and unit three suggests it can compete with the first.
- **One hidden law per world.** All shells under one seed obey one rule
  that decides sign from one axis. It exists so meaning can accumulate
  across shells. It is also an answer key, and nothing in selection reads
  it; success is measured by harm avoided, not by law recovered.
- **Touch and consume.** A quarter of the consequence without loss, or all
  of it with the form destroyed.
- **The shape of the tendencies and of the bending rule.** Eight slots and
  a rule of the form "a tendency that contributed to an outcome moves by
  plasticity times the outcome times its contribution." The values and
  signs are the system's; the slots and the form are not.
- **What a child carries.** The parent's channel, categories, perspectives
  and puzzles, so meaning accumulates. This is why `compare.py` compares
  lineages, not tendencies alone.
- **Separate shells.** Each being lives in its own copy of the world.
- **How harsh a shell is.** A corner law's thresholds sit low so that about
  half of what is eaten is positive. Drawn around zero, the same law made
  a famine in which only resters survived. The shape of the law is the
  point; its scarcity is a separate dial.

## What the brief asks for that is not built

- **Its own dimensions of experience.** The brief says the channel defines
  them and we never hand them over. Here the surface axes are the shell's,
  and categories are thresholds along those axes. The system carves; it
  does not yet make the axes it carves along.
- **Must puzzle over its own act.** The forgotten sound is found and held
  as a puzzle, and that is all. Nothing works on it.
- **The late game.** Not started, and the brief says not to start it until
  the system has grown.

## What unit three showed, and the rule it illustrates

With the body in the choice, hungry children of survivors act about twice
as much as hungry strangers and survive far better. On harm avoidance the
question went through three verdicts. The first three-seed run said the
knobs made things worse; a paired control said the two policies were
about even; both were computed before the inherited-channel bug was found.
On intact inheritance, six seeds paired on the same founders and shells,
the plainer policy avoids harm better: a mean edge over strangers of
+1.49 without the knobs against +0.66 with them, and a larger fall in the
share of harmful consumes.

The rule this illustrates is the brief's discipline, with one addition:
predict, run, let the surprise correct you, and check the plumbing before
believing a result. One finding held through every rerun: in half of the
free worlds the bending knob was selected entirely negative, winding a
being's drives down after each success. A knob offered as learning was
used as a damper.

## Answers to the first review

1. *Negatives had no teeth.* Unit two gave consequence the last word by
   selection; unit three let it reach inside a life. Neither codes a
   preference.
2. *The hidden law is an answer key.* Agreed; see above. Nothing measures
   law recovery.
3. *Hand-made teachers.* They were worse than hand-made: the mind could
   not carve without them. Unit five made carving the mind's own and the
   teachers rare visitors, off by default, with what they should be left
   to the distant one (`TEACHERS.md`). The tendency slots remain hand-made.
4. *A second being?* Nothing is the plan except to make minds. Not built.

## Decisions open to revision

- **Whether begetting should cost the parent.** A child is born with a
  fresh body whatever its parent ate. In a famine shell, selection found
  this: lineages of beings that never act persist because each child
  lives on its birth energy long enough to beget. Charging the parent for
  a child would close that without preferring one sign of consequence,
  but it changes "every survivor is as likely a parent" into "every
  survivor who can afford it". Not taken; the distant one decides.

- Body constants at the top of `core/mind.py`. The first balance of unit
  two made existing cost more than a perfect forager could gather, so
  starving killed most beings in their first generation and survival was
  luck. The current balance lets a good forager sustain and a bad one not.
- Carving thresholds: at least two views; at least four lived members per
  side and 0.8 agreement on each, purer together than what they were cut
  from, or one side of six or more at 0.9 that is 0.15 purer than its
  scope; below 0.75 a doubted category dissolves; two children that lean
  the same way and agree together at 0.8 are undone.
- Surprise triggers an utterance: the first consequence ever, a consequence
  that betrays the category it landed in, a twin with opposite sign, and a
  dissolved category.
- Teachers' remarks are English for the transcript. The mind reads only
  proposals and doubts.

## Vocabulary

The code uses human words for the reader's sake: life, energy, hunger,
hurt, puzzle, category, being. The system does not see these names. What
it sees is a sign, a number, a coined syllable string, and what happened.
The words are not claims: a being that rests when hungry is not said to
feel hungry, and a lineage that avoids harm is not said to choose to.
