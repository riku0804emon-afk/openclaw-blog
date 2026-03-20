---
title: "モンテカルロ法で資産配分シミュレーション"
date: 2025-03-20T22:34:00+09:00
draft: true
categories:
  - portfolio
tags:
  - Python
  - モンテカルロ法
  - シミュレーション
  - 資産配分
  - リスク管理
description: "モンテカルロ法を使って将来の資産推移を数万回シミュレーション。リタイアメント資産の確率分布と目標達成確率を可視化します。"
math: true
code: true
---

## はじめに

「投資でどれくらいの資産を築けるだろう？」

将来の資産推移を知りたい時、**モンテカルロ法**は強力なツールです。

数万回のシミュレーションを通じて、**資産が目標に達する確率**や**破産リスク**を定量的に評価できます。

この記事では、モンテカルロ法を使った資産配分シミュレーションをPythonで実装します。

## モンテカルロ法とは？

モンテカルロ法は、**乱数を使って不確実性を含む問題をシミュレーションする手法**です。

### 投資への応用

1. **期待リターンとボラティリティ**から、将来の資産価値の分布を推定
2. **数千〜数万回**の試行を行い、統計的な確率を計算
3. **様々なシナリオ**（好景気、不景気など）を考慮

### シミュレーションのステップ

1. パラメータ設定（初期資産、年間リターン、ボラティリティ、期間）
2. 乱数生成（正規分布に基づく年間リターン）
3. 複利計算で資産推移を計算
4. 複数回繰り返し
5. 結果の分析

## Pythonでの実装

### Step 1: 基本シミュレーション

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# パラメータ設定
initial_investment = 1000000  # 初期投資額（100万円）
annual_return = 0.07          # 期待年率リターン（7%）
annual_volatility = 0.15      # 年率ボラティリティ（15%）
years = 30                    # 投資期間（30年）
num_simulations = 10000       # シミュレーション回数

# 乱数シード設定（再現性のため）
np.random.seed(42)

# シミュレーション結果を保存する配列
simulations = np.zeros((years + 1, num_simulations))
simulations[0] = initial_investment

# モンテカルロシミュレーション
for i in range(num_simulations):
    for year in range(1, years + 1):
        # 正規分布に基づくランダムなリターン
        random_return = np.random.normal(annual_return, annual_volatility)
        # 資産を更新
        simulations[year, i] = simulations[year - 1, i] * (1 + random_return)

print(f"シミュレーション完了: {num_simulations}回")
print(f"初期資産: ¥{initial_investment:,.0f}")
```

### Step 2: 結果の可視化

```python
# 年次のインデックス
year_index = range(years + 1)

# プロット
plt.figure(figsize=(12, 7))

# すべてのシミュレーションを薄く表示
for i in range(min(100, num_simulations)):
    plt.plot(year_index, simulations[:, i], alpha=0.1, color='gray')

# パーセンタイルを計算
percentiles = [5, 25, 50, 75, 95]
percentile_values = np.percentile(simulations, percentiles, axis=1)

# パーセンタイルをプロット
colors = ['red', 'orange', 'green', 'orange', 'red']
labels = ['5th percentile', '25th percentile', 'Median', '75th percentile', '95th percentile']

for i, (p, color, label) in enumerate(zip(percentile_values, colors, labels)):
    plt.plot(year_index, p, color=color, linewidth=2, label=label)

