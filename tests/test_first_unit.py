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
from core.mind import LIFE_START, Body, Disposition, Mind
from core.persist import load, save
from core.symbols import SYLLABLES, coin
from core.teachers import AxisTeacher, default_teachers
from core.valence import TruthViolation, Valence, assert_truth
from shell.seed import build, first_moment, law_for, scatter
from shell.space import Form, Gone, Space

CAUTIOUS = Disposition(novelty=1.0, echo=0.0, kin=0.0, bold=-1.0, heat=0.01)   # touches the new
BOLD = Disposition(novelty=1.0, echo=0.0, kin=0.0, bold=1.0, heat=0.01)        # consumes the new


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
        found = channel.experiences[mind.puzzles[0].found]
        self.assertIsNone(found.features, "it arrived with no surface")
        self.assertEqual(found.token, u.payload["that"])
        self.assertIn(found, channel.open_bucket())

    def test_paradox_is_lived_and_nothing_on_the_surface_resolves_it(self):
        ledger, channel, mind, god = make_core(disposition=BOLD)
        space = god.remake(0, lambda: first_moment(random.Random(0), law_for(0, 4)))
        mind.enter(space)
        for _ in range(12):
            mind.tick(space)
        self.assertTrue(space.empty)
        self.assertEqual(channel.categories, {})
        signs = {e.sign for e in channel.experiences.values() if e.sign}
        self.assertEqual(signs, {1, -1}, "both signs were lived")
        nearness = [p for p in mind.perspectives if p.source == "nearness"]
        self.assertTrue(nearness)
        self.assertTrue(all(p.proposal is None for p in nearness))
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

    def test_axis_teacher_proposes_its_best_line(self):
        channel = lived_channel(12)
        p = AxisTeacher(0).regard(channel.view(), 1)
        self.assertIsNotNone(p.proposal)
        self.assertEqual(p.proposal.axis, 0)
        self.assertLess(abs(p.proposal.threshold), 0.3)

    def test_carving_needs_consequence_and_more_than_one_view(self):
        ledger = Ledger()
        channel = lived_channel(12)
        lone = Mind(ledger, channel, [AxisTeacher(0)], random.Random(0))
        lone.consider(1)
        self.assertEqual(channel.categories, {}, "one view is never enough")

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

    def test_category_dissolves_when_consequence_turns(self):
        ledger = Ledger()
        channel = lived_channel(12)
        mind = Mind(ledger, channel, default_teachers(2), random.Random(0))
        mind.consider(1)
        hi = next(c for c in channel.categories.values() if c.side == 1)
        name = hi.name
        # the world turns: things on the high side now come out negative
        for i in range(8):
            landed = channel.add(Experience(index=100 + i, tick=2, features=(0.5, 0.1 * i), token="x", valence=-0.6))
            self.assertEqual(landed, name)
        mind.consider(2)
        self.assertNotIn(name, channel.categories)
        self.assertEqual(len(ledger.of_kind("dissolve")), 1)
        self.assertTrue(ledger.of_kind("utterance"), "a dissolution is a surprise")


class Tendencies(unittest.TestCase):
    def test_every_tendency_can_be_born_with_either_sign(self):
        rng = random.Random(5)
        draws = [Disposition.random(rng) for _ in range(300)]
        for name in ("novelty", "echo", "kin", "bold"):
            values = [getattr(d, name) for d in draws]
            self.assertTrue(any(v > 0 for v in values), name)
            self.assertTrue(any(v < 0 for v in values), name)
        self.assertTrue(all(d.heat > 0 for d in draws))

    def test_no_sign_is_given_the_tendency_decides(self):
        hurt, far = (0.0, 0.0), (1.0, 1.0)
        for echo, goes_back in ((-1.0, True), (+1.0, False)):
            ledger, channel = Ledger(), Channel()
            channel.add(Experience(index=0, tick=0, features=hurt, token="x", valence=-0.8))
            d = Disposition(novelty=0.0, echo=echo, kin=0.0, bold=0.0, heat=0.001)
            mind = Mind(ledger, channel, [], random.Random(0), d)
            space = Space([Form("hurt", hurt, -0.8), Form("far", far, +0.8)], dims=2, label="t")
            mind.enter(space)
            obs = space.perceive()
            picks = {mind.choose(obs, mind.notice(obs, 1))[1] for _ in range(5)}
            self.assertEqual("hurt" in picks, goes_back, f"echo {echo:+}")

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
        found = channel.experiences[mind.puzzles[0].found]
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
