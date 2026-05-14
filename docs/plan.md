# 計画（Plan）

## 運用ルール

- この文書は「現在の計画」を表す。過去ログを増やさない。
- 変更履歴は直近10件までとし、重要判断は ADR に移す。
- 自動実行の対象は「Next」のみとする。Backlog は自動で着手しない。

## 現状（Status）

- フェーズ：**Advanced**（N-001〜N-043 完了）
- ブロッカー：なし
- 直近の重要決定：N-043 まで完了。Next を N-044〜N-045 に再編（2026-05-14）

## ロードマップ（概略）

| Phase | 名称       | 目標                                  | 期間目安  |
| ----- | ---------- | ------------------------------------- | --------- |
| 0     | Foundation | CI 品質ゲート確立、リポジトリ基盤整備 | 1〜2 週間 |
| 1     | MVP        | 最小限の機能パイプラインを確立        | 2〜4 週間 |
| 2     | Quality    | 制約・品質フレームワークの実装        | 2〜3 週間 |
| 3     | Hardening  | 機能拡充、設定管理強化                | 3〜4 週間 |
| 4     | Advanced   | 高度な機能、研究開発                  | 継続      |

※ 期間目安は目標であり、検証結果に基づき随時見直す。

## 今月のゴール

- G1 CI を含む開発基盤を確立する（✅ N-001 完了）
- G2 MVP パイプラインを一本通す（✅ N-002 完了）
- G3 品質ゲートと監査手順を整備する（✅ N-003 完了）

## Next（自動実行対象：最大3件）

1. **N-044** 制約イベント履歴の保持期間・自動削除
2. **N-045** 管理者監査ログの request_id 付与

## Backlog（保留）

- **✅ 完了（2026-04-30）**
- 目的：CI（lint/type/test/policy_check）を安定稼働させ、最低限の品質を自動判定できるようにする
- 受入条件：
  - ✅ pyproject.toml 整備（ruff/mypy/pytest 設定）
  - ✅ パッケージ構造配置（各サブパッケージに `__init__.py`）
  - ✅ CI 全ステップ通過（policy/lint/format/type/test）
  - ✅ ポリシーチェック誤検知なし
- 依存：なし
- 触る領域：プロジェクト設定, CI, ソースディレクトリ

### N-002 MVP パイプラインの確立

- **✅ 完了（2026-04-30）**
- 目的：認証→プロファイル→権限判定→Drive→Gemini の MVP パイプラインが一本で動作する状態を作る
- 受入条件：
  - ✅ `src/app.py` の `main()` が例外なく実行できる
  - ✅ 各サービスのインタフェースが整合し、型エラーがない
  - ✅ 統合テスト `tests/test_main_pipeline.py` が追加・通過する
  - ✅ CI（lint/type/test）がすべて通過する
- 依存：N-001
- 触る領域：src/app.py, tests/

### N-003 品質フレームワークの整備

- **✅ 完了（2026-04-30）**
- 目的：制約・品質の基盤を作る
- 受入条件：
  - ✅ `src/domain/constraints.py` の制約判定ロジックがテストで検証されている（境界値10ケース含む）
  - ✅ カバレッジ 80% 以上を CI で計測・記録する（達成値：99.32%）
  - ✅ `pytest --cov` が CI に追加されている
- 依存：N-002
- 触る領域：src/domain/, tests/, ci.yml

### N-004 設定管理・エラーハンドリングの強化

- **✅ 完了（2026-05-02）**
- 目的：本番運用に向けて設定の外部化と統一的なエラーハンドリングを整備する
- 受入条件：
  - ✅ 環境変数による設定管理（`AppConfig` dataclass + `from_env()`）が実装されている
  - ✅ 全サービスで `DomainError` 系例外を適切にキャッチ・ログ出力している
  - ✅ ローカル実行で設定ロード → 処理 → エラー時の動作が一貫して確認できる
  - ✅ CI が通過する（117 passed, カバレッジ 98.50%）
- 依存：N-003
- 触る領域：`src/core/`, `src/app.py`, `tests/`

### N-005 認証・権限の本番化

- **✅ 完了（2026-05-02）**
- 目的：スタブ実装から実際の認証（Google OAuth など）と権限制御に切り替える
- 受入条件：
  - ✅ 認証フローが `AuthMode.MOCK`（固定ダミーユーザー）で動作する
  - ✅ `AuthMode.GOOGLE` は将来実装のプレースホルダー（`NotImplementedError`）として設置済み
  - ✅ `AUTH_MODE` 環境変数でモード切り替え可能（不正値は `mock` にフォールバック）
  - ✅ 権限ロール（student / admin / parent）に基づくアクセス制御がエンドツーエンドで機能する
  - ✅ プロファイル未取得時はフェイルクローズ（`AuthorizationError` 送出）する
  - ✅ テストでモック認証を使用し CI が通過する（128 passed, カバレッジ 96.83%）
- 依存：N-004
- 触る領域：`src/auth/`, `src/permissions/`, `tests/`

### N-006 データ永続化

