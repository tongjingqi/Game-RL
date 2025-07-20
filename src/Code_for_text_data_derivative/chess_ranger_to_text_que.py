import json
from pathlib import Path

# 国际象棋棋子名称映射
PIECE_NAMES = {
    "K": "King",
    "Q": "Queen",
    "R": "Rook",
    "B": "Bishop",
    "N": "Knight",
    "P": "Pawn"
}

def load_data(json_path):
    """加载原始数据文件"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(json_path, data):
    """保存处理后的数据"""
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def index_to_chess_coord(row_idx, col_idx):
    """将数组索引转换为国际象棋坐标"""
    # 行号转换（数组行索引0对应棋盘第8行）
    row_number = 8 - row_idx
    # 列字母转换（数组列索引0对应a列）
    col_letter = chr(ord('a') + col_idx)
    return f"{col_letter}{row_number}"

def generate_piece_description(state_data):
    """生成棋子位置描述文本"""
    board = state_data["mine_board"]
    pieces = []
    
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell != 0 and str(cell).strip():
                piece_type = PIECE_NAMES.get(str(cell).upper(), "Unknown")
                coord = index_to_chess_coord(row_idx, col_idx)
                pieces.append(f"{piece_type} at {coord}")
    
    return "Current pieces positions:\n" + ",\n".join(pieces)

def process_entry(entry):
    """处理单个数据条目"""
    state_path = Path(entry["state"])
    
    # 加载棋盘状态文件
    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")
    
    with open(state_path, 'r', encoding='utf-8') as f:
        state_data = json.load(f)
    
    # 生成描述文本
    board_desc = generate_piece_description(state_data)
    
    # 构建新question内容
    new_question = (
        f"{board_desc}\n\n"
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