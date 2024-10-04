import random

# Constants
MAX_TURN = 1
MIN_TURN = -1
MAX_SUCC = 100
VS = -1000000
VL = 1000000
BLANK = 0
OPP_COLOR = -1
MY_COLOR = 1
CORNER_MULTI = 150
MOVE_NUM_MULTI = 6
OPP_MOVE_MULTI = 20
STAB_MULTI = 70
OPP_STAB_MULTI = 10
SHITTY = 1000
FM_MULTI = 1
moves = ""
board = [[0 for _ in range(8)] for _ in range(8)]
best = "0"
node_count = 0

# find all available moves
# @input n: board
# @input mine: my color
# @input yours: opponent's color
# @output valid_move: with the format "brcrcrc" where r is the row and c is the column
def available_moves(n, mine, yours):
    valid_move = "b"
    for i in range(8):
        for j in range(8):
            if n[i][j] == BLANK:
                # Check all 8 directions
                directions = [
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ]
                for di, dj in directions:
                    if 0 <= i + di < 8 and 0 <= j + dj < 8 and n[i + di][j + dj] == yours:
                        k, l = i + di, j + dj
                        while 0 <= k < 8 and 0 <= l < 8:
                            if n[k][l] == mine:
                                valid_move += f"{i}{j}"
                                break
                            if n[k][l] == BLANK:
                                break
                            k, l = k + di, l + dj

    return valid_move

def stability(n, turn):
    others = -1 * turn
    value = 0
    for i in range(8):
        for j in range(8):
            if n[i][j] == turn:
                y_stab = x_stab = ne_stab = nw_stab = 1
                # Check stability in all directions
                for k in range(8):
                    if n[k][j] != turn:
                        y_stab = 0
                        break
                for l in range(8):
                    if n[i][l] != turn:
                        x_stab = 0
                        break
                for k, l in zip(range(8), range(8)):
                    if n[k][l] != turn:
                        ne_stab = 0
                        break
                for k, l in zip(range(8), range(7, -1, -1)):
                    if n[k][l] != turn:
                        nw_stab = 0
                        break
                value += y_stab + x_stab + ne_stab + nw_stab
    return value

def corner(n, mine, yours):
    return mine * (n[0][0] + n[0][7] + n[7][0] + n[7][7])

def shitty_squares(n, turn):
    nw = 5*n[0][0] + n[1][0] + n[0][1] - 3*n[1][1]
    sw = 5*n[0][7] + n[0][6] + n[1][7] - 3*n[1][6]
    se = 5*n[7][0] + n[6][0] - 3*n[6][1] + n[7][1]
    ne = 5*n[7][7] + n[7][6] - 3*n[6][6] + n[6][7]
    return turn * (nw + sw + se + ne)

def possible_move(orig, n, r, c, mine, yours):
    n = [row[:] for row in orig]
    n[r][c] = mine
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    for di, dj in directions:
        i, j = r + di, c + dj
        flip_counter = 0
        while 0 <= i < 8 and 0 <= j < 8:
            if n[i][j] == yours:
                flip_counter += 1
            elif n[i][j] == BLANK:
                break
            elif n[i][j] == mine:
                for k in range(1, flip_counter + 1):
                    n[r + k*di][c + k*dj] = mine
                break
            i, j = i + di, j + dj
    return n

def future_moves(n, turn):
    value = 0
    for i in range(8):
        for j in range(8):
            if n[i][j] == BLANK:
                directions = [
                    (0, 1), (0, -1), (1, 0), (-1, 0),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ]
                for di, dj in directions:
                    if 0 <= i + di < 8 and 0 <= j + dj < 8 and n[i + di][j + dj] == -1 * turn:
                        value += 1
    return value

def is_terminal(state, turn):
    global moves
    moves = available_moves(state, turn, -1 * turn)
    return moves == "b"

# find the number of moves, if refind is true, then find the available moves
# if
# @input n: board
# @input mine: my color
# @input yours: opponent's color
# @input refind: if it's the first time finding the available moves
# @output move_num: number of moves
def move_num(n, mine, yours, refind):
    global moves
    if refind:
        return (len(available_moves(n, mine, yours)) - 1) // 2
    else:
        return (len(moves) - 1) // 2

# 
def expand(state, turn):
    global moves
    sn = move_num(state, turn, -1 * turn, 0)
    successor = []
    for _ in range(sn):
        rc = moves[-2:]
        moves = moves[:-2]
        successor.append(rc)
    return successor

def eval(n, turn):
    s = STAB_MULTI * stability(n, turn) - OPP_STAB_MULTI * stability(n, -1 * turn)
    c = CORNER_MULTI * corner(n, turn, -1 * turn)
    m = MOVE_NUM_MULTI * move_num(n, turn, -1 * turn, 1)
    o = -OPP_MOVE_MULTI * move_num(n, -1 * turn, turn, 1)
    ss = SHITTY * shitty_squares(n, turn)
    return s + c + m + o + ss

# alpha beta pruning
def alphabeta(state, max_depth, cur_depth, alpha, beta):
    # add a node
    global node_count
    global best
    node_count += 1
    # determine whose turn it is
    turn = MAX_TURN if cur_depth % 2 == 0 else MIN_TURN

    # cutoff test
    if cur_depth == max_depth or is_terminal(state, turn):
        return eval(state, turn)

    # expand the state
    successor = expand(state, turn)

    # if it's max's turn
    if turn == MAX_TURN:
        alpha = VS
        for move in successor:
            r, c = int(move[0]), int(move[1])
            n = possible_move(state, state, r, c, turn, -1 * turn)
            cur_value = alphabeta(n, max_depth, cur_depth + 1, alpha, beta)
            if cur_value > alpha or (cur_value == alpha and random.randint(0, 1) == 0):
                alpha = cur_value
                if cur_depth == 0:
                    best = move
            if alpha >= beta:
                return alpha
        return alpha
    else:
        for move in successor:
            r, c = int(move[0]), int(move[1])
            n = possible_move(state, state, r, c, turn, -1 * turn)
            cur_value = alphabeta(n, max_depth, cur_depth + 1, alpha, beta)
            if beta > cur_value:
                beta = cur_value
            if alpha >= beta:
                return beta
        return beta

def main(b, depth):
    global board
    # Read the board from file
    global node_count
    global moves
    global best
    moves = ""
    best = ""
    node_count = 0

    board = b
    value = alphabeta(board, depth, 0, VS, VL)
    
    
    return [int(best[0]), int(best[1])]
    #r, c = int(best[0]), int(best[1])
    #reset global variables
    
    
    # Here you would typically make the move on the board
    # putMove(r, c)

if __name__ == "__main__":
    main()