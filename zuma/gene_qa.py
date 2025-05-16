import os
import json
import math
import numpy as np
from typing import List, Tuple, Dict, Union

# 计算两点距离
def calculate_distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)


# 计算p2相对于p1角度
def calculate_angle(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    angle = math.degrees(math.atan2(dy, dx))
    return angle


# 获取方向
def get_direction(angle: float) -> str:
    if -22.5 <= angle < 22.5:
        return "right"
    elif 22.5 <= angle < 67.5:
        return "up-right"
    elif 67.5 <= angle < 112.5:
        return "up"
    elif 112.5 <= angle < 157.5:
        return "up-left"
    elif 157.5 <= angle or angle < -157.5:
        return "left"
    elif -157.5 <= angle < -112.5:
        return "down-left"
    elif -112.5 <= angle < -67.5:
        return "down"
    elif -67.5 <= angle < -22.5:
        return "down-right"
    else:
        return "unknown"


# 检查是否有相邻同色弹珠
def are_adjacent(ball_idx: int, balls: List[Dict], color: str) -> bool:
    if ball_idx > 0 and balls[ball_idx - 1]["color"] == color:
        return True
    if ball_idx < len(balls) - 1 and balls[ball_idx + 1]["color"] == color:
        return True
    return False


# 判断是否为障碍
def is_obstacle(frog_pos: Dict[str, float], target_pos: Dict[str, float], obstacle_pos: Dict[str, float], ball_radius=0.3) -> bool:
    t_x = target_pos["x"] - frog_pos["x"]
    t_y = target_pos["y"] - frog_pos["y"]
    o_x = obstacle_pos["x"] - frog_pos["x"]
    o_y = obstacle_pos["y"] - frog_pos["y"]
    
    # 计算obstacle到直线距离
    return abs(t_y*o_x - o_y*t_x)**2 <= (t_x**2+t_y**2)*(1.1*ball_radius**2) and (o_x**2 + o_y**2) < (t_x**2 + t_y**2) and (t_x*o_x + t_y*o_y) > 0


# 检查青蛙是否能击中某弹珠
def can_hit(frog_pos: Dict[str, float], target_ball: Dict[str, float], balls: List[Dict]) -> bool:
    target_pos = target_ball["position"]
    for other_ball in balls:
        obstacle_pos = other_ball["position"]
        # 判断弹珠是否为障碍
        if is_obstacle(frog_pos, target_pos, obstacle_pos):
            return False
    return True


# 查找所有在方位内的相邻同色弹珠组
def get_ball_in_direction(frog_pos: Dict[str, float], balls: List[Dict], direction: str) -> List[Tuple[int, int, str]]:
    def is_in_direction(frog_pos, ball_pos, direction):
        return get_direction(calculate_angle(frog_pos, ball_pos)) == direction
    
    ball_groups = []  # 存储弹珠组
    n = len(balls)

    i = 0
    while i < n:
        ball = balls[i]
        color = ball["color"]  # 获取当前弹珠的颜色
        group_start = i  # 初始化弹珠组的起点
        group_end = i  # 初始化弹珠组的终点
        
        # 查找后续连续同色弹珠
        for j in range(i + 1, n):
            if balls[j]["color"] == color:  # 判断颜色是否相同
                group_end = j
            else:
                break
        
        # 将弹珠组加入结果列表
        if group_end > group_start and (is_in_direction(frog_pos, ball["position"], direction) or is_in_direction(frog_pos, balls[group_end]["position"], direction)):  # 确保是一个有效的弹珠组
            ball_groups.append((group_start, group_end, color))

        i = group_end + 1

    return ball_groups
        

# 是否能从某角度打中
def can_hit_by_angle(frog_pos: Dict[str, float], ball_pos: Dict[str, float], direction_vector: Dict[str, float], ball_radius=0.3) -> bool:
    # 计算青蛙到目标弹珠的向量
    dx = ball_pos["x"] - frog_pos["x"]
    dy = ball_pos["y"] - frog_pos["y"]

    return abs(dx*direction_vector["y"] - dy*direction_vector["x"]) < 2*ball_radius and (dx*direction_vector["x"] + dy*direction_vector["y"]) > 0

# 距离青蛙最近的弹珠颜色
def nearest_ball_color(frog_pos: Dict[str, float], hit_balls: List[Dict]) -> Union[str, None]:
    if not hit_balls:
        return None
    
    # 初始化最近距离和对应颜色
    nearest_distance = float('inf')
    nearest_color = None
    
    # 遍历命中的弹珠，找到距离最近的颜色
    for ball in hit_balls:
        ball_pos = ball["position"]
        distance = (ball_pos["x"] - frog_pos["x"])**2 + (ball_pos["y"] - frog_pos["y"])**2
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_color = ball["color"]
    
    return nearest_color

# 距离青蛙最近的弹珠编号
def nearest_ball_index(frog_pos: Dict[str, float], hit_balls: Tuple[int, List[Dict]]) -> Union[int, None]:
    if not hit_balls:
        return None
    
    # 初始化最近距离和对应颜色
    nearest_distance = float('inf')
    nearest_idx = None

    # 遍历命中的弹珠，找到距离最近的颜色
    for ball_idx, ball in hit_balls:
        ball_pos = ball["position"]
        distance = (ball_pos["x"] - frog_pos["x"])**2 + (ball_pos["y"] - frog_pos["y"])**2
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_idx = ball_idx
    
    return nearest_idx

# 从某角度打到的弹珠颜色
def angle_shot_color(frog_pos: Dict[str, float], balls: List[Dict], angle: float) -> str:
    radian = math.radians(angle)
    direction_vector = {"x": math.cos(radian), "y": math.sin(radian)}
    hit_balls = []
    
    for ball in balls:
        # 检查是否能命中当前弹珠
        if can_hit_by_angle(frog_pos, ball["position"], direction_vector):
            hit_balls.append(ball)
        
    color = nearest_ball_color(frog_pos, hit_balls)
    if color is None:
        color = "none"
    return color

# 从某角度射出弹珠的结果
def angle_shot_result(frog: Dict, balls: List[Dict], ball_radius=0.3) -> Tuple[bool, bool, int]:
    frog_pos = frog["position"]
    angle = frog["angle"]
    radian = math.radians(angle)
    direction_vector = {"x": math.cos(radian), "y": math.sin(radian)}
    hit_balls = []
    
    for ball_idx, ball in enumerate(balls):
        # 检查是否能命中当前弹珠
        if can_hit_by_angle(frog_pos, ball["position"], direction_vector):
            hit_balls.append((ball_idx, ball))
    
    nearest_idx = nearest_ball_index(frog_pos, hit_balls)
    if nearest_idx is None:
        return False, False, 0

    # 计算O1到射线的垂足P
    O1 = balls[nearest_idx]["position"]
    dx = O1["x"] - frog_pos["x"]
    dy = O1["y"] - frog_pos["y"]
    proj_length = dx * direction_vector["x"] + dy * direction_vector["y"]
    P_x = frog_pos["x"] + proj_length * direction_vector["x"]
    P_y = frog_pos["y"] + proj_length * direction_vector["y"]

    # 计算A点(O1到射线的较近交点)
    d = math.sqrt((O1["x"] - P_x)**2 + (O1["y"] - P_y)**2)
    l = math.sqrt(4 * ball_radius**2 - d**2)
    A_x = P_x - l * direction_vector["x"]
    A_y = P_y - l * direction_vector["y"]
    # 计算向量v1(O1到A)
    v1_x = A_x - O1["x"]
    v1_y = A_y - O1["y"]

    # 计算向量v2
    if nearest_idx == len(balls) - 1:  # 最后一个弹珠
        if nearest_idx == 0:  # 只有一个弹珠
            return True, False, 0
        O3 = balls[nearest_idx - 1]["position"]
        v2_x = O1["x"] - O3["x"]
        v2_y = O1["y"] - O3["y"]
        adj_idx = None
    else:
        O2 = balls[nearest_idx + 1]["position"]
        v2_x = O2["x"] - O1["x"]
        v2_y = O2["y"] - O1["y"]
        adj_idx = nearest_idx + 1

    dot_product = v1_x * v2_x + v1_y * v2_y
    color = frog["next_ball_color"]
    removal_count = 0
    check_idx = adj_idx if dot_product > 0 else (nearest_idx - 1 if nearest_idx > 0 else None)

    # 击中边缘
    if check_idx is None:
        idx = nearest_idx
        # 在最左，向右扩张
        if nearest_idx == 0:
            while idx <= len(balls) - 1 and balls[idx]["color"] == color:
                removal_count += 1
                idx += 1
        # 在最右，向左扩张
        else:
            while idx >= 0 and balls[idx]["color"] == color:
                removal_count += 1
                idx -= 1
        if removal_count >= 2:
            return True, True, removal_count
        else:
            return True, False, 0

    left_idx = min(nearest_idx, check_idx)
    right_idx = max(nearest_idx, check_idx)
    ball1_color = balls[left_idx]["color"]
    ball2_color = balls[right_idx]["color"]

    # 两球均不同色
    if ball1_color != color and ball2_color != color:
        return True, False, 0
    
    # 有球同色
    # 可双向扩张
    if ball1_color == color and ball2_color == color:
        removal_count = 2
        # 向左扩张
        idx = left_idx - 1
        while idx >= 0 and balls[idx]["color"] == color:
            removal_count += 1
            idx -= 1
        # 向右扩张
        idx = right_idx + 1
        while idx < len(balls) and balls[idx]["color"] == color:
            removal_count += 1
            idx += 1
    
    # 单向扩张
    else:
        removal_count = 1
        # 左球同色，向左扩张
        if ball1_color == color:
            idx = left_idx - 1
            while idx >= 0 and balls[idx]["color"] == color:
                removal_count += 1
                idx -= 1
        # 右球同色，向右扩张
        else:
            idx = right_idx + 1
            while idx < len(balls) and balls[idx]["color"] == color:
                removal_count += 1
                idx += 1

    if removal_count >= 2:
        return True, True, removal_count
    
    return True, False, 0

# 寻找最优解
def simulate_shot(frog: Dict, balls: List[Dict], new_ball_color: str) -> Tuple[bool, str, int]:
    frog_pos = frog["position"]
    best_directions = []  # 存储所有最优方向
    max_removal = 0
    
    n = len(balls)
    ball_idx = 0
    while ball_idx < n:
    # for ball_idx, ball in enumerate(balls):
        ball = balls[ball_idx]
        if ball["color"] == new_ball_color and can_hit(frog_pos, ball, balls):
            if are_adjacent(ball_idx, balls, new_ball_color):
                direction = get_direction(calculate_angle(frog_pos, ball["position"]))
                removal_count = 1
                left_idx, right_idx = ball_idx - 1, ball_idx + 1
                
                # 计算左侧相邻同色弹珠
                while left_idx >= 0 and balls[left_idx]["color"] == new_ball_color:
                    removal_count += 1
                    left_idx -= 1
                
                # 计算右侧相邻同色弹珠
                while right_idx < len(balls) and balls[right_idx]["color"] == new_ball_color:
                    removal_count += 1
                    right_idx += 1
                
                # 如果当前移除数大于最大值，清空并更新最佳方向
                if removal_count > max_removal:
                    max_removal = removal_count
                    best_directions = [direction]
                # 如果当前移除数等于最大值，添加方向
                elif removal_count == max_removal:
                    best_directions.append(direction)

                ball_idx = right_idx - 1

        ball_idx += 1
    
    if max_removal > 0:
        return True, best_directions, max_removal
    return False, [], 0


# 回答所有问题
def generate_qa(json_file: Union[str, None] = None) -> Dict[str, str]:
    if json_file is None:
        index = f"{np.random.randint(1, 3):04d}"  # 生成0001-0003的随机编号
        json_file = f"state/{index}.json"
    else:
        index = os.path.splitext(os.path.basename(json_file))[0]

    with open(json_file, "r") as f:
        data = json.load(f)

    # print(f"在图{index}:")
    
    frog = data["frog"]
    balls = data["balls"]
    plot_level = data["track"]["plot_level"]
    frog_pos = frog["position"]
    angle = frog["angle"]
    
    # 问题1/2
    if np.random.randint(0, 1):
        question1 = answer_question1(index, plot_level, frog)
    else: 
        question2 = answer_question2(index, plot_level, balls)

    # 问题3
    question3 = answer_question3(index, plot_level, frog_pos, balls)

    # 问题4
    question4 = answer_question4(index, plot_level, frog_pos, balls, angle)
    
    # 问题5
    question5 = answer_question5(index, plot_level, frog, balls)

    # 问题6
    question6 = answer_question6(index, plot_level, frog, balls)
    
    return {
        # "问题1": question1,
        # "问题2": question2,
        # "问题3": question3,
        # "问题4": question4,
        # "问题5": question5,
        # "问题6": question6
    }


def calculate_data_id(file_path: str) -> str:
    if not os.path.exists(file_path):
        return "00001"  # 如果文件不存在，序号从 1 开始
    with open(file_path, "r") as file:
        try:
            existing_data = json.load(file)
            max_index = max([int(item["data_id"].split("-")[-1]) for item in existing_data], default=0)
        except json.JSONDecodeError:
            max_index = 0
    return f"{max_index + 1:05d}"

def save_to_dataset(qa_data: Dict):
    target_file = "data.json"
    # 如果文件不存在，初始化为空列表
    if not os.path.exists(target_file):
        dataset = []
    else:
        with open(target_file, "r") as f:
            dataset = json.load(f)

    # 添加新的数据到列表
    dataset.append(qa_data)

    # 写回到文件
    with open(target_file, "w") as f:
        json.dump(dataset, f, indent=4)


question = (
    f"This is a Zuma game. "
    f"You need to control a frog to shoot colored marbles from its mouth toward a winding track of approaching marbles. "
    f"Your goal is to clear all marbles before they reach the black hole at the end of the track. "
    f"The marbles roll steadily along the track, and the player must fire marbles to create groups of three or more of the same color. "
    f"These groups will disappear, reducing the number of marbles on the track. "
    f"The frog will shoot marbles in a straight line, "
    f"if there is no marble on the track, the shooted marble will pass through the track. "
    f"However, the marble it shoots cannot bypass marbles already in its direct line of fire. "
    f"In the offered pictures, the frog is often represented as a long triangle, "
    f"with the circle on it representing the next marble it will shoot. "
    f"The colored marbles are positioned on a gray track. "
    f"Any directions or angles mentioned in questions are relative to the center of the circle on the frog, "
    f"with its positive x-axis as the 0-degree reference line. "
)

# 问题1：青蛙将要发射哪种颜色的弹珠？
def answer_question1(index: str, plot_level: str, frog: Dict) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-mcq-{calculate_data_id(file_path)}" # 格式化为五位序号
    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "StateInfo",
        "question_id": 1,
        "question_description": "The color of the marble that the frog is going to shoot.",
        "plot_level": plot_level,
        "qa_level": "Easy",
        "question": (question+
            "What color is the the marble that the frog is going to shoot? "
            "Answer in one of the following formats: 'red', 'yellow', 'blue', or 'green'."
        ),
        "answer": f"{frog['next_ball_color']}",
        "analysis": f"According to the color of the circle on the triangle(frog), the answer is {frog['next_ball_color']}.",
        "options": ["red", "yellow", "blue", "green"]
    }

    save_to_dataset(qa_data)
    return qa_data


