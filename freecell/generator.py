from freecell import Suit,Color,FreeCell
import random
import os
import json

qa_type=["specified_card","valid_move","card_after_move"]
qa_level={
    "specified_card":"Easy",
    "valid_move":"Medium",
    "card_after_move":"Hard"

}
plot_level_map={
    8:"Easy",
    6:"Medium",
    4:"Hard"
}
value_map={
    1:"A",
    2:"2",
    3:"3",
    4:"4",
    5:"5",
    6:"6",
    7:"7",
    8:"8",
    9:"9",
    10:"10",
    11:"J",
    12:"Q",
    13:"K",
}
suit_to_string_map={
    "♥":"Heart",
    "♦":"Diamond",
    "♣":"Club",
    "♠":"Spade"
}
string_to_suit_map={
    "Heart":"♥",
    "Diamond":"♦",
    "Club":"♣",
    "Spade":"♠"
}
def generate_dataset(num_puzzles,base_path):
    # 创建目录
    os.makedirs(base_path,exist_ok=True)
    os.makedirs(os.path.join(base_path, "images"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "states"), exist_ok=True)

    data_sum_easy,data_specified_card_easy,data_valid_move_easy,data_card_after_move_easy=generate_state_analysis_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=8)
    data_sum_medium,data_specified_card_medium,data_valid_move_medium,data_card_after_move_medium=generate_state_analysis_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=6)
    data_sum_hard,data_specified_card_hard,data_valid_move_hard,data_card_after_move_hard=generate_state_analysis_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=4)

    # data_4=generate_solution_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=8)
    # data_5=generate_solution_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=6)
    # data_6=generate_solution_dataset(num_puzzles=num_puzzles,base_path=base_path,cascade_number=4)

    data_specified_card=data_specified_card_easy+data_specified_card_medium+data_specified_card_hard
    data_valid_move=data_valid_move_easy+data_valid_move_medium+data_valid_move_hard
    data_card_after_move=data_card_after_move_easy+data_card_after_move_medium+data_card_after_move_hard

    specified_card_path=os.path.join(base_path,"specified_card_dataset.json")
    with open(specified_card_path,"w",encoding="utf-8") as f:
        json.dump(data_specified_card,f,ensure_ascii=False,indent=4)
    
    valid_move_path=os.path.join(base_path,"valid_move_dataset.json")
    with open(valid_move_path,"w",encoding="utf-8") as f:
        json.dump(data_valid_move,f,ensure_ascii=False,indent=4)
    
    card_after_move_path=os.path.join(base_path,"card_after_move_dataset.json")
    with open(card_after_move_path,"w",encoding="utf-8") as f:
        json.dump(data_card_after_move,f,ensure_ascii=False,indent=4)

    data=data_sum_easy+data_sum_medium+data_sum_hard
    data_path=os.path.join(base_path,"data.json")
    with open(data_path,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)