- **✅ 完了（2026-05-02）**
- 目的：インメモリ状態をデータベース（SQLite または PostgreSQL）に移行する
- 受入条件：
  - ✅ ユーザープロファイル・学習進捗が DB に保存・取得できる
  - ✅ マイグレーション手順が `docs/runbook.md` に記載されている
  - ✅ テスト用インメモリ DB（SQLite + pytest-fixtures）で CI が通過する（140 passed, カバレッジ 97.12%）
- 依存：N-005
- 触る領域：`src/`, `tests/`, `docs/runbook.md`

### N-007 子供向け学習機能の実装

- **✅ 完了（2026-05-02）**
- 目的：学年別コンテンツ配信・問題生成・進捗管理を実装し、子供が学年に合った問題を解ける機能を提供する
- 受入条件：
  - ✅ `Grade`（1〜6）と `Subject` による学年別コンテンツ取得ができる
  - ✅ Gemini 連携で問題生成（`LearningService.generate_question`）が動作する
  - ✅ 回答記録（正誤）を SQLite に保存・取得できる
  - ✅ 進捗サマリー（科目別正答率）を取得できる
  - ✅ メインパイプライン（`src/app.py`）に学習機能が統合されている
  - ✅ テストが追加され CI が通過する（178 passed, カバレッジ 97.30%）
- 依存：N-006
- 触る領域：`src/learning/`, `src/domain/`, `src/app.py`, `tests/`

### N-008 FR-020 拡充（理科・社会・英語カタログ）

- **✅ 完了（2026-05-03）**
- 目的：学習コンテンツの対象科目を拡張し、理科・社会・英語を含む学年別カタログを整備する
- 受入条件：
  - ✅ `Subject` に理科・社会・英語が追加されている
  - ✅ 5科目 × 6学年のコンテンツカタログが提供されている
  - ✅ 学年・科目ごとの取得ロジックがテストで検証されている
  - ✅ CI が通過する（196 passed, カバレッジ 98.98%）
- 依存：N-007
- 触る領域：`src/domain/learning.py`、`src/learning/`、`tests/`

### N-009 observability 統合

- **✅ 完了（2026-05-03）**
- 目的：主要処理にトレースを導入し、OpenTelemetry ベースの observability を整備する
- 受入条件：
  - ✅ `src/observability/tracing.py` に tracer 初期化と decorator 群が実装されている
  - ✅ auth / gemini / learning の主要処理に trace decorator が適用されている
  - ✅ OpenTelemetry 未導入環境でも no-op で動作する
  - ✅ テストが追加され CI が通過する（190 passed, カバレッジ 97.36%）
- 依存：N-008
- 触る領域：`src/observability/`、`src/auth/service.py`、`src/gemini/service.py`、`src/learning/service.py`、`tests/`

### N-010 NFR-030 CLI/runbook 整備

- **✅ 完了（2026-05-03）**
- 目的：ローカル実行・検証・Docker 実行の運用性を高めるため、CLI と runbook を整備する
- 受入条件：
  - ✅ `Makefile` に setup / run / test / ci / docker 系ターゲットが追加されている
  - ✅ `Dockerfile` で実行イメージを構築できる
  - ✅ `docs/runbook.md` に実行・復旧・ロールバック手順が記載されている
  - ✅ CI が通過する（190 passed, カバレッジ 97.30%）
- 依存：N-009
- 触る領域：`Makefile`、`Dockerfile`、`docs/runbook.md`

### N-011 Google OAuth 本実装

- **✅ 完了（2026-05-04）**
- 目的：`AuthMode.GOOGLE` のプレースホルダーを Google OAuth 2.0 で本実装し、本番環境の認証フローを完成させる
- 受入条件：
  - ✅ Google OAuth 2.0 フロー実装（`google-auth-oauthlib` 利用）
  - ✅ 環境変数 `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` 設定対応
  - ✅ ローカル開発用リダイレクト URL（`http://localhost:8080/auth/callback`）対応
  - ✅ テストで Google モードの挙動を検証している
  - ✅ CI 通過（209 passed, カバレッジ 92.89%）
  - ✅ `.env.example` に Google OAuth 設定例を追記
  - ✅ `docs/runbook.md` に Google Cloud Console 設定手順を記載
- 依存：N-010
- 触る領域：`src/auth/`、`src/core/config.py`、`.env.example`、`tests/`、`docs/runbook.md`

### N-012 docs Markdown lint 整理

- **✅ 完了（2026-05-04）**
- 目的：`docs/plan.md` と `docs/runbook.md` に残っていた Markdown lint 警告を解消し、正本文書の保守性を上げる
- 受入条件：
  - ✅ `docs/plan.md` の bare URL 警告を解消している
  - ✅ `docs/runbook.md` の MD032 / MD060 / MD012 を解消している
  - ✅ `get_errors` で対象ドキュメントの diagnostics が 0 件である
- 依存：N-011
- 触る領域：`docs/plan.md`、`docs/runbook.md`

### N-013 正本ドキュメント整合性回復

- **✅ 完了（2026-05-04）**
- 目的：`docs/requirements.md` と `docs/architecture.md` を N-011（Google OAuth 本実装）の実装に合わせて整合させる
- 受入条件：
  - ✅ requirements.md に FR-001 の Google OAuth 動作・失敗時仕様が正確に記載されている
  - ✅ architecture.md の auth/ 責務記述が実装と整合している
  - ✅ `get_errors` で対象ドキュメントの diagnostics が 0 件である
