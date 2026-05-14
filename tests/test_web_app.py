"""
web/app.py の Flask アプリテスト
Flask テストクライアントを用いて主要エンドポイントを検証する。
"""

from __future__ import annotations

import logging
import os
from unittest.mock import patch

import pytest
from src.core.exceptions import RateLimitError, ValidationError

# create_app のモジュール初期化用。テスト専用のダミー値を設定する。
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from web.app import app as flask_app
from web.app import create_app


@pytest.fixture()
def client():
    with patch.dict(
        os.environ,
        {
            "AUTH_MODE": "mock",
            "DATABASE_PATH": ":memory:",
            "SECRET_KEY": "test-secret-key",
        },
    ):
        # 元の設定を保存
        original_testing = flask_app.config.get("TESTING", False)
        original_secure = flask_app.config.get("SESSION_COOKIE_SECURE", True)
        try:
            flask_app.config["TESTING"] = True
            # テストクライアントは HTTP 扱いのため Secure Cookie は無効化して検証する
            flask_app.config["SESSION_COOKIE_SECURE"] = False
            with flask_app.test_client() as client:
                yield client
        finally:
            # 設定をリセットして副作用を防ぐ
            flask_app.config["TESTING"] = original_testing
            flask_app.config["SESSION_COOKIE_SECURE"] = original_secure


def test_health_endpoint(client) -> None:
    """/health が 200 を返すことを確認する。"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_startup_raises_when_secret_key_missing() -> None:
    """SECRET_KEY 未設定時は起動エラーになることを確認する。"""
    with (
        patch.dict(os.environ, {"SECRET_KEY": ""}),
        pytest.raises(RuntimeError, match="SECRET_KEY"),
    ):
        create_app()


def test_unauthenticated_index_redirects_to_login(client) -> None:
    """未ログインで / にアクセスした場合は /login へリダイレクトする。"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_page_returns_form(client) -> None:
    """GET /login でログイン画面を表示する。"""
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 200
    assert "<h1>" in response.data.decode("utf-8")


def test_login_creates_session_and_index_returns_200(client) -> None:
    """POST /login でログイン後はセッションが維持され、/ で 200 を返す。"""
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.return_value = {
            "question": {"text": "dummy"}
        }
        login_response = client.post("/login", follow_redirects=False)
        assert login_response.status_code == 302
        assert "/" in login_response.headers["Location"]

        with client.session_transaction() as sess:
            assert "uid" in sess

        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert b"MiraStudy Web" in response.data


def test_index_returns_429_on_rate_limit_error(client) -> None:
    """C-003 の RateLimitError 発生時は 429 を返す。"""
    client.post("/login", follow_redirects=False)
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.side_effect = RateLimitError(
            "rate limit",
            reason_code="C003_rate_limit_exceeded",
        )
        response = client.get("/", follow_redirects=False)
    assert response.status_code == 429
    assert "アクセス制限" in response.data.decode("utf-8")


def test_index_returns_429_on_session_warning_validation_error(client) -> None:
    """C-004 警告発生時は 429 を返す。"""
    client.post("/login", follow_redirects=False)
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.side_effect = ValidationError(
            "session timeout",
            reason_code="C004_session_warning",
        )
        response = client.get("/", follow_redirects=False)
    assert response.status_code == 429
    assert "休憩のお願い" in response.data.decode("utf-8")


def test_index_returns_403_on_session_forced_stop_validation_error(client) -> None:
    """C-004 強制停止発生時は 403 を返す。"""
    client.post("/login", follow_redirects=False)
    with patch("web.app.LearningService") as mock_learning_cls:
        mock_learning_cls.return_value.generate_question.side_effect = ValidationError(
            "session forced stop",
            reason_code="C004_session_forced_stop",
        )
        response = client.get("/", follow_redirects=False)
    assert response.status_code == 403
    assert "セッション終了" in response.data.decode("utf-8")


