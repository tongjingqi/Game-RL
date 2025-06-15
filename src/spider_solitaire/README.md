# Spider Solitaire VQA Dataset Generator

## Overview
**Spider Solitaire VQA Dataset Generator** is a tool designed to simulate the classic card game **Spider Solitaire** and generate a comprehensive Visual Question Answering (VQA) dataset. The generated VQA dataset includes game images, questions, answers, and detailed analyses, making it ideal for training and evaluating multimodal models in understanding and reasoning about complex game environments.

## Game Rules
### OBJECTIVE
Spider is played with eight decks of 13 spade cards each, totaling 104 unique cards with multiple copies. The objective is to arrange each of the ten waste piles in sequence from the King down to the Ace. When a suit is arranged in sequence, it may be removed to a foundation pile. If all suits are moved to the foundations, the game is won.

### SETUP
There are ten waste piles. The leftmost four initially have six cards each, and the remaining six initially have five cards each. The remaining 104 cards are placed in the stock. There are also eight foundation piles. All the interesting action takes place in the waste piles.

**Waste Pile Numbering:** The waste piles are numbered from left to right starting with `0` for the leftmost pile, `1` for the next pile to the right, and so on, up to `9` for the rightmost pile. This numbering is used to reference specific waste piles in questions and game operations.

### GAME BOARD COMPONENTS

#### Stock Pile
The **Stock Pile** is located typically at the top-left corner of the game board. It contains all the remaining cards that are not initially dealt into the waste piles. Players can deal additional cards from the stock to the waste piles by performing a deal operation. Each deal action moves one card face up to each of the ten waste piles, provided that no waste pile is empty. The stock serves as the source of new cards that can be utilized to continue building sequences in the waste piles.

#### Foundation Piles
The **Foundation Piles** are positioned at the top-right corner of the game board. There are eight foundation piles where complete sequences of cards can be moved. Once a sequence of 13 cards from King down to Ace of the same suit is arranged in a waste pile, it can be transferred to a foundation pile. These foundation piles act as the final destination for complete sequences, and moving all cards to the foundations results in winning the game. However, players are not required to move sequences to the foundations immediately, allowing strategic flexibility in organizing other piles.

#### Waste Piles
The **Waste Piles** form the central area of the game board and consist of ten separate piles. These piles are where the primary gameplay occurs. Players can move cards between waste piles to form descending sequences of the same suit or different suits, depending on the game variant. The waste piles are dynamic, allowing for the creation and manipulation of card sequences to unlock more cards and ultimately transfer complete sequences to the foundation piles. Managing the waste piles efficiently is crucial for progressing towards the game's objective.

### MOVING CARDS
Any card may be placed on top of another card that is one higher in rank. For example, a 7 may be moved on top of an 8, or a Queen on top of a King; suits and colors don't matter for this purpose. A run of cards in the same suit in descending sequence is available for play, but you don't have to move all of them. For example, if the top three cards of some pile are the 3, 4, and 5 of Spades, you can move the 3 on top of a 4, the 3 and 4 on top of a 5, or all three on top of a 6. 

- If you have an empty waste pile, you can move any available cards for play onto the empty pile.  

- If a move leaves a face-down card showing on the top of a pile, that card is turned face up.

### COMPLETE SUITS
Once you have arranged a complete suit in order from the King down to the Ace, it can be removed to a foundation pile, but you needn't do so immediately. This allows you to use it to help organize other piles in the waste piles.

### DEALING
When there are no more moves you care to make, you can deal another row. You deal by clicking the stock. This deals one card face up on each of the waste piles. You may not deal if there is an empty waste pile.

### STRATEGY
- Turn as many cards as possible face up.
- Form runs of the same suit in descending order.
- Utilize empty waste piles (spaces) strategically.
- Prioritize moves involving higher-ranked cards to unlock more possibilities.

### VARIANTS 
In circular spider solitaire, a King may be placed on top of an Ace and a run may have a King on top of an Ace, allowing for extended sequences.

## Output Contents

### 1. Image Files
- **Location**: `spider_solitaire_dataset_example/images/`
- **Content**: Generated images representing the current game state, including waste piles, stock pile, and foundation piles.
- **Naming Convention**: Sequentially named as `board_00001.png`, `board_00002.png`, etc.

### 2. State Files
- **Location**: `spider_solitaire_dataset_example/states/`
- **Content**: JSON files saving the current game state, including the rank and suit of the cards in waste piles, stock pile, and foundation piles, as well as the number of cards in each pile.
- **Naming Convention**: Sequentially named as `board_00001.json`, `board_00002.json`, etc.

### 3. VQA Dataset
- **File**: `spider_solitaire_dataset_example/data.json`
- **Content**: JSON array with entries containing:
  - `data_id`
  - `qa_type`
  - `question_id`
  - `question_description`
  - `image`
  - `state`
  - `plot_level`
  - `qa_level`
  - `question`
  - `answer`
  - `analysis`
  - `options` (only for multiple-choice questions)

