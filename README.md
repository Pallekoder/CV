---
title: The world
emoji: "●"
colorFrom: purple
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
---

# Growing minds from almost nothing

Read `BRIEF.md` first. It is the project, in the words it was handed over
in, and the code is measured against it. `NOTEBOOK.md` holds the
predictions written before each run and what happened instead; the
surprises there are the point. `DESIGN.md` says how each piece of the
brief is built, where the build adds things the brief does not ask for,
and what the brief asks for that is not built yet. `TEACHERS.md` is for
review: what a teacher is and is not here, and what is still undecided.

This file says what exists and how to run it.

## The window

    python serve.py --open            # starts the world and opens the page
    python serve.py --fresh --beings 12 --law corner --speed 4

The world runs inside that process for as long as it runs, generation
after generation, and saves itself at the end of every generation, so a
restart resumes where it was. Leave it running and come back; closing
the terminal stops it, and the next start continues from the last
finished generation. The page
shows every being as a creature sized by its life and coloured by its
energy, with its last act; the selected being's space, with what it has
lived as green and red dots, the forms still there, and its categories
drawn as boxes on any two axes you choose; its channel as a table, with
sub-categories indented and inherited ones marked; the history of its
cuts; its last ticks; and the generations so far. The controls: play,
pause, step one tick, a speed dial from one tick every twenty seconds to
a thousand a second, how often teachers visit (zero is never), a line to
say something to all who live, and a form to begin a new world.

    python run.py                                 # one mind, the seed space, the first moment
    python run.py --generations 3                 # carry it on through fresh shells
    python run.py --beings 12 --generations 20    # the many
    python run.py --beings 12 --generations 20 --law corner   # a world whose law needs two cuts
    python view.py                                # every living being's channel in one row, then growth by generation
    python view.py --being 3                      # one being: open bucket, category tree, history of carving
    python run.py --beings 12 --generations 20 --visits 30     # let a teacher visit, about every 30 ticks
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

**Five: the teachers were a crutch.** Until this unit the mind consulted
six teachers on every tick and could not carve without their proposals.
Now it finds its own cuts along every axis it perceives and doubts its own
categories. Teachers are visitors: off unless switched on, rare and
irregular when on, each visit recorded, each leaving at most one proposed
cut that is weighed exactly like the mind's own. One placeholder teacher
exists. The check that growth does not depend on them found an older bug
(see the notebook), fixed here: a child's own acts had been overwriting
inherited experiences that shared an index.

**Four: narrowing, and a way to see it.** A category whose members
disagree can split along another axis into two more specific children; an
arrival lands in the deepest category that admits it; a cut that no longer
parts consequence is undone. A `corner` law, positive only when two axes
both clear a threshold, makes narrowing necessary. `view.py` shows the open
bucket, each tree, the history of every cut, and growth by generation.

## Layout

    core/            the value-and-consequence core; persists across shells
      valence.py     the one truth: a sign exists. Nothing else.
      ledger.py      append-only, hash-chained; what happened, happened
      channel.py     the open bucket, the categories carved out of it, and their narrowing
      mind.py        a body, heritable tendencies, and the tick:
                     upkeep, reflect, notice, choose, act, bend, utter-and-forget, consider
      teachers.py    teachers as rare visitors, off by default; see TEACHERS.md
      god.py         the rare contact; can also throw the shell away
      being.py       a ledger, a channel, a mind, and where it came from
      many.py        the population: the dead are sealed, the living beget
      symbols.py     the system's own names: syllables hashed from state
      persist.py     carry the world between runs
    shell/           disposable; cheap; meant to be rebuilt
      space.py       forms with an unnamed surface and a hidden consequence
      seed.py        the hidden law, the first moment, a scatter space
    run.py           one run, one or many beings, a transcript
    serve.py         the window: a world that keeps running, watched in a browser
    ui/index.html    the page the window serves
    view.py          look into the channels: boxes, trees, histories, growth
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
- No teacher is on unless switched on. When on, a teacher visits rarely
  and irregularly, sees the open bucket through a read-only view, and
  leaves a remark and at most one proposed cut, weighed like the mind's
  own. The mind finds its own cuts and doubts its own categories; it never
  waits for a teacher and never carves because of one.
