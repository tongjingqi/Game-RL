import json
import os
import pprint  # 用于漂亮打印调试输出

def read_json(file_path):
    """Read and parse a JSON file with UTF-8 encoding."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def klondike_state_to_text(state_data):
    """Convert Klondike state data to a text description."""
    # 打印状态数据结构，调试用
    print("State data structure:")
    pprint.pprint(state_data)
    
    # 尝试查找各种可能的键名，以适应不同的状态格式
    # 对于stock
    stock = []
    for key in ["stock", "stockPile", "deck"]:
        if key in state_data:
            stock = state_data[key]
            break
    
    # 对于waste
    waste = []
    for key in ["waste", "wastePile", "discard"]:
        if key in state_data:
            waste = state_data[key]
            break
            
    # 对于foundation
    foundation = []
    for key in ["foundation", "foundationPiles", "foundations"]:
        if key in state_data:
            foundation = state_data[key]
            break
            
    # 对于tableau
    tableau = []
    for key in ["tableau", "tableauPiles", "columns", "piles"]:
        if key in state_data:
            tableau = state_data[key]
            break
    
    # 创建一个人类可读的文本描述
    text = "KLONDIKE BOARD DESCRIPTION:\n\n"
    text += "This is a text representation of the current Klondike solitaire game state.\n\n"
    text += "The game consists of four areas: stock pile, waste pile, foundation piles, and tableau piles.\n\n"
    
    # Stock pile description
    text += "STOCK PILE:\n"
    if not stock:
        text += "The stock pile is empty.\n\n"
    else:
        text += f"The stock pile contains {len(stock)} face-down cards.\n\n"
    
    # Waste pile description
    text += "WASTE PILE:\n"
    if not waste:
        text += "The waste pile is empty.\n\n"
    else:
        # 检查waste是列表还是字典
        if isinstance(waste, dict):
            waste = [waste]  # 如果是字典，转为单元素列表
            
        visible_waste = []
        for card in waste:
            if isinstance(card, dict) and card.get("faceUp", False):
                visible_waste.append(card)
            # 如果卡牌没有faceUp属性但有其他属性标识可见，也添加
            elif isinstance(card, dict) and any(key in card for key in ["visible", "shown", "revealed"]):
                visible_waste.append(card)
        
        if visible_waste:
            top_card = visible_waste[-1]
            text += f"The top card is {format_card(top_card)}.\n"
            if len(visible_waste) > 1:
                text += f"There are {len(visible_waste) - 1} more face-up cards beneath it.\n"
        text += f"Total cards in waste pile: {len(waste)}.\n\n"
    
    # Foundation piles description
    text += "FOUNDATION PILES:\n"
    if not foundation:
        text += "All foundation piles are empty.\n\n"
    else:
        # 检查foundation是否是列表列表或列表字典
        if not isinstance(foundation, list):
            foundation = [foundation]
        
        for i, pile in enumerate(foundation):
            if not pile:
                text += f"Foundation pile {i+1}: Empty\n"
            else:
                # 如果pile是字典而不是列表
                if isinstance(pile, dict):
                    if "cards" in pile:  # 如果是{"cards": [...]}格式
                        cards = pile["cards"]
                        if cards:
                            top_card = cards[-1]
                            text += f"Foundation pile {i+1}: Top card is {format_card(top_card)}\n"
                        else:
                            text += f"Foundation pile {i+1}: Empty\n"
                    elif "topCard" in pile:  # 如果是{"topCard": {...}}格式
                        text += f"Foundation pile {i+1}: Top card is {format_card(pile['topCard'])}\n"
                    else:
                        text += f"Foundation pile {i+1}: Has cards but format unknown\n"
                else:  # 如果pile是列表
                    if pile:
                        top_card = pile[-1]
                        text += f"Foundation pile {i+1}: Top card is {format_card(top_card)}\n"
                    else:
                        text += f"Foundation pile {i+1}: Empty\n"
        text += "\n"
    
    # Tableau piles description
    text += "TABLEAU PILES:\n"
    if not tableau:
        text += "No tableau piles information available.\n"
    else:
        # 检查tableau是否是列表列表或列表字典
        if not isinstance(tableau, list):
            # 尝试处理其他格式
            if isinstance(tableau, dict):
                # 转换为列表格式
                tableau_list = []
                for i in range(1, 8):  # 假设有7个tableau堆
                    key = str(i)
                    if key in tableau:
                        tableau_list.append(tableau[key])
                    else:
                        tableau_list.append([])
                tableau = tableau_list
        
        for i, pile in enumerate(tableau):
            text += f"Tableau pile {i+1}: "
            if not pile:
                text += "Empty\n"
            else:
                # 检查pile是字典还是列表
                if isinstance(pile, dict):
                    if "cards" in pile:  # 如果是{"cards": [...]}格式
                        cards = pile["cards"]
                    else:
                        cards = []  # 没有找到cards属性
                else:
                    cards = pile  # pile已经是卡牌列表
                
                if not cards:
                    text += "Empty\n"
                    continue
                    
                face_down = 0
                face_up = []
                
                for card in cards:
                    if isinstance(card, dict):
                        # 检查各种可能表示卡牌朝上的属性
                        is_face_up = False
                        for key in ["faceUp", "visible", "shown", "revealed"]:
                            if key in card and card[key]:
                                is_face_up = True
                                break
                        
                        if is_face_up:
                            face_up.append(card)
                        else:
                            face_down += 1
                    else:
                        # 如果不是字典而是简单的卡牌代码，假定是可见的
                        face_up.append(card)
                
                if face_down > 0:
                    text += f"{face_down} face-down card(s)"
                    if face_up:
                        text += " followed by "
                
                if face_up:
                    cards_text = ", ".join(format_card(card) for card in face_up)
                    text += f"face-up cards: {cards_text}"
                text += "\n"
    
    return text

def format_card(card):
    """Format a card object as a human-readable string."""
    if not isinstance(card, dict):
        # 如果不是字典，尝试解析简单的卡牌代码（如 "AH", "10C"等）
        card_str = str(card)
        if len(card_str) >= 2:
            # 提取最后一个字符作为花色
            suit_code = card_str[-1]
            # 其余部分作为点数
            rank_code = card_str[:-1]
            
            rank_map = {"A": "Ace", "2": "2", "3": "3", "4": "4", "5": "5", 
                        "6": "6", "7": "7", "8": "8", "9": "9", "10": "10", 
                        "J": "Jack", "Q": "Queen", "K": "King"}
            suit_map = {"H": "Hearts", "D": "Diamonds", "C": "Clubs", "S": "Spades",
                        "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
            
            rank = rank_map.get(rank_code, rank_code)
            suit = suit_map.get(suit_code, suit_code)
            
            return f"{rank} of {suit}"
        return str(card)
        
    # 检查各种可能表示卡牌朝上的属性
    is_face_up = False
    for key in ["faceUp", "visible", "shown", "revealed"]:
        if key in card and card[key]:
            is_face_up = True
            break
            
    if not is_face_up:
        return "face-down card"
    
    # 尝试多种方式获取花色和点数
    suit = None
    rank = None
    
    # 尝试获取花色
    for suit_key in ["suit", "suitName", "suitSymbol"]:
        if suit_key in card:
            suit = card[suit_key]
            break
    
    # 尝试获取点数
    for rank_key in ["rank", "rankName", "value", "val"]:
        if rank_key in card:
            rank = card[rank_key]
            break
        
    # 如果没有找到花色和点数，尝试解析code
    if (suit is None or rank is None) and "code" in card:
        code = card["code"]
        if len(code) >= 2:
            rank_code = code[0] if code[0] != "1" else "10" if len(code) > 2 and code[1] == "0" else code[0]
            suit_code = code[-1]
            
            rank_map = {"A": "Ace", "2": "2", "3": "3", "4": "4", "5": "5", 
                        "6": "6", "7": "7", "8": "8", "9": "9", "0": "10", 
                        "J": "Jack", "Q": "Queen", "K": "King"}
            suit_map = {"H": "Hearts", "D": "Diamonds", "C": "Clubs", "S": "Spades",
                        "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
            
            if rank is None:
                rank = rank_map.get(rank_code, rank_code)
            if suit is None:
                suit = suit_map.get(suit_code, suit_code)
    
    # 如果还是没找到，返回整个卡牌对象的字符串表示
    if suit is None and rank is None:
        return str(card)
    
    # 转换数字点数为名称
    rank_names = {
        "1": "Ace",
        "11": "Jack",
        "12": "Queen",
        "13": "King"
    }
    
    rank_display = rank_names.get(str(rank), str(rank))
    
    # 使用花色符号或名称
    suit_names = {
        "hearts": "Hearts",
        "diamonds": "Diamonds",
        "clubs": "Clubs",
        "spades": "Spades",
        "h": "Hearts",
        "d": "Diamonds",
        "c": "Clubs",
        "s": "Spades",
        "♥": "Hearts",
        "♦": "Diamonds",
        "♣": "Clubs",
        "♠": "Spades"
    }
    
    if isinstance(suit, str):
        suit_display = suit_names.get(suit.lower(), suit)
    else:
        suit_display = str(suit)
    
    return f"{rank_display} of {suit_display}"

def process_dataset():
    """Process the Klondike dataset to convert image references to text descriptions."""
    # 检查是否在正确的目录中
    if not os.path.exists("data.json"):
        print("Error: data.json not found in the current directory.")
        print("Please make sure you're running this script from the dataset directory.")
        return
    
    # 加载数据集
    try:
        data = read_json('data.json')
        processed_data = []
    except UnicodeDecodeError:
        print("Encountered an encoding error. Trying alternative approach...")
        # 如果UTF-8失败，尝试以二进制读取并使用'utf-8-sig'解码
        try:
            with open('data.json', 'rb') as f:
                content = f.read()
                data = json.loads(content.decode('utf-8-sig'))
                processed_data = []
        except Exception as e:
            print(f"Failed to read data.json: {str(e)}")
            return
    
    # 处理每个条目
    for entry in data:
        try:
            # 获取状态路径并加载状态数据
            state_path = entry.get("state", "")
            if isinstance(state_path, str) and not state_path:
                print(f"Warning: No state path found for entry {entry.get('data_id', 'unknown')}")
                continue
                
            # 打印正在处理的条目信息以便调试
            print(f"Processing entry: {entry.get('data_id', 'unknown')}")
            print(f"State path: {state_path}")
            
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
            except UnicodeDecodeError:
                print(f"Encoding issue with {state_path}, trying alternative approach...")
                with open(state_path, 'rb') as f:
                    content = f.read()
                    state_data = json.loads(content.decode('utf-8-sig'))
            except Exception as e:
                print(f"Error reading state file {state_path}: {str(e)}")
                # 如果无法读取状态文件，跳过此条目
                continue
            
            # 转换Klondike状态为文本
            text = klondike_state_to_text(state_data)
            
            # 创建一个带有修改后问题的新条目
            new_entry = entry.copy()
            
            # 添加说明，表明这是文本表示
            original_question = new_entry.get("question", "")
            if isinstance(original_question, str):
                new_entry["question"] = text + "NOTE: This is a text representation of the game state, not a visual one.\n\n" + original_question
            else:
                new_entry["question"] = text + "NOTE: This is a text representation of the game state, not a visual one.\n\n"
                print(f"Warning: Question for entry {entry.get('data_id', 'unknown')} is not a string.")

            # 删除图像引用但保留状态引用以便调试
            if "image" in new_entry:
                del new_entry["image"]
                
            processed_data.append(new_entry)
        
        except Exception as e:
            print(f"Error processing entry {entry.get('data_id', 'unknown')}: {str(e)}")
            # 打印更多详细信息以便调试
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