import random
import time
from collections import defaultdict
import itertools
import multiprocessing as mp
import os

# Constants
MAX_TURN = 1
MIN_TURN = -1
MAX_SUCC = 100
VS = -1000000
VL = 1000000
BLANK = 0
OPP_COLOR = -1
MY_COLOR = 1

# Heuristic weights
CORNER_MULTI = 1000
EDGE_MULTI = 50
NEAR_CORNER_PENALTY = 500
MOBILITY_MULTI = 20
STABILITY_MULTI = 100
SHITTY = 1000
FM_MULTI = 1

node_count = 0
best = "0"

# New constants
LATE_GAME_THRESHOLD = 50  # Number of empty squares to consider as late game
TRANSPOSITION_TABLE_SIZE = 1000000  # Size of the transposition table

# Global variables
node_count = 0
best = "0"
transposition_table = {}

def quiescence(state, alpha, beta, turn, depth):
    stand_pat = eval(state, turn)
    if depth == 0:
        return stand_pat
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    successors = expand(state, turn)
    successors = move_ordering(state, successors, turn)

    for succ in successors:
        r, c = int(succ[0]), int(succ[1])
        new_state = possible_move(state, r, c, turn, -turn)
        score = -quiescence(new_state, -beta, -alpha, -turn, depth - 1)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha



def available_moves(board, mine, yours):
    valid_move = "b"
    for i in range(8):
        for j in range(8):
            if board[i][j] == BLANK:
                # Check all 8 directions
                directions = [
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ]
                for di, dj in directions:
                    if 0 <= i + di < 8 and 0 <= j + dj < 8 and board[i + di][j + dj] == yours:
                        for k in range(1, 8):
                            ni, nj = i + k*di, j + k*dj
                            if not (0 <= ni < 8 and 0 <= nj < 8):
                                break
                            if board[ni][nj] == mine:
                                valid_move += f"{i}{j}"
                                break
                            if board[ni][nj] == BLANK:
                                break
    return valid_move

def stability(board, turn):
    others = -turn
    yStab = xStab = neStab = nwStab = 0
    value = 0

    for i in range(8):
        for j in range(8):
            if board[i][j] == turn:
                # Check vertical stability (y-axis)
                yStab = 1
                for k in range(i-1, -1, -1):  # check up
                    if board[k][j] != turn:
                        yStab = 0
                        break
                if not yStab:
                    yStab = 1
                    for k in range(i+1, 8):  # check down
                        if board[k][j] != turn:
                            yStab = 0
                            break

                # Check horizontal stability (x-axis)
                xStab = 1
                for l in range(j-1, -1, -1):  # check left
                    if board[i][l] != turn:
                        xStab = 0
                        break
                if not xStab:
                    xStab = 1
                    for l in range(j+1, 8):  # check right
                        if board[i][l] != turn:
                            xStab = 0
                            break

                # Check northeast-southwest diagonal stability
                neStab = 1
                for k, l in zip(range(i-1, -1, -1), range(j-1, -1, -1)):  # check top left
                    if board[k][l] != turn:
                        neStab = 0
                        break
                if not neStab:
                    neStab = 1
                    for k, l in zip(range(i+1, 8), range(j+1, 8)):  # check bottom right
                        if board[k][l] != turn:
                            neStab = 0
                            break

                # Check northwest-southeast diagonal stability
                nwStab = 1
                for k, l in zip(range(i-1, -1, -1), range(j+1, 8)):  # check top right
                    if board[k][l] != turn:
                        nwStab = 0
                        break
                if not nwStab:
                    nwStab = 1
                    for k, l in zip(range(i+1, 8), range(j-1, -1, -1)):  # check bottom left
                        if board[k][l] != turn:
                            nwStab = 0
                            break

                value += (yStab + xStab + neStab + nwStab)

    return value

def corner(board, mine, yours):
    return mine * (board[0][0] + board[0][7] + board[7][0] + board[7][7])

