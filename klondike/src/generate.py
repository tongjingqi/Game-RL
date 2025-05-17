from constants import KLONDIKE_GAME_DESCR_GENERAL, DEADLOCK_DESCR, EFFECTIVE_MOVE_DESCR
from typing import Literal, List, Dict, Any
import random
import json
import os
import uuid
import itertools
class KlondikeQAGenerator:
    """
    Generate question and answer data for Klondike Solitaire game states
    """
    def __init__(self, game_state: Dict[str, Any]):
        self.tableau = game_state.get("tableau", [])
        self.foundation = game_state.get("piles", [])
        self.draw_pile = game_state.get("draw", [])
        self.waste_pile = game_state.get("dump", [])

    def _parse_card(self, card_str: str) -> Dict[str, Any]:
        """
        Parse a card string into a structured representation
        e.g., 'heart 1' or '<Card>'
        """
        if str(card_str).startswith('<Card'):
            return {
                'suit': '',
                'rank': '',
                'faceup': False
            }
        
        # Split the card string
        parts = str(card_str).split()
        if len(parts) < 2:
            return {
                'suit': '',
                'rank': '',
                'faceup': False
            }
        
        return {
            'suit': parts[0],
            'rank': parts[1],
            'faceup': True
        }

    def _can_move_to_tableau(self, source_card: Dict[str, Any], target_card: Dict[str, Any] = None) -> bool:
        """
        Check if a card can be moved to a tableau pile
        """
        if not source_card['faceup']:
            return False

        # If target is None, only King can be placed on an empty pile
        if target_card is None or not target_card['faceup']:
            return source_card['rank'] == '13'

        # Define rank sequence
        rank_sequence = {
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
            '6': 6, '7': 7, '8': 8, '9': 9, 
            '10': 10, '11': 11, '12': 12, '13': 13
        }

        # Check rank sequence
        rank_difference = (rank_sequence.get(target_card['rank'], 0) - 
                           rank_sequence.get(source_card['rank'], 0))
        
        # Check color alternation
        source_color = "red" if source_card['suit'] in ["heart", "diamond"] else "black"
        target_color = "red" if target_card['suit'] in ["heart", "diamond"] else "black"

        return (source_color != target_color and 
                rank_difference == 1)

    def _can_move_to_foundation(self, card: Dict[str, Any], foundation_pile: List[str]) -> bool:
        """
        Check if a card can be moved to a foundation pile
        """
        if not card['faceup']:
            return False

        # If foundation is empty, only Ace can be placed
        if not foundation_pile:
            return card['rank'] == '1'

        # Get top card of foundation pile
        top_card = self._parse_card(foundation_pile[-1])

        # Check same suit and sequential
        rank_sequence = {
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
            '6': 6, '7': 7, '8': 8, '9': 9, 
            '10': 10, '11': 11, '12': 12, '13': 13
        }

        return (card['suit'] == top_card['suit'] and 
                rank_sequence.get(card['rank'], 0) == rank_sequence.get(top_card['rank'], 0) + 1)
    
    def _get_move_impossibility_reason(self, source_card: Dict[str, Any], target_card: Dict[str, Any]) -> str:
        """
        Determine the specific reason why a move between two cards is not possible
        """
        if not source_card['faceup']:
            return "The move is invalid because the source card is face down"
            
        # Handle empty target pile case
        if target_card is None:
            if source_card['rank'] != '13':
                return "The move is invalid because only Kings can be placed on empty piles"
            return "The move is valid because king can be placed on empty pile"

        # Check color alternation
        source_color = "red" if source_card['suit'] in ["heart", "diamond"] else "black"
        target_color = "red" if target_card['suit'] in ["heart", "diamond"] else "black"

        # Define rank sequence
        rank_sequence = {
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
            '6': 6, '7': 7, '8': 8, '9': 9, 
            '10': 10, '11': 11, '12': 12, '13': 13
        }

        # Check rank sequence
        source_rank_val = rank_sequence.get(source_card['rank'], 0)
        target_rank_val = rank_sequence.get(target_card['rank'], 0)

        if source_color == target_color:
            return f"The move is invalid because both cards are {source_color} (cards must alternate colors)"

        if source_rank_val != target_rank_val - 1:
            return (f"The move is invalid because the source card's value ({source_card['rank']}) "
                    f"is not one less than the target card's value ({target_card['rank']})")

        return "The move is invalid for an unknown reason"

    def gen_board_state_qa(self) -> dict:
        question_id = uuid.uuid4().hex[:8]

        visible_cards_by_tableau = []

        analysis = "Current State Analysis:\n\n"
        plot_level_card_count = 0
        for i, pile in enumerate(self.tableau):
            if pile:
                top_card = self._parse_card(pile[-1])
                if top_card['faceup']:
                    card_str = f"{top_card['suit']} {top_card['rank']}"
                    visible_cards_by_tableau.append(f"Tab{i+1}: {card_str}")
                plot_level_card_count += sum([1 for card in pile if self._parse_card(card)['faceup']])
        analysis += "Top Cards in Tableau Piles:\n" + "\n".join(visible_cards_by_tableau) + "\n\n"

        # Foundation Piles
        foundation_analysis = "**Foundation Piles:**\n"
        for i, foundation_pile in enumerate(self.foundation):
            if foundation_pile:
                top_card = self._parse_card(foundation_pile[-1])
                foundation_analysis += f"- Foundation {i+1}: {top_card['suit']} {top_card['rank']}\n"
                plot_level_card_count += 1
            else:
                foundation_analysis += f"- Foundation {i+1}: Empty\n"
        analysis += foundation_analysis + "\n"

        # Waste Pile
        waste_analysis = "**Waste Pile:** "
        if self.waste_pile:
            top_waste_card = self._parse_card(self.waste_pile[-1])
            waste_analysis += f"{top_waste_card['suit']} {top_waste_card['rank']}\n"
            plot_level_card_count += 1
        else:
            waste_analysis += "Empty\n"
        analysis += waste_analysis + "\n"

        # 1. 先收集所有可能的正确选项
        valid_moves = []

        # 1.1 Tableau 到 Tableau
        for from_tab in range(1, 8):
            for to_tab in range(1, 8):
                if from_tab == to_tab:
                    continue
                source_pile = self.tableau[from_tab - 1]
                target_pile = self.tableau[to_tab - 1]

                if source_pile:
                    source_card = self._parse_card(source_pile[-1])
                    target_card = self._parse_card(target_pile[-1]) if target_pile else None
                    if self._can_move_to_tableau(source_card, target_card):
                        valid_moves.append(f"Move from Tab{from_tab} to Tab{to_tab}")

        # 1.2 Waste Pile 到 Tableau
        if self.waste_pile:
            waste_card = self._parse_card(self.waste_pile[-1])
            for tab in range(1, 8):
                target_pile = self.tableau[tab - 1]
                target_card = self._parse_card(target_pile[-1]) if target_pile else None
                if self._can_move_to_tableau(waste_card, target_card):
                    valid_moves.append(f"Move from Waste Pile to Tab{tab}")

        # 1.3 Waste Pile 到 Foundation
        if self.waste_pile:
            waste_card = self._parse_card(self.waste_pile[-1])
            for found in range(1, 5):
                if self._can_move_to_foundation(waste_card, self.foundation[found - 1]):
                    valid_moves.append(f"Move from Waste Pile to Foundation {found}")

        # 1.4 Tableau 到 Foundation
        for tab in range(1, 8):
            if self.tableau[tab - 1]:
                source_card = self._parse_card(self.tableau[tab - 1][-1])
                for found in range(1, 5):
                    if self._can_move_to_foundation(source_card, self.foundation[found - 1]):
                        valid_moves.append(f"Move from Tab{tab} to Foundation {found}")
        # 2. Generate options and ensure correct answer placement
        options = [None] * 8  # Initialize list with 8 None values

        if valid_moves:
            correct_move = random.choice(valid_moves)  # Select a correct answer
            # Place correct move in a random position between 1-7
            correct_answer = random.randint(1, 7)
            options[correct_answer - 1] = correct_move
        else:
            correct_move = "No possible moves from the options"
            correct_answer = 8
            options[7] = correct_move  # Place in 8th position

        # 3. Fill remaining positions with invalid moves
        available_positions = [i for i in range(8) if options[i] is None]
        while available_positions:
            fake_move = random.choice([
                f"Move from Tab{random.randint(1, 7)} to Tab{random.randint(1, 7)}",
                f"Move from Waste Pile to Tab{random.randint(1, 7)}",
                f"Move from Tab{random.randint(1, 7)} to Foundation {random.randint(1, 4)}",
                f"Move from Waste Pile to Foundation {random.randint(1, 4)}"
            ])
            
            # Ensure fake move is not valid and not already in options
            if fake_move not in valid_moves and fake_move not in options:
                pos = random.choice(available_positions)
                options[pos] = fake_move
                available_positions.remove(pos)

        # Ensure 8th option is "No possible moves" if it's not the correct answer
        if correct_answer != 8:
            options[7] = "No possible moves from the options"
        '''
        # 2. 确保只有一个正确答案
        if valid_moves:
            correct_move = random.choice(valid_moves)  # 选取一个正确答案
        else:
            correct_move = "No possible moves from the options"
        
        # 3. 生成选项，确保正确选项唯一
        options = [correct_move]

        while len(options) < 7:  # 生成 7 个选项
            fake_move = random.choice([
                f"Move from Tab{random.randint(1, 7)} to Tab{random.randint(1, 7)}",
                f"Move from Waste Pile to Tab{random.randint(1, 7)}",
                f"Move from Tab{random.randint(1, 7)} to Foundation {random.randint(1, 4)}",
                f"Move from Waste Pile to Foundation {random.randint(1, 4)}"
            ])
            if fake_move not in valid_moves and fake_move not in options:  # 确保干扰选项是错误的
                options.append(fake_move)

        # **确保第八个选项永远是 "No possible moves from the options"**
        options.append("No possible moves from the options")
        '''
        # **计算正确答案的索引**
        correct_answer = str(options.index(correct_move) + 1)
        def format_move_analysis(move_str, is_valid, reason):
            return f"{move_str}:\n{reason}\n\n"
        analysis += "Analyzing Each Move Option:\n\n"
        for move in options:
            if move == "No possible moves from the options":
                if not valid_moves:
                    analysis += format_move_analysis(move, True, "Correct, no possible moves from the options")
                else:
                    analysis += format_move_analysis(move, False, "Wrong, there are valid moves available")
                continue

            if move.startswith("Move from Tab"):
                parts = move.split()
                if "Foundation" in move:
                    # Tab to foundation move
                    from_tab = int(parts[2][3:])
                    foundation_num = int(parts[-1])
                    
                    if not self.tableau[from_tab - 1]:
                        analysis += format_move_analysis(move, False, "The move is invalid because the source tableau is empty")
                        continue
                    
                    source_card = self._parse_card(self.tableau[from_tab - 1][-1])
                    foundation_pile = self.foundation[foundation_num - 1]
                    
                    if self._can_move_to_foundation(source_card, foundation_pile):
                        analysis += format_move_analysis(
                            move, True,
                            f"The move is valid because you can move {source_card['suit']} {source_card['rank']} to foundation {foundation_num}"
                        )
                    else:
                        analysis += format_move_analysis(
                            move, False,
                            "The move is invalid because the card cannot be moved to foundation (must build up from Ace in same suit)"
                        )
                else:
                    # Tab to tab move
                    from_tab = int(parts[2][3:])
                    to_tab = int(parts[4][3:])
                    
                    source_pile = self.tableau[from_tab - 1]
                    target_pile = self.tableau[to_tab - 1]
                    
                    if not source_pile:
                        analysis += format_move_analysis(move, False, "The move is invalid because the source pile is empty")
                        continue
                    
                    source_card = self._parse_card(source_pile[-1])
                    target_card = self._parse_card(target_pile[-1]) if target_pile else None
                    
                    if self._can_move_to_tableau(source_card, target_card):
                        if target_card:
                            analysis += format_move_analysis(
                                move, True,
                                f"The move is valid because you can move {source_card['suit']} {source_card['rank']} onto {target_card['suit']} {target_card['rank']}"
                            )
                        else:
                            analysis += format_move_analysis(
                                move, True,
                                f"The move is valid because you can move {source_card['suit']} {source_card['rank']} to empty tableau (it's a King)"
                            )
                    else:
                        analysis += format_move_analysis(
                            move, False,
                            self._get_move_impossibility_reason(source_card, target_card)
                        )

            elif move.startswith("Move from Waste Pile"):
                if not self.waste_pile:
                    analysis += format_move_analysis(move, False, "The move is invalid because the waste pile is empty")
                    continue
                
                waste_card = self._parse_card(self.waste_pile[-1])
                
                if "Foundation" in move:
                    # Waste to foundation move
                    foundation_num = int(move.split()[-1])
                    foundation_pile = self.foundation[foundation_num - 1]
                    
                    if self._can_move_to_foundation(waste_card, foundation_pile):
                        analysis += format_move_analysis(
                            move, True,
                            f"The move is valid because you can move {waste_card['suit']} {waste_card['rank']} to foundation {foundation_num}"
                        )
                    else:
                        analysis += format_move_analysis(
                            move, False,
                            "The move is invalid because the card cannot be moved to foundation (must build up from Ace in same suit)"
                        )
                else:
                    # Waste to tableau move
                    tab_num = int(move.split("Tab")[-1])
                    target_pile = self.tableau[tab_num - 1]
                    target_card = self._parse_card(target_pile[-1]) if target_pile else None
                    
                    if self._can_move_to_tableau(waste_card, target_card):
                        analysis += format_move_analysis(
                            move, True,
                            f"The move is valid because you can move {waste_card['suit']} {waste_card['rank']} from waste pile"
                        )
                    else:
                        analysis += format_move_analysis(
                            move, False,
                            self._get_move_impossibility_reason(waste_card, target_card)
                        )
        analysis += f"So the correct option number is {correct_answer}."
        return {
            "data_id": f"klondike-mcq-{question_id}",
            "qa_type": "StateInfo",
            "question_description": "Analyze the current state of the board and possible moves.",
            "plot_level": "Easy" if plot_level_card_count <= 19 else "Medium" if plot_level_card_count <= 23 else "Hard",
            "qa_level": "Medium",
            "question": KLONDIKE_GAME_DESCR_GENERAL + "Analyze the current state of the board and possible moves.\nChoose the correct move or choose option 8 if there are no possible moves from the options\nOptions:\n" + "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]),
            "answer": correct_answer,
            "analysis": analysis,  # **保持原本的分析**
            "options": options
        }

    def gen_deadlock_qa(self) -> dict:
        question_id = uuid.uuid4().hex[:8]
        visible_cards_by_tableau = []
        plot_level_card_count = 0
        
        analysis = "Current State Analysis:\n\n"
        for i, pile in enumerate(self.tableau):
            if pile:
                top_card = self._parse_card(pile[-1])
                under_status = "which is the only card in this pile" if len(pile) == 1 else "with a hidden card underneath" if self._parse_card(pile[-2])['faceup'] is False else "with a visible card underneath"
                if top_card['faceup']:
                    card_str = f"{top_card['suit']} {top_card['rank']}"
                    # visible_cards_by_tableau.append(f"Tab{i+1}: {card_str}")
                    visible_cards_by_tableau.append(f"Tab{i+1}: {card_str}, {under_status}")
                plot_level_card_count += sum([1 for card in pile if self._parse_card(card)['faceup']])
        analysis += "Top Cards in Tableau Piles:\n" + "\n".join(visible_cards_by_tableau) + "\n\n"
        # Foundation Piles
        foundation_analysis = "**Foundation Piles:**\n"
        for i, foundation_pile in enumerate(self.foundation):
            if foundation_pile:
                top_card = self._parse_card(foundation_pile[-1])
                foundation_analysis += f"- Foundation {i+1}: {top_card['suit']} {top_card['rank']}\n"
                plot_level_card_count += 1
            else:
                foundation_analysis += f"- Foundation {i+1}: Empty\n"
        analysis += foundation_analysis + "\n"
        # Waste Pile
        waste_analysis = "**Waste Pile:** "
        if self.waste_pile:
            top_waste_card = self._parse_card(self.waste_pile[-1])
            waste_analysis += f"{top_waste_card['suit']} {top_waste_card['rank']}\n"
            plot_level_card_count += 1
        else:
            waste_analysis += "Empty\n"
        analysis += waste_analysis + "\n"
        analysis += "**Draw Pile:** "
        analysis += ("Not empty" if self.draw_pile else "Empty") + "\n\n"

        analysis += "Analyzing possible moves in priority order:\n\n"
        # 1. Check if draw pile and waste pile are empty
        def reason1() -> bool:
            return len(self.draw_pile) == 0 and len(self.waste_pile) == 0

        # 2. Check if any cards can be moved to foundation piles
        def reason2() -> tuple[bool, list]:
            can_move_to_foundation = False
            foundation_moves_dict = {}

            for found_idx, foundation_pile in enumerate(self.foundation):
                if self.waste_pile:
                    waste_card = self._parse_card(self.waste_pile[-1])
                    if self._can_move_to_foundation(waste_card, foundation_pile):
                        can_move_to_foundation = True
                        foundation_moves_dict[waste_card['suit'] + waste_card['rank']] = f"- Waste: {waste_card['suit']} {waste_card['rank']} → Foundation {found_idx + 1}"

                for tab_idx, tableau_pile in enumerate(self.tableau):
                    if tableau_pile:
                        source_card = self._parse_card(tableau_pile[-1])
                        if self._can_move_to_foundation(source_card, foundation_pile):
                            can_move_to_foundation = True
                            foundation_moves_dict[source_card['suit'] + source_card['rank']] = f"- Tab{tab_idx + 1}: {source_card['suit']} {source_card['rank']} → Foundation {found_idx + 1}"

            return can_move_to_foundation, list(foundation_moves_dict.values())

        def reason3() -> tuple[bool, list]:
            can_move_to_tableau = False
            tableau_moves = []

            for tab_idx, source_pile in enumerate(self.tableau):
                if not source_pile:
                    continue
                source_card = self._parse_card(source_pile[-1])
                hidden_card = self._parse_card(source_pile[-2]) if len(source_pile) > 1 else None

                # 当移动后能清空某个 Tableau Pile 时，有效移动
                if hidden_card is None:
                    for target_idx, target_pile in enumerate(self.tableau):
                        if tab_idx != target_idx:
                            if target_pile:
                                target_card = self._parse_card(target_pile[-1])
                                if self._can_move_to_tableau(source_card, target_card):
                                    can_move_to_tableau = True
                                    tableau_moves.append(f"- Tab{tab_idx + 1}: {source_card['suit']} {source_card['rank']} → Tab{target_idx + 1} (Top: {target_card['suit']} {target_card['rank']}), emptying Tab{tab_idx + 1}")
                            else:
                                if self._can_move_to_tableau(source_card, None):
                                    can_move_to_tableau = True
                                    tableau_moves.append(f"- Tab{tab_idx + 1}: {source_card['suit']} {source_card['rank']} → Tab{target_idx + 1} (Empty), emptying Tab{tab_idx + 1}")
                # 当移动后能翻出隐藏牌时，有效移动
                elif not hidden_card['faceup']:
                    for target_idx, target_pile in enumerate(self.tableau):
                        if tab_idx != target_idx:
                            if target_pile:
                                target_card = self._parse_card(target_pile[-1])
                                if self._can_move_to_tableau(source_card, target_card):
                                    can_move_to_tableau = True
                                    tableau_moves.append(f"- Tab{tab_idx + 1}: {source_card['suit']} {source_card['rank']} → Tab{target_idx + 1} (Top: {target_card['suit']} {target_card['rank']}), revealing a hidden card in Tab{tab_idx + 1}")
                            else:
                                if self._can_move_to_tableau(source_card, None):
                                    can_move_to_tableau = True
                                    tableau_moves.append(f"- Tab{tab_idx + 1}: {source_card['suit']} {source_card['rank']} → Tab{target_idx + 1} (Empty), revealing a hidden card in Tab{tab_idx + 1}")
                
            return can_move_to_tableau, tableau_moves

        # Analyze game state
        analysis += f"1. Draw Pile and Waste Pile Check: {'Both are empty' if reason1() else 'Not both empty'}\n\n"

        # Foundation moves analysis
        can_move_to_foundation, foundation_moves = reason2()
        if can_move_to_foundation:
            analysis += "2. Cards to Foundation Check:\n" + "\n".join(foundation_moves) + "\n\n"
        else:
            analysis += "2. Cards to Foundation Check: No cards can be moved to foundation piles.\n\n"

        # Tableau moves analysis
        can_move_to_tableau, tableau_moves = reason3()
        if can_move_to_tableau:
            analysis += "3. Effective Tableau Pile Move Check:\n" + "\n".join(tableau_moves) + "\n\n"
        else:
            # analysis += "3. Effective Moves Check: No hidden cards in the tableau pile can be revealed through a move in current state.\n\n"
            analysis += "3. Effective Tableau Pile Move Check: No tableau pile move can reveal a hidden card or empty a tableau pile.\n\n"

        # Determine deadlock
        is_deadlock = reason1() and not can_move_to_foundation and not can_move_to_tableau

        # Generate the correct option
        if is_deadlock:
            correct_option = "Draw pile and waste pile are both empty AND No cards can be moved to foundation piles AND No hidden cards in the tableau pile can be revealed through a move in current state, so the game is in a deadlock."
        else:
            correct_option = (
                ("Draw pile and waste pile are NOT both empty" if not reason1() else "Draw pile and waste pile are both empty")
                + " AND "
                + ("Existing cards can be moved to foundation piles" if can_move_to_foundation else "No cards can be moved to foundation piles")
                + " AND "
                # + ("No hidden cards in the tableau pile can be revealed through a move in current state" if not can_move_to_tableau else "Existing hidden cards in the tableau pile can be revealed through a move in current state")
                + ("No tableau pile move can reveal a hidden card or empty a tableau pile" if not can_move_to_tableau else "Some tableau pile move can reveal a hidden card or empty a tableau pile")
                + ", so the game is NOT in a deadlock."
            )

        # Generate options with the correct one randomly placed
        # options = [
        #     "Draw pile and waste pile are both empty AND No cards can be moved to foundation piles AND No hidden cards in the tableau pile can be revealed through a move in current state, so the game is in a deadlock.",
        #     "Draw pile and waste pile are both empty AND No cards can be moved to foundation piles AND Existing hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are both empty AND Existing cards can be moved to foundation piles AND No hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are both empty AND Existing cards can be moved to foundation piles AND Existing hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are NOT both empty AND No cards can be moved to foundation piles AND No hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are NOT both empty AND No cards can be moved to foundation piles AND Existing hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are NOT both empty AND Existing cards can be moved to foundation piles AND No hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock.",
        #     "Draw pile and waste pile are NOT both empty AND Existing cards can be moved to foundation piles AND Existing hidden cards in the tableau pile can be revealed through a move in current state, so the game is NOT in a deadlock."
        # ]

        options = [
            "Draw pile and waste pile are both empty AND No cards can be moved to foundation piles AND No tableau pile move can reveal a hidden card or empty a tableau pile, so the game is in a deadlock.",
            "Draw pile and waste pile are both empty AND No cards can be moved to foundation piles AND Some tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are both empty AND Existing cards can be moved to foundation piles AND No tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are both empty AND Existing cards can be moved to foundation piles AND Some tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are NOT both empty AND No cards can be moved to foundation piles AND No tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are NOT both empty AND No cards can be moved to foundation piles AND Some tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are NOT both empty AND Existing cards can be moved to foundation piles AND No tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock.",
            "Draw pile and waste pile are NOT both empty AND Existing cards can be moved to foundation piles AND Some tableau pile move can reveal a hidden card or empty a tableau pile, so the game is NOT in a deadlock."
        ]
        random.shuffle(options)
        
        # Find the index of the correct option and add 1 to make it 1-based
        correct_answer = str(options.index(correct_option) + 1)
        
        # Update analysis with the correct answer
        analysis += f"So the answer is option {correct_answer}: {correct_option}"

        return {
            "data_id": f"klondike-mcq-{question_id}",
            "qa_type": "StrategyOptimization",
            "question_description": "Determine if the game has reached a state where no further moves are possible",
            "plot_level": "Easy" if plot_level_card_count <= 19 else "Medium" if plot_level_card_count <= 23 else "Hard",
            "qa_level": "Medium",
            "question": KLONDIKE_GAME_DESCR_GENERAL + DEADLOCK_DESCR + "Analyze the current game state and select the most appropriate reason for why the game is or is not in a deadlock.\n"
                        "Choose the correct option and give the analysis.\nOptions:\n" +
                        "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]),
            "answer": correct_answer,
            "analysis": analysis,
            "options": options
        }
    def gen_move_effectiveness_qa(self) -> dict:
        """
        Generate question and answer about move effectiveness.
        A move is considered effective if it:
        1. Reveals a hidden card (for tableau to tableau moves)
        2. Creates an empty tableau spot (for tableau to tableau moves)
        3. Is a move to foundation (all foundation moves are effective)
        """
        visible_cards_by_tableau = []
        plot_level_card_count = 0
        
        question_id = uuid.uuid4().hex[:8]
        analysis = "Current State Analysis:\n\n"
        for i, pile in enumerate(self.tableau):
            if pile:
                top_card = self._parse_card(pile[-1])
                under_status = "which is the only card in this pile" if len(pile) == 1 else "with a hidden card underneath" if self._parse_card(pile[-2])['faceup'] is False else "with a visible card underneath"
                if top_card['faceup']:
                    card_str = f"{top_card['suit']} {top_card['rank']}"
                    # visible_cards_by_tableau.append(f"Tab{i+1}: {card_str}")
                    visible_cards_by_tableau.append(f"Tab{i+1}: {card_str}, {under_status}")
                plot_level_card_count += sum([1 for card in pile if self._parse_card(card)['faceup']])
        analysis += "Top Cards in Tableau Piles:\n" + "\n".join(visible_cards_by_tableau) + "\n\n"
        # Foundation Piles
        foundation_analysis = "**Foundation Piles:**\n"
        for i, foundation_pile in enumerate(self.foundation):
            if foundation_pile:
                top_card = self._parse_card(foundation_pile[-1])
                foundation_analysis += f"- Foundation {i+1}: {top_card['suit']} {top_card['rank']}\n"
                plot_level_card_count += 1
            else:
                foundation_analysis += f"- Foundation {i+1}: Empty\n"
        analysis += foundation_analysis + "\n"
        # Waste Pile
        waste_analysis = "**Waste Pile:** "
        if self.waste_pile:
            top_waste_card = self._parse_card(self.waste_pile[-1])
            waste_analysis += f"{top_waste_card['suit']} {top_waste_card['rank']}\n"
            plot_level_card_count += 1
        else:
            waste_analysis += "Empty\n"
        analysis += waste_analysis + "\n"
        analysis += "**Draw Pile:** "
        analysis += ("Not empty" if self.draw_pile else "Empty") + "\n\n"


        # Step 0: Initialize collections for all possible moves and their analyses
        all_valid_moves = []  # List of tuples (move_str, source_type, is_effective, reason)
        foundation_moves = []  # Valid foundation moves
        tableau_moves = []    # Valid tableau to tableau moves
        
        # Step 1: Find all valid moves and categorize them
        # Check all possible tableau to tableau moves
        for from_tab in range(1, 8):
            source_pile = self.tableau[from_tab - 1]
            if not source_pile:
                continue
                
            source_card = self._parse_card(source_pile[-1])
            
            # Check tableau to foundation moves
            for found in range(1, 5):
                if self._can_move_to_foundation(source_card, self.foundation[found - 1]):
                    move_str = f"Move from Tab{from_tab} to Foundation {found}"
                    reason = f"moves {source_card['suit']} {source_card['rank']} to foundation"
                    foundation_moves.append((move_str, "foundation", True, reason))

            # Check tableau to tableau moves
            for to_tab in range(from_tab+1, 8):
                target_pile = self.tableau[to_tab - 1]
                target_card = self._parse_card(target_pile[-1]) if target_pile else None
                
                if self._can_move_to_tableau(source_card, target_card):
                    move_str = f"Move from Tab{from_tab} to Tab{to_tab}"
                    is_effective = False
                    reasons = []
                    
                    # Check if move reveals hidden card
                    if len(source_pile) > 1 and str(source_pile[-2]).startswith('<Card'):
                        is_effective = True
                        reasons.append("reveals a hidden card")
                    
                    # Check if move creates empty tableau spot
                    if len(source_pile) == 1:
                        is_effective = True
                        reasons.append("creates an empty tableau spot")
                    
                    reason = " and ".join(reasons) if reasons else "valid but not effective"
                    tableau_moves.append((move_str, "tableau", is_effective, reason))

        # Combine all valid moves
        all_valid_moves = foundation_moves + tableau_moves

        # Step 2: Select correct answer based on probabilities
        if not all_valid_moves:
            # No valid moves - Option 8 is correct
            correct_answer = 8
            options = []
            
            # Generate invalid moves for other options
            while len(options) < 7:
                move = f"Move from Tab{random.randint(1, 7)} to Tab{random.randint(1, 7)}"
                if move not in options:
                    options.append(move)
            
            options.append("None of these moves are both valid and effective")
            
        else:
            # Choose between foundation (25%) and tableau (75%) if both exist
            valid_effective_moves = []
            if foundation_moves:
                valid_effective_moves.extend(foundation_moves)
            if tableau_moves:
                valid_effective_moves.extend([move for move in tableau_moves if move[2]])  # Only effective tableau moves
                
            if not valid_effective_moves:
                # No effective moves - Option 8 is correct
                correct_answer = 8
                options = []
                
                # Fill with valid but ineffective moves and invalid moves
                valid_ineffective = [move[0] for move in all_valid_moves if not move[2]]
                while len(options) < 7:
                    if valid_ineffective and random.random() < 0.5:
                        move = valid_ineffective.pop(0) if valid_ineffective else f"Move from Tab{random.randint(1, 7)} to Tab{random.randint(1, 7)}"
                    else:
                        move = f"Move from Tab{random.randint(1, 7)} to Tab{random.randint(1, 7)}"
                    if move not in options:
                        options.append(move)
                
                options.append("None of these moves are both valid and effective")
                
            else:
                # Choose correct move based on probabilities
                if random.random() < 0.25 and foundation_moves:
                    chosen_move = random.choice(foundation_moves)
                else:
                    effective_tableau_moves = [move for move in tableau_moves if move[2]]
                    if effective_tableau_moves:
                        chosen_move = random.choice(effective_tableau_moves)
                    else:
                        chosen_move = random.choice(valid_effective_moves)
                
                # Place correct move in random position 1-7
                correct_answer = random.randint(1, 7)
                options = [None] * 8
                options[correct_answer - 1] = chosen_move[0]
                options[7] = "None of these moves are both valid and effective"
                
                # Fill remaining positions
                remaining_positions = [i for i in range(7) if options[i] is None]
                
                # Get pool of valid but ineffective moves
                valid_ineffective = [move[0] for move in all_valid_moves if not move[2]]
                
                # Fill remaining positions with mix of valid ineffective and invalid moves
                for pos in remaining_positions:
                    if valid_ineffective and random.random() < 0.5:
                        move = valid_ineffective.pop(0)
                    else:
                        while True:
                            mis_from_pile = random.randint(1, 6)
                            move = f"Move from Tab{mis_from_pile} to Tab{random.randint(mis_from_pile+1, 7)}"
                            if move not in options:
                                break
                    options[pos] = move

        # Step 4: Generate analysis using stored reasons
        analysis += "Analysis of move options:\n\n"
        
        # Create lookup dictionary for move analyses
        move_analysis = {move[0]: (move[2], move[3]) for move in all_valid_moves}
        
        for i, move in enumerate(options, 1):
            if move == "None of these moves are both valid and effective":
                if correct_answer == 8:
                    analysis += f"Option {i}: Correct - no moves listed are both valid and effective\n\n"
                else:
                    analysis += f"Option {i}: Incorrect - there is at least one valid and effective move\n\n"
                continue
                
            if move in move_analysis:
                is_effective, reason = move_analysis[move]
                if is_effective:
                    analysis += f"Option {i}: {move} - Valid and effective because it {reason}\n\n"
                else:
                    analysis += f"Option {i}: {move} - {reason}\n\n"
            else:
                # This is an invalid move
                parts = move.split()
                from_tab = int(parts[2][3:])
                if "Foundation" in move:
                    to_foundation = int(parts[-1])
                    analysis += f"Option {i}: {move} - Invalid move to foundation\n\n"
                else:
                    to_tab = int(parts[4][3:])
                    source_pile = self.tableau[from_tab - 1]
                    target_pile = self.tableau[to_tab - 1]
                    
                    if not source_pile:
                        analysis += f"Option {i}: {move} - Invalid because source pile is empty\n\n"
                        continue
                        
                    source_card = self._parse_card(source_pile[-1])
                    target_card = self._parse_card(target_pile[-1]) if target_pile else None
                    
                    analysis += f"Option {i}: {move} - {self._get_move_impossibility_reason(source_card, target_card)}\n\n"

        analysis += f"\nCorrect answer is option {correct_answer}"
        if correct_answer != 8:
            analysis += f" because {options[correct_answer-1]} is both valid and effective"
        else:
            analysis += " because none of the moves are both valid and effective"

        return {
            "data_id": f"klondike-mcq-{question_id}",
            "qa_type": "StrategyOptimization",
            "question_description": "Evaluate the strategic effectiveness of possible moves",
            "plot_level": "Easy" if plot_level_card_count <= 19 else "Medium" if plot_level_card_count <= 23 else "Hard",
            "qa_level": "Hard",
            "question": KLONDIKE_GAME_DESCR_GENERAL + EFFECTIVE_MOVE_DESCR + 
                    "Which of the following moves is both valid and effective? " +
                    "A move is effective if it either reveals a hidden card, enables a foundation move, or creates an empty tableau spot.\n" +
                    "Choose the correct option and give the analysis.\nOptions:\n" + 
                    "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]),
            "answer": str(correct_answer),
            "analysis": analysis,
            "options": options
        }
        
