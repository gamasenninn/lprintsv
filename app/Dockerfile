# FastAPI公式のベースイメージを使用
#FROM tiangolo/uvicorn-gunicorn:python3.9

# メンテナ情報（必要に応じて変更）
#LABEL maintainer="Your Name <your-email@example.com>"

# 依存関係をコピーしてインストール
#COPY requirements.txt /tmp/requirements.txt
#RUN pip install --no-cache-dir -r /tmp/requirements.txt

# アプリケーションコードをコピー
#COPY . /app

# ベースイメージとしてPython 3.8を使用
FROM python:3.9

# /app ディレクトリを作成
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /app

# ドキュメンテーションのためにポートを公開
EXPOSE 8000

# アプリケーションを起動（ポート番号を環境変数により指定）
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
