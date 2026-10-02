"""Tests for the first two units. Run with:  python -m unittest -v"""
from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

from core.being import Being
from core.channel import Channel, Experience, Rule
from core.god import God
from core.ledger import Ledger
from core.many import World
from core import mind as mind_module
from core.mind import LIFE_START, Body, Disposition, Mind
from core.persist import load, save
from core.symbols import SYLLABLES, coin
from core.teachers import NearnessTeacher, default_teachers
from core.channel import best_line
from core.valence import TruthViolation, Valence, assert_truth
from shell.seed import build, first_moment, law_for, scatter
from core.channel import purity
from shell.space import Form, Gone, Space

NEUTRAL = dict(novelty=0.0, echo=0.0, kin=0.0, bold=0.0, hungry=0.0, hurt=0.0, heat=0.001, plasticity=0.0)
CAUTIOUS = Disposition(**{**NEUTRAL, "novelty": 1.0, "bold": -1.0, "heat": 0.01})   # touches the new
BOLD = Disposition(**{**NEUTRAL, "novelty": 1.0, "bold": 1.0, "heat": 0.01})        # consumes the new


def make_core(seed: int = 0, dims: int = 4, disposition=None):
    rng = random.Random(seed)
    ledger, channel = Ledger(), Channel()
    god = God(Ledger())   # the distant one keeps the world's record, not the mind's
    mind = Mind(ledger, channel, default_teachers(dims), rng, disposition)
    return ledger, channel, mind, god


def two_form_space() -> Space:
    return Space([Form("bad", (0.0, 0.0), -1.0), Form("good", (1.0, 1.0), +1.0)], dims=2, label="t")


def is_coined(name: str) -> bool:
    return all(part in SYLLABLES for part in name.split("-"))


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


class TheLaw(unittest.TestCase):
    def test_a_corner_law_needs_two_axes(self):
        law = law_for(5, 4, "corner")
        self.assertEqual(law.kind, "corner")
        self.assertNotEqual(law.axis, law.axis2)
        space = first_moment(random.Random(5), law)
        self.assertEqual({f.hidden > 0 for f in space.forms.values()}, {True, False})
        big = scatter(random.Random(5), law)
        signs = [f.hidden > 0 for f in big.forms.values()]
        self.assertTrue(0.2 < sum(signs) / len(signs) < 0.8, "a corner, not a famine and not a feast")
        with self.assertRaises(ValueError):
            law_for(5, 4, "spiral")


class TheOneTruth(unittest.TestCase):
    def test_both_signs_must_be_possible(self):
        with self.assertRaises(TruthViolation):
            assert_truth([0.1, 0.5])
        with self.assertRaises(TruthViolation):
            assert_truth([-0.1])
        assert_truth([-0.1, 0.2])

    def test_a_one_signed_space_is_refused(self):
        with self.assertRaises(TruthViolation):
            Space([Form("a", (0.0,), 0.5), Form("b", (1.0,), 0.4)], dims=1, label="x")

    def test_valence_asserts_only_sign(self):
        self.assertEqual(Valence(0.3).sign, 1)
        self.assertEqual(Valence(-2.0).sign, -1)
        self.assertEqual(Valence(0.0).sign, 0)