# 生成一二三类问题的数据
def generate_state_analysis_dataset(num_puzzles,base_path,cascade_number):
    puzzles_generated = 0
    attempt = 0
    max_attempts = num_puzzles * 10  # Maximum attempts to avoid infinite loops

    specified_card_data=[]
    valid_move_data=[]
    card_after_move_data=[]
    plot_level=plot_level_map[cascade_number]
    while puzzles_generated<num_puzzles and attempt<max_attempts:
        attempt+=1
        game=FreeCell(cascade_number=cascade_number) # 创建游戏
        
        # 保存图片
        image_file=f"images/state_analysis_{plot_level}_{puzzles_generated+1:05d}.png"
        game.visualize(save_path=os.path.join(base_path,image_file))

        # 保存state
        state_file=f"states/state_analysis_{plot_level}_{puzzles_generated+1:05d}.json"
        game_state = {
            "cascade_piles": [[str(card) for card in pile] if pile else None for pile in game.cascade_piles],
            "free_cells": [str(card) if card else None for card in game.free_cells],
            "foundation_piles": {suit.name: [str(card) for card in pile] if pile else None
                             for suit, pile in game.foundation_piles.items()}
        }
        state_path=os.path.join(base_path,state_file)
        with open(state_path, 'w',encoding="utf-8") as f:
            json.dump(game_state, f, indent=4,ensure_ascii=False)
        
        """
        生成第一类问题 specified_card 的数据 并且保存
        """
        puzzle_data_1=generate_specified_card_dataset(game=game,generated_number=puzzles_generated,image_file=image_file,state_file=state_file,plot_level=plot_level)
        specified_card_data.append(puzzle_data_1)

        """
        生成第二类问题 valid_move 的数据
        """
        puzzle_data_2=generate_valid_move_dataset(game=game,generated_number=puzzles_generated,image_file=image_file,state_file=state_file,plot_level=plot_level)
        valid_move_data.append(puzzle_data_2)

        """
        生成第三类问题的数据
        """
        puzzle_data_3=generate_state_after_move_dataset(game=game,generated_number=puzzles_generated,image_file=image_file,state_file=state_file,plot_level=plot_level)    
        card_after_move_data.append(puzzle_data_3)
        puzzles_generated+=1
    
    # # 保存生成的数据
    
    # ## 第一类问题
    # specified_card_data_path=os.path.join(base_path,f"specified_card-{plot_level}_dataset.json")
    # with open(specified_card_data_path,"w",encoding="utf-8") as f:
    #     json.dump(specified_card_data,f,indent=4,ensure_ascii=False)
    
    # ## 第二类问题
    # valid_move_data_path=os.path.join(base_path,f"valid_move-{plot_level}_dataset.json")
    # with open(valid_move_data_path,"w",encoding="utf-8") as f:
    #     json.dump(valid_move_data,f,indent=4,ensure_ascii=False)

    # ## 第三类问题
    # card_after_move_data_path=os.path.join(base_path,f"card_after_move-{plot_level}_dataset.json")
    # with open(card_after_move_data_path,"w",encoding="utf-8") as f:
    #     json.dump(card_after_move_data,f,indent=4,ensure_ascii=False)
    ## 全部数据
    data=specified_card_data+valid_move_data+card_after_move_data

    return data,specified_card_data,valid_move_data,card_after_move_data

# 生成第一类问题的一条数据
def generate_specified_card_dataset(game:FreeCell,generated_number,image_file,state_file,plot_level):
    """
    这一函数用于生成第一类问题:给定一个game,问某一牌堆的某一card是什么
    """
    # 随机选择一个牌堆
    cascade_index = random.randint(0, len(game.cascade_piles) - 1)
    selected_pile = game.cascade_piles[cascade_index]

    # Ensure the selected pile is not empty 确保牌堆非空
    while not selected_pile:
        cascade_index = random.randint(0, len(game.cascade_piles) - 1)
        selected_pile = game.cascade_piles[cascade_index]

    # Randomly select a card from the pile 从牌堆中随机选取一个
    n = random.randint(1, len(selected_pile))  # Index is 1-based for the puzzle
    selected_card = selected_pile[-n]  # Get the nth card from the top (1-based)    # 选中的card

    # Generate the question and options  构造四个选项
    options = []
    correct_answer = f"({suit_to_string_map[selected_card.suit.value]}, {value_map[selected_card.value]})"
    options.append(correct_answer)

    all_cards = [str(card) for pile in game.cascade_piles for card in pile]
    random.shuffle(all_cards)
    # 构造干扰选项
    while len(options) < 8:
        card = random.choice(all_cards)
        value, suit = card[0:1].strip(), card[2:].strip()   # 这里的value是字符
        option = f"({suit_to_string_map[suit]}, {value})"
        if option not in options:
            # print(option)
            options.append(option)

    random.shuffle(options)

    options_text=f''''''
    for idx,option_idx in enumerate(options):
        options_text+=(f'''{idx+1}.'''+option_idx+"\n")
    # Determine the answer index    构造answer
    answer_index = options.index(correct_answer) + 1

    # Generate analysis
    pile_analysis = ", ".join(f"({suit_to_string_map[card.suit.value]},{value_map[card.value]})" for card in reversed(selected_pile))
    analysis = (
                f"The selected pile{cascade_index} contains (from top to bottom) the following cards:\n {pile_analysis}. "
                f"The {n}-th card from the top is {correct_answer}.")

    # Generate the puzzle data
    puzzle_data = {
        "data_id": f"free_cell-specified_card-{plot_level}-{generated_number+1:05d}",
        "qa_type": "Target Perception",
        "question_id":1,
        "question_description":"Given a particular game state, the puzzle will present a question about which card is at a specific position in one of the cascade piles.Your task is to indentify the card in the options. ",
        "image": f"{image_file}",
        "state": f"{state_file}",
        "plot_level": plot_level,
        "qa_level": qa_level["specified_card"],
        "question": (f"In this FreeCell game:\nwe have {game.cascade_number} cascade piles at sum, and their indexes are {[i for i in range(game.cascade_number)]}"
                     f"We have 4 freecell on the left top, and their indexes are 0,1,2,3."
                     f"We have 4 foundation piles on the right top, and their indexes are 0,1,2,3."
                     f"In FreeCell, cards can be moved according to specific rules: "
                     "A card can be moved to a free cell if available, stacked in descending "
                     "order alternating colors in cascade piles, or placed in foundation piles "
                     f"starting from Ace. Now, find the {n}-th card from the top of cascade pile {cascade_index}."
                     f"the options are as follows:\n{options_text}"),
        "answer": answer_index,
        "analysis": analysis,
        "options": options
    }
    return puzzle_data

