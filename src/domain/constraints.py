"""
品質フレームワーク：制約判定・状態遷移
"""
from enum import Enum
from typing import Tuple

class SystemState(Enum):
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    HALTED = "HALTED"

class ConstraintResult:
    def __init__(self, allowed: bool, reason_code: str, next_state: SystemState):
        self.allowed = allowed
        self.reason_code = reason_code
        self.next_state = next_state

# しきい値定義
LOSS_THRESHOLDS = [
    (-2.0, "C099_warn", SystemState.RUNNING),
    (-3.0, "C099_degraded", SystemState.DEGRADED),
    (-5.0, "C099_halt", SystemState.HALTED),
]

def evaluate_loss_constraint(loss_rate: float) -> ConstraintResult:
    """
    日次損失率に基づき制約判定・状態遷移を返す
    """
    for threshold, code, state in reversed(LOSS_THRESHOLDS):
        if loss_rate <= threshold:
            allowed = state == SystemState.RUNNING
            return ConstraintResult(allowed, code, state)
    return ConstraintResult(True, "C099_ok", SystemState.RUNNING)
