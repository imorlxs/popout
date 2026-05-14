import math
import numpy as np
from concurrent.futures import ProcessPoolExecutor

ROWS = 6
COLS = 7
MAX_STEPS = 200

try:
    from numba import njit
except Exception:
    # Fallback decorator if numba is not installed
    def njit(fn=None, **kwargs):
        if fn is None:
            return lambda f: f
        return fn


@njit
def _get_winner(board):
    # board is 2D numpy array shape (6,7)
    for player in (1, 2):
        # horizontal
        for r in range(ROWS):
            count = 0
            for c in range(COLS):
                if board[r, c] == player:
                    count += 1
                    if count >= 4:
                        return player
                else:
                    count = 0

        # vertical
        for c in range(COLS):
            count = 0
            for r in range(ROWS):
                if board[r, c] == player:
                    count += 1
                    if count >= 4:
                        return player
                else:
                    count = 0

        # diag TL-BR
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                cnt = 0
                for k in range(4):
                    if board[r + k, c + k] == player:
                        cnt += 1
                    else:
                        break
                if cnt >= 4:
                    return player

        # diag TR-BL
        for r in range(ROWS - 3):
            for c in range(3, COLS):
                cnt = 0
                for k in range(4):
                    if board[r + k, c - k] == player:
                        cnt += 1
                    else:
                        break
                if cnt >= 4:
                    return player

    return 0


@njit
def _can_drop(board, col):
    return 0 <= col < COLS and board[0, col] == 0


@njit
def _drop(board, col, player):
    for r in range(ROWS - 1, -1, -1):
        if board[r, col] == 0:
            board[r, col] = player
            return True
    return False


@njit
def _can_pop(board, col, player):
    return 0 <= col < COLS and board[ROWS - 1, col] == player


@njit
def _pop(board, col):
    for r in range(ROWS - 1, 0, -1):
        board[r, col] = board[r - 1, col]
    board[0, col] = 0
    return True


@njit
def _is_full(board):
    for c in range(COLS):
        if board[0, c] == 0:
            return False
    return True


@njit
def _pick_random_move(board, player):
    # returns (code, col)
    # code: 1=drop, 2=pop, 0=draw (only possible at full board with pop available)
    possible_cols = np.empty(COLS * 2, dtype=np.int64)
    count = 0
    # drops
    for c in range(COLS):
        if _can_drop(board, c):
            possible_cols[count] = (1 << 16) | c
            count += 1
    # pops
    for c in range(COLS):
        if _can_pop(board, c, player):
            possible_cols[count] = (2 << 16) | c
            count += 1

    if count == 0:
        return 0, -1

    idx = np.random.randint(0, count)
    val = possible_cols[idx]
    code = val >> 16
    col = int(val & 0xFFFF)
    # draw rule: only when full and pops exist
    if code == 0:
        return 0, -1
    return code, col


@njit
def _rollout(flat_board, current_player, max_steps):
    board = flat_board.reshape((ROWS, COLS)).copy()

    for _ in range(max_steps):
        winner = _get_winner(board)
        if winner != 0:
            return winner

        code, col = _pick_random_move(board, current_player)
        if code == 0:
            return 0
        if code == 1:
            _drop(board, col, current_player)
        else:
            _pop(board, col)

        current_player = 1 if current_player == 2 else 2

    return _get_winner(board)


def _worker_run(flat_board, player_id, iterations):
    # pure python worker that uses numba rollout for speed
    flat = np.array(flat_board, dtype=np.int64)
    wins = {}
    visits = {}

    for _ in range(iterations):
        # pick first move uniformly among possible
        board2 = flat.reshape((ROWS, COLS)).copy()
        # build possible moves in python for the first move
        moves = []
        for c in range(COLS):
            if board2[0, c] == 0:
                moves.append(("drop", c))
        for c in range(COLS):
            if board2[ROWS - 1, c] == player_id:
                moves.append(("pop", c))
        if _is_full(board2) and any(m[0] == "pop" for m in moves):
            moves.append(("draw", -1))

        if not moves:
            first_move = ("draw", -1)
        else:
            idx = np.random.randint(0, len(moves))
            first_move = moves[idx]

        # apply first move
        if first_move[0] == "draw":
            winner = 0
        else:
            code = 1 if first_move[0] == "drop" else 2
            col = first_move[1]
            # apply
            if code == 1:
                _drop(board2, col, player_id)
            else:
                _pop(board2, col)

            # simulate rest
            next_player = 1 if player_id == 2 else 2
            winner = _rollout(board2.flatten(), next_player, MAX_STEPS)

        visits[first_move] = visits.get(first_move, 0) + 1
        if winner == player_id:
            wins[first_move] = wins.get(first_move, 0) + 1

    return wins, visits


def parallel_root_monte_carlo(board, player_id, iterations=10000, processes=4):
    """Run parallel flat Monte Carlo rollouts from root and return the best move.

    This is a root-parallel flat Monte Carlo: each rollout picks a first move
    uniformly and simulates the rest using a fast numba rollout. Results are
    aggregated across worker processes and the best move (highest win rate)
    is returned.
    """
    flat = np.array(board.to_flat_list(), dtype=np.int64)

    # split iterations across processes
    per_worker = [iterations // processes] * processes
    for i in range(iterations % processes):
        per_worker[i] += 1

    args = [(flat, int(player_id), it) for it in per_worker if it > 0]

    total_wins = {}
    total_visits = {}

    if len(args) == 1:
        w, v = _worker_run(*args[0])
        for k, val in w.items():
            total_wins[k] = total_wins.get(k, 0) + val
        for k, val in v.items():
            total_visits[k] = total_visits.get(k, 0) + val
    else:
        with ProcessPoolExecutor(max_workers=processes) as ex:
            futures = [ex.submit(_worker_run, a[0], a[1], a[2]) for a in args]
            for fut in futures:
                w, v = fut.result()
                for k, val in w.items():
                    total_wins[k] = total_wins.get(k, 0) + val
                for k, val in v.items():
                    total_visits[k] = total_visits.get(k, 0) + val

    # select best move by win rate (wins / visits), tie-break by visits
    best_move = None
    best_score = -1.0

    for move, vis in total_visits.items():
        win = total_wins.get(move, 0)
        score = win / vis if vis > 0 else 0.0
        if score > best_score or (abs(score - best_score) < 1e-12 and vis > (total_visits.get(best_move, 0) if best_move else 0)):
            best_score = score
            best_move = move

    # If no move was found (shouldn't happen), fallback to a random legal move
    if best_move is None:
        moves = board.get_possible_moves(player_id)
        if not moves:
            return ("draw", -1)
        return moves[0]

    return best_move
