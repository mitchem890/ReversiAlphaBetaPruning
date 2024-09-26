import logging
from flask import Flask, render_template, request, jsonify
from app.shallowBrain import get_best_move as shallow_best_move

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

@app.route('/ai_move', methods=['POST'])
def ai_move():
    logger.info("Received request for AI move")
    board = request.json['board']
    ai_color = request.json['aiColor']
    ai_type = request.json['aiType']
    
    logger.debug(f"Board state: {board}")
    logger.debug(f"AI color: {ai_color}")
    logger.debug(f"AI type: {ai_type}")
    
    # Ensure the board is 8x8
    if len(board) != 8 or any(len(row) != 8 for row in board):
        logger.error("Invalid board size")
        return jsonify({'error': 'Invalid board size'}), 400
    
    if ai_type == 'shallow':
        logger.info("Calculating move using ShallowBrain")
        row, col = shallow_best_move(board, ai_color)
        logger.info(f"ShallowBrain chose move: ({row}, {col})")
    else:
        logger.error(f"Invalid AI type: {ai_type}")
        return jsonify({'error': 'Invalid AI type'}), 400
    
    return jsonify({'row': row, 'col': col})

@app.route('/get_ai_move', methods=['POST'])
def get_ai_move():
    logger.info("Received request for AI move (new endpoint)")
    data = request.json
    board = data['board']
    current_player = data['current_player']
    difficulty = data['difficulty']
    
    logger.debug(f"Board state: {board}")
    logger.debug(f"Current player: {current_player}")
    logger.debug(f"Difficulty: {difficulty}")
    
    # Add warning for higher difficulties
    if difficulty >= 4:
        logger.warning(f"High difficulty level ({difficulty}) selected. ShallowBrain may take longer to respond.")
    
    # Use ShallowBrain to calculate the best move
    logger.info("Calculating move using ShallowBrain")
    move = shallow_best_move(board, current_player, max_time=difficulty)
    logger.info(f"ShallowBrain chose move: {move}")
    
    return jsonify({'move': move})

if __name__ == '__main__':
    logger.info("Starting Reversi application")
    app.run(host='0.0.0.0', port=5000)
