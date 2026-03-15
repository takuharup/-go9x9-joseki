# 実装進捗ログ

## ステータス凡例

- [ ] 未着手
- [~] 作業中
- [x] 完了

---

## フェーズ 1: プロジェクト初期化

- [x] リポジトリ作成
- [x] KataGo submodule 追加 (`katago/`)
- [x] ディレクトリ構成作成
- [x] 各モジュールのスケルトン作成 (`src/`)
- [x] `.gitignore` 設定
- [x] `CLAUDE.md` / `README.md` 作成

## フェーズ 2: コア実装

- [ ] `board.py` — `Board` クラス実装（盤面操作・着手合法判定）
- [ ] `board.py` — `ZobristTable` 実装
- [ ] `katago_pipe.py` — KataGo プロセス起動・終了
- [ ] `katago_pipe.py` — JSON クエリ送受信
- [ ] `katago_pipe.py` — `AnalysisResult` パース

## フェーズ 3: 探索エンジン

- [ ] `explorer.py` — 基本的な DFS 探索ループ
- [ ] `explorer.py` — 枝刈りロジック（勝率・Policy 閾値）
- [ ] `explorer.py` — Zobrist ハッシュによる重複局面検出
- [ ] `explorer.py` — 探索統計の収集

## フェーズ 4: エクスポート

- [ ] `export.py` — SGF エクスポート
- [ ] `export.py` — JSON エクスポート
- [ ] `export.py` — SQLite スキーマ設計・エクスポート

## フェーズ 5: 検証・最適化

- [ ] 小規模テスト（深さ5程度での動作確認）
- [ ] パフォーマンス計測・ボトルネック特定
- [ ] 並列クエリ対応（KataGo の並列処理活用）

---

## 変更履歴

### 2026-03-15
- プロジェクト初期化、スケルトン作成
