"""
domain/sample_logic.py のMVPテスト
"""
import pytest
from src.domain.sample_logic import generate_sample_question, get_sample_answer, get_sample_curriculum_reference

def test_generate_sample_question():
    q = generate_sample_question()
    assert q["text"] == "2 + 2 = ?"
    assert q["type"] == "choice"
    assert "4" in q["options"]

def test_get_sample_answer():
    a = get_sample_answer()
    assert a["correct"] == "4"
    assert "足す" in a["explanation"]

def test_get_sample_curriculum_reference():
    ref = get_sample_curriculum_reference()
    assert ref["chapter"] == "第1章"
    assert ref["section"] == "計算の基礎"
    assert 10 in ref["pages"]
