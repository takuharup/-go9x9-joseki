# go9x9-joseki

KataGo を用いた9路盤定石の網羅的探索ツール。

## 概要

9路盤のゲームツリーを KataGo AI で系統的に評価し、序盤定石を網羅的に収集・データベース化するプロジェクト。

---

## 必要環境

- Python 3.10+
- CMake 3.12+
- C++17 対応コンパイラ（GCC 7+ / Clang 5+ / MSVC 2017+）
- KataGo バックエンドいずれか:
  - **CUDA** （推奨）: CUDA 10.2+ + cuDNN 7.6+
  - **OpenCL**: OpenCL 1.2+ 対応 GPU
  - **Eigen**: CPU のみ、GPU 不要（最も遅い）

---

## セットアップ

### 1. リポジトリの取得

```bash
git clone --recurse-submodules <this-repo>
cd go9x9-joseki
```

submodule をあとから初期化する場合:

```bash
git submodule update --init --recursive
```

---

### 2. KataGo のビルド

`katago/cpp/` に CMakeLists.txt がある。ビルドディレクトリは `katago/cpp/` 内で行うのが推奨。

#### CUDA バックエンド（GPU 推奨）

```bash
cd katago/cpp
cmake . -DUSE_BACKEND=CUDA
make -j$(nproc)
```

cuDNN のパスが通っていない場合:

```bash
cmake . -DUSE_BACKEND=CUDA \
        -DCUDNN_INCLUDE_DIR=/usr/local/cuda/include \
        -DCUDNN_LIBRARY=/usr/local/cuda/lib64/libcudnn.so
make -j$(nproc)
```

#### OpenCL バックエンド

```bash
cd katago/cpp
cmake . -DUSE_BACKEND=OPENCL
make -j$(nproc)
```

初回実行時に GPU ごとの自動チューニングが走る（数分）。
チューニング結果は `~/.katago/` にキャッシュされる。

#### Eigen バックエンド（CPU のみ）

```bash
cd katago/cpp
cmake . -DUSE_BACKEND=EIGEN
make -j$(nproc)
```

GPU が無い環境や動作確認に使用する。推論が大幅に遅くなる点に注意。

#### ビルド確認

```bash
./katago version
# → KataGo v1.x.x
```

ビルドした実行ファイルはそのまま `katago/cpp/katago` に生成される。
このプロジェクトのスクリプト・設定はデフォルトでそのパスを参照する。

---

### 3. モデルのダウンロード

公式最軽量モデル（b18c384nbt）を取得するスクリプトを用意している:

```bash
bash scripts/download_model.sh
```

スクリプトは `data/models/` にモデルを保存する。
ダウンロード済みの場合はスキップされる。

手動でダウンロードする場合は [KataGo Networks](https://katagotraining.org/networks/) から
`kata1-b18c384nbt` 系のファイルを取得して `data/models/` に置く。

---

### 4. 動作確認

```bash
# GTP モードで起動（すぐ Ctrl+C で終了して良い）
katago/cpp/katago gtp \
  -model data/models/kata1-b18c384nbt-s9996604736-d4316597426.bin.gz \
  -config data/katago_gtp.cfg
```

`KataGo v...` と表示されれば正常。

---

## 使い方

```bash
# 定石探索の実行（実装後）
python -m src.explorer \
  --katago katago/cpp/katago \
  --model  data/models/kata1-b18c384nbt-s9996604736-d4316597426.bin.gz \
  --config data/katago_gtp.cfg \
  --depth  20 \
  --output output/joseki.db
```

---

## ファイル構成

```
go9x9-joseki/
├── katago/              # git submodule: lightvector/KataGo
├── scripts/
│   └── download_model.sh  # モデル自動ダウンロード
├── src/
│   ├── board.py         # 9路盤表現 + Zobrist ハッシュ
│   ├── katago_pipe.py   # KataGo Analysis Mode 通信
│   ├── explorer.py      # 定石探索エンジン
│   └── export.py        # 結果出力 (SGF / JSON / SQLite)
├── data/
│   ├── models/          # KataGo モデル置き場（.gitignore 対象）
│   └── katago_gtp.cfg   # KataGo GTP 設定
├── tests/
│   └── test_board.py
├── CLAUDE.md
├── PROGRESS.md
└── README.md
```

---

## ライセンス

- このプロジェクトのコード: MIT License
- KataGo: MIT License（`katago/LICENSE` 参照）
