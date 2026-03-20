---
title: "Pythonで株価のボラティリティを予測する - GARCHモデル入門"
date: 2025-03-20T22:33:00+09:00
draft: false
categories:
  - algorithm
tags:
  - Python
  - GARCH
  - ボラティリティ
  - 時系列分析
  - 統計モデル
description: "GARCHモデルを使って株価のボラティリティ（変動性）を予測。Pythonでarchライブラリを使った実装と解釈方法を解説。"
math: true
code: true
---

## はじめに

株価の**ボラティリティ（変動性）**は、リスク管理やオプション価格の決定に重要です。

「ボラティリティは常に変化する」という特徴を捉えるために、**GARCHモデル**が広く使われています。

この記事では、GARCHモデルの基礎とPython実装を解説します。

## GARCHモデルとは？

### ボラティリティの特徴

株価のボラティリティには以下の特徴があります：

1. **クラスタリング**: 高いボラティリティの後に高いボラティリティが続きやすい
2. **平均回帰**: 長期的には平均レベルに戻る
3. **レバレッジ効果**: 下落時の方がボラティリティが上がりやすい

### GARCH(1,1)モデル

GARCH（Generalized Autoregressive Conditional Heteroskedasticity）モデルは、
条件付き分散（ボラティリティ）を以下の式でモデル化します：

$$\sigma_t^2 = \omega + \alpha r_{t-1}^2 + \beta \sigma_{t-1}^2$$

ここで：
- $\sigma_t^2$ = 時点$t$での条件付き分散
- $\omega$ = 定数項
- $\alpha$ = ARCH項の係数（前日のリターンの影響）
- $\beta$ = GARCH項の係数（前日のボラティリティの影響）
- $r_{t-1}$ = 前日のリターン

**制約条件:**
- $\omega > 0$
- $\alpha \geq 0, \beta \geq 0$
- $\alpha + \beta < 1$（安定性条件）

## Pythonでの実装

### ライブラリのインストール

```bash
pip install arch yfinance pandas numpy matplotlib
```

### Step 1: データ取得と前処理

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model

# S&P500のデータを取得
ticker = "^GSPC"
data = yf.download(ticker, start="2020-01-01", end="2024-12-31")['Close']

# 日次リターンを計算
returns = 100 * data.pct_change().dropna()  # パーセンテージ表記

