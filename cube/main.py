import os
import json
import random
from cube import RubiksCube, generate_random_cube


def get_difficulty2(qtype: int) -> str:
    """Return difficulty level for each question type."""
    difficulties = {
        '1': 'Easy',
        '2': 'Medium',
        '3': 'Hard'
    }
    return difficulties.get(qtype, 'Medium')


def get_plot_level_moves(level: int) -> int:
    """
    Get number of random moves for each plot level.
    Level 1: 0 moves (initial state)
    Level 2: 1 move
    Level 3: 2 moves
  
    """
    moves_range = {
        1: 1,  
        2: 2, 
        3:3, 
        
      
    }
    return moves_range[level]



def get_question_type(question_id: int) -> str:
    """Map question ID to question type."""
    # All questions are mapped to one of four main types
    if question_id in [1, 5, 6]:  # face_recognition, color_count, face_solved
        return "StateInfo"
    elif question_id == 2:
        return "ActionOutcome"
    elif question_id == 3:
        return "TransitionPath"
    elif question_id == 4:
        return "StrategyOptimization"
    
def get_difficulty(qtype: str) -> str:
    """Return difficulty level for each question type."""
    difficulties = {
        'StateInfo': 'Easy',
        'ActionOutcome': 'Medium',
        'TransitionPath': 'Hard',
        'StrategyOptimization': 'Hard'
    }
    return difficulties.get(qtype, 'Medium')

def get_question_description(qtype: str, subtype: str = None) -> str:
    """Get description for each question type."""
    descriptions = {
        'StateInfo': {
            'face_recognition': "Identify colors on specific positions",
            'color_count': "Count specific colors on a face",
            
        },
        'ActionOutcome': "Predict the cube state after performing specific moves",
        'TransitionPath': "Find the sequence of moves between two cube states",
        'StrategyOptimization': "Determine optimal move sequence to solve the cube"
    }
    
    if qtype == 'StateInfo' and subtype:
        return descriptions['StateInfo'][subtype]
    return descriptions.get(qtype, "")

def get_subtype_for_question(question_id: int) -> str:
    """Get the specific subtype for a question ID."""
    subtypes = {
        1: 'face_recognition',
        5: 'color_count',
     
        
    }
    return subtypes.get(question_id)

def generate_dataset(num_cubes: int, output_dir: str = "rubiks_cube_dataset"):
    """Generate dataset with cube states, questions, and solutions."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "states"), exist_ok=True)

    all_data = []
    question_counter = 1

    # Mapping from question types to cube method names
    qa_mapping = {
        'StateInfo': {
            'face_recognition': 'face_recognition',
            'color_count': 'color_count',
            
        },
        'ActionOutcome': 'move_prediction',
        'TransitionPath': 'single_face_solve',
        'StrategyOptimization': 'full_solve'
    }

    for cube_id in range(1, num_cubes + 1):
        try:
            # Generate cube with appropriate difficulty
            plot_level = cube_id % 3 + 1
            num_moves = get_plot_level_moves(plot_level)
            cube = generate_random_cube(num_moves)
            
            # Save visualization and state
            image_path = f"images/cube_{cube_id:05d}.png"
            state_path = f"states/cube_{cube_id:05d}.json"
            
            cube.save_visualization(os.path.join(output_dir, image_path))
            
            with open(os.path.join(output_dir, state_path), "w") as f:
                json.dump(cube.get_full_state(), f, indent=4)

            # Generate all types of questions
            for question_id in range(1, 6):
                qa_type = get_question_type(question_id)
                
                try:
                    # Handle StateInfo questions differently as they have subtypes
                    if qa_type == 'StateInfo':
                        subtype = get_subtype_for_question(question_id)
                        cube_qa_type = qa_mapping[qa_type][subtype]
                        description = get_question_description(qa_type, subtype)
                    else:
                        if (qa_type=='TransitionPath'and plot_level==3) or (qa_type=='StrategyOptimization' and plot_level==3):
                            continue
                        else:
                            cube_qa_type = qa_mapping[qa_type]
                            description = get_question_description(qa_type)
                    
                    q, analysis, opts, correct = cube.generate_question(cube_qa_type)
                    
                    data_entry = {
                        "data_id": f"rubiks_cube-data-{cube_id:05d}-{question_id:05d}",
                        "image": image_path,
                        "state": state_path,
                        "plot_level": get_difficulty2(str(plot_level)),
                        "qa_level": get_difficulty(qa_type),
                        "qa_type": qa_type,
                        "question_id": question_id,
                        "question_description": description,
                        "question": q,
                        "answer": correct + 1,
                        "analysis": analysis,
                        "options": opts
                    }
                    
                    all_data.append(data_entry)
                    question_counter += 1
                    print(qa_type)
                except Exception as e:
                    print(f"Error generating {qa_type} question (ID: {question_id}) for cube {cube_id}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error processing cube {cube_id}: {str(e)}")
            continue

    # Save all data
    with open(os.path.join(output_dir, "data.json"), "w") as f:
        json.dump(all_data, f, indent=4)

    return all_data

if __name__ == "__main__":
    dataset = generate_dataset(num_cubes=116)
    print(f"Generated {len(dataset)} questions")
