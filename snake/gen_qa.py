import random
import numpy as np
from snake import SnakeGame
import os
import json

seed=42
random.seed(seed)
np.random.seed(seed)

qa_types=['head_pos','food_pos','snake_len','which_happen','path']
qa_levels=['Easy','Easy','Medium','Hard','Hard']
rule_prompt='This is a Snake game. The yellow block is the head of the snake. The blue block is the body of the snake. The red block is the food. The coordinates (x, y) in the grid represent the matrix format, where x is the row index and y is the column index. The origin (0,0) is in the the upper left of the grid. You need to control the snake that moves across the grid. Each step it can move up, down, right or left. The game ends if the snake head hits the bound of the grid or its own body. '
que_prompts=[
    'Where is the head of the snake?',
    'Where is the food?',
    'How long is the snake?',
    'Which will happen until this process ends if the snake moves like this each step: ',
    'How long is the shortest path if the snake wants to reach the food? If there is no path, print -1.'
]
real_qa_types=['Target Perception','Target Perception','Target Perception','State Prediction','Strategy Optimization']

def generate_moves(length,head,neck):
    pos2dir={
        (-1,0):'up',
        (0,1):'right',
        (1,0):'down',
        (0,-1):'left'
    }
    directions = ['up', 'right', 'down', 'left']
    moves = []
    last_move = pos2dir[(head[0]-neck[0],head[1]-neck[1])]
    print('last move: ',last_move)
    
    for _ in range(length):
        # 根据上一个移动过滤掉不允许的方向
        valid_moves = directions.copy()
        if last_move == 'up':
            valid_moves.remove('down')
        elif last_move == 'down':
            valid_moves.remove('up')
        elif last_move == 'left':
            valid_moves.remove('right')
        elif last_move == 'right':
            valid_moves.remove('left')
            
        # 随机选择一个有效移动
        move = random.choice(valid_moves)
        moves.append(move)
        last_move = move
        
    return moves

def gen_qa(id,type_id):
    #type_id=random.randint(0,4)
    print(type_id)
    qa_type=qa_types[type_id]
    real_qa_type=real_qa_types[type_id]
    qa_level=qa_levels[type_id]
    data_id=f'snake-{id}-{qa_type}'
    que_prompt=que_prompts[type_id]
    image_path=f'images/snake_{id}.png'
    state_path=f'states/snake_{id}.json'

    plot_id=random.randint(1,3)
    plot=plot_id*5
    if plot==5:
        plot_level='Easy'
    elif plot==10:
        plot_level='Medium'
    else:
        plot_level='Hard'
    game=SnakeGame(width=plot, height=plot, snake_length=random.randint(10,20))
    map=game.board
    head_pos=game.snake[0]
    neck_pos=game.snake[1]
    snake=game.snake
    food_pos=game.food
    
    snake_len=len(game.snake)
    game.draw(image_path='snake_dataset/'+image_path)
    path=game.find_path()
    path_len=-1 #-1代表无法到达
    if path:
        print(f"找到最短路径：{','.join(path)}")
        path_len=len(path)
        print(f"路径长度：{path_len}步")
    

    print(map)
    print('head: ',head_pos)
    print('food: ',food_pos)
    print('path_len: ',path_len)
    print('path: ',path)

    state={'map':map.astype(np.int8).tolist()}
    with open('snake_dataset/'+state_path,'w') as f:
        json.dump(state,f)

    if type_id==0:
        question=rule_prompt+que_prompt
        answer=str(head_pos)
        analysis=f'The head is the yellow block, and the yellow block is at {head_pos}. Thus, the answer is {head_pos}.'
    elif type_id==1:
        question=rule_prompt+que_prompt
        answer=str(food_pos)
        analysis=f'The food is the red block, and the red block is at {food_pos}. Thus, the answer is {food_pos}.'
    elif type_id==2:
        question=rule_prompt+que_prompt
        answer=snake_len
        analysis=f'The head(yellow) block is at {head_pos} and the body(blue) blocks are at {snake[1:]}. The total number of these blocks is {snake_len}. Thus, the length is {snake_len}.'
    elif type_id==3:
        '''
        dir_symbols = ['up', 'right', 'down', 'left']
        move_len=random.randint(1,10)
        moves=np.random.randint(0,4,size=(move_len)).tolist()
        moves=[dir_symbols[move] for move in moves]
        '''
        move_len=random.randint(1,10)
        moves=generate_moves(move_len,head_pos,neck_pos)
        answer,analysis=game.simulate_path(moves)
        print(analysis)
        options=[
            'The snake hits the bound of the grid.',
            'The snake hits its body.',
            'The snake reaches the food.',
            'Nothing happens.'
        ]
        new_moves=''
        for i,move in enumerate(moves):
            new_moves+=f'\nstep {i+1}: '+move
        question=rule_prompt+que_prompt+new_moves+'\nOptions:?\n0: The snake hits the bound of the grid.\n1: The snake hits its body.\n2: The snake reaches the food.\n3: Nothing happens.'
    elif type_id==4:
        question=rule_prompt+que_prompt
        answer=path_len
        #analysis=game.simulate_path(path)
        if path:
            _,sim=game.simulate_path(path)
            analysis='It can move like this: '+sim+f'. Thus, the length is {path_len}'
        else:
            analysis='No path!'

    #with open('snake_dataset_example/data.json','w') as f:
    type_id=int(type_id)

    if type_id==3:
        dataset={
            'data_id':data_id,
            'qa_type':real_qa_type,
            'question_id':type_id,
            'question_description':que_prompts[type_id],
            'image':image_path,
            'state':state_path,
            'plot_level':plot_level,
            'qa_level':qa_level,
            'question':question,
            'answer':answer,
            'analysis':analysis,
            'options':options,
        }
    else:
        dataset={
            'data_id':data_id,
            'qa_type':real_qa_type,
            'question_id':type_id,
            'question_description':que_prompts[type_id],
            'image':image_path,
            'state':state_path,
            'plot_level':plot_level,
            'qa_level':qa_level,
            'question':question,
            'answer':answer,
            'analysis':analysis,
        }
    return dataset

os.makedirs('snake_dataset/images', exist_ok=True)
os.makedirs('snake_dataset/states', exist_ok=True)

qa_num=20
type_ids=np.repeat(np.arange(5), qa_num//5)
np.random.shuffle(type_ids)
datasets=[]
for i in range(qa_num):
    datasets+=[gen_qa(i,type_ids[i])]

with open('snake_dataset/data.json','w') as f:
    json.dump(datasets, f, indent=4)