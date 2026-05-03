# 運用手順（Runbook）

## 目的

開発・検証環境を再現可能に運用し、失敗時に復旧できるようにする。

## 前提

- 秘密情報はリポジトリに含めない（P-002）
- `.env.example` を `.env` にコピーし、`AUTH_MODE` と `DATABASE_PATH` を確認する

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd test02
```

### 2. 環境の準備

<!-- 言語・ツールに合わせて記載 -->

#### Python (uv) の例

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --dev
```

#### Node.js (pnpm) の例

```bash
corepack enable
pnpm install
```

### 3. 環境変数の設定

```bash
cp .env.example .env
# .env を編集し、必要な値を設定する
# ⚠️ .env は絶対にコミットしない
```

最低限確認する変数:

- `AUTH_MODE=mock` でローカル検証を行う
- `DATABASE_PATH=data/mirastudy.db` で SQLite ファイル保存先を指定する

## 代表コマンド

### ローカル開発コマンド（make 推奨）

```bash
# セットアップ
make setup

# テスト実行（カバレッジ付き）
make test

# ローカル CI 全ステップ（lint/format/typecheck/test）
make ci

# 個別コマンド
make lint         # リンター
make format       # フォーマットチェック
make typecheck    # 型チェック
```

### 静的解析

```bash
# リンター
ruff check .

# フォーマッタ（チェックのみ）
ruff format --check .

# 型チェック（テストディレクトリも含める）
mypy src/ tests/ --ignore-missing-imports
# ⚠️ 型チェックのスコープにテストディレクトリを必ず含めること
```

### IDE エラー検証（ゲートチェック）

CI の静的解析に加えて、IDE（Pylance 等）のエラーもゼロであることを確認する。
Copilot エージェントの場合は `get_errors` ツール（filePaths 省略）でワークスペース全体を検査する。

### テスト

```bash
# 全テスト実行
make test

# または直接実行
uv run pytest -q --tb=short --cov=src --cov-report=term-missing
```

### ローカル実行（CLI）

```bash
# 方法1: make コマンド
make run

# 方法2: uv 直接実行
uv run python -m src.app
```

初回実行時に `DATABASE_PATH` で指定した SQLite ファイルと必要テーブルを自動生成する.

### Docker での実行

```bash
# ステップ1: Docker イメージをビルド
make docker-build

# ステップ2: Docker コンテナを実行
make docker-run
```

または手動で:

```bash
docker build -t mirastudy:latest .
docker run --rm --env-file .env -v "$(pwd)/data:/app/data" mirastudy:latest
```

**注意:**

- `.env` が存在することを確認してから実行してください（ない場合は `cp .env.example .env` で作成）
- `data/` ディレクトリはホストマシンの同名ディレクトリにマウントされます（永続化のため）

### SQLite の確認

```bash
sqlite3 data/mirastudy.db ".tables"
sqlite3 data/mirastudy.db "SELECT count(*) FROM user_profiles;"
sqlite3 data/mirastudy.db "SELECT count(*) FROM learning_progress;"
```

### ポリシーチェック

```bash
# 禁止操作・秘密情報検出
uv run python ci/policy_check.py
```

## 生成物の扱い

| ディレクトリ | 内容               | git 管理                   |
| ------------ | ------------------ | -------------------------- |
| `outputs/`   | 実行結果、レポート | しない                     |
| `data/raw/`  | 実データ           | しない                     |
| `configs/`   | 実行設定           | する（秘密情報を含めない） |

## 失敗時対応

### CI 失敗

1. GitHub Actions のログで失敗箇所を特定する
2. ローカルで再現する（`.venv/bin/python -m pytest -q --tb=short --cov=src --cov-report=term-missing`）
3. 修正して再プッシュする

### 設定の破損

1. `configs/` のデフォルト設定に戻す
2. テストを実行して正常動作を確認する

### SQLite ファイルの破損・初期化

1. 破損した DB を退避する

   ```bash
   mv data/mirastudy.db "data/mirastudy.db.bak.$(date +%Y%m%d-%H%M%S)"
   ```

