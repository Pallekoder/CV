# The first unit

A system meant to grow meaning from the bottom up, over many iterations, with
one hard-coded truth: positives and negatives exist. Everything else is left
for it to build, revise, and own.

This repository holds the first unit: the irreducible floor and the first
moment. It runs, it is tested, and it is small on purpose.

    python run.py              # a new core in the seed space: the first moment
    python run.py --ticks 40   # carry the saved core into a fresh, larger shell
    python run.py --god "..."  # say something to it (rarely answered)
    python run.py --fresh      # throw the saved core away and begin again
    python -m unittest -v      # the tests

The runner prints a transcript written for you, the distant one. The mind
never sees those words; it sees numbers, coined syllables, and consequence.
`DESIGN.md` holds the philosophy and the decisions.

## Layout

    core/            the value-and-consequence core; persists across shells
      valence.py     the one truth: a sign exists. Nothing else.
      ledger.py      append-only, hash-chained; what happened, happened
      channel.py     the open bucket, and the categories carved out of it
      mind.py        notice, choose, act, utter-and-forget, reflect, consider
      teachers.py    peer perspectives; read-only access, never decrees
      god.py         the rare contact; can also throw the shell away
      symbols.py     the system's own names: syllables hashed from state
      persist.py     carry the core between shells
    shell/           disposable; cheap; meant to be rebuilt
      space.py       forms with an unnamed surface and a hidden consequence
      seed.py        the hidden law, the first moment, a scatter space
    run.py           one run, one shell, a transcript
    tests/           what the first unit guarantees

## What is fixed and what is not

Fixed, and enforced in code:

- Valence has a sign. A shell that cannot produce both signs is refused.
- The ledger is append-only. Nothing in it can be edited or removed.
- A consumed form is gone. Only its id remains.
- Life lost to negatives never returns.
- Teachers receive a read-only view and return a perspective. They cannot
  carve, dissolve, or write.
- The distant one is rate-limited. Its words land as a featureless
  experience, the same way the mind's own forgotten utterances do.
- Nothing is carved on one view. Nothing is carved that lived consequence
  does not support.
- Every name the system gives anything is coined from its own state.

Not fixed, and meant to be revised, by you or eventually by the system:

- All magnitudes: starting life, energy, costs, regeneration, purity
  thresholds, the gap between contacts.
- The choosing policy. Right now it is curiosity only: go where nothing has
  been lived and where no category reaches. There is no preference for
  positive over negative anywhere in the code. The body's physics are the
  only orientation. This is deliberate for unit one and is the most
  important open question for unit two.
- The teachers. Three kinds exist. More kinds, and disagreement among them,
  is where this is meant to grow.
- The shells. `first` and `scatter` are the only two. Build more, throw them
  away.

## What a run shows

In the seed space the mind's first act is noticing: it sees two forms that
are nearly the same and two that are exactly the same. Its first touch is
its first consequence, which surprises it; it utters a coined sound and
writes down only the sound. On the next tick it finds that sound in its own
ledger with no cause anywhere in what it has lived, and holds it as a
puzzle. When it touches the second of the identical pair and the consequence
is opposite, that is the paradox lived, and no teacher can offer a surface
rule that survives it.

Carried into a larger shell, the open bucket fills, a first carve along the
wrong axis is betrayed and dissolved, and a second carve along the hidden
law's axis holds. The paradox pair keeps agreement below perfect forever.
Every negative lived takes life that does not come back.

## What this unit does not do

It does not learn to choose. It does not name its puzzles or its categories
in any way you can read. It does not have more than one mind, more than one
law per world, or any way to change its own code. Those are next.