## Dataset Details

### Difficulty levels
The Spider Solitaire VQA dataset supports three levels of difficulty, each with same 104 cards but different waste counts:
- **Easy**: 8 waste piles.
- **Medium**: 9 waste piles.
- **Hard**: 10 waste piles.

### Supported Question Types
#### Questions about StateInfo Description
1. **How many times can the stockpile still deal cards?**
   - **Type**: Fill in the blank

2. **Which card is on the top of waste pile {num}?**
   - **Type**: Fill in the blank

3. **How many face-down cards are currently in all waste piles?**
   - **Type**: Fill in the blank

4. **If I click the stockpile {num1} to deal cards twice, how many face-up cards will be in waste pile {num2}?**
   - **Type**: Fill in the blank

#### Questions about ActionOutcome Description
1. **What will happen if I want to move the {num1}-th card of pile {num2} to pile {num3}?**
   - **Type**: Multiple choice
   - **Options**
     - A. The move will be successful, and the cards will be in descending order, following the rules of movement.
     - B. The move cannot be made because this card is face-down and its value is unknown.
     - C. The move cannot be made because there is a card above it, and its rank is not smaller by 1.
     - D. The move cannot be made because the top card of the target pile does not have a rank equal to this card’s rank plus one.
     - E. The move cannot be made because the pile has too few cards, and this card does not exist.

#### Question about TransitionPath Description
1. **What should I do if I want to reveal the first face-down card in waste pile {num}?**
   - **Type**: Multiple choice
   - **Options**
     - A. No action is needed; there are no face-down cards in this pile.
     - B. There is no immediate way to reveal it; we should move cards from other piles first and wait for more information.
     - C. We should move the {num1}-th card of pile {num2} to pile {num3}.
     - D. We should move the {num4}-th card of pile {num5} to pile {num6}.
     - E. We should move the {num7}-th card of pile {num8} to pile {num9}.
     - F. We should move the {num10}-th card of pile {num11} to pile {num12}.
     - G. We should move the {num13}-th card of pile {num14} to pile {num15}.
     - H. We should move the {num16}-th card of pile {num17} to pile {num18}.

#### Question About StrategyOptimization Description
1. **Based on the current board state, what is the optimal strategy we should adopt?**
   - **Type**: Multiple choice
   - **Options**
     - A. We should move the {num1}-th card of pile {num2} to pile {num3}.
     - B. We should move the {num4}-th card of pile {num5} to pile {num6}.
     - C. We should move the {num7}-th card of pile {num8} to pile {num9}.
     - D. We should move the {num10}-th card of pile {num11} to pile {num12}.
     - E. We should move the {num13}-th card of pile {num14} to pile {num15}.
     - F. We should move the {num16}-th card of pile {num17} to pile {num18}.
     - G. No cards can be moved; we should click the stockpile to deal cards.
     - H. We should move cards from pile {num19} to the foundation piles.

## How to Use

### 1. Install Dependencies
Before generating the VQA dataset, ensure that all required Python packages are installed. It's recommended to use a virtual environment to manage dependencies.

1. **Set Up a Virtual Environment** *(Optional but recommended)*:
   ```bash
   python -m venv venv
   ```
   - **Activate the Virtual Environment**:
     - **Windows**:
       ```bash
       venv\Scripts\activate
       ```
     - **macOS/Linux**:
       ```bash
       source venv/bin/activate
       ```

2. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Generate the VQA Dataset
```bash
python main.py
```
- **Actions**:
  - Generates game states and corresponding images in the `spider_solitaire_dataset_example/images/` directory.
  - Saves game states as JSON files in the `spider_solitaire_dataset_example/states/` directory.
  - Creates VQA entries and compiles them into `spider_solitaire_dataset_example/data.json`.

### 3. Customize Generation Parameters
You can adjust the dataset generation parameters by modifying the `main.py` script:

- **Number of Samples per Difficulty Level**:
  - Locate the following line in `main.py`:
    ```python
    # Number of samples to generate per plot_level
    num_samples_per_level = 10  # Adjust as needed
    ```

- **Difficulty Levels and Board Sizes**:
  - The script supports three difficulty levels, each with a corresponding number of waste:
    ```python
    # Define plot_levels and corresponding waste pile counts
    plot_levels = [
        {"plot_level": "Easy", "num_waste": 8},
        {"plot_level": "Medium", "num_waste": 9},
        {"plot_level": "Hard", "num_waste": 10}
    ]
    ```

## Acknowledgments

This project utilizes code from the [rdasxy/spider_solitaire](https://github.com/rdasxy/spider_solitaire) GitHub repository. The original implementation provided the foundational mechanics and logic for simulating Spider Solitaire, which were adapted and extended to generate the VQA dataset.

- **Repository**: [rdasxy/spider_solitaire](https://github.com/rdasxy/spider_solitaire)

Special thanks to the contributors of the original repository for their work, which made this project possible.

## License
This project is licensed under the [MIT License](LICENSE).