2. アプリを再実行してスキーマを自動再生成する

   ```bash
   .venv/bin/python -m src.app
   ```

3. 必要に応じてバックアップから `user_profiles` / `learning_progress` を手動移行する

### 依存関係の問題

1. ロックファイルを削除して再インストール
2. CI で動作確認する

## マイグレーション手順

現時点の SQLite スキーマは `UserProfileService` 初期化時に自動生成される。
列追加やテーブル変更が必要になった場合は次の手順で移行する。

1. 既存 DB をバックアップする

   ```bash
   cp data/mirastudy.db "data/mirastudy.db.backup.$(date +%Y%m%d-%H%M%S)"
   ```

2. 変更後コードで新スキーマを初期化する

   ```bash
   .venv/bin/python -m src.app
   ```

3. 必要なデータを SQLite で移し替える

   ```bash
   sqlite3 data/mirastudy.db ".schema"
   # 例: old_learning_progress から learning_progress へ移行
   sqlite3 data/mirastudy.db "INSERT OR REPLACE INTO learning_progress (uid, topic, progress_json) SELECT uid, topic, progress_json FROM old_learning_progress;"
   ```

4. 移行後にテストを実行して整合性を確認する

   ```bash
   .venv/bin/python -m pytest -q --tb=short --cov=src --cov-report=term-missing
   ```

## モバイルでの開発

iPhone / iPad からの開発作業については [docs/mobile-workflow.md](mobile-workflow.md) を参照する。

## ロールバック手順

### フィーチャーブランチの巻き戻し

マージ済み PR に問題が発覚した場合、`git revert` で安全に取り消す。

```bash
# マージコミットを revert（-m 1 で first parent を指定）
git checkout main  # または master
git pull origin main
git revert -m 1 <マージコミットSHA>
git push origin main
```

**禁止事項**:

- `main` / `master` ブランチへの `git push --force` は禁止する（ブランチ保護ルール）。
- 直接コミットの修正ではなく、必ず revert コミットで対応する。

**手順**:

1. 問題のある PR のマージコミット SHA を特定する
2. `git revert -m 1 <SHA>` で revert コミットを作成する
3. CI が通ることを確認し、プッシュする
4. 必要に応じて修正 PR を別途作成する

### 本番リリースのロールバック

GitHub Releases を用いて前バージョンを特定し、ロールバックする。

**前バージョンの特定**:

```bash
# GitHub Releases の一覧を確認（最新5件）
gh release list --limit 5

# 特定リリースの詳細を確認
gh release view <タグ名>
```

**ロールバック手順**:

1. `gh release list` で前回の安定リリースのタグを特定する
2. 対象タグのコミット SHA を確認する: `git log --oneline <タグ名>`
3. production ブランチを安定コミットに巻き戻す:

   ```bash
   git checkout production
   # 安定コミット以降のコミットを確認
   git log --oneline <安定コミットSHA>..HEAD
   # ロールバック対象のコミット SHA を新しい順に列挙して revert
   git revert --no-commit <コミット1のSHA> <コミット2のSHA> ... <コミットNのSHA>
   git commit -m "fix: <タグ名> へのロールバック"
   git push origin production
   ```

4. CI / 品質ゲートの通過を確認する
5. ロールバック完了後、GitHub Release に状況を記録する:

   ```bash
   gh release create "rollback-$(date -u +%Y%m%d-%H%M%S)" \
     --title "ロールバック: <理由の要約>" \
     --notes "ロールバック先: <タグ名>、理由: <問題の詳細>"
   ```

### ポリシー違反発覚時の復旧フロー

P-001〜P-003 違反が発覚した場合の即時対応手順。

**即時停止条件**（copilot-instructions.md 参照）:

- ポリシー違反（P-001〜P-003）の検出
- 秘密情報の漏洩（P-002）
- 制約の回避・無効化（P-003）

**復旧フロー**:

