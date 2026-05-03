"""
ユーザープロファイル管理サービス雛形
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import suppress
from pathlib import Path

from src.core.exceptions import ValidationError


class UserProfileService:
    """SQLite を用いてユーザープロファイルと学習進捗を永続化する。"""

    _logger = logging.getLogger(__name__)

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
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS family_members (
                    admin_uid TEXT NOT NULL,
                    member_uid TEXT NOT NULL,
                    member_profile_json TEXT NOT NULL,
                    PRIMARY KEY (admin_uid, member_uid)
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
                self._logger.warning("学習進捗データ破損: uid=%s", uid)
                continue
        return result

    def add_family_member(self, admin_uid: str, member_uid: str, member_profile: dict) -> bool:
        """家族メンバーを追加する。自分自身（admin_uid == member_uid）は登録不可。"""
        # 自己参照は許可しない
        if not admin_uid or not admin_uid.strip():
            raise ValidationError("admin_uid が空です")
        if not member_uid or not member_uid.strip():
            raise ValidationError("member_uid が空です")
        if admin_uid == member_uid:
            raise ValidationError("自分自身を家族メンバーに追加することはできません")
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO family_members (admin_uid, member_uid, member_profile_json)
                VALUES (?, ?, ?)
                ON CONFLICT(admin_uid, member_uid)
                DO UPDATE SET member_profile_json = excluded.member_profile_json
                """,
                (admin_uid, member_uid, json.dumps(member_profile, ensure_ascii=False)),
            )
        return True

    def remove_family_member(self, admin_uid: str, member_uid: str) -> bool:
        """家族メンバーを削除する。削除できた場合は True、存在しなかった場合は False を返す。"""
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM family_members WHERE admin_uid = ? AND member_uid = ?",
                (admin_uid, member_uid),
            )
        # rowcount が 1 以上なら実際に削除された
        return cursor.rowcount > 0

    def get_family_members(self, admin_uid: str) -> list[dict]:
        """指定した管理者ユーザーの家族メンバー一覧を返す。件数 0 の場合は空リストを返す。"""
        rows = self._connection.execute(
            "SELECT member_profile_json FROM family_members WHERE admin_uid = ?",
            (admin_uid,),
        ).fetchall()
        result: list[dict] = []
        for (member_profile_json,) in rows:
            try:
                result.append(self._deserialize_payload(member_profile_json))
            except Exception:
                self._logger.warning("家族メンバーデータ破損: admin_uid=%s", admin_uid)
                continue
        return result

    def list_family_members(self, admin_uid: str) -> list:
        """
        管理者の家族メンバー一覧取得（後方互換用ラッパー）
        """
        return self.get_family_members(admin_uid)

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()
