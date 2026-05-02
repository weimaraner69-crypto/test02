"""
ユーザープロファイル管理サービス雛形
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import suppress
from pathlib import Path

from src.core.exceptions import ValidationError


class UserProfileService:
    """SQLite を用いてユーザープロファイルと学習進捗を永続化する。"""

    def __init__(self, db_path: str = ":memory:"):
        path_obj = Path(db_path)
        if db_path != ":memory:" and (path_obj.is_absolute() or ".." in path_obj.parts):
            raise ValidationError(f"不正な DATABASE_PATH が指定されました: {db_path!r}")
        self._db_path = db_path
        if db_path != ":memory:":
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(db_path)
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """必要なテーブルを初期化する。"""
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    uid TEXT PRIMARY KEY,
                    profile_json TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_progress (
                    uid TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    progress_json TEXT NOT NULL,
                    PRIMARY KEY (uid, topic)
                )
                """
            )

    def close(self) -> None:
        """DB 接続をクローズする。呼び出し側が明示的に管理する。"""
        self._connection.close()

    def _deserialize_payload(self, payload: str) -> dict:
        """保存済み JSON を dict に復元する。"""
        try:
            return json.loads(payload)
        except json.JSONDecodeError as error:
            raise ValidationError("保存済みデータが破損しています") from error

    def get_profile(self, uid: str) -> dict | None:
        """
        ユーザープロファイル取得
        """
        row = self._connection.execute(
            "SELECT profile_json FROM user_profiles WHERE uid = ?",
            (uid,),
        ).fetchone()
        if row is None:
            return None
        return self._deserialize_payload(row[0])

    def set_profile(self, uid: str, profile: dict) -> bool:
        """
        ユーザープロファイル保存/更新
        """
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO user_profiles (uid, profile_json)
                VALUES (?, ?)
                ON CONFLICT(uid) DO UPDATE SET profile_json = excluded.profile_json
                """,
                (uid, json.dumps(profile, ensure_ascii=False)),
            )
        return True

    def get_learning_progress(self, uid: str, topic: str) -> dict | None:
        """学習進捗を取得する。"""
        row = self._connection.execute(
            "SELECT progress_json FROM learning_progress WHERE uid = ? AND topic = ?",
            (uid, topic),
        ).fetchone()
        if row is None:
            return None
        return self._deserialize_payload(row[0])

    def set_learning_progress(self, uid: str, topic: str, progress: dict) -> bool:
        """学習進捗を保存/更新する。"""
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO learning_progress (uid, topic, progress_json)
                VALUES (?, ?, ?)
                ON CONFLICT(uid, topic) DO UPDATE SET progress_json = excluded.progress_json
                """,
                (uid, topic, json.dumps(progress, ensure_ascii=False)),
            )
        return True

    def list_all_learning_progress(self, uid: str) -> list[dict]:
        """指定ユーザーのすべての学習進捗を一覧で返す。"""
        rows = self._connection.execute(
            "SELECT progress_json FROM learning_progress WHERE uid = ?",
            (uid,),
        ).fetchall()
        result: list[dict] = []
        for (progress_json,) in rows:
            try:
                result.append(self._deserialize_payload(progress_json))
            except Exception:
                continue
        return result

    def list_family_members(self, admin_uid: str) -> list:
        """
        管理者の家族メンバー一覧取得（雛形）
        """
        # 実際はprofile['familyMembers']参照
        admin = self.get_profile(admin_uid)
        return admin.get("familyMembers", []) if admin else []

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()
