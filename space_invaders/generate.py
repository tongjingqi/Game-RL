from SpaceInvaders import SpaceInvaders
from utils.gen_chocies import (
    form_options,
    gen_consecutive_int_options,
    gen_consecutive_five_multiple_options,
    gen_consecutive_ten_multiple_options,
)
from utils.calculation import (
    form_addition_formula,
    enumerate_items,
)
from utils.constants import (
    INSTRUCTION_TO_GIVE_OPTION_NUM,
    SPACE_INVADERS_GAME_DESCR_GENERAL,
    SHIP_SHOOT_DESCR,
    SPACE_INVADERS_TIMES_SEQ_RULES,
)
from typing import Literal
import random

def gen_num_enemies_on_row_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the number of enemies on a randomly selected row.'''

    row = game.weight_select_row(faver_weight=0.75)
    num = len(game.enemies_on_row[row]) if row in game.enemies_on_row else 0

    question = SPACE_INVADERS_GAME_DESCR_GENERAL
    question += f'How many enemies are on row {row}? '
    if num > 0:
        analysis = f'It can be seen from the image that on row {row}, {"enemies are present on columns" if num > 1 else "an enemy is present on column"} {enumerate_items([enemy.col for enemy in game.enemies_on_row[row]], conj="and")}. So the number is {num}. '
    else:
        analysis = f'As can be seen from the image, there is no enemy on row {row}. So the number is 0. '

    if q_type == 'fill':
        return {
            'qa_level': 'Easy',
            'qa_type': 'StateInfo', 'question': question, 'answer': num,
            'analysis': analysis,
        }
    else:
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        options = gen_consecutive_int_options(num, total=8)
        question += form_options(options)
        analysis += f'The option number is {options.index(num)+1}.'
        return {
            'qa_level': 'Easy',
            'qa_type': 'StateInfo', 'question': question, 'answer': options.index(num) + 1,
            'analysis': analysis,
            'options': options,
        }

def gen_num_enemies_on_col_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the number of enemies on a randomly selected column.'''

    col = game.weight_select_col(favar_weight=0.75)
    num = len(game.enemies_on_col[col]) if col in game.enemies_on_col else 0

    question = SPACE_INVADERS_GAME_DESCR_GENERAL
    question += f'How many enemies are on column {col}? '
    if num > 0:
        analysis = f'It can be seen from the image that on column {col}, {"enemies are present on rows" if num > 1 else "an enemy is present on row"} {enumerate_items([enemy.row for enemy in game.enemies_on_col[col]], conj="and")}. So the number is {num}. '
    else:
        analysis = f'As can be seen from the image, there is no enemy on column {col}. So the number is 0. '

    if q_type == 'fill':
        return {
            'qa_level': 'Easy',
            'qa_type': 'StateInfo', 'question': question, 'answer': num,
            'analysis': analysis,
        }
    else:
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        options = gen_consecutive_int_options(num, total=8)
        question += form_options(options)
        analysis += f'The option number is {options.index(num)+1}.'
        return {
            'qa_level': 'Easy',
            'qa_type': 'StateInfo', 'question': question, 'answer': options.index(num) + 1,
            'analysis': analysis,
            'options': options,
        }
        
