# go9x9-joseki — 9路盤定石網羅的探索プロジェクト

## プロジェクトの目的

KataGo の強化学習モデルを用いて **9路盤の序盤定石を網羅的に探索・記録** することを目的とする。

9路盤は19路盤と比べてゲームツリーが扱いやすいサイズであり、AIの最善応手を系統的に収集・分析することで、定石データベースの構築や人間の学習支援ツールの開発が現実的に可能である。

### 具体的なゴール

1. KataGo Analysis Mode を用いた高精度な局面評価
2. 勝率・スコアリードを基準とした枝刈りによる効率的な定石ツリー構築
3. Zobrist ハッシュによる局面の同一判定と重複排除
4. SGF・JSON・SQLite への結果エクスポート

---

## プロジェクト構成

```
go9x9-joseki/
├── katago/              # git submodule: lightvector/KataGo
├── src/
│   ├── board.py         # 9路盤表現 + Zobrist ハッシュ
│   ├── katago_pipe.py   # KataGo Analysis Mode との JSON 通信
│   ├── explorer.py      # 定石探索エンジン（DFS/BFS + 枝刈り）
│   └── export.py        # 結果出力 (SGF / JSON / SQLite)
├── data/
│   └── models/          # KataGo モデルファイル置き場（.gitignore 対象）
├── CLAUDE.md            # このファイル
├── PROGRESS.md          # 実装進捗ログ
├── README.md            # プロジェクト概要
└── .gitignore
```

---

## 開発ガイドライン

### セットアップ

```bash
# KataGo submodule の初期化
git submodule update --init --recursive

# KataGo のビルド（要 CMake / CUDA）
cd katago/cpp && cmake . -DUSE_BACKEND=CUDA && make -j4

# モデルの配置
# https://katagotraining.org/ からモデルをダウンロード
cp <model>.bin.gz data/models/
```

### 主要モジュール

| ファイル | 役割 |
|---|---|
| `src/board.py` | `Board` クラス・着手合法判定・Zobrist ハッシュ |
| `src/katago_pipe.py` | サブプロセス起動・JSON送受信・`AnalysisResult` |
| `src/explorer.py` | `JosekiExplorer` による再帰探索・枝刈り設定 |
| `src/export.py` | SGF/JSON/SQLite への書き出し |

### KataGo Analysis Mode プロトコル

- 標準入力に JSON 1行を送信し、標準出力の JSON 応答を受信する
- 詳細: `katago/docs/Analysis_Engine.md`

### 探索パラメーター（`ExplorationConfig`）

| パラメーター | 説明 | デフォルト |
|---|---|---|
| `max_depth` | 最大探索手数 | 20 |
| `winrate_threshold` | 探索打ち切りの勝率下限 | 0.45 |
| `policy_threshold` | 探索する最小 Policy 確率 | 0.01 |
| `max_branches` | 各局面の最大分岐数 | 10 |
