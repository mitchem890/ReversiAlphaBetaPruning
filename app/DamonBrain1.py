import math
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def alpha_beta_reversi(board, difficulty):
    start_time = time.time()
    nodes_generated = 0
    max_depth_reached = 0
    
    # Convert difficulty to thinking time using a non-linear progression
    max_times = [1, 3, 8, 20, 45]
    max_time = max_times[difficulty - 1]

    logger.info(f"Difficulty: {difficulty}, Max thinking time: {max_time} seconds")

    def is_valid_move(board, row, col, player):
        if board[row][col] != 0:
            return False
        
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == -player:
                while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == -player:
                    r, c = r + dr, c + dc
                if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
                    return True
        return False

    def get_valid_moves(board, player):
        return [(r, c) for r in range(8) for c in range(8) if is_valid_move(board, r, c, player)]

    def make_move(board, row, col, player):
        new_board = [row[:] for row in board]
        new_board[row][col] = player
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            while 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == -player:
                to_flip.append((r, c))
                r, c = r + dr, c + dc
            if 0 <= r < 8 and 0 <= c < 8 and new_board[r][c] == player:
                for fr, fc in to_flip:
                    new_board[fr][fc] = player
        return new_board

    def evaluate_board(board):
        corner_weight = 25
        near_corner_weight = -5
        edge_weight = 5
        mobility_weight = 2
        piece_weight = 1
        stability_weight = 10

        score = 0
        ai_moves = len(get_valid_moves(board, 1))
        opponent_moves = len(get_valid_moves(board, -1))

        # Helper function to check if a position is stable
        def is_stable(r, c):
            if (r, c) in [(0, 0), (0, 7), (7, 0), (7, 7)]:  # Corners are always stable
                return True
            # Check if the piece is part of a stable line (horizontal, vertical, or diagonal)
            directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
            for dr, dc in directions:
                if all(0 <= r + i*dr < 8 and 0 <= c + i*dc < 8 and board[r + i*dr][c + i*dc] == board[r][c] for i in range(-7, 8)):
                    return True
            return False

        for r in range(8):
            for c in range(8):
                if board[r][c] == 0:
                    continue
                
                value = piece_weight
                if (r, c) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                    value = corner_weight
                elif (r, c) in [(0, 1), (1, 0), (0, 6), (1, 7), (6, 0), (7, 1), (6, 7), (7, 6)]:
                    value = near_corner_weight
                elif r in [0, 7] or c in [0, 7]:
                    value = edge_weight
                
                if is_stable(r, c):
                    value += stability_weight

                if board[r][c] == 1:
                    score += value
                else:
                    score -= value

        # Mobility score
        score += (ai_moves - opponent_moves) * mobility_weight

        return score

    def iterative_deepening_alpha_beta(board, max_time):
        nonlocal nodes_generated, max_depth_reached
        best_move = None
        depth = 1
        prev_score = None
        score_stability_count = 0
        required_stability = 3  # Number of stable scores required

        while time.time() - start_time < max_time:
            try:
                score, move = alpha_beta(board, depth, -math.inf, math.inf, True, start_time + max_time)
                if move:
                    best_move = move
                max_depth_reached = depth

                # Check if the score has stabilized
                if prev_score is not None and abs(score - prev_score) < 0.01:
                    score_stability_count += 1
                else:
                    score_stability_count = 0

                prev_score = score

                # If score has been stable for required number of iterations, break early
                if score_stability_count >= required_stability:
                    logger.info(f"Score stabilized at depth {depth}. Breaking early.")
                    break

                # Break if we've reached a satisfactory depth based on game phase
                if is_satisfactory_depth(board, depth):
                    logger.info(f"Satisfactory depth {depth} reached. Breaking early.")
                    break

                depth += 1
            except TimeoutError:
                break
        
        logger.info(f"Max depth reached: {max_depth_reached}")
        logger.info(f"Total nodes generated: {nodes_generated}")
        return best_move

    def is_satisfactory_depth(board, depth):
        empty_squares = sum(row.count(0) for row in board)
        if empty_squares >= 50:  # Early game
            return depth >= 6
        elif 20 <= empty_squares < 50:  # Mid game
            return depth >= 8
        else:  # Late game
            return depth >= 10

    def alpha_beta(board, depth, alpha, beta, maximizing_player, end_time):
        nonlocal nodes_generated
        nodes_generated += 1
        
        if time.time() > end_time:
            raise TimeoutError("Time limit reached")
        
        if depth == 0 or not get_valid_moves(board, 1) and not get_valid_moves(board, -1):
            return evaluate_board(board), None

        if maximizing_player:
            max_eval = -math.inf
            best_move = None
            moves = get_valid_moves(board, 1)
            # Sort moves to prioritize those that limit opponent's options
            moves.sort(key=lambda move: -len(get_valid_moves(make_move(board, move[0], move[1], 1), -1)))
            for move in moves:
                new_board = make_move(board, move[0], move[1], 1)
                eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, False, end_time)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            best_move = None
            for move in get_valid_moves(board, -1):
                new_board = make_move(board, move[0], move[1], -1)
                eval, _ = alpha_beta(new_board, depth - 1, alpha, beta, True, end_time)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_opening_move(board, end_time):
        if time.time() > end_time:
            raise TimeoutError("Time limit reached")
        
        # Define preferred opening moves
        opening_moves = [
            (2, 3), (3, 2), (4, 5), (5, 4),  # X square moves
            (2, 2), (2, 5), (5, 2), (5, 5)   # C square moves
        ]
        
        for move in opening_moves:
            if is_valid_move(board, move[0], move[1], 1):
                return move
        
        return None

    # Check if it's an early game state (less than 10 pieces on the board)
    total_pieces = sum(row.count(1) + row.count(-1) for row in board)
    
    if total_pieces < 10:
        try:
            opening_move = get_opening_move(board, start_time + max_time)
            if opening_move:
                return list(opening_move)
        except TimeoutError:
            pass  # Fall through to iterative deepening if timeout occurs

    best_move = iterative_deepening_alpha_beta(board, max_time)
    logger.info(f"Time taken: {time.time() - start_time:.2f} seconds")
    return list(best_move) if best_move else None

# Example usage:
# ... (same as shallowbrain2)