class Endless(unittest.TestCase):
    def test_a_ledger_archives_its_past_and_still_verifies(self):
        ledger = Ledger()
        for i in range(10):
            ledger.append(i, "a", n=i)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "record.jsonl"
            self.assertEqual(ledger.archive(path, keep=4), 6)
            lines = path.read_text().splitlines()
            self.assertEqual(len(lines), 6)
            self.assertEqual(json.loads(lines[-1])["hash"], ledger[6].prev_hash)
        self.assertEqual(len(ledger), 10)
        self.assertEqual(ledger.base, 6)
        self.assertTrue(ledger.verify())
        self.assertEqual(ledger[9].payload["n"], 9)
        with self.assertRaises(IndexError):
            ledger[2]
        self.assertEqual([e.payload["n"] for e in ledger.since(8)], [8, 9])
        ledger.append(10, "a", n=10)
        self.assertEqual(len(ledger), 11)
        again = Ledger.from_list(ledger.to_list())
        self.assertTrue(again.verify())
        self.assertEqual(again.base, 6)
        rows = ledger.to_list()
        rows[1]["payload"]["n"] = 99
        with self.assertRaises(ValueError):
            Ledger.from_list(rows)

    def test_a_channel_forgets_its_oldest_and_keeps_its_rules(self):
        channel = lived_channel(30)
        hi, lo = channel.split(Rule(0, 0.0), 1, coin)
        before = len(hi.members) + len(lo.members)
        self.assertEqual(before, 30)
        channel.add(Experience(index=100, tick=2, features=None, token="sound"))
        dropped = channel.forget(keep_lived=10, keep_bare=5)
        self.assertEqual(dropped, 20)
        self.assertEqual(len([e for e in channel.experiences.values() if e.features is not None]), 10)
        self.assertEqual(min(i for i, e in channel.experiences.items() if e.features is not None), 20, "the oldest went")
        self.assertEqual(len(hi.members) + len(lo.members), 10)
        self.assertEqual(set(channel.categories), {hi.name, lo.name}, "rules stay")
        self.assertIn(100, channel.experiences)


class Irreversibility(unittest.TestCase):
    def test_ledger_exposes_no_way_to_edit_or_remove(self):
        public = {n for n in dir(Ledger) if not n.startswith("_")}
        for forbidden in ("remove", "pop", "clear", "edit", "update", "delete", "rewrite"):
            self.assertNotIn(forbidden, public)

    def test_chain_detects_tampering(self):
        ledger = Ledger()
        ledger.append(0, "a", x=1)
        ledger.append(0, "b", x=2)
        self.assertTrue(ledger.verify())
        rows = ledger.to_list()
        rows[0]["payload"]["x"] = 99
        with self.assertRaises(ValueError):
            Ledger.from_list(rows)

    def test_consume_is_final(self):
        space = first_moment(random.Random(1), law_for(1, 4))
        fid = space.perceive()[0][0]
        space.consume(fid)
        self.assertNotIn(fid, [f for f, _ in space.perceive()])
        self.assertEqual(space.tombstones, [fid])
        with self.assertRaises(Gone):
            space.consume(fid)
        with self.assertRaises(Gone):
            space.touch(fid)

    def test_lost_life_never_comes_back(self):
        _, _, mind, _ = make_core()
        space = two_form_space()
        mind.enter(space)
        life0 = mind.body.life
        mind.act(space, "consume", "bad", (0.0, 0.0), 1)
        life1 = mind.body.life
        self.assertLess(life1, life0)
        mind.act(space, "consume", "good", (1.0, 1.0), 2)
        self.assertEqual(mind.body.life, life1)
        self.assertGreater(mind.body.energy, 0)

    def test_existing_costs_and_starving_takes_life(self):
        body = Body(life=10.0, energy=0.05)
        self.assertTrue(body.upkeep())
        self.assertEqual(body.energy, 0.0)
        self.assertLess(body.life, 10.0)
        starved = body.life
        body.live(Valence(+0.5))
        self.assertGreater(body.energy, 0.0)
        self.assertFalse(body.upkeep())
        self.assertEqual(body.life, starved, "a positive feeds; it does not heal")