- 依存：N-012
- 触る領域：`docs/requirements.md`、`docs/architecture.md`

### N-014 app.py ログ整理・web/app.py セキュリティ修正

- **✅ 完了（2026-05-04）**
- 目的：`src/app.py` の重複コードを排除しログを構造化する。`web/app.py` のハードコード API キーおよび XSS 脆弱性を修正する
- 受入条件：
  - ✅ `src/app.py` の重複 Gemini 呼び出しを排除し、すべての `print()` を `logger` に置換
  - ✅ `web/app.py` の `API_KEY="dummy-key"` を環境変数に変更
  - ✅ XSS（f-string テンプレート）を Jinja2 `{{ }}` オートエスケープに修正
  - ✅ `user is None` ガード・`profile_service.close()` を finally に追加
  - ✅ CI 通過（212 passed, カバレッジ 93.22%）
- 依存：N-013
- 触る領域：`src/app.py`、`web/app.py`

### N-015 家族メンバー管理 API

- **✅ 完了（2026-05-04）**
- 目的：`UserProfileService` に家族メンバーの追加・削除・一覧取得 API を実装する
- 受入条件：
  - ✅ `family_members` テーブルがスキーマに追加されている
  - ✅ `add_family_member` / `remove_family_member` / `get_family_members` が実装されている
  - ✅ 自己参照・空 uid のバリデーションがある
  - ✅ CI 通過（214 passed, カバレッジ 91.95%）
- 依存：N-014
- 触る領域：`src/user/profile.py`、`tests/`

### N-016 バリデーション強化・Gemini リトライ

- **✅ 完了（2026-05-04）**
- 目的：`LearningService` に入力バリデーション、`GeminiService` にリトライ機構を追加する
- 受入条件：
  - ✅ `validate_grade` が `LearningService` のエントリポイントで呼ばれている
  - ✅ Gemini 呼び出しで最大 3 回・指数バックオフ（1s/2s/4s）のリトライが実装されている
  - ✅ `ValidationError` / `ValueError` は即再送出（リトライしない）
  - ✅ CI 通過（209 passed, カバレッジ 90.53%）
- 依存：N-015
- 触る領域：`src/learning/service.py`、`src/gemini/service.py`

### N-017 OAuth トークンローカル永続化

- **✅ 完了（2026-05-04）**
- 目的：Google OAuth ログイン後のトークンを `TOKEN_PATH`（既定 `data/token.json`）に保存し、次回起動時のブラウザ認証を省略する
- 受入条件：
  - ✅ `AuthService.__init__` に `token_path` 引数を追加
  - ✅ 有効なトークンファイルがある場合はブラウザ認証をスキップする
  - ✅ 認証後に `creds.to_json()` でトークンをファイルに永続化する
  - ✅ `data/` を `.gitignore` に追加（P-002）
  - ✅ `.env.example` に `TOKEN_PATH` を追加
  - ✅ CI 通過（212 passed, カバレッジ 94.06%）
- 依存：N-016
- 触る領域：`src/auth/service.py`、`src/core/config.py`、`src/app.py`、`tests/`、`.env.example`、`.gitignore`

### N-018 web/app.py 現行 API 準拠

- **✅ 完了（2026-05-04）**
- 目的：`web/app.py` を `AppConfig.from_env()` / `AuthService(mode=...)` / `UserProfileService(db_path=...)` の現行 API に準拠させ、`/health` エンドポイントと Flask テストを追加する
- 受入条件：
  - ✅ `AppConfig.from_env()` でコンフィグを一元管理している
  - ✅ `API_KEY` ハードコードが完全に除去されている（P-002）
  - ✅ `/health` エンドポイントが追加されている
  - ✅ Flask テストクライアントを用いた 3 ケースのテストが追加されている
  - ✅ `flask>=3.0` が `pyproject.toml` の依存に追加されている
  - ✅ CI 通過（212 passed, カバレッジ 92.89%）
- 依存：N-017
- 触る領域：`web/app.py`、`tests/test_web_app.py`、`pyproject.toml`

### N-019 テスト補強

- **✅ 完了（2026-05-04）**
- 目的：カバレッジの低い箇所（権限型ガード・設定不正値フォールバック）を補強するテストを追加する
- 受入条件：
  - ✅ `has_permission` が str 以外を受け取った場合に `False` を返すテストが追加されている
  - ✅ `AUTH_MODE` 不正値時の `mock` フォールバックをカバーするテストが追加されている
  - ✅ CI 通過（211 passed, カバレッジ 93.63%）
- 依存：N-018
- 触る領域：`tests/test_permissions_roles.py`、`tests/test_config.py`

### N-020 OAuth 永続化仕様の docs 反映

- **✅ 完了（2026-05-04）**
- 目的：N-017 で実装した OAuth トークン永続化仕様（TOKEN_PATH・再利用動作・フォールバック）を正本 docs に整合させる
- 受入条件：
  - ✅ `docs/requirements.md` の FR-001 に TOKEN_PATH・再利用動作・フォールバック仕様を追記している
  - ✅ `docs/architecture.md` の auth/ 責務とデータフローに TOKEN_PATH を反映している
  - ✅ `docs/runbook.md` の前提・環境変数・Docker 例・トラブルシュートに TOKEN_PATH 運用を追記している
  - ✅ `get_errors` で変更した docs の diagnostics が 0 件である
