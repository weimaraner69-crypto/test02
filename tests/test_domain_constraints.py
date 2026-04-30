"""
domain/constraints.py の品質フレームワークテスト

境界値分析:
  loss_rate > -2.0          → C099_ok     / RUNNING  / allowed=True
  -2.0 <= loss_rate > -3.0  → C099_warn   / RUNNING  / allowed=True
  -3.0 <= loss_rate > -5.0  → C099_degraded / DEGRADED / allowed=False
  loss_rate <= -5.0         → C099_halt   / HALTED   / allowed=False
"""

from src.domain.constraints import ConstraintResult, SystemState, evaluate_loss_constraint

# ------------------------------------------------------------------
# 正常系: しきい値ちょうどの動作確認（同値クラス）
# ------------------------------------------------------------------


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


# ------------------------------------------------------------------
# 境界値テスト: 各しきい値の直上・直下
# ------------------------------------------------------------------


def test_loss_constraint_zero():
    """損失ゼロ（通常運用）は OK"""
    result = evaluate_loss_constraint(0.0)
    assert result.allowed is True
    assert result.reason_code == "C099_ok"
    assert result.next_state == SystemState.RUNNING


def test_loss_constraint_just_above_warn_threshold():
    """-2.0 より上（-1.9）は C099_ok"""
    result = evaluate_loss_constraint(-1.9)
    assert result.reason_code == "C099_ok"
    assert result.next_state == SystemState.RUNNING


def test_loss_constraint_just_below_warn_threshold():
    """-2.0 より下（-2.1）は C099_warn"""
    result = evaluate_loss_constraint(-2.1)
    assert result.reason_code == "C099_warn"
    assert result.next_state == SystemState.RUNNING
    assert result.allowed is True


def test_loss_constraint_just_below_degraded_threshold():
    """-3.0 より下（-3.1）は C099_degraded"""
    result = evaluate_loss_constraint(-3.1)
    assert result.reason_code == "C099_degraded"
    assert result.next_state == SystemState.DEGRADED
    assert result.allowed is False


def test_loss_constraint_just_below_halt_threshold():
    """-5.0 より下（-5.1）は C099_halt"""
    result = evaluate_loss_constraint(-5.1)
    assert result.reason_code == "C099_halt"
    assert result.next_state == SystemState.HALTED
    assert result.allowed is False


# ------------------------------------------------------------------
# ConstraintResult の属性確認
# ------------------------------------------------------------------


def test_constraint_result_fields():
    """ConstraintResult が 3 属性を持つことを確認"""
    cr = ConstraintResult(True, "C099_ok", SystemState.RUNNING)
    assert cr.allowed is True
    assert cr.reason_code == "C099_ok"
    assert cr.next_state == SystemState.RUNNING