def gen_total_num_enemies_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the total number of enemies in the game.'''

    num = len(game.enemies)
    question = SPACE_INVADERS_GAME_DESCR_GENERAL
    question += 'How many enemies are there in total? '
    enemy_num_list = []
    analysis = ''
    for row in game.enemies_on_row.keys():
        analysis += f'- On row {row}, there {"are" if len(game.enemies_on_row[row]) > 1 else "is"} {len(game.enemies_on_row[row])} {"enemies" if len(game.enemies_on_row[row]) > 1 else "enemy"}.\n'
        enemy_num_list.append(len(game.enemies_on_row[row]))
    analysis += '\n'
    analysis += f'Therefore, there {"are" if num > 1 else "is"} {form_addition_formula(enemy_num_list)} {"enemies" if num > 1 else "enemy"} in total. '

    if q_type == 'fill':
        return {
            'qa_level': 'Medium',
            'qa_type': 'StateInfo', 'question': question, 'answer': num,
            'analysis': analysis,
        }
    else:
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        options = gen_consecutive_int_options(num, total=8)
        question += form_options(options)
        analysis += f'The option number is {options.index(num)+1}.'
        return {
            'qa_level': 'Medium',
            'qa_type': 'StateInfo', 'question': question, 'answer': options.index(num) + 1,
            'analysis': analysis,
            'options': options,
        }
    
def gen_num_color_enemies_qa(game: SpaceInvaders, color: Literal['purple', 'blue', 'green'], q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the number of enemies with a specific color in the game.'''

    type = 1 if color == 'purple' else 2 if color == 'blue' else 3
    
    question = SPACE_INVADERS_GAME_DESCR_GENERAL
    question += f'How many {color} enemies are there in total? '
    enemy_num_list = []
    analysis = ''
    for row in game.enemies_on_row.keys():
        if game.enemies_on_row[row][0].type != type:
            continue
        analysis += f'- On row {row}, there {"are" if len(game.enemies_on_row[row]) > 1 else "is"} {len([enemy for enemy in game.enemies_on_row[row] if enemy.type == type])} {color} {"enemies" if len([enemy for enemy in game.enemies_on_row[row] if enemy.type == type]) > 1 else "enemy"}.\n'
        enemy_num_list.append(len([enemy for enemy in game.enemies_on_row[row] if enemy.type == type]))
    analysis += '\n'
    analysis += f'Therefore, there {"are" if len(enemy_num_list) > 1 else "is"} {form_addition_formula(enemy_num_list)} {color} {"enemies" if len(enemy_num_list) > 1 else "enemy"} in total. '
    num = sum(enemy_num_list)
    
    if q_type == 'fill':
        return {
            'qa_level': 'Medium',
            'qa_type': 'StateInfo', 'question': question, 'answer': num,
            'analysis': analysis,
        }
    else:
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        options = gen_consecutive_int_options(num, total=8)
        question += form_options(options)
        analysis += f'The option number is {options.index(num)+1}.'
        return {
            'qa_level': 'Medium',
            'qa_type': 'StateInfo', 'question': question, 'answer': options.index(num) + 1,
            'analysis': analysis,
            'options': options,
        }

def gen_shoot_here_gain_points_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the points gained by shooting once at the current position.'''

    question = SPACE_INVADERS_GAME_DESCR_GENERAL + SHIP_SHOOT_DESCR
    question += 'If the ship shoots at the current position, how many points will the player get? '
    analysis = f'As can be seen from the image, the ship is on column {game.ship_x}. '

    score, col = 0, game.ship_x
    if col in game.enemies_on_col:
        hit_enemy_row, color, score = game.enemies_on_col[col][-1].row, game.enemies_on_col[col][-1].color, game.enemies_on_col[col][-1].score
    if score > 0:
        analysis += f'And The enemy closest to the ship on this column is on row {hit_enemy_row}, which is {color}. '
        analysis += f'Therefore, the player will get {score} points if the ship shoots at the current position. '
    else:
        analysis += 'But There is no enemy on this column. '
        analysis += 'So the player will get 0 points if the ship shoots at the current position. '

    if q_type == 'choice':
        options = [10, 20, 30, 0]
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        question += form_options(options)
        analysis += f'The option number is {options.index(score)+1}.'
    
    ret = {
        'qa_level': 'Easy',
        'qa_type': 'ActionOutcome', 'question': question, 'answer': score,
        'analysis': analysis,
    }
    if q_type == 'choice':
        ret['answer'] = options.index(score) + 1
        ret['options'] = options
    return ret

def gen_move_and_shoot_gain_points_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the points gained by moving to a specific column and shooting once.'''
    
    question = SPACE_INVADERS_GAME_DESCR_GENERAL + SHIP_SHOOT_DESCR
    nxt_col = game.weight_select_col_to_move_to(game.ship_x)
    question += 'Suppose that all the enemies keep still. '
    question += f'If the ship moves to column {nxt_col} and shoots, how many points will the player get? '
    
    if nxt_col in game.enemies_on_col:
        enemy = game.enemies_on_col[nxt_col][-1]
        row, score, color = enemy.row, enemy.score, enemy.color
        analysis = f'The lowermost enemy on column {nxt_col} is on row {row}, which is {color}. '
        analysis += f'Therefore, the player will get {score} points if the ship moves to column {nxt_col} and shoots. '
    else:
        score = 0
        analysis = f'As can be seen from the image, there is no enemy on column {nxt_col}. '
        analysis += f'So the player will get 0 points if the ship moves to column {nxt_col} and shoots. '

    if q_type == 'choice':
        options = [0, 10, 20, 30]
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        question += form_options(options)
        analysis += f'The option number is {options.index(score)+1}.'
    ret = {
        'qa_level': 'Easy',
        'qa_type': 'ActionOutcome', 'question': question, 'answer': score,
        'analysis': analysis,
    }
    if q_type == 'choice':
        ret['answer'] = options.index(score) + 1
        ret['options'] = options
    return ret

