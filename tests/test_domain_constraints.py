"""
domain/constraints.py の品質フレームワークテスト
"""
import pytest
from src.domain.constraints import evaluate_loss_constraint, SystemState

def test_loss_constraint_ok():
    result = evaluate_loss_constraint(-1.0)
    assert result.allowed is True
    assert result.reason_code == "C099_ok"
    assert result.next_state == SystemState.RUNNING

def test_loss_constraint_warn():
    result = evaluate_loss_constraint(-2.0)
    assert result.allowed is True
    assert result.reason_code == "C099_warn"
    assert result.next_state == SystemState.RUNNING

def test_loss_constraint_degraded():
    result = evaluate_loss_constraint(-3.0)
    assert result.allowed is False
    assert result.reason_code == "C099_degraded"
    assert result.next_state == SystemState.DEGRADED

def test_loss_constraint_halt():
    result = evaluate_loss_constraint(-5.0)
    assert result.allowed is False
    assert result.reason_code == "C099_halt"
    assert result.next_state == SystemState.HALTED