# 问题2：目前轨道上一共有几个某种颜色的弹珠？
def answer_question2(index: str, plot_level: str, balls: List[Dict]) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-fill-{calculate_data_id(file_path)}" # 格式化为五位序号

    color = np.random.choice(["red", "yellow", "blue", "green"])
    number = sum(1 for ball in balls if ball["color"] == color)

    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "StateInfo",
        "question_id": 2,
        "question_description": f"Number of the {color} marbles on the track.",
        "plot_level": plot_level,
        "qa_level": "Easy",
        "question": (question+
            f"How many {color} marbles are there on the track? "
            f"Answer as a non-negative integer, such as '0', '1', '2', etc."
        ),
        "answer": f"{number}",
        "analysis": f"By counting the marbles on the track, it can be determined that there are {number} {color} marbles."
    }

    save_to_dataset(qa_data)
    return qa_data


# 问题3：在某方位有多少相邻同色弹珠组？
def answer_question3(index: str, plot_level: str, frog_pos: Dict[str, float], balls: List[Dict]) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-fill-{calculate_data_id(file_path)}" # 格式化为五位序号
    direction_ranges = {
        "up": "67.5 degrees ~ 112.5 degrees",
        "down": "-112.5 degrees ~ -67.5 degrees",
        "left": "157.5 degrees ~ 180 degrees or -180 degrees ~ -157.5 degrees",
        "right": "-22.5 degrees ~ 22.5 degrees",
        "up-left": "112.5 degrees ~ 157.5 degrees",
        "up-right": "22.5 degrees ~ 67.5 degrees",
        "down-left": "-157.5 degrees ~ -112.5 degrees",
        "down-right": "-67.5 degrees ~ -22.5 degrees"
    }
    direction = np.random.choice(["up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"])
    ball_groups = get_ball_in_direction(frog_pos, balls, direction)
    color_group_stats = {}  # 统计不同颜色的弹珠组信息

    # 遍历所有弹珠组，统计每种颜色的弹珠组数量及每种组的大小
    for group_start, group_end, color in ball_groups:
        group_size = group_end - group_start + 1  # 弹珠组的大小
        if color not in color_group_stats:
            color_group_stats[color] = {"total_groups": 0, "group_sizes": {}}
        # 更新统计
        color_group_stats[color]["total_groups"] += 1
        if group_size not in color_group_stats[color]["group_sizes"]:
            color_group_stats[color]["group_sizes"][group_size] = 0
        color_group_stats[color]["group_sizes"][group_size] += 1

    # 生成输出字符串
    analysis = [f"At the {direction} side of the frog(triangle)({direction_ranges[direction]}), there are {len(ball_groups)} groups of adjacent marbles with the same color"]
    analysis.append(f"{'.' if len(ball_groups) == 0 else ': '}")
    for color, stats in color_group_stats.items():
        analysis.append(f"{stats['total_groups']} {color} marble group ")
        size_details = []
        for size, count in stats["group_sizes"].items():
            size_details.append(f"{count} group with {size} marbles")
        analysis.append("including " + ", ".join(size_details) + ". ")
    analysis.append(f"So the answer is '{len(ball_groups)}'.")

    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "StateInfo",
        "question_id": 3,
        "question_description": f"Number of the groups of adjacent marbles with the same color at the {direction} side of the frog.",
        "plot_level": plot_level,
        "qa_level": "Medium",
        "question": (question+
            f"How many marble groups of two or more same-colored marbles are there at the {direction} side of the frog? "
            f"The direction '{direction}' refers to the region {direction_ranges[direction]}, which is already divided by dashed lines. "
            f"Any marble group with at least one marble in this region is considered to be in the '{direction}' direction. "
            f"Answer as a non-negative integer, such as '0', '1', '2', etc."
        ),
        "answer": f"{len(ball_groups)}",
        "analysis": "".join(analysis)
    }

    save_to_dataset(qa_data)
    return qa_data
    