def gen_continual_shoot_here_gain_points_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the points gained by shooting here continually during some time intervals.'''
    
    question = SPACE_INVADERS_GAME_DESCR_GENERAL + SHIP_SHOOT_DESCR + SPACE_INVADERS_TIMES_SEQ_RULES 

    ld = game.left_distance_to_border()
    rd = game.right_distance_to_border()
    if ld == 0:
        dir, dir_descr = 1, 'right' 
        delta_time = random.randint(1, min(rd, 4)) 
    elif rd == 0:
        dir, dir_descr = -1, 'left'
        delta_time = random.randint(1, min(ld, 4))
    else:
        dir = random.choice([-1, 1])
        dir_descr = 'left' if dir == -1 else 'right'
        d = ld if dir == -1 else rd
        delta_time = random.randint(1, min(d, 4))

    question += f'Given that the image depicts the scene at the beginning of time interval t, and the enemies keep on moving {dir_descr}.\n'
    question += f'How many points will the player get in total at the end of time interval t+{delta_time} if the ship stays at the current position and shoots once during each time interval? '
    col_ids = []
    for i in range(delta_time+1):
        if game.ship_x - dir * i <= 0 or game.ship_x - dir * i > game.total_columns:
            break
        col_ids.append(game.ship_x - dir * i)
    
    analysis = f'''As can be seen from the image, the ship is on column {game.ship_x}. It keeps still and shoots once during each time interval while the enemies move {dir_descr}.
Thus equivalently, in the current scene, there will be laser attacks from the ship on columns {enumerate_items(col_ids, conj="and")}. Let's check points gained on these columns one by one.
'''
    points = []
    for col in col_ids:
        if col in game.enemies_on_col:
            enemy = game.enemies_on_col[col][-1]
            row, score, color = enemy.row, enemy.score, enemy.color
            analysis += f'- Column {col}: The lowermost enemy is on row {row}, which is {color}, adding {score} points.\n'
            points.append(score)
        else:
            analysis += f'- Column {col}: There is no enemy. No points are added.\n'
            points.append(0)
    analysis += f'\nSo finally the player will get {form_addition_formula(points)} points at the end of time interval t+{delta_time}. '
    score = sum(points)
    
    if q_type == 'choice':
        options = gen_consecutive_ten_multiple_options(score, total=8) if random.random() < 0.8 else gen_consecutive_five_multiple_options(score, total=8)
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        question += form_options(options)
        analysis += f'The option number is {options.index(score)+1}.'
    ret = {
        'qa_level': 'Hard',
        'qa_type': 'ActionOutcome', 'question': question, 'answer': score,
        'analysis': analysis,
    } 
    if q_type == 'choice':
        ret['answer'] = options.index(score) + 1
        ret['options'] = options
    return ret

def gen_move_shoot_once_max_points_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the maximum points gained by shooting once.'''
    
    question = SPACE_INVADERS_GAME_DESCR_GENERAL + SHIP_SHOOT_DESCR + SPACE_INVADERS_TIMES_SEQ_RULES
    question += f'Given that the image depicts the scene at the beginning of time interval t, during which the enemies keep still.\n'
    question += 'What is the maximum number of points the player can get if he can move the ship to any column and let the ship shoot? '
    
    analysis = "Since the ship can move to any column and shoot, we just need to find the enemy with the highest score among all the ones being the lowermost on their columns. Let's check the columns one by one.\n" 
    max_score = 0
    for col in range(1, game.total_columns+1):
        if col in game.enemies_on_col:
            enemy = game.enemies_on_col[col][-1]
            row, score, color = enemy.row, enemy.score, enemy.color
            analysis += f'- Column {col}: The lowermost enemy is on row {row}, which is {color} and worth {score} points.\n'
            max_score = max(max_score, score)
        else:
            analysis += f'- Column {col}: There is no enemy.\n' 

    if max_score == 0:
        analysis += 'So the maximum number of points the player can get is 0. '
    else:
        col_ids = []
        for col in range(1, game.total_columns+1):
            if col in game.enemies_on_col and game.enemies_on_col[col][-1].score == max_score:
                col_ids.append(col)

        analysis += f'\nTherefore, the maximum number of points the player can get is {max_score}, which can be achieved by letting the ship shoot on column {enumerate_items(col_ids, conj="or")}. '
        
    if q_type == 'choice':
        options = gen_consecutive_ten_multiple_options(max_score, total=8) if random.random() < 0.2 else gen_consecutive_five_multiple_options(max_score, total=8)
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        question += form_options(options)
        analysis += f'The option number is {options.index(max_score)+1}.'
    ret = {
        'qa_level': 'Medium',
        'qa_type': 'StrategyOptimization', 'question': question, 'answer': max_score,
        'analysis': analysis,
    }
    if q_type == 'choice':
        ret['answer'] = options.index(max_score) + 1
        ret['options'] = options
    return ret
    