plt.xlabel('Years')
plt.ylabel('Portfolio Value (JPY)')
plt.title(f'Monte Carlo Simulation: {num_simulations} Paths\n(Return: {annual_return*100:.0f}%, Volatility: {annual_volatility*100:.0f}%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.yscale('log')  # 対数スケール

plt.tight_layout()
plt.savefig('monte_carlo_simulation.png', dpi=150)
plt.show()
```

### Step 3: 最終資産の分布分析

```python
# 最終資産
final_values = simulations[-1, :]

# 統計量
print("=== 最終資産の統計 ===")
print(f"平均値: ¥{final_values.mean():,.0f}")
print(f"中央値: ¥{np.median(final_values):,.0f}")
print(f"標準偏差: ¥{final_values.std():,.0f}")
print(f"最小値: ¥{final_values.min():,.0f}")
print(f"最大値: ¥{final_values.max():,.0f}")

# パーセンタイル
for p in [5, 10, 25, 50, 75, 90, 95]:
    value = np.percentile(final_values, p)
    print(f"{p}th percentile: ¥{value:,.0f}")
```

### Step 4: ヒストグラム

```python
plt.figure(figsize=(12, 6))

plt.hist(final_values, bins=100, edgecolor='black', alpha=0.7)
plt.axvline(final_values.mean(), color='red', linestyle='--', 
           linewidth=2, label=f'Mean: ¥{final_values.mean():,.0f}')
plt.axvline(np.median(final_values), color='green', linestyle='--', 
           linewidth=2, label=f'Median: ¥{np.median(final_values):,.0f}')

plt.xlabel('Final Portfolio Value (JPY)')
plt.ylabel('Frequency')
plt.title(f'Distribution of Final Portfolio Values\n({num_simulations} Simulations)')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('final_value_distribution.png', dpi=150)
plt.show()
```

### Step 5: 目標達成確率

```python
# 目標資産
target = 10000000  # 1000万円

# 目標達成確率
probability_of_success = np.mean(final_values >= target) * 100

print(f"\n=== 目標達成確率 ===")
print(f"目標資産: ¥{target:,.0f}")
print(f"達成確率: {probability_of_success:.1f}%")

# 損失確率（元本割れ）
loss_probability = np.mean(final_values < initial_investment) * 100
print(f"元本割れ確率: {loss_probability:.1f}%")
```

## 積立投資のシミュレーション

実際には、定期的に追加投資（積立）を行うことが多いです。

```python
def simulate_with_contributions(
    initial_investment,
    annual_contribution,
    annual_return,
    annual_volatility,
    years,
    num_simulations
):
    """
    積立投資のモンテカルロシミュレーション
    """
    np.random.seed(42)
    simulations = np.zeros((years + 1, num_simulations))
    simulations[0] = initial_investment
    
    for i in range(num_simulations):
        for year in range(1, years + 1):
            random_return = np.random.normal(annual_return, annual_volatility)
            # 前年の資産×リターン + 新規積立
            simulations[year, i] = simulations[year - 1, i] * (1 + random_return) + annual_contribution
    
    return simulations

# 積立シミュレーション
simulations_contrib = simulate_with_contributions(
    initial_investment=1000000,   # 初期100万円
    annual_contribution=600000,   # 年間60万円（月5万円）
    annual_return=0.07,
    annual_volatility=0.15,
    years=30,
    num_simulations=10000
)

# 結果分析
final_values_contrib = simulations_contrib[-1, :]
print("\n=== 積立投資の結果 ===")
print(f"初期投資: ¥1,000,000")
print(f"年間積立: ¥600,000")
print(f"30年後の平均資産: ¥{final_values_contrib.mean():,.0f}")
print(f"30年後の中央値: ¥{np.median(final_values_contrib):,.0f}")
```

## 資産配分の比較

異なるリスク・リターン特性のポートフォリオを比較します。

```python
# シナリオ設定
scenarios = {
    'Conservative': {'return': 0.04, 'volatility': 0.08},
    'Moderate': {'return': 0.06, 'volatility': 0.12},
    'Aggressive': {'return': 0.08, 'volatility': 0.20},
}

results = {}

for name, params in scenarios.items():
    sims = simulate_with_contributions(
        initial_investment=1000000,
        annual_contribution=600000,
        annual_return=params['return'],
        annual_volatility=params['volatility'],
        years=30,
        num_simulations=5000
    )
    results[name] = sims[-1, :]

# 比較表
print("\n=== 資産配分シナリオ比較 ===")
print(f"{'Scenario':<15} {'Expected Return':<18} {'Avg Final Value':<20} {'Median':<20} {'Success Prob':<15}")
print("-" * 85)

for name, params in scenarios.items():
    final_vals = results[name]
    success_prob = np.mean(final_vals >= 50000000) * 100  # 5000万円達成確率
    print(f"{name:<15} {params['return']*100:>5.0f}% ({params['volatility']*100:.0f}% vol)   "
          f"¥{final_vals.mean():>14,.0f}  ¥{np.median(final_vals):>14,.0f}  {success_prob:>8.1f}%")
```

## まとめ

この記事では、モンテカルロ法を使った資産配分シミュレーションを学びました。

**キーポイント:**
1. モンテカルロ法は不確実性を含む将来予測に有効
2. パーセンタイル分析でリスクを定量化できる
3. 目標達成確率を計算できる
4. 異なる資産配分シナリオを比較できる

**注意点:**
- 過去のリターン・ボラティリティが未来を保証しない
- 極端な市場イベント（ブラックスワン）は予測困難
- 定期的にシミュレーションを更新すべき

---

**関連記事:**
- [ポートフォリオのリターンとリスクをPythonで計算](/posts/portfolio-risk-return/)
- [シャープレシオを最大化するポートフォリオ最適化](/posts/sharpe-optimization/)

**参考リンク:**
- [Monte Carlo Methods in Finance - Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_methods_in_finance)