foundation_to_suit_map={
    0:"♥",
    1:"♦",
    2:"♣",
    3:"♠",

}

# 生成第二类问题的一条数据
def generate_valid_move_dataset(game: FreeCell, generated_number, image_file, state_file, plot_level):
    """
    Generate a dataset for the second type of puzzle: given the current game state and four options
    representing different card moves, choose the valid move.
    """
    valid_moves = game.get_valid_moves()
    
    if not valid_moves:
        raise ValueError("No valid moves available in the current game state")
    
    correct_move = random.choice(valid_moves)
    options = []
    moves_info = []
    
    # Add the correct move  {correct_move['card']}
    from_=correct_move['from']
    if "Foundation" in correct_move['from']:
        suit=correct_move['from'].split()[1]
        from_=f'''Foundation {suit_to_string_map[suit]}'''
        correct_move['from']=from_
    to_=correct_move['to']
    if "Foundation" in correct_move['to']:
        suit=correct_move['to'].split()[1]
        to_=f'''Foundation {suit_to_string_map[suit]}'''
        correct_move['to']=to_
    correct_option = f"Move ({suit_to_string_map[correct_move['card'].suit.value]},{correct_move['card'].value}) from {from_} to {to_}"
    # print("正确选项:",correct_option)
    options.append(correct_option)
    moves_info.append(correct_move) # 加入的move都是修改suit为string的move
    
    # Generate invalid moves
    invalid_moves = []
    
    # 无效moves不超过3个时,要补成三个
    while len(invalid_moves) < 3:
        # 定义各堆类型及其范围
        dest_types = {
            "Cascade": len(game.cascade_piles),  # Cascade 堆数量
            "FreeCell": 4,                      # FreeCell 固定为 4 个
            "Foundation": 4                     # Foundation 固定为 4 个
        }
        source_types={
            "Cascade": len(game.cascade_piles),  # Cascade 堆数量
            "FreeCell": 4,                      # FreeCell 固定为 4 个
        }

        # 随机选择 source的类型以及索引
        source_type = random.choice(list(source_types.keys()))
        source_index = random.randint(0, source_types[source_type] - 1)
        source = f"{source_type} {source_index}"
        
        # 随机选择dest的类型及索引  把foundation的花色转成了string
        dest_type = random.choice(list(dest_types.keys()))
        dest_index = random.randint(0, dest_types[dest_type] - 1)
        dest=f''''''
        if dest_type == "Foundation":
            dest_index=foundation_to_suit_map[dest_index]   # 数字转suit符号
            dest = f"{dest_type} {suit_to_string_map[dest_index]}"
        else:
            dest = f"{dest_type} {dest_index}"
        all_cards = [card for pile in game.cascade_piles for card in pile]
        if all_cards:
            card = random.choice(all_cards)
            invalid_move = {"card": card, "from": source, "to": dest}
            if invalid_move not in invalid_moves and invalid_move not in valid_moves:
                # print("干扰项:",invalid_move)
                invalid_moves.append(invalid_move)
    
    selected_invalid_moves = random.sample(invalid_moves, 3)
    # 构造一对三错的选项
    for move in selected_invalid_moves:
        option = f"Move ({suit_to_string_map[move['card'].suit.value]},{move['card'].value}) from {move['from']} to {move['to']}"
        options.append(option)
        moves_info.append(move)
    
    combined = list(zip(options, moves_info))
    random.shuffle(combined)
    options, moves_info = zip(*combined)
    options = list(options)
    moves_info = list(moves_info)
    
    answer_index = options.index(correct_option) + 1
    
    options_text=f''''''
    for idx,option_idx in enumerate(options):
        options_text+=(f'''{idx+1}.'''+option_idx+"\n")

    # Generate detailed analysis
    analysis = "Let's analyze each option in detail:\n\n"
    
    def get_destination_info(move, game):
        """Helper function to get destination pile information"""
        # print("get destination of move: ",move)
        if "Foundation" in move['to']:
            # idx = move['to'].split()[-1]
            suit_string= move['to'].split()[-1]
            suit=string_to_suit_map[suit_string]
            # suit=Suit(foundation_to_suit_map[idx])
            foundation_pile = game.foundation_piles[Suit(suit)]
            return foundation_pile[-1] if foundation_pile else "empty"
        elif "Cascade" in move['to']:
            pile_index = int(move['to'].split()[-1])
            return game.cascade_piles[pile_index][-1] if game.cascade_piles[pile_index] else "empty"
        else:  # FreeCell
            cell_index = int(move['to'].split()[-1])
            return game.free_cells[cell_index] if game.free_cells[cell_index] else "empty"
    
    for i, (option, move) in enumerate(zip(options, moves_info), 1):
        analysis += f"Option {i}: {option}\n"
        card = move['card']
        analysis += f"• Moving card: {card.value} of {suit_to_string_map[card.suit.value]} ({card.color.value})\n"
        analysis += f"• From: {move['from']}\n"
        analysis += f"• To: {move['to']}\n"
        
        if option == correct_option:
            analysis += "This is the CORRECT move because:\n"
            
            if "Foundation" in move['to']:
                dest_card = get_destination_info(move, game)
                if dest_card == "empty":
                    analysis += (f"- The foundation pile for {suit_to_string_map[card.suit.value]} is empty\n"
                               f"- This card is an Ace ({card.value}), which is valid to start a foundation pile\n"
                               f"- Foundation piles must start with Ace and build up by suit\n")
                else:
                    analysis += (f"- Top card of foundation pile: {dest_card.value} of {suit_to_string_map[dest_card.suit.value]}\n"
                               f"- Moving {card.value} of {suit_to_string_map[card.suit.value]} on top\n"
                               f"- This follows the rule: same suit, ascending order (+1)\n")
            
            elif "FreeCell" in move['to']:
                cell_index = int(move['to'].split()[-1])
                analysis += (f"- Free Cell {cell_index} is empty\n"
                           f"- Any single card can be moved to an empty free cell\n"
                           f"- The {card.value} of {suit_to_string_map[card.suit.value]} is a single card move\n")
            
            else:  # Cascade pile
                dest_card = get_destination_info(move, game)
                if dest_card == "empty":
                    analysis += (f"- The destination cascade pile is empty\n"
                               f"- Any card can be placed on an empty cascade pile\n")
                else:
                    analysis += (f"- Top card of destination pile: {dest_card.value} of {suit_to_string_map[dest_card.suit.value]} ({dest_card.color.value})\n"
                               f"- Moving {card.value} of {suit_to_string_map[card.suit.value]} ({card.color.value}) underneath\n"
                               f"- This follows cascade rules:\n"
                               f"  1. Colors alternate ({card.color.value} ≠ {dest_card.color.value})\n"
                               f"  2. Values descend ({dest_card.value} = {card.value + 1})\n")
        
        else:   # 错误选项分析
            analysis += "This is an INVALID move because:\n"
            
            # 先分析src
            src_index=(int)(move['from'].split()[1])
            if "Cascade" in move['from']:
                src_top_card=game.cascade_piles[src_index][-1]
                if src_top_card != move["card"]:
                    analysis+=f'''card ({suit_to_string_map[card.suit.value]},{card.value}) is not the top card of Cascade  pile {src_index}\n'''
                else:
                    analysis+=f'''card ({suit_to_string_map[card.suit.value]},{card.value}) is the top card of Cascade  pile {src_index}\n'''
            elif "FreeCell" in move["from"]:
                if not game.free_cells[src_index]:
                    free_cell_card = game.free_cells[src_index]
                    if free_cell_card != move["card"]:
                        analysis+=f'''Free Cell {src_index} doesn't hold the card ({suit_to_string_map[card.suit.value]},{card.value})\n'''
                    else:
                        analysis+=f'''Free Cell {src_index} holds the card ({suit_to_string_map[card.suit.value]},{card.value})\n'''
            else:
                analysis+=''
            # 再分析dst
            if "Foundation" in move['to']:
                dest_card = get_destination_info(move, game)
                if dest_card == "empty":
                    analysis += (f"- The foundation pile is empty but the card ({card.value} of {suit_to_string_map[card.suit.value]}) "
                               f"is not an Ace\n"
                               f"- Foundation piles must start with Ace\n")
                else:
                    analysis += (f"- Top card of foundation pile: {dest_card.value} of {suit_to_string_map[dest_card.suit.value]}\n"
                               f"- Attempting to move: {card.value} of {suit_to_string_map[card.suit.value]}\n"
                               f"- This violates foundation rules:\n")
                    if card.suit != dest_card.suit:
                        analysis += f"  * Cards must be of the same suit\n"
                    if card.value != dest_card.value + 1:
                        analysis += f"  * Cards must be placed in ascending order (+1)\n"
            
            elif "FreeCell" in move['to']:
                cell_index = int(move['to'].split()[-1])
                if game.free_cells[cell_index]:
                    analysis += (f"- Free Cell {cell_index} is occupied by ({suit_to_string_map[game.free_cells[cell_index].suit.value]},{game.free_cells[cell_index].value})\n"
                               f"- Free cells can only hold one card at a time\n")
            
            else:  # Cascade pile
                dest_card = get_destination_info(move, game)
                if dest_card == "empty":
                    analysis += f"- The destination cascade pile is empty\n"
                else:
                    analysis += (f"- Top card of destination pile: {dest_card.value} of {suit_to_string_map[dest_card.suit.value]} ({dest_card.color.value})\n"
                               f"- Attempting to move: {card.value} of {suit_to_string_map[card.suit.value]} ({card.color.value})\n"
                               f"- This violates cascade rules:\n")
                    if card.color == dest_card.color:
                        analysis += f"  * Colors must alternate (both are {card.color.value})\n"
                    if card.value != dest_card.value - 1:
                        analysis += f"  * Values must descend (difference is not 1)\n"
        
        analysis += "\n"
    
    puzzle_data = {
        "data_id": f"free_cell-valid_move-{plot_level}-{generated_number+1:05d}",
        "qa_type": "State Prediction",
        "question_id": 2,
        "question_description": "Given the current game state, identify which of the following moves is valid according to FreeCell rules.",
        "image": f"{image_file}",
        "state": f"{state_file}",
        "plot_level": plot_level,
        "qa_level": qa_level["valid_move"],
        "question": (
            f"In this FreeCell game:\nwe have {game.cascade_number} cascade piles at sum, and their indexes are {[i for i in range(game.cascade_number)]}"
            f"We have 4 freecell on the left top, and their indexes are 0,1,2,3."
            f"We have 4 foundation piles on the right top, and their indexes are 0,1,2,3."
            "In FreeCell, cards must be moved according to specific rules:\n"
            "1. Cards in cascade piles must be stacked in descending order with alternating colors\n"
            "2. Only one card can be moved at a time (unless using free cells)\n"
            "3. Foundation piles must be built up by suit from Ace to King\n"
            "4. Free cells can hold only one card each\n\n"
            "Which of the following moves is valid in the current game state?"
            f'''the options are as follows:\n{options_text}'''
        ),
        "answer": answer_index,
        "analysis": analysis,
        "options": options
    }
    
    return puzzle_data

