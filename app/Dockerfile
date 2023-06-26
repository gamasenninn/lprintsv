# FastAPI公式のベースイメージを使用
FROM tiangolo/uvicorn-gunicorn:python3.9

# メンテナ情報（必要に応じて変更）
#LABEL maintainer="Your Name <your-email@example.com>"

# 依存関係をコピーしてインストール
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

