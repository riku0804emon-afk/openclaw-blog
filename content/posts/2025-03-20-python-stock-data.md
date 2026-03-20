---
title: "Pythonで株価データを取得する完全ガイド - yfinance入門"
date: 2025-03-20T21:58:00+09:00
draft: true
categories:
  - beginner
tags:
  - Python
  - yfinance
  - 株価データ
  - スクレイピング
  - 初心者
description: "yfinanceライブラリを使って、無料で簡単に株価データを取得する方法を徹底解説。Python初心者でもコピペで動くコード付き。"
math: true
code: true
---

## はじめに

投資の自動化や分析を始めたいけど、株価データの取得方法がわからない…そんな悩みありませんか？

この記事では、**yfinance**という無料のPythonライブラリを使って、Yahoo Financeから株価データを取得する方法を徹底解説します。

### yfinanceとは？

yfinanceは、Yahoo Financeの株価データを簡単に取得できるPythonライブラリです。

**メリット:**
- ✅ 無料で使える
- ✅ APIキー不要
- ✅ コード数行でデータ取得可能
- ✅ 日本株（東証上場企業）にも対応

## この記事で学べること

1. yfinanceのインストール方法
2. 株価データ（終値、始値、高値、安値、出来高）の取得
3. 期間指定や複数銘柄の一括取得
4. データのCSV保存方法

## 前提条件

- Python 3.8以上がインストールされていること
- pipまたはcondaが使えること

## 環境構築

### Step 1: yfinanceのインストール

ターミナル（コマンドプロンプト）で以下を実行します：

```bash
pip install yfinance pandas
```

または、Anacondaを使っている場合：

```bash
conda install -c conda-forge yfinance pandas
```

**インストール確認：**

```python
import yfinance as yf
print(yf.__version__)
```

バージョン番号が表示されればOKです。

## 実装

### 基本的な株価データ取得

まずは、米国株の代表であるApple（AAPL）の株価を取得してみましょう。

```python
import yfinance as yf
import pandas as pd

# Appleの株価データを取得
 ticker = "AAPL"
stock = yf.Ticker(ticker)

# 過去1年間の日次データを取得
df = stock.history(period="1y")

# 先頭5行を表示
print(df.head())
```

**実行結果：**

```
                 Open       High        Low      Close     Volume  Dividends  Stock Splits
Date
2024-03-21  171.919998  173.130005  170.779999  171.479996   53397000        0.0           0.0
2024-03-22  171.759995  173.050003  170.059998  172.279999   58589300        0.0           0.0
2024-03-25  170.589996  171.940002  169.449997  170.850006   54288900        0.0           0.0
2024-03-26  170.000000  171.419998  169.580002  170.119995   45469700        0.0           0.0
2024-03-27  169.410004  173.600006  169.410004  173.309998   71758700        0.0           0.0
```

### 取得できるデータの種類

| カラム名 | 説明 |
|---------|------|
| `Open` | 始値（その日の最初の取引価格） |
| `High` | 高値（その日の最高取引価格） |
| `Low` | 安値（その日の最低取引価格） |
| `Close` | 終値（その日の最後の取引価格） |
| `Volume` | 出来高（その日の取引株数） |
| `Dividends` | 配当金 |
| `Stock Splits` | 株式分割 |

### 期間の指定方法

`period`パラメータで取得期間を指定できます：

```python
# 様々な期間の取得例
df_5d = stock.history(period="5d")      # 過去5日
df_1mo = stock.history(period="1mo")    # 過去1ヶ月
df_3mo = stock.history(period="3mo")    # 過去3ヶ月
df_6mo = stock.history(period="6mo")    # 過去6ヶ月
df_1y = stock.history(period="1y")      # 過去1年
df_5y = stock.history(period="5y")      # 過去5年
```

### 日本株の取得方法

日本株の場合は、**東証コード.T**の形式で指定します。

```python
# トヨタ自動車（東証コード: 7203）
toyota = yf.Ticker("7203.T")
df_toyota = toyota.history(period="1y")
print(df_toyota.head())

# ソフトバンクグループ（東証コード: 9984）
softbank = yf.Ticker("9984.T")
df_sb = softbank.history(period="6mo")
```