# 问题4：青蛙朝某角度发射弹珠，会击中什么颜色的弹珠？
def answer_question4(index: str, plot_level: str, frog_pos: Dict[str, float], balls: List[Dict], angle: Dict[str, float]) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-mcq-{calculate_data_id(file_path)}" # 格式化为五位序号

    color = angle_shot_color(frog_pos, balls, angle)
    analysis = (
        f"To determine which marble the frog hits, we draw a ray from the frog's position "
        f"(the center of the circle inside the triangle) at an angle of {angle} degrees. "
        f"We then check if there is any marble within a distance of the diameter of the marble from this ray. "
        f"{'For there is no such marble, the frog does not hit any marble.' if color == 'none' else ''} "
        f"{'If there are marbles within this distance, we identify the closest marble to the frog, which is of color '+color+'. Thus, the frog hits this marble. ' if color != 'none' else ''}"
        f"So the answer is {color}. "
    )

    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "StateInfo",
        "question_id": 4,
        "question_description": f"The color of the marble that the frog hits if it shoots at {angle} degrees.",
        "plot_level": plot_level,
        "qa_level": "Medium",
        "question": (question+
            f"If the frog shoots the marble at {angle} degrees, as shown in the picture, what color is the marble it hits? "
            f"If it doesn't hit any marble, answer 'none'. "
            f"Answer in one of the following formats: 'red', 'yellow', 'blue', 'green', or 'none'."
        ),
        "answer": f"{color}",
        "analysis": analysis,
        "options": ["red", "yellow", "blue", "green", "none"]
    }

    save_to_dataset(qa_data)
    return qa_data