def near_corner_penalty(board, turn):
    penalty = 0
    corners = [(0,0), (0,7), (7,0), (7,7)]
    near_corner_spots = [
        [(0,1), (1,0), (1,1)],
        [(0,6), (1,7), (1,6)],
        [(6,0), (7,1), (6,1)],
        [(6,7), (7,6), (6,6)]
    ]
    for i, corner in enumerate(corners):
        if board[corner[0]][corner[1]] == 0:  # If corner is empty
            for spot in near_corner_spots[i]:
                if board[spot[0]][spot[1]] == turn:
                    penalty += 1
    return penalty

def shitty_squares(board, turn):
    value = 0
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    for i, j in corners:
        corner_val = 5 * board[i][j]
        adj1 = board[i + (1 if i == 0 else -1)][j]
        adj2 = board[i][j + (1 if j == 0 else -1)]
        diag = board[i + (1 if i == 0 else -1)][j + (1 if j == 0 else -1)]
        value += turn * (corner_val + adj1 + adj2 - 3 * diag)
    return value

def possible_move(orig, r, c, mine, yours):
    board = [row[:] for row in orig]
    board[r][c] = mine
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    for di, dj in directions:
        i, j = r + di, c + dj
        to_flip = []
        while 0 <= i < 8 and 0 <= j < 8 and board[i][j] == yours:
            to_flip.append((i, j))
            i, j = i + di, j + dj
        if 0 <= i < 8 and 0 <= j < 8 and board[i][j] == mine:
            for fi, fj in to_flip:
                board[fi][fj] = mine
    return board

def is_terminal(state, turn):
    return len(available_moves(state, turn, -turn)) == 1

def move_num(state, mine, yours):
    return (len(available_moves(state, mine, yours)) - 1) // 2

def expand(state, turn):
    moves = available_moves(state, turn, -turn)
    # Skip the first character 'b' and group the rest into pairs
    # Filter out any empty strings
    return [move for move in [moves[i:i+2] for i in range(1, len(moves), 2)] if move]

def eval(board, turn):
    score = 0
    score += corner_eval(board, turn) * CORNER_MULTI
    score += edge_eval(board, turn) * EDGE_MULTI
    score += near_corner_eval(board, turn) * NEAR_CORNER_PENALTY
    score += mobility_eval(board, turn) * MOBILITY_MULTI
    score += stability_eval(board, turn) * STABILITY_MULTI
    return score

def corner_eval(board, turn):
    corners = [(0,0), (0,7), (7,0), (7,7)]
    return sum(board[r][c] == turn for r, c in corners) - sum(board[r][c] == -turn for r, c in corners)

def edge_eval(board, turn):
    edges = [board[0], board[7], [board[i][0] for i in range(8)], [board[i][7] for i in range(8)]]
    return sum(row.count(turn) - row.count(-turn) for row in edges)

def near_corner_eval(board, turn):
    near_corners = [(0,1), (1,0), (1,1), (0,6), (1,7), (1,6), (6,0), (7,1), (6,1), (6,7), (7,6), (6,6)]
    return sum(board[r][c] == -turn for r, c in near_corners) - sum(board[r][c] == turn for r, c in near_corners)

def mobility_eval(board, turn):
    return len(expand(board, turn)) - len(expand(board, -turn))

def stability_eval(board, turn):
    return stability(board, turn) - stability(board, -turn)

def late_game_strategy(board):
    empty_count = sum(row.count(0) for row in board)
    if empty_count <= LATE_GAME_THRESHOLD:
        global PIECE_DIFF_MULTI, MOVE_NUM_MULTI, STAB_MULTI
        PIECE_DIFF_MULTI *= 2  # Increase importance of piece difference
        MOVE_NUM_MULTI //= 2   # Decrease importance of mobility
        STAB_MULTI *= 1.5      # Increase importance of stability

