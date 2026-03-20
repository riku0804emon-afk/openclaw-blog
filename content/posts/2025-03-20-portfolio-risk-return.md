---
title: "ポートフォリオのリターンとリスクをPythonで計算する"
date: 2025-03-20T22:32:00+09:00
draft: true
categories:
  - portfolio
tags:
  - Python
  - ポートフォリオ理論
  - リスク
  - リターン
  - 分散投資
description: "複数銘柄のポートフォリオのリターンとリスク（標準偏差）をPythonで計算。相関係数と共分散行列を使った現代的ポートフォリオ理論の基礎。"
math: true
code: true
---

## はじめに

「分散投資をするとリスクが減る」とはよく聞く言葉ですが、具体的にどう計算するのでしょうか？

この記事では、**複数銘柄からなるポートフォリオ**のリターンとリスクを、**現代的ポートフォリオ理論（MPT）**に基づいてPythonで計算します。

## ポートフォリオの基礎

### リターンの計算

ポートフォリオ全体のリターンは、各銘柄のリターンを**加重平均**します：

$$R_p = \sum_{i=1}^{n} w_i R_i$$

ここで：
- $R_p$ = ポートフォリオのリターン
- $w_i$ = 銘柄$i$のウェイト（投資比率）
- $R_i$ = 銘柄$i$のリターン
- $n$ = 銘柄数

### リスク（標準偏差）の計算

ポートフォリオのリスクは、単なる加重平均ではなく、**共分散行列**を使います：

$$\sigma_p = \sqrt{\mathbf{w}^T \Sigma \mathbf{w}}$$

ここで：
- $\sigma_p$ = ポートフォリオの標準偏差（リスク）
- $\mathbf{w}$ = ウェイトベクトル
- $\Sigma$ = 共分散行列
- $\mathbf{w}^T$ = ウェイトベクトルの転置

**分散**（バリアンス）は：
$$\sigma_p^2 = \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_{ij}$$

ここで$\sigma_{ij}$は銘柄$i$と銘柄$j$の共分散です。

## Pythonでの実装

### Step 1: データ取得

```python
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 分析対象銘柄（S&P500の主要銘柄）
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# 2年分のデータを取得
data = yf.download(tickers, period='2y')['Close']

print(data.head())
print(f"\n銘柄数: {len(tickers)}")
print(f"データ期間: {len(data)}日")
```

### Step 2: 日次リターンの計算

```python
# 日次リターンを計算（対数リターン）
returns = np.log(data / data.shift(1)).dropna()

# または単純リターン
# returns = data.pct_change().dropna()

print("日次リターンの統計:")
print(returns.describe())
```

### Step 3: 年率換算リターンの計算

```python
# 平均日次リターン
mean_returns = returns.mean()

# 年率換算（252取引日）
annual_returns = mean_returns * 252

print("年率換算リターン:")
for ticker, ret in annual_returns.items():
    print(f"  {ticker}: {ret*100:.2f}%")
```

### Step 4: 共分散行列の計算

```python
# 日次リターンの共分散行列
cov_matrix = returns.cov()

# 年率換算共分散行列（×252）
annual_cov_matrix = cov_matrix * 252

print("共分散行列（年率換算）:")
print(annual_cov_matrix.round(4))
```

### Step 5: 相関行列

```python
# 相関行列（標準化された共分散）
corr_matrix = returns.corr()

print("相関行列:")
print(corr_matrix.round(2))

# ヒートマップで可視化
import seaborn as sns

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
            square=True, fmt='.2f')
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=150)
plt.show()
```

### Step 6: ポートフォリオのリターンとリスク計算

```python
# 等ウェイトポートフォリオ（各銘柄20%ずつ）
weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

# ポートフォリオの年率リターン
portfolio_return = np.dot(weights, annual_returns)

# ポートフォリオの年率分散
portfolio_variance = np.dot(weights.T, np.dot(annual_cov_matrix, weights))

# ポートフォリオの年率標準偏差（リスク）
portfolio_std = np.sqrt(portfolio_variance)

print(f"=== 等ウェイトポートフォリオ ===")
print(f"銘柄: {tickers}")
print(f"ウェイト: {weights}")
print(f"年率リターン: {portfolio_return*100:.2f}%")
print(f"年率リスク（標準偏差）: {portfolio_std*100:.2f}%")
print(f"シャープレシオ（仮定無リスク金利2%）: {(portfolio_return - 0.02) / portfolio_std:.2f}")
```

## 効果的フロンティアの計算

### 様々なウェイト組み合わせを試す

