# ベースイメージとしてNginxを使用
FROM nginx:latest

# ビルド済みのWebサイトをNginxが配信できるようにコピー
#COPY ./dist/spa /usr/share/nginx/html

# Nginxのデフォルトポートを公開
EXPOSE 80

# Nginxを前景で実行
CMD ["nginx", "-g", "daemon off;"]