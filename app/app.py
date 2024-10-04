import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.serving import run_simple
#from shallowBrain import get_best_move as shallow_best_move
from app.shallowbrain import main as sb1_best_move
from app.shallowbrain2 import alpha_beta_reversi as sb2_best_move
from app.DamonBrain1 import alpha_beta_reversi as damon_best_move

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='./templates')

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('reversi.html')

@app.route('/how_to_play')
def how_to_play():
    logger.info("Serving 'How to Play' page")
    return render_template('HowToPlay.html')

@app.route('/what_is_shallowbrain')
def what_is_shallowbrain():
    logger.info("Serving 'What is ShallowBrain' page")
    return render_template('ShallowBrain.html')


@app.route('/get_ai_move', methods=['POST'])
def get_ai_move():
    logger.info("Received request for AI move (new endpoint)")
    data = request.json
    board = data['board']
    current_player = data['current_player']
    difficulty = data['difficulty']
    ai_version = data['ai_version']
    
    logger.debug(f"Board state: {board}")
    logger.debug(f"Current player: {current_player}")
    logger.debug(f"Difficulty: {difficulty}")
    logger.debug(f"AI Version: {ai_version}")
    #Convert the board to a 2D array of 1 for AI and -1 for human, 0 for empty
    if current_player == 'black':
        user = 'white'
    else:
        user = 'black'
    for i in range(8):
        for j in range(8):
            if board[i][j] == current_player:
                board[i][j] = 1
            elif board[i][j] == user:
                board[i][j] = -1
            else:
                board[i][j] = 0
    # Add warning for higher difficulties
    if difficulty >= 4:
        logger.warning(f"High difficulty level ({difficulty}) selected. ShallowBrain may take longer to respond.")
    
    # Use ShallowBrain to calculate the best move
    logger.info(f"Calculating move using ShallowBrain {ai_version}")
    if ai_version == 1:
        move = sb1_best_move(board, difficulty)
    if ai_version == 2:
        move = sb2_best_move(board, difficulty)
    if ai_version == 3:
        move = damon_best_move(board, difficulty)
    logger.info(f"ShallowBrain {ai_version} chose move: {move}")
    return jsonify({'move': move})

if __name__ == '__main__':
    logger.info("Starting Reversi application")
    run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True, threaded=True, request_timeout=60)