# 问题5：青蛙朝某角度发射弹珠，导致什么情况？
def answer_question5(index: str, plot_level: str, frog: Dict, balls: List[Dict]) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-fill-{calculate_data_id(file_path)}" # 格式化为五位序号

    angle = frog["angle"]
    color = frog["next_ball_color"]
    frog_pos = frog["position"]
    ball_color = angle_shot_color(frog_pos, balls, angle)
    is_hit, can_remove, removal_count = angle_shot_result(frog, balls)
    is_same_color = (color == ball_color) if is_hit else False

    if not is_hit:
        answer = "The marble left the field."
        analysis = (
            "The marble shot by the frog did not hit any marbles on the track, "
            "so the answer is 'The marble left the field.'."
        )
    elif is_hit and not can_remove:
        answer = "The marble stayed on the track."
        if is_same_color:
            analysis = (
                f"The marble shot by the frog hit a {ball_color} marble on the track. "
                "Although the hit marble is the same color as the shot marble, it does not belong to "
                "any group of two or more same-colored marbles, "
                "so the answer is 'The marble stayed on the track.'."
            )
        else:
            analysis = (
                f"The marble shot by the frog hit a {ball_color} marble on the track. "
                f"Firstly, the hit marble is a different color from the shot marble. "
                f"Secondly, there is not a marble group of two or more marbles which is the same color as the shot marble "
                f"on the side that the shot marble was inserted into. "
                f"So the answer is 'The marble stayed on the track.'."
            )
    else:
        answer = f"{removal_count} marbles on the track were removed."
        if is_same_color:
            analysis = (
                f"The marble shot by the frog hit a {ball_color} marble on the track. "
                f"Since the hit marble is the same color as the shot marble, and it belongs to "
                f"a group of {removal_count} same-colored marbles on the track, these marbles "
                f"were removed from the track. "
                f"So the answer is '{removal_count} marbles on the track were removed.'."
            )
        else:
            analysis = (
                f"The marble shot by the frog hit a {ball_color} marble on the track. "
                f"Although the hit marble is a different color from the shot marble, the side "
                f"the shot marble was inserted into has a group of {removal_count} same-colored marbles, "
                f"leading to the removal of {removal_count} marbles."
                f"So the answer is '{removal_count} marbles on the track were removed.'."
            )

    question_text = (
        f"If the frog shoots the marble at {angle} degrees, as shown in the picture, "
        "what will happen? Answer with one of the following options: "
        "'The marble left the field.', 'The marble stayed on the track.', or "
        "'[X] marbles on the track were removed.', where [X] is a positive integer."
    )

    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "ActionOutcome",
        "question_id": 5,
        "question_description": f"The state of the plot if the frog shoots at {angle} degrees.",
        "plot_level": plot_level,
        "qa_level": "Hard",
        "question": question+question_text,
        "answer": answer,
        "analysis": analysis
    }

    save_to_dataset(qa_data)
    return qa_data


