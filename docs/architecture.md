# アーキテクチャ（Architecture）

## 目的

責務境界を明確にし、実装・テスト・監査を容易にする。

## モジュール責務

```text
src/
├─ app.py           CLI エントリポイント。設定ロードと各サービスのオーケストレーション
├─ auth/            認証モード切り替えとユーザー取得
├─ core/            設定、型、例外、共通ユーティリティ
├─ domain/          ドメインロジック
├─ drive/           Drive メタデータ取得
├─ gemini/          問題生成
├─ permissions/     ロールと権限制御
├─ user/            SQLite によるプロファイル・学習進捗の永続化
├─ observability/   OpenTelemetry 計装（オプショナル）
└─ sample/          Design by Contract のサンプル実装
```

### core/

- 型定義（ドメインオブジェクト）
- ドメイン例外
- 共通ユーティリティ

### domain/

- プロジェクト固有のドメインロジック

### auth/

- `AUTH_MODE` に応じて認証処理を切り替える
- `mock` は CI / ローカル検証用の固定ダミーユーザーを返す
- `google` は将来実装のプレースホルダーとして保持する

### permissions/

- `admin` / `student` / `parent` のロール定義
- `Permission` 列挙体と RBAC 判定

### user/

- SQLite テーブル初期化
- ユーザープロファイルの保存・取得
- 学習進捗の保存・取得
- 家族メンバー一覧の参照

## データフロー

```text
1. 環境変数ロード（AUTH_MODE / DATABASE_PATH / GEMINI_*）
       │
       ▼
2. 認証（auth/AuthService）→ プロファイル保存（user/UserProfileService）
       │
       ▼
3. 権限判定（permissions/roles.py）
       │
       ▼
4. Drive / Gemini 連携
       │
       ▼
5. 学習進捗を SQLite に保存し、同一 DB から再取得する
```

## 依存ルール

| モジュール | 依存してよい | 依存禁止 |
| --- | --- | --- |
| core | （なし：最下層） | 他の全モジュール |
| domain | core | auth, drive, gemini, user |
| auth | core | drive, gemini, user |
| permissions | core | drive, gemini, user |
| user | core | auth, drive, gemini |
| drive | core | auth, permissions, user |
| gemini | core | auth, permissions, user |
| observability | （外部: OTel SDK） | core, domain |
| sample | （なし） | core, domain |

## 不変条件

- 禁止操作を実装しない（P-001）
- 判断不能時は安全側に倒す（P-010: フェイルクローズ）
- 制約は常に優先され、ドメインロジックが回避できない

## 設計論点（必要に応じて ADR）

- SQLite は標準ライブラリ `sqlite3` を使い、追加依存を増やさない
- スキーマは `UserProfileService` 初期化時に自動生成する
- `DATABASE_PATH` を切り替えることでローカル永続化とテスト用インメモリ DB を両立する
