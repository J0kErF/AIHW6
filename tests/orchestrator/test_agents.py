"""Parser, belief, and agent-guard unit tests (Track C)."""
import pytest

from src.agents.agent import LlmAgent
from src.agents.belief import BeliefGrid
from src.agents.llm_adapter import MockAdapter
from src.agents.parser import ParseFailure, parse_decision, to_engine_action
from src.common.schemas import Direction, Move, Pass, PlaceBarrier, Role
from src.engine.engine import Engine
from tests.conftest import make_config


# -- parser -------------------------------------------------------------------
def test_parse_clean_json():
    d = parse_decision('{"action": "NE", "message": "hi", "belief": [2, 3]}')
    assert d.action == "NE" and d.belief == (2, 3)
    assert to_engine_action(d) == Move(direction=Direction.NE)


def test_parse_json_inside_chatty_text():
    text = 'Sure! Here is my move:\n```json\n{"action": "barrier", "message": "blocked!"}\n```'
    d = parse_decision(text)
    assert isinstance(to_engine_action(d), PlaceBarrier)


def test_parse_rejects_garbage_and_unknown_action():
    with pytest.raises(ParseFailure):
        parse_decision("I will wander around")
    with pytest.raises(ParseFailure):
        parse_decision('{"action": "TELEPORT", "message": "zap"}')


# -- belief -------------------------------------------------------------------
def test_belief_vision_collapse_and_exclusion():
    b = BeliefGrid((5, 5))
    b.observe((0, 0), 2, opponent_pos=(4, 4))
    assert b.argmax() == (4, 4) and b.p[4, 4] == pytest.approx(1.0)
    b2 = BeliefGrid((5, 5))
    b2.observe((0, 0), 2, opponent_pos=None)  # not seen: vision disk excluded
    assert b2.p[0, 0] == 0.0 and b2.p[2, 2] == 0.0 and b2.p[4, 4] > 0


def test_belief_motion_spread_and_accuracy():
    b = BeliefGrid((5, 5))
    b.observe((0, 0), 1, opponent_pos=(2, 2))   # certainty at (2,2)
    b.motion_spread(barriers=[])                # now spread over neighbors
    assert b.p[2, 2] > 0 and b.p[3, 3] > 0 and b.p[0, 0] == 0.0
    assert b.accuracy((2, 2)) <= 1


def test_belief_hint_blend_deception_aware():
    b = BeliefGrid((5, 5), hint_weight=0.25)
    b.apply_hint((1, 1))
    assert b.argmax() == (1, 1)          # hint tilts...
    assert b.p[1, 1] < 0.5               # ...but never dominates (deception-aware)
    b.apply_hint((99, 99))               # out-of-board hints ignored
    assert b.argmax() == (1, 1)


# -- agent guard/fallback -------------------------------------------------------
class BrokenLlm:
    def complete(self, system, user):
        return "no json here, ever"


class IllegalMoveLlm:
    def complete(self, system, user):
        return '{"action": "N", "message": "going north into the wall"}'


def agent_env(llm, role=Role.THIEF):
    cfg = make_config(
        grid_size=[3, 3],
        start_positions={"mode": "fixed", "fixed_cop": [0, 0], "fixed_thief": [2, 0]},
    )
    engine = Engine(cfg)
    engine.new_sub_game()
    return LlmAgent(role, cfg, llm), engine


def test_unparseable_llm_falls_back_to_heuristic():
    agent, engine = agent_env(BrokenLlm())
    obs = engine.observation(Role.THIEF)
    legal = engine.legal_actions(Role.THIEF)
    d = agent.decide(obs, legal, "the cop says hello")
    assert d.used_fallback and d.action in legal and d.message


def test_illegal_llm_action_is_guarded():
    # thief at (2,0): N is off-board -> guard must substitute a legal move
    agent, engine = agent_env(IllegalMoveLlm())
    d = agent.decide(engine.observation(Role.THIEF), engine.legal_actions(Role.THIEF), None)
    assert d.used_fallback and d.action in engine.legal_actions(Role.THIEF)


def test_mock_adapter_full_pipeline_produces_legal_actions():
    agent, engine = agent_env(MockAdapter(seed=1), role=Role.THIEF)
    for _ in range(5):
        if engine.state.terminal:
            break
        role = engine.state.turn
        a = LlmAgent(role, agent.config, MockAdapter(seed=2))
        d = a.decide(engine.observation(role), engine.legal_actions(role), None)
        engine.apply(role, d.action)
        assert isinstance(d.message, str) and len(d.message) > 5
