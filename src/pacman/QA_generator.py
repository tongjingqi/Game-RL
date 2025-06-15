# QA_generator.py

import random
import copy
from typing import Tuple, List, Optional
from game_logic import PacManGame

VALID_QA_TYPES = {"StateInfo", "ActionOutcome", "TransitionPath", "StrategyOptimization"}

directions = ["UP", "DOWN", "RIGHT", "LEFT"]

question_prompt = """
# Game Overview
Pac-Man is a maze arcade game where the player controls Pac-Man to eat as many beans as possible while avoiding ghosts. If a ghost catches Pac-Man, the game ends.

# Basic Elements
- **Pac-Man**: The yellow circular character that the player controls
- **Beans**: Yellow dots that Pac-Man can eat to score points
- **Walls**: Blue barriers that restrict movement
- **Ghosts**: Two ghosts (Pinky and Blinky) that chase Pac-Man

# Game Rules
- Pac-Man must eat beans while avoiding ghosts
- Each bean eaten adds 1 point to the score
- The game ends if a ghost catches Pac-Man
- Movement is restricted by walls

# Movement and Direction
- Pac-Man's mouth opening indicates its current direction
- The direction can be UP, DOWN, LEFT, or RIGHT
- Neither Pac-Man nor ghosts can move through walls

# **Ghost Behavior**
- **Pinky** (Pink Ghost): Targets up to 4 spaces ahead of Pac-Man's current position and direction (stops at walls)
- **Blinky** (Red Ghost): Directly targets Pac-Man's current position
- Both ghosts follow a movement priority system based on the direction they are trying to move:
  - When moving in more than one direction is optimal, the priority order for both ghosts is **UP > DOWN > LEFT > RIGHT**.
  - This means if a ghost has multiple possible directions to move in, it will first attempt to move **UP** if possible, then **DOWN**, followed by **LEFT**, and finally **RIGHT** if all other directions are blocked.

# Board Layout
- The board is surrounded by walls on all four sides
- Position (0,0) is located at the top-left corner wall
- Movement grid uses (row, column) coordinates

# Scoring
The score equals the total number of beans eaten by Pac-Man
"""

