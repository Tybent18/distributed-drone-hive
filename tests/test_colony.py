"""Contracts for the operator-governed game simulator (not Stage One claims)."""

import pytest

from drone_hive.colony import ColonyMission


def crew(m: ColonyMission) -> None:
    m.assign_role(0, "queen", 1)
    m.assign_role(1, "handler", 0)
    m.assign_role(2, "worker", 1)


def test_assign_roles_only_before_launch() -> None:
    m = ColonyMission(seed=7, count=4)
    crew(m)
    assert m.metrics()["queens"] == 1
    assert m.metrics()["handlers"] == 1
    m.start()
    with pytest.raises(ValueError):
        m.assign_role(3, "worker", 1)


def test_assign_single_queen_per_nest() -> None:
    m = ColonyMission(count=4)
    m.assign_role(0, "queen", 1)
    with pytest.raises(ValueError):
        m.assign_role(3, "queen", 1)


def test_failure_requires_operator_approval_and_handler() -> None:
    m = ColonyMission(seed=7, count=4)
    crew(m)
    assert m.is_hive_connected(2)
    m.fail_hive(1)
    assert not m.is_hive_connected(2)
    assert m.pending_egg == 0
    assert not m.eggs[0].active
    assert m.authorize_contingency()
    assert m.eggs[0].deploying and not m.eggs[0].active
    m.start()
    for _ in range(35):
        m.step()
        if m.eggs[0].active:
            break
    assert m.eggs[0].active
    assert m.is_hive_connected(2)
    assert any("activated egg" in event for event in m.events)


def test_no_handler_cannot_approve_failure_repair() -> None:
    m = ColonyMission(count=4)
    m.assign_role(2, "worker", 1)
    m.fail_hive(1)
    assert m.pending_egg == 0
    assert not m.authorize_contingency()


def test_operator_link_loss_disables_eggs_and_retreats() -> None:
    m = ColonyMission(count=4)
    crew(m)
    m.fail_hive(1)
    assert m.authorize_contingency()
    m.lose_operator_link()
    assert not m.operator_connected
    assert not any(egg.active for egg in m.eggs)
    assert not any(egg.deploying for egg in m.eggs)
    assert not m.authorize_contingency()
    assert m.bees[0].state == "return_root"
    assert m.bees[2].state == "return_home"


def test_deterministic_mission_and_no_motion_without_start() -> None:
    a, b = ColonyMission(8, 6), ColonyMission(8, 6)
    crew(a)
    crew(b)
    assert a.step()["tick"] == 0
    a.start()
    b.start()
    for _ in range(12):
        assert a.step() == b.step()
    assert [(bee.x, bee.y, bee.energy, bee.state) for bee in a.bees] == [
        (bee.x, bee.y, bee.energy, bee.state) for bee in b.bees
    ]


def test_paused_infrastructure_editing() -> None:
    m = ColonyMission(count=4)
    assert m.add_hive(75, 35) == 3
    assert m.add_egg(75, 40) == 2
    m.assign_role(2, "worker", 1)
    m.start()
    with pytest.raises(ValueError):
        m.add_hive(80, 35)
