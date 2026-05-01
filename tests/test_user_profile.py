"""src/user/profile.py の SQLite 永続化テスト。"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from src.core.exceptions import ValidationError
from src.user.profile import UserProfileService

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def profile_service() -> Iterator[UserProfileService]:
    service = UserProfileService(db_path=":memory:")
    yield service
    service.close()


def test_set_and_get_profile(profile_service: UserProfileService) -> None:
    uid = "user1"
    profile = {"displayName": "テストユーザー", "role": "student"}
    assert profile_service.set_profile(uid, profile) is True
    result = profile_service.get_profile(uid)
    assert result == profile


def test_list_family_members(profile_service: UserProfileService) -> None:
    admin_uid = "admin1"
    admin_profile = {
        "displayName": "管理者",
        "role": "admin",
        "familyMembers": ["user1", "user2"],
    }
    profile_service.set_profile(admin_uid, admin_profile)
    members = profile_service.list_family_members(admin_uid)
    assert members == ["user1", "user2"]


def test_set_and_get_learning_progress(profile_service: UserProfileService) -> None:
    progress = {"topic": "算数", "status": "in_progress", "score": 80}
    assert profile_service.set_learning_progress("user1", "算数", progress) is True
    result = profile_service.get_learning_progress("user1", "算数")
    assert result == progress


def test_profile_update_overwrites_existing(profile_service: UserProfileService) -> None:
    profile_service.set_profile("user1", {"displayName": "初期", "role": "student"})
    profile_service.set_profile("user1", {"displayName": "更新後", "role": "parent"})
    result = profile_service.get_profile("user1")

    assert result is not None
    assert result["displayName"] == "更新後"
    assert result["role"] == "parent"


def test_learning_progress_update_overwrites_existing(
    profile_service: UserProfileService,
) -> None:
    profile_service.set_learning_progress(
        "user1", "算数", {"topic": "算数", "status": "in_progress", "score": 60}
    )
    profile_service.set_learning_progress(
        "user1", "算数", {"topic": "算数", "status": "completed", "score": 100}
    )
    result = profile_service.get_learning_progress("user1", "算数")

    assert result is not None
    assert result["status"] == "completed"
    assert result["score"] == 100


def test_broken_profile_json_raises_validation_error(
    profile_service: UserProfileService,
) -> None:
    import pytest as _pytest

    profile_service._connection.execute(
        "INSERT INTO user_profiles (uid, profile_json) VALUES (?, ?)",
        ("broken", "{not-json}"),
    )

    with _pytest.raises(ValidationError):
        profile_service.get_profile("broken")


def test_profile_persists_across_instances(tmp_path: Path) -> None:
    db_path = f"data/test_profile_{tmp_path.name}.db"
    first = UserProfileService(db_path=db_path)
    first.set_profile("user1", {"displayName": "永続ユーザー", "role": "student"})
    first.close()

    second = UserProfileService(db_path=db_path)
    result = second.get_profile("user1")
    second.close()

    if os.path.exists(db_path):
        os.remove(db_path)

    assert result is not None
    assert result["displayName"] == "永続ユーザー"


def test_learning_progress_persists_across_instances(tmp_path: Path) -> None:
    db_path = f"data/test_progress_{tmp_path.name}.db"
    first = UserProfileService(db_path=db_path)
    first.set_learning_progress(
        "user1", "算数", {"topic": "算数", "status": "completed", "score": 95}
    )
    first.close()

    second = UserProfileService(db_path=db_path)
    result = second.get_learning_progress("user1", "算数")
    second.close()

    if os.path.exists(db_path):
        os.remove(db_path)

    assert result is not None
    assert result["score"] == 95


def test_get_profile_returns_none_for_unknown_uid(
    profile_service: UserProfileService,
) -> None:
    assert profile_service.get_profile("missing") is None


def test_get_learning_progress_returns_none_for_unknown_uid(
    profile_service: UserProfileService,
) -> None:
    assert profile_service.get_learning_progress("missing", "算数") is None


def test_broken_learning_progress_json_raises_validation_error(
    profile_service: UserProfileService,
) -> None:
    import pytest as _pytest

    profile_service._connection.execute(
        "INSERT INTO learning_progress (uid, topic, progress_json) VALUES (?, ?, ?)",
        ("broken", "算数", "{not-json}"),
    )

    with _pytest.raises(ValidationError):
        profile_service.get_learning_progress("broken", "算数")


def test_invalid_db_path_raises_validation_error() -> None:
    import pytest as _pytest

    with _pytest.raises(ValidationError):
        UserProfileService(db_path="../../outside/app.db")