1. **即時停止**: 自動実行パイプラインが稼働中の場合は即時停止する
2. **影響範囲の特定**:
   - `git log --oneline -20` で直近のコミットを確認する
   - `git diff <違反前のコミットSHA>..HEAD` で変更範囲を確認する
   - 秘密情報漏洩の場合は `git log --all -p -S '<漏洩パターン>'` で全履歴を検索する
3. **秘密情報漏洩時の追加対応**:
   - 漏洩したキー/トークンを即座に無効化（ローテーション）する
   - `git filter-repo` 等で履歴からも除去する（ADR に記録必須）
4. **違反コミットの revert**:

   ```bash
   git revert <違反コミットSHA>
   python ci/policy_check.py  # ポリシーチェックで解消を確認
   ```

5. **エスカレーション**:
   - 重大な違反（秘密情報漏洩、外部への影響）はリポジトリオーナーに即時報告する
   - ADR を作成し、原因・対応・再発防止策を記録する（P-900 例外運用に準拠）
6. **再発防止**:
   - `ci/policy_check.py` のパターンに検出漏れがあれば追加する
   - ブランチ保護ルールの見直しを行う

---

## Google OAuth 本番設定（N-011）

本番環境で Google OAuth を有効化するための設定手順です。

### 前提条件

- Google Cloud Project が作成されていること
- Google OAuth API が有効化されていること

### Google Cloud Console での設定

#### 1. OAuth 2.0 認証情報の作成

1. [Google Cloud Console](https://console.cloud.google.com/) にログイン
2. ナビゲーションメニュー → 「APIs と サービス」→ 「認証情報」
3. 「認証情報を作成」→ 「OAuth クライアント ID」
4. アプリケーションの種類：**ウェブアプリケーション** を選択
5. リダイレクト URI を設定：
   - ローカル開発：`http://localhost:8080/auth/callback`
   - 本番環境：`https://<本番ドメイン>/auth/callback`
6. 「作成」をクリック
7. クライアント ID とクライアント シークレットをコピー

#### 2. 環境変数の設定

本番環境に以下の環境変数を設定します：

```bash
export GOOGLE_CLIENT_ID="<クライアント ID>"
export GOOGLE_CLIENT_SECRET="<クライアント シークレット>"
export AUTH_MODE=google
```

⚠️ **セキュリティ**: シークレット情報は環境変数またはシークレット管理システム（AWS Secrets Manager, Google Secret Manager 等）で管理し、**リポジトリにコミットしない**。

### ローカル開発での テスト

```bash
# .env にテスト用 認証情報を設定
cat >> .env << 'DEVENV'
AUTH_MODE=google
GOOGLE_CLIENT_ID="<テスト用クライアント ID>"
GOOGLE_CLIENT_SECRET="<テスト用クライアント シークレット>"
DEVENV

# アプリを実行
make run

# ブラウザが自動起動し、Google ログイン画面が表示されます
# ログイン後、アプリがユーザー情報を取得します
```

### Docker での本番実行

```bash
# 環境変数を指定して実行
docker run --rm \
  -e GOOGLE_CLIENT_ID="<本番クライアント ID>" \
  -e GOOGLE_CLIENT_SECRET="<本番クライアント シークレット>" \
  -e AUTH_MODE=google \
  -e DATABASE_PATH=/app/data/mirastudy.db \
  -v /path/to/data:/app/data \
  mirastudy:latest
```

### トラブルシューティング

| 問題 | 原因 | 解決方法 |
| --- | --- | --- |
| `ValueError: Google OAuth 認証情報が未設定` | GOOGLE_CLIENT_ID / SECRET が未設定 | 環境変数を確認・設定 |
| `RuntimeError: ローカル web サーバー起動失敗` | ポート 8080 が使用中 | 別のプロセスを終了するか、ポートを変更 |
| `ImportError: google-auth-oauthlib が未インストール` | 依存ライブラリ未インストール | `pip install google-auth-oauthlib` |
| ログイン後に認証エラー | リダイレクト URI が不正 | Google Cloud Console のリダイレクト URI を確認 |

必要に応じて、OAuth 同意画面の公開ステータスとテストユーザー設定も Google Cloud Console 側で確認する。