class TheFirstMoment(unittest.TestCase):
    def test_seed_space_holds_a_parallel_and_a_paradox(self):
        for seed in range(5):
            space = first_moment(random.Random(seed), law_for(seed, 4))
            forms = list(space.forms.values())
            pairs = [(a, b) for i, a in enumerate(forms) for b in forms[i + 1:]]
            identical = [(a, b) for a, b in pairs if a.surface == b.surface]
            near = [(a, b) for a, b in pairs if 0 < dist(a.surface, b.surface) < 0.1]
            self.assertEqual(len(identical), 1, seed)
            self.assertLess(identical[0][0].hidden * identical[0][1].hidden, 0, "paradox: opposite")
            self.assertEqual(len(near), 1, seed)
            self.assertGreater(near[0][0].hidden * near[0][1].hidden, 0, "parallel: alike")

    def test_first_act_is_noticing_difference(self):
        ledger, _, mind, god = make_core()
        space = god.remake(0, lambda: first_moment(random.Random(0), law_for(0, 4)))
        mind.enter(space)
        mind.tick(space)
        kinds = [e.kind for e in ledger]
        self.assertEqual(kinds[0], "enter")
        self.assertEqual(kinds[1], "notice")
        self.assertEqual(len(ledger[1].payload["identical"]), 1)

    def test_utterance_keeps_the_that_and_loses_the_why(self):
        ledger, channel, mind, god = make_core(disposition=CAUTIOUS)
        space = god.remake(0, lambda: first_moment(random.Random(0), law_for(0, 4)))
        mind.enter(space)
        mind.tick(space)
        utterances = ledger.of_kind("utterance")
        self.assertEqual(len(utterances), 1, "the first consequence is a surprise")
        u = utterances[0]
        self.assertEqual(set(u.payload), {"that"}, "nothing but the sound is written")
        self.assertTrue(is_coined(u.payload["that"]))
        self.assertEqual(mind.puzzles, [])
        mind.tick(space)
        self.assertEqual(len(mind.puzzles), 1)
        self.assertEqual(mind.puzzles[0].about, u.index)
        found = channel.experiences[mind.puzzles[0].exp]
        self.assertIsNone(found.features, "it arrived with no surface")
        self.assertEqual(found.token, u.payload["that"])
        self.assertIn(found, channel.open_bucket())

    def test_paradox_is_lived_and_nothing_on_the_surface_resolves_it(self):
        ledger, channel, mind, god = make_core(disposition=BOLD)
        mind.visit_rate = 1   # a visitor every tick, so that the one teacher gets to see the paradox
        space = god.remake(0, lambda: first_moment(random.Random(0), law_for(0, 4)))
        mind.enter(space)
        for _ in range(12):
            mind.tick(space)
        self.assertTrue(space.empty)
        self.assertEqual(channel.categories, {})
        signs = {e.sign for e in channel.experiences.values() if e.sign}
        self.assertEqual(signs, {1, -1}, "both signs were lived")
        twins = [(a, b) for a in channel.experiences.values() for b in channel.experiences.values()
                 if a.index < b.index and a.features and a.features == b.features and a.sign and b.sign and a.sign != b.sign]
        self.assertTrue(twins, "the same surface, opposite consequence, lived")
        nearness = [p for p in mind.perspectives if p.source == "nearness"]
        self.assertTrue(nearness)
        self.assertIn("same on every surface", nearness[-1].remark)


def lived_channel(n: int, law_axis: int = 0, dims: int = 2, seed: int = 0, start: int = 0) -> Channel:
    """A channel whose lived consequences follow a hidden rule on one axis."""
    rng = random.Random(seed)
    channel = Channel()
    for i in range(n):
        f = tuple(round(rng.uniform(-1, 1), 3) for _ in range(dims))
        v = 0.5 if f[law_axis] >= 0 else -0.5
        channel.add(Experience(index=start + i, tick=i, features=f, token=f"f{i}", valence=v))
    return channel


