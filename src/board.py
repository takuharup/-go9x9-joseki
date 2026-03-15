"""
board.py - 9路盤の盤面表現と Zobrist ハッシュ

盤面は int[81] の1次元配列で表現する（row * 9 + col でインデックス）。
モジュールレベル関数と、それをラップする Board クラスの両方を提供する。

  EMPTY = 0, BLACK = 1, WHITE = 2

モジュールレベル API:
  new_board()                              → list[int]
  compute_hash(board)                      → int
  place_stone(board, row, col, color)      → (new_board, captured) | None
  get_legal_moves(board, color, ko_hash)   → list[(row, col)]
"""

from __future__ import annotations

import random
from typing import Optional

# ---------------------------------------------------------------------------
# 定数
# ---------------------------------------------------------------------------

SIZE: int = 9
EMPTY: int = 0
BLACK: int = 1
WHITE: int = 2

_OPPONENT = {BLACK: WHITE, WHITE: BLACK}


# ---------------------------------------------------------------------------
# Zobrist テーブル
# ---------------------------------------------------------------------------

class ZobristTable:
    """Zobrist ハッシュのランダムテーブルを管理するクラス。

    各 (座標, 色) ペアに対して64ビットの乱数を割り当てる。
    シードを固定することで実行間の再現性を保証する。
    """

    def __init__(self, seed: int = 42) -> None:
        """ランダムテーブルを初期化する。

        Args:
            seed: 乱数シード（再現性のため固定）
        """
        rng = random.Random(seed)
        # _table[pos][color - 1]  (color: 1=BLACK → 0, 2=WHITE → 1)
        self._table: list[list[int]] = [
            [rng.getrandbits(64), rng.getrandbits(64)]
            for _ in range(SIZE * SIZE)
        ]

    def get_value(self, pos: int, color: int) -> int:
        """指定座標・色に対応するハッシュ値を返す。

        Args:
            pos: row * SIZE + col
            color: BLACK(1) または WHITE(2)

        Returns:
            64ビット整数のハッシュ値
        """
        return self._table[pos][color - 1]


# モジュール共有のシングルトン
_ZOBRIST = ZobristTable()


# ---------------------------------------------------------------------------
# 盤面ユーティリティ
# ---------------------------------------------------------------------------

def new_board() -> list[int]:
    """空の9路盤（int[81]、全 EMPTY）を返す。"""
    return [EMPTY] * (SIZE * SIZE)


def compute_hash(board: list[int]) -> int:
    """盤面全体の Zobrist ハッシュを計算して返す。

    Args:
        board: int[81] の盤面配列

    Returns:
        64ビット整数のハッシュ値（同一局面は常に同値）
    """
    h = 0
    for pos, color in enumerate(board):
        if color != EMPTY:
            h ^= _ZOBRIST.get_value(pos, color)
    return h


def _idx(row: int, col: int) -> int:
    """(row, col) を1次元インデックスに変換する。"""
    return row * SIZE + col


def _neighbors(pos: int) -> list[int]:
    """上下左右の隣接インデックスリストを返す（盤外を除く）。"""
    row, col = divmod(pos, SIZE)
    result: list[int] = []
    if row > 0:        result.append(_idx(row - 1, col))
    if row < SIZE - 1: result.append(_idx(row + 1, col))
    if col > 0:        result.append(_idx(row, col - 1))
    if col < SIZE - 1: result.append(_idx(row, col + 1))
    return result


def _get_group(board: list[int], pos: int) -> tuple[set[int], set[int]]:
    """フラッドフィルで連の全座標と呼吸点を返す。

    Args:
        board: 盤面配列
        pos:   連に属する任意の1点

    Returns:
        (group, liberties)  いずれも座標インデックスの set
    """
    color = board[pos]
    group: set[int] = set()
    liberties: set[int] = set()
    stack = [pos]
    while stack:
        p = stack.pop()
        if p in group:
            continue
        group.add(p)
        for n in _neighbors(p):
            if board[n] == EMPTY:
                liberties.add(n)
            elif board[n] == color and n not in group:
                stack.append(n)
    return group, liberties


# ---------------------------------------------------------------------------
# 着手処理
# ---------------------------------------------------------------------------

def place_stone(
    board: list[int], row: int, col: int, color: int
) -> Optional[tuple[list[int], list[int]]]:
    """石を置き (新盤面, 取り石インデックスリスト) を返す。

    合法手チェックは行わない（呼び出し側の責任）。
    座標がすでに占有されている場合は None を返す。

    処理順:
      1. 指定座標に石を置く
      2. 相手の呼吸点が0になった連を全て取り上げる
      3. 取り石リストを返す（自殺手・コウの判定は行わない）

    Args:
        board: 元の盤面（変更されない）
        row:   行 (0-indexed)
        col:   列 (0-indexed)
        color: BLACK または WHITE

    Returns:
        (new_board, captured_indices) または None
    """
    pos = _idx(row, col)
    if board[pos] != EMPTY:
        return None

    new = board[:]
    new[pos] = color
    opponent = _OPPONENT[color]

    captured: list[int] = []
    for n in _neighbors(pos):
        if new[n] == opponent:
            group, libs = _get_group(new, n)
            if not libs:
                captured.extend(group)
                for p in group:
                    new[p] = EMPTY

    return new, captured


