# 計画（Plan）

## 運用ルール

- この文書は「現在の計画」を表す。過去ログを増やさない。
- 変更履歴は直近10件までとし、重要判断は ADR に移す。
- 自動実行の対象は「Next」のみとする。Backlog は自動で着手しない。

## 現状（Status）

- フェーズ：**Advanced**（N-001〜N-020 完了）
- ブロッカー：なし
- 直近の重要決定：N-021 ・ N-022 マージ完了、N-023 PR #43 マージ待ち（2026-05-05）

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

1. **N-024** DriveService Google Drive API 実装（N-021/022 マージ済み、N-023 マージ待ち）
2. **N-025** auth/gemini カバレッジ補強（auth 81%、gemini 65% → 90%+）
3. **N-026** Flask セッション管理（SECRET_KEY 環境変数・スッションハイジャック対策）

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
  - [ ] C-001（学年制約）：`Grade` を 1〜6 に限定。範囲外は `ValidationError` で拒否
  - [ ] C-002（コンテンツ安全性）：Gemini 生成コンテンツに対し、不適切表現チェックを定義
  - [ ] C-003（API レート制限）：Gemini API 呼び出しを 1 ユーザーあたり 10 req/min 以内に制限
  - [ ] C-004（セッション時間制限）：1 学習セッション上限を 60 分とし、超過時は警告
  - [ ] 各制約が `docs/constraints.md` の正式フォーマットで記述されている
  - [ ] `get_errors` で diagnostics が 0 件である
- 依存：N-020
- 触る領域：`docs/constraints.md`

### N-022 FR-030 Drive 連携要件定義

- **✅ 完了（2026-05-05）**
- 目的：`docs/requirements.md` に空欄のままの FR-030 を定義し、`DriveService` 実装の仕様基盤を作る
- 受入条件：
  - [ ] FR-030 に「Google Drive 共有フォルダから PDF 一覧を取得する」機能要件を記述
  - [ ] 入力（`folder_id`）・出力（`list[dict]`）・失敗時挙動が明記されている
  - [ ] FR-031 として「`metadata.json` 取得」要件を追加
  - [ ] `docs/architecture.md` の `drive/` 責務を FR-030/031 に整合させる
  - [ ] `get_errors` で diagnostics が 0 件である
- 依存：N-021
- 触る領域：`docs/requirements.md`、`docs/architecture.md`

### N-023 GeminiService 実 API 接続

- **� PR #43 レビュー対応済み・マージ待ち**
- 目的：`GeminiService` のスタブ実装を `google-generativeai` SDK で置き換え、実際の Gemini API で問題を生成できるようにする
- 受入条件：
  - [ ] `google-generativeai>=0.7` を `pyproject.toml` に追加
  - [ ] `GeminiService.__init__` で `genai.configure(api_key=self.api_key)` を呼び出す
  - [ ] `generate_question` が `genai.GenerativeModel.generate_content()` で JSON レスポンスを返す
  - [ ] CI では `genai` モジュールをモックし、既存リトライロジックが通過する
  - [ ] `src/gemini/service.py` のカバレッジが 85% 以上になる
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-022
- 触る領域：`src/gemini/service.py`、`tests/test_gemini_service.py`、`pyproject.toml`

### N-024 DriveService Google Drive API 実装

- **📋 予定（Backlog）**
- 目的：`DriveService` のスタブを `google-api-python-client` で置き換え、実際の Google Drive から PDF 一覧・`metadata.json` を取得できるようにする
- 受入条件：
  - [ ] `google-api-python-client>=2.0` を `pyproject.toml` に追加
  - [ ] `list_pdfs_in_folder(folder_id)` が Drive API `files.list` を呼び出す
  - [ ] `get_metadata(folder_id, subject)` が Drive API 経由で `metadata.json` を取得・パースする
  - [ ] CI では Drive API をモックし、テストが通過する
  - [ ] FR-030/031 受入条件をすべて満たす
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-023
- 触る領域：`src/drive/service.py`、`tests/test_drive_service.py`、`pyproject.toml`

### N-025 auth・gemini カバレッジ補強