def test_logout_clears_session_and_redirects_to_login(client) -> None:
    """ログアウトでセッションを破棄し、再度 / は /login へリダイレクトする。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        assert "uid" in sess

    logout_response = client.post("/logout", follow_redirects=False)
    assert logout_response.status_code == 303
    assert "/login" in logout_response.headers["Location"]

    with client.session_transaction() as sess:
        assert "uid" not in sess

    response_after_logout = client.get("/", follow_redirects=False)
    assert response_after_logout.status_code == 302
    assert "/login" in response_after_logout.headers["Location"]


def test_session_cookie_security_flags_enabled() -> None:
    """セッション Cookie のセキュリティ設定が有効であることを確認する。"""
    assert flask_app.config["SESSION_COOKIE_HTTPONLY"] is True
    # テスト fixture で False に上書きされる可能性があるため create_app の既定値を検証する
    with patch.dict(os.environ, {"SECRET_KEY": "test-secret-key"}):
        tmp_app = create_app()
    assert tmp_app.config["SESSION_COOKIE_SECURE"] is True
    assert tmp_app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_login_returns_500_on_auth_failure(client) -> None:
    """POST /login で sign_in_with_google が None の場合は 500 を返す。"""
    with patch("web.app.AuthService") as mock_auth_cls:
        mock_auth = mock_auth_cls.return_value
        mock_auth.sign_in_with_google.return_value = None
        response = client.post("/login")
    assert response.status_code == 500


def test_admin_constraint_metrics_redirects_when_unauthenticated(client) -> None:
    """未ログインで管理者メトリクス API にアクセスした場合はログインへリダイレクトする。"""
    response = client.get("/admin/metrics/constraints", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_constraint_metrics_forbidden_for_non_admin(client) -> None:
    """非管理者ユーザーは管理者メトリクス API にアクセスできない。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "student"

    response = client.get("/admin/metrics/constraints", follow_redirects=False)
    assert response.status_code == 403
    assert response.get_json() == {"error": "forbidden"}


def test_admin_constraint_metrics_forbidden_for_parent(client) -> None:
    """保護者ロールも管理者メトリクス API にはアクセスできない。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "parent"

    response = client.get("/admin/metrics/constraints", follow_redirects=False)
    assert response.status_code == 403
    assert response.get_json() == {"error": "forbidden"}


def test_admin_constraint_metrics_returns_json_for_admin(client) -> None:
    """管理者ユーザーは制約メトリクス JSON を取得できる。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    expected = {
        "c003_user_limit": 1,
        "c003_global_limit": 0,
        "c004_session_warning": 2,
        "c004_session_forced_stop": 0,
        "total_events": 3,
        "unique_users_total": 2,
        "unique_users_by_event": {
            "c003_user_limit": 1,
            "c003_global_limit": 0,
            "c004_session_warning": 2,
            "c004_session_forced_stop": 0,
        },
    }
    with patch("web.app.get_constraint_metrics", return_value=expected):
        response = client.get("/admin/metrics/constraints", follow_redirects=False)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_admin_constraint_metrics_emits_audit_log_for_admin(client, caplog) -> None:
    """N-041: 管理者アクセス時に監査ログが出力される。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    expected = {
        "c003_user_limit": 0,
        "c003_global_limit": 0,
        "c004_session_warning": 0,
        "c004_session_forced_stop": 0,
        "total_events": 0,
        "unique_users_total": 0,
        "unique_users_by_event": {
            "c003_user_limit": 0,
            "c003_global_limit": 0,
            "c004_session_warning": 0,
            "c004_session_forced_stop": 0,
        },
    }
    caplog.set_level(logging.INFO)
    with patch("web.app.get_constraint_metrics", return_value=expected):
        response = client.get("/admin/metrics/constraints", follow_redirects=False)

    assert response.status_code == 200
    assert "admin_constraint_metrics allowed" in caplog.text


def test_admin_constraint_metrics_emits_audit_log_for_denied_access(client, caplog) -> None:
    """N-041: 拒否時にも監査ログが出力される。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "student"

    caplog.set_level(logging.WARNING)
    response = client.get("/admin/metrics/constraints", follow_redirects=False)

    assert response.status_code == 403
    assert "admin_constraint_metrics denied" in caplog.text


def test_admin_constraint_metrics_contract_keys_and_types(client) -> None:
    """N-038: 管理者メトリクス API の主要スキーマを契約テストで固定する。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    expected = {
        "c003_user_limit": 1,
        "c003_global_limit": 0,
        "c004_session_warning": 2,
        "c004_session_forced_stop": 0,
        "total_events": 3,
        "unique_users_total": 2,
        "unique_users_by_event": {
            "c003_user_limit": 1,
            "c003_global_limit": 0,
            "c004_session_warning": 2,
            "c004_session_forced_stop": 0,
        },
    }
    with patch("web.app.get_constraint_metrics", return_value=expected):
        response = client.get("/admin/metrics/constraints", follow_redirects=False)

    data = response.get_json()
    assert response.status_code == 200
    assert set(data.keys()) == {
        "c003_user_limit",
        "c003_global_limit",
        "c004_session_warning",
        "c004_session_forced_stop",
        "total_events",
        "unique_users_total",
        "unique_users_by_event",
    }
    assert isinstance(data["c003_user_limit"], int)
    assert isinstance(data["unique_users_by_event"], dict)


def test_admin_constraint_metrics_history_returns_events_for_admin(client) -> None:
    """N-037: 管理者は制約イベント履歴 API を取得できる。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    history = [{"timestamp": "2026-05-14T00:00:00Z", "event_name": "c003_user_limit", "uid": "u1"}]
    with patch("web.app.get_constraint_recent_events", return_value=history):
        response = client.get("/admin/metrics/constraints/history", follow_redirects=False)

    assert response.status_code == 200
    assert response.get_json() == {"events": history, "limit": 50, "offset": 0, "count": 1}


