"""Drex Life: every pixel is an agent, the laws of physics are plain English, Drex decides every cell, every frame.

A world = a few cell states (each with a palette color) + rules in English + a starting layout.
  1. The director (DeepInfra LLM) turns an idea into a world spec. It never decides any cell.
  2. Drex paints the starting grid: one `choice` question per cell.
  3. Each step, every cell asks Drex "I am X and my 8 neighbours are ...; what do I become?"
     - Questions are asked once per UNIQUE neighbourhood (cells in the same situation share one answer),
       and answers are cached across steps, so the world gets faster as Drex learns its physics.
     - The next state is SAMPLED from Drex's calibrated probabilities, so "slowly regrows" really is slow.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
from dataclasses import asdict, dataclass, field
from typing import Callable

from PIL import Image

from pixeldrex.drex import Drex, choice
from pixeldrex.llm import DeepInfra
from pixeldrex.pixels import PALETTE

EDGE = "edge"
DIRS = [("north-west", -1, -1), ("north", -1, 0), ("north-east", -1, 1), ("west", 0, -1),
        ("east", 0, 1), ("south-west", 1, -1), ("south", 1, 0), ("south-east", 1, 1)]


@dataclass
class CellState:
    name: str
    color: str
    meaning: str


@dataclass
class World:
    title: str
    states: list[CellState]
    rules: str
    start: str

    @property
    def names(self) -> list[str]:
        return [s.name for s in self.states]

    def color(self, name: str) -> tuple[int, int, int]:
        for s in self.states:
            if s.name == name:
                return PALETTE.get(s.color, (255, 0, 255))
        return (255, 0, 255)

    def to_dict(self) -> dict:
        return {"title": self.title, "states": [asdict(s) for s in self.states], "rules": self.rules,
                "start": self.start}

    @classmethod
    def from_dict(cls, d: dict) -> "World":
        states, seen = [], set()
        for s in d.get("states") or []:
            name = re.sub(r"[^a-z0-9 _-]", "", str(s.get("name", "")).lower()).strip()[:20]
            color = str(s.get("color", "")).lower().replace(" ", "")
            if not name or name in seen:
                continue
            seen.add(name)
            states.append(CellState(name, color if color in PALETTE else "gray", str(s.get("meaning", name))))
        if len(states) < 2:
            raise ValueError("a world needs at least 2 cell states")
        return cls(str(d.get("title") or "Untitled world")[:60], states[:6], str(d.get("rules") or ""),
                   str(d.get("start") or "random"))


DIRECTOR = f"""You design tiny cellular-automaton worlds, like Conway's Game of Life but with rules in plain English.
Each cell of a grid is in one of a few states. Every step, each cell changes based ONLY on its own state and its
8 neighbours. Turn the user's idea into a JSON world:
{{
  "title": "short title, max 5 words",
  "states": [{{"name": "one lowercase word", "color": "palette color", "meaning": "what this cell is"}}],
  "rules": "3-6 short rules, one per line, each saying what a cell in some state becomes depending on its neighbours, e.g. 'a tree with a burning neighbour catches fire'. Use words like often, rarely, slowly for randomness.",
  "start": "where each state is at the start, e.g. 'mostly trees, with a small fire in the center and a river of water down the left side'"
}}
Rules for you:
- 3 to 5 states. Each state gets a DIFFERENT color from this palette: {", ".join(PALETTE)}.
  The colors must look clearly different from each other (never two grays, never two greens, never two blues).
- Every state must be able to change into something, so the world keeps moving for many steps.
- Include a quiet/background state (like empty, grass, water) that covers most of the start.
- Rules must only mention a cell's own state and its neighbours (directions north/south/east/west are allowed).
- All cells update at the same time, so MOVEMENT always needs two rules: one for the cell being left
  ("sand with empty to the south becomes empty") and one for the cell being entered
  ("empty with sand to the north becomes sand"). Never write a movement rule without its partner.
- Avoid rules that spawn things at random everywhere; change should spread from neighbours.
- Colors must contrast strongly with the background state so the action is easy to see.
- Reply with the JSON object only."""


async def design_world(di: DeepInfra, idea: str, retries: int = 2) -> World:
    prompt = f"Idea: {idea}"
    err: Exception | None = None
    for _ in range(retries + 1):
        text = await di.chat(prompt, system=DIRECTOR, max_tokens=700, temperature=0.5, json_mode=True)
        try:
            m = re.search(r"\{.*\}", text, re.S)
            return World.from_dict(json.loads(m.group(0) if m else text))
        except (ValueError, json.JSONDecodeError, AttributeError) as e:
            err = e
            prompt = f"Idea: {idea}\n\nYour last reply was not a valid world ({e}). Reply with the JSON object only."
    raise RuntimeError(f"director failed to design a world: {err}")


def _criteria(world: World) -> dict[str, str]:
    return {s.name: s.meaning for s in world.states}


async def seed(drex: Drex, world: World, n: int) -> list[list[str]]:
    """Drex paints the starting layout: one choice question per cell."""
    qs = {
        f"c_{r:02d}_{c:02d}": choice(
            f"At the start, which state is the cell at row {r}, column {c}? "
            f"(row 0 is the top, column 0 the left, the grid is {n}x{n})",
            _criteria(world),
        )
        for r in range(n) for c in range(n)
    }
    state = f"A {n}x{n} grid world: {world.title}. Starting layout: {world.start}."
    ans = await drex.ask_many(state, qs)
    return [[ans[f"c_{r:02d}_{c:02d}"]["choice"] for c in range(n)] for r in range(n)]


def neighbourhood(grid: list[list[str]], r: int, c: int) -> tuple[str, ...]:
    n = len(grid)
    return tuple(grid[r + dr][c + dc] if 0 <= r + dr < n and 0 <= c + dc < n else EDGE for _, dr, dc in DIRS)


DIRECTION_WORDS = re.compile(r"\b(north|south|east|west|above|below|up|down|left|right|falls?|rises?|wind)\b", re.I)


def is_directional(world: World) -> bool:
    """Do the rules care which side a neighbour is on? If not, only neighbour counts matter."""
    return bool(DIRECTION_WORDS.search(world.rules))


def situation(grid: list[list[str]], r: int, c: int, directional: bool) -> tuple:
    """The key a cell's next state depends on. Count-based keys collapse many cells into one question."""
    nb = neighbourhood(grid, r, c)
    if directional:
        return (grid[r][c], nb)
    counts: dict[str, int] = {}
    for x in nb:
        counts[x] = counts.get(x, 0) + 1
    return (grid[r][c], tuple(sorted(counts.items())))


