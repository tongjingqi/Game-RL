# QA_generator.py
import random
from typing import Tuple, List, Optional
import model
from model import Stack, SelectableStack, OneWayStack, Card, Model

VALID_QA_TYPES = {"Target Perception", "State Prediction", "Strategy Optimization"}

question_prompt = """
Spider Solitaire

# OBJECTIVE
Spider is played with eight decks of 13 spade cards each, totaling 104 cards. Every card is a spade, so suits never differ. The goal is to arrange cards into King-to-Ace sequences and move them to the foundation piles. Once all sequences are moved to the foundations, the game is won.

# SETUP
The game features waste piles, a stock pile, and foundation piles. Waste piles are where the action happens, and the stock pile provides new cards when necessary.

**Waste Pile Numbering**: Waste piles are numbered from left to right starting with `0`. The cards within each waste pile are also numbered starting from the bottom card.

# GAME BOARD COMPONENTS

## **Stock Pile**
The **Stock Pile** holds all remaining cards and is used to deal new cards into the waste piles. 
Stock Pile is in the top left corner of the board.

- **Staggered Card Stacking**: Cards are stacked in layers, and the number of layers indicates how many more times you can deal cards to the waste piles. Each deal moves one card face-up to each waste pile.

## **Waste Piles**
The **Waste Piles** are where cards are played and organized.
Waste Piles are on the bottom of the chessboard

- **Face-Up vs. Face-Down Cards**: Cards are stacked with face-up cards visible and face-down cards hidden. Only face-up cards can be played. When a face-down card becomes the top card of a pile, it is turned face-up and can be played.

- **Staggered Cards**: Cards in each waste pile are arranged so that face-up cards are on top, and face-down cards are beneath. As you move cards, new face-down cards are revealed.

- **Card Numbering and Screen Position**: 
  - **Waste Pile Numbering**: Piles are numbered from left to right starting with `0` for the leftmost pile. 
  - The card at the bottom of each waste pile (usually face-down) is numbered **0**.
  - As you move upward in the pile, the next cards are numbered **1**, **2**, **3**, and so on.
  - Visually, the bottom card (number **0**) is the one closest to the top of the screen, and the cards above it are stacked above in the pile, going downwards.

## **Foundation Pile**
Foundation piles store the completed sequences. When 13 cards are arranged in a King-to-Ace sequence, they may be removed to a foundation pile. If all eight sequences are moved to the foundations, the game is won.
Foundation Pile is in the top right corner of the board.

# MOVING CARDS
- **Movement Conditions**: 
  - **Move a single card**: The single card being moved must be placed on a top card that has the **next higher rank** (e.g., a Q can be placed on a K).
  - **Move multiple cards**: A complete **descending sequence** of cards (such as K, Q, J, 10, etc.) can be moved from one pile to another. The cards being moved must already form a descending sequence, and the pile they are placed on must continue it in **descending order** from K, Q, J, 10, 9, ..., 2, A.
- **Face-Down Cards**: If the sequence you are moving includes face-down cards, they will be flipped face-up once they are moved. After flipping, the newly face-up cards can continue to be moved or interacted with.
- **Example**: If you have a sequence of K-Q-J-10-9-8-7, you can move a 6 to the top of this pile, resulting in a new sequence K-Q-J-10-9-8-7-6.
- **Empty Pile Rule**: An empty waste pile can accept any card. After placing the card, you can continue adding a descending sequence to that pile.
- **Reveal Cards**: If a move leaves a face-down card on top, it will be turned face-up.

# DEALING
Click the stock to deal a new row of face-up cards to the waste piles. You may not deal if there is an empty waste pile.

# STRATEGY
- Turn face-down cards face-up.
- Form runs in descending order.
- Use empty waste piles strategically.

# VARIANTS
In **circular spider solitaire**, a King can be placed on an Ace, allowing for extended sequences.

# **NOTE: Important Numbering Reminder**
- **Waste Pile Numbering**: Waste piles are numbered from **left to right** starting with `0` for the leftmost pile.
- **Card Numbering within Waste Piles**: The **bottom-most card** of each pile (usually face-down) is numbered **0**, and the cards above it are numbered **1**, **2**, **3**, etc., moving upwards in the pile.
- **Please Pay Attention** to both the waste pile and card numbering methods, as they will help you navigate and make strategic decisions effectively.
"""

