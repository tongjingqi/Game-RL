import json
from pathlib import Path

# 颜色代码到名称的映射
COLOR_MAP = {
    "#FF0000": "red",
    "#00FF00": "green",
    "#0000FF": "blue",
    "#FF00FF": "magenta",
    "#FFFF00": "yellow",
    "#00FFFF": "aqua",
    "#696969": "gray",
    "#A020F0": "purple",
    "#228B22": "forest green"
}

def load_data(json_path):
    """加载原始数据文件"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(json_path, data):
    """保存处理后的数据"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_color_name(hex_code):
    """获取颜色名称，未知颜色返回unknown"""
    return COLOR_MAP.get(hex_code, "unknown")

def generate_board_description(state_data):
    """生成棋盘描述文本"""
    size = state_data["size"]
    board = state_data["board"]
    color_hexs = state_data["colors"]
    
    # 转换HEX颜色码为名称
    color_names = [get_color_name(code) for code in color_hexs]
    
    # 生成每行描述
    rows = []
    for row_num, row in enumerate(board, 1):
        cells = []
        for val in row:
            if val == 0:
                cells.append("empty")
            else:
                try:
                    cells.append(color_names[val-1])
                except IndexError:
                    cells.append("invalid")
        rows.append(f"row{row_num}: [{', '.join(cells)}]")
    
    # 生成颜色对应关系
    color_mapping = [f"{i+1}: {name}" for i, name in enumerate(color_names)]
    
    return "\n".join(rows), "the color corresponding to the numbers is " + ", ".join(color_mapping) + "."

def process_entry(entry):
    """处理单个数据条目"""
    state_path = Path(entry["state"])
    
    # 加载棋盘状态文件
    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")
    
    with open(state_path, 'r', encoding='utf-8') as f:
        state_data = json.load(f)
    
    # 生成描述文本
    board_desc, color_desc = generate_board_description(state_data)
    
    # 构建新question内容
    new_question = (
        f"Current board state:\n{board_desc}"
        #f"{color_desc}"
        f"{entry['question']}"
    )
    
    entry["question"] = new_question
    return entry

def main():
    # 加载原始数据
    data = load_data("data.json")
    
    # 处理每个条目
    processed_data = [process_entry(entry) for entry in data]
    
    # 保存结果（建议先备份原始文件）
    save_data("data_text.json", processed_data)

if __name__ == "__main__":
    main()