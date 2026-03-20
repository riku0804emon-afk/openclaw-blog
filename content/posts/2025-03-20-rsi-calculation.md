---
title: "RSI（相対力指数）の計算と可視化 - Python実装"
date: 2025-03-20T22:31:00+09:00
draft: true
categories:
  - technical
tags:
  - Python
  - RSI
  - テクニカル分析
  - オシレーター
  - トレーディング
description: "RSI（相対力指数）の計算式を理解し、Pythonでゼロから実装。過買い・過売いの判定と売買シグナルの生成方法を解説。"
math: true
code: true
---

## はじめに

RSI（Relative Strength Index、相対力指数）は、**価格の変動の強さを測るオシレーター**です。

「株価が上がりすぎたか、下がりすぎたか」を数値化し、**30以下（過売い）**や**70以上（過買い）**を売買のタイミングとして使います。

この記事では、RSIの計算式を理解し、Pythonでゼロから実装します。

## RSIとは？

### 基本的な考え方

RSIは、**過去n日間の値上がり幅と値下がり幅の比率**を表します。

$$RSI = 100 - \frac{100}{1 + RS}$$

ここで、$RS$（Relative Strength）は：

$$RS = \frac{過去n日間の平均値上がり幅}{過去n日間の平均値下がり幅}$$

### 解釈の仕方

| RSI値 | 状態 | トレーディングの意味 |
|-------|------|---------------------|
| 70以上 | 過買い（Overbought） | 売りのサイン |
| 50 | 中立 | トレンドの転換点 |
| 30以下 | 過売い（Oversold） | 買いのサイン |

### 計算ステップ

1. **前日比の変化**を計算
2. **値上がり/値下がり**に分類
3. **平均値上がり幅・平均値下がり幅**を計算（通常は14日）
4. **RS**を計算
5. **RSI**を計算

## Pythonでの実装

### Step 1: データ取得

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Appleのデータを取得
ticker = "AAPL"
df = yf.download(ticker, period="2y")
df = df['Close'].to_frame()

print(df.head())
```

### Step 2: RSIの計算

```python
def calculate_rsi(prices, period=14):
    """
    RSIを計算する関数
    
    Parameters:
        prices: 株価データ（ pandas Series）
        period: RSIの期間（デフォルト14）
    
    Returns:
        RSI値のSeries
    """
    # 前日比の変化
    delta = prices.diff()
    
    # 値上がりと値下がりに分ける
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # RSを計算
    rs = gain / loss
    
    # RSIを計算
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# RSIを計算（14日）
df['RSI'] = calculate_rsi(df['Close'], period=14)

# 最初の14日はNaNになるので削除
df = df.dropna()

