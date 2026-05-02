# 要件定義（Requirements）

## 目的

<!-- プロジェクトの目的を記載する -->

## スコープ

### 対象（本リポジトリで扱う）

<!-- 対象とする機能・作業を箇条書きで記載 -->

### 非対象（本リポジトリでは行わない）

<!-- 除外する機能・作業を箇条書きで記載 -->

## 用語

| 用語           | 定義                                                         |
| -------------- | ------------------------------------------------------------ |
| 正本（SSOT）   | Single Source of Truth。docs/ 配下の文書を唯一の信頼源とする |
| 受入条件（AC） | Issue/PR が完了と判断できる基準                              |

<!-- プロジェクト固有の用語を追加 -->

## 成功条件（ゴール）

- CI が品質ゲートとして機能し、失敗時はマージできない
- 仕様（requirements/policies/constraints/plan/ADR）が更新され、会話ログ依存が最小化される
<!-- プロジェクト固有の成功条件を追加 -->

## 機能要件（FR）

### FR-001 認証・権限制御

- 入力：AUTH_MODE 環境変数（`mock` または `google`）
- 出力：
  - 認証済みユーザー情報 `dict`（uid / email / displayName / isNewUser）
  - ロール（`admin` / `student` / `parent`）に基づく権限判定結果
- 動作モード：
  - `AuthMode.MOCK`：テスト用固定ダミーユーザーを返す（CI 向け）
  - `AuthMode.GOOGLE`：将来の Google OAuth 実装のプレースホルダー（現在 `NotImplementedError`）
- 権限マッピング：
  - `admin`：VIEW_KNOWLEDGE / MANAGE_KNOWLEDGE / VIEW_ALL_HISTORY / VIEW_OWN_HISTORY / MANAGE_FAMILY / MANAGE_API_KEY
  - `student`：VIEW_KNOWLEDGE / VIEW_OWN_HISTORY
  - `parent`：VIEW_OWN_HISTORY / MANAGE_FAMILY
- 失敗時：
  - プロファイル未取得（None）→ `AuthorizationError` を送出してフェイルクローズ（P-010）
  - 不正 AUTH_MODE 値 → `logger.warning` を出力し `mock` にフォールバック
- 担当モジュール：`src/auth/`、`src/permissions/`

### FR-010 SQLite 永続化

- 入力：
  - `DATABASE_PATH` 環境変数で指定された SQLite ファイルパス
  - ユーザープロファイル `dict`
  - 学習進捗 `dict`（topic / status / grade など）
- 出力：
  - SQLite に保存されたユーザープロファイル
  - SQLite に保存された学習進捗
  - 管理者プロフィールの `familyMembers` を参照した家族メンバー一覧
  - 同一 DB ファイルを再オープンした後も取得可能な永続データ
- 保存対象：
  - ユーザープロファイル（uid 単位）
  - 学習進捗（uid + topic 単位）
  - 家族メンバー情報（admin の `familyMembers`）
- テスト要件：
  - `pytest` fixture を用いた SQLite インメモリ DB で保存・取得を検証する
  - ファイルベース DB を再オープンした後もプロファイルが取得できることを検証する
- 担当モジュール：`src/user/`、`src/app.py`、`docs/runbook.md`

### FR-020 学年別学習機能

- 入力：Grade（1〜6）、Subject（算数・国語・理科・社会・英語）、topic 文字列
- 出力：
  - 学年・科目に対応する LearningContent（タイトル・説明・サンプルトピック）
  - Gemini 生成問題（question/answer/hints/curriculum_reference）
  - 回答記録（正誤・日時）
  - 科目別進捗サマリー（正答率・総問題数・正解数）
- 動作：
  - `LearningService` が `UserProfileService`（永続化）と `GeminiService`（問題生成）を統合する
  - 回答記録は SQLite に保存し、進捗サマリーは集計して返す
  - コンテンツカタログは `CONTENT_CATALOG` に静的定義する（算数・国語 各 6 学年）
- 失敗時：
  - Gemini が None を返した場合 → `ValidationError` を送出
  - 進捗保存失敗 → `ValidationError` を送出
- 担当モジュール：`src/learning/`, `src/domain/learning.py`

<!-- 必要に応じて FR-030 ... を追加 -->

## 非機能要件（NFR）

### NFR-001 再現性

<!-- 例: 同一の設定ファイル + 同一の入力データで、出力が一致することを CI で自動検証する -->

- 設定、シード、データバージョン、コードバージョン（コミットSHA）を記録する
- 同一入力に対して同一出力が得られることをテストで担保する

### NFR-010 セキュリティ

<!-- 例: CI の policy_check で AKIA*, ghp_*, Bearer トークン等のパターンを自動検出し、PR をブロックする -->

- 秘密情報をコミットしない
- CI の policy_check で機械的に検査する

### NFR-020 保守性

<!-- 例: カバレッジ 80% 以上を維持し、複雑度スコア 10 以上の関数は分割する -->

- 重要ロジックは単体テストを必須とする
- 変更は 1PR で理解可能な粒度に分割する
- コードの識別子は英語、説明文・PR・Issue は日本語で記述する

### NFR-030 運用容易性

<!-- 例: `uv run python scripts/run_pipeline.py` の1コマンドでパイプラインを実行できる -->

- ローカルで最小コマンドで実行できる
- 失敗時の復旧手順を runbook に記載する

## 受入条件（全PR共通）

| ID     | 条件                                                                    |
| ------ | ----------------------------------------------------------------------- |
| AC-001 | 変更は要件・ポリシー・計画のいずれかに整合する                          |
| AC-010 | 必要なテストが追加または更新されている                                  |
| AC-020 | CI（lint/type/test/policy_check）が成功している                         |
| AC-030 | 変更に応じて正本（docs）が更新されている                                |
| AC-040 | 検証手順と結果が PR 本文に記載されている                                |
| AC-050 | プロジェクト固有の制約に反する変更がない（例外は ADR に記載されている） |

---

## テンプレート適用時のチェックリスト

本ファイルをプロジェクトに適用する際は、以下のチェックリストを確認してください。

- [ ] **目的**: プロジェクトの目的を具体的に記載した
- [ ] **スコープ**: 対象・非対象を明確に列挙した
- [ ] **用語**: プロジェクト固有の用語を追加した
- [ ] **成功条件**: プロジェクト固有の成功条件を追加した
- [ ] **FR**: 最低1つの機能要件を具体的に記載した（プレースホルダーの `<!-- 機能名 -->` を置換済み）
- [ ] **NFR**: 各 NFR に具体的な基準値を設定した（例: カバレッジ 80%、応答時間 500ms 以内）
- [ ] **受入条件**: AC-050 にプロジェクト固有の制約を追記した（該当する場合）
- [ ] **相互参照**: `docs/constraints.md` / `docs/policies.md` / `docs/architecture.md` との整合性を確認した

> **参考**: 記入手順の詳細は [GETTING_STARTED.md](GETTING_STARTED.md) §12「やりたいことを計画に落とし込む」を参照。
