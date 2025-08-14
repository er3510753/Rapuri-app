# Node.jsのLTSバージョンをベースイメージとして使用
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルを先にコピーしてキャッシュを活用
COPY package.json package-lock.json ./

# 依存関係をインストール
# `npm ci` は package-lock.json から依存関係をインストールするため、より高速で確実です。
RUN npm ci

# プロジェクトのソースコードをコピー
COPY . .

# Expoが使用するポートを公開
# 8081: Metro Bundler
EXPOSE 8081

# アプリケーションを起動
CMD ["npm", "start"]
