# MiraStudy バックエンド - Docker イメージ
# ビルド: docker build -t mirastudy:latest .
# 実行:   docker run --rm --env-file .env -v "$(pwd)/data:/app/data" mirastudy:latest

FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# uv のインストール
RUN pip install --no-cache-dir uv

# 依存関係ファイルのコピーと依存インストール
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# ソースコードのコピー
COPY src/ ./src/
COPY ci/ ./ci/
COPY configs/ ./configs/
COPY .env.example ./

# データディレクトリの作成
RUN mkdir -p data

# 実行ユーザー（root 不使用）
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 環境変数のデフォルト値（.env でオーバーライド可）
ENV AUTH_MODE=mock \
    DATABASE_PATH=data/mirastudy.db \
    LOG_LEVEL=INFO \
    GEMINI_TOPIC=算数 \
    GEMINI_GRADE=3 \
    DRIVE_FOLDER_ID=folder1

# エントリポイント
CMD ["uv", "run", "python", "-m", "src.app"]