- The distant one is rate-limited. Its words land as a featureless
  experience, the same way the mind's own forgotten utterances do.
- Nothing is carved on one view. Nothing is carved that lived consequence
  does not support: a side needs enough lived members, a cut must leave
  its material purer than it found it, a category is doubted only after it
  has had its chance to narrow, and a cut whose two sides no longer differ
  in consequence is undone.
- Every name the system gives anything is coined from its own state.

Not fixed, and meant to be revised, by you or eventually by the system:

- All magnitudes: starting life and energy, what existing costs, what acting
  costs, how fast starving takes life, how far a consequence echoes, how
  much a child varies, how far a tendency can bend, purity thresholds, the
  gap between contacts.
- The shape of the tendencies. Eight numbers weigh the acts. The eight
  slots and the bending rule's form are hand-chosen; their values and
  signs are not.
- The teachers. What they should be is undecided and the distant one's to
  decide; one placeholder exists, and visits are off by default.
- The shells, and the hidden law.

## What the runs showed

The full record, with the predictions that preceded each run, is in
`NOTEBOOK.md`. In short:

**The first moment** goes as designed: the first act is noticing the
identical pair; the first consequence is a surprise; the sound is written
and the why is not; the next tick finds the sound with no cause and holds
it as a puzzle; the paradox is lived and no surface rule survives it.

**The many** (unit two's policy on the fixed code: six seeds, 24 beings,
20 generations, no teacher): in four of the six worlds the share of
consumes that hit a negative fell by more than half over the generations
(60 to 21 percent, 43 to 13, 52 to 18, 62 to 36), and children of
survivors lost less than half the life that strangers lost in identical
fresh shells (1.84 against 3.99, 1.00 against 4.04, 1.89 against 4.69,
1.78 against 3.84). In the other two worlds lineages did no better than
strangers. In all six, more children than strangers were still alive at
the end. Nobody told them to avoid harm.

**The body in the choice** (unit three's knobs, same seeds, paired on the
same founders and shells): hungry children of survivors act about twice as
much as hungry strangers and survive far better. On harm avoidance the
knobs cost something: the children's mean edge over strangers is +0.66
with them and +1.49 without, and the share of harmful consumes falls less.
Three earlier verdicts on this question, in the notebook, were drawn from
three seeds, then from corrupted inheritance; this is the one on intact
inheritance, and it is six seeds. In three of six free worlds the bending
knob was selected entirely negative, winding a being's drives down after
each success; nobody offered it as a damper.

**Narrowing** (a corner world, 12 beings, 20 generations, no teacher):
the first versions grew thickets, then showed trees that turned out to
have been computed on corrupted inheritance (the notebook has both). On
the fixed code, in a corner world where about half of what is eaten is
positive, every living being holds the same four-category tree by
generation 5: a cut on one of the law's axes, then a cut on the other
inside the side that needed it, leaf agreement 0.97, and nothing further
to carve. `python view.py --being 0` on such a world shows the tree.

**What selection does in a famine.** With the corner's thresholds set so
that seven in ten things eaten hurt, every forager died inside its first
generation; the beings that remained acted less than once a generation
and begot children born fed. The ones who are around are the ones who do
nothing. Whether begetting should cost the parent something is an open
decision, recorded in the notebook and `DESIGN.md`.

Two things stay true of all of this, and the brief says to keep them in
view: selection is not choosing, and richness is not experience. The
lineages that avoid harm were not told to and do not know that they do.

## What the brief asks for that is not built

- The channel defines its own dimensions of experience. Here the axes are
  still the shell's; the system carves and narrows along them but does not
  make them.
- The puzzle is held, not worked on. Nothing yet tries to account for the
  forgotten sound.
- The late game: a flood of raw knowledge dropped on a grown system.
