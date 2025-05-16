import json
import argparse
import random
import os

from data_generate_aq import generate_data_aq
from data_generate_count import generate_data_count
from data_generate_find import generate_data_find
from data_generate_pos import generate_data_pos
from data_generate_predict import generate_data_predict

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Chess Ranger puzzles and save as JSON files.")
    parser.add_argument('--data_num', type=int, default=100, help='Number of puzzles to generate')
    parser.add_argument('--num_pieces', type=int, default=6, help='Maximum number of pieces in the puzzle')
    parser.add_argument('--max_length', type=int, default=5000, help='Maximum length of analysis')  # 定义 max_length
    args = parser.parse_args()
    return args

# 自定义参数
args = parse_arguments()
data_num = args.data_num  # 从命令行获取生成的数据个数
max_pieces = args.num_pieces  # 从命令行获取最大棋子
max_analysis_len = args.max_length

all_data = []

'''
level_percentage_1 = 0.3
level_percentage_2 = 0.3
level_percentage_3 = 1 - level_percentage_1 - level_percentage_2
'''

# 创建多级文件夹（如果父文件夹不存在则会创建）
os.makedirs('chess_ranger_dataset/images', exist_ok=True)
os.makedirs('chess_ranger_dataset/states', exist_ok=True)

for num in range(1, data_num + 1):  # 循环生成data_num个数据

    '''
    if num/datanum <= level_percentage_1 : num_pieces = 4
    elif level_percentage_1 < num/datanum <= level_percentage_1 + level_percentage_2 : num_pieces = 5
    elif level_percentage_1 + level_percentage_2 < num/datanum <= 1 : num_pieces = 6
    '''

    # 随机选择棋子数量（范围为4到max_pieces之间）
    num_pieces = random.randint(4, max_pieces)

    '''
    if(num <= 5): num_pieces = random.randint(4,5)
    elif(5 < num <= 10): num_pieces = 6
    elif(10 < num <= 15): num_pieces = random.randint(7,8)
    '''

    data_path = "chess_ranger_dataset"
    image_path = f"images/board_{num:03}.png"
    state_path = f"states/board_{num:03}.json"

    opt = num % 3
    if opt == 1:
        data = generate_data_aq(num, num_pieces, data_path, image_path, state_path, max_analysis_len, 100)
    elif opt == 2:
        second_opt = random.randint(1,3)
        if second_opt == 1:
            data = generate_data_count(num, num_pieces, data_path, image_path, state_path)
        elif second_opt == 2:
            data = generate_data_find(num, num_pieces, data_path, image_path, state_path)
        elif second_opt == 3:
            data = generate_data_pos(num, num_pieces, data_path, image_path, state_path)
    elif opt == 0:
        data = generate_data_predict(num, num_pieces, data_path, image_path, state_path, max_analysis_len, 100)

    all_data.append(data)

# 将数据写入 JSON 文件 
with open('chess_ranger_dataset/data.json', 'w') as f:
    json.dump(all_data, f, indent=4)
