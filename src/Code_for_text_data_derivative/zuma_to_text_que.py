import json
import os
import math

def read_json(file_path):
    """Read and parse a JSON file with UTF-8 encoding."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def zuma_state_to_text(state_data):
    """Convert Zuma state data to a text description."""
    # 创建一个人类可读的文本描述
    text = "\n\nZUMA GAME STATE DESCRIPTION:\n"
    text += "This is a text representation of the current Zuma game state.\n"
    
    # 描述游戏的组成部分
    text += "The game consists of three main components: the track with a hole (hole radius = 0.6), a frog that shoots marbles, and colored marbles (marble radius = 0.3) on the track.\n\n"
    
    # Track description
    track_info = state_data.get("track", {})
    text += "TRACK INFORMATION:\n"
    text += f"Plot difficulty level: {track_info.get('plot_level', 'Unknown')}\n"
    
    hole_pos = track_info.get("hole_position", {})
    if hole_pos:
        text += f"Hole position: x={hole_pos.get('x', 0):.6f}, y={hole_pos.get('y', 0):.6f}\n\n"
    else:
        text += "Hole position information not available.\n\n"
    
    # Frog description
    frog_info = state_data.get("frog", {})
    text += "FROG INFORMATION:\n"
    
    frog_pos = frog_info.get("position", {})
    if frog_pos:
        text += f"Position: x={frog_pos.get('x', 0):.6f}, y={frog_pos.get('y', 0):.6f}\n"
    else:
        text += "Position information not available.\n"
    
    text += f"Shooting angle: {frog_info.get('angle', 'Unknown')} degrees\n"
    text += f"Next marble to shoot: {frog_info.get('next_ball_color', 'Unknown')}\n"
    
    # Marbles on track description
    balls = state_data.get("balls", [])
    text += "MARBLES ON TRACK:\n"
    if not balls:
        text += "No marbles on the track.\n"
    else:
        text += f"There are {len(balls)} marbles on the track.\n"
        
        # Describe the first few marbles for more detail
        text += f"\nColor and position of all the marbles on the track (from start to end/the hole):\n"
        for i in range(len(balls)):
            ball = balls[i]
            pos = ball.get("position", {})
            if pos:
                text += f"#{i+1}: {ball.get('color', 'Unknown')} marble at x={pos.get('x', 0):.6f}, y={pos.get('y', 0):.6f}\n"
            else:
                text += f"#{i+1}: {ball.get('color', 'Unknown')} marble (position unknown)\n"
    
    return text

def process_dataset():
    """Process the Zuma dataset to convert state JSON to text descriptions."""
    # 检查是否在正确的目录中
    if not os.path.exists("data.json"):
        print("Error: data.json not found in the current directory.")
        print("Please make sure you're running this script from the dataset directory.")
        return
    
    # 加载数据集
    try:
        data = read_json('data.json')
        processed_data = []
    except Exception as e:
        print(f"Failed to read data.json: {str(e)}")
        return
    
    # 处理每个条目
    for entry in data:
        try:
            # 获取状态路径并加载状态数据
            state_path = entry.get("state", "")
            if not state_path:
                print(f"Warning: No state path found for entry {entry.get('data_id', 'unknown')}")
                continue
                
            print(f"Processing entry: {entry.get('data_id', 'unknown')}")
            
            # 确保路径是正确的
            if not os.path.exists(state_path):
                print(f"State file does not exist: {state_path}")
                # 尝试修正路径
                base_state_path = os.path.basename(state_path)
                if os.path.exists(f"states/{base_state_path}"):
                    state_path = f"states/{base_state_path}"
                    print(f"Found state file at: {state_path}")
                else:
                    print(f"Cannot find state file, skipping entry")
                    continue
            
            try:
                state_data = read_json(state_path)
            except Exception as e:
                print(f"Error reading state file {state_path}: {str(e)}")
                # 如果无法读取状态文件，跳过此条目
                continue
            
            # 转换Zuma状态为文本
            text = zuma_state_to_text(state_data)
            
            # 创建一个带有修改后问题的新条目
            new_entry = entry.copy()
            
            # 添加说明，表明这是文本表示
            original_question = new_entry.get("question", "")
            
            # 找到插入点：找到 "Any directions or angles..." 这句话后面
            insertion_point = original_question.find("Any directions or angles mentioned in questions are relative to the center of the circle on the frog, with its positive x-axis as the 0-degree reference line.")
            
            if insertion_point != -1:
                # 在找到的句子后面插入文本
                insertion_point += len("Any directions or angles mentioned in questions are relative to the center of the circle on the frog, with its positive x-axis as the 0-degree reference line.")
                new_question = original_question[:insertion_point] + " " + text + "\nNOTE: This is a text representation of the game state, not a visual one. \nQUESTION:" + original_question[insertion_point:]
                new_entry["question"] = new_question
            else:
                # 如果找不到插入点，就直接在问题前面添加文本
                new_entry["question"] = text + "NOTE: This is a text representation of the game state, not a visual one. \nQUESTION:" + original_question
                
            processed_data.append(new_entry)
        
        except Exception as e:
            print(f"Error processing entry {entry.get('data_id', 'unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 保存处理后的数据
    try:
        with open('data_text.json', 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully processed {len(processed_data)} entries. Saved to data_text.json")
    except Exception as e:
        print(f"Error saving data_text.json: {str(e)}")

if __name__ == "__main__":
    process_dataset()