```python
def portfolio_performance(weights, returns, cov_matrix):
    """
    ポートフォリオのパフォーマンスを計算
    """
    portfolio_return = np.dot(weights, returns)
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_std

def random_portfolios(num_portfolios, returns, cov_matrix):
    """
    ランダムなポートフォリオを生成
    """
    results = np.zeros((3, num_portfolios))
    weights_record = []
    
    for i in range(num_portfolios):
        # ランダムなウェイト（合計1）
        weights = np.random.random(len(returns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        # パフォーマンス計算
        portfolio_return, portfolio_std = portfolio_performance(weights, returns, cov_matrix)
        
        # シャープレシオ（無リスク金利2%と仮定）
        sharpe = (portfolio_return - 0.02) / portfolio_std
        
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std
        results[2,i] = sharpe
    
    return results, weights_record

# 10,000個のランダムポートフォリオを生成
num_portfolios = 10000
results, weights_record = random_portfolios(num_portfolios, annual_returns, annual_cov_matrix)

print(f"{num_portfolios}個のポートフォリオを生成しました")
```

### 効果的フロンティアの可視化

```python
# マックスシャープレシオポートフォリオ
max_sharpe_idx = np.argmax(results[2])
max_sharpe_return = results[0, max_sharpe_idx]
max_sharpe_std = results[1, max_sharpe_idx]
max_sharpe_weights = weights_record[max_sharpe_idx]

# 最小リスクポートフォリオ
min_risk_idx = np.argmin(results[1])
min_risk_return = results[0, min_risk_idx]
min_risk_std = results[1, min_risk_idx]
min_risk_weights = weights_record[min_risk_idx]

# プロット
plt.figure(figsize=(12, 8))

# 全ポートフォリオ
scatter = plt.scatter(results[1], results[0], c=results[2], cmap='viridis', alpha=0.5)
plt.colorbar(scatter, label='Sharpe Ratio')

# マックスシャープレシオ
plt.scatter(max_sharpe_std, max_sharpe_return, c='red', marker='*', s=300, 
           label=f'Max Sharpe: {results[2, max_sharpe_idx]:.2f}')

# 最小リスク
plt.scatter(min_risk_std, min_risk_return, c='blue', marker='*', s=300, 
           label=f'Min Risk: {results[1, min_risk_idx]*100:.1f}%')

# 個別銘柄
for i, ticker in enumerate(tickers):
    plt.scatter(np.sqrt(annual_cov_matrix.iloc[i,i]), annual_returns.iloc[i], 
               c='black', marker='o', s=100)
    plt.annotate(ticker, (np.sqrt(annual_cov_matrix.iloc[i,i]), annual_returns.iloc[i]),
                xytext=(5, 5), textcoords='offset points')

plt.xlabel('Risk (Standard Deviation)')
plt.ylabel('Expected Return')
plt.title('Efficient Frontier')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('efficient_frontier.png', dpi=150)
plt.show()

print("\n=== マックスシャープレシオポートフォリオ ===")
for ticker, weight in zip(tickers, max_sharpe_weights):
    print(f"  {ticker}: {weight*100:.1f}%")
print(f"年率リターン: {max_sharpe_return*100:.2f}%")
print(f"年率リスク: {max_sharpe_std*100:.2f}%")

print("\n=== 最小リスクポートフォリオ ===")
for ticker, weight in zip(tickers, min_risk_weights):
    print(f"  {ticker}: {weight*100:.1f}%")
print(f"年率リターン: {min_risk_return*100:.2f}%")
print(f"年率リスク: {min_risk_std*100:.2f}%")
```

## 分散投資の効果

### 等ウェイト vs 個別銘柄

```python
print("=== 個別銘柄のリスク vs 等ウェイトポートフォリオ ===\n")

# 個別銘柄のリスク
individual_risks = np.sqrt(np.diag(annual_cov_matrix))

for ticker, risk in zip(tickers, individual_risks):
    print(f"{ticker}: {risk*100:.2f}%")

print(f"\n等ウェイトポートフォリオのリスク: {portfolio_std*100:.2f}%")
print(f"\n平均的な個別銘柄のリスク: {individual_risks.mean()*100:.2f}%")
print(f"リスク低減効果: {(1 - portfolio_std/individual_risks.mean())*100:.1f}%")
```

## まとめ

この記事では、ポートフォリオのリターンとリスク計算を学びました。

**キーポイント:**
1. ポートフォリオリターン = 加重平均
2. ポートフォリオリスク = $\sqrt{\mathbf{w}^T \Sigma \mathbf{w}}$
3. 分散効果があるため、ポートフォリオのリスク < 個別銘柄の平均リスク
4. 効果的フロンティア上で最適な組み合わせを探せる

**次のステップ:**
- シャープレシオ最大化を数学的最適化で解く
- ブラック・リターマンモデルを応用する
- 実際の資産配分に応用する

---

**関連記事:**
- [シャープレシオを最大化するポートフォリオ最適化](/posts/sharpe-optimization/)
- [モンテカルロ法で資産配分シミュレーション](/posts/monte-carlo-simulation/)

**参考リンク:**
- [Modern Portfolio Theory - Wikipedia](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [PyPortfolioOptドキュメント](https://pyportfolioopt.readthedocs.io/)
