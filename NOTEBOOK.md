# Notebook

The discipline from the brief: before each run, write what it will do.
After it, write what it did and where the prediction was wrong. The
surprises are the learning. An entry is never edited after its run; a
correction is a new entry.

The first two units were run before this notebook existed. Their entries
are reconstructed from the session and say so.

## Unit one: the floor and the first moment (reconstructed)

**Expected.** The seed space would make the mind notice the identical pair
first, touch, be surprised, utter, forget, and find its own sound the next
tick. Carried into a second shell, it would carve categories.

**Happened.** The first moment went as expected. In the second shell nothing
was carved at all.

**Surprises.** Each shell had drawn its own hidden law, so what shell one
taught contradicted shell two, and no rule could satisfy both. One law per
world fixed it. Also, the axis teachers' midpoint-of-means threshold was too
crude to find a clean line even when one existed; a best-line search fixed
that. Neither had been anticipated.

## Unit two: the many (reconstructed)

**Expected.** With tendencies whose signs are random at birth, selection
would favour a positive echo weight (go toward what nearby consequences
were), since that is the obvious way to avoid negatives.

**Happened, first balance.** In seed 0 one family swept the population by
generation 10 with a strongly negative echo weight, the opposite of the
prediction. Death ages clustered at 31 to 40 ticks.

**Surprises.** Two. Starving took 60 percent of all life lost: existing cost
more per generation than a perfect forager could gather, so survival was
luck and selection could not act. And the paradox pair, two forms at the
same point with opposite consequences, is the strongest exact echo in the
whole space and it lies: a mind that distrusts the exact echo avoids the
twin trap. Nobody designed that lesson; the shell taught it.

**Happened, rebalanced.** Across three seeds the share of consumes that hit
a negative fell from 42, 43 and 62 percent to 27, 25 and 9 percent, and
children of survivors lost less than half the life strangers lost in
identical shells. Which tendency values the survivors carried differed by
seed; in seed 2 they became cautious touchers with almost no heat, a
strategy not anticipated. The behaviour was consistent; the numbers behind
it were not.

## Unit three: the body enters the choice

Written before reading the results of the three-seed run of `compare.py`
with 24 beings and 20 generations. Disclosed: before writing this, a
12-being seed-0 run to generation 5 had shown hungry +12/-0, hurt +1/-11,
plasticity +11/-1 among the living, and seed 0 of the 24-being run had
been glimpsed through generation 14 with the negative-consume share
between 32 and 44 percent, not clearly falling.

**Predictions.**

1. `hungry` ends positive in the majority of the living in all three seeds:
   when energy is low, acting beats resting because resting starves.
2. `plasticity` ends positive in the majority in at least two of three
   seeds: bending toward what predicted correctly should help.
3. `hurt` has no consistent sign across seeds; it will go with whichever
   family sweeps.
4. Children of survivors lose less life than strangers in all three seeds,
   by at least as wide a margin as in unit two.
5. Hungry children of survivors rest less per being than hungry strangers
   in at least two of three seeds.
6. Life bends the living by between 0.3 and 1.0 on average per bendable
   tendency, because the bending accumulates over a hundred or more acts.
7. The negative-consume share falls in seeds 1 and 2 as in unit two; in
   seed 0 it ends above 25 percent, less cleanly than before.

**Results.** Seeds 0, 1, 2, in order.

| | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| hungry, sign among the living | +23/-1 | +7/-17 | +21/-3 |
| hurt | +17/-7 | +22/-2 | +0/-24 |
| plasticity | +0/-24 | +11/-13 | +24/-0 |
| bent by life, mean | 0.63 | 0.26 | 0.91 |
| negative consumes, generation 1 to 19 | 41% to 28% | 44% to 37% | 61% to 35% |
| life lost, children vs strangers | 2.43 vs 3.50 | 4.21 vs 2.94 | 3.51 vs 4.09 |
| alive, children vs strangers | 21 vs 15 | 23 vs 23 | 19 vs 10 |
| hungry: acts per being, children vs strangers | 16.4 vs 8.5 | 18.1 vs 7.8 | 9.2 vs 3.2 |
| hungry: alive, children vs strangers | 15 vs 7 | 18 vs 6 | 15 vs 1 |

Scored against the predictions:

1. Wrong in seed 1, where the living are mostly hungry-negative.
2. Wrong. Only seed 2 is plasticity-positive. Seed 0 is entirely negative.
3. Right, for what a prediction of inconsistency is worth.
4. Wrong. In seed 1 the children lose more life than strangers, and in
   every seed the margin is narrower than unit two's (1.50 vs 3.68,
   2.70 vs 3.33, 0.87 vs 4.30).