# ---------------------------------------------------------------------------
# 合法手判定
# ---------------------------------------------------------------------------

def is_legal(
    board: list[int],
    row: int,
    col: int,
    color: int,
    ko_hash: Optional[int] = None,
) -> bool:
    """指定の着手が合法かどうかを判定する。

    判定順:
      1. 座標が盤内かつ空きであること
      2. 着手後（取り石除去後）に自連の呼吸点が1以上あること（自殺手禁止）
      3. 着手後の局面ハッシュが ko_hash と一致しないこと（コウ禁止）

    Args:
        board:   盤面配列
        row:     行 (0-indexed)
        col:     列 (0-indexed)
        color:   BLACK または WHITE
        ko_hash: 禁止局面のハッシュ（None でコウチェックなし）

    Returns:
        合法であれば True
    """
    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return False

    result = place_stone(board, row, col, color)
    if result is None:
        return False
    new_board, _ = result

    # 自殺手チェック: 着手後（取り石除去後）に自連の呼吸点が0なら違法
    pos = _idx(row, col)
    _, own_libs = _get_group(new_board, pos)
    if not own_libs:
        return False

    # コウチェック
    if ko_hash is not None and compute_hash(new_board) == ko_hash:
        return False

    return True


def get_legal_moves(
    board: list[int],
    color: int,
    ko_hash: Optional[int] = None,
) -> list[tuple[int, int]]:
    """color の合法手 (row, col) リストを返す。

    Args:
        board:   盤面配列
        color:   BLACK または WHITE
        ko_hash: 禁止局面のハッシュ（None でコウチェックなし）

    Returns:
        合法手の (row, col) タプルリスト
    """
    return [
        (row, col)
        for row in range(SIZE)
        for col in range(SIZE)
        if is_legal(board, row, col, color, ko_hash)
    ]


# ---------------------------------------------------------------------------
# Board クラス（高レベルラッパー）
# ---------------------------------------------------------------------------

class Board:
    """9路盤の状態を管理する高レベルクラス。

    内部的には int[81] 配列と Zobrist ハッシュを保持し、
    モジュールレベル関数に処理を委譲する。
    """

    SIZE = SIZE
    EMPTY = EMPTY
    BLACK = BLACK
    WHITE = WHITE

    def __init__(self, stones: Optional[list[int]] = None) -> None:
        """盤面を初期化する。

        Args:
            stones: 初期盤面配列（None の場合は空盤）
        """
        self._stones: list[int] = stones[:] if stones else new_board()
        self._hash: int = compute_hash(self._stones)

    # ------------------------------------------------------------------
    # プロパティ
    # ------------------------------------------------------------------

    @property
    def stones(self) -> list[int]:
        """盤面配列（読み取り専用ビュー）。"""
        return self._stones

    def get_hash(self) -> int:
        """現在の局面の Zobrist ハッシュ値を返す。"""
        return self._hash

    # ------------------------------------------------------------------
    # 盤面操作
    # ------------------------------------------------------------------

    def copy(self) -> Board:
        """現在の盤面の複製を返す（O(81) のシャローコピー）。"""
        b = Board.__new__(Board)
        b._stones = self._stones[:]
        b._hash = self._hash
        return b

    def place_stone(
        self, row: int, col: int, color: int
    ) -> tuple[bool, list[int]]:
        """石を置く（合法手チェックなし）。

        Args:
            row:   行 (0-indexed)
            col:   列 (0-indexed)
            color: BLACK または WHITE

        Returns:
            (成功フラグ, 取り石インデックスリスト)
        """
        result = place_stone(self._stones, row, col, color)
        if result is None:
            return False, []
        self._stones, captured = result
        self._hash = compute_hash(self._stones)
        return True, captured

    # ------------------------------------------------------------------
    # 判定
    # ------------------------------------------------------------------

    def is_legal(
        self,
        row: int,
        col: int,
        color: int,
        ko_hash: Optional[int] = None,
    ) -> bool:
        """指定の着手が合法かどうかを判定する。"""
        return is_legal(self._stones, row, col, color, ko_hash)

    def get_legal_moves(
        self,
        color: int,
        ko_hash: Optional[int] = None,
    ) -> list[tuple[int, int]]:
        """color の合法手リストを返す。"""
        return get_legal_moves(self._stones, color, ko_hash)

    # ------------------------------------------------------------------
    # ユーティリティ
    # ------------------------------------------------------------------

    def to_sgf_coords(self, row: int, col: int) -> str:
        """(row, col) を SGF 座標文字列に変換する（例: (0,0) → "aa"）。"""
        return chr(ord("a") + col) + chr(ord("a") + row)

    def __repr__(self) -> str:
        """盤面の ASCII 表現を返す（X=黒, O=白, .=空）。"""
        sym = {EMPTY: ".", BLACK: "X", WHITE: "O"}
        header = "  " + " ".join(str(c) for c in range(SIZE))
        rows = [
            f"{r} " + " ".join(sym[self._stones[_idx(r, c)]] for c in range(SIZE))
            for r in range(SIZE)
        ]
        return header + "\n" + "\n".join(rows)