- **📋 予定（Backlog）**
- 目的：カバレッジが低い `src/auth/service.py`（81%）と `src/gemini/service.py`（65%）のテストを補強し、90% 以上にする
- 受入条件：
  - [ ] `auth/service.py` の line 60-62、88-92、118-120、129-130、141-143 をカバーするテストを追加
  - [ ] `gemini/service.py` の line 35-36、49-57 をカバーするテストを追加
  - [ ] `src/auth/service.py` カバレッジ 90% 以上
  - [ ] `src/gemini/service.py` カバレッジ 85% 以上
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-024
- 触る領域：`tests/test_auth_service.py`、`tests/test_gemini_service.py`

### N-026 Flask セッション管理

- **📋 予定（Backlog）**
- 目的：`web/app.py` にサーバーサイドセッションを追加し、ログイン状態をリクエスト間で維持できるようにする
- 受入条件：
  - [ ] `flask-login` または `flask` 標準セッションでログイン状態を維持
  - [ ] `SECRET_KEY` 環境変数でセッション署名キーを設定（未設定時は起動エラー）
  - [ ] 未ログイン時にログインページへリダイレクト
  - [ ] セッションハイジャック対策（`SESSION_COOKIE_HTTPONLY=True`、`SESSION_COOKIE_SECURE=True`）が設定されている
  - [ ] テストでセッションありの認証フローを検証する
  - [ ] CI 通過（全 passed・カバレッジ 80% 以上）
- 依存：N-025
- 触る領域：`web/app.py`、`tests/test_web_app.py`

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
| N-023 GeminiService 実 API 接続 | [#37](https://github.com/weimaraner69-crypto/test02/issues/37) | 5-Future | 🔄 PR #43 マージ待ち | Feature |
| N-024 DriveService Google Drive API 実装 | [#38](https://github.com/weimaraner69-crypto/test02/issues/38) | 5-Future | 📋 予定 | Feature |
| N-025 auth・gemini カバレッジ補強 | [#39](https://github.com/weimaraner69-crypto/test02/issues/39) | 5-Future | 📋 予定 | QA |
| N-026 Flask セッション管理 | [#40](https://github.com/weimaraner69-crypto/test02/issues/40) | 5-Future | 📋 予定 | Feature |

## 直近の変更履歴（最大10件）

- 2026-05-05: N-021 ・ N-022 マージ完了（PR #41/#42）、N-023 PR #43 レビュー対応済み・マージ待ち
- 2026-05-05: N-021〜N-023 実装完了（PR #41/#42/#43 作成、CI 全グリーン、リリースマネージャー approve、マージ順序 #41→#42→#43）
- 2026-05-05: N-024〜N-026 を Next に是格昇格（DriveService 実装・カバレッジ補強・Flask セッション）
- 2026-05-04: N-021〜N-026 を計画（Next 3件 + Backlog 3件。仕様先行：N-021 constraints.md → N-022 FR-030 → N-023 Gemini 実 API）
- 2026-05-04: N-020 完了（requirements / architecture / runbook に TOKEN_PATH とトークン再利用仕様を反映）
- 2026-05-04: N-014〜N-019 完了（PR #28〜#33 マージ、225 passed / 91.88%）
- 2026-05-04: N-013 完了（requirements / architecture を Google OAuth 本実装に整合、docs diagnostics 0件）
- 2026-05-04: N-012 完了（docs Markdown lint 整理、`docs/plan.md` / `docs/runbook.md` diagnostics 0件）
- 2026-05-04: N-011 完了（PR #18 マージ、Google OAuth 本実装、209 passed / 92.89%）、N-012 を Next に昇格
- 2026-05-02: N-008〜N-010 Next 追加、B-002 Backlog 追加（GitHub Issues #11〜#14 作成）
- 2026-05-02: N-007 完了（子供向け学習機能、PR #10 マージ、178 passed / 97.30%）
- 2026-05-02: B-001 → N-007 昇格（子供向け学習機能、Phase 4 Advanced 着手）
- 2026-05-02: N-006 完了（SQLite 永続化、runbook/architecture 更新、140 passed / 97.12%）
- 2026-05-02: N-005 完了（認証モード切り替え、RBAC、PR #8 マージ、128 passed / 96.83%）