def handle_state_info_q0(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q0: What is Pac-Man's position and direction?
    """
    question = question_prompt + "\n\n**Question:** What is Pac-Man's position and direction?"
    x_real = game.pacman_position[0]
    y_real = game.pacman_position[1]
    dir_real = game.direction

    options = []
    coordinate_list = [(x_real, y_real, dir_real)]
    correct_option = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    correct_index = ord(correct_option) - ord('A')

    for _ in range(8):
        while True:
            random_x = random.randint(0, game.grid_size - 1)
            random_y = random.randint(0, game.grid_size - 1)
            random_dir = random.choice(directions)
            if (random_x, random_y, random_dir) != (x_real, y_real, dir_real) and (random_x, random_y, random_dir) not in coordinate_list:
                coordinate_list.append((random_x, random_y, random_dir))
                break
    
    for i in range(8):
        if i == correct_index:
            (x, y, dir) = coordinate_list[0]
        else:
            if i > correct_index:
                (x, y, dir) = coordinate_list[i]
            else:
                (x, y, dir) = coordinate_list[i+1]
        options.append(f"{chr(65+i)}. ({x}, {y}), {dir}")

    answer = correct_option
    question += "\n\n**Options:**\n" + "\n".join(options)
    analysis = (f"First, we locate the yellow pacman on the board."
                f"Then we determine its row is {game.pacman_position[0]} and column is {game.pacman_position[1]} according to the scale around the board.\n"
                f"Second, we know from the orientation of the pacman opening that its direction is {game.direction}")
    return question, answer, analysis, options

def handle_state_info_q1(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q1: Count visible beans in 5x5 grid centered on Pac-Man
    
    Returns:
        Tuple containing question, answer, analysis, and None for optional choices
    """
    pacman_row, pacman_col = game.pacman_position
    bean_count = 0

    ghost_positions = [ghost.position for ghost in game.ghosts]
    
    # Check 5x5 grid around Pac-Man
    for row in range(pacman_row - 2, pacman_row + 3):
        for col in range(pacman_col - 2, pacman_col + 3):
            # Validate position is within game bounds and is a bean
            if (0 <= row < game.grid_size and 
                0 <= col < game.grid_size and 
                (row, col) in game.beans and
                (row, col) not in ghost_positions):
                bean_count += 1

    question = question_prompt + "\n\n**Question:** Now how many beans are visible there in the 5 by 5 grid around the Pac-man center?"
    answer = str(bean_count)
    analysis = (f"Beans are yellow dots on a board\n"
                f"First, we identify the 5x5 grid centered at Pac-Man's position ({pacman_row}, {pacman_col}).\n"
                f"Then, we count yellow beans within this grid while ensuring we stay within game boundaries.\n"
                f"The total number of beans in this area is: {bean_count}")
    
    return question, answer, analysis, None

def handle_state_info_q2(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q2: Which ghost is closer to Pac-Man, Pinky or Blinky?
    """
    # Find distances using Manhattan distance
    pinky = None
    blinky = None
    for ghost in game.ghosts:
        if ghost.name == 'Pinky':
            pinky = ghost
        elif ghost.name == 'Blinky':
            blinky = ghost
    
    pinky_distance = abs(pinky.position[0] - game.pacman_position[0]) + \
                    abs(pinky.position[1] - game.pacman_position[1])
    blinky_distance = abs(blinky.position[0] - game.pacman_position[0]) + \
                     abs(blinky.position[1] - game.pacman_position[1])

    # Create options
    options = [
        "A. Pinky is closer to Pac-Man",
        "B. Blinky is closer to Pac-Man",
        "C. Both ghosts are equidistant from Pac-Man"
    ]

    # Determine answer and analysis
    if pinky_distance < blinky_distance:
        answer = options[0]
        comparison = "less than"
    elif blinky_distance < pinky_distance:
        answer = options[1]
        comparison = "greater than"
    else:
        answer = options[2]
        comparison = "equal to"

    question = question_prompt + "\n\n**Question:** Which ghost is closer to Pac-Man, Pinky or Blinky?" + "\n\n**Options:**\n" + "\n".join(options)
    
    analysis = (f"To determine which ghost is closer, we calculate Manhattan distance for each ghost.\n"
               f"Manhattan distance for Pinky is:\n"
               f"   |{pinky.position[0]} - {game.pacman_position[0]}| + |{pinky.position[1]} - {game.pacman_position[1]}| = {pinky_distance}\n"
               f"Manhattan distance for Blinky is:\n"
               f"   |{blinky.position[0]} - {game.pacman_position[0]}| + |{blinky.position[1]} - {game.pacman_position[1]}| = {blinky_distance}\n"
               f"By comparing the distance, we find that Pinky's distance ({pinky_distance}) is {comparison} Blinky's distance ({blinky_distance})")

    return question, answer, analysis, options

def handle_action_outcome_q3(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q3: How many beans can Pac-Man eat if it moves in its current direction until hitting a wall?
    """
    # Count beans in current direction until wall
    row, col = game.pacman_position
    bean_count = 0
    while True:
        if game.direction == 'UP':
            row -= 1
        elif game.direction == 'DOWN':
            row += 1
        elif game.direction == 'LEFT':
            col -= 1
        elif game.direction == 'RIGHT':
            col += 1
        
        # Check if hit wall or out of bounds
        if (row, col) in game.walls or not (0 <= row < game.grid_size and 0 <= col < game.grid_size):
            break
        if (row, col) in game.beans:
            bean_count += 1

    question = question_prompt + "\n\n**Question:** Assuming the ghosts don't move, how many beans can Pac-Man eat if it moves in its current direction until hitting a wall?"
    answer = str(bean_count)
    analysis = (f"To count beans in Pac-Man's path, \n"
               f"we first find the starting position of the pacman. And it is ({game.pacman_position[0]}, {game.pacman_position[1]}).\n"
               f"Then we counted all beans in the path moving in direction {game.direction} until hitting wall or boundary.\n"
               f"So there are {bean_count} beans in total.")
    return question, answer, analysis, None

def handle_action_outcome_q4(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q4: What would happen if Pac-Man moves in specified directions?
    """

    direction1 = random.choice(directions)
    direction2 = random.choice(directions)
    num1 = random.randint(1, 3)
    num2 = random.randint(1, 3)

    test_game = copy.deepcopy(game)
    initial_score = test_game.score
    
    question = question_prompt + f"\n\n**Question:** Assuming Pac-Man and both ghosts move one step at a time, what would happen if Pac-Man moves {direction1} {num1} times, then {direction2} {num2} times?"

    # Initialize path tracking for first sequence
    ghost_paths_first = {ghost.name: [(ghost.position, 'initial')] for ghost in test_game.ghosts}
    pacman_path_first = [(test_game.pacman_position, 'initial')]

    # First movement sequence
    for i in range(num1):
        old_position = test_game.pacman_position
        test_game.move_pacman(direction1)
        pacman_path_first.append((test_game.pacman_position, f"step {i+1}"))
        
        """ if test_game.pacman_position == old_position:
            break """

        for ghost in test_game.ghosts:
            old_ghost_pos = ghost.position
            # Update ghost's target location
            ghost.update_direction()
            # Move if there is a viable path
            if ghost.path and len(ghost.path) >= 2:
                ghost.move()
            ghost_paths_first[ghost.name].append((ghost.position, f"step {i+1}"))
        


            if ghost.position == test_game.pacman_position:

                beans_list = []
                for _ in range(6):
                    while True:
                        random_beans = random.randint(1, test_game.score - initial_score + 10)
                        if random_beans not in beans_list:
                            beans_list.append(random_beans)
                            break

                options = [
                    f"A. It will eat {beans_list[0]} beans, and the score will become {initial_score + beans_list[0]}",
                    f"B. It will eat {beans_list[1]} beans, and the score will become {initial_score + beans_list[1]}",
                    f"C. It will eat {beans_list[2]} beans, and the score will become {initial_score + beans_list[2]}",
                    f"D. It will eat {beans_list[3]} beans, and the score will become {initial_score + beans_list[3]}",
                    f"E. It will eat {beans_list[4]} beans, and the score will become {initial_score + beans_list[4]}",
                    f"F. It will eat {beans_list[5]} beans, and the score will become {initial_score + beans_list[5]}",
                    "G. It will be caught by Pinky (the pink ghost)",
                    "H. It will be caught by Blinky (the red ghost)"
                ]

                question += "\n\n**Options:**\n" + "\n".join(options)
                
                if ghost.name == 'Pinky':
                    answer = "G"
                    analysis = (f"Let's analyze Pac-Man's movement step by step:\n\n"
                                f"1. Initial state:\n"
                                f"   - Pac-Man's starting position: {game.pacman_position}\n"
                                f"   - Pinky's starting position: {ghost_paths_first['Pinky'][0][0]}\n"
                                f"   - Blinky's starting position: {ghost_paths_first['Blinky'][0][0]}\n\n"
                                f"2. Movement paths analysis:\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_first:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Pinky's path:\n"
                    for pos, step in ghost_paths_first['Pinky']:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Blinky's path:\n"
                    for pos, step in ghost_paths_first['Blinky']:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += (f"\n3. Movement analysis:\n"
                                f"   - Pac-Man attempts to move {direction1} {num1} times\n"
                                f"   - During the {i+1}th move in direction {direction1}, Pinky catches Pac-Man\n"
                                f"   - Collision occurs at position {ghost.position}\n\n"
                                f"Therefore, Pac-Man is caught by Pinky before completing its planned movement.")
                else:
                    answer = "H"
                    analysis = (f"Let's analyze Pac-Man's movement step by step:\n\n"
                                f"1. Initial state:\n"
                                f"   - Pac-Man's starting position: {game.pacman_position}\n"
                                f"   - Blinky's starting position: {ghost_paths_first['Blinky'][0][0]}\n"
                                f"   - Pinky's starting position: {ghost_paths_first['Pinky'][0][0]}\n\n"
                                f"2. Movement paths analysis:\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_first:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Blinky's path:\n"
                    for pos, step in ghost_paths_first['Blinky']:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Pinky's path:\n"
                    for pos, step in ghost_paths_first['Pinky']:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += (f"\n3. Movement analysis:\n"
                                f"   - Pac-Man attempts to move {direction1} {num1} times\n"
                                f"   - During the {i+1}th move in direction {direction1}, Blinky catches Pac-Man\n"
                                f"   - Collision occurs at position {ghost.position}\n\n"
                                f"Therefore, Pac-Man is caught by Blinky before completing its planned movement.")
                

                return question, answer, analysis, options


    # Initialize path tracking for second sequence
    ghost_paths_second = {ghost.name: [(ghost.position, 'start_second_sequence')] for ghost in test_game.ghosts}
    pacman_path_second = [(test_game.pacman_position, 'start_second_sequence')]


    # Second movement sequence
    for i in range(num2):
        old_position = test_game.pacman_position
        test_game.move_pacman(direction2)
        pacman_path_second.append((test_game.pacman_position, f"step {i+1}"))

        """ if test_game.pacman_position == old_position:
            break """
             
        for ghost in test_game.ghosts:
            old_ghost_pos = ghost.position
            # Update ghost's target location
            ghost.update_direction()
            # Move if there is a viable path
            if ghost.path and len(ghost.path) >= 2:
                ghost.move()
            ghost_paths_second[ghost.name].append((ghost.position, f"step {i+1}"))



            if ghost.position == test_game.pacman_position:

                beans_eaten = test_game.score - initial_score
                
                beans_list = []
                for _ in range(6):
                    while True:
                        random_beans = random.randint(1, beans_eaten + 10)
                        if random_beans not in beans_list:
                            beans_list.append(random_beans)
                            break

                options = [
                    f"A. It will eat {beans_list[0]} beans, and the score will become {initial_score + beans_list[0]}",
                    f"B. It will eat {beans_list[1]} beans, and the score will become {initial_score + beans_list[1]}",
                    f"C. It will eat {beans_list[2]} beans, and the score will become {initial_score + beans_list[2]}",
                    f"D. It will eat {beans_list[3]} beans, and the score will become {initial_score + beans_list[3]}",
                    f"E. It will eat {beans_list[4]} beans, and the score will become {initial_score + beans_list[4]}",
                    f"F. It will eat {beans_list[5]} beans, and the score will become {initial_score + beans_list[5]}",
                    "G. It will be caught by Pinky (the pink ghost)",
                    "H. It will be caught by Blinky (the red ghost)"
                ]

                question += "\n\n**Options:**\n" + "\n".join(options)

                if ghost.name == 'Pinky':
                    answer = "G"
                    analysis = (f"Let's analyze Pac-Man's movement step by step:\n\n"
                                f"1. First movement sequence:\n"
                                f"   - Successfully moves {direction1} {num1} times\n"
                                f"   - Eats {beans_eaten} beans during this phase\n"
                                f"   Paths during first sequence:\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_first:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Ghost paths:\n"
                    for pos, step in ghost_paths_first['Pinky']:
                        analysis += f"   Pinky {step}: {pos}\n"
                    for pos, step in ghost_paths_first['Blinky']:
                        analysis += f"   Blinky {step}: {pos}\n"
                    
                    analysis += (f"\n2. Second movement sequence:\n"
                                f"   - Attempts to move {direction2} {num2} times\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_second:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Ghost paths:\n"
                    for pos, step in ghost_paths_second['Pinky']:
                        analysis += f"   Pinky {step}: {pos}\n"
                    for pos, step in ghost_paths_second['Blinky']:
                        analysis += f"   Blinky {step}: {pos}\n"
                    
                    analysis += (f"\n3. Final outcome:\n"
                                f"   - During the {i+1}th move, Pinky catches Pac-Man\n"
                                f"   - Collision occurs at position {ghost.position}\n\n"
                                f"Therefore, Pac-Man is caught by Pinky before completing its planned movement.")
                else:
                    answer = "H"
                    analysis = (f"Let's analyze Pac-Man's movement step by step:\n\n"
                                f"1. First movement sequence:\n"
                                f"   - Successfully moves {direction1} {num1} times\n"
                                f"   - Eats {beans_eaten} beans during this phase\n"
                                f"   Paths during first sequence:\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_first:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Ghost paths:\n"
                    for pos, step in ghost_paths_first['Blinky']:
                        analysis += f"   Blinky {step}: {pos}\n"
                    for pos, step in ghost_paths_first['Pinky']:
                        analysis += f"   Pinky {step}: {pos}\n"
                    
                    analysis += (f"\n2. Second movement sequence:\n"
                                f"   - Attempts to move {direction2} {num2} times\n"
                                f"   Pac-Man's path:\n")
                    for pos, step in pacman_path_second:
                        analysis += f"   - {step}: {pos}\n"
                    analysis += f"\n   Ghost paths:\n"
                    for pos, step in ghost_paths_second['Blinky']:
                        analysis += f"   Blinky {step}: {pos}\n"
                    for pos, step in ghost_paths_second['Pinky']:
                        analysis += f"   Pinky {step}: {pos}\n"
                    
                    analysis += (f"\n3. Final outcome:\n"
                                f"   - During the {i+1}th move, Blinky catches Pac-Man\n"
                                f"   - Collision occurs at position {ghost.position}\n\n"
                                f"Therefore, Pac-Man is caught by Blinky before completing its planned movement.")
                return question, answer, analysis, options
    
    final_score = test_game.score
    beans_eaten = final_score - initial_score

    options = []
    correct_option = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    correct_index = ord(correct_option) - ord('A')

    beans_list = [beans_eaten]
    for _ in range(5):
        while True:
            random_beans = random.randint(1, beans_eaten + 5)
            if random_beans != beans_eaten and random_beans not in beans_list:
                beans_list.append(random_beans)
                break

    random.shuffle(beans_list[1:])

    for i in range(6):
        if i == correct_index:
            bean_count = beans_eaten
        elif i > correct_index:
            bean_count = beans_list[i]
        elif i < correct_index:
            bean_count = beans_list[i + 1]
        options.append(f"{chr(65+i)}. It will eat {bean_count} beans, and the score will become {initial_score + bean_count}")

    options.extend([
        "G. It will be caught by Pinky (the pink ghost)",
        "H. It will be caught by Blinky (the red ghost)"
    ])

    answer = correct_option
    question += "\n\n**Options:**\n" + "\n".join(options)

    analysis = (f"Let's analyze Pac-Man's movement step by step:\n\n"
                f"1. Initial state:\n"
                f"   - Starting position: {game.pacman_position}\n"
                f"   - Initial score: {initial_score}\n\n"
                f"2. First movement sequence:\n"
                f"   - Successfully moves {direction1} {num1} times\n"
                f"   - No collision with ghosts during this phase\n"
                f"   Paths during first sequence:\n"
                f"   Pac-Man's path:\n")
    
    for pos, step in pacman_path_first:
        analysis += f"   - {step}: {pos}\n"
    
    analysis += f"\n   Ghost paths:\n"    
    for pos, step in ghost_paths_first['Pinky']:
        analysis += f"   Pinky {step}: {pos}\n"
    for pos, step in ghost_paths_first['Blinky']:
        analysis += f"   Blinky {step}: {pos}\n"
        
    analysis += (f"\n3. Second movement sequence:\n"
                f"   - Successfully moves {direction2} {num2} times\n"
                f"   - No collision with ghosts during this phase\n"
                f"   Paths during second sequence:\n"
                f"   Pac-Man's path:\n")
    
    for pos, step in pacman_path_second:
        analysis += f"   - {step}: {pos}\n"
        
    analysis += f"\n   Ghost paths:\n"
    for pos, step in ghost_paths_second['Pinky']:
        analysis += f"   Pinky {step}: {pos}\n"
    for pos, step in ghost_paths_second['Blinky']:
        analysis += f"   Blinky {step}: {pos}\n"
        
    analysis += (f"\n4. Final results:\n"
                f"   - Total beans eaten: {beans_eaten}\n"
                f"   - Final score: {final_score}\n\n"
                f"Therefore, Pac-Man successfully completes its movement, eating {beans_eaten} beans and reaching a score of {final_score}.")
    return question, answer, analysis, options

def handle_action_outcome_q5(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q5: Will Pinky's next movement direction change after Pac-Man moves?
    """
    # Generate random movement
    direction0 = random.choice(directions)
    num1 = random.randint(1, 3)
    
    # Get Pinky's current target and path
    pinky = None
    for ghost in game.ghosts:
        if ghost.name == 'Pinky':
            pinky = ghost
            break
            
    test_game = copy.deepcopy(game)
    
    # Get current Pinky's path
    original_target = test_game.get_pinky_target()
    original_path = test_game.bfs(pinky.position, original_target)
    if len(original_path) >= 2:
        original_direction = test_game.get_direction_between(original_path[0], original_path[1])
    else:
        original_direction = test_game.direction  # Default if no path
    
    # Move Pac-Man
    for _ in range(num1):
        old_position = test_game.pacman_position
        test_game.move_pacman(direction0)
        if test_game.pacman_position == old_position:  # Hit wall
            break
    
    # Get new Pinky's target and path
    new_target = test_game.get_pinky_target()
    new_path = test_game.bfs(pinky.position, new_target)
    
    # Get new direction if path exists
    if len(new_path) >= 2:
        new_direction = test_game.get_direction_between(new_path[0], new_path[1])
    else:
        new_direction = test_game.direction  # Default if no path

    # Generate all possible directions excluding original direction
    other_directions = [d for d in directions if d != original_direction]
    random.shuffle(other_directions)

    options = [
        f"A. Pinky's direction remains unchanged, still {original_direction}",
        f"B. Pinky's direction changes to {other_directions[0]}",
        f"C. Pinky's direction changes to {other_directions[1]}",
        f"D. Pinky's direction changes to {other_directions[2]}"
    ]

    question = question_prompt + f"\n\n**Question:** Assuming Pinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Pinky's next movement direction change?" + "\n\n**Options:**\n" + "\n".join(options)

    if new_direction == original_direction:
        answer = "A"
        change_str = "remains unchanged"
    else:
        answer = next(i for i, opt in enumerate(options) if new_direction in opt)
        answer = chr(ord('A') + answer)  # Convert to letter
        change_str = f"changes to {new_direction}"
    
    analysis = (f"To determine Pinky's direction change, we should find Pinky's state before and after Pac-Man's movement:\n"
               f"We find that original Pinky position is {pinky.position}\n"
               f"And Pinky's original target (4 spaces ahead) is {original_target}\n"
               f"Specifically, Pinky's Original movement direction is {original_direction}\n"
               f"After Pac-Man moves {direction0} {num1} times, the new Pac-Man position is {test_game.pacman_position}\n"
               f"So the new target position for Pinky is {new_target}\n"
               f"And Pinky's new movement direction is {new_direction}\n"
               f"Therefore, Pinky's direction {change_str}")
               
    return question, answer, analysis, options

def handle_action_outcome_q6(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q6: Will Blinky's next movement direction change after Pac-Man moves?
    """
    # Generate random movement
    direction0 = random.choice(directions)
    num1 = random.randint(1, 3)
    
    # Get Blinky
    blinky = None
    for ghost in game.ghosts:
        if ghost.name == 'Blinky':
            blinky = ghost
            break
            
    test_game = copy.deepcopy(game)
    
    # Get current Blinky's path (directly to Pac-Man)
    original_path = test_game.bfs(blinky.position, test_game.pacman_position)
    if len(original_path) >= 2:
        original_direction = test_game.get_direction_between(original_path[0], original_path[1])
    else:
        original_direction = test_game.direction  # Default if no path
    
    # Move Pac-Man
    for _ in range(num1):
        old_position = test_game.pacman_position
        test_game.move_pacman(direction0)
        if test_game.pacman_position == old_position:  # Hit wall
            break
    
    # Get new path
    new_path = test_game.bfs(blinky.position, test_game.pacman_position)
    
    # Get new direction if path exists
    if len(new_path) >= 2:
        new_direction = test_game.get_direction_between(new_path[0], new_path[1])
    else:
        new_direction = test_game.direction  # Default if no path

    # Generate all possible directions excluding original direction
    other_directions = [d for d in directions if d != original_direction]
    random.shuffle(other_directions)
    
    options = [
        f"A. Blinky's direction remains unchanged, still {original_direction}",
        f"B. Blinky's direction changes to {other_directions[0]}",
        f"C. Blinky's direction changes to {other_directions[1]}",
        f"D. Blinky's direction changes to {other_directions[2]}"
    ]

    question = question_prompt + f"\n\n**Question:** Assuming Blinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Blinky's next movement direction change?" + "\n\n**Options:**\n" + "\n".join(options)

    if new_direction == original_direction:
        answer = "A"
        change_str = "remains unchanged"
    else:
        answer = next(i for i, opt in enumerate(options) if new_direction in opt)
        answer = chr(ord('A') + answer)  # Convert to letter
        change_str = f"changes to {new_direction}"
    
    analysis = (f"To determine Blinky's direction change, we should find Blinky's state before and after Pac-Man's movement:\n"
               f"We find that original Blinky position is {blinky.position}\n"
               f"And Blinky's original target (Pac-Man's position) is {game.pacman_position}\n"
               f"Specifically, Blinky's original movement direction is {original_direction}\n"
               f"After Pac-Man moves {direction0} {num1} times,  the new Pac-Man position is {test_game.pacman_position}. So the new target position for Blinky is {test_game.pacman_position}.\n"
               f"And Blinky's new movement direction is {new_direction}\n"
               f"Therefore, Blinky's direction {change_str}")
               
    return question, answer, analysis, options

def handle_transition_path_q7(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q7: Where will Pinky move in the next turn if Pac-Man stays still?
    """
    # Get Pinky and its current path
    pinky = None
    for ghost in game.ghosts:
        if ghost.name == 'Pinky':
            pinky = ghost
            break
    
    # Get Pinky's target and path
    target = game.get_pinky_target()
    path = game.bfs(pinky.position, target)
    
    # Get the direction of next move if path exists
    if len(path) >= 2:
        next_position = path[1]
        actual_direction = game.get_direction_between(pinky.position, next_position)
    else:
        actual_direction = game.direction  # Default if no path
    
    # Prepare options
    options = [
        "A. Pinky will move one step UP",
        "B. Pinky will move one step DOWN",
        "C. Pinky will move one step RIGHT",
        "D. Pinky will move one step LEFT"
    ]
    
    question = question_prompt + "\n\n**Question:** If Pac-Man stays still, where will Pinky move in the next turn?" + "\n\n**Options:**\n" + "\n".join(options)
    # Determine answer based on actual direction
    direction_to_answer = {
        'UP': 'A',
        'DOWN': 'B',
        'RIGHT': 'C',
        'LEFT': 'D'
    }
    answer = direction_to_answer[actual_direction]
    
    analysis = (f"To determine Pinky's next move, we need to find the current target of Pinky.\n"
               f"Firstly, current Pinky position is {pinky.position}\n"
               f"Currrent Pac-Man's position is {game.pacman_position}\n"
               f"And Pac-Man's direction is {game.direction}\n"
               f"So Pinky's target (4 spaces ahead) is {target}\n"
               f"Secondly, we calculate the shortest path using BFS: {path}\n"
               f"So the next position in path is {path[1] if len(path) >= 2 else 'No valid next position'}\n"
               f"Therefore, Pinky will move {actual_direction}")
    
    return question, answer, analysis, options

def handle_transition_path_q8(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q8: Where will Blinky move in the next turn if Pac-Man stays still?
    """
    # Get Blinky and its current path
    blinky = None
    for ghost in game.ghosts:
        if ghost.name == 'Blinky':
            blinky = ghost
            break
    
    # Get Blinky's path (directly to Pac-Man)
    path = game.bfs(blinky.position, game.pacman_position)
    
    # Get the direction of next move if path exists
    if len(path) >= 2:
        next_position = path[1]
        actual_direction = game.get_direction_between(blinky.position, next_position)
    else:
        actual_direction = game.direction  # Default if no path
        
    # Generate other random directions
    other_directions = [d for d in directions if d != actual_direction]
    random.shuffle(other_directions)
    
    # Prepare options
    options = [
        "A. Blinky will move one step UP",
        "B. Blinky will move one step DOWN",
        "C. Blinky will move one step RIGHT",
        "D. Blinky will move one step LEFT"
    ]
    
    question = question_prompt + "\n\n**Question:** If Pac-Man stays still, where will Blinky move in the next turn?" + "\n\n**Options:**\n" + "\n".join(options)
    # Determine answer based on actual direction
    direction_to_answer = {
        'UP': 'A',
        'DOWN': 'B',
        'RIGHT': 'C',
        'LEFT': 'D'
    }
    answer = direction_to_answer[actual_direction]
    
    analysis = (f"To determine Blinky's next move, we need to find the current target of Blinky.\n"
               f"Firstly, current Blinky position is {blinky.position}\n"
               f"And Blinky's target (Pac-Man's position) is {game.pacman_position}\n"
               f"Secondly, we calculate the shortest path using BFS: {path}\n"
               f"So the next position in path is {path[1] if len(path) >= 2 else 'No valid next position'}\n"
               f"Therefore, Blinky will move {actual_direction}")
    
    return question, answer, analysis, options

def handle_strategy_optimization_q9(game: PacManGame) -> Tuple[str, str, str, Optional[List[str]]]:
    """
    Generates Q9: Which direction should Pac-Man move to eat the most beans without being caught?
    """
    results = {}
    best_direction = None
    max_beans = -1
    will_be_caught = True
    
    for test_direction in directions:
        test_game = copy.deepcopy(game)
        initial_score = test_game.score
        beans_eaten = 0
        caught = False
        final_pacman_pos = None
        final_ghost_positions = {}
        
        # Initialize path tracking
        pacman_path = [(test_game.pacman_position, 'initial')]
        ghost_paths = {ghost.name: [(ghost.position, 'initial')] for ghost in test_game.ghosts}
        
        step_count = 0
        while True:
            old_position = test_game.pacman_position
            test_game.move_pacman(test_direction)
            step_count += 1
            pacman_path.append((test_game.pacman_position, f'step {step_count}'))
            
            if test_game.pacman_position == old_position:
                final_pacman_pos = test_game.pacman_position
                final_ghost_positions = {ghost.name: ghost.position for ghost in test_game.ghosts}
                break
            
            for ghost in test_game.ghosts:
                ghost.update_direction()
                if ghost.path and len(ghost.path) >= 2:
                    ghost.move()
                ghost_paths[ghost.name].append((ghost.position, f'step {step_count}'))
                
                if ghost.position == test_game.pacman_position:
                    caught = True
                    final_pacman_pos = test_game.pacman_position
                    final_ghost_positions = {ghost.name: ghost.position for ghost in test_game.ghosts}
                    break
            
            if caught:
                break
        
        beans_eaten = test_game.score - initial_score
        results[test_direction] = (beans_eaten, caught, final_pacman_pos, final_ghost_positions, pacman_path, ghost_paths)
        
        if not caught and beans_eaten > max_beans:
            max_beans = beans_eaten
            best_direction = test_direction
            will_be_caught = False
    
    # Rest of the options setup remains the same...
    options = [
        "A. Pac-Man should move UP",
        "B. Pac-Man should move DOWN",
        "C. Pac-Man should move RIGHT",
        "D. Pac-Man should move LEFT",
        "E. Pac-Man will be caught by a ghost regardless of direction"
    ]
    
    question = question_prompt + "\n\n**Question:** If Pac-Man and both ghosts move one step at a time, in which direction should Pac-Man move continuously until hitting a wall to eat the most beans without being caught by a ghost? (When moving in more than one direction is optimal, the priority order is UP > DOWN > LEFT > RIGHT)" + "\n\n**Options:**\n" + "\n".join(options)
    
    if will_be_caught:
        answer = "E"
        analysis_text = "All directions lead to being caught by ghosts"
    else:
        direction_to_letter = {'UP': 'A', 'DOWN': 'B', 'RIGHT': 'C', 'LEFT': 'D'}
        answer = direction_to_letter[best_direction]
        analysis_text = f"Moving {best_direction} is optimal with {max_beans} beans collected without being caught"

    analysis = "Analysis of each direction:\n"
    for direction in directions:
        beans, caught, final_pos, ghost_pos, pac_path, ghost_paths = results[direction]
        analysis += f"\n{direction}:\n"
        analysis += f"- Beans that can be eaten: {beans}\n"
        analysis += f"- Will be caught by ghost: {caught}\n"
        analysis += f"- Movement paths:\n"
        
        # Add Pac-Man's path
        analysis += "  Pac-Man's path:\n"
        for pos, step in pac_path:
            analysis += f"    {step}: {pos}\n"
        
        # Add ghosts' paths
        for ghost_name, path in ghost_paths.items():
            analysis += f"  {ghost_name}'s path:\n"
            for pos, step in path:
                analysis += f"    {step}: {pos}\n"
        
        analysis += "\n"

    analysis += f"\nConclusion: {analysis_text}"
    
    return question, answer, analysis, options

def generate_pacman_QA(game: PacManGame, num: int, size: int) -> Tuple[str, str, str, int, str, str, Optional[List[str]]]:
    """
    Generates a question and answer pair for Pacman.

    Parameters:
    - game: PacManGame object representing the current game state.
    - num: Integer used to select the question type.
    - size: The grid size of the chessboard.

    Returns:
    - qa_type: Type of the question.
    - qa_level: Difficulty level of the question.
    - question: The question text (including question_prompt).
    - question_id: The type number of the question.
    - answer: The correct answer.
    - analysis: Detailed explanation of the answer.
    - options: List of options if it's a multiple-choice question, else None.
    """
    
    # Define question types with VALID_QA_TYPES
    question_types = [
        # 0: StateInfo
        {"qa_type": "StateInfo", "template": "What is Pac-Man's position and direction?", "difficulty": "Easy", "is_mcq": False, "description": "Identify Pacman location"},
        
        # 1: StateInfo
        {"qa_type": "StateInfo", "template": "Now how many beans are visible there in the 5 by 5 grid around the Pac-man center?", "difficulty": "Easy", "is_mcq": False, "description": "Count Pacman's surrounding beans"},
        
        # 2: StateInfo - Multiple choice
        {"qa_type": "StateInfo", "template": "Which ghost is closer to Pac-Man, Pinky or Blinky?", "difficulty": "Easy", "is_mcq": True, "description": "Identify the closest ghost"},

        # 3: ActionOutcome
        {"qa_type": "ActionOutcome", "template": "Assuming the ghosts don't move, how many beans can Pac-Man eat if it moves in its current direction until hitting a wall?", "difficulty": "Easy", "is_mcq": False, "description": "Count beans in Pacman's path"},
        
        # 4: ActionOutcome - Multiple choice
        {"qa_type": "ActionOutcome", "template": "Assuming Pac-Man and both ghosts move one step at a time, what would happen if Pac-Man moves {direction1} {num1} times, then {direction2} {num2} times?", "difficulty": "Hard", "is_mcq": True, "description": "Predict Pacman's movement result"},

        # 5: ActionOutcome - Multiple choice
        {"qa_type": "ActionOutcome", "template": "Assuming Pinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Pinky's next movement direction change?", "difficulty": "Medium", "is_mcq": True, "description": "Predict change in Pinky's movement"},

        # 6: ActionOutcome - Multiple choice
        {"qa_type": "ActionOutcome", "template": "Assuming Blinky doesn't move, if Pac-Man moves {direction0} {num1} times, will Blinky's next movement direction change?", "difficulty": "Medium", "is_mcq": True, "description": "Predict change in Blinky's movement"},

        # 7: TransitionPath - Multiple choice
        {"qa_type": "TransitionPath", "template": "If Pac-Man stays still, where will Pinky move in the next turn?", "difficulty": "Medium", "is_mcq": True, "description": "Infer Pinky's next move"},
        
        # 8: TransitionPath - Multiple choice
        {"qa_type": "TransitionPath", "template": "If Pac-Man stays still, where will Blinky move in the next turn?", "difficulty": "Medium", "is_mcq": True, "description": "Infer Blinky's next move"},

        # 9: StrategyOptimization - Multiple choice
        {"qa_type": "StrategyOptimization", "template": "If Pac-Man and both ghosts move one step at a time, in which direction should Pac-Man move continuously until hitting a wall to eat the most beans without being caught by a ghost? (When moving in more than one direction is optimal, the priority order is UP > DOWN > LEFT > RIGHT)", "difficulty": "Hard", "is_mcq": True, "description": "Judge Pacman's optimal movement"},
        
    ]
        
    # Initialize variable
    question = ""
    answer = ""
    analysis = ""
    options = None

    # Select question based on num
    num = num % 10  # Ensure num is within 0-9
    question_id = 0
    if num == 0:
        question_choice = question_types[0]  # Question 0
        question_id = 0
        question, answer, analysis, options = handle_state_info_q0(game)
    elif num == 1:
        question_choice = question_types[1]  # Question 1
        question_id = 1
        question, answer, analysis, options = handle_state_info_q1(game)
    elif num == 2:
        question_choice = question_types[2]  # Question 2
        question_id = 2
        question, answer, analysis, options = handle_state_info_q2(game)
    elif num == 3:
        question_choice = question_types[3]  # Question 3
        question_id = 3
        question, answer, analysis, options = handle_action_outcome_q3(game)
    elif num == 4:
        question_choice = question_types[4]  # Question 4
        question_id = 4
        question, answer, analysis, options = handle_action_outcome_q4(game)
    elif num == 5:
        question_choice = question_types[5]  # Question 5
        question_id = 5
        question, answer, analysis, options = handle_action_outcome_q5(game)
    elif num == 6:
        question_choice = question_types[6]  # Question 6
        question_id = 6
        question, answer, analysis, options = handle_action_outcome_q6(game)
    elif num == 7:
        question_choice = question_types[7]  # Question 7
        question_id = 7
        question, answer, analysis, options = handle_transition_path_q7(game)
    elif num == 8:
        question_choice = question_types[8]  # Question 8
        question_id = 8
        question, answer, analysis, options = handle_transition_path_q8(game)
    elif num == 9:
        question_choice = question_types[9]  # Question 9
        question_id = 9
        question, answer, analysis, options = handle_strategy_optimization_q9(game)

    qa_type = question_choice["qa_type"]
    question_template = question_choice["template"]
    qa_level = question_choice["difficulty"]  # 'Easy', 'Medium', 'Hard'
    is_mcq = question_choice["is_mcq"]
    question_description = question_choice["description"]
    
    return qa_type, qa_level, question, question_id, question_description, answer, analysis, options
