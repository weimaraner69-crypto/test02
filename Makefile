# MiraStudy - 開発・運用コマンド集
# 使用方法: source .venv/bin/activate && make <target>

.PHONY: help setup run lint format typecheck test ci docker-build docker-run

# デフォルトターゲット
help:
	@echo "利用可能なコマンド:"
	@echo "  make setup        - 依存パッケージのインストール"
	@echo "  make run          - アプリケーション実行"
	@echo "  make lint         - リンター実行（ruff）"
	@echo "  make format       - フォーマットチェック（ruff format）"
	@echo "  make typecheck    - 型チェック実行（mypy）"
	@echo "  make test         - テスト実行（pytest + coverage）"
	@echo "  make ci           - ローカル CI 全ステップ実行"
	@echo "  make docker-build - Docker イメージをビルド"
	@echo "  make docker-run   - Docker コンテナを実行"

# 依存パッケージのインストール
setup:
	python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e ".[dev]"

# アプリケーション実行
run:
	python -m src.app

# リンター
lint:
	ruff check .

# フォーマットチェック
format:
	ruff format --check .

# 型チェック（テストディレクトリを含める）
typecheck:
	mypy src/ tests/ --ignore-missing-imports

# テスト実行（カバレッジ付き）
test:
	pytest -q --tb=short --cov=src --cov-report=term-missing

# ローカル CI 全ステップ
ci: lint format typecheck test
	@echo "✅ CI 全ステップ完了"

# Docker イメージをビルド
docker-build:
	docker build -t mirastudy:latest .

# Docker コンテナを実行
docker-run:
	docker run --rm \
		--env-file .env \
		-v "$(PWD)/data:/app/data" \
		mirastudy:latest