print(f"データ期間: {returns.index[0]} ～ {returns.index[-1]}")
print(f"観測数: {len(returns)}")
print(f"平均リターン: {returns.mean():.4f}%")
print(f"リターンの標準偏差: {returns.std():.4f}%")
```

### Step 2: リターンの可視化

```python
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 株価
axes[0].plot(data.index, data, label='S&P 500')
axes[0].set_title('S&P 500 Index')
axes[0].set_ylabel('Price')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# リターン
axes[1].plot(returns.index, returns, label='Daily Returns', alpha=0.7)
axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
axes[1].set_title('Daily Returns (%)')
axes[1].set_ylabel('Return (%)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('returns_analysis.png', dpi=150)
plt.show()
```

### Step 3: GARCH(1,1)モデルの推定

```python
# GARCH(1,1)モデルを構築
model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal')

# モデルをフィット
result = model.fit(update_freq=5)

print(result.summary())
```

### Step 4: 結果の解釈

```python
# 推定されたパラメータ
params = result.params
omega = params['omega']
alpha = params['alpha[1]']
beta = params['beta[1]']

print(f"\n=== 推定パラメータ ===")
print(f"ω (定数項): {omega:.6f}")
print(f"α (ARCH項): {alpha:.4f}")
print(f"β (GARCH項): {beta:.4f}")
print(f"α + β (持続性): {alpha + beta:.4f}")
print(f"長期分散: {omega / (1 - alpha - beta):.4f}")

# 持続性の解釈
persistence = alpha + beta
if persistence > 0.95:
    print("\n高い持続性: ショックは長期間影響を残します")
elif persistence > 0.9:
    print("\n中程度の持続性: ショックは中期的に影響を残します")
else:
    print("\n低い持続性: ショックは短期間で消散します")
```

### Step 5: 条件付きボラティリティの可視化

```python
# 条件付きボラティリティを取得
conditional_volatility = result.conditional_volatility

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(returns.index, conditional_volatility, label='Conditional Volatility', color='red')
ax.set_ylabel('Volatility (%)')
ax.set_xlabel('Date')
ax.set_title('GARCH(1,1) Estimated Volatility')
ax.legend()
ax.grid(True, alpha=0.3)

# ボラティリティが高かった時期を強調
high_vol_periods = conditional_volatility[conditional_volatility > conditional_volatility.quantile(0.95)]
ax.scatter(high_vol_periods.index, high_vol_periods.values, color='orange', s=20, zorder=5)

plt.tight_layout()
plt.savefig('garch_volatility.png', dpi=150)
plt.show()
```

### Step 6: ボラティリティの予測

```python
# 将来のボラティリティを予測
forecast = result.forecast(horizon=30)

# 予測された分散
forecast_variance = forecast.variance.values[-1, :]
forecast_volatility = np.sqrt(forecast_variance)

# 予測期間の日付を生成
last_date = returns.index[-1]
forecast_dates = pd.date_range(start=last_date, periods=31, freq='B')[1:]

# プロット
fig, ax = plt.subplots(figsize=(12, 6))

# 過去のボラティリティ
ax.plot(returns.index[-60:], conditional_volatility[-60:], 
       label='Historical Volatility', color='blue')

# 予測ボラティリティ
ax.plot(forecast_dates, forecast_volatility, 
       label='Forecasted Volatility', color='red', linestyle='--')

# 信頼区間（仮に±2標準偏差）
ax.fill_between(forecast_dates, 
               forecast_volatility * 0.8, 
               forecast_volatility * 1.2,
               alpha=0.2, color='red', label='Confidence Interval')

ax.set_ylabel('Volatility (%)')
ax.set_xlabel('Date')
ax.set_title('Volatility Forecast (Next 30 Days)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('volatility_forecast.png', dpi=150)
plt.show()

print(f"\n=== 30日先のボラティリティ予測 ===")
print(f"現在のボラティリティ: {conditional_volatility.iloc[-1]:.2f}%")
print(f"30日後の予測: {forecast_volatility[-1]:.2f}%")
```

## モデルの診断

### 残差の検定

```python
# 標準化残差
std_residuals = result.resid / conditional_volatility

# 残差の自己相関を検定
from statsmodels.stats.diagnostic import acorr_ljungbox

ljung_box = acorr_ljungbox(std_residuals**2, lags=10, return_df=True)
print("\n=== 残差のLjung-Box検定（ボラティリティの残差）===")
print(ljung_box)

# p値が0.05以上なら、残差に自己相関なし（モデルは適切）
```

### 他のモデルとの比較

```python
# EGARCHモデル（非対称性を考慮）
egarch_model = arch_model(returns, vol='EGarch', p=1, q=1)
egarch_result = egarch_model.fit(disp='off')

# モデル比較
print("\n=== モデル比較 ===")
print(f"GARCH(1,1) AIC: {result.aic:.2f}")
print(f"EGARCH(1,1) AIC: {egarch_result.aic:.2f}")

if result.aic < egarch_result.aic:
    print("GARCH(1,1)がより良いフィット")
else:
    print("EGARCH(1,1)がより良いフィット（レバレッジ効果あり）")
```

## よくあるエラーと解決法

### エラー1: "ConvergenceWarning"

**原因:** モデルが収束しない

**解決法:**
```python
# 初期値を変更して再試行
result = model.fit(update_freq=5, starting_values=None)
```

### エラー2: データにNaNがある

**解決法:**
```python
returns = returns.dropna()
```

## まとめ

この記事では、GARCHモデルを使ったボラティリティ予測を学びました。

**キーポイント:**
1. GARCHモデルはボラティリティのクラスタリングを捉えられる
2. GARCH(1,1)はパラメータが少なく、実務で広く使われる
3. α+βが高いほどショックの持続性が高い
4. 予測は短期的なものに限定すべき

**応用例:**
- オプション価格の計算（インプライド・ボラティリティの代替）
- VaR（Value at Risk）の計算
- ポジションサイジングの決定

---

**関連記事:**
- [ポートフォリオのリターンとリスクをPythonで計算](/posts/portfolio-risk-return/)
- [モンテカルロ法で資産配分シミュレーション](/posts/monte-carlo-simulation/)

**参考リンク:**
- [archライブラリドキュメント](https://arch.readthedocs.io/)
- [GARCHモデル - Wikipedia](https://en.wikipedia.org/wiki/GARCH)