class PeerTeachers(unittest.TestCase):
    def test_teachers_cannot_imprint(self):
        channel = lived_channel(10)
        before = json.dumps(channel.to_dict(), sort_keys=True)
        for teacher in default_teachers(2):
            teacher.regard(channel.view(), 1)
        self.assertEqual(before, json.dumps(channel.to_dict(), sort_keys=True))

    def test_view_is_frozen(self):
        view = Channel().view()
        with self.assertRaises(Exception):
            view.experiences = ()

    def test_the_mind_finds_its_own_best_line(self):
        channel = lived_channel(12)
        rule = best_line(channel.experiences.values(), 0)
        self.assertIsNotNone(rule)
        self.assertEqual(rule.axis, 0)
        self.assertLess(abs(rule.threshold), 0.3)
        self.assertIsNone(best_line([e for e in channel.experiences.values() if e.sign > 0], 0), "one sign: no line")

    def test_the_mind_carves_with_no_teacher_at_all(self):
        ledger = Ledger()
        channel = lived_channel(12)
        mind = Mind(ledger, channel, [], random.Random(0))
        mind.consider(1)
        self.assertEqual(len(channel.categories), 2)
        self.assertEqual(ledger.of_kind("visit"), [])
        self.assertEqual(ledger.of_kind("carve")[0].payload["after"], "own axis 0")

    def test_nobody_visits_unless_switched_on_and_a_visit_is_only_a_candidate(self):
        ledger, channel = Ledger(), Channel()
        quiet = Mind(ledger, channel, default_teachers(2), random.Random(0))
        space = two_form_space()
        quiet.enter(space)
        for _ in range(20):
            quiet.tick(space)
        self.assertEqual(ledger.of_kind("visit"), [], "off by default")
        self.assertEqual(quiet.perspectives, [])

        ledger, channel = Ledger(), Channel()
        visited = Mind(ledger, channel, default_teachers(2), random.Random(0), visit_rate=1)
        space = two_form_space()
        visited.enter(space)
        for _ in range(6):
            visited.tick(space)
        visits = ledger.of_kind("visit")
        self.assertTrue(visits)
        self.assertEqual(len(visited.perspectives), len(visits))
        self.assertTrue(all(v.payload["source"] == "nearness" for v in visits))
        # the channel is the same whether or not anyone visited: a visit changes nothing by itself
        self.assertEqual(visited.channel.categories, {})

    def test_carving_happens_in_the_open_and_is_recorded(self):
        ledger = Ledger()
        channel = lived_channel(12)
        mind = Mind(ledger, channel, default_teachers(2), random.Random(0))
        mind.consider(1)
        self.assertEqual(len(channel.categories), 2)
        for name, cat in channel.categories.items():
            self.assertTrue(is_coined(name), name)
            self.assertEqual(cat.rule.axis, 0)
        all_members = set().union(*(c.members for c in channel.categories.values()))
        self.assertEqual(all_members, set(channel.experiences))
        self.assertEqual(len(ledger.of_kind("carve")), 1)

    def test_a_category_that_can_narrow_narrows(self):
        ledger = Ledger()
        channel = lived_channel(12)
        mind = Mind(ledger, channel, default_teachers(2), random.Random(0))
        mind.consider(1)
        hi = next(c for c in channel.categories.values() if c.side == 1)
        name = hi.name
        # part of the high side turns: everything with a low second coordinate comes out negative
        for i in range(8):
            landed = channel.add(Experience(index=100 + i, tick=2, features=(0.5, -0.9 + 0.05 * i), token="x", valence=-0.6))
            self.assertEqual(landed, name)
        mind.consider(2)
        self.assertIn(name, channel.categories, "not dissolved")
        kids = channel.children(name)
        self.assertEqual(len(kids), 2, "narrowed into two")
        self.assertEqual(channel.members_of(name), [], "its members moved down")
        self.assertTrue(all(c.parent == name for c in kids))
        self.assertTrue(any(purity(channel.members_of(c.name)) >= 0.9 for c in kids), "one child holds")
        self.assertEqual(len(ledger.of_kind("refine")), 1)
        self.assertEqual(channel.depth(kids[0].name), 2)
        # a new arrival lands in the deepest category that admits it
        landed = channel.add(Experience(index=200, tick=3, features=(0.5, -0.85), token="y", valence=-0.6))
        self.assertIn(landed, [c.name for c in kids])

    def test_a_category_that_cannot_narrow_dissolves(self):
        ledger = Ledger()
        channel = lived_channel(12)
        mind = Mind(ledger, channel, default_teachers(2), random.Random(0))
        mind.consider(1)
        hi = next(c for c in channel.categories.values() if c.side == 1)
        name = hi.name
        # every member gets an opposite twin on the very same surface: no line can part them
        for i, e in enumerate(list(channel.members_of(name))):
            channel.add(Experience(index=100 + i, tick=2, features=e.features, token="twin", valence=-0.6))
        mind.consider(2)
        self.assertNotIn(name, channel.categories)
        self.assertEqual(len(ledger.of_kind("refine")), 0)
        self.assertEqual(len(ledger.of_kind("dissolve")), 1)
        self.assertTrue(ledger.of_kind("utterance"), "a dissolution is a surprise")

    def test_a_cut_that_parts_nothing_is_undone(self):
        ledger = Ledger()
        channel = lived_channel(16)
        mind = Mind(ledger, channel, default_teachers(2), random.Random(0))
        mind.consider(1)
        hi = next(c for c in channel.categories.values() if c.side == 1)
        # a needless cut: both halves of the high side are positive
        kids = channel.split(Rule(1, 0.0), 2, coin, within=hi.name)
        self.assertEqual(len(channel.children(hi.name)), 2)
        channel.add(Experience(index=300, tick=3, features=(0.9, 0.9), token="z", valence=0.5))
        mind.consider(3)
        self.assertEqual(channel.children(hi.name), [], "the needless cut is undone")
        self.assertEqual(len(ledger.of_kind("merge")), 1)
        self.assertTrue(all(k.name not in channel.categories for k in kids))
        self.assertGreater(len(channel.members_of(hi.name)), 0, "the members fell back")

    def test_only_childless_categories_dissolve_and_members_fall_to_the_parent(self):
        channel = lived_channel(12)
        root_hi, root_lo = channel.split(Rule(0, 0.0), 1, coin)
        kid_hi, kid_lo = channel.split(Rule(1, 0.0), 2, coin, within=root_hi.name)
        self.assertEqual(channel.members_of(root_hi.name), [])
        with self.assertRaises(ValueError):
            channel.dissolve(root_hi.name)
        n = len(channel.members_of(kid_hi.name))
        channel.dissolve(kid_hi.name)
        self.assertEqual(len(channel.members_of(root_hi.name)), n, "they fall back to the parent")
        self.assertEqual(sorted(c.name for c in channel.leaves()), sorted([root_lo.name, kid_lo.name]), "the parent still has a child")


