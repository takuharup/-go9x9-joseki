#!/usr/bin/env bash
# scripts/download_model.sh
#
# KataGo 公式最軽量モデル（kata1-b18c384nbt）を data/models/ にダウンロードする。
# ダウンロード済みの場合はスキップする。
#
# 使い方:
#   bash scripts/download_model.sh
#
# 前提:
#   wget がインストールされていること

set -euo pipefail

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------

MODEL_FILE="kata1-b18c384nbt-s9996604736-d4316597426.bin.gz"
MODEL_URL="https://media.katagotraining.org/uploaded/networks/models/kata1/${MODEL_FILE}"
DEST_DIR="$(cd "$(dirname "$0")/.." && pwd)/data/models"
DEST_PATH="${DEST_DIR}/${MODEL_FILE}"

# ---------------------------------------------------------------------------
# ダウンロード
# ---------------------------------------------------------------------------

echo "=== KataGo モデルダウンロード ==="
echo "保存先: ${DEST_PATH}"
echo ""

mkdir -p "${DEST_DIR}"

if [[ -f "${DEST_PATH}" ]]; then
    echo "✓ すでにダウンロード済みです。スキップします。"
    echo "  ${DEST_PATH}"
    exit 0
fi

if ! command -v wget &>/dev/null; then
    echo "エラー: wget が見つかりません。インストールしてください。" >&2
    echo "  Ubuntu/Debian: sudo apt install wget" >&2
    echo "  macOS:         brew install wget" >&2
    exit 1
fi

echo "ダウンロード中..."
echo "  URL: ${MODEL_URL}"
echo ""

wget \
    --progress=bar:force \
    --tries=3 \
    --waitretry=5 \
    --output-document="${DEST_PATH}.tmp" \
    "${MODEL_URL}"

# ダウンロード成功後にリネーム（中断時に壊れたファイルが残らないように）
mv "${DEST_PATH}.tmp" "${DEST_PATH}"

echo ""
echo "✓ ダウンロード完了: ${DEST_PATH}"
echo "  サイズ: $(du -h "${DEST_PATH}" | cut -f1)"