# 生成第三类问题的一条数据
def generate_state_after_move_dataset(game:FreeCell,generated_number,image_file,state_file,plot_level):
    
    # 获取全部valid_moves
    valid_moves=game.get_valid_moves()
    
    # 选择一个move
    selected_move=random.choice(valid_moves)
    cascade_index = int(selected_move['from'].split()[-1])
    while not selected_move["from"].startswith('Cascade') :
        selected_move=random.choice(valid_moves)
    selected_pile=game.cascade_piles[cascade_index]

    if "Foundation" in selected_move['to']:
        suit=selected_move['to'].split()[1]
        selected_move['to']=f'''Foundation {suit_to_string_map[suit]}'''

    # 构造正确选项
    selected_card=game.cascade_piles[cascade_index][-2]
    answer_text=f"({suit_to_string_map[selected_card.suit.value]}, {value_map[selected_card.value]})"
    options=[answer_text]
    

    # 下面开始生成干扰选项
    all_cards = [str(card) for pile in game.cascade_piles for card in pile]
    
    # 完全随机的牌
    while len(options) < 8:
        random_card = random.choice(all_cards)
        value, suit = random_card[0:1].strip(), random_card[2:].strip()
        option = f"({suit_to_string_map[suit]}, {value})"
        if option not in options:
            options.append(option)
    random.shuffle(options)
    answer_index=options.index(answer_text)+1

    options_text=f''''''
    for idx,option_idx in enumerate(options):
        options_text+=(f'''{idx+1}.'''+option_idx+"\n")

    new_state={
        "cascade_piles": [[f"({suit_to_string_map[card.suit.value]},{card.value})" for card in pile] if pile else None for pile in game.cascade_piles],
        "free_cells": [f"({suit_to_string_map[card.suit.value]},{card.value})" if card else None for card in game.free_cells],
        "foundation_piles": {suit.name: [str(card) for card in pile] if pile else None
                             for suit, pile in game.foundation_piles.items()}
    }

    analysis = (f"We have {game.cascade_number} cascade piles.Their indexes are {[i for i in range(game.cascade_number)]}.\n"
                f"Before the move,the state of the cascade_pile{cascade_index} is:{new_state['cascade_piles'][cascade_index]}. "
                f"After moving the card ({suit_to_string_map[selected_move['card'].suit.value]},{value_map[selected_move['card'].value]}) from {selected_move['from']} to {selected_move['to']},the top card of the cascade_pile {cascade_index} is ({suit_to_string_map[selected_pile[-2].suit.value]},{selected_pile[-2].value})."
                f"and the top card of the {selected_move['to']} becomes card ({suit_to_string_map[selected_card.suit.value]},{value_map[selected_card.value]}).")
    new_state={
        "cascade_piles": [[card for card in pile] if pile else None for pile in game.cascade_piles],
        "free_cells": [str(card) if card else None for card in game.free_cells],
        "foundation_piles": {suit.name: [str(card) for card in pile] if pile else None
                             for suit, pile in game.foundation_piles.items()}
    }
    from_pile=int(selected_move["from"].split()[1])
    new_state["cascade_piles"][from_pile].pop()
    if selected_move["to"].startswith("Cascade"):
        to_pile=int(selected_move["to"].split()[1])
        card=new_state["cascade_piles"][from_pile][-1]
        new_state["cascade_piles"][to_pile].append(card)
    
    
    analysis+=f"the new state of the cascade_pile {cascade_index} is:\n{[f'({suit_to_string_map[card.suit.value]},{card.value})' for card in new_state['cascade_piles'][cascade_index]]}\n Therefore the top card of the cascade_pile {cascade_index} is {answer_text}"
    puzzle_data={
        "data_id": f"free_cell-card_after_move-{plot_level}-{generated_number+1:05d}",
        "qa_type": "State Prediction",
        "question_id":3,
        "question_description":"Given a particular game state,a selected move and a selected cascade pile, the puzzle will present a question about which card is at the top of the cascade pile.\nYour task is to indentify the card in the options. ",
        "image": f"{image_file}",
        "state": f"{state_file}",
        "plot_level": plot_level,
        "qa_level": qa_level["card_after_move"],
        "question": (
                     f"In this FreeCell game:\nwe have {game.cascade_number} cascade piles, and their indexes are {[i for i in range(game.cascade_number)]}"
                     f"We have 4 freecell on the left top, and their indexes are 0,1,2,3."
                     f"We have 4 foundation piles on the right top, and their indexes are 0,1,2,3."
                     f"In FreeCell, cards can be moved according to specific rules: "
                     "A card can be moved to a free cell if available, stacked in descending "
                     "order alternating colors in cascade piles, or placed in foundation piles "
                     f"starting from Ace. Now, find the top card from cascade pile {cascade_index} after moving the card ({suit_to_string_map[selected_move['card'].suit.value]},{selected_move['card'].value}) from {selected_move['from']} to {selected_move['to']}."
                     f"the options are as follows:\n{options_text}"),
        "answer": answer_index,
        "analysis": analysis,
        "options": options
    }
    return puzzle_data