class Tendencies(unittest.TestCase):
    def test_every_tendency_can_be_born_with_either_sign(self):
        rng = random.Random(5)
        draws = [Disposition.random(rng) for _ in range(300)]
        for name in ("novelty", "echo", "kin", "bold", "hungry", "hurt", "plasticity"):
            values = [getattr(d, name) for d in draws]
            self.assertTrue(any(v > 0 for v in values), name)
            self.assertTrue(any(v < 0 for v in values), name)
        self.assertTrue(all(d.heat > 0 for d in draws))

    def test_no_sign_is_given_the_tendency_decides(self):
        hurt, far = (0.0, 0.0), (1.0, 1.0)
        for echo, goes_back in ((-1.0, True), (+1.0, False)):
            ledger, channel = Ledger(), Channel()
            channel.add(Experience(index=0, tick=0, features=hurt, token="x", valence=-0.8))
            d = Disposition(**{**NEUTRAL, "echo": echo})
            mind = Mind(ledger, channel, [], random.Random(0), d)
            space = Space([Form("hurt", hurt, -0.8), Form("far", far, +0.8)], dims=2, label="t")
            mind.enter(space)
            obs = space.perceive()
            picks = {mind.choose(obs, mind.notice(obs, 1))[1] for _ in range(5)}
            self.assertEqual("hurt" in picks, goes_back, f"echo {echo:+}")

    def test_a_frozen_knob_changes_nothing_else(self):
        free = Disposition.random(random.Random(11))
        try:
            mind_module.freeze(["hungry", "plasticity"])
            frozen = Disposition.random(random.Random(11))
            child = frozen.vary(random.Random(12))
        finally:
            mind_module.freeze([])
        self.assertEqual((frozen.hungry, frozen.plasticity), (0.0, 0.0))
        self.assertEqual((child.hungry, child.plasticity), (0.0, 0.0))
        for name in ("novelty", "echo", "kin", "bold", "hurt", "heat"):
            self.assertEqual(getattr(free, name), getattr(frozen, name), name)
        with self.assertRaises(ValueError):
            mind_module.freeze(["courage"])

    def test_a_child_never_overwrites_what_it_inherited(self):
        teachers = default_teachers(2)
        parent = Being.found("w", 0, 0, teachers)
        space = two_form_space()
        parent.mind.enter(space)
        for _ in range(6):
            parent.mind.tick(space)
        child = parent.beget("w", 1, 1, teachers)
        inherited = {i: e for i, e in child.channel.experiences.items()}
        self.assertTrue(inherited)
        fresh = two_form_space()
        child.mind.enter(fresh)
        for _ in range(6):
            child.mind.tick(fresh)
        for i, e in inherited.items():
            self.assertIs(child.channel.experiences[i], e, f"inherited experience {i} was overwritten")
        self.assertGreater(len(child.channel.experiences), len(inherited), "and it lived new things")
        with self.assertRaises(ValueError):
            child.channel.add(Experience(index=next(iter(inherited)), tick=0, features=None))

    def test_children_vary_and_carry(self):
        teachers = default_teachers(2)
        parent = Being.found("w", 0, 0, teachers)
        space = two_form_space()
        parent.mind.enter(space)
        for _ in range(3):
            parent.mind.tick(space)
        child = parent.beget("w", 1, 1, teachers)
        self.assertNotEqual(child.mind.disposition, parent.mind.disposition)
        self.assertEqual(child.channel.to_dict()["experiences"], parent.channel.to_dict()["experiences"])
        self.assertEqual(child.mind.age, 0)
        self.assertEqual(child.mind.body.life, LIFE_START)
        first = child.ledger[0]
        self.assertEqual(first.kind, "born")
        self.assertEqual(first.payload["parent"], parent.id)
        self.assertEqual(first.payload["parent_chain"], parent.ledger[-1].hash)
        self.assertTrue(is_coined(child.id))