def test_admin_constraint_metrics_history_supports_pagination(client) -> None:
    """N-039: 履歴 API が limit/offset を受け取り、ページングできる。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    history = [
        {"timestamp": f"2026-05-14T00:00:0{i}Z", "event_name": "c003_user_limit", "uid": f"u{i}"}
        for i in range(5)
    ]
    with patch(
        "web.app.get_constraint_recent_events",
        return_value=history[1:3],
    ) as mock_get_events:
        response = client.get(
            "/admin/metrics/constraints/history?limit=2&offset=1",
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.get_json() == {"events": history[1:3], "limit": 2, "offset": 1, "count": 2}
    mock_get_events.assert_called_once_with(limit=2, offset=1)


def test_admin_constraint_metrics_history_rejects_negative_pagination(client) -> None:
    """N-039: 負の limit/offset は 400 で拒否する。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    response = client.get(
        "/admin/metrics/constraints/history?limit=-1&offset=0",
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_pagination"}


def test_admin_constraint_metrics_history_caps_limit(client) -> None:
    """N-039: 上限を超える limit は安全側に丸められる。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    with patch("web.app.get_constraint_recent_events", return_value=[]) as mock_get_events:
        response = client.get(
            "/admin/metrics/constraints/history?limit=999&offset=0",
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.get_json() == {"events": [], "limit": 200, "offset": 0, "count": 0}
    mock_get_events.assert_called_once_with(limit=999, offset=0)


def test_admin_constraint_metrics_history_filters_by_event_name(client) -> None:
    """N-042: 履歴 API が event_name で絞り込める。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    filtered = [
        {
            "timestamp": "2026-05-14T00:00:00Z",
            "event_name": "c004_session_warning",
            "uid": "u1",
        }
    ]
    with patch(
        "web.app.get_constraint_recent_events",
        return_value=filtered,
    ) as mock_get_events:
        response = client.get(
            "/admin/metrics/constraints/history?limit=5&offset=0&event_name=c004_session_warning",
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "events": filtered,
        "limit": 5,
        "offset": 0,
        "event_name": "c004_session_warning",
        "count": 1,
    }
    mock_get_events.assert_called_once_with(
        limit=5,
        offset=0,
        event_name="c004_session_warning",
    )


def test_admin_constraint_metrics_history_supports_csv_export(client) -> None:
    """N-043: 履歴 API が CSV 形式でエクスポートできる。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    history = [
        {
            "timestamp": "2026-05-14T00:00:00Z",
            "event_name": "c003_user_limit",
            "uid": "u1",
        },
        {
            "timestamp": "2026-05-14T00:00:01Z",
            "event_name": "c004_session_warning",
            "uid": "u2",
        },
    ]
    with patch("web.app.get_constraint_recent_events", return_value=history) as mock_get_events:
        response = client.get(
            "/admin/metrics/constraints/history?limit=2&offset=0&format=csv",
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.headers["Content-Disposition"] == (
        "attachment; filename=constraint-events-history.csv"
    )
    assert response.data.decode("utf-8").splitlines() == [
        "timestamp,event_name,uid",
        "2026-05-14T00:00:00Z,c003_user_limit,u1",
        "2026-05-14T00:00:01Z,c004_session_warning,u2",
    ]
    mock_get_events.assert_called_once_with(limit=2, offset=0)


def test_admin_constraint_metrics_history_rejects_invalid_export_format(client) -> None:
    """N-043: 未知の export 形式は 400 で拒否する。"""
    client.post("/login", follow_redirects=False)
    with client.session_transaction() as sess:
        sess["role"] = "admin"

    response = client.get(
        "/admin/metrics/constraints/history?limit=5&offset=0&format=xml",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_export_format"}
