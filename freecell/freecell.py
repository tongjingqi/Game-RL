import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from copy import deepcopy
import heapq
from heapq import heappush,heappop
from dataclasses import replace
import os

# 四种花色(利用枚举)
class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

# 两种颜色(利用枚举)
class Color(Enum):
    RED = "red"
    BLACK = "black"

# Card
@dataclass
class Card:
    suit: Suit  # 花色
    value: int  # 数值取值为1-13,对应A,2,……,K
    
    # 通过花色获取card的颜色
    @property
    def color(self) -> Color:
        return Color.RED if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else Color.BLACK
    
    # 返回card的花色和数值
    def __str__(self) -> str:
        value_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        value_str = value_map.get(self.value, str(self.value))
        return f"{value_str} {self.suit.value}"

# 游戏实例
class FreeCell:
    def __init__(self,cascade_number):
        self.cascade_number=cascade_number
        self.cascade_piles: List[List[Card]] = [[] for _ in range(cascade_number)]   # 8个牌堆,牌数分别是7,7,7,7,6,6,6,6  放在游戏区
        self.free_cells: List[Optional[Card]] = [None] * 4      # 4个空闲堆,每个堆可以用于暂存一张牌
        self.foundation_piles: Dict[Suit, List[Card]] = {suit: [] for suit in Suit} # 基牌堆,放置结果
        self.initialize_game()  
    
    def initialize_game(self):  # 初始化游:把52张牌分配给游戏区的八个排队
        # Create deck 52张牌
        cards = [Card(suit, value) 
                for suit in Suit 
                for value in range(1, 14)]
        # 打乱牌的顺序并构造
        random.shuffle(cards)
            
        # Deal cards to cascade piles,把牌分到不同的牌堆中。 保证有77776666
        for i, card in enumerate(cards):
            pile_num = i % self.cascade_number
            self.cascade_piles[pile_num].append(card)
            
                


    def visualize(self, save_path=None, show=False):
        """
        Visualize the current state of FreeCell game using matplotlib
        
        Args:
            save_path (str, optional): Path to save the image. If None, image won't be saved.
            show (bool): Whether to display the plot. Default is True.
        """
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        
        # Create figure with specific DPI to achieve 640x480 resolution
        fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=100) # 设置图片大小,轴
        
        # Set background color and remove axes
        ax.set_facecolor('#2F4F4F')     # 轴的背景颜色
        fig.patch.set_facecolor('#2F4F4F')  # 图形背景颜色
        ax.axis('off')  # 轴不显示
        
        # Constants for layout
        CARD_WIDTH = 0.9    # 卡片宽度
        CARD_HEIGHT = 1.8   # 卡片高度
        SPACING = 0.2       # 两张卡片之间的距离
        OVERLAP = 0.4  # 卡片重叠的距离
        
        # Colors
        CELL_COLOR = '#1C352D'  # 单元格的颜色
        CARD_COLOR = 'white'    # 卡片颜色
        
        def draw_card(x, y, card, bottom_edge=True):
            """Helper function to draw a single card with border"""
            # Draw white card background with or without bottom edge   (x,y)是卡片左下角坐标
            ax.add_patch(Rectangle((x, y), CARD_WIDTH, CARD_HEIGHT, 
                                 facecolor=CARD_COLOR, 
                                 edgecolor='black', 
                                 linewidth=1,
                                 zorder=1))
            
            if card:
                color = 'red' if card.color.value == 'red' else 'black'
                # Calculate text position relative to the current card's position
                text_y = y + CARD_HEIGHT * 0.88  # Center of the current card
                ax.text(x + CARD_WIDTH/2, text_y, str(card), 
                       ha='center', va='center', 
                       color=color, 
                       fontsize=10, 
                       fontweight='bold',
                       zorder=2)
        
        # Draw Free Cells (top left)
        for i in range(4):
            x = i * (CARD_WIDTH + SPACING)
            y = 8
            # Draw empty cell background
            ax.add_patch(Rectangle((x, y), CARD_WIDTH, CARD_HEIGHT, 
                                 facecolor=CELL_COLOR, edgecolor='black', linewidth=1))
            if self.free_cells[i]:
                draw_card(x, y, self.free_cells[i])
        
        # Draw Foundation Piles (top right)
        for i, suit in enumerate(self.foundation_piles.keys()):
            x = (i + 4) * (CARD_WIDTH + SPACING)
            y = 8
            # Draw empty foundation cell
            ax.add_patch(Rectangle((x, y), CARD_WIDTH, CARD_HEIGHT, 
                                 facecolor=CELL_COLOR, edgecolor='black', linewidth=1))
            if self.foundation_piles[suit]:
                draw_card(x, y, self.foundation_piles[suit][-1])
        
        # Draw Cascade Piles
        for i, pile in enumerate(self.cascade_piles):
            x = i * (CARD_WIDTH + SPACING)
            # Draw cards in pile from bottom to top
            for j, card in enumerate(pile):
                y = 6 - (j * OVERLAP)
                # 最后一张牌显示完整边框，其他牌可能被遮挡
                is_last_card = j == len(pile) - 1
                draw_card(x, y, card, bottom_edge=is_last_card)
        
        # Set view limits
        ax.set_xlim(-0.2, 8.5)
        ax.set_ylim(-1, 10)
        
        # Add title
        plt.title('FreeCell Game State', color='white', pad=20, fontsize=14)
        
        # Tight layout to minimize margins
        plt.tight_layout()
        
        # Save image if path is provided
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
        
        # Show plot if requested
        if show:
            plt.show()
        
        # Close the figure to free memory
        plt.close()
    
    # 全部有效move
    def get_valid_moves(self):
        """
        获取当前 FreeCell 游戏状态的所有合法移动。
        返回一个列表，每个元素为一个合法移动的字典，包含 'card'、'from' 和 'to' 三个字段。
        """
        valid_moves = []
        # print("全部的有效move如下:")
        # 检查从牌堆到空闲单元的合法移动
        for pile_index, pile in enumerate(self.cascade_piles):
            if pile:  # 如果牌堆不为空
                card = pile[-1]  # 取最上面的牌
                for free_cell_index, free_cell in enumerate(self.free_cells):
                    if free_cell is None:  # 如果空闲单元是空的
                        valid_moves.append({
                            "card": card,
                            "from": f"Cascade {pile_index}",
                            "to": f"FreeCell {free_cell_index}"
                        })

        # 检查从牌堆到基础牌堆的合法移动
        for pile_index, pile in enumerate(self.cascade_piles):
            if pile:  # 如果牌堆不为空
                card = pile[-1]  # 取最上面的牌
                for suit, foundation_pile in self.foundation_piles.items():
                    if self._can_move_to_foundation(card, foundation_pile):  # 判断是否可以移动到基础牌堆
                        valid_moves.append({
                            "card": card,
                            "from": f"Cascade {pile_index}",
                            "to": f"Foundation {suit.value}"
                        })
                        # print(valid_moves)

        # 检查从空闲单元到基础牌堆的合法移动
        for free_cell_index, card in enumerate(self.free_cells):
            if card:  # 如果空闲单元有牌
                for suit, foundation_pile in self.foundation_piles.items():
                    if self._can_move_to_foundation(card, foundation_pile):  # 判断是否可以移动到基础牌堆
                        valid_moves.append({
                            "card": card,
                            "from": f"FreeCell {free_cell_index}",
                            "to": f"Foundation {suit.value}"
                        })
                        # print(valid_moves)

        # 检查从空闲单元到牌堆的合法移动
        for free_cell_index, card in enumerate(self.free_cells):
            if card:  # 如果空闲单元有牌
                for pile_index, pile in enumerate(self.cascade_piles):
                    if self._can_move_to_cascade(card, pile):  # 判断是否可以移动到牌堆
                        valid_moves.append({
                            "card": card,
                            "from": f"FreeCell {free_cell_index}",
                            "to": f"Cascade {pile_index}"
                        })

        # 检查从一个牌堆到另一个牌堆的合法移动
        for from_pile_index, from_pile in enumerate(self.cascade_piles):
            if from_pile:  # 如果起始牌堆不为空
                card = from_pile[-1]  # 取最上面的牌
                for to_pile_index, to_pile in enumerate(self.cascade_piles):
                    if from_pile_index != to_pile_index and self._can_move_to_cascade(card, to_pile):
                        valid_moves.append({
                            "card": card,
                            "from": f"Cascade {from_pile_index}",
                            "to": f"Cascade {to_pile_index}"
                        })

        return valid_moves

    def get_all_possible_moves(self):
        """
        获取当前游戏状态下的所有可能的移动组合，涵盖所有来源和目标。
        返回一个列表，其中每个元素为一个合法移动的字典。
        """
        possible_moves = []
        # print("全部的可能move如下:")
        # 从牌堆到其他位置
        for from_pile_index, from_pile in enumerate(self.cascade_piles):
            if from_pile:  # 如果牌堆不为空
                card = from_pile[-1]  # 取牌堆顶部的牌

                # 检查是否可以移动到空闲单元
                for free_cell_index, free_cell in enumerate(self.free_cells):
                    if free_cell is None:  # 空闲单元为空
                        possible_moves.append({
                            "card": card,
                            "from": f"Cascade {from_pile_index}",
                            "to": f"FreeCell {free_cell_index}"
                        })

                # 检查是否可以移动到基础牌堆
                for suit, foundation_pile in self.foundation_piles.items():
                    if self._can_move_to_foundation(card, foundation_pile):
                        possible_moves.append({
                            "card": card,
                            "from": f"Cascade {from_pile_index}",
                            "to": f"Foundation {suit.value}"
                        })
                        # print(possible_moves)

                # 检查是否可以移动到其他牌堆
                for to_pile_index, to_pile in enumerate(self.cascade_piles):
                    if from_pile_index != to_pile_index and self._can_move_to_cascade(card, to_pile):
                        possible_moves.append({
                            "card": card,
                            "from": f"Cascade {from_pile_index}",
                            "to": f"Cascade {to_pile_index}"
                        })

        # 从空闲单元到其他位置
        for free_cell_index, card in enumerate(self.free_cells):
            if card:  # 如果空闲单元有牌
                # 检查是否可以移动到基础牌堆
                for suit, foundation_pile in self.foundation_piles.items():
                    if self._can_move_to_foundation(card, foundation_pile):
                        possible_moves.append({
                            "card": card,
                            "from": f"FreeCell {free_cell_index}",
                            "to": f"Foundation {suit.value}"
                        })
                        # print(possible_moves)

                # 检查是否可以移动到牌堆
                for to_pile_index, to_pile in enumerate(self.cascade_piles):
                    if self._can_move_to_cascade(card, to_pile):
                        possible_moves.append({
                            "card": card,
                            "from": f"FreeCell {free_cell_index}",
                            "to": f"Cascade {to_pile_index}"
                        })

        return possible_moves
 
    # 判断是否能移动到基堆
    def _can_move_to_foundation(self, card, foundation_pile):
        """
        判断是否可以将给定的牌移动到基础牌堆。
        """
        if not foundation_pile:  # 基础牌堆为空
            return card.value == 1  # 只有A可以放置到空的基础牌堆
        top_card = foundation_pile[-1]
        return card.suit == top_card.suit and card.value == top_card.value + 1

    def _can_move_to_cascade(self, card, cascade_pile):
        """
        判断是否可以将给定的牌移动到牌堆。
        """
        if not cascade_pile:  # 如果目标牌堆为空
            return True  # 任何牌都可以放置到空的牌堆
        top_card = cascade_pile[-1]
        return (card.color != top_card.color) and (card.value == top_card.value - 1)
    
    
    # 判断是否还有free_cell
    def has_free_cell(self):
        """
        判断是否有空闲单元格
        """
        # 如果free_cells中有一个单元格是空的，则说明有空闲单元格
        return any(cell is None for cell in self.free_cells)
    
    def get_state_hash(self):
        """生成当前游戏状态的哈希值,用于判断重复状态"""
        state = []
        # 添加cascade_piles的状态
        for pile in self.cascade_piles:
            state.append(tuple((card.suit, card.value) for card in pile))
        # 添加free_cells的状态
        state.append(tuple((card.suit, card.value) if card else None for card in self.free_cells))
        # 添加foundation_piles的状态
        for suit in Suit:
            pile = self.foundation_piles[suit]
            state.append(tuple((card.suit, card.value) for card in pile))
        return hash(tuple(state))

    def evaluate_state(self):
        """评估当前状态的得分,用于启发式搜索
        较低的分数表示状态更好
        """
        score = 0
        # 基础牌堆中的牌越多越好
        for suit, pile in self.foundation_piles.items():
            score -= len(pile) * 10
        
        # 空闲单元格越多越好
        empty_cells = sum(1 for cell in self.free_cells if cell is None)
        score -= empty_cells * 5
        
        # 牌堆中顺序正确的牌得分
        for pile in self.cascade_piles:
            for i in range(len(pile)-1):
                current_card = pile[i]
                next_card = pile[i+1]
                if (current_card.color != next_card.color and 
                    current_card.value == next_card.value + 1):
                    score -= 2
        
        return score

    def apply_move(self, move):
        """应用一个移动到当前游戏状态"""
        from_loc, to_loc = move["from"].split(), move["to"].split()
        card = move["card"]
        
        # 从源位置移除卡牌
        if from_loc[0] == "Cascade":
            pile_index = int(from_loc[1])
            self.cascade_piles[pile_index].pop()
        elif from_loc[0] == "FreeCell":
            cell_index = int(from_loc[1])
            self.free_cells[cell_index] = None
            
        # 将卡牌添加到目标位置
        if to_loc[0] == "Cascade":
            pile_index = int(to_loc[1])
            self.cascade_piles[pile_index].append(card)
        elif to_loc[0] == "FreeCell":
            cell_index = int(to_loc[1])
            self.free_cells[cell_index] = card
        elif to_loc[0] == "Foundation":
            suit = next(s for s in Suit if s.value == to_loc[1])
            self.foundation_piles[suit].append(card)

    def undo_move(self, move):
        """撤销一个移动"""
        from_loc, to_loc = move["from"].split(), move["to"].split()
        card = move["card"]
        
        # 从目标位置移除卡牌
        if to_loc[0] == "Cascade":
            pile_index = int(to_loc[1])
            self.cascade_piles[pile_index].pop()
        elif to_loc[0] == "FreeCell":
            cell_index = int(to_loc[1])
            self.free_cells[cell_index] = None
        elif to_loc[0] == "Foundation":
            suit = next(s for s in Suit if s.value == to_loc[1])
            self.foundation_piles[suit].pop()
            
        # 将卡牌放回源位置
        if from_loc[0] == "Cascade":
            pile_index = int(from_loc[1])
            self.cascade_piles[pile_index].append(card)
        elif from_loc[0] == "FreeCell":
            cell_index = int(from_loc[1])
            self.free_cells[cell_index] = card

    def is_solved(self):
        """检查游戏是否已解决"""
        return all(len(pile) == 13 for pile in self.foundation_piles.values())

    def solve(self):
        """Solves the current FreeCell game state
        Returns:
            solution: List[Dict] - list of moves
            analysis: str - condensed analysis log
        """
        analysis = []
        visited_states = set()
        min_heap = []  # (score, moves_count, move_id, moves)
        move_counter = 0
        milestone_moves = 100  # Record analysis every X moves
        best_score = float('inf')
        
        # Initial state
        initial_state_hash = self.get_state_hash()
        initial_score = self.evaluate_state()
        heapq.heappush(min_heap, (initial_score, 0, move_counter, []))
        visited_states.add(initial_state_hash)
        
        analysis.append(f"Starting FreeCell analysis with initial score: {initial_score}")
        moves_tried = 0
        
        while min_heap and moves_tried < 200:
            current_score, moves_count, _, current_moves = heapq.heappop(min_heap)
            moves_tried += 1
            
            # Only record when there's significant progress
            if current_score < best_score:
                best_score = current_score
                analysis.append(f"New best score found: {best_score} at move {moves_tried}")
            
            # Record milestone updates
            if moves_tried % milestone_moves == 0:
                analysis.append(f"Progress update - Moves tried: {moves_tried}, Current best score: {best_score}")
            
            # Restore to current state
            game_copy = deepcopy(self)
            for move in current_moves:
                game_copy.apply_move(move)
            
            # Check if solved
            if game_copy.is_solved():
                analysis.append(f"Solution found after {moves_tried} moves!")
                analysis.append(f"Final path length: {len(current_moves)} moves")
                return current_moves, "\n".join(analysis)
            
            # Get and try possible moves
            possible_moves = game_copy.get_valid_moves()
            
            # Only record if number of possible moves is notably low
            if len(possible_moves) < 3:
                analysis.append(f"Limited options at move {moves_tried}: {len(possible_moves)} possible moves")
            
            for move in possible_moves:
                game_copy.apply_move(move)
                analysis.append(f"Exploaring move {move} at move {moves_tried}")
                new_state_hash = game_copy.get_state_hash()
                
                if new_state_hash not in visited_states:
                    move_counter += 1
                    new_score = game_copy.evaluate_state()
                    new_moves = current_moves + [move]
                    heapq.heappush(min_heap, (new_score, len(new_moves), move_counter, new_moves))
                    visited_states.add(new_state_hash)
                
                game_copy.undo_move(move)
        
        analysis.append(f"Search terminated after {moves_tried} moves without finding a solution")
        return [], "\n".join(analysis)