---
title: "Pythonで株価予測 - 線形回帰とランダムフォレストで未来を予測"
date: 2025-03-21T02:35:00+09:00
draft: false
categories:
  - algorithm
tags:
  - Python
  - 機械学習
  - 株価予測
  - scikit-learn
  - ランダムフォレスト
description: "scikit-learnを使って、線形回帰とランダムフォレストで株価を予測。過去のデータから特徴量を作り、翌日の株価を予測するモデルを構築します。"
math: true
code: true
---

## はじめに

**株価は予測できるのか？**

この問いには明確な答えはありませんが、**機械学習を使って統計的な予測**は可能です。

この記事では、Pythonの**scikit-learn**を使って、基本的な株価予測モデルを構築します。

## 注意：予測の限界

⚠️ **重要な免責事項**

- 過去のパターンが未来を保証しない
- ブラックスワン（予測不可能なイベント）がある
- このモデルは**学習目的**であり、実際の取引には使用しないこと

## 準備

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# データ取得
ticker = "AAPL"
df = yf.download(ticker, period="5y")

print(f"データ期間: {df.index[0]} ～ {df.index[-1]}")
print(f"データ数: {len(df)}")
```

## 特徴量エンジニアリング

### テクニカル指標を特徴量として作成

```python
def create_features(df):
    """
    特徴量を作成する関数
    """
    data = df.copy()
    
    # 終値の変化率（リターン）
    data['Return'] = data['Close'].pct_change()
    
    # 移動平均
    data['MA5'] = data['Close'].rolling(window=5).mean()
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # 移動平均との差
    data['Close_MA5'] = data['Close'] - data['MA5']
    data['Close_MA20'] = data['Close'] - data['MA20']
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # ボラティリティ（過去20日の標準偏差）
    data['Volatility'] = data['Return'].rolling(window=20).std()
    
    # 出来高の変化
    data['Volume_Change'] = data['Volume'].pct_change()
    data['Volume_MA20'] = data['Volume'].rolling(window=20).mean()
    
    # 高値・安値との位置
    data['High_Low_Range'] = (data['Close'] - data['Low']) / (data['High'] - data['Low'])
    
    # 翌日の終値（予測対象）
    data['Target'] = data['Close'].shift(-1)
    
    return data

# 特徴量作成
df_features = create_features(df)

# 最初の50日と最後の1日は削除（NaNがあるため）
df_features = df_features.iloc[50:-1]

print("作成された特徴量:")
print(df_features.columns.tolist())
print(f"\n特徴量の統計:")
print(df_features.describe())
```

## 線形回帰モデル

```python
# 特徴量とターゲットを分離
feature_cols = ['Return', 'Close_MA5', 'Close_MA20', 'RSI', 'MACD', 
                'Volatility', 'Volume_Change', 'High_Low_Range']

X = df_features[feature_cols]
y = df_features['Target']

# 訓練データとテストデータに分割（時系列なのでシャッフルしない）
split_point = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_point], X.iloc[split_point:]
y_train, y_test = y.iloc[:split_point], y.iloc[split_point:]

# スケーリング
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 線形回帰モデル
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)

# 予測
lr_pred = lr_model.predict(X_test_scaled)

# 評価
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
lr_r2 = r2_score(y_test, lr_pred)

print("=== 線形回帰モデル ===")
print(f"RMSE: ${lr_rmse:.2f}")
print(f"R²: {lr_r2:.4f}")

# 特徴量の重要度
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'coefficient': lr_model.coef_
}).sort_values('coefficient', key=abs, ascending=False)

print("\n特徴量の係数:")
print(feature_importance)
```

## ランダムフォレストモデル

```python
# ランダムフォレストモデル
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)

rf_model.fit(X_train_scaled, y_train)

# 予測
rf_pred = rf_model.predict(X_test_scaled)

# 評価
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_r2 = r2_score(y_test, rf_pred)

print("\n=== ランダムフォレストモデル ===")
print(f"RMSE: ${rf_rmse:.2f}")
print(f"R²: {rf_r2:.4f}")

# 特徴量の重要度
rf_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n特徴量の重要度:")
print(rf_importance)
```

## 予測結果の可視化

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# 実際の価格と予測価格
dates = y_test.index

ax1.plot(dates, y_test.values, label='Actual', color='black', linewidth=2)
ax1.plot(dates, lr_pred, label='Linear Regression', color='blue', alpha=0.7)
ax1.plot(dates, rf_pred, label='Random Forest', color='green', alpha=0.7)
ax1.set_title('Stock Price Prediction')
ax1.set_ylabel('Price (USD)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 予測誤差
lr_error = y_test.values - lr_pred
rf_error = y_test.values - rf_pred

ax2.plot(dates, lr_error, label='Linear Regression Error', color='blue', alpha=0.5)
ax2.plot(dates, rf_error, label='Random Forest Error', color='green', alpha=0.5)
ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax2.fill_between(dates, lr_error, alpha=0.2, color='blue')
ax2.set_title('Prediction Error')
ax2.set_ylabel('Error (USD)')
ax2.set_xlabel('Date')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('stock_prediction.png', dpi=150)
plt.show()
```

## 翌日の価格予測

```python
# 最新のデータで翌日を予測
latest_features = X.iloc[-1:].values
latest_features_scaled = scaler.transform(latest_features)

lr_next_day = lr_model.predict(latest_features_scaled)[0]
rf_next_day = rf_model.predict(latest_features_scaled)[0]
actual_latest = df['Close'].iloc[-1]

print("=== 翌日の価格予測 ===")
print(f"現在の終値: ${actual_latest:.2f}")
print(f"線形回帰予測: ${lr_next_day:.2f} ({(lr_next_day/actual_latest-1)*100:+.2f}%)")
print(f"ランダムフォレスト予測: ${rf_next_day:.2f} ({(rf_next_day/actual_latest-1)*100:+.2f}%)")
```

## モデルの評価と注意点

```python
# 方向性の正解率（上がるか下がるか）
actual_direction = np.diff(y_test.values) > 0
lr_direction = np.diff(lr_pred) > 0
rf_direction = np.diff(rf_pred) > 0

lr_accuracy = np.mean(actual_direction == lr_direction)
rf_accuracy = np.mean(actual_direction == rf_direction)

print("\n=== 方向性予測の精度 ===")
print(f"ランダム（ベースライン）: 50.00%")
print(f"線形回帰: {lr_accuracy*100:.2f}%")
print(f"ランダムフォレスト: {rf_accuracy*100:.2f}%")
```

## まとめ

**モデルのポイント:**
1. **特徴量エンジニアリング**が重要
2. **線形回帰**は解釈しやすい
3. **ランダムフォレスト**は非線形パターンを捉えられる

**限界:**
- 予測精度は限定的
- 過学習のリスクがある
- 市場の制度変化に弱い

**次のステップ:**
- LSTMなどの深層学習
- アンサンブル学習
- ウォークフォワード検証

---

**免責事項**: この記事は教育目的です。実際の投資判断には使用しないでください。

**関連記事:**
- [Pythonで株価のボラティリティを予測](/posts/volatility-garch/)