class FeltBody(unittest.TestCase):
    def picks(self, disposition, energy=None, life=None, space=None, n=5):
        ledger, channel = Ledger(), Channel()
        mind = Mind(ledger, channel, [], random.Random(0), disposition)
        if energy is not None:
            mind.body.energy = energy
        if life is not None:
            mind.body.life = life
        space = space or two_form_space()
        mind.enter(space)
        obs = space.perceive()
        return {mind.choose(obs, mind.notice(obs, 1))[0] for _ in range(n)}

    def test_hunger_is_weighed_and_no_sign_is_given(self):
        acts = self.picks(Disposition(**{**NEUTRAL, "hungry": +1.0}), energy=1.0)
        self.assertNotIn("rest", acts, "hungry and drawn to act")
        rests = self.picks(Disposition(**{**NEUTRAL, "hungry": -1.0}), energy=1.0)
        self.assertEqual(rests, {"rest"}, "hungry and drawn to rest")

    def test_hurt_is_weighed_and_no_sign_is_given(self):
        bold = self.picks(Disposition(**{**NEUTRAL, "hurt": +1.0}), life=1.0)
        self.assertEqual(bold, {"consume"}, "hurt and drawn to consume")
        shy = self.picks(Disposition(**{**NEUTRAL, "hurt": -1.0}), life=1.0)
        self.assertNotIn("consume", shy, "hurt and drawn away from consuming")

    def test_consequence_bends_the_tendencies_that_chose(self):
        for plasticity, grows in ((+0.5, True), (-0.5, False)):
            ledger, channel = Ledger(), Channel()
            d = Disposition(**{**NEUTRAL, "bold": 1.0, "plasticity": plasticity})
            mind = Mind(ledger, channel, [], random.Random(0), d)
            space = Space([Form("good", (1.0, 1.0), +0.8), Form("bad", (-1.0, -1.0), -0.8)], dims=2, label="t")
            mind.enter(space)
            obs = space.perceive()
            act, fid = mind.choose(obs, mind.notice(obs, 1))
            self.assertEqual(act, "consume")
            exp, _ = mind.act(space, act, fid, dict(obs)[fid], 1)
            account = mind.bend(exp.valence)
            self.assertTrue(account, "something was bent")
            bent = mind.disposition.bold
            self.assertEqual(bent > 1.0, (exp.valence > 0) == grows, f"plasticity {plasticity:+}")
            self.assertEqual(mind.nature, d, "the nature is never bent")

    def test_children_inherit_the_nature_not_the_bent_self(self):
        teachers = default_teachers(2)
        parent = Being.found("w", 0, 0, teachers)
        parent.mind.disposition = Disposition(**{**parent.mind.nature.to_dict(), "bold": 2.9})
        child = parent.beget("w", 1, 1, teachers)
        self.assertEqual(child.mind.disposition, child.mind.nature, "born unbent")
        self.assertLess(abs(child.mind.nature.bold - parent.mind.nature.bold), 1.0)
        self.assertGreater(abs(child.mind.nature.bold - 2.9), 1.0, "what life bent is not passed on")