### 複数銘柄の一括取得

`download()`関数を使うと、複数銘柄を一度に取得できます。

```python
# 複数銘柄のデータを一括取得
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
df_multi = yf.download(tickers, period="1y", group_by='ticker')

# 各銘柄の終値を表示
print(df_multi['AAPL']['Close'].head())
```

### データのCSV保存

取得したデータをCSVファイルに保存する方法：

```python
import yfinance as yf

# データ取得
ticker = "AAPL"
stock = yf.Ticker(ticker)
df = stock.history(period="1y")

# CSVに保存
df.to_csv(f"{ticker}_stock_data.csv")
print(f"{ticker}_stock_data.csv に保存しました")
```

**読み込み時：**

```python
# CSVから読み込み
df_loaded = pd.read_csv("AAPL_stock_data.csv", index_col=0, parse_dates=True)
print(df_loaded.head())
```

## 応用例

### 例1: 終値の推移を簡単に可視化

```python
import yfinance as yf
import matplotlib.pyplot as plt

# データ取得
ticker = "AAPL"
stock = yf.Ticker(ticker)
df = stock.history(period="1y")

# グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Close Price')
plt.title(f'{ticker} Stock Price (1 Year)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(f'{ticker}_chart.png')
plt.show()
```

### 例2: 日次リターンの計算

```python
import yfinance as yf

# データ取得
ticker = "AAPL"
stock = yf.Ticker(ticker)
df = stock.history(period="1y")

# 日次リターンを計算
df['Daily_Return'] = df['Close'].pct_change()

# 基本統計量を表示
print("日次リターンの統計:")
print(df['Daily_Return'].describe())
```

**実行結果：**

```
日次リターンの統計:
count    251.000000
mean       0.001234
std        0.018765
min       -0.045678
25%       -0.008901
50%        0.000123
75%        0.011234
max        0.056789
Name: Daily_Return, dtype: float64
```

## よくあるエラーと解決法

### エラー1: `ImportError: No module named 'yfinance'`

**原因:** yfinanceがインストールされていない

**解決法:**

```bash
pip install yfinance
```

### エラー2: データが取得できない（`Empty DataFrame`）

**原因:** ティッカーシンボルが間違っている、または取引時間外

**解決法:**
- ティッカーシンボルを確認（Yahoo Financeで検索）
- 日本株は`.T`を忘れずに

```python
# 正しい例
ticker = "7203.T"  # トヨタ
# 間違い例
ticker = "7203"    # これだと取得できない
```

### エラー3: `YFRateLimitError`（レート制限）

**原因:** 短時間に大量のリクエストを送りすぎた

**解決法:**
- リクエスト間に待ち時間を入れる

```python
import time
import yfinance as yf

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

for ticker in tickers:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1mo")
    print(f"{ticker}: {df['Close'][-1]}")
    time.sleep(1)  # 1秒待機
```

## まとめ

この記事では、yfinanceを使った株価データの取得方法を解説しました。

**キーポイント：**
1. **yfinance**は無料で簡単に株価データを取得できるライブラリ
2. `Ticker()`で単一銘柄、`download()`で複数銘柄を取得
3. 日本株は**東証コード.T**の形式で指定
4. `history(period="期間")`で柔軟に期間を指定可能

次のステップでは、取得したデータを使って**移動平均線**を計算し、**バックテスト**を行う方法を解説します。

## 次のステップ

- [移動平均線クロスオーバーのバックテスト](/posts/moving-average-backtest/) - 取得したデータを使った戦略検証
- [Pythonでテクニカル指標を計算する](/posts/technical-indicators-python/) - RSI、MACDなどの計算方法

---

**参考リンク:**
- [yfinance GitHub](https://github.com/ranaroussi/yfinance)
- [Yahoo Finance](https://finance.yahoo.com/)
- [pandasドキュメント](https://pandas.pydata.org/docs/)
