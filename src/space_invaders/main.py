from SpaceInvaders import SpaceInvaders
from generate import (
    gen_num_enemies_on_row_qa, gen_num_enemies_on_col_qa,
    gen_total_num_enemies_qa, gen_num_color_enemies_qa,
    gen_shoot_here_gain_points_qa,
    gen_move_and_shoot_gain_points_qa,
    gen_continual_shoot_here_gain_points_qa,
    gen_move_shoot_once_max_points_qa,
    gen_move_shoot_twice_max_points_qa,
)
from typing import Literal
from tqdm import tqdm
from copy import deepcopy
import random
import json
import os
import argparse

tasks = [
    (1, 'Ask the number of enemies in a row', gen_num_enemies_on_col_qa),
    (2, 'Ask the number of enemies in a column', gen_num_enemies_on_row_qa),
    (3, 'Ask the total number of enemies', gen_total_num_enemies_qa),
    (4, 'Ask the number of enemies with a specific color', gen_num_color_enemies_qa),
    (5, 'Ask the points gained by shooting once where the ship is', gen_shoot_here_gain_points_qa),
    (6, 'Ask the points gained by moving to a given column and shooting once', gen_move_and_shoot_gain_points_qa),
    (7, 'Ask the points gained by continually shooting where the ship is with the enemies keeping on moving', gen_continual_shoot_here_gain_points_qa),
    (8, 'Ask the maximum points gained by shooting once', gen_move_shoot_once_max_points_qa),
    (9, 'Ask the maximum points gained by shooting twice', gen_move_shoot_twice_max_points_qa),
]

# Note: `pad_col_num` should be greater than zero; `enemy_area_rows` should be greater than than `enemy_rows`
params_range = {
    'Easy': {'enemy_rows': [3], 'enemy_cols': [4, 5], 'pad_col_num': [1, 2], 'enemy_area_rows': [5, 6]},
    'Medium': {'enemy_rows': [4], 'enemy_cols': [6, 7, 8], 'pad_col_num': [2], 'enemy_area_rows': [6, 7]},
    'Hard': {'enemy_rows': [5], 'enemy_cols': [9, 10, 11], 'pad_col_num': [2, 3], 'enemy_area_rows': [7, 8]}
}

def generate_datasets(
    num_qa: int,
    # q_type: Literal['fill', 'choice'],
    game_scene_level_dist: list,
    output_dir: str = 'space_invaders_dataset',
    cover_exist: bool = False
):
    '''Generate dataset for Space Invaders game
    Args:
        num_qa: number of questions to generate
        game_scene_level_dist: distribution of questions among levels
        output_dir: output directory
        cover_exist: whether to overwrite if output directory exists
    '''
    print('============= Generating dataset for Space Invaders game =============')
    print(f'num_qa: {num_qa}')
    print(f'game_scene_level_dist: {game_scene_level_dist}')    
    print(f'output_dir: {output_dir}')
    print(f'cover_exist: {cover_exist}')
    
    if os.path.exists(output_dir):
        if cover_exist:
            os.system(f'rm -rf {output_dir}')
        else:
            index = 1
            while os.path.exists(f'{output_dir}_{index}'):
                index += 1
            output_dir = f'{output_dir}_{index}'
    os.makedirs(output_dir)

    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'states'), exist_ok=True)

    one_scene_qas = 9 # number of questions in one scene, which is the same as the length of tasks

    level_qa_num = [int(num_qa * dist / sum(game_scene_level_dist)) for dist in game_scene_level_dist]
    
    level_qa_num[-1] = num_qa - sum(level_qa_num[:-1])
    level_qa_num = {level: num for level, num in zip(['Easy', 'Medium', 'Hard'], level_qa_num)}

    fill_data = []
    choice_data = []
    game_id = 0
    tot = 0
    for level in ['Easy', 'Medium', 'Hard']:
        for i in tqdm(range(level_qa_num[level]), desc=f'Generating plot_level={level}'):
            if i % one_scene_qas == 0:
                params = deepcopy(params_range[level])
                for key, values in params.items():
                    params[key] = random.choice(values)            
                game = SpaceInvaders(**params)
                while len(game.enemies) < 2:
                    game = SpaceInvaders(**params)
                game_id += 1
                game.draw_scene(
                    with_grid_line=True,
                    output_path=os.path.join(output_dir, 'images', f'space_invaders_{game_id:05d}.png')
                )
                with open(os.path.join(output_dir, 'states', f'space_invaders_{game_id:05d}.json'), 'w') as f:
                    json.dump(game.dump_dict(), f, indent=4, ensure_ascii=False)
              
            for q_type in ['fill', 'choice']:
                question_id, question_desc, func = tasks[i % one_scene_qas]
                if func == gen_num_color_enemies_qa:
                    color = random.choice(['purple', 'blue', 'green'])
                    qa = func(game, color, q_type)
                else:
                    qa = func(game, q_type)

                sample = {
                    'data_id': f'space_invaders-{"mcq" if q_type == "choice" else "fill"}-{tot+1:05d}',
                    'question_id': question_id,
                    'question_description': question_desc,
                    'image': f'images/space_invaders_{game_id:05d}.png',
                    'state': f'states/space_invaders_{game_id:05d}.json',
                    'plot_level': level,
                }
                sample.update(qa)
                
                sample = {
                    key: sample[key] for key in [
                        'data_id', 'qa_type', 'question_id', 'question_description', 'image', 'state', 'plot_level', 'qa_level', 'question', 'answer', 'analysis', 'options'
                        ] if key in sample
                }

                if q_type == 'fill':
                    fill_data.append(sample)
                else:
                    choice_data.append(sample)

            tot += 1

    with open(os.path.join(output_dir, 'fill_dataset.json'), 'w') as f:
        json.dump(fill_data, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, 'mcq_dataset.json'), 'w') as f:
        json.dump(choice_data, f, indent=4, ensure_ascii=False)

    data = fill_data + choice_data
    with open(os.path.join(output_dir, 'data.json'), 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
def parse_args():
    parser = argparse.ArgumentParser(description='Generate dataset for Space Invaders game')
    parser.add_argument('--num-qa', type=int, required=True, help='Number of QA pairs to generate')
    parser.add_argument('--scene-level-dist', type=float, nargs=3, default=[5, 3, 2], help='Distribution ratios of three scene difficulty levels, default: [5, 3, 2]')
    parser.add_argument('--output-dir', type=str, default='space_invaders_dataset', help='Output directory path')
    parser.add_argument('--cover-exist', action='store_true', help='Whether to overwrite if output directory exists')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    generate_datasets(
        num_qa=args.num_qa,
        game_scene_level_dist=args.scene_level_dist,
        output_dir=args.output_dir,
        cover_exist=args.cover_exist
    )