def improved_move_ordering(board, successors, turn):
    def move_score(move):
        r, c = int(move[0]), int(move[1])
        new_state = possible_move(board, r, c, turn, -turn)
        
        # Prioritize corners
        if move in ['00', '07', '70', '77']:
            return 10000
        
        # Avoid squares next to corners if the corner is empty
        if move in ['01', '06', '10', '16', '61', '67', '71', '76']:
            adjacent_corner = (0,0) if move in ['01', '10'] else (0,7) if move in ['06', '16'] else (7,0) if move in ['61', '71'] else (7,7)
            if board[adjacent_corner[0]][adjacent_corner[1]] == 0:
                return -5000
        
        # Prioritize edges, but be careful of the second-from-edge squares
        if r in [0, 7] or c in [0, 7]:
            if (r in [1, 6] and c in [0, 7]) or (c in [1, 6] and r in [0, 7]):
                return -1000  # Penalize second-from-edge squares
            return 1000
        
        # Use the evaluation function for other moves
        return eval(new_state, turn)

    return sorted(successors, key=move_score, reverse=True)

def transposition_table_lookup(board, depth, alpha, beta):
    key = hash(str(board))
    if key in transposition_table:
        stored_depth, stored_value, stored_flag = transposition_table[key]
        if stored_depth >= depth:
            if stored_flag == 'EXACT':
                return stored_value
            elif stored_flag == 'LOWERBOUND' and stored_value > alpha:
                alpha = stored_value
            elif stored_flag == 'UPPERBOUND' and stored_value < beta:
                beta = stored_value
            if alpha >= beta:
                return stored_value
    return None

def transposition_table_store(board, depth, value, flag):
    key = hash(str(board))
    if len(transposition_table) >= TRANSPOSITION_TABLE_SIZE:
        transposition_table.pop(next(iter(transposition_table)))
    transposition_table[key] = (depth, value, flag)

def principal_variation_search(state, depth, alpha, beta, turn, start_time, max_time, is_root=False):
    global node_count, best

    if time.time() - start_time > max_time:
        return None

    node_count += 1
    
    if depth == 0 or is_terminal(state, turn):
        return eval(state, turn)

    tt_result = transposition_table_lookup(state, depth, alpha, beta)
    if tt_result is not None:
        return tt_result

    successors = expand(state, turn)
    successors = improved_move_ordering(state, successors, turn)

    if not successors:
        return eval(state, turn)

    original_alpha = alpha
    best_move = None
    first_child = True
    for succ in successors:
        r, c = int(succ[0]), int(succ[1])
        new_state = possible_move(state, r, c, turn, -turn)

        if first_child:
            score = principal_variation_search(new_state, depth - 1, -beta, -alpha, -turn, start_time, max_time)
            first_child = False
        else:
            score = principal_variation_search(new_state, depth - 1, -alpha - 1, -alpha, -turn, start_time, max_time)
            if score is not None and alpha < score < beta:
                score = principal_variation_search(new_state, depth - 1, -beta, -score, -turn, start_time, max_time)

        if score is None:
            return None

        score = -score  # Negate the score here, after checking for None

        if score > alpha:
            alpha = score
            best_move = succ
            if is_root:
                best = succ

        if alpha >= beta:
            transposition_table_store(state, depth, alpha, 'LOWERBOUND')
            return alpha

    transposition_table_store(state, depth, alpha, 'EXACT' if alpha > original_alpha else 'UPPERBOUND')
    return alpha

def iterative_deepening(board, ai_color, max_time=5):
    global best
    start_time = time.time()
    depth = 1
    best_move = None

    late_game_strategy(board)

    while time.time() - start_time < max_time:
        shallow_board = [[1 if cell == ai_color else -1 if cell else 0 for cell in row] for row in board]
        value = principal_variation_search(shallow_board, depth, float('-inf'), float('inf'), 1, start_time, max_time, is_root=True)
        if value is not None:
            best_move = (int(best[0]), int(best[1]))
            depth += 1
        else:
            break

    return best_move


