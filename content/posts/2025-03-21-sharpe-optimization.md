---
title: "シャープレシオを最大化するポートフォリオ最適化"
date: 2025-03-21T02:30:00+09:00
draft: false
categories:
  - portfolio
tags:
  - Python
  - シャープレシオ
  - ポートフォリオ最適化
  - scipy
  - 数理最適化
description: "scipy.optimizeを使って、シャープレシオを最大化するポートフォリオの資産配分を計算。効率的フロンティア上の最適解を求めます。"
math: true
code: true
---

## はじめに

前回はランダムなポートフォリオを生成して効率的フロンティアを描きました。

今回は**数理最適化**を使って、**シャープレシオを最大化する最適な資産配分**を計算します。

## シャープレシオとは？

シャープレシオは、**リスク調整後リターン**を表す指標です：

$$Sharpe = \frac{R_p - R_f}{\sigma_p}$$

ここで：
- $R_p$ = ポートフォリオの期待リターン
- $R_f$ = 無リスク金利
- $\sigma_p$ = ポートフォリオの標準偏差（リスク）

**目標**: シャープレシオを最大化するウェイト $w$ を求める

## 最適化の定式化

### 制約条件

1. **ウェイトの合計 = 1**: $\sum w_i = 1$
2. **各銘柄のウェイト ≥ 0**（空売りなし）: $w_i \geq 0$

### 最適化問題

$$\max_w \frac{R_p - R_f}{\sigma_p}$$

$$subject\ to: \sum w_i = 1, w_i \geq 0$$

## Pythonでの実装

### ライブラリ準備

```python
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# データ取得
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
data = yf.download(tickers, period='2y')['Close']

# 日次リターン
returns = np.log(data / data.shift(1)).dropna()

# 年率換算
annual_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252

# 無リスク金利（2%と仮定）
rf = 0.02

print("年率期待リターン:")
for ticker, ret in annual_returns.items():
    print(f"  {ticker}: {ret*100:.2f}%")
```

### ポートフォリオ計算関数

```python
def portfolio_performance(weights, returns, cov_matrix):
    """
    ポートフォリオのリターンとリスクを計算
    """
    portfolio_return = np.dot(weights, returns)
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_std

def negative_sharpe(weights, returns, cov_matrix, rf):
    """
    シャープレシオの負の値（最小化のため）
    """
    p_return, p_std = portfolio_performance(weights, returns, cov_matrix)
    return -(p_return - rf) / p_std
```

### 最適化の実行

```python
# 初期値（等ウェイト）
n_assets = len(tickers)
initial_weights = np.array([1/n_assets] * n_assets)

# 制約条件
constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # 合計=1

# 境界条件（0 <= w <= 1）
bounds = tuple((0, 1) for _ in range(n_assets))

# 最適化
result = minimize(
    negative_sharpe,
    initial_weights,
    args=(annual_returns, cov_matrix, rf),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints
)

# 結果の表示
optimal_weights = result.x
optimal_return, optimal_std = portfolio_performance(optimal_weights, annual_returns, cov_matrix)
optimal_sharpe = (optimal_return - rf) / optimal_std

print("\n=== 最適ポートフォリオ ===")
print("資産配分:")
for ticker, weight in zip(tickers, optimal_weights):
    if weight > 0.001:  # 0.1%以上を表示
        print(f"  {ticker}: {weight*100:.2f}%")

print(f"\n期待リターン: {optimal_return*100:.2f}%")
print(f"リスク（標準偏差）: {optimal_std*100:.2f}%")
print(f"シャープレシオ: {optimal_sharpe:.4f}")
```

## 効率的フロンティアとの比較

