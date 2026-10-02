#!/usr/bin/env python3
"""A window onto the world, and a world that keeps running.

    python serve.py                              # then open http://localhost:8000
    python serve.py --port 8080 --state state/world.json
    python serve.py --fresh --beings 12 --law corner --visits 0

The world runs inside this process for as long as the process runs,
generation after generation, and saves itself at the end of every
generation, so a restart resumes where it was. The page lets you watch
every being, slow down or pause, step one tick at a time, set how often
teachers visit, say something to all who live, and begin a new world.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import signal
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.channel import purity
from core.many import World
from core.persist import load, save
from core.teachers import default_teachers
from shell.seed import LAW_KINDS, build, law_for
from view import history_lines

DIMS = 4
HERE = Path(__file__).resolve().parent
PAGE = HERE / "ui" / "index.html"
KEEP_RECORD = 3000      # world-record entries kept in the save file; older ones go to record.jsonl
KEEP_SEALED = 2000      # sealed ledgers of the dead kept on disk; the world's record keeps every death
KEEP_HISTORY = 5000


def env(name: str, default):
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return type(default)(value) if not isinstance(default, bool) else value.lower() in ("1", "true", "yes")


class Runner:
    """Owns the world and the thread that ticks it."""

    def __init__(self, state: Path, args) -> None:
        self.state_path = state
        self.gone_dir = state.parent / "gone"
        self.lock = threading.RLock()
        self.recent: dict = {}                 # being id -> its last lines
        self.events: deque = deque(maxlen=300)  # world-level notes, newest last
        self.history: list = []                # one row per finished generation
        self.speed = float(args.speed)         # ticks per second
        self.paused = bool(args.paused)
        self.steps_wanted = 0
        self.token = args.token or ""          # when set, only requests that carry it may steer the world
        self.stop = threading.Event()
        if state.exists() and not args.fresh:
            self.world = load(state, default_teachers)
            self.note(f"the world continues at generation {self.world.generation}")
        else:
            self.world = self.new_world(args.seed, args.beings, args.law or "axis", args.visits, args.ticks, args.first_ticks)
        self.world.options.setdefault("ticks", args.ticks)
        self.world.options.setdefault("first_ticks", args.first_ticks)
        self.law = law_for(self.world.seed, self.world.dims, self.world.options.get("law", "axis"))
        hist = state.parent / "history.json"
        if hist.exists() and not args.fresh:
            try:
                self.history = json.loads(hist.read_text())
            except ValueError:
                self.history = []
        self.thread = threading.Thread(target=self.loop, daemon=True)

    # -- making and keeping worlds ------------------------------------------

    def new_world(self, seed, beings, law_kind, visits, ticks, first_ticks) -> World:
        world = World(seed, DIMS, default_teachers(DIMS))
        world.options.update({"law": law_kind, "visits": int(visits), "ticks": int(ticks), "first_ticks": int(first_ticks)})
        world.found(int(beings))
        self.recent, self.history = {}, []
        self.events.clear()
        self.note(f"a new world: {beings} beings, law {law_kind}, seed {seed}")
        return world

    def persist(self) -> None:
        w = self.world
        w.ledger.archive(self.state_path.parent / "record.jsonl", KEEP_RECORD)
        save(self.state_path, w)
        del self.history[:-KEEP_HISTORY]
        (self.state_path.parent / "history.json").write_text(json.dumps(self.history))
        alive = {b.id for b in w.beings}
        for bid in [k for k in self.recent if k not in alive]:
            del self.recent[bid]
        self.prune_sealed()

    def prune_sealed(self) -> None:
        """Keep the newest sealed ledgers; the world's record keeps every death."""
        if not self.gone_dir.is_dir():
            return
        files = sorted(self.gone_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        for path in files[:-KEEP_SEALED]:
            path.unlink(missing_ok=True)

    def note(self, text: str) -> None:
        self.events.append({"gen": getattr(self, "world", None) and self.world.generation, "text": text})

    # -- ticking --------------------------------------------------------------

    def builder(self, being):
        g = self.world.generation
        kind = "first" if g == 0 else "scatter"
        return build(kind, random.Random(f"{self.world.seed}:{g}:{being.id}"), self.law)

    def advance(self) -> None:
        w = self.world
        if not w.in_generation:
            if w.shells:
                w.finish()
                report = w.select(refound=True, gone_dir=self.gone_dir)
                for b in report["died"]:
                    self.note(f"{b.id} is gone at age {b.mind.age}")
                for b in report["born"]:
                    self.note(f"{b.id} is born of {b.parent}")
                if report["extinct"]:
                    self.note("no one was left; the world begins again from strangers")
                self.history.append(self.generation_row(report))
                self.persist()
            ticks = int(w.options.get("first_ticks", 12)) if w.generation == 0 else int(w.options.get("ticks", 60))
            w.begin(self.builder, ticks)
            self.note(f"generation {w.generation} begins; {len(w.living)} living")
        out = w.step()
        for bid, lines in out.items():
            self.recent.setdefault(bid, deque(maxlen=120)).extend(lines)

    def generation_row(self, report) -> dict:
        w = self.world
        living = w.living
        cats = [len(b.channel.categories) for b in living]
        depth = [max((b.channel.depth(c.name) for c in b.channel.categories.values()), default=0) for b in living]
        return {
            "gen": w.generation - 1,
            "survived": len(report["living"]),
            "died": len(report["died"]),
            "born": len(report["born"]),
            "categories": round(sum(cats) / len(cats), 2) if cats else 0.0,
            "deepest": max(depth, default=0),
            "life": round(sum(b.mind.body.life for b in living) / len(living), 2) if living else 0.0,
        }

    def loop(self) -> None:
        while not self.stop.is_set():
            if self.paused and self.steps_wanted <= 0:
                time.sleep(0.05)
                continue
            started = time.monotonic()
            with self.lock:
                self.advance()
                if self.steps_wanted > 0:
                    self.steps_wanted -= 1
            if self.steps_wanted > 0:
                continue
            wait = 1.0 / max(self.speed, 0.01) - (time.monotonic() - started)
            if wait > 0:
                time.sleep(min(wait, 5.0))

    # -- what the page asks for ------------------------------------------------

    def state(self) -> dict:
        w = self.world
        beings = []
        for i, b in enumerate(w.beings):
            ch = b.channel
            m = b.mind
            lines = self.recent.get(b.id, ())
            last = next((l for l in reversed(lines) if not l.startswith("tick ") and not l.startswith("  notice")), "")
            beings.append({
                "i": i, "id": b.id, "alive": b.alive, "age": m.age, "born": b.born, "parent": b.parent,
                "life": round(m.body.life, 2), "energy": round(m.body.energy, 2),
                "lived": b.lived()[0], "categories": len(ch.categories),
                "depth": max((ch.depth(c.name) for c in ch.categories.values()), default=0),
                "puzzles": len(m.puzzles), "visits": len(b.ledger.of_kind("visit")),
                "disposition": {k: round(v, 2) for k, v in m.disposition.to_dict().items()},
                "last": last.strip(),
            })
        return {
            "generation": w.generation, "tick": w.tick_in_generation, "ticks": w.ticks_per_generation,
            "paused": self.paused, "speed": self.speed, "seed": w.seed,
            "law": self.law.describe(), "law_kind": self.law.kind, "visits": w.visit_rate,
            "living": len(w.living), "total": len(w.beings), "record": len(w.ledger),
            "beings": beings, "events": list(self.events)[-40:], "history": self.history[-80:],
        }

    def being(self, i: int, axes) -> dict:
        w = self.world
        b = w.beings[i]
        ch = b.channel
        born = b.ledger[0]
        inherited = set(born.payload.get("categories", [])) if born.kind == "born" else set()
        tree = []
        for cat in sorted(ch.categories.values(), key=lambda c: (ch.depth(c.name), c.born, c.name)):
            members = ch.members_of(cat.name)
            lived = [e for e in members if e.valence is not None]
            tree.append({
                "name": cat.name, "parent": cat.parent, "depth": ch.depth(cat.name),
                "axis": cat.rule.axis, "side": cat.side, "threshold": round(cat.rule.threshold, 3),
                "chain": [[c.rule.axis, c.side, round(c.rule.threshold, 3)] for c in ch.chain(cat.name)],
                "members": len(members), "agreement": round(purity(members), 2),
                "mean": round(sum(e.valence for e in lived) / len(lived), 3) if lived else 0.0,
                "born": cat.born, "inherited": cat.name in inherited,
                "narrowed": bool(ch.children(cat.name)),
            })
        open_ = ch.open_bucket()
        featured = [e for e in open_ if e.features is not None]
        forms = self.world.forms.get(b.id, {})
        space = self.world.shells.get(b.id)
        alive_forms = set(space.forms) if space is not None else set()
        lived_all = [e for e in ch.experiences.values() if e.features is not None and e.valence is not None]
        lived_all = sorted(lived_all, key=lambda e: e.index)[-600:]
        this_shell = set(forms)
        last_form = next((e.payload["form"] for e in reversed(list(b.ledger)) if e.kind == "act"), None)
        return {
            "i": i, "id": b.id, "alive": b.alive, "age": b.mind.age, "born": b.born, "parent": b.parent,
            "life": round(b.mind.body.life, 2), "energy": round(b.mind.body.energy, 2),
            "disposition": {k: round(v, 2) for k, v in b.mind.disposition.to_dict().items()},
            "nature": {k: round(v, 2) for k, v in b.mind.nature.to_dict().items()},
            "open": {"featured": len(featured), "positive": sum(1 for e in featured if e.sign and e.sign > 0),
                     "negative": sum(1 for e in featured if e.sign and e.sign < 0), "bare": len(open_) - len(featured)},
            "tree": tree,
            "forms": [{"id": fid, "surface": list(s), "hidden": h, "gone": fid not in alive_forms}
                      for fid, (s, h) in forms.items()],
            "lived": [{"s": list(e.features), "v": e.valence, "here": e.token in this_shell} for e in lived_all],
            "last_form": last_form,
            "puzzles": [p.token for p in b.mind.puzzles[-12:]],
            "history": history_lines(b.ledger)[-40:],
            "recent": list(self.recent.get(b.id, ()))[-60:],
        }

    def control(self, cmd: dict) -> dict:
        action = cmd.get("action")
        if action == "whoami":
            return {"ok": True, "protected": bool(self.token)}
        with self.lock:
            w = self.world
            if action == "pause":
                self.paused = True
            elif action == "play":
                self.paused = False
            elif action == "step":
                self.paused = True
                self.steps_wanted += int(cmd.get("n", 1))
            elif action == "speed":
                self.speed = max(0.05, min(1000.0, float(cmd.get("value", 10))))
            elif action == "visits":
                w.set_visits(int(cmd.get("value", 0)))
                self.note("teachers visit about every %d ticks" % w.visit_rate if w.visit_rate else "no teacher visits")
            elif action == "say":
                text = str(cmd.get("text", "")).strip()
                if text:
                    p = w.god.speak(w.generation, text)
                    if p is None:
                        self.note(f"too soon; the distant one stays silent (last contact in generation {w.god.last_contact})")
                    else:
                        for b in w.living:
                            b.mind.receive(p)
                        self.note(f'the distant one speaks to all who live: "{text}"')
            elif action == "remake":
                w.tick_in_generation = w.ticks_per_generation
                self.note("the shells are thrown away early")
            elif action == "ticks":
                w.options["ticks"] = max(5, int(cmd.get("value", 60)))
            elif action == "new":
                law_kind = cmd.get("law", "axis")
                if law_kind not in LAW_KINDS:
                    law_kind = "axis"
                self.world = self.new_world(int(cmd.get("seed", 0)), int(cmd.get("beings", 12)), law_kind,
                                            int(cmd.get("visits", 0)), int(cmd.get("ticks", 60)), int(cmd.get("first_ticks", 12)))
                self.law = law_for(self.world.seed, self.world.dims, law_kind)
                self.persist()
            elif action == "save":
                self.persist()
            else:
                return {"ok": False, "error": f"unknown action {action!r}"}
        return {"ok": True}


def make_handler(runner: Runner):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # quiet
            pass

        def send_json(self, data, code=200):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path in ("/", "/index.html"):
                body = PAGE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif url.path == "/api/state":
                with runner.lock:
                    self.send_json(runner.state())
            elif url.path == "/healthz":
                self.send_json({"ok": True, "generation": runner.world.generation})
            elif url.path == "/api/being":
                q = parse_qs(url.query)
                i = int(q.get("i", ["0"])[0])
                with runner.lock:
                    if not (0 <= i < len(runner.world.beings)):
                        self.send_json({"error": "no such being"}, 404)
                        return
                    self.send_json(runner.being(i, None))
            else:
                self.send_json({"error": "not found"}, 404)

        def do_POST(self):
            url = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                cmd = json.loads(raw or b"{}")
            except ValueError:
                self.send_json({"ok": False, "error": "bad json"}, 400)
                return
            if url.path == "/api/control":
                if runner.token and cmd.get("action") != "whoami" and self.headers.get("X-World-Token", "") != runner.token:
                    self.send_json({"ok": False, "error": "token"}, 401)
                    return
                self.send_json(runner.control(cmd))
            else:
                self.send_json({"error": "not found"}, 404)

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=env("PORT", 8000))
    ap.add_argument("--host", default=env("WORLD_HOST", "127.0.0.1"))
    ap.add_argument("--state", default=env("WORLD_STATE", str(Path("state") / "world.json")))
    ap.add_argument("--fresh", action="store_true", help="discard any saved world")
    ap.add_argument("--beings", type=int, default=env("WORLD_BEINGS", 12))
    ap.add_argument("--law", choices=LAW_KINDS, default=env("WORLD_LAW", "") or None)
    ap.add_argument("--visits", type=int, default=env("WORLD_VISITS", 0))
    ap.add_argument("--seed", type=int, default=env("WORLD_SEED", 0))
    ap.add_argument("--ticks", type=int, default=env("WORLD_TICKS", 60))
    ap.add_argument("--first-ticks", type=int, default=12)
    ap.add_argument("--speed", type=float, default=env("WORLD_SPEED", 4.0), help="ticks per second to start with")
    ap.add_argument("--paused", action="store_true")
    ap.add_argument("--token", default=env("WORLD_TOKEN", ""),
                    help="if set, the page must present this to steer the world; watching needs nothing")
    args = ap.parse_args(argv)

    runner = Runner(Path(args.state), args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(runner))
    runner.thread.start()

    def shutdown(*_):
        runner.stop.set()
        with runner.lock:
            runner.persist()
        print("\nsaved; the world will continue from here next time")
        server.shutdown()

    signal.signal(signal.SIGINT, lambda *a: threading.Thread(target=shutdown).start())
    signal.signal(signal.SIGTERM, lambda *a: threading.Thread(target=shutdown).start())
    print(f"the world is running at http://{args.host}:{args.port}  (generation {runner.world.generation}, "
          f"{len(runner.world.living)} living; {runner.speed:g} ticks per second; "
          f"{'steering needs the token' if runner.token else 'anyone who can reach it can steer it'})", flush=True)
    try:
        server.serve_forever()
    finally:
        runner.stop.set()
    return 0


if __name__ == "__main__":
    sys.exit(main())
