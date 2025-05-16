import random
from collections import deque

# 定义花色和牌面
SUITS = ['H', 'D', 'C', 'S']
VALUES = list(range(1, 14))  # 1到13

# 卡牌类，表示一张牌
class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return f"{self.value}{self.suit}"

# 初始化牌堆
def initialize_deck():
    deck = [Card(suit, value) for suit in SUITS for value in VALUES]
    random.shuffle(deck)
    return deck

# 初始化FreeCell游戏
def initialize_game():
    deck = initialize_deck()
    cascade_piles = [deque() for _ in range(8)]  # 8个堆叠
    for i in range(8):
        for _ in range(7):
            if deck:
                cascade_piles[i].append(deck.pop())
    
    foundation_piles = [[] for _ in range(4)]  # 4个基础堆
    free_cells = [None] * 4  # 4个空闲堆
    
    return cascade_piles, foundation_piles, free_cells

# 判断一张卡牌是否可以放到基础堆
def can_place_on_foundation(card, foundation_pile):
    if not foundation_pile:
        return card.value == 1  # 只有1可以放到空基础堆
    top_card = foundation_pile[-1]
    return card.suit == top_card.suit and card.value == top_card.value + 1

# 判断一张卡牌是否可以放到另一个堆叠
def can_place_on_cascade(card, cascade_pile):
    if not cascade_pile:
        return True  # 空堆叠可以放任何卡牌
    top_card = cascade_pile[-1]
    return card.value == top_card.value - 1 and ((card.suit == 'H' or card.suit == 'D') != (top_card.suit == 'H' or top_card.suit == 'D'))

# 定义合法的移动操作
def get_legal_moves(cascade_piles, foundation_piles, free_cells):
    moves = []
    
    # 从堆叠移动到空闲堆
    for i, pile in enumerate(cascade_piles):
        if pile:
            card = pile[-1]
            for j in range(4):
                if free_cells[j] is None:
                    moves.append(('cascade_to_free', i, j))
    
    # 从堆叠移动到基础堆
    for i, pile in enumerate(cascade_piles):
        if pile:
            card = pile[-1]
            for j, foundation_pile in enumerate(foundation_piles):
                if can_place_on_foundation(card, foundation_pile):
                    moves.append(('cascade_to_foundation', i, j))
    
    # 从空闲堆移动到堆叠
    for i in range(4):
        if free_cells[i] is not None:
            card = free_cells[i]
            for j, pile in enumerate(cascade_piles):
                if can_place_on_cascade(card, pile):
                    moves.append(('free_to_cascade', i, j))
    
    # 从空闲堆移动到基础堆
    for i in range(4):
        if free_cells[i] is not None:
            card = free_cells[i]
            for j, foundation_pile in enumerate(foundation_piles):
                if can_place_on_foundation(card, foundation_pile):
                    moves.append(('free_to_foundation', i, j))
    
    return moves

# 执行移动
def execute_move(move, cascade_piles, foundation_piles, free_cells):
    if move[0] == 'cascade_to_free':
        pile_index = move[1]
        free_index = move[2]
        card = cascade_piles[pile_index].pop()
        free_cells[free_index] = card
    elif move[0] == 'cascade_to_foundation':
        pile_index = move[1]
        foundation_index = move[2]
        card = cascade_piles[pile_index].pop()
        foundation_piles[foundation_index].append(card)
    elif move[0] == 'free_to_cascade':
        free_index = move[1]
        pile_index = move[2]
        card = free_cells[free_index]
        free_cells[free_index] = None
        cascade_piles[pile_index].append(card)
    elif move[0] == 'free_to_foundation':
        free_index = move[1]
        foundation_index = move[2]
        card = free_cells[free_index]
        free_cells[free_index] = None
        foundation_piles[foundation_index].append(card)

# 检查游戏是否完成
def is_game_solved(foundation_piles):
    return all(len(pile) == 13 for pile in foundation_piles)

def solve_freecell(cascade_piles, foundation_piles, free_cells, depth=0, visited=None):
    if visited is None:
        visited = set()

    # 将当前状态转化为可哈希的类型进行记录（例如元组）
    current_state = tuple(tuple(pile) for pile in cascade_piles)
    
    # 如果当前状态已经被访问过，停止递归
    if current_state in visited:
        return False
    
    # 记录当前状态
    visited.add(current_state)

    if is_game_solved(foundation_piles):
        return True

    moves = get_legal_moves(cascade_piles, foundation_piles, free_cells)
    if not moves:
        return False

    for move in moves:
        # 保存当前状态用于回溯
        backup_cascade_piles = [pile.copy() for pile in cascade_piles]
        backup_foundation_piles = [pile.copy() for pile in foundation_piles]
        backup_free_cells = free_cells[:]
        
        execute_move(move, cascade_piles, foundation_piles, free_cells)
        
        # 递归尝试
        if solve_freecell(cascade_piles, foundation_piles, free_cells, depth + 1, visited):
            return True
        
        # 回溯
        cascade_piles = backup_cascade_piles
        foundation_piles = backup_foundation_piles
        free_cells = backup_free_cells

    return False

# 主程序
if __name__ == "__main__":
    cascade_piles, foundation_piles, free_cells = initialize_game()
    visited=set()
    print("初始牌局：")
    for i, pile in enumerate(cascade_piles):
        print(f"堆叠{i + 1}: {list(pile)}")
    
    if solve_freecell(cascade_piles, foundation_piles, free_cells,visited=visited):
        print("游戏已成功解决！")
    else:
        print("没有找到解决方案。")
