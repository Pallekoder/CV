# Growing minds from almost nothing

Read `BRIEF.md` first. It is the project, in the words it was handed over
in, and the code is measured against it. `NOTEBOOK.md` holds the
predictions written before each run and what happened instead; the
surprises there are the point. `DESIGN.md` says how each piece of the
brief is built, where the build adds things the brief does not ask for,
and what the brief asks for that is not built yet.

This file says what exists and how to run it.

    python run.py                                 # one mind, the seed space, the first moment
    python run.py --generations 3                 # carry it on through fresh shells
    python run.py --beings 12 --generations 20    # the many
    python run.py --watch 3                       # follow one being tick by tick
    python run.py --god "..."                     # say something to them (rarely answered)
    python run.py --fresh                         # throw the saved world away
    python compare.py --seed 2                    # children of survivors against strangers
    python compare.py --seed 2 --frozen hungry,hurt,plasticity   # the same, with unit three's knobs held at zero
    python -m unittest -v                         # the tests

The runner prints a transcript written for you, the distant one. The minds
never see those words; they see numbers, coined syllables, and consequence.

## The units so far

**One: the floor and the first moment.** The one truth, an append-only
ledger, a space of forms with a hidden consequence, the open channel and
the carving of categories, peer teachers, the rare contact, and the seed:
contrast, a sound uttered and forgotten, a puzzle held.

**Two: the many.** Tendencies with random signs at birth. A body that
existing costs. A population in which the dead are sealed and the living
beget, with nothing ranking them.

**Three: the body enters the choice.** Two more tendencies read hunger and
injury, and a third lets lived consequence bend the others within a life.
All three are inherited and unsigned at birth. A control holds them at
zero so a world with and without them can be compared on the same
founders and shells.

## Layout

    core/            the value-and-consequence core; persists across shells
      valence.py     the one truth: a sign exists. Nothing else.
      ledger.py      append-only, hash-chained; what happened, happened
      channel.py     the open bucket, and the categories carved out of it
      mind.py        a body, heritable tendencies, and the tick:
                     upkeep, reflect, notice, choose, act, bend, utter-and-forget, consider
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
- Every tendency a being is born with may have either sign, including the
  ones that read the body and the one that bends the others. No preference
  for positive over negative is coded anywhere. Nothing ranks the living:
  being alive at the end of a generation is the whole of what it takes to
  beget, and every survivor is as likely a parent as any other.
- A child inherits what its parent was born as, never what life bent.
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
  much a child varies, how far a tendency can bend, purity thresholds, the
  gap between contacts.
- The shape of the tendencies. Eight numbers weigh the acts. The eight
  slots and the bending rule's form are hand-chosen; their values and
  signs are not.
- The teachers. Three kinds exist, and they are hand-made.
- The shells, and the hidden law.

## What the runs showed

The full record, with the predictions that preceded each run, is in
`NOTEBOOK.md`. In short:

**The first moment** goes as designed: the first act is noticing the
identical pair; the first consequence is a surprise; the sound is written
and the why is not; the next tick finds the sound with no cause and holds
it as a puzzle; the paradox is lived and no surface rule survives it.

**The many** (unit two, 24 beings, 20 generations, three seeds): the share
of consumes that hit a negative fell from 42, 43 and 62 percent to 27, 25
and 9 percent. Children of survivors lost less than half the life that
strangers lost in identical fresh shells. Nobody told them to avoid harm.

**The body in the choice** (unit three, same setup): hungry children of
survivors act about twice as much as hungry strangers and survive far
better. But the harm-avoidance margin is narrower than unit two's in every
seed, and in one seed the children lose more life than strangers. In one
seed the bending knob was selected entirely negative and used as a damper,
winding a being's drives down after each success so it rests before the
bad forms are all that is left. Richer was not better at the thing that
mattered. Whether the knobs themselves are the cause is the paired
experiment recorded in the notebook.

Two things stay true of all of this, and the brief says to keep them in
view: selection is not choosing, and richness is not experience. The
lineages that avoid harm were not told to and do not know that they do.

## What the brief asks for that is not built

- The channel defines its own dimensions of experience. Here the axes are
  still the shell's; the system carves along them but does not make them.
- The puzzle is held, not worked on. Nothing yet tries to account for the
  forgotten sound.
- The late game: a flood of raw knowledge dropped on a grown system.