# 问题6：是否能够通过发射这个球消除一些轨道上已有的弹珠？如果能，最多能消除多少弹珠（不算发射的弹珠）？有多少个最优解？
def answer_question6(index: str, plot_level: str, frog: Dict, balls: List[Dict]) -> Dict:
    file_path = "data.json"
    data_id = f"zuma-fill-{calculate_data_id(file_path)}" # 格式化为五位序号

    can_remove, directions, removal_count = simulate_shot(frog, balls, frog["next_ball_color"])
    direction_ranges = {
        "up": "67.5 degrees ~ 112.5 degrees",
        "down": "-112.5 degrees ~ -67.5 degrees",
        "left": "157.5 degrees ~ 180 degrees or -180 degrees ~ -157.5 degrees",
        "right": "-22.5 degrees ~ 22.5 degrees",
        "up-left": "112.5 degrees ~ 157.5 degrees",
        "up-right": "22.5 degrees ~ 67.5 degrees",
        "down-left": "-157.5 degrees ~ -112.5 degrees",
        "down-right": "-67.5 degrees ~ -22.5 degrees"
    }
    optimal_solution_count = len(directions)
    question_text = (
        f"Can the frog eliminate some marbles on the track by shooting the marble? "
        f"If yes, how many marbles (excluding the one being shot) can be eliminated in the best case? "
        f"How many distinct optimal solutions (counting different groups in the same direction separately) exist? "
        f"Answer in the format: '<Yes/No>, <number of eliminated marbles>, <number of optimal solutions>'. For example, 'Yes, 3, 2' or 'No, 0, 0'."
    )
    answer_text = (
        f"{'Yes' if can_remove else 'No'}, {removal_count if can_remove else 0}, {optimal_solution_count if can_remove else 0}"
    )

    if can_remove:
        direction_details = []
        for direction in set(directions):  # 可能有重复方位，使用 set 去重后遍历
            direction_details.append(f"{direction} ({direction_ranges[direction]})")
        direction_text = ", ".join(direction_details)
        analysis_text = (
            f"By searching for groups of marbles on the track that the frog can hit and eliminate, "
            f"we find that the best case allows for the elimination of {removal_count} consecutive marbles of color "
            f"{frog['next_ball_color']} in the directions {directions}. "
            f"This results in {optimal_solution_count} distinct optimal solutions. "
            f"The specific angle range for each direction is as follows: {direction_text}. "
            f"Any marble group with at least one marble in the region of the direction is considered to be in the region. "
            f"These regions have been divided by gray dashed lines in the image."
            f"So, the answer is '{answer_text}'."
        )
    else:
        analysis_text = (
            f"By searching for groups of marbles on the track that the frog can hit and eliminate, "
            f"we find that there are no groups of marbles on the track that the frog can hit and eliminate, "
            f"so the frog cannot eliminate any marbles."
            f"So, the answer is '{answer_text}'."
        )

    qa_data = {
        "data_id": data_id,
        "image": f"images/{index}.png",
        "state": f"states/{index}.json",
        "qa_type": "StrategyOptimization",
        "question_id": 6,
        "question_description": "The optimal strategy for eliminating marbles in one step.",
        "plot_level": plot_level,
        "qa_level": "Hard",
        "question": question+question_text,
        "answer": answer_text,
        "analysis": analysis_text
    }

    save_to_dataset(qa_data)
    return qa_data

# 测试代码
# answers = generate_qa("states/0003.json")
# for key, value in answers.items():
#     print(f"{key}: {value}")
