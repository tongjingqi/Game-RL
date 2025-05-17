import os
import json
import random
import pyramidchess_image_generate as gen_image
import pyramidchess_board_generate as gen_board

def json_generate(type,data_id,question_id,qa_level,question_description,image,state,plot_level,qa_type,question,answer,analysis,option=None,example=None):
    # 根据类型写入不同的文件
    if type == "mcq":
        data_entry = {
        "data_id": data_id,
        "qa_type": qa_type,
        "question_id":question_id,
        "question_description":question_description,
        "image": image,
        "state": state,
        "plot_level": plot_level,
        "qa_level":qa_level,
        "question": question,
        "answer": answer,
        "analysis": analysis,
        "options": option
        }
        if example:
            file_name = "pyramidchess_dataset_example/data.json"
        else:
            file_name = "pyramidchess_dataset/data.json"
    elif type == "fill":
        data_entry = {
        "data_id": data_id,
        "qa_type": qa_type,
        "question_id":question_id,
        "question_description":question_description,
        "image": image,
        "state": state,
        "plot_level": plot_level,
        "qa_level":qa_level,
        "question": question,
        "answer": answer,
        "analysis": analysis
        }
        if example:
            file_name = "pyramidchess_dataset_example/data.json"
        else:
            file_name = "pyramidchess_dataset/data.json"
    else:
        raise ValueError("Unsupported type. Please use 'mcq' or 'fill'.")

    try:
        # 尝试读取已存在的文件数据
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                dataset = json.load(file)
        except FileNotFoundError:
            # 如果文件不存在，则初始化为空列表
            dataset = []

        # 添加新条目
        
        dataset.append(data_entry)
        

        # 写回文件
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(dataset, file, ensure_ascii=False, indent=4)

        # print(f"Data successfully added to {file_name}.")
    except Exception as e:
        print(f"An error occurred: {e}.Probably due to data.json. Try delete the file.")
        
def json_conbine():
    file1 = "fill_dataset.json"
    file2 = "mcq_dataset.json"
    output_file = "data.json"

    # 加载文件
    with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    # 合并内容（假设两者都是列表）
    if isinstance(data1, list) and isinstance(data2, list):
        merged_data = data1 + data2
    elif isinstance(data1, dict) and isinstance(data2, dict):
        merged_data = {**data1, **data2}
    else:
        raise ValueError("不兼容的JSON格式,确保两个文件都为列表或字典！")

    # 保存到新的文件
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(merged_data, out, ensure_ascii=False, indent=4)