- 依存：N-019
- 触る領域：`docs/requirements.md`、`docs/architecture.md`、`docs/runbook.md`

### N-021 constraints.md プロジェクト固有制約定義

- **✅ 完了（2026-05-05）**
- 目的：テンプレートのままになっている `docs/constraints.md` に、子供向け学習アプリ固有の制約（学年範囲・コンテンツ安全性・API レート制限・学習セッション時間）を定義する
- 受入条件：
  - [x] C-001（学年制約）：`Grade` を 1〜6 に限定する仕様が定義されている
  - [x] C-002（コンテンツ安全性）：Gemini 生成コンテンツの不適切表現チェック仕様が定義されている
  - [x] C-003（API レート制限）：Gemini API 呼び出しのレート制限仕様（1ユーザー 10 req/min、全体 50 req/min）が定義されている
  - [x] C-004（セッション時間制限）：学習セッション時間制限仕様（警告 60 分、強制終了 120 分）が定義されている
  - [x] 各制約が `docs/constraints.md` の正式フォーマットで記述されている
  - [x] `get_errors` で diagnostics が 0 件である
- 依存：N-020
- 触る領域：`docs/constraints.md`

### N-022 FR-030 Drive 連携要件定義

- **✅ 完了（2026-05-05）**
- 目的：`docs/requirements.md` に空欄のままの FR-030 を定義し、`DriveService` 実装の仕様基盤を作る
- 受入条件：
  - [x] FR-030 に「Google Drive 共有フォルダから PDF 一覧を取得する」機能要件を記述
  - [x] 入力（`folder_id`）・出力（`list[dict]`）・失敗時挙動が明記されている
  - [x] FR-031 として「`metadata.json` 取得」要件を追加
  - [x] `docs/architecture.md` の `drive/` 責務を FR-030/031 に整合させる
  - [x] `get_errors` で diagnostics が 0 件である
- 依存：N-021
- 触る領域：`docs/requirements.md`、`docs/architecture.md`

### N-023 GeminiService 実 API 接続

- **✅ 完了（2026-05-05）**
- 目的：`GeminiService` のスタブ実装を `google-genai` SDK で置き換え、実際の Gemini API で問題を生成できるようにする
- 受入条件：
  - [x] `google-genai>=0.3` を `pyproject.toml` に追加
  - [x] `GeminiService.__init__` で `genai.Client(api_key=self.api_key)` を生成する
  - [x] `generate_question` が `client.models.generate_content()` で JSON レスポンスを返す
  - [x] CI では `genai` モジュールをモックし、既存リトライロジックが通過する
  - [x] `src/gemini/service.py` のカバレッジが 85% 以上になる
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-022
- 触る領域：`src/gemini/service.py`、`tests/test_gemini_service.py`、`pyproject.toml`

### N-024 DriveService Google Drive API 実装

- **✅ 完了（2026-05-14）**
- 目的：`DriveService` のスタブを `google-api-python-client` で置き換え、実際の Google Drive から PDF 一覧・`metadata.json` を取得できるようにする
- 受入条件：
  - [x] `google-api-python-client>=2.0` を `pyproject.toml` に追加
  - [x] `list_pdfs_in_folder(folder_id)` が Drive API `files.list` を呼び出す
  - [x] `get_metadata(folder_id, subject)` が Drive API 経由で `metadata.json` を取得・パースする
  - [x] CI では Drive API をモックし、テストが通過する
  - [x] FR-030/031 受入条件をすべて満たす
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-023
- 触る領域：`src/drive/service.py`、`tests/test_drive_service.py`、`pyproject.toml`

### N-025 auth・gemini カバレッジ補強

- **✅ 完了（2026-05-14）**
- 目的：カバレッジが低い `src/auth/service.py`（81%）と `src/gemini/service.py`（65%）のテストを補強し、90% 以上にする
- 受入条件：
  - [x] `auth/service.py` の line 60-62、88-92、118-120、129-130、141-143 をカバーするテストを追加
  - [x] `gemini/service.py` の line 35-36、49-57 をカバーするテストを追加
  - [x] `src/auth/service.py` カバレッジ 90% 以上
  - [x] `src/gemini/service.py` カバレッジ 85% 以上
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-024
- 触る領域：`tests/test_auth_service.py`、`tests/test_gemini_service.py`

### N-026 Flask セッション管理

- **✅ 完了**
- 目的：`web/app.py` にサーバーサイドセッションを追加し、ログイン状態をリクエスト間で維持できるようにする
- 受入条件：
  - [x] `flask-login` または `flask` 標準セッションでログイン状態を維持
  - [x] `SECRET_KEY` 環境変数でセッション署名キーを設定（未設定時は起動エラー）
  - [x] 未ログイン時にログインページへリダイレクト
  - [x] セッションハイジャック対策（`SESSION_COOKIE_HTTPONLY=True`、`SESSION_COOKIE_SECURE=True`）が設定されている
  - [x] テストでセッションありの認証フローを検証する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-025