def find_longest_same_suit_sequence(model_instance: model.Model) -> Optional[Tuple[int, int, int]]:
    """
    Finds the move that forms the longest descending sequence of the same suit.
    
    Returns:
        A tuple containing (source_pile_index, destination_pile_index, number_of_cards_to_move).
        Returns None if no such move exists.
    """
    longest_sequence_length = 0
    best_move = None
    
    num_waste = model_instance.num_waste
    
    for src_index, src_pile in enumerate(model_instance.waste):
        for card_idx in range(len(src_pile)):
            if src_pile[card_idx].faceDown():
                continue  # Face-down cards cannot be moved
            sequence = src_pile[card_idx:]
            if not model.Card.isDescending(sequence):
                continue
            # Check if all cards in the sequence are of the same suit
            suit = sequence[0].suit
            if any(card.suit != suit for card in sequence):
                continue
            # Calculate the length of the sequence
            seq_length = len(sequence)
            # Update if this sequence is longer than previously found
            if seq_length > longest_sequence_length:
                # Now, find a destination pile where the top card is one higher in rank
                for dest_index, dest_pile in enumerate(model_instance.waste):
                    if dest_index == src_index:
                        continue
                    if dest_pile.isEmpty() or (dest_pile[-1].rank - sequence[0].rank == 1):
                        # Valid move found
                        if seq_length > longest_sequence_length:
                            longest_sequence_length = seq_length
                            best_move = (src_index, dest_index, card_idx)
                        break  # No need to check other destination piles for this sequence
    return best_move

def legal_sequence_moves(model_instance: model.Model) -> List[Tuple[int, int, int, int]]:
    """
    All legal moves of a face-up descending same-suit sequence onto another waste pile.
    Returns tuples (source_pile_index, card_index, destination_pile_index, number_of_cards_moved).
    """
    moves = []
    for src_index, src_pile in enumerate(model_instance.waste):
        for card_idx in range(len(src_pile)):
            sequence = src_pile[card_idx:]
            if src_pile[card_idx].faceDown() or not model.Card.isDescending(sequence):
                continue
            for dest_index, dest_pile in enumerate(model_instance.waste):
                if dest_index != src_index and (dest_pile.isEmpty() or dest_pile[-1].rank - sequence[0].rank == 1):
                    moves.append((src_index, card_idx, dest_index, len(sequence)))
    return moves

def reveal_targets(model_instance: model.Model, pile_index: int) -> List[int]:
    """
    Waste piles that can take, in one move, every face-up card lying above the first face-down card of the given pile.
    Those cards move together only as a descending sequence, onto an empty pile or a card one rank higher.
    Empty if the pile has no face-down card or no such move exists.
    """
    pile = model_instance.waste[pile_index]
    num_face_down = model_instance.downUp(pile_index)[0]
    moving_cards = pile[num_face_down:]
    if not num_face_down or not moving_cards or not model.Card.isDescending(moving_cards):
        return []
    return [
        idx for idx, other in enumerate(model_instance.waste)
        if idx != pile_index and (other.isEmpty() or other[-1].rank - moving_cards[0].rank == 1)
    ]

def random_move_options(labels: List[str], num_waste: int, card_range: Tuple[int, int], exclude: List[str] = ()) -> List[str]:
    """
    Distractor options "We should move the k-th card of pile i to pile j." for the given labels.
    No two of them are alike, none moves a card onto its own pile, and none equals a move in exclude
    (the correct move of the question).
    """
    moves = []
    while len(moves) < len(labels):
        card_index = random.randint(*card_range)
        source = random.randint(0, num_waste - 1)
        destination = random.randint(0, num_waste - 1)
        move = f"We should move the {card_index}-th card of pile {source} to pile {destination}."
        if source != destination and move not in moves and move not in exclude:
            moves.append(move)
    return [f"{label}. {move}" for label, move in zip(labels, moves)]

