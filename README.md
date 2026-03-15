# go9x9-joseki

KataGo を用いた9路盤定石の網羅的探索ツール。

## 概要

9路盤のゲームツリーを KataGo AI で系統的に評価し、序盤定石を網羅的に収集・データベース化するプロジェクト。

## 必要環境

- Python 3.10+
- KataGo（submodule、要ビルド）
- CUDA 対応 GPU（推奨）または CPU

## セットアップ

```bash
# リポジトリのクローン（submodule含む）
git clone --recurse-submodules <this-repo>
cd go9x9-joseki

# KataGo のビルド
cd katago/cpp
cmake . -DUSE_BACKEND=CUDA   # CPU のみの場合: -DUSE_BACKEND=EIGEN
make -j4
cd ../..

# モデルのダウンロード
# https://katagotraining.org/ から適切なモデルを取得
mkdir -p data/models
cp <downloaded-model>.bin.gz data/models/
```

## 使い方

```bash
# 探索の実行（実装後）
python -m src.explorer \
  --model data/models/<model>.bin.gz \
  --depth 20 \
  --output output/joseki.db
```

## ライセンス

- このプロジェクトのコード: MIT License
- KataGo: MIT License（`katago/LICENSE` 参照）
