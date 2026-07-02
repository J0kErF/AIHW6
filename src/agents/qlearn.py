"""Tabular Q-Learning (spec §8 — optional, recommended; Bellman + epsilon-greedy).

State  = (own cell, opponent cell) -> (W*H)^2 rows (625 on 5x5).
Actions = the 8 compass moves. Trained by self-play against a random opponent
inside the real engine — no neural nets, no external libs (spec §8 sample style).
All hyper-parameters from config.qlearning. Exports an episode-reward CSV for
the README learning curve.

Train: uv run python -m src.agents.qlearn [--role cop] [--config config.json]
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import numpy as np

from src.common.config import Config, load_config
from src.common.schemas import Action, Cell, Direction, Move, Observation, Role
from src.engine.board import step
from src.engine.engine import Engine
from src.engine.series import random_policy

ACTIONS: list[Direction] = list(Direction)


class QTable:
    def __init__(self, config: Config) -> None:
        w, h = config.grid_size
        self.w, self.h = w, h
        self.q = np.zeros((w * h * w * h, len(ACTIONS)))
        self.cfg = config.qlearning

    def state_index(self, own: Cell, opp: Cell) -> int:
        cells = self.w * self.h
        return (own[0] * self.h + own[1]) * cells + (opp[0] * self.h + opp[1])

    def update(self, s: int, a: int, reward: float, s_next: int, done: bool) -> None:
        best_next = 0.0 if done else float(np.max(self.q[s_next]))
        td_target = reward + self.cfg.discount_factor * best_next
        self.q[s, a] += self.cfg.learning_rate * (td_target - self.q[s, a])

    def best_action(self, s: int, legal_dirs: list[Direction]) -> Direction:
        idxs = [ACTIONS.index(d) for d in legal_dirs]
        return ACTIONS[idxs[int(np.argmax(self.q[s, idxs]))]]

    def save(self, path: str | Path) -> None:
        np.save(str(path), self.q)

    def load(self, path: str | Path) -> None:
        self.q = np.load(str(path))


def train(config: Config, role: Role = Role.COP, episodes: int | None = None,
          out_dir: str | Path = "artifacts/analysis") -> list[float]:
    """Self-play training vs a random opponent. Returns per-episode rewards."""
    qcfg = config.qlearning
    episodes = episodes or qcfg.training_episodes
    rng = random.Random(config.random_seed)
    engine = Engine(config, rng=rng)
    table = QTable(config)
    opponent = random_policy(rng)
    epsilon = qcfg.epsilon_start
    rewards: list[float] = []

    for _ in range(episodes):
        state = engine.new_sub_game()
        total = 0.0
        while not state.terminal:
            turn_role = state.turn
            legal = engine.legal_actions(turn_role)
            if turn_role is not role:
                action = opponent(engine.observation(turn_role), legal) if legal else None
                state = engine.apply(turn_role, action).state if action else state
                engine.state = state
                continue
            own = state.cop_pos if role is Role.COP else state.thief_pos
            opp = state.thief_pos if role is Role.COP else state.cop_pos
            s = table.state_index(tuple(own), tuple(opp))
            legal_dirs = [a.direction for a in legal if isinstance(a, Move)]
            if not legal_dirs:
                break
            if rng.random() < epsilon:
                chosen = rng.choice(legal_dirs)
            else:
                chosen = table.best_action(s, legal_dirs)
            result = engine.apply(turn_role, Move(direction=chosen))
            state = result.state
            engine.state = state
            # reward shaping: win/lose from config scoring, small step cost
            if state.terminal:
                sc = config.scoring
                if state.winner is role:
                    r = float(sc.cop_win if role is Role.COP else sc.thief_win)
                else:
                    r = -float(sc.thief_win if role is Role.COP else sc.cop_win)
            else:
                r = -0.1
            own2 = state.cop_pos if role is Role.COP else state.thief_pos
            opp2 = state.thief_pos if role is Role.COP else state.cop_pos
            s2 = table.state_index(tuple(own2), tuple(opp2))
            table.update(s, ACTIONS.index(chosen), r, s2, state.terminal)
            total += r
        rewards.append(total)
        epsilon = max(qcfg.epsilon_min, epsilon * qcfg.epsilon_decay)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    table.save(out / f"qtable_{role.value}.npy")
    with (out / f"qlearn_rewards_{role.value}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["episode", "reward"])
        writer.writerows(enumerate(rewards))
    return rewards


class QPolicy:
    """SeriesManager-compatible policy backed by a trained table (greedy)."""

    def __init__(self, config: Config, role: Role, table_path: str | Path) -> None:
        self.table = QTable(config)
        self.table.load(table_path)
        self.role = role

    def __call__(self, obs: Observation, legal: list[Action]) -> Action:
        legal_dirs = [a.direction for a in legal if isinstance(a, Move)]
        if not legal_dirs:
            return legal[0]
        opp = obs.opponent_pos or obs.self_pos  # unseen: fall back to own cell anchor
        s = self.table.state_index(tuple(obs.self_pos), tuple(opp))
        return Move(direction=self.table.best_action(s, legal_dirs))


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--role", default="cop", choices=["cop", "thief"])
    args = parser.parse_args()
    config = load_config(args.config)
    role = Role(args.role)
    rewards = train(config, role)
    window = max(1, len(rewards) // 50)
    smooth = np.convolve(rewards, np.ones(window) / window, mode="valid")
    plt.figure(figsize=(8, 4))
    plt.plot(rewards, alpha=0.25, label="episode reward")
    plt.plot(range(window - 1, len(rewards)), smooth, label=f"moving avg ({window})")
    plt.xlabel("episode")
    plt.ylabel("total reward")
    plt.title(f"Tabular Q-Learning ({role.value}) — {config.grid_size[0]}x{config.grid_size[1]}")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = Path("artifacts/analysis") / f"qlearn_curve_{role.value}.png"
    plt.savefig(out, dpi=130)
    print(f"trained {len(rewards)} episodes -> {out}")
    print(f"mean reward first 10%: {np.mean(rewards[:len(rewards)//10]):.2f}  "
          f"last 10%: {np.mean(rewards[-len(rewards)//10:]):.2f}")


if __name__ == "__main__":
    main()
