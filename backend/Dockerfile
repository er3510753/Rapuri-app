# --- 1. ビルドステージ ---
FROM python:3.11-slim as builder

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Poetryのインストール
RUN pip install poetry

# 依存関係の定義ファイルのみを先にコピー
COPY poetry.lock pyproject.toml ./

# 依存関係をインストール（本番用のみ）
# --no-root オプションで仮想環境をプロジェクト内に作成し、キャッシュ効率を向上
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction --no-ansi --no-root

# --- 2. 実行ステージ ---
FROM python:3.11-slim as runner

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN groupadd -r django-user && useradd -r -g django-user django-user

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY . .

RUN chown -R django-user:django-user /app

USER django-user

# Gunicornを起動
CMD ["/app/.venv/bin/gunicorn", "ramen_project.wsgi:application", "--bind", "0.0.0.0:8000"]