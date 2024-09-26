import random
import time

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
CORNER_MULTI = 500  # Increased from 150
MOVE_NUM_MULTI = 6
OPP_MOVE_MULTI = 20
STAB_MULTI = 70
OPP_STAB_MULTI = 10
SHITTY = 1000
FM_MULTI = 1
NEAR_CORNER_PENALTY = 200  # New constant

node_count = 0
best = "0"

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
    s = STAB_MULTI * stability(board, turn) - OPP_STAB_MULTI * stability(board, -turn)
    c = CORNER_MULTI * corner(board, turn, -turn)
    m = MOVE_NUM_MULTI * move_num(board, turn, -turn)
    o = -OPP_MOVE_MULTI * move_num(board, -turn, turn)
    ss = SHITTY * shitty_squares(board, turn)
    ncp = -NEAR_CORNER_PENALTY * near_corner_penalty(board, turn)
    
    # Add edge control
    e = EDGE_MULTI * edge_control(board, turn)
    
    # Add piece difference, more important in endgame
    p = PIECE_DIFF_MULTI * piece_difference(board, turn)
    
    # Add parity (odd/even empty squares)
    par = PARITY_MULTI * parity(board)
    
    return s + c + m + o + ss + ncp + e + p + par

def edge_control(board, turn):
    edges = [board[0], board[7], [board[i][0] for i in range(8)], [board[i][7] for i in range(8)]]
    return sum(edge.count(turn) - edge.count(-turn) for edge in edges)

def piece_difference(board, turn):
    flat_board = [cell for row in board for cell in row]
    return flat_board.count(turn) - flat_board.count(-turn)

def parity(board):
    empty_count = sum(row.count(0) for row in board)
    return 1 if empty_count % 2 == 0 else -1

# Add new constants
EDGE_MULTI = 30
PIECE_DIFF_MULTI = 10
PARITY_MULTI = 5

def iterative_deepening(board, ai_color, max_time=5):
    global best
    start_time = time.time()
    depth = 1
    best_move = None

    while time.time() - start_time < max_time:
        shallow_board = [[1 if cell == ai_color else -1 if cell else 0 for cell in row] for row in board]
        value = alphabeta(shallow_board, depth, 0, float('-inf'), float('inf'), start_time, max_time)
        if value is not None:
            best_move = (int(best[0]), int(best[1]))
            depth += 1
        else:
            break  # Time limit reached

    return best_move

def move_ordering(board, successors, turn):
    # Improved move ordering: prioritize corners, then edges, then evaluate moves
    corners = ['00', '07', '70', '77']
    edges = ['01', '02', '03', '04', '05', '06', '10', '20', '30', '40', '50', '60', '17', '27', '37', '47', '57', '67', '71', '72', '73', '74', '75', '76']
    
    def move_score(move):
        r, c = int(move[0]), int(move[1])
        if move in corners:
            return 1000
        elif move in edges:
            return 100
        return eval(possible_move(board, r, c, turn, -turn), turn)

    return sorted(successors, key=move_score, reverse=True)

def alphabeta(state, max_depth, cur_depth, alpha, beta, start_time, max_time):
    global node_count, best
    
    if time.time() - start_time > max_time:
        return None  # Time limit reached
    
    node_count += 1
    turn = MAX_TURN if cur_depth % 2 == 0 else MIN_TURN
    
    if cur_depth == max_depth or is_terminal(state, turn):
        return eval(state, turn)

    successors = expand(state, turn)
    successors = move_ordering(state, successors, turn)  # Apply move ordering
    
    if not successors:  # If there are no valid moves
        return eval(state, turn)

    if turn == MAX_TURN:
        for succ in successors:
            r, c = int(succ[0]), int(succ[1])
            new_state = possible_move(state, r, c, turn, -turn)
            cur_value = alphabeta(new_state, max_depth, cur_depth + 1, alpha, beta, start_time, max_time)
            if cur_value is None:
                return None  # Time limit reached
            if cur_value > alpha or (cur_value == alpha and random.randint(0, 1) == 0):
                alpha = cur_value
                if cur_depth == 0:
                    best = succ
            if alpha >= beta:
                return alpha
        return alpha
    else:
        for succ in successors:
            r, c = int(succ[0]), int(succ[1])
            new_state = possible_move(state, r, c, turn, -turn)
            cur_value = alphabeta(new_state, max_depth, cur_depth + 1, alpha, beta, start_time, max_time)
            if cur_value is None:
                return None  # Time limit reached
            if cur_value < beta:
                beta = cur_value
            if alpha >= beta:
                return beta
        return beta

def get_best_move(board, ai_color, max_time=5):
    return iterative_deepening(board, ai_color, max_time)

def main():
    board = [[0 for _ in range(8)] for _ in range(8)]
    
    # Read the board from file
    with open("board.txt", "r") as fp:
        for i in range(8):
            row = fp.readline().split()
            for j in range(8):
                board[i][j] = int(row[j])

    # Print the board
    for row in board:
        print(" ".join(map(str, row)))

    value = alphabeta(board, 4, 0, VS, VL)
    print(f"best value {value}")
    print(f"move {best}")
    print(node_count)

    r, c = int(best[0]), int(best[1])
    # Here you would typically make the move on the actual game board
    # putMove(r, c)

if __name__ == "__main__":
    main()