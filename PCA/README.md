# Anime Audience Analysis using PCA, Random Forest, and Principal Component Regression

## 概要

本プログラムは、アニメ作品の視聴者属性データを対象として、多変量解析を用いて視聴傾向を分析するためのPythonコードです。

以下の分析を実施します。

* 主成分分析（PCA）
* 因子負荷量の算出・可視化
* Random Forestによる特徴量重要度分析
* K-meansクラスタリング
* 主成分回帰（Principal Component Regression：PCR）
* 残差分析

---

# データ

入力データは `Data/AnimeData.csv` を使用します。

## 必要な列

| 列名  | 内容       |
| --- | -------- |
| F1  | 女性10〜20代 |
| F2  | 女性30〜40代 |
| F3  | 女性50代以上  |
| M1  | 男性10〜20代 |
| M2  | 男性30〜40代 |
| M3  | 男性50代以上  |
| T   | ティーン     |
| ALL | 全体視聴率    |

※各行が1作品を表します。

---

# 使用ライブラリ

* pandas
* numpy
* matplotlib
* seaborn
* scikit-learn
* statsmodels

インストール例

```bash
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels
```

---

# 実行内容

## 1. データ読み込み

CSVファイルを読み込み、作品に連番IDを付与します。

---

## 2. 主成分分析（PCA）

対象変数

* F1
* F2
* F3
* M1
* M2
* M3
* T

標準化後にPCAを実施し、

* 第1主成分
* 第2主成分

を算出します。

表示内容

* 寄与率
* 累積寄与率
* 因子負荷量
* PCAマップ

---

## 3. 因子負荷量

各視聴者層が各主成分へどの程度寄与しているかを算出します。

ヒートマップで可視化します。

---

## 4. Random Forest

目的変数

```
ALL
```

説明変数

```
F1
F2
F3
M1
M2
M3
T
```

各属性が全体視聴率にどれだけ寄与しているかを特徴量重要度として表示します。

---

## 5. K-meansクラスタリング

PCAで得られた2次元座標を用いて、

```
クラスタ数 = 3
```

で作品を分類します。

視聴者タイプの近い作品を可視化します。

---

## 6. 主成分回帰（PCR）

PCAで得られた

* PC1
* PC2

を説明変数として、

```
ALL
```

を予測します。

statsmodelsを用いることで以下を出力します。

* 回帰係数
* p値
* R²
* Adjusted R²
* 回帰式
* OLS Summary

さらに、

* 実測値
* 予測値

の散布図を表示します。

---

## 7. 残差分析

残差

```
Residual = Actual - Predicted
```

を計算し、

### 上振れ作品

モデル予測を上回った作品

TOP5

### 下振れ作品

モデル予測を下回った作品

TOP5

を表示します。

さらに全作品について残差を棒グラフで可視化します。

---

# 出力される図

プログラム実行時に以下の図が表示されます。

1. 因子負荷量ヒートマップ
2. PCAマップ
3. Random Forest特徴量重要度
4. K-meansクラスタ
5. PCR予測結果（Actual vs Predicted）
6. 残差グラフ

---

# 想定される分析用途

本プログラムは以下のような分析を目的としています。

* 視聴者層の特徴把握
* アニメ作品のポジショニング分析
* 世代・性別ごとの視聴傾向の可視化
* 全体視聴率への寄与要因分析
* 作品の過大・過小評価の検出
* コンテンツ編成・マーケティング分析の基礎資料

---

# ファイル構成

```
project/
│
├── Data/
│   └── AnimeData.csv
│
├── analysis.py
│
└── README.md
```

---

# 実行方法

```bash
python analysis.py
```

実行後、統計結果がコンソールへ出力され、各分析結果のグラフが順番に表示されます。