print(df.head(20))
```

### 精度向上版：指数移動平均を使用

上記の単純移動平均（SMA）版RSIは簡単ですが、**指数移動平均（EMA）**を使う方が一般的です。

```python
def calculate_rsi_ema(prices, period=14):
    """
    EMAを使用したRSI計算（Wilder's method）
    """
    delta = prices.diff()
    
    # 最初の平均はSMAで計算
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # EMAのスムージング係数
    alpha = 1 / period
    
    # EMAを計算
    avg_gain = gain.ewm(alpha=alpha, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=alpha, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

df['RSI_EMA'] = calculate_rsi_ema(df['Close'], period=14)
```

### Step 3: 可視化

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]})

# 価格チャート
ax1.plot(df.index, df['Close'], label='Close Price', color='black')
ax1.set_ylabel('Price')
ax1.set_title(f'{ticker} - Price & RSI')
ax1.legend()
ax1.grid(True, alpha=0.3)

# RSIチャート
ax2.plot(df.index, df['RSI'], label='RSI(14)', color='blue')
ax2.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
ax2.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
ax2.fill_between(df.index, 70, 100, alpha=0.2, color='red')
ax2.fill_between(df.index, 0, 30, alpha=0.2, color='green')
ax2.set_ylabel('RSI')
ax2.set_xlabel('Date')
ax2.set_ylim(0, 100)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rsi_chart.png', dpi=150)
plt.show()
```

## トレーディングシグナルの生成

### 基本シグナル

```python
# シグナル生成
df['Signal'] = 0
df.loc[df['RSI'] < 30, 'Signal'] = 1   # 過売い→買い
df.loc[df['RSI'] > 70, 'Signal'] = -1  # 過買い→売り

# シグナルポイントの抽出
buy_signals = df[df['Signal'] == 1].index
sell_signals = df[df['Signal'] == -1].index

print(f"買いシグナル回数: {len(buy_signals)}")
print(f"売りシグナル回数: {len(sell_signals)}")
```

### シグナルの可視化

```python
fig, ax = plt.subplots(figsize=(14, 6))

# 価格
ax.plot(df.index, df['Close'], label='Close Price', color='black', alpha=0.7)

# シグナル
ax.scatter(buy_signals, df.loc[buy_signals, 'Close'], 
          color='green', marker='^', s=100, label='Buy Signal (RSI<30)', zorder=5)
ax.scatter(sell_signals, df.loc[sell_signals, 'Close'], 
          color='red', marker='v', s=100, label='Sell Signal (RSI>70)', zorder=5)

ax.set_ylabel('Price')
ax.set_title(f'{ticker} - RSI Trading Signals')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rsi_signals.png', dpi=150)
plt.show()
```

## RSIの応用テクニック

### 1. RSIのダイバージェンス検出

**ダイバージェンス（ Divergence）**とは、価格とRSIの動きが逆方向に進む現象です。

```python
def find_divergence(df, lookback=5):
    """
    ダイバージェンスを検出する関数
    """
    divergence_signals = []
    
    for i in range(lookback, len(df) - lookback):
        window = df.iloc[i-lookback:i+lookback+1]
        
        # 価格の高値/安値
        price_low = window['Close'].min()
        price_high = window['Close'].max()
        
        # RSIの高値/安値
        rsi_low = window['RSI'].min()
        rsi_high = window['RSI'].max()
        
        # 現在値
        current_price = df.iloc[i]['Close']
        current_rsi = df.iloc[i]['RSI']
        
        # ベアリッシュダイバージェンス（価格上昇、RSI下降）
        if current_price > price_low and current_rsi < rsi_low + 5:
            divergence_signals.append({'date': df.index[i], 'type': 'Bearish'})
        
        # ブルリッシュダイバージェンス（価格下降、RSI上昇）
        elif current_price < price_high and current_rsi > rsi_high - 5:
            divergence_signals.append({'date': df.index[i], 'type': 'Bullish'})
    
    return divergence_signals
```

### 2. RSIの移動平均

```python
# RSIの9日移動平均（シグナル線）
df['RSI_MA'] = df['RSI'].rolling(window=9).mean()

# RSIがそのMAを上抜けたら買い、下抜けたら売り
df['RSI_Signal'] = np.where(df['RSI'] > df['RSI_MA'], 1, 
                   np.where(df['RSI'] < df['RSI_MA'], -1, 0))
```

## よくあるエラーと解決法

### エラー1: RSIがNaNになる

**原因:** データが不足している

**解決法:**
```python
# period分以上のデータがあるか確認
if len(df) < period:
    raise ValueError(f"データが不足しています。{period}日分以上必要です。")
```

### エラー2: RSIが100や0で固定される

**原因:** 長期間同じ方向に価格が動き続けた

**対策:**
```python
# 極値をクリップ
rsi = rsi.clip(0, 100)
```

## まとめ

この記事では、RSIの計算とPython実装を学びました。

**キーポイント:**
1. RSI = 100 - (100 / (1 + RS))
2. 30以下は過売い（買い）、70以上は過買い（売り）
3. EMA版のRSIが一般的に使用される
4. ダイバージェンス検出でより精度を上げられる

**注意点:**
- RSIは強いトレンド中に長期間過買い/過売いのままになることがある
- **単独では使わず**、他の指標と組み合わせることが重要

---

**関連記事:**
- [移動平均線クロスオーバーのバックテスト](/posts/moving-average-backtest/)
- [MACDの計算と使い方](/posts/macd-trading/)

**参考リンク:**
- [RSI - Investopedia](https://www.investopedia.com/terms/r/rsi.asp)