- 触る領域：`web/app.py`、`tests/test_web_app.py`

### N-027 C-003 Gemini API レート制限実装

- **✅ 完了（2026-05-14）**
- 目的：Gemini API 呼び出しを 1 ユーザー 10 req/min、全体 50 req/min に制限し、過負荷時にフェイルクローズする
- 受入条件：
  - [x] 1ユーザー 10 req/min のしきい値を実装
  - [x] 全体 50 req/min のしきい値を実装
  - [x] しきい値超過時に `RateLimitError(reason_code="C003_rate_limit_exceeded")` を送出
  - [x] 境界値テスト（ちょうど/直上）を追加
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-026
- 触る領域：`src/core/exceptions.py`、`src/learning/service.py`、`tests/test_learning_service.py`

### N-028 C-004 学習セッション時間制限実装

- **✅ 完了（2026-05-14）**
- 目的：学習セッションの継続時間を監視し、60分超過で警告、120分超過で強制停止する
- 受入条件：
  - [x] セッション継続時間を追跡する
  - [x] 60分超過で警告（`ValidationError(reason_code="C004_session_warning")`）
  - [x] 120分超過で強制停止（`ValidationError(reason_code="C004_session_forced_stop")`）
  - [x] 境界値テスト（3600秒/3601秒、7200秒/7201秒）を追加
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-027
- 触る領域：`src/learning/service.py`、`tests/test_learning_service.py`、`docs/constraints.md`

### N-029 Web: C-004 セッション警告/停止の表示反映

- **✅ 完了（2026-05-14）**
- 目的：Web 画面で C-004 セッション時間制限および C-003 レート制限を利用者向けメッセージとして返却する
- 受入条件：
  - [x] `web/app.py` が `LearningService.generate_question()` を利用する
  - [x] `C004_session_timeout` を検知して利用者向けメッセージを 429 で返す
  - [x] `C003_rate_limit_exceeded` を検知して利用者向けメッセージを 429 で返す
  - [x] `tests/test_web_app.py` に検証テストを追加
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-028
- 触る領域：`web/app.py`、`tests/test_web_app.py`

### N-030 C-004 セッション制御の警告/強制停止を段階化

- **✅ 完了（2026-05-14）**
- 目的：C-004 の 60分超過（警告）と 120分超過（強制停止）を明確に区別し、UI と業務制御で段階的に扱えるようにする
- 受入条件：
  - [x] 60分超過で警告状態を返却し、120分超過とは識別できる
  - [x] 120分超過で強制停止状態を返却できる
  - [x] `web/app.py` の応答が警告/停止で分岐する
  - [x] 境界値テスト（3600/3601、7200/7201）を維持しつつ新状態を検証する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-029
- 触る領域：`src/learning/service.py`、`src/core/exceptions.py`、`web/app.py`、`tests/`

### N-031 C-003/C-004 の永続化レート・セッション追跡

- **✅ 完了（2026-05-14）**
- 目的：C-003/C-004 判定状態をプロセス内メモリ依存から脱却し、再起動後・複数ワーカーでも一貫した判定を実現する
- 受入条件：
  - [x] レート履歴とセッション開始時刻の永続化ストアを実装する
  - [x] 再起動後も C-003/C-004 判定が一貫する
  - [x] 複数ユーザー並行アクセス時に判定が安定する
  - [x] 再現性テストを追加する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-030
- 触る領域：`src/learning/service.py`、`src/user/profile.py`、`tests/`、`docs/architecture.md`

### N-032 C-003/C-004 の運用可観測性（メトリクス/ログ）強化

- **✅ 完了（2026-05-14）**
- 目的：C-003/C-004 イベントの運用観測性を高め、発生頻度や影響ユーザーを迅速に把握できるようにする
- 受入条件：
  - [x] C-003/C-004 イベントを構造化ログで出力する
  - [x] 超過回数・対象ユーザー数など主要メトリクスを追加する
  - [x] `docs/runbook.md` に監視・一次対応手順を追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-031
- 触る領域：`src/observability/`、`src/learning/service.py`、`docs/runbook.md`、`tests/`

### N-033 C-003/C-004 メトリクスの管理者向け可視化 API 追加

- **✅ 完了（2026-05-14）**
- 目的：運用者が C-003/C-004 の発生状況を API 経由で確認できるようにし、障害切り分けを高速化する
- 受入条件：
  - [x] 管理者権限で参照可能なメトリクス API を追加する
  - [x] C-003/C-004 の主要カウンタを JSON で返却できる
  - [x] `tests/test_web_app.py` に API 応答テストを追加する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-032
- 触る領域：`web/app.py`、`src/observability/`、`tests/`

### N-034 C-003/C-004 のアラート閾値定義と運用手順の標準化

- **✅ 完了（2026-05-14）**
- 目的：C-003/C-004 の監視アラート基準を定義し、一次対応を標準化する
- 受入条件：
  - [x] `docs/constraints.md` に監視向けアラート閾値を定義する
  - [x] `docs/runbook.md` にエスカレーション条件を追記する
  - [x] 監視設定のサンプル手順を文書化する
  - [x] docs の diagnostics が 0 件である