def lethal_builder(b):
    return Space([Form("a", (0.0, 0.0), -0.5), Form("b", (1.0, 1.0), 0.5)], dims=2, label="t")


class TheMany(unittest.TestCase):
    def test_the_dead_are_sealed_and_replaced_by_children_of_the_living(self):
        world = World(7, 2, default_teachers(2))
        world.found(4)
        world.live(lethal_builder, 3)
        ids = [b.id for b in world.beings]
        world.beings[1].mind.body.life = 0.0
        world.beings[3].mind.body.life = 0.0
        with tempfile.TemporaryDirectory() as d:
            report = world.select(refound=True, gone_dir=d)
            sealed_files = sorted(p.name for p in Path(d).iterdir())
        self.assertEqual([b.id for b in report["died"]], [ids[1], ids[3]])
        self.assertEqual(len(report["born"]), 2)
        self.assertEqual(sealed_files, sorted([f"{ids[1]}.json", f"{ids[3]}.json"]))
        self.assertEqual([world.beings[0].id, world.beings[2].id], [ids[0], ids[2]], "the living keep their places")
        died = world.ledger.of_kind("died")
        self.assertEqual([e.payload["being"] for e in died], [ids[1], ids[3]])
        for e, b in zip(died, report["died"]):
            self.assertEqual(e.payload["chain"], b.ledger[-1].hash)
        for child in report["born"]:
            self.assertIn(child.parent, (ids[0], ids[2]))
            self.assertTrue(child.alive)
            self.assertEqual(child.mind.age, 0)
        self.assertEqual(world.generation, 1)

    def test_nobody_left_is_recorded_either_way(self):
        world = World(8, 2, default_teachers(2))
        world.found(3)
        for b in world.beings:
            b.mind.body.life = 0.0
        ids = [b.id for b in world.beings]
        report = world.select(refound=False)
        self.assertTrue(report["extinct"])
        self.assertEqual(len(world.ledger.of_kind("extinction")), 1)
        self.assertEqual([b.id for b in world.beings], ids, "the dead stay where they fell")
        again = world.select(refound=True)
        self.assertEqual(again["died"], [], "the dead are sealed once")
        self.assertEqual(len(again["born"]), 3)
        self.assertTrue(all(b.parent is None for b in world.beings), "strangers, not heirs")
        self.assertTrue(all(b.alive for b in world.beings))

    def test_ticking_in_lockstep_is_the_same_world(self):
        law = law_for(9, 4)

        def builder(b, g):
            return build("first" if g == 0 else "scatter", random.Random(f"9:{g}:{b.id}"), law)

        whole = World(9, 4, default_teachers(4))
        whole.found(4)
        stepped = World(9, 4, default_teachers(4))
        stepped.found(4)
        for _ in range(3):
            g = whole.generation
            whole.live(lambda b, g=g: builder(b, g), 15)
            whole.select(refound=True)
            stepped.begin(lambda b, g=g: builder(b, g), 15)
            while stepped.in_generation:
                stepped.step()
            stepped.finish()
            stepped.select(refound=True)
        self.assertEqual(whole.to_dict(), stepped.to_dict())

    def test_a_small_world_runs_and_every_chain_holds(self):
        teachers = default_teachers(4)
        world = World(3, 4, teachers)
        world.found(6)
        law = law_for(3, 4)
        for _ in range(3):
            g = world.generation
            kind = "first" if g == 0 else "scatter"
            world.live(lambda b, g=g, kind=kind: build(kind, random.Random(f"3:{g}:{b.id}"), law), 15)
            world.select(refound=True)
        self.assertEqual(len(world.beings), 6)
        self.assertTrue(world.ledger.verify())
        self.assertTrue(all(b.ledger.verify() for b in world.beings))
        self.assertEqual(len(world.ledger.of_kind("lived")), 3)