def state_save(path,layers):
    try:
        # 将 layers 字典保存为 JSON 文件
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(layers, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An error occurred while saving: {e}")

def get_question_info(question_id):
    if question_id == 0:
        question_type = "mcq"
        qa_type = "StateInfo"
        description = "Choose a random coordinate and ask what status is the cooradinate"
        level = "Easy"
        return question_type,qa_type,level,description
    
    elif question_id == 1:
        question_type = "mcq"
        qa_type = "ActionOutcome"
        description = "Select a coordinate and determine whether a ball can be placed at this coordinate. If so, what would happen after the place of the ball."
        level = "Medium"
        return question_type,qa_type,level,description
    
    elif question_id == 2:
        question_type = "fill"
        qa_type = "TransitionPath"
        description = "Calculate how many steps (turns) are required for a ball to be placed at certain coordinate.(Including the step putting the ball at the cooradinate)"
        level = "Hard"
        return question_type,qa_type,level,description
    
    elif question_id == 3:
        question_type = "fill"
        qa_type = "StrategyOptimization"
        description = "Give out the best position to put the ball at a certain point of a game."
        level = "Hard"
        return question_type,qa_type,level,description
    
    elif question_id == 4:
        question_type = "fill"
        qa_type = "StateInfo"
        description = "Calculate how many balls are there one the board."
        level = "Easy"
        return question_type,qa_type,level,description
    
    elif question_id == 5:
        question_type = "mcq"
        qa_type = "StateInfo"
        description = "Provide the higher level status of a coordinate: Is the coordinate legal? Does it contain a ball? Can the ball be taken? Can a ball be placed?"
        level = "Medium"
        return question_type,qa_type,level,description
    
    else:
        raise ValueError(f"Question_id:{question_id} unsupported")
   
def question_generate(question_id,board,param_list=None): 
    # with open("rule.txt", "r", encoding="utf-8") as file:
    #     rule = file.read()
    rule = (
        "Pyramid Chess Rules:\n"
        "0.Game Board:\n"
        "The game board is square and comes in various sizes: 3x3, 4x4, or 5x5. On an nxn board, there are n levels (0 to n-1). At each level k, the x and y coordinates range from 0 to n-1-k, resulting in (n-k)**2 slots per level. The slots in the lower levels act as the base for the slots in the upper levels. Slots at level 0 have no base, while slots at level j (j!=0) with coordinates (m,n) are supported by four base slots (m,n),(m+1,n),(m,n+1),(m+1,n+1) from level j-1.\n"
        "1.Players and Initial Setup:\n"
        "The game is played between two players, designated as PLAYER_0 and PLAYER_1, each using balls of a distinct color from their color pool, blue balls for PLAYER_0 and red balls for PLAYER_1. Players take turns placing their balls on a square game board. The number of balls available to each player depends on the size of the board: on a 3x3 board, each player has 7 balls; on a 4x4 board, each has 15 balls; and on a 5x5 board, PLAYER_0 (the first player to place a ball) has 28 balls, while PLAYER_1 has 27 balls.\n"
        "2.Placing Balls and Creating New Slots:\n"
        "At the start of the game, the lowest level of the board (Level 0) is completely open and balls can be placed in any available slot on this level(since there is no base for slots in level 0, slots in level 0 have full base). After a ball is placed in a slot, that slot is no longer available for placing another ball. A ball can only be placed on the upper level if it is supported by a fully completed 2x2 block of balls on the level directly beneath, which means all the base of the slot is full(there is a ball in each of these slots).\n"
        "3.Take-back mechnism:\n"
        "If a player places a ball that completes a 2x2 block of the same color (all four balls belonging to that player), they may return up to two balls from the block to their color pool. A ball can only be removed if it does not have another ball directly above it, as removing a \"base\" ball would collapse the pyramid. Returning a ball reopens the slot it occupied, allowing it to be used for future placements, but the rule requiring a full 2x2 block as a base for placing balls on upper levels still applies.\n"
        "4.Winning the Game:\n"
        "The game ends when one player successfully places the last ball on top of the pyramid. The player who place the ball on the top of the pyramid wins.\n"
    )
    options = None
    length = len(board.Board)
    analysis = f"From the image provided, we can recognize that the board is a {length}x{length} board."
    if question_id == 0:
        # 随机选择一个坐标，生成问题
        out_of_bound_flag = 0
        position_table = board.all_pos()

        # 检查 position_table 是否为空
        if not position_table:
            raise ValueError("The position table is empty.")

        answer_index = random.randint(0, len(position_table) - 1)
        answer_item = position_table[answer_index]
        level, position = answer_item.Level, answer_item.Position

        if param_list is not None:
            out_of_bound_prob = param_list[0]
            if random.random() < out_of_bound_prob:
                out_of_bound_flag = 1
                out_of_bound_info = random.choice([0, 1])
                if out_of_bound_info == 0:
                    level = random.randint(5, 15)  # 随机生成超界的 level
                else:
                    position = [random.randint(5, 15), random.randint(5, 15)]  # 随机生成超界的 position
                    


        question = (
            rule +
            f"\nQuestion: What is the status of the ball on Level {level}, "
            f"which has coordinate ({position})?\n"
            "Options:\n1. PLAYER_0\n2. PLAYER_1\n3. Empty\n4. Index out of bound\n"
        )

        if out_of_bound_flag == 1:
            answer = 4
            if out_of_bound_info == 0:
                analysis += (
                    f"The coordinate {position} in level {level} "
                    f"is outside the bounds of the level shown in the image (the z-axis only spans from 0 to {board.Level - 1}). "
                    f"Therefore, the status is Index out of bound."
                )
            else:
                analysis += (
                    f"The coordinate {position} in level {level} "
                    f"is outside the bounds of the grid in level {level} (only spans from 0 to {board.Level - 1 - level}). "
                    f"Therefore, the status is Index out of bound."
                )
        else:
            ball_color = getattr(answer_item, "Color", None)
            if ball_color is None:
                answer = 3
                analysis += (
                    f"The coordinate {position} in level {level} "
                    f"does not contain any balls (it is empty). Therefore, the status of the ball at coordinate {position} in level {level} is 3. Empty."
                )
            elif ball_color == 0:
                answer = 1
                analysis += (
                    f"We can observe the layout of the pyramid across its levels. "
                    f"Based on level {level}'s grid (specifically at coordinate {position}), the ball is blue, which corresponds to PLAYER_0."
                )
            elif ball_color == 1:
                answer = 2
                analysis += (
                    f"We can observe the layout of the pyramid across its levels. "
                    f"Based on level {level}'s grid (specifically at coordinate {position}), the ball is red, which corresponds to PLAYER_1."
                )
            else:
                raise ValueError("Faulty item: Unexpected ball color.")

        options = ["PLAYER_0", "PLAYER_1", "Empty", "Index out of bound"]
        return question, answer, analysis, options  
    elif question_id == 1:
        #选定一个坐标，问这个坐标可不可以进行放置，若放置后发生的结果
        position_table = board.all_pos()
        # 检查 position_table 是否为空
        if not position_table:
            raise ValueError("The position table is empty.")
        
        answer_index = random.randint(0, len(position_table) - 1)
        answer_item = position_table[answer_index]
        level, position = answer_item.Level, answer_item.Position
        
        COLOR = ['blue','red']
        color_ind = random.choice([0,1])
        color = COLOR[color_ind]
        # 生成问题的基础内容
        question = (
            rule +
            f"\nQuestion: Can a ball be placed at coordinate {position} on Level {level}? "
            f"If a {color} ball is placed there, what would be the outcome?\n"
            "Options:\n1. Can place and no balls taken\n"
            "2. Can place and then balls can be taken\n"
            "3. Cannot place, position already occupied\n"
            "4. Cannot place, ball not ready below\n"
        )

        if answer_item.Legal:
            # 如果能放置，检查是否能形成 2x2 block
            answer_item.put(color_ind)
            take_check_result = board.take_put_check(stop_mode=True)

            if not take_check_result:  # 没有触发take机制
                answer = 1
                analysis += (
                    f"Coordinate {position} on level {level} is empty and a ball can be placed there."
                    f"Placing a {color} ball at coordinate {position} on level {level} does not form 2x2 block of the same color, and therefore no balls would be taken. "
                    "Therefore, the status is: Can place and no balls taken."

                )
            else:
                take_level = take_check_result[0].Level
                take_position = [item.Position for item in take_check_result]
                answer = 2
                analysis += (
                    f"Coordinate {position} on level {level} is empty and a ball can be placed there."
                    f"Placing a {color} ball at coordinate {position} on level {level} forms a 2x2 block of the same color {color} at Level:{take_level},Position:{take_position} and triggers a take-back mechanism."
                    "Therefore, the status is:Can place and 2x2 block formed, balls can be taken."
                )
        else:
            # 如果不能放置，检查该位置是否已经被占用或未准备好
            if answer_item.Available is False:
                color_ind = answer_item.Color
                color = COLOR[color_ind]
                answer = 3
                analysis += (
                    f"The coordinate {position} on level {level} is already occupied by a {color} ball, "
                    "so it is not possible to place a ball there. Therefore, the status is: Cannot place, position already occupied."
                )
            else:
                bases = []
                not_ready = []
                # 判断是否未准备好，不能形成 2x2 block
                for base in answer_item.Base:
                    bases.append(base.Position)
                    if base.Available is True:
                        not_ready.append(base.Position)
                answer = 4
                analysis += (
                    f"The coordinate {position} on level {level} cannot have a ball placed there. Because there are no platform which four balls below it form a 2x2 block to support it."
                    f"To put a ball at coordinate {position} on level {level}, the bases of the position which are {bases} on level{level-1} must be full. But there is no ball at {not_ready} on level{level-1}."
                    "If a ball is placed at the position it will fall down. Therefore, the status is: Cannot place, ball not ready below."
                )

        options = [
            "Can place and no balls taken",
            "Can place and then balls can be taken",
            "Cannot place, position already occupied",
            "Cannot place, ball not ready below"
        ]

        return question, answer, analysis, options
    elif question_id == 2:
        # Select a coordinate and check how many steps it takes for the ball to be placed there
        position_table = board.all_avl_pos()

        # Check if position_table is empty
        if not position_table:
            raise ValueError("The position table is empty.")
        
        answer_index = random.randint(0, len(position_table) - 1)
        answer_item = position_table[answer_index]
        level, position = answer_item.Level, answer_item.Position

        
        # Calculate the number of steps to reach a legal state using count_base
        info = [0,0,0,0,0]
        dict_info = {0:[],1:[],2:[],3:[],4:[],5:[]}
        steps_needed = gen_board.count_base(answer_item,info,dict_info)
        steps_needed += 1

        # Generate the question content
        question = (
            rule +
            f"Question: How many steps (turns) are required for a ball to be placed at coordinate {position} on Level {level}? (including the turn placing the ball)"
        )
        
        
                # Initialize the analysis string
        analysis_string = (
            f"From the image provided, we can recognize that the board is a {length}x{length} board."
            f"To place a ball at coordinate {position} on Level {level}, we need to ensure all the balls in its sub-pyramid, which are the balls supporting the position, are placed.\n"
        )
        # Describe the calculation process
        analysis_string += (
            "This is determined by checking each level below the target position, from the highest level below it to the base level, "
            "and counting how many balls that support the position are missing in each layer. The total number of missing balls represents the steps needed.\n"
        )

        # Iterate from the target level downward and calculate missing balls
        full_flag = 1
        for i in range(level - 1, -1, -1):  # Start from the level below the target
            if info[i] != 0:
                full_flag = 0
                analysis_string += f"Level {i}: {info[i]} more ball(s) need to be placed at {dict_info[i]}.\n"

        # Conclude with the total steps needed
        if level == 0:
            assert(steps_needed == 1)
            analysis_string += (
            "Since the ball is on level 0 the ground of the board, there is no ball need to be placed to support te ball, the ball at the target position can be placed immediately.\n"
            f"Therefore, it needs 1 step in total."
        )
        elif full_flag == 0:
            analysis_string += (
            "Once all the required balls in the sub-pyramid are placed, the ball at the target position can be placed.\n"
            f"Therefore, it needs {steps_needed} steps in total."
        )
        else:
            assert(steps_needed == 1)
            analysis_string += (
            "All the required balls in the sub-pyramid has already been placed placed, the ball at the target position can be placed.\n"
            f"Therefore, it needs 1 step in total."
        )
        analysis = analysis_string
        # If it cannot be placed, provide the number of steps needed to reach a legal state
        answer = f"{steps_needed}"

        return question, answer, analysis, options
    elif question_id == 3:
        if param_list == None:
            raise ValueError("Genration error in question id 3")

        take_point = param_list[0]
        turn = param_list[1]
        take_pos = param_list[2]
        take_pos = [item.Position for item in take_pos]
        turn_flag = random.choice([0, 1])
        if turn_flag == 1:
            turn = (turn + 1) % 2    
        other_turn = (turn + 1) % 2
        PLAYER = ["PLAYER_0","PLAYER_1"]
        COLOR = ['blue','red']
        question = (
            rule +
            f"\nIt is {PLAYER[turn]}'s turn.(which uses the {COLOR[turn]} ball)What is the best coordinate to put a ball in order to maximize the opportunity of winning. Please answer in the form of \"[x,y] at level z\"."
        )
        answer = f"{take_point.Position} at level {take_point.Level}"
        if turn_flag:
            analysis += (
                "To maximize the winning chance, one must try his best to form a 2x2 block of his color for the take-back mechanism. "
                "So that he avoid losing balls in his turn and therefore minimize the chance of running out of balls first."
                "Blocking the opponents chance to form 2x2 block of his color also increase the oppotunity of winning."
                f"From the image provided, now is the {PLAYER[turn]}'s turn, who uses the {COLOR[turn]} ball. Putting a {COLOR[turn]} ball at {take_point.Position} at Level {take_point.Level} stop the other player {PLAYER[other_turn]} to form 2x2 block of {COLOR[other_turn]} at {take_pos}."
                f"So the answer is Putting a ball at {take_point.Position} at level {take_point.Level}."
            )
        else:
            analysis += (
                "To maximize the winning chance, one must try his best to form a 2x2 block of his color for the take-back mechanism. "
                "So that he avoid losing balls in his turn and therefore minimize the chance of running out of balls first."
                "Blocking the opponents chance to form 2x2 block of his color also increase the oppotunity of winning."
                f"From the image provided,now is the {PLAYER[turn]}'s turn, who uses the {COLOR[turn]} ball. Putting a {COLOR[turn]} ball at {take_point.Position} at Level {take_point.Level} form 2x2 block of {COLOR[turn]} at {take_pos},which avoid losing a ball for {PLAYER[turn]} in this turn."
                f"So the answer is Putting a ball at {take_point.Position} at level {take_point.Level}."
            )
        return question, answer, analysis, options           
    elif question_id == 4:
        question = (
            rule +
            f"\nQuestion: How many balls are there on the board in the image. "
        )
        ball_dict = board.board_dict()
        balls_list,count = gen_board.count_ball(ball_dict)
        analysis_string = ""
        for level,num_balls in enumerate(balls_list):
            analysis_string += f"There are {num_balls}  balls in level {level}. "
        
        answer = f"{count}"

        # Initialize the analysis string
        analysis_string = (
            f"From the image provided, we can recognize that the board is a {length}x{length} board."
            "To count the total number of balls on the board, we start from the downmost level and proceed upward. "
            "For each level, we use the 2D representation of that level to count the balls row by row and column by column. "
            "Here is the detailed count:\n"
        )

        # Iterate through levels to count balls and provide details
        for level, (num_balls, details) in enumerate(balls_list):
            analysis_string += f"Level {level} contains {num_balls} ball(s):\n"
            
            for row_idx, row in enumerate(details):
                for col_idx, (color, coord) in enumerate(row):
                    analysis_string += f"A {color} ball at {coord}.\n"

        # Conclude with the total count
        analysis_string += (
            f"\nFrom the image provided, the total number of balls on the board is {count}.\n"
        )

        # Final analysis result
        analysis = analysis_string
        return question, answer, analysis, options   
    elif question_id == 5:
        # 随机选择一个坐标，生成问题
        out_of_bound_flag = 0
        position_table = board.all_pos()

        # 检查 position_table 是否为空
        if not position_table:
            raise ValueError("The position table is empty.")

        answer_index = random.randint(0, len(position_table) - 1)
        answer_item = position_table[answer_index]
        level, position = answer_item.Level, answer_item.Position

        if param_list is not None:
            out_of_bound_prob = param_list[0]
            if random.random() < out_of_bound_prob:
                out_of_bound_flag = 1
                out_of_bound_info = random.choice([0, 1])
                if out_of_bound_info == 0:
                    level = random.randint(5, 15)  # 随机生成超界的 level
                else:
                    position = [random.randint(5, 15), random.randint(5, 15)]  # 随机生成超界的 position
                    


        question = (
            rule +
            f"\nQuestion: What is the status of the ball on Level {level}, "
            f"which has coordinate ({position})?\n"
            f"Is the coordinate legal? Does it contain a ball? Can the ball be taken(has no ball directly above it)? Can a ball be placed?"
            "Options:\n1. The coordinate is out of bound\n2. It contain a ball and the ball can't be taken\n3. It contain a ball and can be taken\n4. It doesn't contain a ball and a ball can't be put here\n5.It doesn't contain a ball and a ball can be put here\n"
        )

        if out_of_bound_flag == 1:
            answer = 1
            if out_of_bound_info == 0:
                analysis += (
                    f"The coordinate {position} in level {level} "
                    f"is outside the bounds of the level shown in the image (the z-axis only spans from 0 to {board.Level - 1}). "
                    f"Therefore, the status is The coordinate is out of bound."
                )
            else:
                analysis += (
                    f"The coordinate {position} in level {level} "
                    f"is outside the bounds of the grid in level {level} (only spans from 0 to {board.Level - 1 - level}). "
                    f"Therefore, the status is The coordinate is out of bound."
                )
        else:
            Available = getattr(answer_item, "Available", None)
            Legal = getattr(answer_item, "Legal", None)
            Can_be_taken = getattr(answer_item, "Can_be_taken", None)
            if not Available:
                if not Can_be_taken:
                    answer = 2
                    analysis += (
                        f"From the image provided, there is a ball at the coordinate {position} in level {level}. "
                        f"And there are also balls sitting above the ball, which means the ball is supporting other balls,so when the take-back happen, the ball can't be taken. Otherwise the pyramid would collapse."
                        f"Therefore, the status is it contain a ball and the ball can't be taken ."
                    )
                elif Can_be_taken:
                    answer = 3
                    analysis += (
                        f"From the image provided, there is a ball at the coordinate {position} in level {level}. "
                        f"And there is no ball sitting above the ball, which means the ball isn't supporting other balls,so when the take-back happen, the ball can be taken without collapsing the pyramid."
                        f"Therefore, the status is it contain a ball and the ball can be taken."
                    )
                else:
                    raise ValueError("Faulty item.")
            elif Available:
                if Legal:
                    answer = 4
                    analysis += (
                        f"From the image provided, there is no ball at the coordinate {position} in level {level}.  "
                        f"The position is legal to put a ball(It is on the ground or the 2x2 block under it is full and a ball can be put in the center above the block)."
                        f"Therefore, the status is it doesn't contain a ball and the player can put a ball here this turn."
                    )
                elif not Legal:
                    answer = 5
                    analysis += (
                        f"From the image provided, we can observe the layout of the pyramid across its levels. "
                        f"The 2x2 block below it isn't full, putting a ball here the ball will fall off the pyramid. So it can't be put in the center above the block."
                        f"Therefore, the status is it doesn't contain a ball and the player can't put a ball here this turn."
                    )
                else:
                    raise ValueError("Faulty item.")
            else:
                raise ValueError("Faulty item.")

        options = ["The coordinate is out of bound", "It contain a ball and the ball can't be taken", "It contain a ball and can be taken", "It doesn't contain a ball and the player can put a ball here this turn","It doesn't contain a ball and the player can't put a ball here this turn"]
        return question, answer, analysis, options  
    else: 
        raise ValueError(f"Question_id:{question_id} unsupported")
    
def data_generate(num_question,param_list = None,question_id_list=[0,1,2,3,4,5],plot_level_list=["Easy","Medium","Hard"],start_id = 0,example=False,max_turn=None):
    num_generate = 0
    id = start_id
    if example:
        path = "pyramidchess_dataset_example/"
    else:
        path = "pyramidchess_dataset/"
        
    num_type = len(question_id_list)
    num_type_plot = len(plot_level_list)
    while(num_generate < num_question):
        
        question_id_ind = random.randint(0,num_type-1)
        question_id = question_id_list[question_id_ind]
            
        plot_level_ind = random.randint(0,num_type_plot-1)
        plot_level = plot_level_list[plot_level_ind]
        
        question_type,qa_type,qa_level,question_description = get_question_info(question_id)
        
        if question_id == 3:
            board,take_point,turn,take_pos = gen_board.board_generate_stop_at_take(plot_level=plot_level)
            param_list = [take_point,turn,take_pos]
        else:    
            board = gen_board.board_generate(max_turn=max_turn,plot_level=plot_level)
        layers = board.board_dict()
        
        data_id = f"pyramidchess-{str(question_type)}-{str(id).zfill(5)}-{qa_type}"
        
        image_path = f"images/board_{str(id).zfill(5)}.png"
        gen_image.combine_image_generate(id=id,layers=layers,example=example,plot_level=plot_level)
        state_path = f"states/board_{str(id).zfill(5)}.json"
        state_save(path=path+state_path,layers=layers)
        
        question,answer,analysis,options = question_generate(question_id,board,param_list=param_list)

        json_generate(type=question_type,question_id=question_id,qa_level=qa_level,question_description=question_description,data_id=data_id,image=image_path,state=state_path,plot_level=plot_level,qa_type=qa_type,question=question,answer=answer,analysis=analysis,option=options,example=example)
        
        id +=1
        num_generate += 1
        
    return id

def check_file_structure(example=False):
    # 确保pyramidchess_dataset/目录存在
    base_dir = "pyramidchess_dataset"
    if example:
        base_dir = "pyramidchess_dataset_example"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 确保images/和states/目录存在
    images_dir = os.path.join(base_dir, "images")
    states_dir = os.path.join(base_dir, "states")
    
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    if not os.path.exists(states_dir):
        os.makedirs(states_dir)

    # 检查并处理data.json
    data_json_path = os.path.join(base_dir, "data.json")
    if not os.path.exists(data_json_path):
        # 创建空的JSON文件
        with open(data_json_path, "w") as f:
            json.dump([], f)
    else:
        # 检查data.json内容是否为列表
        try:
            with open(data_json_path, "r") as f:
                content = json.load(f)
            if not isinstance(content, list):
                raise ValueError("data.json内容不是列表")
        except (json.JSONDecodeError, ValueError):
            # 如果JSON无效或不是列表，重新初始化为空列表
            with open(data_json_path, "w") as f:
                json.dump([], f)
    