```python
# ランダムポートフォリオを生成
def random_portfolios(num_portfolios, returns, cov_matrix, rf):
    results = np.zeros((3, num_portfolios))
    weights_record = []
    
    for i in range(num_portfolios):
        weights = np.random.random(len(returns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        p_return, p_std = portfolio_performance(weights, returns, cov_matrix)
        sharpe = (p_return - rf) / p_std
        
        results[0,i] = p_return
        results[1,i] = p_std
        results[2,i] = sharpe
    
    return results, weights_record

# 生成
results, _ = random_portfolios(10000, annual_returns, cov_matrix, rf)

# プロット
plt.figure(figsize=(12, 8))

# ランダムポートフォリオ
scatter = plt.scatter(results[1], results[0], c=results[2], cmap='viridis', alpha=0.5)
plt.colorbar(scatter, label='Sharpe Ratio')

# 最適ポートフォリオ（赤い星）
plt.scatter(optimal_std, optimal_return, c='red', marker='*', s=500, 
           label=f'Optimal (Sharpe: {optimal_sharpe:.2f})', zorder=5)

# 個別銘柄
for i, ticker in enumerate(tickers):
    std = np.sqrt(cov_matrix.iloc[i,i])
    ret = annual_returns.iloc[i]
    plt.scatter(std, ret, c='black', marker='o', s=100)
    plt.annotate(ticker, (std, ret), xytext=(5, 5), textcoords='offset points')

# 資本市場線（CML）
x_cml = np.linspace(0, max(results[1]) * 1.2, 100)
y_cml = rf + optimal_sharpe * x_cml
plt.plot(x_cml, y_cml, 'r--', alpha=0.5, label='Capital Market Line')

plt.xlabel('Risk (Standard Deviation)')
plt.ylabel('Expected Return')
plt.title('Efficient Frontier with Optimal Portfolio')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('optimal_portfolio.png', dpi=150)
plt.show()
```

## 最小リスクポートフォリオ

```python
def portfolio_variance(weights, cov_matrix):
    """ポートフォリオの分散を計算"""
    return np.dot(weights.T, np.dot(cov_matrix, weights))

# 最小分散ポートフォリオを計算
result_minvar = minimize(
    portfolio_variance,
    initial_weights,
    args=(cov_matrix,),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints
)

minvar_weights = result_minvar.x
minvar_return, minvar_std = portfolio_performance(minvar_weights, annual_returns, cov_matrix)

print("\n=== 最小リスクポートフォリオ ===")
for ticker, weight in zip(tickers, minvar_weights):
    if weight > 0.001:
        print(f"  {ticker}: {weight*100:.2f}%")
print(f"リターン: {minvar_return*100:.2f}%")
print(f"リスク: {minvar_std*100:.2f}%")
```

## 目標リターンに対する最適ポートフォリオ

```python
def minimize_risk_for_target_return(target_return, returns, cov_matrix):
    """
    目標リターンを達成する最小リスクポートフォリオ
    """
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: np.dot(x, returns) - target_return}
    ]
    
    result = minimize(
        portfolio_variance,
        initial_weights,
        args=(cov_matrix,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    return result.x

# 目標リターンに対する最適ポートフォリオを計算
target_returns = np.linspace(minvar_return, max(annual_returns), 50)
efficient_portfolios = []

for target in target_returns:
    try:
        w = minimize_risk_for_target_return(target, annual_returns, cov_matrix)
        ret, std = portfolio_performance(w, annual_returns, cov_matrix)
        efficient_portfolios.append((std, ret))
    except:
        pass

# 効率的フロンティアをプロット
eff_df = pd.DataFrame(efficient_portfolios, columns=['Risk', 'Return'])
plt.plot(eff_df['Risk'], eff_df['Return'], 'b-', linewidth=2, label='Efficient Frontier')
plt.scatter(optimal_std, optimal_return, c='red', marker='*', s=300, label='Max Sharpe', zorder=5)
plt.scatter(minvar_std, minvar_return, c='green', marker='*', s=300, label='Min Variance', zorder=5)
plt.legend()
plt.show()
```

## まとめ

**最適化のポイント:**
1. **SLSQP**アルゴリズムで制約付き最適化
2. **シャープレシオ最大化**でリスク調整後リターン最適化
3. **効率的フロンティア**上で最適解を選択

**次のステップ:**
- ブラック・リターマンモデルの実装
- 実際の資産配分への適用

---

**関連記事:**
- [ポートフォリオのリターンとリスクをPythonで計算](/posts/portfolio-risk-return/)
- [モンテカルロ法で資産配分シミュレーション](/posts/monte-carlo-simulation/)
