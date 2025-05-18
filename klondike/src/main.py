import pygame
import os
import datetime
import json
import random
from board import Board
from input import InputManager
from generate import KlondikeQAGenerator
from tqdm import tqdm
from pygame import transform

class Game:
    def __init__(self, w, h, total_datasets=100) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (w, h), 
            flags=pygame.SCALED,
            vsync=1
        )

        icon = pygame.image.load("assets/big_spade.png")
        pygame.display.set_caption("klondike")
        pygame.display.set_icon(icon)

        bg_img = pygame.image.load("assets/klondike_bg.png").convert_alpha()
        self.bg = transform.scale_by(bg_img, 2)
    
        self.clock = pygame.time.Clock()
        self.bg_color = (30, 100, 90, 255)

        self.board = Board()
        InputManager.init()

        self.total_datasets = total_datasets
        self.current_dataset = 1

        # Create dataset directory structure
        self.main_dataset_dir = "klondike_dataset"
        self.images_dir = os.path.join(self.main_dataset_dir, "images")
        self.states_dir = os.path.join(self.main_dataset_dir, "states")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.states_dir, exist_ok=True)
        
        # Initialize dataset storage
        self.all_data = []

        # Define question types and their order
        self.question_types = [
            ("board_state", "mcq"),
            # ("move_validity", "mcq"),
            # ("foundation_move", "fill"),
            ("deadlock", "mcq"),
            ("move_effectiveness", "mcq")
        ]

    # Remove create_dataset_directory method as it's no longer needed

    def save_current_state(self, dataset_num, question_number):
        # Generate filenames with sequential numbering
        img_filename = f"board_{dataset_num:03d}_{question_number:03d}.png"
        state_filename = f"board_{dataset_num:03d}_{question_number:03d}.json"
        img_path = os.path.join(self.images_dir, img_filename)
        state_path = os.path.join(self.states_dir, state_filename)

        # Get the current display surface
        current_surface = self.screen.copy()
        
        # Resize the surface to 640x480
        resized_surface = pygame.transform.scale(current_surface, (640, 480))
        
        # Save the resized screenshot and state
        pygame.image.save(resized_surface, img_path)
        state_data = self.board.get_game_state()
        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=4)

        return img_filename, state_filename
    
    def generate_qa_data(self):
            question_number = self.questions_generated + 1
            current_type, qa_category = self.question_types[self.questions_generated]
            
            # Save current game state and screenshot
            img_filename, state_filename = self.save_current_state(self.current_dataset, question_number)
            
            # Get game state for QA generation
            state_data = self.board.get_game_state()
            qa_generator = KlondikeQAGenerator(state_data)
            
            # Generate random pile numbers for move-related questions
            from_pile = random.randint(1, 7)
            to_pile = random.randint(1, 7)
            while from_pile == to_pile:
                to_pile = random.randint(1, 7)

            # Map question types to qa_type values
            qa_type_mapping = {
                "board_state": "Target Perception",
                # "move_validity": "ActionOutcome",
                # "foundation_move": "TransitionPath",
                "deadlock": "State Prediction",
                "move_effectiveness": "Strategy Optimization"
            }

            # Map question types to difficulty levels
            qa_level_mapping = {
                "board_state": "Easy",
                # "move_validity": "Medium",
                # "foundation_move": "Medium",
                "deadlock": "Medium",
                "move_effectiveness": "Hard"
            }

            # Generate QA based on question type
            qa_data = None
            if current_type == "board_state":
                qa_data = qa_generator.gen_board_state_qa()
            # elif current_type == "move_validity":
            #    qa_data = qa_generator.gen_move_validity_qa(from_pile, to_pile)
            # elif current_type == "foundation_move":
            #    qa_data = qa_generator.gen_foundation_move_qa()
            elif current_type == "deadlock":
                qa_data = qa_generator.gen_deadlock_qa()
            elif current_type == "move_effectiveness":
                qa_data = qa_generator.gen_move_effectiveness_qa()
            # Format data according to specified structure
            formatted_data = {
                "data_id": f"klondike-{qa_category}-{self.current_dataset:03d}-{question_number:03d}",
                "question_id": question_number,
                "question_description": f"A {current_type} question about the current state of Klondike Solitaire",
                "image": f"images/{img_filename}",
                "state": f"states/{state_filename}",
                "plot_level": qa_data["plot_level"],
                "qa_level": qa_level_mapping[current_type],
                "qa_type": qa_type_mapping[current_type],
                "question": qa_data["question"],
                "answer": qa_data["answer"],
                "analysis": qa_data["analysis"],
                "options": qa_data.get("options", []),
            }

            self.all_data.append(formatted_data)

            self.questions_generated += 1

    def save_datasets(self):
        # Save all QA data to single json file
        path = os.path.join(self.main_dataset_dir, "data.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, indent=4, ensure_ascii=False)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            InputManager.process_input(event)

        InputManager.cursor_pos = pygame.mouse.get_pos()
        InputManager.cursor_rel_pos = pygame.mouse.get_rel()
        return True

    def update(self):
        self.board.update()
        
    def render(self):
        self.screen.fill("white")
        self.screen.blit(self.bg, (0, 0))
        self.board.draw(self.screen)
        pygame.display.flip()

    def run(self):
        print(f"Starting data generation for {self.total_datasets} datasets...")
        
        # Create progress bars
        dataset_pbar = tqdm(total=self.total_datasets, desc="Datasets", position=0)
        #question_pbar = tqdm(total=TOTAL_DATASETS, desc="Questions", position=1, leave=False)

        while self.current_dataset <= self.total_datasets:
            # Reset question counter
            self.questions_generated = 0
            #question_pbar.reset()

            # Generate 3 questions for current dataset
            self.questions_generated = 0
            while self.questions_generated < 3:
                if not self.handle_input():
                    print("\nData generation interrupted by user.")
                    pygame.quit()
                    return

                self.update()
                self.render()
                
                # Generate QA data for current state
                self.generate_qa_data()
                #question_pbar.update(1)
                
                # Reset board with random state for next question
                if self.questions_generated < 3:
                    self.board.randomstart()
                    pygame.time.delay(100)  # Reduced delay for faster generation
            
            # Save current dataset
            self.save_datasets()
            dataset_pbar.update(1)
            
            # Prepare for next dataset
            self.current_dataset += 1

        dataset_pbar.close()
        #question_pbar.close()
        print(f"\nSuccessfully generated {self.total_datasets} datasets!")
        pygame.quit()

# Run the game
if __name__ == "__main__":
    # Set number of datasets to generate
    TOTAL_DATASETS = 167  # Adjust this number as needed
    
    game = Game(1280, 720, TOTAL_DATASETS)
    game.run()
