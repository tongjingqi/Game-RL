import os
import json
import random
from sokoban import generate_random_board, SokobanBoard
from timeout_utils import timeout, TimeoutError
import datetime
import logging
from textured_sokoban import TexturedSokobanBoard, generate_textured_random_board
# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sokoban_generation.log'),
        logging.StreamHandler()
    ]
)

def get_plot_level_moves(level: int) -> int:
    moves_range = {
        1: 5,  # Easy
        2: 8,  # Medium
        3: 12  # Hard
    }
    return moves_range[level]

@timeout(2)  # 2秒超时
def generate_question_with_timeout(board: SokobanBoard, num_moves: int) -> tuple:
    """带超时的问题生成函数"""
    return board.generate_question(num_moves, 8)

def generate_dataset(num_boards: int, output_dir: str = "sokoban_dataset"):
    """Generate dataset with boards, questions, and solutions."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "states"), exist_ok=True)

    all_data = []
    question_counter = 1
    
    # 记录失败的问题以供后续分析
    failed_questions = []

    for board_id in range(1, num_boards + 1):
        try:
            # Generate board with appropriate difficulty
            plot_level = board_id % 3 + 1
            num_moves = get_plot_level_moves(plot_level)
            num_boxes = random.randint(2, 3) if board_id % 2 == 0 else 1
            
            try:
                board = generate_textured_random_board(size=num_moves, num_boxes=num_boxes, 
                                         check_solvable=num_boxes==1)
            except Exception as e:
                logging.error(f"Failed to generate board {board_id}: {str(e)}")
                continue

            # Save visualization and state
            image_path = f"images/board_{board_id:05d}.png"
            state_path = f"states/board_{board_id:05d}.json"
            
            try:
                board.save_board(os.path.join(output_dir, image_path))
                with open(os.path.join(output_dir, state_path), "w") as f:
                    json.dump(board.get_full_state(), f, indent=4)
            except Exception as e:
                logging.error(f"Failed to save board {board_id}: {str(e)}")
                continue

            # 选择问题类型
            question_ids = [1,4] if num_boxes > 1 else range(1, 7)

            for question_id in question_ids:
                try:
                    qa_type = get_question_type(question_id)
                    
                    # 设置问题类型
                    question_type_mapping = {
                        'ActionOutcome': ['next_position', 'box_position'],
                        'StrategyOptimization': ['steps_to_target'],
                        'StateInfo': ['state_info_player', 'state_info_distance'],
                        'TransitionPath': ['transition_path']
                    }
                    
                    # 选择合适的内部类型
                    if qa_type == 'ActionOutcome':
                        internal_type = question_type_mapping[qa_type][question_id - 1]
                    elif qa_type == 'StrategyOptimization':
                        internal_type = question_type_mapping[qa_type][0]
                    elif qa_type == 'StateInfo':
                        internal_type = question_type_mapping[qa_type][question_id - 4]
                    else:  # TransitionPath
                        internal_type = question_type_mapping[qa_type][0]
                    
                    board.question_types = [internal_type]
                    
                    try:
                        q, analysis, opts, correct = generate_question_with_timeout(board, num_moves)
                    except TimeoutError:
                        logging.warning(f"Question generation timed out for board {board_id}, question {question_id}")
                        failed_questions.append({
                            'board_id': board_id,
                            'question_id': question_id,
                            'reason': 'timeout'
                        })
                        continue
                    except Exception as e:
                        logging.error(f"Failed to generate question for board {board_id}, question {question_id}: {str(e)}")
                        failed_questions.append({
                            'board_id': board_id,
                            'question_id': question_id,
                            'reason': str(e)
                        })
                        continue

                    data_entry = {
                        "data_id": f"sokoban-data-{board_id:05d}-{question_id:05d}",
                        "image": image_path,
                        "state": state_path,
                        "plot_level": "Easy" if plot_level == 1 else ("Medium" if plot_level == 2 else "Hard"),
                        "qa_level": get_difficulty(qa_type),
                        "qa_type": qa_type,
                        "question_id": question_id,
                        "question_description": get_question_description(question_id),
                        "question": q,
                        "answer": correct + 1,
                        "analysis": analysis,
                        "options": opts
                    }
                    
                    all_data.append(data_entry)
                    question_counter += 1

                except Exception as e:
                    logging.error(f"Error in question generation loop for board {board_id}, question {question_id}: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Error in main board generation loop for board {board_id}: {str(e)}")
            continue

    # 保存数据和失败记录
    with open(os.path.join(output_dir, "data.json"), "w") as f:
        json.dump(all_data, f, indent=4)
        
    if failed_questions:
        with open(os.path.join(output_dir, "failed_questions.json"), "w") as f:
            json.dump(failed_questions, f, indent=4)

    logging.info(f"Generated {len(all_data)} questions successfully")
    logging.info(f"Failed to generate {len(failed_questions)} questions")
    
    return all_data

def get_question_type(question_id: int) -> str:
    """Map question ID to question type."""
    type_mapping = {
        1: 'ActionOutcome',
        2: 'ActionOutcome',
        3: 'StrategyOptimization',
        4: 'StateInfo',
        5: 'StateInfo',
        6: 'TransitionPath'
    }
    return type_mapping.get(question_id, 'ActionOutcome')

def get_difficulty(qtype: str) -> str:
    """Return difficulty level for each question type."""
    difficulties = {
        'ActionOutcome': 'Medium',
        'StrategyOptimization': 'Hard', 
        'StateInfo': 'Easy',
        'TransitionPath': 'Hard'
    }
    return difficulties.get(qtype, 'Medium')

def get_question_description(question_id: int) -> str:
    """Get specific description for each question ID."""
    descriptions = {
        1: "Given a sequence of player moves, predict the final position of the player",
        2: "Given a sequence of moves, predict the final position of the box",
        3: "Determine the minimum number of moves needed to solve the puzzle",
        4: "Identify the current position of the player on the board",
        5: "Calculate the Manhattan distance between a box and its target",
        6: "Find the optimal sequence of moves to reach a specific position"
    }
    return descriptions.get(question_id, "")

if __name__ == "__main__":
    dataset = generate_dataset(num_boards=3)
    print(f"Generated {len(dataset)} questions")