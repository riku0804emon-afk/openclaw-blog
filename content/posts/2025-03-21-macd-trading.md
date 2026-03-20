---
title: "MACD（マックディー）の計算とトレーディング戦略"
date: 2025-03-21T02:25:00+09:00
draft: false
categories:
  - technical
tags:
  - Python
  - MACD
  - テクニカル分析
  - トレーディング
  - トレンド分析
description: "MACD（Moving Average Convergence Divergence）の計算式を理解し、Pythonで実装。ゴールデンクロスとダイバージェンス戦略を解説。"
math: true
code: true
---

## はじめに

**MACD**（Moving Average Convergence Divergence）は、**トレンドの強さと方向**を捉える最も人気のあるテクニカル指標の一つです。

移動平均線の収束と発散を捉えることで、買い・売りのタイミングを判断します。

## MACDとは？

### 計算式

MACDは3つの要素から構成されます：

#### 1. MACDライン
$$MACD = EMA_{12} - EMA_{26}$$

- 12日指数移動平均（短期）から
- 26日指数移動平均（長期）を引いた値

#### 2. シグナルライン
$$Signal = EMA_9(MACD)$$

- MACDラインの9日指数移動平均

#### 3. ヒストグラム（オシレーター）
$$Histogram = MACD - Signal$$

### 解釈の仕方

| 状態 | 意味 | トレードシグナル |
|------|------|-----------------|
| MACD > シグナル | 上昇トレンド | 買い |
| MACD < シグナル | 下降トレンド | 売り |
| ヒストグラム > 0 | 買い圧力 | 強気 |
| ヒストグラム < 0 | 売り圧力 | 弱気 |

## Pythonでの実装

### 基本計算

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# データ取得
ticker = "AAPL"
df = yf.download(ticker, period="2y")

# EMAの計算
def calculate_ema(prices, span):
    return prices.ewm(span=span, adjust=False).mean()

# MACD計算
def calculate_macd(prices, fast=12, slow=26, signal=9):
    # MACDライン
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    
    # シグナルライン
    signal_line = calculate_ema(macd_line, signal)
    
    # ヒストグラム
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

# 計算実行
df['MACD'], df['Signal'], df['Histogram'] = calculate_macd(df['Close'])

# 最初の26日は削除（データが不安定）
df = df.iloc[26:]

print(df[['Close', 'MACD', 'Signal', 'Histogram']].tail())
```

### 可視化

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                gridspec_kw={'height_ratios': [2, 1]})

# 価格チャート
ax1.plot(df.index, df['Close'], label='Close Price', color='black', alpha=0.7)
ax1.set_ylabel('Price (USD)')
ax1.set_title(f'{ticker} - Price & MACD')
ax1.legend()
ax1.grid(True, alpha=0.3)

# MACDチャート
ax2.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=2)
ax2.plot(df.index, df['Signal'], label='Signal', color='red', linewidth=2)

# ヒストグラム（バー）
colors = ['green' if h >= 0 else 'red' for h in df['Histogram']]
ax2.bar(df.index, df['Histogram'], label='Histogram', color=colors, alpha=0.6, width=1)

# ゼロライン
ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)

ax2.set_ylabel('MACD')
ax2.set_xlabel('Date')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('macd_chart.png', dpi=150)
plt.show()
```

## トレーディングシグナル

### ゴールデンクロス / デッドクロス

```python
# シグナル生成
df['Position'] = 0
df.loc[df['MACD'] > df['Signal'], 'Position'] = 1  # 買い
df.loc[df['MACD'] < df['Signal'], 'Position'] = -1  # 売り

# クロスポイントの検出
df['Signal_Change'] = df['Position'].diff()

buy_signals = df[df['Signal_Change'] == 2].index
death_signals = df[df['Signal_Change'] == -2].index

print(f"ゴールデンクロス: {len(buy_signals)}回")
print(f"デッドクロス: {len(death_signals)}回")
```

### シグナルの可視化

```python
fig, ax = plt.subplots(figsize=(14, 7))

# 価格
ax.plot(df.index, df['Close'], label='Close Price', color='black', alpha=0.7)

# シグナル
ax.scatter(buy_signals, df.loc[buy_signals, 'Close'], 
          color='green', marker='^', s=100, label='Golden Cross', zorder=5)
ax.scatter(death_signals, df.loc[death_signals, 'Close'], 
          color='red', marker='v', s=100, label='Death Cross', zorder=5)

ax.set_ylabel('Price (USD)')
ax.set_title(f'{ticker} - MACD Trading Signals')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## MACDダイバージェンス

### ダイバージェンスの検出

```python
def find_divergence(prices, macd, lookback=20):
    """
    MACDダイバージェンスを検出
    """
    divergences = []
    
    for i in range(lookback, len(prices) - lookback):
        # 価格の高値/安値
        price_window = prices.iloc[i-lookback:i+lookback]
        price_high = price_window.max()
        price_low = price_window.min()
        
        # MACDの高値/安値
        macd_window = macd.iloc[i-lookback:i+lookback]
        macd_high = macd_window.max()
        macd_low = macd_window.min()
        
        current_price = prices.iloc[i]
        current_macd = macd.iloc[i]
        
        # ベアリッシュダイバージェンス
        if current_price >= price_high * 0.98 and current_macd <= macd_high * 0.95:
            divergences.append((prices.index[i], 'Bearish', current_price))
        
        # ブルリッシュダイバージェンス
        elif current_price <= price_low * 1.02 and current_macd >= macd_low * 0.95:
            divergences.append((prices.index[i], 'Bullish', current_price))
    
    return divergences

# 検出実行
divs = find_divergence(df['Close'], df['MACD'])

print(f"検出されたダイバージェンス: {len(divs)}個")
for date, type_, price in divs[:5]:
    print(f"  {date.strftime('%Y-%m-%d')}: {type_} at ${price:.2f}")
```

## バックテスト

### MACDクロスオーバー戦略の検証

```python
# ポジションの計算（シグナルラインクロス）
df['Signal_Line'] = np.where(df['MACD'] > df['Signal'], 1, -1)
df['Position'] = df['Signal_Line'].shift(1)  # 翌日オープンでエントリー

# リターン計算
df['Market_Return'] = df['Close'].pct_change()
df['Strategy_Return'] = df['Position'] * df['Market_Return']

# 累積リターン
df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

# パフォーマンス比較
print("=== MACD戦略 vs Buy & Hold ===")
print(f"Buy & Hold リターン: {(df['Cumulative_Market'].iloc[-1] - 1) * 100:.2f}%")
print(f"MACD戦略 リターン: {(df['Cumulative_Strategy'].iloc[-1] - 1) * 100:.2f}%")

# 可視化
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Cumulative_Market'], label='Buy & Hold', color='gray', alpha=0.7)
plt.plot(df.index, df['Cumulative_Strategy'], label='MACD Strategy', color='blue')
plt.title('MACD Strategy Backtest')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## まとめ

**MACDのポイント:**
1. トレンドの方向と強さを捉えられる
2. シグナルラインクロスでシンプルにトレードできる
3. ダイバージェンスで反転シグナルを検出できる

**注意点:**
- 横ばい相場では偽シグナルが多い
- 単独では使わず、他の指標と組み合わせる

---

**関連記事:**
- [RSI（相対力指数）の計算と可視化](/posts/rsi-calculation/)
- [移動平均線クロスオーバーのバックテスト](/posts/moving-average-backtest/)
