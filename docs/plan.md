# 計画（Plan）

## 運用ルール

- この文書は「現在の計画」を表す。過去ログを増やさない。
- 変更履歴は直近10件までとし、重要判断は ADR に移す。
- 自動実行の対象は「Next」のみとする。Backlog は自動で着手しない。

## 現状（Status）

- フェーズ：**Advanced**（N-001〜N-010 完了）
- ブロッカー：なし
- 直近の重要決定：N-008〜N-010 実装完了・マージ（2026-05-03）

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

### N-011 Google OAuth 本実装（B-002 昇格）

- **⏳ 未着手**
- 目的：`AuthMode.GOOGLE` プレースホルダーを Google OAuth 2.0 で本実装し、本番環境での認証フローを完成させる
- 受入条件：
  - [ ] Google OAuth 2.0 フロー実装（google-auth-oauthlib 利用）
  - [ ] 環境変数 GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET 設定
  - [ ] ローカル開発用リダイレクト URL（http://localhost:8080/auth/callback）対応
  - [ ] テストでモック OAuth を検証する
  - [ ] CI 通過（pytest/mypy/ruff）
  - [ ] `.env.example` に Google OAuth 設定例を追記
  - [ ] `docs/runbook.md` に本番デプロイ用 Google Cloud Console 設定手順を記載
- 依存：N-010
- 触る領域：`src/auth/`、`src/core/config.py`、`.env.example`、`tests/`、`docs/runbook.md`

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
| N-011 Google OAuth 本実装 | [#14](https://github.com/weimaraner69-crypto/test02/issues/14) | 5-Future | ⏳ 着手予定 | Feature |

## 直近の変更履歴（最大10件）

- 2026-05-02: N-008〜N-010 Next 追加、B-002 Backlog 追加（GitHub Issues #11〜#14 作成）
- 2026-05-02: N-007 完了（子供向け学習機能、PR #10 マージ、178 passed / 97.30%）
- 2026-05-02: B-001 → N-007 昇格（子供向け学習機能、Phase 4 Advanced 着手）
- 2026-05-02: N-006 完了（SQLite 永続化、runbook/architecture 更新、140 passed / 97.12%）
- 2026-05-02: N-005 完了（認証モード切り替え、RBAC、PR #8 マージ、128 passed / 96.83%）
- 2026-05-02: N-004 完了（AppConfig 設定管理・エラーハンドリング強化、PR #7 マージ、117 passed / 98.50%）
- 2026-04-30: Phase 3 計画追加（N-004〜N-006 策定、B-001 バックログ登録）
- 2026-04-30: 今月のゴール G1〜G3 記録
- 2026-04-30: N-003 完了（constraints.py 境界値テスト、pytest --cov CI追加、カバレッジ 99.32%）
- 2026-04-30: N-002 完了（MVPパイプライン統合テスト、test_main_pipeline.py追加）
- 2026-04-30: N-001 完了（`pyproject.toml`, `__init__.py`, CI ステップ有効化）