- 依存：N-033
- 触る領域：`docs/constraints.md`、`docs/runbook.md`

### N-035 C-003/C-004 高負荷時の再現試験（負荷・再現性）整備

- **✅ 完了（2026-05-14）**
- 目的：高負荷時でも C-003/C-004 判定が安定することを検証し、再現性を担保する
- 受入条件：
  - [x] レート制限・セッション制限の負荷試験シナリオを追加する
  - [x] 再現性（同一条件で同一判定）を検証するテストを追加する
  - [x] テスト結果を `docs/quality-guide.md` に反映する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-034
- 触る領域：`tests/`、`docs/quality-guide.md`

### N-036 C-003/C-004 管理者メトリクス API の認可強化（parent/admin 分離）

- **✅ 完了（2026-05-14）**
- 目的：可観測性 API の認可を明確化し、admin のみ参照可・parent/student は拒否する
- 受入条件：
  - [x] `web/app.py` の管理者 API で role 判定を明確化する
  - [x] parent/student で 403 を返すテストを追加する
  - [x] 権限仕様を `docs/requirements.md` に追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-033
- 触る領域：`web/app.py`、`tests/test_web_app.py`、`docs/requirements.md`

### N-037 C-003/C-004 イベントの時系列履歴化（直近N件保持）

- **✅ 完了（2026-05-14）**
- 目的：運用時に直近の制約イベント時系列を追跡できるようにする
- 受入条件：
  - [x] C-003/C-004 イベントの直近履歴（時刻・event_name・uid）を保持する
  - [x] 履歴を取得する API または関数を追加する
  - [x] 履歴上限 N 件（例: 200）を超えた場合に古い順で破棄する
  - [x] テストで履歴保持と上限制御を検証する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-036
- 触る領域：`src/observability/tracing.py`、`tests/test_observability.py`

### N-038 可観測性 API の契約テスト（スキーマ固定）追加

- **✅ 完了（2026-05-14）**
- 目的：管理者メトリクス API の JSON スキーマを固定化し、将来変更による破壊を防ぐ
- 受入条件：
  - [x] メトリクス API の必須キーを契約テストで固定化する
  - [x] 型（int/dict など）をテストで検証する
  - [x] 主要レスポンス例を `docs/runbook.md` に記載する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-037
- 触る領域：`tests/test_web_app.py`、`docs/runbook.md`

### N-039 制約イベント履歴 API のページング対応

- **✅ 完了（2026-05-14）**
- 目的：履歴 API の応答サイズを制御し、運用時の取得負荷を下げる
- 受入条件：
  - [x] `limit` / `offset` パラメータを追加する
  - [x] 境界値テスト（0、上限超過、負値）を追加する
  - [x] `docs/runbook.md` に利用例を追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-037
- 触る領域：`web/app.py`、`src/observability/tracing.py`、`tests/`、`docs/runbook.md`

### N-040 制約イベント履歴の永続化（SQLite）

- **✅ 完了（2026-05-14）**
- 目的：プロセス再起動後も制約イベント履歴を保持し、運用調査の再現性を高める
- 受入条件：
  - [x] SQLite テーブルを追加する
  - [x] 履歴保存・取得を実装する
  - [x] 再起動後の履歴継続をテストで検証する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-039
- 触る領域：`src/user/profile.py`、`src/observability/`、`tests/`

### N-041 管理者メトリクス API の認証監査ログ追加

- **✅ 完了（2026-05-14）**
- 目的：管理者 API へのアクセス成功/拒否を監査可能にし、運用時の追跡性を高める
- 受入条件：
  - [x] 成功アクセス・拒否アクセスを構造化ログで出力する
  - [x] テストでログ出力を検証する
  - [x] `docs/runbook.md` に監査確認手順を追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-040
- 触る領域：`web/app.py`、`tests/test_web_app.py`、`docs/runbook.md`

### N-042 C-003/C-004 履歴 API の event_name フィルタ追加

- **✅ 完了（2026-05-14）**
- 目的：制約イベント履歴を event_name で絞り込み、運用時の調査を容易にする
- 受入条件：
  - [x] event_name フィルタを追加する
  - [x] フィルタ時のテストを追加する
  - [x] runbook に利用例を追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-041
- 触る領域：`src/observability/tracing.py`、`web/app.py`、`tests/`、`docs/runbook.md`

### N-043 C-003/C-004 履歴 API のエクスポート形式追加

- **✅ 完了（2026-05-14）**
- 目的：制約イベント履歴を JSON 以外の形式でも扱えるようにし、運用・分析をしやすくする
- 受入条件：
  - [x] export 形式（JSON/CSV など）を選択できる
  - [x] 出力形式ごとのテストを追加する
  - [x] runbook にサンプルを追記する
  - [x] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-042
- 触る領域：`web/app.py`、`tests/`、`docs/runbook.md`

### N-044 制約イベント履歴の保持期間・自動削除

- **📋 予定（Backlog）**
- 目的：制約イベント履歴のサイズを制御し、SQLite の肥大化を防ぐ
- 受入条件：
  - [ ] 保持期間または保持件数の削除ロジックを実装する
  - [ ] 削除処理のテストを追加する
  - [ ] runbook に運用手順を追記する
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-043
- 触る領域：`src/observability/tracing.py`、`tests/`、`docs/runbook.md`