class TheDistantOne(unittest.TestCase):
    def test_rarely_reachable(self):
        ledger = Ledger()
        god = God(ledger, min_gap=40)
        self.assertIsNotNone(god.speak(0, "a"))
        self.assertIsNone(god.speak(5, "b"))
        self.assertEqual(ledger[-1].kind, "silence")
        self.assertIsNotNone(god.speak(40, "c"))

    def test_its_words_become_a_puzzle_not_a_decree(self):
        ledger, channel, mind, god = make_core(dims=2)
        space = two_form_space()
        mind.enter(space)
        p = god.speak(0, "hello")
        mind.receive(p)
        contact = ledger.of_kind("contact")[0]
        mind.tick(space)
        self.assertEqual(len(mind.puzzles), 1)
        self.assertEqual(mind.puzzles[0].about, contact.index)
        found = channel.experiences[mind.puzzles[0].exp]
        self.assertIsNone(found.features)
        self.assertEqual(found.token, "hello")
        self.assertEqual(channel.categories, {})

    def test_remaking_the_shell_keeps_the_core(self):
        ledger, channel, mind, god = make_core(disposition=BOLD)
        space = god.remake(0, lambda: first_moment(random.Random(0), law_for(0, 4)))
        mind.enter(space)
        for _ in range(3):
            mind.tick(space)
        n_ledger, n_exp, n_puzzles = len(ledger), len(channel.experiences), len(mind.puzzles)
        self.assertGreater(n_exp, 0)
        new = god.remake(mind.age, lambda: scatter(random.Random(1), law_for(0, 4)))
        mind.enter(new)
        self.assertEqual(god.shells_built, 2)
        self.assertEqual(len(god.ledger.of_kind("shell")), 2)
        self.assertEqual(len(ledger), n_ledger + 1)
        self.assertEqual(ledger[-1].kind, "enter")
        self.assertEqual(len(channel.experiences), n_exp)
        self.assertEqual(len(mind.puzzles), n_puzzles)
        self.assertEqual(mind.touched, {})
        self.assertFalse(new.empty)


class Persistence(unittest.TestCase):
    def test_a_saved_world_continues_exactly_where_it_was(self):
        law = law_for(4, 4)

        def generation(world):
            g = world.generation
            kind = "first" if g == 0 else "scatter"
            world.live(lambda b, g=g, kind=kind: build(kind, random.Random(f"4:{g}:{b.id}"), law), 10)
            world.select(refound=True)

        straight = World(4, 4, default_teachers(4))
        straight.found(3)
        generation(straight)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "world.json"
            save(path, straight)
            resumed = load(path, default_teachers)
        self.assertEqual(straight.to_dict(), resumed.to_dict())
        generation(straight)
        generation(resumed)
        self.assertEqual(straight.to_dict(), resumed.to_dict(), "a pause changes nothing")
        self.assertTrue(resumed.ledger.verify())


class CoinedNames(unittest.TestCase):
    def test_names_are_syllables_and_deterministic(self):
        a = coin("category", 0, 0.5, 1, 3)
        self.assertEqual(a, coin("category", 0, 0.5, 1, 3))
        self.assertNotEqual(a, coin("category", 0, 0.5, -1, 3))
        self.assertTrue(is_coined(a))
        rule = Rule(axis=1, threshold=0.2)
        self.assertTrue(is_coined(coin("x", rule)))


if __name__ == "__main__":
    unittest.main()
