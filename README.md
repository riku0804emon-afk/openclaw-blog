# algo-money.dev ブログ

Pythonで始めるアルゴリズム投資 - 数理ファイナンスとプログラミングの融合

## セットアップ手順

### 1. Hugoのインストール

Windows (PowerShell):
```powershell
winget install Hugo.Hugo.Extended
```

Mac:
```bash
brew install hugo
```

### 2. テーマのインストール

```bash
cd algo-money-blog
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
```

### 3. 記事の作成

```bash
# 手動で作成
hugo new content posts/my-first-post.md

# または自動生成スクリプトを使用
python generate_post.py "記事タイトル" beginner "Python, タグ1, タグ2" "記事の説明"
```

### 4. ローカルプレビュー

```bash
hugo server -D
```

ブラウザで http://localhost:1313 を開く

### 5. ビルド

```bash
hugo  # public/ディレクトリに生成
```

## 記事生成スクリプトの使い方

```bash
# カテゴリ一覧を表示
python generate_post.py -l

# 新規記事を作成
python generate_post.py "記事タイトル" category "タグ1, タグ2" -d "記事の説明"

# 例:
python generate_post.py "Pythonで株価データを取得する" beginner "Python, yfinance, 初心者" "yfinanceライブラリの使い方"
```

## デプロイ（GitHub Pages）

1. GitHubリポジトリを作成
2. `.github/workflows/gh-pages.yml` を設定
3. `algo-money.dev` ドメインを設定
4. プッシュすると自動デプロイ

## ディレクトリ構成

```
algo-money-blog/
├── archetypes/          # 記事テンプレート
├── assets/              # CSS, JS
├── config.toml          # Hugo設定
├── content/             # 記事コンテンツ
│   └── posts/           # ブログ記事
├── layouts/             # HTMLテンプレート
├── static/              # 静的ファイル
├── themes/              # テーマ
├── generate_post.py     # 記事生成スクリプト
└── blog-design.md       # サイト設計書
```

## カテゴリ一覧

| カテゴリ | 説明 |
|---------|------|
| beginner | 入門編 - Python環境構築、基本的な株価データ取得 |
| technical | テクニカル分析 - 移動平均線、RSI、MACDなど |
| portfolio | ポートフォリオ理論 - リスク・リターン計算、最適化 |
| algorithm | アルゴリズム戦略 - バックテスト、自動売買 |
| practice | 実践・運用 - API連携、本番運用 |

## 記事の書き方

1. `generate_post.py` で記事テンプレートを生成
2. `content/posts/xxx.md` を編集
3. `draft: false` に変更して公開
4. `hugo server -D` でプレビュー
5. GitHubにプッシュしてデプロイ