def _question(world: World, key: tuple, directional: bool) -> dict:
    me, rest = key
    if directional:
        counts: dict[str, int] = {}
        for x in rest:
            if x != EDGE:
                counts[x] = counts.get(x, 0) + 1
        around = ", ".join(f"{d} {x}" for (d, _, _), x in zip(DIRS, rest))
        tally = ", ".join(f"{v} {k}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
        desc = f"Its neighbours: {around} (in total: {tally})."
    else:
        parts = [f"{v} {k}" for k, v in sorted(rest, key=lambda kv: -kv[1]) if k != EDGE]
        edges = dict(rest).get(EDGE, 0)
        desc = f"Of its 8 neighbours: {', '.join(parts) or 'none'}" + (f" ({edges} are outside the world)." if edges else ".")
    return choice(
        f"This cell is currently {me}. {desc} Following the rules, what is this cell in the next step?",
        _criteria(world),
    )


@dataclass
class Life:
    world: World
    grid: list[list[str]]
    temperature: float = 0.6
    seed_value: int = 0
    cache: dict = field(default_factory=dict)  # (me, neighbourhood) -> probabilities
    steps: int = 0
    asked: int = 0  # unique questions sent to Drex
    cell_updates: int = 0  # cell decisions made (asked + reused)

    def __post_init__(self):
        self.rnd = random.Random(self.seed_value)
        self.directional = is_directional(self.world)

    def _rules_state(self) -> str:
        legend = "; ".join(f"{s.name}: {s.meaning}" for s in self.world.states)
        return (f"A cellular world simulation called '{self.world.title}'. Cell states: {legend}. "
                f"'edge' means outside the world. Rules, applied to every cell at the same time each step:\n"
                f"{self.world.rules}")

    async def step(self, drex: Drex) -> dict:
        n = len(self.grid)
        keyed = [[situation(self.grid, r, c, self.directional) for c in range(n)] for r in range(n)]
        keys = {k for row in keyed for k in row}
        new = [k for k in keys if k not in self.cache]
        if new:
            qs = {f"q{i:04d}": _question(self.world, k, self.directional) for i, k in enumerate(new)}
            ans = await drex.ask_many(self._rules_state(), qs)
            for i, k in enumerate(new):
                self.cache[k] = ans[f"q{i:04d}"]["probabilities"]
        nxt = []
        for r in range(n):
            row = []
            for c in range(n):
                probs = self.cache[keyed[r][c]]
                names = list(probs)
                if self.temperature <= 0:
                    row.append(max(names, key=probs.get))
                else:
                    w = [max(probs[x], 1e-9) ** (1 / self.temperature) for x in names]
                    row.append(self.rnd.choices(names, weights=w)[0])
            nxt.append(row)
        self.grid = nxt
        self.steps += 1
        self.asked += len(new)
        self.cell_updates += n * n
        return {"step": self.steps, "new_questions": len(new), "cached": len(keys) - len(new),
                "unique_situations": len(self.cache)}

    def image(self, scale: int = 10) -> Image.Image:
        n = len(self.grid)
        img = Image.new("RGB", (n, n))
        for r in range(n):
            for c in range(n):
                img.putpixel((c, r), self.world.color(self.grid[r][c]))
        return img.resize((n * scale, n * scale), Image.NEAREST)

    def census(self) -> dict[str, int]:
        out = {s.name: 0 for s in self.world.states}
        for row in self.grid:
            for x in row:
                out[x] = out.get(x, 0) + 1
        return out


async def run_life(
    idea: str | None = None,
    *,
    world: World | None = None,
    n: int = 24,
    steps: int = 30,
    temperature: float = 0.6,
    on_frame: Callable[[int, Life, dict], None] | None = None,
    on_world: Callable[[World], None] | None = None,
) -> tuple[Life, list[Image.Image], dict]:
    """Design (or take) a world, let Drex seed it, then run `steps` Drex-decided steps."""
    director = None
    if world is None:
        async with DeepInfra() as di:
            world = await design_world(di, idea or "a forest fire")
            director = di.usage.summary()
    if on_world:
        on_world(world)
    async with Drex() as drex:
        grid = await seed(drex, world, n)
        life = Life(world, grid, temperature=temperature)
        frames = [life.image()]
        if on_frame:
            on_frame(0, life, {"step": 0, "new_questions": n * n, "cached": 0, "unique_situations": 0})
        for _ in range(steps):
            info = await life.step(drex)
            frames.append(life.image())
            if on_frame:
                on_frame(life.steps, life, info)
        usage = drex.usage.summary()
    return life, frames, {"drex": usage, "director": director}
