"""Ambiguity experiment (sanity ladder stage 3 / README §5).

Sweeps observation.vision_radius on 4x4 and 5x5, running full agent pipelines
(mock LLM: free + deterministic — the belief machinery under test is the
hard-evidence part: vision collapse, exclusion, motion spread) and records
belief accuracy, capture rate, and sub-game length.

Run: uv run python scripts/vision_sweep.py
Out: artifacts/analysis/vision_sweep.csv + vision_sweep.png
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.agents.agent import LlmAgent
from src.agents.llm_adapter import MockAdapter
from src.common.config import Config
from src.common.schemas import Role
from src.engine.engine import Engine
from tests.conftest import make_config

GRIDS = [(4, 4), (5, 5)]
RADII = [1, 2, 3, 4]
GAMES_PER_CELL = 12


def run_cell(cfg: Config) -> dict:
    engine = Engine(cfg)
    adapter = MockAdapter(seed=cfg.random_seed)
    agents = {r: LlmAgent(r, cfg, adapter) for r in Role}
    accuracies, lengths, cop_wins = [], [], 0
    for g in range(GAMES_PER_CELL):
        state = engine.new_sub_game()
        for a in agents.values():
            a.reset()
        last_msg: dict[Role, str | None] = {r: None for r in Role}
        while not state.terminal:
            role = state.turn
            agent = agents[role]
            d = agent.decide(
                engine.observation(role), engine.legal_actions(role), last_msg[role]
            )
            true_opp = state.thief_pos if role is Role.COP else state.cop_pos
            accuracies.append(agent.belief.accuracy(tuple(true_opp)))
            last_msg[role.opponent] = d.message
            state = engine.apply(role, d.action).state
            engine.state = state
        lengths.append(state.move_count)
        cop_wins += state.winner is Role.COP
    return {
        "mean_belief_err": round(statistics.mean(accuracies), 3),
        "capture_rate": round(cop_wins / GAMES_PER_CELL, 3),
        "mean_length": round(statistics.mean(lengths), 2),
    }


def main() -> None:
    out_dir = Path("artifacts/analysis")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for grid in GRIDS:
        for radius in RADII:
            cfg = make_config(
                grid_size=list(grid),
                observation={"vision_radius": radius},
                llm={"provider": "mock"},
            )
            metrics = run_cell(cfg)
            rows.append({"grid": f"{grid[0]}x{grid[1]}", "vision_radius": radius, **metrics})
            print(rows[-1])

    with (out_dir / "vision_sweep.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for grid in GRIDS:
        name = f"{grid[0]}x{grid[1]}"
        sub = [r for r in rows if r["grid"] == name]
        axes[0].plot(RADII, [r["mean_belief_err"] for r in sub], marker="o", label=name)
        axes[1].plot(RADII, [r["capture_rate"] for r in sub], marker="s", label=name)
    axes[0].set(xlabel="vision radius", ylabel="mean belief error (Chebyshev)",
                title="Ambiguity vs vision radius")
    axes[1].set(xlabel="vision radius", ylabel="cop capture rate",
                title="Outcome vs vision radius")
    for ax in axes:
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "vision_sweep.png", dpi=130)
    print(f"saved {out_dir/'vision_sweep.csv'} and vision_sweep.png")


if __name__ == "__main__":
    main()
