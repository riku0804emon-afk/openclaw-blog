# algo-money.dev サイト設計書

## 1. カテゴリ構成

| カテゴリ名 | 説明 | 対象読者 |
|-----------|------|----------|
| **入門編** | Python環境構築、基本的な株価データ取得、ライブラリ紹介 | 完全初心者 |
| **テクニカル分析** | 移動平均線、RSI、MACDなどのテクニカル指標をPython実装 | 初〜中級者 |
| **ポートフォリオ理論** | リスク・リターン計算、最適化、シャープレシオなど数理ファイナンス | 中〜上級者 |
| **アルゴリズム戦略** | バックテスト、自動売買ロジック、機械学習導入 | 中〜上級者 |
| **実践・運用** | 実際の証券会社API連携、本番運用の注意点、リスク管理 | 上級者 |

## 2. サイトマップ

```
algo-money.dev/
├── /                          # トップページ（最新記事一覧）
├── /about/                    # 自己紹介、サイト理念
├── /categories/               # カテゴリ一覧
│   ├── /beginner/            # 入門編
│   ├── /technical/           # テクニカル分析
│   ├── /portfolio/           # ポートフォリオ理論
│   ├── /algorithm/           # アルゴリズム戦略
│   └── /practice/            # 実践・運用
├── /tags/                     # タグ一覧
├── /archives/                 # 月別アーカイブ
├── /posts/                    # 記事（スラッグ形式）
│   ├── /python-stock-data/   # 各記事
│   └── /moving-average-backtest/
└── /rss.xml                   # RSSフィード
```

## 3. デザイン仕様

### カラースキーム
| 用途 | カラーコード | 説明 |
|------|-------------|------|
| Primary | `#1a5f2a` | 深い緑（お金、成長のイメージ） |
| Secondary | `#2d3748` | 濃いグレー（テキスト） |
| Accent | `#f6ad55` | オレンジ（アクセント、CTA） |
| Background | `#ffffff` | 白（メイン背景） |
| Code BG | `#f7fafc` | 薄いグレー（コードブロック背景） |
| Border | `#e2e8f0` | ボーダー色 |

### フォント
| 用途 | フォント |
|------|----------|
| 見出し | "Noto Sans JP", sans-serif |
| 本文 | "Noto Sans JP", sans-serif |
| コード | "Fira Code", "JetBrains Mono", monospace |
| 数式 | KaTeX（サーバー側レンダリング） |

### レイアウト
- **ヘッダー**: ロゴ（algo-money.dev）+ ナビゲーション（カテゴリ）
- **メインコンテンツ**: 記事本文（max-width: 800px、中央寄せ）
- **サイドバー**: なし（シンプル重視、モバイルファースト）
- **フッター**: コピーライト、SNSリンク、RSS

### 記事ページ構成
1. タイトル（H1）
2. メタ情報（投稿日、更新日、カテゴリ、タグ、読了時間）
3. 目次（TOC、H2/H3から自動生成）
4. 本文（コードブロック、数式対応）
5. シェアボタン
6. 関連記事
7. コメント欄（Utterances or Giscus）

## 4. 技術スタック選定

### 静的サイトジェネレータ: **Hugo**
**選定理由:**
- Go言語製で高速（1,000記事でもビルド秒単位）
- Markdownネイティブ
- テーマが豊富、カスタマイズしやすい
- GitHub Actions連携が簡単

### ホスティング: **GitHub Pages + Cloudflare**
**選定理由:**
- 無料（GitHub Pages）
- カスタムドメイン対応（algo-money.dev）
- CloudflareでSSL + CDN（無料）
- GitHub Actionsで自動デプロイ

### 数式レンダリング: **KaTeX**
**選定理由:**
- MathJaxより高速
- サーバー側レンダリング可能（Hugoプラグインあり）

### コメントシステム: **Giscus**
**選定理由:**
- GitHub Discussions連携
- 無料、広告なし
- 技術ブログに合う

### アナリティクス: **Google Analytics 4** + **Search Console**

## 5. 必要なプラグイン/機能一覧

### Hugo機能
- [ ] 記事テンプレート（archetypes）
- [ ] ショートコード（コードブロック拡張、警告ボックス）
- [ ] RSS生成
- [ ] サイトマップ生成
- [ ] Open Graph / Twitter Card対応

### 外部連携
- [ ] GitHub Actions（自動ビルド・デプロイ）
- [ ] KaTeX（数式レンダリング）
- [ ] highlight.js or Chroma（シンタックスハイライト）
- [ ] Giscus（コメント）

### SEO対策
- [ ] 構造化データ（JSON-LD: Article, BreadcrumbList）
- [ ] meta description自動生成
- [ ] canonical URL設定
- [ ] robots.txt / sitemap.xml

## 6. ファイル構成（Hugo）

```
algo-money-blog/
├── archetypes/
│   └── default.md          # 新規記事テンプレート
├── assets/
│   ├── css/
│   └── js/
├── config.toml             # Hugo設定
├── content/
│   ├── _index.md          # トップページ
│   ├── about.md           # Aboutページ
│   └── posts/             # 記事
├── data/                   # データファイル
├── layouts/
│   ├── _default/          # デフォルトレイアウト
│   ├── partials/          # パーツ
│   └── shortcodes/        # ショートコード
├── static/                 # 静的ファイル（画像等）
└── themes/                 # テーマ（自作 or カスタマイズ）
```

## 7. 今後の拡張予定

- [ ] Newsletter（メールマガジン）- Mailchimp/ConvertKit
- [ ] 検索機能（Algolia DocSearch or Fuse.js）
- [ ] PWA対応（オフライン閲覧）
- [ ] ダークモード対応