def gen_move_shoot_twice_max_points_qa(game: SpaceInvaders, q_type: Literal['fill', 'choice']) -> dict:
    '''Generate question, answer and reasoning for the maximum points gained by shooting twice.'''
    
    ld = game.left_distance_to_border()
    rd = game.right_distance_to_border()
    dir_descr = 'right' if ld == 0 else 'left' if rd == 0 else random.choice(['left', 'right'])

    question = SPACE_INVADERS_GAME_DESCR_GENERAL + SHIP_SHOOT_DESCR + SPACE_INVADERS_TIMES_SEQ_RULES
    question += f'Given that the image depicts the scene at the beginning of time interval t, and the enemies keep on moving {dir_descr}.\n'
    question += 'What is the maximum number of points the player can at the end of time interval t+1?'
    analysis = f'According to the rules and the question, the ship can shoot twice. Besides, since the ship can move to any column, the movement of the enemies does not really matter, and we just need to consider shooting twice in the current scene.\n'
    analysis += "Furthermore, there's two cases: the ship can shoot twice on the same column or on different columns. Let's consider these two cases one by one.\n"

    analysis += 'Case 1. The ship shoots twice on the same column. Two lowermost enemies on one column can be destroyed. Check the columns one by one:\n'
    max_score1 = 0
    for col in range(1, game.total_columns+1):
        if col not in game.enemies_on_col:
            analysis += f'- Column {col}: There is no enemy.\n'
            continue
        elif len(game.enemies_on_col[col]) == 1:
            analysis += f'- Column {col}: There is only one enemy.\n'
            continue
        else:
            enemy1, enemy2 = game.enemies_on_col[col][-1], game.enemies_on_col[col][-2]
            row1, row2 = enemy1.row, enemy2.row
            score1, score2 = enemy1.score, enemy2.score
            color1, color2 = enemy1.color, enemy2.color
            analysis += f'- Column {col}: The lowermost enemy is on row {row1}, which is {color1} and worth {score1} points. The second lowermost enemy is on row {row2}, which is {color2} and worth {score2} points. {score1+score2} points can be gained.\n'
            max_score1 = max(score1 + score2, max_score1)
    analysis += f'\nSo in this case, the maximum number of points the player can get is {max_score1}.\n' if max_score1 > 0 else 'So in this case is impossible here.\n'

    analysis += '\nCase 2. The ship shoots twice on different columns. Two lowermost enemies on two different columns can be destroyed. Check the columns one by one:\n'
    points = []
    for col in range(1, game.total_columns+1):
        if col not in game.enemies_on_col:
            analysis += f'- Column {col}: There is no enemy.\n'
            continue
        else:
            enemy = game.enemies_on_col[col][-1]
            row, score, color = enemy.row, enemy.score, enemy.color
            analysis += f'- Column {col}: The lowermost enemy is on row {row}, which is {color} and worth {score} points.\n'
            points.append(score)
    max_score2 = 0
    if len(points) < 2:
        analysis += '\nSo this case is impossible here.\n'
    else:
        points = sorted(points, reverse=True)[:2]
        analysis += f'\nThe highest two scores are {points[0]} and {points[1]}. So {form_addition_formula(points)} points can be gained.\n'
        max_score2 = sum(points)

    sign = '<' if max_score1 < max_score2 else '>' if max_score1 > max_score2 else '='
    score = max(max_score1, max_score2)
    analysis += f'\nSince {max_score1} {sign} {max_score2}, the maximum number of points the player can get is {score}. ' if max_score1 > 0 and max_score2 > 0 else f'\nTherefore, the maximum number of points the player can get is {score}. '
     
    if q_type == 'choice':
        options = gen_consecutive_ten_multiple_options(score, total=8) if random.random() < 0.2 else gen_consecutive_five_multiple_options(score, total=8)
        question += INSTRUCTION_TO_GIVE_OPTION_NUM
        question += form_options(options)
        analysis += f'The option number is {options.index(score)+1}.'
    ret = {
        'qa_level': 'Hard',
        'qa_type': 'StrategyOptimization', 'question': question, 'answer': score,
        'analysis': analysis,
    }
    if q_type == 'choice':
        ret['answer'] = options.index(score) + 1
        ret['options'] = options
    return ret