5. Wrong as written, and the measure was bad: a stranger that dies early
   stops resting. By acts and by survival, hungry children do far better in
   all three seeds.
6. Right in two seeds; seed 1 bent less.
7. Half right. Every seed fell less than in unit two; seed 1 barely fell.

**Surprises, and what they seem to mean.**

Negative plasticity won outright in seed 0. In this rule, negative
plasticity shrinks every tendency that led to a good outcome. A being born
trusting its categories eats the sure positives, and each success winds its
drives down toward rest. Resting is nearly free in this world and the forms
left late in a shell are disproportionately the bad ones, so winding down
after wins protects life. Those children rest 32 ticks of 54 and lose less
life than strangers. The knob I added as "learning" was used as a damper:
quit while ahead. Nobody put that there.

Seed 1's lineage never rests, consumes eighteen forms a generation, loses
more life than strangers, and survives by gathering so much energy that
starving never threatens it. It solved the fast killer, not the slow one.

Across all three seeds the harm-avoidance margin is narrower than in unit
two. The suspicion: the hunger knob gave lineages a cheaper way to survive
than learning what hurts. In unit two, the only way to not starve was to
target positives, which also meant avoiding negatives. Now a being can
simply act more when hungry. Richer, and worse at the thing that mattered.
The random draws also changed between units, so this could be variance.
That is the next run.

## Unit three, second run: are the knobs the cause?

Written before running. Six seeds (0 to 5), 24 beings, 20 generations,
twice each: once with hungry, hurt and plasticity held at zero, which
reproduces unit two's policy on the same founders and shells, and once
free. The draws are paired, so only the knobs differ.

**Predictions.**

1. Frozen: children lose less life than strangers in at least five of six
   seeds.
2. Free: in at most four of six.
3. The mean margin (strangers' loss minus children's) is larger frozen
   than free.
4. Free: plasticity ends negative-majority in at least two of six seeds.
5. Free: hungry ends positive-majority in at least four of six seeds.

**Results.** Children of survivors against strangers, one generation in
identical fresh shells, life lost each; margin is strangers' loss minus
children's.

| seed | frozen: margin | free: margin | free: hungry | free: hurt | free: plasticity |
|---|---|---|---|---|---|
| 0 | -0.83 | +1.07 | +23/-1 | +17/-7 | +0/-24 |
| 1 | -0.21 | -1.27 | +7/-17 | +22/-2 | +11/-13 |
| 2 | +2.73 | +0.58 | +21/-3 | +0/-24 | +24/-0 |
| 3 | -0.61 | +2.14 | +20/-4 | +24/-0 | +0/-24 |
| 4 | +2.93 | +1.12 | +2/-22 | +24/-0 | +1/-23 |
| 5 | +1.40 | +1.27 | +3/-21 | +22/-2 | +14/-10 |

Frozen: children lose less in 3 of 6 seeds, mean margin +0.90. Free: 5 of
6, mean margin +0.82.

Scored against the predictions:

1. Wrong. Three of six, not five.
2. Wrong. Five of six, not at most four.
3. Right by a hair, +0.90 against +0.82, which is nothing.
4. Right. Plasticity swept negative in seeds 0, 3 and 4.
5. Wrong. Hungry ended positive-majority in three seeds, not four or more.

**What it means.** The knobs did not narrow the margins. On the same
founders and the same shells, the two policies come out about even: the
free one wins more often by less, the frozen one wins bigger and loses
bigger. Unit two's three clean wins were the luck of three draws, and the
previous entry's "richer, and worse at the thing that mattered" was a
conclusion drawn from variance. The lesson is about method, not minds:
three seeds of twenty-four cannot carry a claim about a knob, and the
paired control is the cheapest way to find that out. One thing did hold
up: the damper. Plasticity was selected entirely negative in three of six
free worlds, each time with the same winding-down behaviour.

## Unit four: narrowing, and a world that needs it

Categories can now narrow: a category whose members disagree is offered a
chance to split along another axis into two children before it can be
doubted, and an arrival lands in the deepest category that admits it. A
new kind of hidden law, `corner`, makes a form positive only if it clears
thresholds on two axes at once, so no single cut can sort it. `view.py`
shows the open bucket, the tree, and the history of carving, narrowing and
dissolving, per being and as growth by generation.

Written before the first corner run: seed 0, 12 beings, 20 generations.

**Predictions.**

