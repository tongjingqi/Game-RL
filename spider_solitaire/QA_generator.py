# QA_generator.py
import random
from typing import Tuple, List, Optional
import model
from model import Stack, SelectableStack, OneWayStack, Card, Model

VALID_QA_TYPES = {"StateInfo", "ActionOutcome", "TransitionPath", "StrategyOptimization"}

question_prompt = """
Spider Solitaire

# OBJECTIVE
Spider is played with eight decks of 13 spade cards each, totaling 104 unique cards. The goal is to arrange all cards in a King-to-Ace sequence in the same suit and move them to the foundation piles. Once all sequences are moved to the foundations, the game is won.

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
  - The card at the bottom of each waste pile (usually face-down) is numbered **0** and is the **topmost visible card** in the pile.
  - As you move upward in the pile, the next cards are numbered **1**, **2**, **3**, and so on.
  - Visually, the bottom card (number **0**) is the one closest to the top of the screen, and the cards above it are stacked above in the pile, going downwards.

## **Foundation Pile**
Foundation pile stores all the arranged suit. When a suit is arranged in sequence, it may be removed to a foundation pile. If all suits are moved to the foundations, the game is won.
Foundation Pile is in the top right corner of the board.

# MOVING CARDS
- **Movement Conditions**: 
  - **Move a single card**: The single card being moved must be placed on a top card that is of the **same suit** and has a **higher rank** (e.g., a Q can be placed on a K). 
  - **Move multiple cards**: A complete **descending sequence** of cards (such as K, Q, J, 10, etc.) can be moved from one pile to another. When moving a descending sequence of cards to another pile, the new sequence must be a **same-suit sequence** and follow the **descending order** from K, Q, J, 10, 9, ..., 2, A.
- **Face-Down Cards**: If the sequence you are moving includes face-down cards, they will be flipped face-up once they are moved. After flipping, the newly face-up cards can continue to be moved or interacted with.
- **Example**: If you have a sequence of K-Q-J-10-9-8-7 in the same suit, you can move a card 6 that has the same suit to the top of this pile, resulting in a new sequence K-Q-J-10-9-8-7-6.
- **Empty Pile Rule**: An empty waste pile can accept any card. After placing the card, you can continue adding a descending same-suit sequence to that pile.
- **Reveal Cards**: If a move leaves a face-down card on top, it will be turned face-up.

# DEALING
Click the stock to deal a new row of face-up cards to the waste piles. You may not deal if there is an empty waste pile.

# STRATEGY
- Turn face-down cards face-up.
- Form runs of the same suit in descending order.
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
        {"qa_type": "StateInfo", "template": "How many times can the stockpile still deal cards?", "difficulty": "Easy", "is_mcq": False, "description": "Remaining deals in the stockpile"},
        
        # 1: StateInfo
        {"qa_type": "StateInfo", "template": "Which card is on the top of waste pile {num}?", "difficulty": "Easy", "is_mcq": False, "description": "Identify a card of a waste pile"},
        
        # 2: StateInfo
        {"qa_type": "StateInfo", "template": "How many face-down cards are currently in all waste piles?", "difficulty": "Easy", "is_mcq": False, "description": "Count face-down cards in all waste piles"},
        
        # 3: StateInfo
        {"qa_type": "StateInfo", "template": "If I click the stockpile for {num1} times, how many face-up cards will be in waste pile {num2}?", "difficulty": "Easy", "is_mcq": False, "description": "Simulate click stockpile"},
        
        # 4: ActionOutcome - Multiple choice
        {"qa_type": "ActionOutcome", "template": "What will happen if I want to move the number {num1} card of pile {num2} to pile {num3}?", "difficulty": "Medium", "is_mcq": True, "description": "Predict card move result"},
        
        # 5: TransitionPath - Multiple choice
        {"qa_type": "TransitionPath", "template": "What should I do if I want to reveal the first face-down card in waste pile {num}?", "difficulty": "Hard", "is_mcq": True, "description": "Reveal face-down card strategy"},
        
        # 6: StrategyOptimization - Multiple choice
        {"qa_type": "StrategyOptimization", "template": "Based on the current board state, what is the optimal strategy we should adopt?", "difficulty": "Hard", "is_mcq": True, "description": "Optimal card move selection"}
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
    if qa_type == "StateInfo":
        if "How many times can the stockpile still deal cards?" in question_template:
            # Question Type 0
            question = f"{question_prompt}\n\n**Question:** {question_template}"
            answer = str(model_instance.dealsLeft())
            analysis = (
                f"We can see that the stockpile has {model_instance.dealsLeft()} stacks of overlapping cards. "
                f"By counting the number of overlapping cards in the stockpile, we know that the stockpile can now be dealt {answer} times"
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
                analysis = (
                    f"By checking the top card on the {waste_pile_num + 1}-th waste pile, we can know its rank and suit. "
                    f"So the top card of waste pile {waste_pile_num} is the {model.RANKNAMES[top_card.rank]} of {top_card.suit.capitalize()}."
                )
            else:
                answer = "Empty"
                analysis = f"Waste pile {waste_pile_num} is currently empty."
            options = None  # Fill in the blank
        
        elif "How many face-down cards are currently in all waste piles?" in question_template:
            # Question Type 2
            question = f"{question_prompt}\n\n**Question:** {question_template}"
            answer = str(model_instance.downCards())
            
            # Count the number of upside-down cards in each waste pile
            pile_counts = ", ".join([f"waste pile {k} has {model_instance.downUp(k)[0]} face-down cards" for k in range(num_waste)])
            
            analysis = (
                f"By counting the face-downs cards of each waste pile, we find that {pile_counts}."
                f"Therefore, there are a total of {model_instance.downCards()} face-down cards across all waste piles. "
            )
            options = None  # Fill in the blank
        
        elif "If I click the stockpile for {num1} times, how many face-up cards will be in waste pile {num2}?" in question_template:
            # Question Type 3
            num1 = random.randint(0, 5)
            waste_pile_num = random.randint(0, num_waste - 1)
            question_filled = question_template.format(num1=num1, num2=waste_pile_num)
            question = f"{question_prompt}\n\n**Question:** {question_filled}"
            
            # Calculate how many times we can actually deal twice
            possible_deals = min(num1, model_instance.dealsLeft())
            current_face_up = model_instance.downUp(waste_pile_num)[1]
            additional_face_up = possible_deals
            new_face_up = current_face_up + additional_face_up
            answer = str(new_face_up)
            analysis = (
                f"Dealing {num1} time(s) would add {additional_face_up} face-up card(s) to waste pile {waste_pile_num}. "
                f"Currently, there are {current_face_up} face-up card(s) in this pile. "
                f"Therefore, after clicking the stock pile, there would be {new_face_up} face-up card(s) in waste pile {waste_pile_num}."
            )
            options = None  # Fill in the blank
    
    elif qa_type == "ActionOutcome":
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
                f"The specified card does not exist in the source pile. "
                f"This could be due to selecting an index out of range. {note_text}"
            )
        else:
            card_to_move = source_pile[card_index]
            
            # Case 2: Face-down card
            if card_to_move.faceDown():
                correct_option = "B"
                analysis = (
                    f"The move cannot be made because the selected card is face-down and its value is unknown. "
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
                    
                    if has_face_down_above:
                        correct_option = "B"
                        analysis = (
                            f"The move cannot be made because there are face-down cards above the selected card. "
                            f"All cards above the selected card must be face-up to move the sequence. {note_text}"
                        )
                    elif not is_descending:
                        correct_option = "C"
                        analysis = (
                            f"The move cannot be made because the cards above the selected card "
                            f"do not form a valid descending sequence. {note_text}"
                        )
                    else:
                        # Check destination pile compatibility
                        if dest_pile.isEmpty():
                            correct_option = "A"
                            analysis = (
                                f"Moving the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()} "
                                f"and cards above it from pile {source_pile_index} to the empty pile {destination_pile_index} "
                                f"is successful. {note_text}"
                            )
                        else:
                            dest_top_card = dest_pile[-1]
                            if dest_top_card.rank - card_to_move.rank == 1:
                                correct_option = "A"
                                analysis = (
                                    f"Moving the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()} "
                                    f"and cards above it from pile {source_pile_index} to pile {destination_pile_index} "
                                    f"is successful as it forms a valid descending sequence. {note_text}"
                                )
                            else:
                                correct_option = "D"
                                analysis = (
                                    f"The move cannot be made because the top card of the target pile {destination_pile_index} "
                                    f"does not have a rank equal to this card's rank plus one. {note_text}"
                                )
                else:
                    # Moving a single card (top card of the pile)
                    if dest_pile.isEmpty():
                        correct_option = "A"
                        analysis = (
                            f"Moving the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()} "
                            f"from pile {source_pile_index} to the empty pile {destination_pile_index} "
                            f"is successful. {note_text}"
                        )
                    else:
                        dest_top_card = dest_pile[-1]
                        if dest_top_card.rank - card_to_move.rank == 1:
                            correct_option = "A"
                            analysis = (
                                f"Moving the {model.RANKNAMES[card_to_move.rank]} of {card_to_move.suit.capitalize()} "
                                f"from pile {source_pile_index} to pile {destination_pile_index} "
                                f"is successful as it forms a valid descending sequence. {note_text}"
                            )
                        else:
                            correct_option = "D"
                            analysis = (
                                f"The move cannot be made because the top card of the target pile {destination_pile_index} "
                                f"does not have a rank equal to this card's rank plus one. {note_text}"
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

    elif qa_type == "TransitionPath":
        # Question Type 5
        # "What should I do if I want to reveal the first face-down card in waste pile {num}?" (Multiple choice)
        
        # Step 1: Select a waste pile that has only one card at the top and that card is face-down
        # If multiple such piles exist, randomly choose one
        candidate_piles = [
            i for i, pile in enumerate(model_instance.waste)
            if len(pile) == 1 and pile[-1].faceDown()
        ]
        
        if candidate_piles:
            # If such piles exist, select one randomly
            waste_pile_num = random.choice(candidate_piles)
            correct_option = "A"
            analysis = (
                f"The first face-down card in waste pile {waste_pile_num} is already at the top and should be face up. "
                f"No action is needed as there are no face-down cards above it."
            )
        else:
            # If no such pile exists, select a random pile
            waste_pile_num = random.randint(0, num_waste - 1)
            waste_pile = model_instance.waste[waste_pile_num]
            
            # Check if there are any face-down cards in the selected pile
            has_face_down = any(card.faceDown() for card in waste_pile)
            
            if has_face_down:
                # Determine if the first face-down card can be revealed by moving the top card
                # Search for target piles where the top card is one higher than the selected pile's top card
                selected_top_card = waste_pile[-1]
                possible_targets = [
                    idx for idx, pile in enumerate(model_instance.waste)
                    if idx != waste_pile_num and (
                        pile.isEmpty() or (pile[-1].rank - selected_top_card.rank == 1)
                    )
                ]

                if possible_targets:
                    # If valid target piles are found, set correct_option to "C" to "H" (randomly among these)
                    correct_option = random.choice(["C", "D", "E", "F", "G", "H"])
                    correct_move_pile = random.choice(possible_targets)
                    
                    # Generate incorrect move piles by selecting piles that do not satisfy the move condition
                    invalid_targets = [
                        idx for idx, pile in enumerate(model_instance.waste)
                        if idx != waste_pile_num and (
                            not pile.isEmpty() and (pile[-1].rank - selected_top_card.rank != 1)
                        )
                    ]
                    
                    if invalid_targets:
                        incorrect_move_pile = random.choice(invalid_targets)
                    else:
                        # If no invalid targets are found, select a random pile excluding the source
                        incorrect_move_pile = random.randint(0, num_waste - 1)
                        while incorrect_move_pile == waste_pile_num:
                            incorrect_move_pile = random.randint(0, num_waste - 1)
                    
                    # Prepare options B-H based on the correct_option assignment
                    options = [
                        "A. No action is needed; there are no face-down cards in this pile.",
                        "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
                        f"C. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"D. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"E. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"F. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"G. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"H. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}."
                    ]
                    
                    # Find the correct option by replacing the placeholder in the chosen option
                    correct_option_idx = ["C", "D", "E", "F", "G", "H"].index(f"{correct_option}")
                    
                    # Update the options list, with the correct option at the correct index
                    options[correct_option_idx + 2] = f"{correct_option}. We should move the card of pile {waste_pile_num} to pile {correct_move_pile}."
                    
                    # Update the analysis
                    analysis = (
                        f"To reveal the first face-down card in waste pile {waste_pile_num}, you should move the top card to another pile where it can form a descending sequence. "
                        f"Moving it to pile {correct_move_pile} is a valid move, allowing the face-down card to be revealed."
                    )
                else:
                    # No valid target piles found, default to option D
                    correct_option = "B"
                    analysis = (
                        f"In waste pile {waste_pile_num}, there are face-down cards that are not at the top. "
                        f"And there is no operation to move the top cards from this waste pile to another waste pile."
                        f"So we can't reveal the first face-down card by directly removing the above face-up cards to another waste pile."
                        f"To reveal the first face-down card, you need to move cards from other piles first and wait for more information."
                    )
                    
                    # Generate random indices for options B, C, and other options
                    options = [
                        "A. No action is needed; there are no face-down cards in this pile.",
                        "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
                        f"C. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"D. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"E. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"F. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"G. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                        f"H. We should move the {random.randint(0, num_waste - 1)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}."
                    ]

            else:
                # If there are no face-down cards in the selected pile, default to option A
                waste_pile_num = random.randint(0, num_waste - 1)
                correct_option = "A"
                analysis = (
                    f"In waste pile {waste_pile_num}, all the cards are face up. There are no face-down cards in waste pile {waste_pile_num}."
                )
                
                options = [
                    "A. No action is needed; there are no face-down cards in this pile.",
                    "B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.",
                    f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                    f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                    f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                    f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                    f"G. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                    f"H. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}."
                ]
            
            # Fill the question template with the selected waste pile number
            question_filled = question_template.format(num=waste_pile_num)
            question = f"{question_prompt}\n\n**Question:** {question_filled}"
            
            # Append options to the question
            question += "\n\n**Options:**\n" + "\n".join(options)
            
            # Assign the correct answer
            answer = correct_option
    
    elif qa_type == "StrategyOptimization":
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
                        target_foundation_index = f_index
                        break
            if can_move_complete_sequences:
                break
        
        # Priority 2: Form descending sequences of the same suit as long as possible
        if not can_move_complete_sequences:
            best_move = find_longest_same_suit_sequence(model_instance)
            if best_move:
                can_form_descending_same_suit = True
        
        # Priority 3: Utilize empty waste piles
        if not can_move_complete_sequences and not can_form_descending_same_suit:
            can_utilize_empty_piles = any(pile.isEmpty() for pile in model_instance.waste)
        
        # Priority 4: Deal from the stockpile if no immediate moves are available
        if not can_move_complete_sequences and not can_form_descending_same_suit and not can_utilize_empty_piles:
            can_deal_stock = model_instance.canDeal()
        
        # Decide which priority to act on
        if can_move_complete_sequences:
            # Priority 1: Move complete sequences to foundation (Option D)
            correct_option = "H"
            analysis = (
                "There are complete sequences available to move to the foundation piles. "
                "Moving them will help progress towards winning the game."
            )
            
            
            # Option H: Move to foundation pile (correct)
            options = [
                f"A. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"B. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {target_foundation_index} to the foundation piles.",
            ]

        elif can_form_descending_same_suit:
            # Priority 2: Form descending sequences of the same suit as long as possible (Options A or B)
            # Choose between Option A and B randomly for correct option
            options = [
                f"A. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"B. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]

            correct_option_choice = random.choice(["A", "B", "C", "D", "E", "F"])
            source_pile_index, dest_pile_index, num_cards = best_move
            analysis = (
                f"The optimal strategy is to form a descending sequence of the same suit to maximize potential moves. "
                f"Moving {num_cards} card(s) from pile {source_pile_index} to pile {dest_pile_index} forms the longest possible descending sequence of the same suit. "
                f"So this move is optimal becauce it forms a sequence longer than any other moves."
            )
            
            # Assign correct_option based on the choice
            correct_option = correct_option_choice
            
            # Find the correct option by replacing the placeholder in the chosen option
            correct_option_idx = ["A", "B", "C", "D", "E", "F"].index(f"{correct_option}")

            # Update the options list, with the correct option at the correct index
            options[correct_option_idx] = f"{correct_option}. We should move the {num_cards}-th card of pile {source_pile_index} to pile {dest_pile_index}."


        elif can_utilize_empty_piles:
            # Priority 3: Utilize empty waste piles (Options A or B)
            # Choose between Option A and B randomly for correct option
            correct_option_choice = random.choice(["A", "B", "C", "D", "E", "F"])
            analysis = (
                f"There is an empty pile 'pile {target_pile}' from which we can move our cards to. Utilizing empty waste piles provides more flexibility in organizing cards and can help in creating more opportunities for valid moves."
            )
            
            # Assign correct_option based on the choice
            correct_option = correct_option_choice  # <-- Added line
            
            options = [
                f"A. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"B. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]
            # Generate the correct and incorrect options
            # Correct option is to move cards to an empty pile
            empty_piles = [i for i, pile in enumerate(model_instance.waste) if pile.isEmpty()]
            if empty_piles:
                target_pile = random.choice(empty_piles)
                # Find a source pile that has at least one card
                source_pile = random.randint(0, num_waste - 1)
                while len(model_instance.waste[source_pile]) == 0:
                    source_pile = random.randint(0, num_waste - 1)
                num_cards = len(model_instance.waste[source_pile])

                # Assign correct_option based on the choice
                correct_option = correct_option_choice
                
                # Find the correct option by replacing the placeholder in the chosen option
                correct_option_idx = ["A", "B", "C", "D", "E", "F"].index(f"{correct_option}")

                # Update the options list, with the correct option at the correct index
                options[correct_option_idx] = f"{correct_option}. We should move the {num_cards}-th card of pile {source_pile} to pile {target_pile}."

        elif can_deal_stock:
            # Priority 4: Deal from the stockpile if no immediate moves are available (Option C)
            correct_option = "G"
            analysis = (
                "In the current game, no move can form a descending card order. So no immediate moves are available. Dealing cards from the stockpile will uncover new cards and create new opportunities for moves."
            )
            
            options = [
                f"A. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"B. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"G. No cards can be moved; we should click the stockpile to deal cards.",
                f"H. We should move cards from pile {random.randint(0, num_waste - 1)} to the foundation piles.",
            ]

        else:
            # Default case: No clear priority, choose a random action
            correct_option = "G"  # Arbitrary choice
            analysis = (
                "The current game state does not clearly indicate an optimal strategy."
            )
            
            options = [
                f"A. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"B. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"C. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"D. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"E. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
                f"F. We should move the {random.randint(1, 5)}-th card of pile {random.randint(0, num_waste - 1)} to pile {random.randint(0, num_waste - 1)}.",
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