def save_qa_to_json(qa_data: Dict, dataset_folder: str):
    """Save the generated QA data to a JSON file."""
    os.makedirs(dataset_folder, exist_ok=True)
    qa_filename = os.path.join(dataset_folder, "qa.json")
    
    with open(qa_filename, 'w', encoding='utf-8') as f:
        json.dump(qa_data, f, indent=4, ensure_ascii=False)
    print(f"QA data saved to {qa_filename}")

    '''
    def gen_move_validity_qa(self, from_pile: int, to_pile: int) -> dict:
        """Generate question and answer about the validity of a specific move."""
        question_id = uuid.uuid4().hex[:8]
        
        # Get the cards involved
        from_cards = self.tableau[from_pile - 1]
        to_cards = self.tableau[to_pile - 1]
        
        # Check move validity
        source_card = (self._parse_card(from_cards[-1]) 
                       if from_cards else None)
        target_card = (self._parse_card(to_cards[-1]) 
                       if to_cards else None)
        
        # Determine move validity and get detailed reasoning
        move_valid = (source_card and 
                      self._can_move_to_tableau(source_card, target_card))
        
        # Construct detailed analysis
        analysis = f"Move Analysis:\n"
        analysis += f"Source Pile (Tab{from_pile}): {from_cards}\n"
        analysis += f"Target Pile (Tab{to_pile}): {to_cards}\n\n"
        
        if not source_card:
            analysis += "Move is INVALID Because there are no cards in the source pile."
        elif not source_card['faceup']:
            analysis += "Move is INVALID Because the source card is face down."
        elif not target_card:
            # Special case for empty pile
            if source_card['rank'] == '13':  # King
                analysis += "Move is VALID Because a King can be placed on an empty tableau pile."
                move_valid = True
            else:
                analysis += "Move is INVALID Because only a King can be placed on an empty tableau pile."
                move_valid = False
        else:
            # Detailed reasoning for why the move might be invalid
            # Check color alternation
            source_color = "red" if source_card['suit'] in ["heart", "diamond"] else "black"
            target_color = "red" if target_card['suit'] in ["heart", "diamond"] else "black"

            # Define rank sequence
            rank_sequence = {
                '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
                '6': 6, '7': 7, '8': 8, '9': 9, 
                '10': 10, '11': 11, '12': 12, '13': 13
            }

            # Check rank sequence
            source_rank_val = rank_sequence.get(source_card['rank'], 0)
            target_rank_val = rank_sequence.get(target_card['rank'], 0)

            if source_color == target_color:
                analysis += (f"Move is INVALID Because both cards are {source_color}. "
                             "Cards must alternate colors (red and black).")
                move_valid = False
            elif source_rank_val != target_rank_val - 1:
                analysis += (f"Move is INVALID Because the source card's value ({source_card['rank']}) "
                             f"is not one less than the target card's value ({target_card['rank']}).")
                move_valid = False
            else:
                analysis += "Move is VALID Because the cards meet all movement criteria."
        
        return {
            "data_id": f"klondike-fill-{question_id}",
            "qa_type": "ActionOutcome",
            "question_id": 2,
            "question_description": "Evaluate the validity of a specific card move between tableau piles",
            "plot_level": "Easy" if from_pile <= 4 and to_pile <= 4 else "Medium",
            "qa_level": "Medium",
            "question": KLONDIKE_GAME_DESCR_GENERAL + f"Is moving the card {source_card} from pile {from_pile} to pile {to_pile} valid?  \nAnswer true or false of the question that whether the move is valid and give the analysis.",
            "answer": move_valid,
            "analysis": analysis+"\nSo the answer is "+str(move_valid)+"."
        }


    def gen_foundation_move_qa(self) -> dict:
        """Generate question and answer about possible foundation moves with detailed reasoning."""
        question_id = uuid.uuid4().hex[:8]
        
        # Check for possible foundation moves
        possible_foundation_moves = []
        detailed_move_analysis = []

        # Check tableau piles and waste pile
        for pile_index, pile in enumerate(self.tableau + [self.waste_pile]):
            if pile:
                top_card = self._parse_card(pile[-1])
                
                # Check against each foundation pile
                for foundation_index, foundation_pile in enumerate(self.foundation):
                    if self._can_move_to_foundation(top_card, foundation_pile):
                        move_details = {
                            'card': top_card,
                            'source_pile': 'Tableau ' + str(pile_index + 1) if pile_index < len(self.tableau) else 'Waste Pile',
                            'target_foundation': f'Foundation {foundation_index + 1}',
                            'reason': ''
                        }

                        # Provide specific reasoning
                        if not foundation_pile:
                            # First card in foundation must be an Ace
                            move_details['reason'] = f"Can start a new foundation pile with an Ace ({top_card['rank']})"
                        else:
                            top_foundation_card = self._parse_card(foundation_pile[-1])
                            move_details['reason'] = (
                                f"Follows sequential order: {top_foundation_card['rank']} -> {top_card['rank']} "
                                f"in the {top_card['suit']} suit"
                            )
                        
                        possible_foundation_moves.append(top_card)
                        detailed_move_analysis.append(move_details)

        # Construct comprehensive analysis
        analysis = "Foundation Move Analysis:\n"
        if detailed_move_analysis:
            analysis += "Possible Foundation Moves:\n"
            for move in detailed_move_analysis:
                analysis += (f"- Move {move['card']} from {move['source_pile']} "
                            f"to {move['target_foundation']}: {move['reason']}\n")
        else:
            analysis += "No possible foundation moves found.\n"

        # Provide strategic insights
        strategic_insights = ""
        if possible_foundation_moves:
            strategic_insights += (
                "\nStrategic Considerations:\n"
                "- Moving cards to foundation piles is a key strategy in Klondike Solitaire.\n"
                "- Prioritize moves that:\n"
                "  1. Clear tableau spaces\n"
                "  2. Reveal face-down cards\n"
                "  3. Create more strategic moves"
            )

        full_analysis = analysis + strategic_insights

        return {
            "data_id": f"klondike-fill-{question_id}",
            "qa_type": "TransitionPath",
            "question_id": 3,
            "question_description": "Identify possible moves to foundation piles and their strategic implications",
            "plot_level": "Medium",
            "qa_level": "Medium",
            "question": KLONDIKE_GAME_DESCR_GENERAL + "Are there any cards that can be moved to the foundation piles, and why? \nAnswer true or false of the question and give the analysis.",
            "answer": len(possible_foundation_moves) > 0,
            "analysis": full_analysis +"\nSo the answer is "+str(len(possible_foundation_moves) > 0)+"."
        }
    '''