1. By generation 10, at least half the living beings hold a tree of depth
   two or more that is still standing.
2. In most lineages the first root carve lies along one of the law's two
   axes.
3. After generation 5, narrowings average at least one per generation
   across the population.
4. The corner world is harsher, since positives are rarer: fewer than 7 of
   12 survive a generation on average.
5. Categories per living being settle between 3 and 8.
6. Somewhere a tree reaches depth 3 by generation 19, from noise or the
   paradox pair rather than the law, since the law needs only two cuts.

**Results.** Seed 0; the law turned out to be axis 2 >= -0.203 and
axis 1 >= -0.216.

| generation | survived of 12 | categories per being | deepest | narrowed | dissolved |
|---|---|---|---|---|---|
| 1 | 2 | 3.6 | 4 | 9 | 11 |
| 5 | 1 | 5.2 | 4 | 1 | 0 |
| 10 | 1 | 21.5 | 7 | 8 | 4 |
| 15 | 4 | 37.3 | 8 | 15 | 14 |
| 19 | 8 | 46.6 | 9 | 20 | 14 |

Scored against the predictions:

1. Right. All twelve living hold trees of depth two or more; by generation
   10 the deepest was seven.
2. Right at the top. The inherited roots cut axis 2 near -0.40 and the
   level below cuts axis 1 near -0.45: the law's two axes. No living being
   carved a root itself; every root was inherited from generation 1.
3. Right. Narrowings every generation, between 5 and 26.
4. Right, far beyond what was predicted: one or two of twelve survived
   most generations until generation 15. One lineage carried the world.
5. Wrong by an order of magnitude: 46 categories per being.
6. Right, trivially: depth 9.

**Surprise.** The tree is a thicket. Two members that agree count as a
pure side, so any four points split two and two along some axis, and
narrowing runs down into sample noise. The paradox twins, who can never be
parted, keep every category that holds them impure and so keep inviting
one more cut. Children inherit the whole thicket. Nothing undoes a cut
that separates nothing: dissolution only reaches leaves below 0.75
agreement, and a two-member leaf at 1.00 lives forever. The top of the
tree found the law; everything under it is noise wearing the law's
clothes. `view.py --being` shows it plainly, which is what the viewer is
for.

## Unit four, second run: restraint

Two changes, both of the same kind as the rules already there: a cut must
be supported by consequence. First, a side now needs at least four lived
members, and a two-sided cut must leave its material purer than it found
it. Second, a narrowing whose children no longer part consequence (both
children lean the same way and together they agree) is undone, and the
members fall back to the parent. Nothing else changes. Written before the
rerun of the same corner world: seed 0, 12 beings, 20 generations.

**Predictions.**

1. Categories per living being at generation 19 between 4 and 12.
2. The deepest tree at generation 19 is 4 or less.
3. In most living beings the top two levels lie on the law's two axes.
4. Leaves' agreement averages above 0.8.
5. Survival is unchanged within noise, since the world and not the channel
   decides it: fewer than 4 of 12 survive a generation on average.

**Results.** Same seed, same law.

| generation | survived of 12 | categories per being | deepest | narrowed | dissolved | undone |
|---|---|---|---|---|---|---|
| 1 | 1 | 2.4 | 2 | 4 | 11 | 0 |
| 5 | 6 | 4.0 | 2 | 0 | 0 | 0 |
| 10 | 6 | 4.5 | 4 | 0 | 0 | 0 |
| 15 | 11 | 7.6 | 4 | 13 | 1 | 0 |
| 19 | 9 | 7.8 | 3 | 1 | 1 | 0 |

Scored against the predictions:

1. Right: 7 to 9 per living being.
2. Right: depth 3 in every living being.
3. Right: 12 of 12 have their top two levels on the law's axes. The
   commonest tree cuts axis 1 at -0.233 and then axis 2 at -0.204, against
   a law of -0.216 and -0.203.
4. Right: 0.90 over 55 leaves.
5. Wrong: survival rose, from 1 of 12 at generation 1 to 6 by generation 5
   and 11 by generation 15. Whether sane categories fed the kin tendency
   or the draws simply differed is not settled by one run; a prediction
   that said "unchanged" was wrong either way.

**What it means.** Restraint of the kind the brief already demands, that
consequence must support a cut, turned the thicket into something that can
be read: a corner found in two cuts, agreed on across the whole
population, with a few stale leaves beneath. The undo rule never fired; the
thicket had been made of cuts that the sample rule now stops at the
source. The viewer shows the thing the brief calls growth. Open: whether
survival rose because of it.