### N-045 管理者監査ログの request_id 付与

- **📋 予定（Backlog）**
- 目的：管理者 API の監査ログに request_id を付与し、追跡性を向上させる
- 受入条件：
  - [ ] request_id を監査ログへ含める
  - [ ] テストで request_id の出力を検証する
  - [ ] runbook に確認手順を追記する
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-044
- 触る領域：`web/app.py`、`tests/test_web_app.py`、`docs/runbook.md`

## GitHub Issue / Project 対応表

| 計画 | Issue | Phase | ステータス | 種別 |
| --- | --- | --- | --- | --- |
| N-004 設定管理・エラーハンドリング強化 | [#3](https://github.com/weimaraner69-crypto/test02/issues/3) | 3-Hardening | ✅ 完了 | Feature |
| N-005 認証・権限の本番化 | [#4](https://github.com/weimaraner69-crypto/test02/issues/4) | 3-Hardening | ✅ 完了 | Feature |
| N-006 データ永続化 | [#5](https://github.com/weimaraner69-crypto/test02/issues/5) | 3-Hardening | ✅ 完了 | Feature |
| N-007 子供向け学習機能の実装 | [#6](https://github.com/weimaraner69-crypto/test02/issues/6) | 4-Advanced | ✅ 完了 | Feature |
| N-008 FR-020 拡充（理科・社会・英語カタログ） | [#11](https://github.com/weimaraner69-crypto/test02/issues/11) | 4-Advanced | ✅ 完了 | Feature |
| N-009 observability 統合 | [#12](https://github.com/weimaraner69-crypto/test02/issues/12) | 4-Advanced | ✅ 完了 | Feature |
| N-010 NFR-030 CLI/runbook 整備 | [#13](https://github.com/weimaraner69-crypto/test02/issues/13) | 4-Advanced | ✅ 完了 | Feature |
| N-011 Google OAuth 本実装 | [#14](https://github.com/weimaraner69-crypto/test02/issues/14) | 5-Future | ✅ 完了 | Feature |
| N-012 docs Markdown lint 整理 | [#19](https://github.com/weimaraner69-crypto/test02/issues/19) | 4-Advanced | ✅ 完了 | Maintenance |
| N-013 正本ドキュメント整合性回復 | [#20](https://github.com/weimaraner69-crypto/test02/issues/20) | 4-Advanced | ✅ 完了 | Maintenance |
| N-014 ログ整理・セキュリティ修正 | [#22](https://github.com/weimaraner69-crypto/test02/issues/22) | 4-Advanced | ✅ 完了 | Maintenance |
| N-015 家族メンバー管理 API | [#23](https://github.com/weimaraner69-crypto/test02/issues/23) | 4-Advanced | ✅ 完了 | Feature |
| N-016 バリデーション強化・Gemini リトライ | [#24](https://github.com/weimaraner69-crypto/test02/issues/24) | 4-Advanced | ✅ 完了 | Feature |
| N-017 OAuth トークンローカル永続化 | [#25](https://github.com/weimaraner69-crypto/test02/issues/25) | 4-Advanced | ✅ 完了 | Feature |
| N-018 web/app.py 現行 API 準拠 | [#26](https://github.com/weimaraner69-crypto/test02/issues/26) | 4-Advanced | ✅ 完了 | Maintenance |
| N-019 テスト補強 | [#27](https://github.com/weimaraner69-crypto/test02/issues/27) | 4-Advanced | ✅ 完了 | QA |
| N-020 OAuth 永続化仕様の docs 反映 | [#34](https://github.com/weimaraner69-crypto/test02/issues/34) | 4-Advanced | ✅ 完了 | Maintenance |
| N-021 constraints.md プロジェクト固有制約定義 | [#35](https://github.com/weimaraner69-crypto/test02/issues/35) | 5-Future | ✅ 完了 | Maintenance |
| N-022 FR-030 Drive 連携要件定義 | [#36](https://github.com/weimaraner69-crypto/test02/issues/36) | 5-Future | ✅ 完了 | Maintenance |
| N-023 GeminiService 実 API 接続 | [#37](https://github.com/weimaraner69-crypto/test02/issues/37) | 5-Future | ✅ 完了 | Feature |
| N-024 DriveService Google Drive API 実装 | [#38](https://github.com/weimaraner69-crypto/test02/issues/38) | 5-Future | ✅ 完了 | Feature |
| N-025 auth・gemini カバレッジ補強 | [#39](https://github.com/weimaraner69-crypto/test02/issues/39) | 5-Future | ✅ 完了 | QA |
| N-026 Flask セッション管理 | [#40](https://github.com/weimaraner69-crypto/test02/issues/40) | 5-Future | ✅ 完了 | Feature |
| N-027 C-003 Gemini API レート制限実装 | [#47](https://github.com/weimaraner69-crypto/test02/issues/47) | 5-Future | ✅ 完了 | Feature |
| N-028 C-004 学習セッション時間制限実装 | [#48](https://github.com/weimaraner69-crypto/test02/issues/48) | 5-Future | ✅ 完了 | Feature |
| N-029 Web: C-004 セッション警告/停止の表示反映 | [#49](https://github.com/weimaraner69-crypto/test02/issues/49) | 5-Future | ✅ 完了 | Feature |
| N-030 C-004 セッション制御の警告/強制停止を段階化 | [#50](https://github.com/weimaraner69-crypto/test02/issues/50) | 5-Future | ✅ 完了 | Feature |
| N-031 C-003/C-004 の永続化レート・セッション追跡 | [#51](https://github.com/weimaraner69-crypto/test02/issues/51) | 5-Future | ✅ 完了 | Feature |
| N-032 C-003/C-004 の運用可観測性（メトリクス/ログ）強化 | [#52](https://github.com/weimaraner69-crypto/test02/issues/52) | 5-Future | ✅ 完了 | Feature |
| N-033 C-003/C-004 メトリクスの管理者向け可視化 API 追加 | [#53](https://github.com/weimaraner69-crypto/test02/issues/53) | 5-Future | ✅ 完了 | Feature |
| N-034 C-003/C-004 のアラート閾値定義と運用手順の標準化 | [#54](https://github.com/weimaraner69-crypto/test02/issues/54) | 5-Future | ✅ 完了 | Maintenance |
| N-035 C-003/C-004 高負荷時の再現試験（負荷・再現性）整備 | [#55](https://github.com/weimaraner69-crypto/test02/issues/55) | 5-Future | ✅ 完了 | QA |
| N-036 C-003/C-004 管理者メトリクス API の認可強化（parent/admin 分離） | [#56](https://github.com/weimaraner69-crypto/test02/issues/56) | 5-Future | ✅ 完了 | Feature |
| N-037 C-003/C-004 イベントの時系列履歴化（直近N件保持） | [#57](https://github.com/weimaraner69-crypto/test02/issues/57) | 5-Future | ✅ 完了 | Feature |
| N-038 可観測性 API の契約テスト（スキーマ固定）追加 | [#58](https://github.com/weimaraner69-crypto/test02/issues/58) | 5-Future | ✅ 完了 | QA |
| N-039 制約イベント履歴 API のページング対応 | [#59](https://github.com/weimaraner69-crypto/test02/issues/59) | 5-Future | ✅ 完了 | Feature |
| N-040 制約イベント履歴の永続化（SQLite） | [#60](https://github.com/weimaraner69-crypto/test02/issues/60) | 5-Future | ✅ 完了 | Feature |
| N-041 管理者メトリクス API の認証監査ログ追加 | [#61](https://github.com/weimaraner69-crypto/test02/issues/61) | 5-Future | ✅ 完了 | Maintenance |
| N-042 C-003/C-004 履歴 API の event_name フィルタ追加 | [#62](https://github.com/weimaraner69-crypto/test02/issues/62) | 5-Future | ✅ 完了 | Feature |
| N-043 C-003/C-004 履歴 API のエクスポート形式追加 | [#63](https://github.com/weimaraner69-crypto/test02/issues/63) | 5-Future | ✅ 完了 | Feature |
| N-044 制約イベント履歴の保持期間・自動削除 | [#64](https://github.com/weimaraner69-crypto/test02/issues/64) | 5-Future | 📋 予定 | Maintenance |
| N-045 管理者監査ログの request_id 付与 | [#65](https://github.com/weimaraner69-crypto/test02/issues/65) | 5-Future | 📋 予定 | Maintenance |

## 直近の変更履歴（最大10件）

- 2026-05-14: N-039/N-040/N-041/N-042 完了（ページング、SQLite 永続化、監査ログ、event_name フィルタを実装）
- 2026-05-14: N-043 完了（履歴 API のエクスポート形式に CSV を追加）
- 2026-05-14: Next を再編（N-044/N-045 追加、Issue #64/#65 作成）
- 2026-05-14: N-036/N-037/N-038 完了（認可分離、イベント履歴化、API契約テストを実装）
- 2026-05-14: Next を再編（N-039/N-040/N-041 追加、Issue #59/#60/#61 作成）
- 2026-05-14: N-033/N-034/N-035 完了（管理者メトリクス API、監視閾値定義、負荷/再現性テストを追加）
- 2026-05-14: Next を再編（N-036/N-037/N-038 追加）
- 2026-05-14: N-030/N-031/N-032 完了（段階的 reason_code、永続化ランタイム状態、可観測性ログ/メトリクスを実装）
- 2026-05-14: Next を再編（N-033/N-034/N-035 追加、Issue #53/#54/#55 作成）
- 2026-05-14: N-030〜N-032 を計画追加（Issue #50/#51/#52 作成、Next 設定）
- 2026-05-14: N-029 完了（Web で C-003/C-004 の利用者向け 429 応答を実装、CI グリーン）
- 2026-05-14: N-027/N-028 完了（C-003/C-004 実装、境界値テスト追加、CI グリーン）
- 2026-05-14: Next を再編（N-027/N-028 追加、Issue #47/#48 作成）
- 2026-05-14: N-026 完了（PR #46 マージ、GET /login と POST /login 分離、セッション管理強化、CI グリーン）