def generate_spider_QA(model_instance: model.Model, num: int, num_waste: int) -> Tuple[str, str, str, int, str, str, Optional[List[str]]]:
    """
    Generates a question and answer pair for Spider Solitaire.

    Parameters:
    - model_instance: model object representing the current game state.
    - num: Integer used to select the question type.
    - num_waste: The number of waste piles.

    Returns:
    - qa_type: Type of the question.
    - qa_level: Difficulty level of the question.
    - question: The question text (including question_prompt).
    - answer: The correct answer.
    - analysis: Detailed explanation of the answer.
    - options: List of options if it's a multiple-choice question, else None.
    """
    
    # Define question types with VALID_QA_TYPES
    question_types = [
        # 0: StateInfo
        {"qa_type": "Target Perception", "template": "How many times can the stockpile still deal cards?", "difficulty": "Easy", "is_mcq": False, "description": "Remaining deals in the stockpile"},
        
        # 1: StateInfo
        {"qa_type": "Target Perception", "template": "Which card is on the top of waste pile {num}?", "difficulty": "Easy", "is_mcq": False, "description": "Identify a card of a waste pile"},
        
        # 2: StateInfo
        {"qa_type": "Target Perception", "template": "How many face-down cards are currently in all waste piles?", "difficulty": "Easy", "is_mcq": False, "description": "Count face-down cards in all waste piles"},
        
        # 3: StateInfo
        {"qa_type": "Target Perception", "template": "If I click the stockpile for {num1} times, how many face-up cards will be in waste pile {num2}?", "difficulty": "Easy", "is_mcq": False, "description": "Simulate click stockpile"},
        
        # 4: ActionOutcome - Multiple choice
        {"qa_type": "State Prediction", "template": "What will happen if I want to move the number {num1} card of pile {num2} to pile {num3}?", "difficulty": "Medium", "is_mcq": True, "description": "Predict card move result"},
        
        # 5: TransitionPath - Multiple choice
        {"qa_type": "State Prediction", "template": "What should I do if I want to reveal the first face-down card in waste pile {num}?", "difficulty": "Hard", "is_mcq": True, "description": "Reveal face-down card strategy"},
        
        # 6: StrategyOptimization - Multiple choice
        {"qa_type": "Strategy Optimization", "template": "Based on the current board state, what is the optimal strategy we should adopt?", "difficulty": "Hard", "is_mcq": True, "description": "Optimal card move selection"}
    ]
    
    # Select question based on num
    num = num % 10  # Ensure num is within 0-9
    question_id = 0
    if num == 0:
        question_choice = question_types[0]  # Question 0
        question_id = 0
    elif num == 1:
        question_choice = question_types[1]  # Question 1
        question_id = 1
    elif num == 2:
        question_choice = question_types[2]  # Question 2
        question_id = 2
    elif num == 3:
        question_choice = question_types[3]  # Question 3
        question_id = 3
    elif num in [4, 5, 6, 7]:
        question_choice = question_types[4]  # Question 4 (ActionOutcome)
        question_id = 4
    elif num == 8:
        question_choice = question_types[5]  # Question 5 (TransitionPath)
        question_id = 5
    elif num == 9:
        question_choice = question_types[6]  # Question 6 (StrategyOptimization)
        question_id = 6
    
    qa_type = question_choice["qa_type"]
    question_template = question_choice["template"]
    qa_level = question_choice["difficulty"]  # 'Easy', 'Medium', 'Hard'
    is_mcq = question_choice["is_mcq"]
    question_description = question_choice["description"]

    # Initialize options as None
    options = None
    
    # Handle each question type accordingly
    if qa_type == "Target Perception":
        if "How many times can the stockpile still deal cards?" in question_template:
            # Question Type 0
            question = f"{question_prompt}\n\n**Question:** {question_template}"
            deals_left = model_instance.dealsLeft()
            answer = str(deals_left)
            # The stock draws at most MAX_STOCK_DISPLAY backs and writes "+N" for the rest
            shown = min(deals_left, 10)
            counting = (f"By counting the number of overlapping cards in the stockpile, we know that the stockpile can now be dealt {answer} times."
                        if shown == deals_left else
                        f"The stockpile draws at most 10 overlapping cards and notes the rest as \"+{deals_left - shown}\", "
                        f"so the stockpile can now be dealt {shown} + {deals_left - shown} = {answer} times.")
            analysis = (
                f"We can see that the stockpile has {shown} stacks of overlapping cards. " + counting
            )
            options = None  # Fill in the blank

        elif "Which card is on the top of waste pile {num}?" in question_template:
            # Question Type 1
            waste_pile_num = random.randint(0, num_waste - 1)
            question_filled = question_template.format(num=waste_pile_num)
            question = f"{question_prompt}\n\n**Question:** {question_filled}"
            
            if not model_instance.waste[waste_pile_num].isEmpty():
                top_card = model_instance.waste[waste_pile_num][-1]
                answer = f"{top_card.suit.capitalize()} {model.RANKNAMES[top_card.rank]}"
                # The last card of a pile is drawn lowest on screen and is always face up
                analysis = (
                    f"Waste pile {waste_pile_num} is the {waste_pile_num + 1}-th pile from the left. Its top card is the one drawn "
                    f"lowest in that pile, and it is face up, so we can read its rank and suit directly. "
                    f"So the top card of waste pile {waste_pile_num} is the {model.RANKNAMES[top_card.rank]} of {top_card.suit.capitalize()}."
                )
            else:
                answer = "Empty"
                analysis = (f"Waste pile {waste_pile_num} is the {waste_pile_num + 1}-th pile from the left, and it holds no cards, "
                            f"so it has no top card.")
            options = None  # Fill in the blank
        
        elif "How many face-down cards are currently in all waste piles?" in question_template:
            # Question Type 2
            question = f"{question_prompt}\n\n**Question:** {question_template}"
            answer = str(model_instance.downCards())
            
            # Count the number of upside-down cards in each waste pile
            pile_counts = ", ".join([f"waste pile {k} has {model_instance.downUp(k)[0]} face-down cards" for k in range(num_waste)])
            
            analysis = (
                f"By counting the face-down cards of each waste pile, we find that {pile_counts}. "
                f"Therefore, there are a total of {model_instance.downCards()} face-down cards across all waste piles. "
            )
            options = None  # Fill in the blank
        
        elif "If I click the stockpile for {num1} times, how many face-up cards will be in waste pile {num2}?" in question_template:
            # Question Type 3
            num1 = random.randint(0, 5)
            waste_pile_num = random.randint(0, num_waste - 1)
            question_filled = question_template.format(num1=num1, num2=waste_pile_num)
            question = f"{question_prompt}\n\n**Question:** {question_filled}"
            
            # Each deal puts one card on every waste pile, but dealing is refused while a pile is empty
            deals_left = model_instance.dealsLeft()
            possible_deals = 0 if not model_instance.canDeal() else min(num1, deals_left)
            current_face_up = model_instance.downUp(waste_pile_num)[1]
            new_face_up = current_face_up + possible_deals
            answer = str(new_face_up)
            if not model_instance.canDeal():
                limit = (f"A waste pile is currently empty, and cards may not be dealt while that is the case, "
                         f"so none of the {num1} click(s) deals a card.")
            elif possible_deals < num1:
                limit = (f"The stockpile can only be dealt {deals_left} more time(s), so only {possible_deals} of the "
                         f"{num1} click(s) deal a card.")
            else:
                limit = f"Each deal puts one card face up on every waste pile, so {num1} click(s) add {possible_deals} card(s) to this pile."
            analysis = (
                f"{limit} "
                f"Currently, there are {current_face_up} face-up card(s) in waste pile {waste_pile_num}. "
                f"Therefore, after clicking the stockpile {num1} time(s), there would be {current_face_up} + {possible_deals} = "
                f"{new_face_up} face-up card(s) in waste pile {waste_pile_num}."
            )
            options = None  # Fill in the blank
    
    elif qa_type == "State Prediction" and "What will happen if I want to move the number {num1} card of pile {num2} to pile {num3}?" in question_template:
        # Question Type: "What will happen if I want to move the number {num1} card of pile {num2} to pile {num3}?" (Multiple choice)
        # {num1}: card index in the pile (0-based)
        # {num2}: source pile index
        # {num3}: destination pile index
        
        # Randomly select a source pile
        source_pile_index = random.randint(0, num_waste - 1)
        source_pile = model_instance.waste[source_pile_index]

        # Determine whether to select a face-down card (20% probability)
        if random.random() < 0.2:
            # Try to select a random face-down card index
            face_down_indices = [i for i, card in enumerate(source_pile) if card.faceDown()]
            if not face_down_indices:
                # If no face-down cards, fallback to selecting a face-up card
                face_up_indices = [i for i, card in enumerate(source_pile) if card.faceUp()]
                card_index = random.choice(face_up_indices) if face_up_indices else -1
            else:
                card_index = random.choice(face_down_indices)
        else:
            # Try to select a random face-up card
            face_up_indices = [i for i, card in enumerate(source_pile) if card.faceUp()]
            card_index = random.choice(face_up_indices) if face_up_indices else -1

        # Select destination pile with strategy
        if random.random() < 0.75:
            # 75% chance to select a potentially valid destination
            if card_index != -1 and card_index < len(source_pile):
                card_to_move = source_pile[card_index]
                possible_destinations = []
                for idx, pile in enumerate(model_instance.waste):
                    if idx == source_pile_index:
                        continue
                    if pile.isEmpty() or (pile[-1].rank - card_to_move.rank == 1):
                        possible_destinations.append(idx)
                
                if possible_destinations:
                    destination_pile_index = random.choice(possible_destinations)
                else:
                    # If no suitable destination, select randomly excluding source pile
                    destination_pile_index = random.randint(0, num_waste - 1)
                    while destination_pile_index == source_pile_index:
                        destination_pile_index = random.randint(0, num_waste - 1)
            else:
                # Invalid card_index, select random destination
                destination_pile_index = random.randint(0, num_waste - 1)
                while destination_pile_index == source_pile_index:
                    destination_pile_index = random.randint(0, num_waste - 1)
        else:
            # 25% chance to select completely random destination
            destination_pile_index = random.randint(0, num_waste - 1)
            while destination_pile_index == source_pile_index:
                destination_pile_index = random.randint(0, num_waste - 1)

        # Format the question
        question_filled = question_template.format(
            num1=card_index,
            num2=source_pile_index,
            num3=destination_pile_index
        )
        question = f"{question_prompt}\n\n**Question:** {question_filled}"

        # Standard note text for all analyses
        note_text = (
            f"Note: The number {card_index} card in pile {source_pile_index} is the {card_index + 1}-th card from the bottom. "
            f"Source pile {source_pile_index} is the {source_pile_index + 1}-th pile from the left, and "
            f"destination pile {destination_pile_index} is the {destination_pile_index + 1}-th pile from the left."
        )

        # Determine the correct option and analysis
        dest_pile = model_instance.waste[destination_pile_index]

        if card_index == -1 or card_index >= len(source_pile):
            # Case 1: Invalid card index
            correct_option = "E"
            analysis = (
                f"Waste pile {source_pile_index} holds {len(source_pile)} card(s), numbered 0 to {len(source_pile) - 1}, "
                f"so there is no card numbered {card_index} in it and the move cannot be made. {note_text}"
            )
        else:
            card_to_move = source_pile[card_index]
            
            # Case 2: Face-down card
            if card_to_move.faceDown():
                num_face_down_here = model_instance.downUp(source_pile_index)[0]
                correct_option = "B"
                analysis = (
                    f"The first {num_face_down_here} card(s) of pile {source_pile_index} (numbers 0 to {num_face_down_here - 1}) are face down, "
                    f"so the selected card {card_index} is face down and its value is unknown. "
                    f"In Spider Solitaire, only face-up cards can be moved since their values are visible. {note_text}"
                )
            else:
                # Check the selected card and all cards above it
                if card_index < len(source_pile) - 1:
                    cards_to_check = source_pile[card_index:]  # Include the selected card and all cards above it
                    # Check if any cards above are face-down
                    has_face_down_above = any(card.faceDown() for card in cards_to_check[1:])  # Skip the selected card itself
                    
                    # Check if cards form a descending sequence starting from the selected card
                    is_descending = True
                    for i in range(len(cards_to_check) - 1):
                        current_card = cards_to_check[i]
                        next_card = cards_to_check[i + 1]
                        if next_card.rank != current_card.rank - 1:
                            is_descending = False
                            break
                    
                    above = len(cards_to_check) - 1
                    if has_face_down_above:
                        correct_option = "B"
                        analysis = (
                            f"The move cannot be made because there {'is' if above == 1 else 'are'} {above} face-down "
                            f"card(s) above the selected card. All cards above the selected card must be face-up to move the sequence. {note_text}"
                        )
                    elif not is_descending:
                        correct_option = "C"
                        ranks = ", ".join(model.RANKNAMES[c.rank] for c in cards_to_check)
                        analysis = (
                            f"The move cannot be made because the selected card and the {above} card(s) above it "
                            f"({ranks}, from the selected card upwards) do not form a descending sequence, "
                            f"so they cannot be moved together. {note_text}"
                        )
                    else:
                        # Check destination pile compatibility
                        moved = f"{len(cards_to_check)} cards (the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()} and the {above} card(s) above it, a descending sequence)"
                        if dest_pile.isEmpty():
                            correct_option = "A"
                            analysis = (
                                f"Moving {moved} from pile {source_pile_index} to pile {destination_pile_index} is successful: "
                                f"pile {destination_pile_index} is empty, and an empty pile accepts any card. {note_text}"
                            )
                        else:
                            dest_top_card = dest_pile[-1]
                            if dest_top_card.rank - card_to_move.rank == 1:
                                correct_option = "A"
                                analysis = (
                                    f"Moving {moved} from pile {source_pile_index} to pile {destination_pile_index} is successful: "
                                    f"the top card of pile {destination_pile_index} is the {model.RANKNAMES[dest_top_card.rank]}, one rank higher than the "
                                    f"{model.RANKNAMES[card_to_move.rank]} being moved, so the cards continue the descending sequence. {note_text}"
                                )
                            else:
                                correct_option = "D"
                                analysis = (
                                    f"The move cannot be made because the top card of the target pile {destination_pile_index} is the "
                                    f"{model.RANKNAMES[dest_top_card.rank]}, which is not one rank higher than the "
                                    f"{model.RANKNAMES[card_to_move.rank]} being moved. {note_text}"
                                )
                else:
                    # Moving a single card (top card of the pile)
                    single = f"the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()}, the top card of pile {source_pile_index},"
                    if dest_pile.isEmpty():
                        correct_option = "A"
                        analysis = (
                            f"Moving {single} to pile {destination_pile_index} is successful: "
                            f"pile {destination_pile_index} is empty, and an empty pile accepts any card. {note_text}"
                        )
                    else:
                        dest_top_card = dest_pile[-1]
                        if dest_top_card.rank - card_to_move.rank == 1:
                            correct_option = "A"
                            analysis = (
                                f"Moving {single} to pile {destination_pile_index} is successful: "
                                f"the top card of pile {destination_pile_index} is the {model.RANKNAMES[dest_top_card.rank]}, one rank higher, "
                                f"so the {model.RANKNAMES[card_to_move.rank]} continues the descending sequence. {note_text}"
                            )
                        else:
                            correct_option = "D"
                            analysis = (
                                f"The move cannot be made because the top card of the target pile {destination_pile_index} is the "
                                f"{model.RANKNAMES[dest_top_card.rank]}, which is not one rank higher than the "
                                f"{model.RANKNAMES[card_to_move.rank]} being moved. {note_text}"
                            )

        # Define the multiple choice options
        options = [
            "A. The move will be successful, and the cards will be in descending order, following the rules of movement.",
            "B. The move cannot be made because this card is face-down and its value is unknown.",
            "C. The move cannot be made because there is a card above it, and that card does not form a descending order with the selected card.",
            "D. The move cannot be made because the top card of the target pile does not have a rank equal to this card's rank plus one.",
            "E. The move cannot be made because the pile has too few cards, and this card does not exist."
        ]

        # Add options to the question
        question += "\n\n**Options:**\n" + "\n".join(options)

        answer = correct_option  # The correct option letter

    elif qa_type == "State Prediction" and "What should I do if I want to reveal the first face-down card in waste pile {num}?" in question_template:
        # Question Type 5
        # "What should I do if I want to reveal the first face-down card in waste pile {num}?" (Multiple choice)
        
        # 75% chance to ask about a pile whose first face-down card can be revealed in one move (when there is one).
        # On a random pile the answer is almost always B: after a deal the face-up cards rarely form a sequence.
        revealable_piles = [idx for idx in range(num_waste) if reveal_targets(model_instance, idx)]
        if revealable_piles and random.random() < 0.75:
            waste_pile_num = random.choice(revealable_piles)
        else:
            waste_pile_num = random.randint(0, num_waste - 1)
        waste_pile = model_instance.waste[waste_pile_num]

        # Face-down cards lie under the face-up ones, so the first face-up card is number num_face_down
        num_face_down = model_instance.downUp(waste_pile_num)[0]

        if num_face_down:
            moving_cards = waste_pile[num_face_down:]
            lead_card = moving_cards[0]
            can_move_together = model.Card.isDescending(moving_cards)
            possible_targets = reveal_targets(model_instance, waste_pile_num)

            if possible_targets:
                # If valid target piles are found, set correct_option to "C" to "H" (randomly among these)
                correct_option = random.choice(["C", "D", "E", "F", "G", "H"])
                correct_move_pile = random.choice(possible_targets)
                correct_move = f"We should move the {num_face_down}-th card of pile {waste_pile_num} to pile {correct_move_pile}."
                # Moving the same cards to any other possible target reveals the card too, so no distractor may say so
                reveal_moves = [f"We should move the {num_face_down}-th card of pile {waste_pile_num} to pile {idx}." for idx in possible_targets]

                # Prepare options B-H based on the correct_option assignment
                options = [
                    "A. No action is needed; there are no face-down cards in this pile.",
                    "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
                ] + random_move_options(["C", "D", "E", "F", "G", "H"], num_waste, (0, num_waste - 1), exclude=reveal_moves)

                # Update the options list, with the correct option at the correct index
                correct_option_idx = ["C", "D", "E", "F", "G", "H"].index(f"{correct_option}")
                options[correct_option_idx + 2] = f"{correct_option}. {correct_move}"

                # Update the analysis
                target_pile = model_instance.waste[correct_move_pile]
                target_text = (
                    f"Pile {correct_move_pile} is empty" if target_pile.isEmpty()
                    else f"The top card of pile {correct_move_pile} is the {model.RANKNAMES[target_pile[-1].rank]}, one rank higher"
                )
                ranks = ", ".join(model.RANKNAMES[c.rank] for c in moving_cards)
                analysis = (
                    f"Waste pile {waste_pile_num} has {num_face_down} face-down card(s) (numbers 0 to {num_face_down - 1}) with "
                    f"{len(moving_cards)} face-up card(s) on top of them. To reveal the first face-down card, all of those face-up cards "
                    f"must leave the pile, and one move can take them only as a whole descending sequence. "
                    f"They are {ranks} (from the {num_face_down}-th card upwards), which is such a sequence, so they can be moved together. "
                    f"{target_text}, so moving them to pile {correct_move_pile} is a valid move, allowing the face-down card to be revealed."
                )
            else:
                # No single move can take away all face-up cards above the first face-down card
                correct_option = "B"
                ranks = ", ".join(model.RANKNAMES[c.rank] for c in moving_cards)
                if can_move_together:
                    reason = (
                        f"They are {ranks}, a descending sequence, so they could move together, but no other waste pile is empty "
                        f"or has the {model.RANKNAMES[lead_card.rank + 1] if lead_card.rank < 13 else 'required card'} on top, "
                        f"so there is nowhere to put them."
                    )
                else:
                    reason = (
                        f"They are {ranks} (from the {num_face_down}-th card upwards), which is not a descending sequence, "
                        f"so they cannot be moved away together, and only the whole group leaving would reveal the card."
                    )
                analysis = (
                    f"Waste pile {waste_pile_num} has {num_face_down} face-down card(s) with {len(moving_cards)} face-up card(s) on top of them. "
                    f"{reason} "
                    f"So we can't reveal the first face-down card by moving those face-up cards to another waste pile in one move. "
                    f"To reveal it, you need to move cards from other piles first and wait for more information."
                )

                options = [
                    "A. No action is needed; there are no face-down cards in this pile.",
                    "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
                ] + random_move_options(["C", "D", "E", "F", "G", "H"], num_waste, (0, num_waste - 1))

        else:
            # If there are no face-down cards in the selected pile, default to option A
            correct_option = "A"
            analysis = (
                f"Waste pile {waste_pile_num} holds {len(waste_pile)} card(s), and all of them are face up, so there is no "
                f"face-down card to reveal and no action is needed."
                if waste_pile else
                f"Waste pile {waste_pile_num} is empty, so it has no face-down card to reveal and no action is needed."
            )

            options = [
                "A. No action is needed; there are no face-down cards in this pile.",
                "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
            ] + random_move_options(["C", "D", "E", "F", "G", "H"], num_waste, (1, 5))

        # Fill the question template with the selected waste pile number
        question_filled = question_template.format(num=waste_pile_num)
        question = f"{question_prompt}\n\n**Question:** {question_filled}"

        # Append options to the question
        question += "\n\n**Options:**\n" + "\n".join(options)

        # Assign the correct answer
        answer = correct_option

    elif qa_type == "Strategy Optimization":
        # Question Type 6
        # "Based on the current board state, what is the optimal strategy we should adopt?" (Multiple choice)
        
        # Determine the optimal strategy based on the model's state
        # Priority:
        # 1. Move complete sequences to foundation.
        # 2. Form descending sequences of the same suit as long as possible.
        # 3. Utilize empty waste piles.
        # 4. Deal from the stockpile if no immediate moves are available.
        
        # Initialize variables to determine which priority is applicable
        can_move_complete_sequences = False
        can_form_descending_same_suit = False
        can_utilize_empty_piles = False
        can_deal_stock = False
        
        # Priority 1: Move complete sequences to foundation
        for f_index, foundation in enumerate(model_instance.foundations):
            if len(foundation) == 13:
                continue  # Foundation already complete
            for w_index, waste_pile in enumerate(model_instance.waste):
                if len(waste_pile) >= 13:
                    sequence = waste_pile[-13:]
                    if model_instance.is_complete_sequence(sequence):
                        can_move_complete_sequences = True
                        source_pile_index = w_index
                        target_foundation_index = f_index
                        break
            if can_move_complete_sequences:
                break
        
        # Priority 2: Form descending sequences of the same suit as long as possible
        if not can_move_complete_sequences:
            best_move = find_longest_same_suit_sequence(model_instance)
            if best_move:
                can_form_descending_same_suit = True
        
        # Priority 3: Utilize empty waste piles (only if some sequence can actually be moved into one)
        if not can_move_complete_sequences and not can_form_descending_same_suit:
            empty_pile_indices = [i for i, pile in enumerate(model_instance.waste) if pile.isEmpty()]
            can_utilize_empty_piles = any(destination in empty_pile_indices
                                          for _, _, destination, _ in legal_sequence_moves(model_instance))
        
        # Priority 4: Deal from the stockpile if no immediate moves are available.
        # canDeal() only checks that no waste pile is empty, so the stock may still be exhausted.
        if not can_move_complete_sequences and not can_form_descending_same_suit and not can_utilize_empty_piles:
            can_deal_stock = model_instance.canDeal() and model_instance.dealsLeft() > 0
        
        # Decide which priority to act on
        if can_move_complete_sequences:
            # Priority 1: Move a complete King-to-Ace sequence to a foundation pile (Option H)
            correct_option = "H"
            analysis = (
                f"The top 13 cards of waste pile {source_pile_index} form a complete King-to-Ace sequence, "
                f"so they can be moved to foundation pile {target_foundation_index}. "
                f"Completing a foundation pile is the biggest possible gain, so this takes priority over any other move."
            )
            
            
            # Option H: Move to foundation pile (correct)
            options = random_move_options(["A", "B", "C", "D", "E", "F"], num_waste, (1, 5)) + [
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {source_pile_index} to the foundation piles.",
            ]

        elif can_form_descending_same_suit:
            # Priority 2: Form descending sequences of the same suit as long as possible (Options A or B)
            # Choose between Option A and B randomly for correct option
            source_pile_index, dest_pile_index, card_idx = best_move
            correct_move = f"We should move the {card_idx}-th card of pile {source_pile_index} to pile {dest_pile_index}."
            # The move takes the card at index card_idx and every card above it
            num_cards = len(model_instance.waste[source_pile_index]) - card_idx
            # Any other move of an equally long sequence is just as good, so no distractor may name one
            equally_long_moves = [
                f"We should move the {k}-th card of pile {source} to pile {destination}."
                for source, k, destination, length in legal_sequence_moves(model_instance) if length == num_cards
            ]
            options = random_move_options(["A", "B", "C", "D", "E", "F"], num_waste, (1, 5), exclude=equally_long_moves) + [
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]

            correct_option_choice = random.choice(["A", "B", "C", "D", "E", "F"])
            analysis = (
                f"The optimal strategy is to form the longest descending sequence to maximize potential moves. "
                f"Moving {num_cards} card(s) (the {card_idx}-th card{' and those above it' if num_cards > 1 else ''}) from pile {source_pile_index} to pile {dest_pile_index} forms the longest possible descending sequence. "
                f"So this move is optimal because it forms a sequence longer than any other move can."
            )

            # Assign correct_option based on the choice
            correct_option = correct_option_choice

            # Find the correct option by replacing the placeholder in the chosen option
            correct_option_idx = ["A", "B", "C", "D", "E", "F"].index(f"{correct_option}")

            # Update the options list, with the correct option at the correct index
            options[correct_option_idx] = f"{correct_option}. {correct_move}"


        elif can_utilize_empty_piles:
            # Priority 3: Utilize empty waste piles. Any face-up movable sequence can go to an empty pile,
            # so pick a real move: the longest sequence that can be moved there.
            empty_piles = [i for i, pile in enumerate(model_instance.waste) if pile.isEmpty()]
            target_pile = random.choice(empty_piles)
            candidates = [(source, k, length) for source, k, destination, length in legal_sequence_moves(model_instance)
                          if destination == target_pile]
            source_pile, card_idx, num_cards = max(candidates, key=lambda c: c[2])
            lead_card = model_instance.waste[source_pile][card_idx]
            correct_move = f"We should move the {card_idx}-th card of pile {source_pile} to pile {target_pile}."
            # No distractor may name another move into an empty pile with a sequence at least as long
            equally_good = [f"We should move the {k}-th card of pile {source} to pile {destination}."
                            for source, k, destination, length in legal_sequence_moves(model_instance)
                            if destination in empty_piles and length >= num_cards]
            analysis = (
                f"Waste pile {target_pile} is empty, and an empty pile accepts any card. "
                f"Moving {num_cards} card(s) (the {card_idx}-th card{' and those above it' if num_cards > 1 else ''}, "
                f"starting with the {model.RANKNAMES[lead_card.rank]} of {lead_card.suit.capitalize()}) from pile {source_pile} "
                f"to pile {target_pile} is the longest sequence we can move there. "
                f"Using empty waste piles provides more flexibility in organizing cards and creates more opportunities for valid moves."
            )

            correct_option = random.choice(["A", "B", "C", "D", "E", "F"])
            options = random_move_options(["A", "B", "C", "D", "E", "F"], num_waste, (1, 5), exclude=equally_good) + [
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]
            options[["A", "B", "C", "D", "E", "F"].index(correct_option)] = f"{correct_option}. {correct_move}"

        elif can_deal_stock:
            # Priority 4: Deal from the stockpile if no immediate moves are available (Option G)
            correct_option = "G"
            analysis = (
                f"No face-up sequence can be moved onto another waste pile: no pile is empty, and no pile has a top card "
                f"one rank higher than a movable sequence. No waste pile is empty, so dealing is allowed, and the stockpile "
                f"can still be dealt {model_instance.dealsLeft()} time(s). Dealing uncovers new cards and creates new opportunities for moves."
            )

            options = random_move_options(["A", "B", "C", "D", "E", "F"], num_waste, (1, 5)) + [
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]

        else:
            # No move, and the stock cannot be dealt either (it is empty, or a waste pile is empty): the
            # game is stuck, so none of the moves is available. Option G is the only one that does not
            # name a move, and the analysis says why dealing is not possible either.
            correct_option = "G"
            reason = ("the stockpile is empty" if model_instance.dealsLeft() == 0
                      else "a waste pile is empty, and cards may not be dealt while that is the case")
            analysis = (
                f"No face-up sequence can be moved onto another waste pile, and no waste pile holds a complete "
                f"King-to-Ace sequence to send to a foundation pile. Dealing is not possible either, because {reason}. "
                f"None of the listed moves can be made in this position."
            )

            options = random_move_options(["A", "B", "C", "D", "E", "F"], num_waste, (1, 5)) + [
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles."
            ]
        # Fill the question template with the selected waste pile number
        question_filled = question_template  # No placeholders to replace
        question = f"{question_prompt}\n\n**Question:** {question_filled}"
        
        # Append options to the question
        question += "\n\n**Options:**\n" + "\n".join(options)
        
        # Assign the correct answer
        answer = correct_option
    
    return qa_type, qa_level, question, question_id, question_description, answer, analysis, options
