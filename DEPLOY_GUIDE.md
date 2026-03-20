# algo-money.dev デプロイ完全ガイド

このガイドでは、`algo-money.dev` ドメインの取得から、GitHub Pages + Cloudflare + Hugo ブログの公開までの手順を解説します。

---

## 概要

```
[ユーザー] → [Cloudflare DNS] → [GitHub Pages] → [Hugo ブログ]
                ↓                      ↓
           SSL証明書自動発行      無料ホスティング
```

**使用サービス:**
- **ドメイン**: algo-money.dev（Cloudflare Registrar or お名前.com）
- **ホスティング**: GitHub Pages（無料）
- **DNS/SSL**: Cloudflare（無料）
- **ビルド**: GitHub Actions（無料）

---

## Step 1: GitHub リポジトリの作成

### 1.1 リポジトリ作成

1. [GitHub](https://github.com) にログイン
2. 右上の「+」→「New repository」
3. 設定:
   - **Repository name**: `algo-money-dev`（任意）
   - **Description**: `Pythonで始めるアルゴリズム投資ブログ`
   - **Public** を選択
   - **Add a README file**: ✅ チェック
4. 「Create repository」

### 1.2 ローカルファイルのプッシュ

```bash
# ブログディレクトリに移動
cd C:\Users\riku0\.openclaw\workspace\algo-money-blog

# Git初期化
git init

# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/algo-money-dev.git

# すべてのファイルをステージング
git add .

# コミット
git commit -m "Initial commit: Hugo blog setup with 5 posts"

# プッシュ
git push -u origin main
```

---

## Step 2: ドメインの取得

### 2.1 Cloudflare Registrar で取得（推奨）

Cloudflareでドメインを取得すると、DNS設定とSSLが自動化されます。

1. [Cloudflare Dashboard](https://dash.cloudflare.com) にログイン
2. 右上「Add site」
3. ドメイン名に `algo-money.dev` を入力
4. 「Add site」
5. プラン選択で **Free** を選択
6. ドメイン購入画面で手続き（年間 ~$10-15）

### 2.2 お名前.com で取得する場合

1. [お名前.com](https://www.onamae.com) にアクセス
2. 「algo-money.dev」で検索
3. カートに追加して購入手続き（~1,500円/年）
4. 後で Cloudflare のネームサーバーに変更

---

## Step 3: Hugo テーマのセットアップ

### 3.1 Git サブモジュールとしてテーマを追加

```bash
# ブログディレクトリで実行
cd algo-money-blog

# Ananke テーマを追加
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke

# コミット
git add .
git commit -m "Add Ananke theme as submodule"
git push
```

### 3.2 テーマのカスタマイズ（オプション）

テーマをカスタマイズする場合は、 `layouts/` ディレクトリに同名ファイルを作成して上書きします。

```bash
# カスタムレイアウト用ディレクトリ作成
mkdir -p layouts/_default
mkdir -p layouts/partials
```

---

## Step 4: GitHub Actions の設定

### 4.1 ワークフローファイルの作成

`.github/workflows/gh-pages.yml` を作成:

```yaml
name: GitHub Pages

on:
  push:
    branches:
      - main  # ソースブランチ
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-22.04
    permissions:
      contents: write
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true  # テーマのサブモジュールを取得
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: '0.121.0'
          extended: true

      - name: Build
        run: hugo --minify

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

### 4.2 ファイルをプッシュ

```bash
git add .github/workflows/gh-pages.yml
git commit -m "Add GitHub Actions workflow for GitHub Pages"
git push
```

---

## Step 5: GitHub Pages の有効化

### 5.1 設定を変更

1. GitHub リポジトリページを開く
2. 「Settings」タブ → 左メニュー「Pages」
3. **Source**: 「Deploy from a branch」に変更
4. **Branch**: `gh-pages` / `/(root)` を選択
5. 「Save」

### 5.2 カスタムドメインの設定

1. 「Custom domain」欄に `algo-money.dev` を入力
2. 「Save」
3. 「Enforce HTTPS」にチェック（SSL有効化）

---

## Step 6: Cloudflare DNS の設定

### 6.1 Cloudflare で DNS レコードを追加

1. [Cloudflare Dashboard](https://dash.cloudflare.com) でドメインを選択
2. 「DNS」→「Records」タブ
3. 以下のレコードを追加:

| Type | Name | Content | TTL | Proxy status |
|------|------|---------|-----|--------------|
| A | @ | 185.199.108.153 | Auto | Proxied |
| A | @ | 185.199.109.153 | Auto | Proxied |
| A | @ | 185.199.110.153 | Auto | Proxied |
| A | @ | 185.199.111.153 | Auto | Proxied |
| CNAME | www | YOUR_USERNAME.github.io | Auto | Proxied |

**注意**: `YOUR_USERNAME` はあなたの GitHub ユーザー名に置き換えてください。

### 6.2 GitHub Pages の IP アドレス確認

最新の IP アドレスは GitHub Docs で確認:
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

### 6.3 ネームサーバー設定（お名前.comの場合）

お名前.com でドメインを取得した場合:

1. お名前.com の管理画面で「ネームサーバー変更」
2. 以下の Cloudflare ネームサーバーに変更:
   - `chad.ns.cloudflare.com`
   - `gwen.ns.cloudflare.com`
   （※実際のネームサーバーは Cloudflare で確認）

---

## Step 7: CNAME ファイルの作成

### 7.1 static ディレクトリに CNAME ファイルを作成

```bash
# static ディレクトリ作成
mkdir -p static

# CNAME ファイル作成
echo "algo-money.dev" > static/CNAME
```

### 7.2 コミット

```bash
git add static/CNAME
git commit -m "Add custom domain CNAME file"
git push
```

---

## Step 8: デプロイの確認

### 8.1 GitHub Actions の実行確認

1. リポジトリの「Actions」タブを開く
2. ワークフローが正常に完了するまで待つ（2-3分）
3. 緑のチェックマークが表示されれば成功

### 8.2 サイトにアクセス

ブラウザで以下にアクセス:
- `https://algo-money.dev`
- `https://www.algo-money.dev`

**注意**: DNS 伝播には最大 24時間かかる場合があります。すぐにアクセスできない場合は少し待ってください。

---

## Step 9: 記事の更新方法

### 9.1 新しい記事を追加

```bash
# 新規記事を生成
python generate_post.py "記事タイトル" beginner "Python, タグ" "記事の説明"

# または手動で作成
hugo new content posts/2025-03-21-new-post.md
```

### 9.2 記事を編集

```bash
# Markdownファイルを編集
# content/posts/YYYY-MM-DD-title.md

# draft: false に変更して公開
```

### 9.3 デプロイ

```bash
git add .
git commit -m "Add new post: 記事タイトル"
git push
```

push すると GitHub Actions が自動でビルド・デプロイを行います。

---

## Step 10: カスタマイズ

### 10.1 Google Analytics 追加

`config.toml` に追加:

```toml
[params]
  googleAnalytics = 'G-XXXXXXXXXX'  # あなたのトラッキングID
```

### 10.2 コメント機能追加（Giscus）

1. [Giscus](https://giscus.app) にアクセス
2. GitHub リポジトリと連携
3. 生成されたコードを `layouts/partials/comments.html` に追加

### 10.3 SEO 対策

`config.toml` で設定:

```toml
[params]
  description = 'Pythonで始めるアルゴリズム投資ブログ'
  keywords = ['Python', '投資', 'アルゴリズム取引']
  author = 'りく'
```

---

## トラブルシューティング

### 問題1: DNS エラー

**症状**: `algo-money.dev` にアクセスできない

**解決策**:
1. Cloudflare DNS レコードが正しいか確認
2. `dig algo-money.dev` または `nslookup algo-money.dev` で確認
3. 24時間待つ

### 問題2: SSL エラー

**症状**: HTTPS でアクセスできない

**解決策**:
1. GitHub Pages の設定で「Enforce HTTPS」が有効になっているか確認
2. Cloudflare で SSL/TLS 設定を「Full (strict)」に変更

### 問題3: ビルドエラー

**症状**: GitHub Actions が失敗する

**解決策**:
1. Actions タブでエラーログを確認
2. Hugo バージョンが互換性があるか確認
3. テーマのサブモジュールが正しく取得できているか確認:
   ```bash
   git submodule update --init --recursive
   ```

---

## コスト見積もり

| 項目 | サービス | 料金 |
|------|----------|------|
| ドメイン | Cloudflare Registrar | ~$12/年 (~1,800円) |
| ホスティング | GitHub Pages | 無料 |
| DNS/SSL | Cloudflare | 無料 |
| ビルド | GitHub Actions | 無料（月2000分まで） |
| **合計** | | **~1,800円/年** |

---

## 完了チェックリスト

- [ ] GitHub リポジトリ作成
- [ ] ローカルファイルをプッシュ
- [ ] Hugo テーマをサブモジュールとして追加
- [ ] GitHub Actions ワークフロー作成
- [ ] GitHub Pages 有効化
- [ ] ドメイン取得
- [ ] Cloudflare DNS 設定
- [ ] CNAME ファイル作成
- [ ] 初回デプロイ完了
- [ ] HTTPS アクセス確認
- [ ] Google Analytics 設定（オプション）
- [ ] コメント機能設定（オプション）

---

## 参考リンク

- [Hugo ドキュメント](https://gohugo.io/documentation/)
- [GitHub Pages ドキュメント](https://docs.github.com/ja/pages)
- [Cloudflare DNS ドキュメント](https://developers.cloudflare.com/dns/)
- [Hugo + GitHub Pages チュートリアル](https://gohugo.io/hosting-and-deployment/hosting-on-github/)

---

**最終更新**: 2025-03-20
