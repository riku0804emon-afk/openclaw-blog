import os
import re
import argparse
from datetime import datetime
from pathlib import Path

# 設定
CONTENT_DIR = "content/posts"
ARCHETYPE_FILE = "archetypes/default.md"

def slugify(text):
    """テキストをURLスラッグに変換"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text

def generate_post(title, category, tags, description=""):
    """
    新規記事を生成する
    
    Args:
        title: 記事タイトル
        category: カテゴリ（beginner/technical/portfolio/algorithm/practice）
        tags: タグのリスト（カンマ区切り文字列 or リスト）
        description: 記事の説明
    """
    # スラッグ生成
    slug = slugify(title)
    date = datetime.now().strftime("%Y-%m-%d")
    datetime_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # タグ処理
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    tags_yaml = "\n  - ".join([""] + tags) if tags else ""
    
    # カテゴリ日本語名
    category_names = {
        "beginner": "入門編",
        "technical": "テクニカル分析",
        "portfolio": "ポートフォリオ理論",
        "algorithm": "アルゴリズム戦略",
        "practice": "実践・運用"
    }
    category_jp = category_names.get(category, category)
    
    # Frontmatter付きMarkdown生成
    template = f"""---
title: "{title}"
date: {datetime_str}
draft: true
categories:
  - {category}
tags:{tags_yaml}
description: "{description}"
math: true
code: true
---

## はじめに

<!-- 記事の導入を書く -->

## この記事で学べること

1. 
2. 
3. 

## 前提条件

- Python 3.8以上がインストールされていること
- pipまたはcondaが使えること

## 環境構築

### 必要なライブラリのインストール

```bash
pip install yfinance pandas matplotlib
```

## 実装

### 基本的なコード

```python
import yfinance as yf
import pandas as pd

# ここにコードを書く
```

### コードの解説

<!-- 各行の解説 -->

## 実行結果

<!-- 実行結果のスクリーンショットや説明 -->

## 応用例

### 例1: 

```python
# 応用コード
```

### 例2: 

```python
# 応用コード
```

## よくあるエラーと解決法

### エラー1: 

**原因:** 

**解決法:** 

```python
# 修正後のコード
```

## まとめ

<!-- 記事のまとめ -->

## 次のステップ

<!-- 関連記事へのリンク -->

---

**関連記事:**
- [前の記事タイトル](/posts/xxx/)
- [次の記事タイトル](/posts/xxx/)

**参考リンク:**
- [公式ドキュメント](https://example.com)
- [GitHubリポジトリ](https://github.com/xxx)
"""
    
    # ファイルパス生成
    filename = f"{date}-{slug}.md"
    filepath = Path(CONTENT_DIR) / filename
    
    # ディレクトリ作成
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # ファイル書き込み
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(template)
    
    print(f"✅ 記事を作成しました: {filepath}")
    print(f"   タイトル: {title}")
    print(f"   カテゴリ: {category_jp}")
    print(f"   タグ: {', '.join(tags)}")
    
    return filepath

def list_categories():
    """利用可能なカテゴリ一覧を表示"""
    categories = {
        "beginner": "入門編 - Python環境構築、基本的な株価データ取得",
        "technical": "テクニカル分析 - 移動平均線、RSI、MACDなど",
        "portfolio": "ポートフォリオ理論 - リスク・リターン計算、最適化",
        "algorithm": "アルゴリズム戦略 - バックテスト、自動売買",
        "practice": "実践・運用 - API連携、本番運用"
    }
    print("\n📂 利用可能なカテゴリ:")
    for key, value in categories.items():
        print(f"  {key:12} - {value}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="algo-money.dev ブログ記事生成ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python generate_post.py "Pythonで株価データを取得する" beginner "Python, yfinance, 初心者" "yfinanceライブラリを使って株価データを取得する方法を解説"
        """
    )
    
    parser.add_argument("title", help="記事タイトル")
    parser.add_argument("category", help="カテゴリ（beginner/technical/portfolio/algorithm/practice）")
    parser.add_argument("tags", help="タグ（カンマ区切り）")
    parser.add_argument("--desc", "-d", default="", help="記事の説明")
    parser.add_argument("--list-categories", "-l", action="store_true", help="カテゴリ一覧を表示")
    
    args = parser.parse_args()
    
    if args.list_categories:
        list_categories()
        return
    
    generate_post(args.title, args.category, args.tags, args.desc)

if __name__ == "__main__":
    main()
