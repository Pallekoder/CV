# The first units

A system meant to grow meaning from the bottom up, over many iterations,
with one hard-coded truth: positives and negatives exist. Everything else
is left for it to build, revise, and own.

This repository holds the first two units. Unit one is the irreducible
floor and the first moment. Unit two is the many: a population in which
consequence decides what is still around. It runs, it is tested, and it is
small on purpose.

    python run.py                                 # one mind, the seed space, the first moment
    python run.py --generations 3                 # carry it on through fresh shells
    python run.py --beings 12 --generations 20    # the many
    python run.py --watch 3                       # follow one being tick by tick
    python run.py --god "..."                     # say something to them (rarely answered)
    python run.py --fresh                         # throw the saved world away
    python compare.py --seed 2                    # children of survivors against strangers
    python -m unittest -v                         # the tests

The runner prints a transcript written for you, the distant one. The minds
never see those words; they see numbers, coined syllables, and consequence.
`DESIGN.md` holds the philosophy, the decisions, and the answers to the
first review.

## Layout

    core/            the value-and-consequence core; persists across shells
      valence.py     the one truth: a sign exists. Nothing else.
      ledger.py      append-only, hash-chained; what happened, happened
      channel.py     the open bucket, and the categories carved out of it
      mind.py        a body, heritable tendencies, and the tick:
                     upkeep, reflect, notice, choose, act, utter-and-forget, consider
      teachers.py    peer perspectives; read-only access, never decrees
      god.py         the rare contact; can also throw the shell away
      being.py       a ledger, a channel, a mind, and where it came from
      many.py        the population: the dead are sealed, the living beget
      symbols.py     the system's own names: syllables hashed from state
      persist.py     carry the world between runs
    shell/           disposable; cheap; meant to be rebuilt
      space.py       forms with an unnamed surface and a hidden consequence
      seed.py        the hidden law, the first moment, a scatter space
    run.py           one run, one or many beings, a transcript
    compare.py       the experiment: did being around change anything?
    tests/           what the units guarantee

## What is fixed and what is not

Fixed, and enforced in code:

- Valence has a sign. A shell that cannot produce both signs is refused.
- The ledger is append-only. Nothing in it can be edited or removed. A
  child's first entry names its parent's chain, so generations link by hash.
- A consumed form is gone. Only its id remains.
- Life lost, to a negative or to starving, never returns.
- Every tendency a being is born with may have either sign. A mind can be
  born drawn toward what hurt it. No preference for positive over negative
  is coded anywhere, and nothing ranks the living: being alive at the end
  of a generation is the whole of what it takes to beget, and every
  survivor is as likely a parent as any other.
- Teachers receive a read-only view and return a perspective. They cannot
  carve, dissolve, or write.
- The distant one is rate-limited. Its words land as a featureless
  experience, the same way the mind's own forgotten utterances do.
- Nothing is carved on one view. Nothing is carved that lived consequence
  does not support.
- Every name the system gives anything is coined from its own state.

Not fixed, and meant to be revised, by you or eventually by the system:

- All magnitudes: starting life and energy, what existing costs, what acting
  costs, how fast starving takes life, how far a consequence echoes, how
  much a child varies, purity thresholds, the gap between contacts.
- The shape of the tendencies. Five numbers (novelty, echo, kin, bold,
  heat) weigh the acts. The five are hand-chosen; their values are not.
- The teachers. Three kinds exist, and they are hand-made.
- The shells, and the hidden law. See the caveat below.

## What a run shows

**The first moment.** In the seed space the mind's first act is noticing: it
sees two forms that are nearly the same and two that are exactly the same.
Its first consequence surprises it; it utters a coined sound and writes
down only the sound. On the next tick it finds that sound in its own ledger
with no cause anywhere in what it has lived, and holds it as a puzzle. When
it lives the second of the identical pair and the consequence is opposite,
that is the paradox, and no teacher can offer a surface rule that survives
it.

**Carving.** Carried into a larger shell, the open bucket fills, a first
carve along the wrong axis is betrayed and dissolved, and a later carve
along the law's axis holds. The paradox pair keeps agreement below perfect
forever. This is a sanity check that the machinery works, not growth: the
law was put there.

**The many.** Twenty-four beings, twenty generations, each in its own shell.
Negatives take life. Existing costs energy, and only positives supply it.
Those whose life runs out are sealed and replaced by children of whoever is
left, with varied tendencies and the parent's lived material. The share of
consumes that hit a negative, across the whole population:

| seed | generation 1 | generation 19 |
|---|---|---|
| 0 | 42% | 27% |
| 1 | 43% | 25% |
| 2 | 62% | 9% |

Then one generation in identical fresh shells, children of the survivors
against the same number of strangers:

| seed | life lost to negatives, each | still alive |
|---|---|---|
| 0 | 1.50 vs 3.68 | 24/24 vs 16/24 |
| 1 | 2.70 vs 3.33 | 23/24 vs 22/24 |
| 2 | 0.87 vs 4.30 | 24/24 vs 10/24 |

Nobody told them to avoid harm. The ones who did not are not around, and
their children carry what the survivors had. `python compare.py --seed N`
reproduces each row in under a minute.

Two honest caveats. The children carry the parent's channel as well as its
tendencies, so this compares lineages with strangers, not tendencies alone.
And with twenty-four beings a single family often takes over the population
within ten generations, so which particular tendency values the survivors
end up with differs from seed to seed. What is consistent across seeds is
the behaviour, not the numbers behind it.

## What this does not do

It does not learn within a life; only lineages change. It does not name its
puzzles or its categories in any way you can read. It has one hidden law
per world, hand-made teachers, separate shells for each being, and no way
to change its own code. Those are next, and `DESIGN.md` says which first.
