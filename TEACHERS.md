# Teachers

*For review. Nothing in this file is on until it is switched on, and
what the teachers actually are has not been specified by the distant one.
This file says what the mechanism does, what the one placeholder teacher
says, and what remains to be decided.*

## Why this file exists

Units one to four had the mind consult six teachers on every tick that
something new was lived, and carve categories only on their proposals.
The teachers were the mind's eyes; without them nothing was carved. That
was something to lean on, which the brief and the distant one both rule
out. It has been removed. The mind now finds its own cuts along every axis
it perceives, doubts its own categories, and narrows and undoes on its
own. Teachers are visitors, and no one visits by default.

## What a teacher is here

- A visitor. When visits are switched on, a teacher comes about once every
  N ticks and never twice within N/2, drawn from a stream of its own so
  that switching visits on changes nothing else about a run.
- It looks at the open bucket through a read-only view. It cannot write,
  carve, dissolve, or touch the body.
- It leaves one perspective: a remark in human language for the transcript,
  and at most one proposed cut.
- The mind keeps the perspective and weighs the proposed cut as one
  candidate among the cuts it found itself, by the same rules, by lived
  consequence. A visitor's cut is carved only if it holds better than the
  mind's own.
- Every visit is in the being's ledger as a `visit` entry, in the transcript
  as "a visitor, ...", and in `view.py` in the being's history and as a
  count in its row.

## What a teacher is not

- Not required. The mind carves, narrows, doubts and undoes with no teacher
  at all; the notebook's unit five checks that growth is the same without
  them.
- Not on a schedule the mind could rely on. The gap between visits is
  random above a floor.
- Not a decree. A proposal that consequence does not support is dropped.
- Not an instruction. A teacher never says what to do; it says how it sees
  the open bucket.

## The one teacher that exists, as a placeholder

**nearness.** Looks at pairs, which the mind does not do on its own. It
finds the two closest lived experiences with opposite consequences. If they
are apart, it proposes the axis along which they differ most. If they are
the same on every surface, it says so and proposes nothing. Its remark
when it sees the paradox pair: "#a and #b are the same on every surface
and opposite in consequence. Nothing you can see tells them apart."

## Switching visits on

    python run.py --beings 12 --generations 20 --law corner --visits 30
    python compare.py --seed 0 --visits 30

The rate is kept with the world; a continued world keeps the rate it was
founded with.

## What is not decided

- Which teachers, if any. The nearness teacher is an example of the
  mechanism, not a proposal for what teachers should be.
- How rare. The floor is N/2 ticks between visits; N is a flag.
- Whether a visit should carry a remark the transcript can read, or arrive
  as the distant one's words do, unexplained.
- Whether a teacher should ever propose a cut at all, or only remark.
