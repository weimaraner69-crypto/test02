# 計画（Plan）

## 運用ルール

- この文書は「現在の計画」を表す。過去ログを増やさない。
- 変更履歴は直近10件までとし、重要判断は ADR に移す。
- 自動実行の対象は「Next」のみとする。Backlog は自動で着手しない。

## 現状（Status）

- フェーズ：**Hardening**（N-001/N-002/N-003 完了、Phase 3 開始）
- ブロッカー：なし
- 直近の重要決定：N-003 完了・Phase 3 計画追加（2026-04-30）

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

### N-001 リポジトリ基盤と CI 品質ゲートの確立

- **✅ 完了（2026-04-30）**
- 目的：CI（lint/type/test/policy_check）を安定稼働させ、最低限の品質を自動判定できるようにする
- 受入条件：
  - ✅ pyproject.toml 整備（ruff/mypy/pytest 設定）
  - ✅ パッケージ構造配置（各サブパッケージに __init__.py）
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

- 目的：本番運用に向けて設定の外部化と統一的なエラーハンドリングを整備する
- 受入条件：
  - 環境変数による設定管理（`.env` / `pydantic-settings` または同等）が実装されている
  - 全サービスで `DomainError` 系例外を適切にキャッチ・ログ出力している
  - ローカル実行で設定ロード → 処理 → エラー時の動作が一貫して確認できる
  - CI が通過する
- 依存：N-003
- 触る領域：`src/core/`, `src/app.py`, `tests/`

### N-005 認証・権限の本番化

- 目的：スタブ実装から実際の認証（Google OAuth など）と権限制御に切り替える
- 受入条件：
  - 認証フローが実際のプロバイダ（または環境変数で差し替え可能なモック）で動作する
  - 権限ロール（student / admin 等）に基づくアクセス制御がエンドツーエンドで機能する
  - テストでモック認証を使用し CI が通過する
- 依存：N-004
- 触る領域：`src/auth/`, `src/permissions/`, `tests/`

### N-006 データ永続化

- 目的：インメモリ状態をデータベース（SQLite または PostgreSQL）に移行する
- 受入条件：
  - ユーザープロファイル・学習進捗がDB に保存・取得できる
  - マイグレーション手順が `docs/runbook.md` に記載されている
  - テスト用インメモリ DB（SQLite + pytest-fixtures）で CI が通過する
- 依存：N-005
- 触る領域：`src/`, `tests/`, `docs/runbook.md`

## Backlog（保留）

- B-001 子供向け学習機能の実装（学年別コンテンツ配信・問題生成・進捗管理）

## GitHub Issue / Project 対応表

| 計画 | Issue | Phase | 種別 |
| ---- | ----- | ----- | ---- |
| N-004 設定管理・エラーハンドリング強化 | [#3](https://github.com/weimaraner69-crypto/test02/issues/3) | 3-Hardening | Feature |
| N-005 認証・権限の本番化              | [#4](https://github.com/weimaraner69-crypto/test02/issues/4) | 3-Hardening | Feature |
| N-006 データ永続化                    | [#5](https://github.com/weimaraner69-crypto/test02/issues/5) | 3-Hardening | Feature |
| B-001 子供向け学習機能の実装          | [#6](https://github.com/weimaraner69-crypto/test02/issues/6) | 4-Advanced  | Feature |

## 直近の変更履歴（最大10件）

- 2026-04-30: Phase 3 計画追加（N-004〜N-006 策定、B-001 バックログ登録）
- 2026-04-30: 今月のゴール G1〜G3 記録
- 2026-04-30: N-003 完了（constraints.py 境界値テスト、pytest --cov CI追加、カバレッジ 99.32%）
- 2026-04-30: N-002 完了（MVPパイプライン統合テスト、test_main_pipeline.py追加）
- 2026-04-30: N-001 完了（pyproject.toml, __init__.py, CI ステップ有効化）
