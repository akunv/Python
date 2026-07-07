import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import io
import matplotlib
import statsmodels.api as sm

# ==========================================
# 1. データの読み込みと加工
# ==========================================

df = pd.read_csv("Data/AnimeData.csv")

# --- titileに番号を割り当てる ---
df['title'] = range(1, len(df) + 1)  # 1, 2, 3... と番号を振る

# ==========================================
# 2. 主成分分析 (PCA)
# ==========================================
features_pca = ['F1', 'F2', 'F3', 'M1', 'M2', 'M3', 'T']
X_pca = df[features_pca]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_pca)

pca = PCA(n_components=2)
pca_coords = pca.fit_transform(X_scaled)

# --- 【追加】寄与率・累積寄与率の表示 ---
var_ratio = pca.explained_variance_ratio_
cum_var_ratio = np.cumsum(var_ratio)

print("--- 寄与率 (各軸が説明する情報の割合) ---")
for i, ratio in enumerate(var_ratio, 1):
    print(f"PC{i}: {ratio:.4f} ({ratio:.2%})")

print("\n--- 累積寄与率 (どれだけ情報を要約できたか) ---")
print(f"PC2までで全体の {cum_var_ratio[1]:.2%} の情報を説明できています。")

# --- 【追加】因子負荷量の計算 (変数と主成分の相関) ---
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
loadings_df = pd.DataFrame(loadings, index=features_pca, columns=['PC1', 'PC2'])

print("\n--- 因子負荷量 (数値が高いほどその軸への影響が強い) ---")
print(loadings_df)

# 可視化: 因子負荷量のヒートマップ
plt.figure(figsize=(8, 6))
sns.heatmap(loadings_df, annot=True, cmap='RdBu_r', center=0)
plt.title('Factor loading (Correlation between variables and PCs)') #因子負荷量
plt.show()

plt.figure(figsize=(16, 12))
plt.scatter(pca_coords[:, 0], pca_coords[:, 1], alpha=0.6, c='royalblue', edgecolors='white')

# 全ての点に番号を表示
for i in range(len(df)):
    plt.annotate(str(df['title'].iloc[i]), (pca_coords[i, 0], pca_coords[i, 1]),
                  fontsize=8, fontweight='bold')

plt.title('PCA: Anime Mapping (Numbers 1-67)')
plt.xlabel(f'PC1 How widely known anime works are among a wide range of generations ({pca.explained_variance_ratio_[0]:.1%} variance)')
plt.ylabel(f'PC2 Male or Female / Younger ({pca.explained_variance_ratio_[1]:.1%} variance)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# ==========================================
# 3. 特徴量の重要度 (Random Forest)
# ==========================================
X = df[features_pca]
y = df['ALL']

# 学習
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X, y)

importances = pd.Series(rf.feature_importances_, index=features_pca).sort_values()
plt.figure(figsize=(8, 5))
importances.plot(kind='barh', color='salmon')
plt.title('Which Demographic Dominates "ALL" Rate?')
plt.xlabel('Feature Importance')
plt.show()

# 番号と元の作品名の対応表をプリント（確認用）
print("--- Title Number Mapping ---")
original_names = df['title'].tolist()
for i, name in enumerate(original_names, 1):    
    print(f"{i}: {name}")

from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=0)
clusters = kmeans.fit_predict(pca_coords)

plt.scatter(pca_coords[:,0], pca_coords[:,1], c=clusters, cmap='Set1')
plt.title("Audience-Type Clusters")
plt.show()

from sklearn.linear_model import LinearRegression

# ==========================================
# 4. 主成分回帰 (PCR: PC1, PC2 -> ALL)
# ==========================================

# 説明変数にPC1とPC2をセット
X_pcr = pca_coords
y_pcr = df['ALL']

# 切片(const)の追加
X_pcr_with_const = sm.add_constant(X_pcr)

# 統計モデルの学習
model_sm = sm.OLS(y_pcr, X_pcr_with_const).fit()

# 詳細レポートの表示
print("\n" + "="*50)
print("   主成分回帰 (PCR) 統計詳細レポート")
print("="*50)
print(model_sm.summary())

# --- 警告が出ない「.iloc」を使った書き方に修正 ---
print("\n--- 統計指標の要約 ---")
print(f"決定係数 (R2): {model_sm.rsquared:.4f}")
print(f"自由度調整済み決定係数 (Adj-R2): {model_sm.rsquared_adj:.4f}")

# 位置（iloc）を指定してp値を取得
print(f"PC1のp値: {model_sm.pvalues.iloc[1]:.4e}")
print(f"PC2のp値: {model_sm.pvalues.iloc[2]:.4e}")

# 予測式の係数を取得
coeffs = model_sm.params
print(f"\n予測式: ALL = {coeffs.iloc[1]:.4f}*PC1 + {coeffs.iloc[2]:.4f}*PC2 + {coeffs.iloc[0]:.4f}")

# 予測値の計算
y_pred_pcr = model_sm.predict(X_pcr_with_const)

# プロット表示
plt.figure(figsize=(8, 6))
plt.scatter(y_pcr, y_pred_pcr, alpha=0.6, color='royalblue')
plt.plot([y_pcr.min(), y_pcr.max()], [y_pcr.min(), y_pcr.max()], 'r--', lw=2)
plt.xlabel('Actual ALL Rate')
plt.ylabel('Predicted ALL Rate (PCR)')
plt.title(f'PCR Prediction: Actual vs Predicted (Adj-R2: {model_sm.rsquared_adj:.4f})')
plt.grid(True)
plt.show()

# ==========================================
# 5. 残差分析 (Residual Analysis)
# ==========================================

# 予測値と残差をデータフレームに追加
# 残差 = 実績(ALL) - 予測(Predicted_ALL)
df['Predicted_ALL'] = y_pred_pcr
df['Residual'] = df['ALL'] - df['Predicted_ALL']

# 残差の大きい順（実績が予測を上回った順）に並び替え
residual_ranking = df.sort_values(by='Residual', ascending=False)

print("\n--- 【上振れ】残差ランキング TOP 5（モデルの予測を超えて数字を稼いだ作品） ---")
# 前のセクションでdf['title']が番号になっているので、番号で表示されます
print(residual_ranking[['title', 'ALL', 'Predicted_ALL', 'Residual']].head(5).to_string(index=False))

print("\n--- 【下振れ】残差ランキング TOP 5（ポテンシャルの割に数字が伸び悩んだ作品） ---")
print(residual_ranking[['title', 'ALL', 'Predicted_ALL', 'Residual']].tail(5).to_string(index=False))

# --- 残差の可視化（棒グラフ） ---
plt.figure(figsize=(15, 6))
# プラスの残差は「赤」、マイナスの残差は「青」で色分け
colors = ['red' if x > 0 else 'blue' for x in df['Residual']]

plt.bar(df['title'].astype(str), df['Residual'], color=colors, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1) # 予測ぴったりの基準線

plt.title('Residual Analysis: Deviations from the Model (Actual - Predicted)')
plt.xlabel('Anime Title ID')
plt.ylabel('Residual (Difference from Prediction)')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()