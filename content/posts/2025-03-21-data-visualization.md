---
title: "Pythonで株価を可視化する - matplotlibとPlotlyで美しいチャート作成"
date: 2025-03-21T02:20:00+09:00
draft: false
categories:
  - beginner
tags:
  - Python
  - 可視化
  - matplotlib
  - Plotly
  - 株価チャート
description: "PythonのmatplotlibとPlotlyを使って、株価データを美しく可視化する方法を解説。インタラクティブなチャートまで作成できます。"
math: true
code: true
---

## はじめに

取得した株価データを**分かりやすく可視化**することは、分析の第一歩です。

この記事では、Pythonの代表的な可視化ライブラリ **matplotlib** と **Plotly** を使って、株価チャートを作成する方法を解説します。

## 使用するライブラリ

| ライブラリ | 特徴 | 用途 |
|-----------|------|------|
| **matplotlib** | 静的なチャート | 論文、レポート |
| **Plotly** | インタラクティブ | Webアプリ、ダッシュボード |
| **mplfinance** | 金融特化 | ローソク足チャート |

## 準備

```bash
pip install matplotlib plotly mplfinance pandas yfinance
```

## matplotlibでの基本チャート

### 株価の推移をラインチャートで表示

```python
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# データ取得
ticker = "AAPL"
stock = yf.Ticker(ticker)
df = stock.history(period="1y")

# チャート作成
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='#1a5f2a')

# 移動平均線を追加
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()
plt.plot(df.index, df['MA20'], label='MA20', alpha=0.7, color='orange')
plt.plot(df.index, df['MA50'], label='MA50', alpha=0.7, color='red')

# チャートの装飾
plt.title(f'{ticker} Stock Price with Moving Averages', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Price (USD)', fontsize=12)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# 保存と表示
plt.savefig(f'{ticker}_chart.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 複数銘柄の比較チャート

```python
# 複数銘柄を取得
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
data = yf.download(tickers, period='1y')['Close']

# 正規化（年初を100とする）
normalized = data / data.iloc[0] * 100

# チャート作成
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(normalized.index, normalized[ticker], label=ticker, linewidth=2)

plt.title('Stock Price Comparison (Normalized)', fontsize=16, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Normalized Price (Base=100)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## mplfinanceでローソク足チャート

```python
import mplfinance as mpf

# データ取得（3ヶ月分）
df = yf.download('AAPL', period='3mo')

# カラースタイルの設定
mc = mpf.make_marketcolors(
    up='green',    # 陽線
    down='red',    # 陰線
    edge='inherit',
    wick='inherit'
)

s = mpf.make_mpf_style(
    marketcolors=mc,
    figsize=(12, 6),
    gridstyle='-',
    gridcolor='gray',
    gridalpha=0.3
)

# ローソク足チャート作成
mpf.plot(
    df,
    type='candle',
    style=s,
    title='AAPL Candlestick Chart',
    ylabel='Price (USD)',
    volume=True,           # 出来高も表示
    mav=(20, 50),          # 移動平均線
    tight_layout=True,
    savefig='candlestick.png'
)
```

## Plotlyでインタラクティブチャート

### 基本のラインチャート

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# データ取得
df = yf.download('AAPL', period='1y')

# チャート作成
fig = go.Figure()

# 終値のライン
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['Close'],
    mode='lines',
    name='Close Price',
    line=dict(color='#1a5f2a', width=2)
))

# 高値・安値のレンジ
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['High'],
    mode='lines',
    name='High',
    line=dict(color='green', width=1, dash='dash'),
    opacity=0.5
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['Low'],
    mode='lines',
    name='Low',
    line=dict(color='red', width=1, dash='dash'),
    opacity=0.5
))

# レイアウト設定
fig.update_layout(
    title='AAPL Stock Price (Interactive)',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    hovermode='x unified',
    template='plotly_white'
)

# 表示（HTMLとして保存も可能）
fig.show()
fig.write_html('interactive_chart.html')
```

### ローソク足＋出来高

```python
# サブプロット作成（2行1列）
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.7, 0.3],
    subplot_titles=('AAPL Price', 'Volume')
)

# ローソク足
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ),
    row=1, col=1
)

# 出来高
fig.add_trace(
    go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color='blue'
    ),
    row=2, col=1
)

# レイアウト
fig.update_layout(
    title='AAPL Stock Price with Volume',
    xaxis_rangeslider_visible=False,
    height=600
)

fig.show()
```

## リターン分布の可視化

```python
# 日次リターンの計算
returns = df['Close'].pct_change().dropna()

# ヒストグラム
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# ヒストグラム
ax1.hist(returns, bins=50, edgecolor='black', alpha=0.7, color='#1a5f2a')
ax1.axvline(returns.mean(), color='red', linestyle='--', label=f'Mean: {returns.mean():.4f}')
ax1.axvline(returns.median(), color='orange', linestyle='--', label=f'Median: {returns.median():.4f}')
ax1.set_xlabel('Daily Return')
ax1.set_ylabel('Frequency')
ax1.set_title('Distribution of Daily Returns')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Q-Qプロット（正規性の確認）
from scipy import stats
stats.probplot(returns, dist="norm", plot=ax2)
ax2.set_title('Q-Q Plot (Normality Check)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## まとめ

| ライブラリ | おすすめ用途 |
|-----------|-------------|
| **matplotlib** | 論文、静的レポート |
| **mplfinance** | ローソク足、金融特化 |
| **Plotly** | Webダッシュボード、インタラクティブな分析 |

**次のステップ:**
- [Plotly Dashで株価ダッシュボードを作成](/posts/plotly-dashboard/)

---

**関連記事:**
- [Pythonで株価データを取得する](/posts/python-stock-data/)