def play_single_game(max_time, game_number):
    process_id = os.getpid()
    print(f"Starting game {game_number} on process {process_id}")
    
    board = [[0 for _ in range(8)] for _ in range(8)]
    board[3][3] = board[4][4] = 1
    board[3][4] = board[4][3] = -1
    current_player = 1
    moves = 0

    while True:
        move = iterative_deepening(board, current_player, max_time)
        if move is None:
            if not any(0 in row for row in board):  # Board is full
                break
            current_player = -current_player
            continue

        r, c = move
        board = possible_move(board, r, c, current_player, -current_player)
        current_player = -current_player
        moves += 1

    # Count pieces to determine winner
    piece_count = sum(row.count(1) for row in board) - sum(row.count(-1) for row in board)
    winner = 1 if piece_count > 0 else -1 if piece_count < 0 else 0
    
    print(f"Game {game_number} finished on process {process_id}. Winner: {winner}, Moves: {moves}")
    return winner, moves

def self_play(num_games=100, max_time=1):
    print(f"Starting self-play with {num_games} games")
    print(f"Number of CPU cores: {mp.cpu_count()}")
    
    with mp.Pool() as pool:
        results = pool.starmap(play_single_game, [(max_time, i) for i in range(num_games)])
    
    wins = {1: 0, -1: 0, 0: 0}
    total_moves = 0
    for winner, moves in results:
        wins[winner] += 1
        total_moves += moves

    print(f"\nSelf-play completed")
    print(f"Player 1 wins: {wins[1]}")
    print(f"Player -1 wins: {wins[-1]}")
    print(f"Draws: {wins[0]}")
    print(f"Average moves per game: {total_moves / num_games}")

    return wins

def optimize_weights(iterations=10):
    global CORNER_MULTI, EDGE_MULTI, NEAR_CORNER_PENALTY, MOBILITY_MULTI, STABILITY_MULTI

    best_weights = (CORNER_MULTI, EDGE_MULTI, NEAR_CORNER_PENALTY, MOBILITY_MULTI, STABILITY_MULTI)
    best_win_ratio = 0

    for i in range(iterations):
        print(f"\nRunning iteration {i+1}/{iterations}")
        # Randomly adjust weights
        CORNER_MULTI = max(0, CORNER_MULTI + random.gauss(0, 100))
        EDGE_MULTI = max(0, EDGE_MULTI + random.gauss(0, 10))
        NEAR_CORNER_PENALTY = max(0, NEAR_CORNER_PENALTY + random.gauss(0, 50))
        MOBILITY_MULTI = max(0, MOBILITY_MULTI + random.gauss(0, 5))
        STABILITY_MULTI = max(0, STABILITY_MULTI + random.gauss(0, 10))

        print("Current weights:")
        print(f"CORNER_MULTI: {CORNER_MULTI}")
        print(f"EDGE_MULTI: {EDGE_MULTI}")
        print(f"NEAR_CORNER_PENALTY: {NEAR_CORNER_PENALTY}")
        print(f"MOBILITY_MULTI: {MOBILITY_MULTI}")
        print(f"STABILITY_MULTI: {STABILITY_MULTI}")

        wins = self_play(num_games=50, max_time=0.5)
        win_ratio = wins[1] / (wins[1] + wins[-1] + wins[0])

        if win_ratio > best_win_ratio:
            best_win_ratio = win_ratio
            best_weights = (CORNER_MULTI, EDGE_MULTI, NEAR_CORNER_PENALTY, MOBILITY_MULTI, STABILITY_MULTI)

        print(f"Current win ratio: {win_ratio}")
        print(f"Best win ratio so far: {best_win_ratio}")

    CORNER_MULTI, EDGE_MULTI, NEAR_CORNER_PENALTY, MOBILITY_MULTI, STABILITY_MULTI = best_weights
    print(f"\nOptimization completed")
    print(f"Optimized weights: {best_weights}")
    print(f"Best win ratio: {best_win_ratio}")

if __name__ == "__main__":
    mp.freeze_support()  # Needed for Windows
    optimize_weights()

