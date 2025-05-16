# image_exporter.py

import os
from PIL import Image, ImageDraw, ImageFont
from model import Model, Card, ALLRANKS, SUITNAMES, RANKNAMES

# Define constants, keeping consistent with view.py
CARDWIDTH = 71
CARDHEIGHT = 96
MARGIN = 2
XSPACING = CARDWIDTH + MARGIN
YSPACING = CARDHEIGHT + MARGIN
OFFSET1 = 12
OFFSET2 = 25

MAX_STOCK_DISPLAY = 10      # Maximum number of cards to display in the stock pile
STOCK_DELTA_X = 20          # X-axis offset for each card in the stock

BACKGROUND = (7, 112, 7)     # '#070' in RGB
OUTLINE = (6, 96, 6)         # '#060' in RGB
CELEBRATE = (255, 255, 0)    # 'yellow' in RGB

# Define font (requires the relevant font to be present in the system)
try:
    FONT = ImageFont.truetype("arial.ttf", 14)
except IOError:
    FONT = ImageFont.load_default()

class ImageExporter:
    def __init__(self, model, card_dir='cards', output_path='game_state.png'):
        self.model = model
        self.card_dir = card_dir
        self.output_path = output_path
        self.image_dict = {}
        self.load_images()
        # Dynamically calculate canvas width based on number of waste piles
        self.canvas_width = max(745, + self.model.num_waste * XSPACING)
        self.canvas_height = 410
        self.canvas = Image.new('RGB', (self.canvas_width, self.canvas_height), BACKGROUND)
        self.draw = ImageDraw.Draw(self.canvas)

    def load_images(self):
        """
        Load all card front and back images into image_dict
        """
        # Load back image
        blue_back_path = os.path.join(self.card_dir, 'blueBackVert.gif')
        if not os.path.exists(blue_back_path):
            raise FileNotFoundError(f'Card image file missing: {blue_back_path}')
        blue_back = Image.open(blue_back_path).convert('RGBA')
        self.image_dict['blue'] = blue_back

        # Load front images
        for rank in ALLRANKS:
            suit = 'spade'
            face_filename = f'{suit}{RANKNAMES[rank]}.gif'
            face_path = os.path.join(self.card_dir, face_filename)
            if not os.path.exists(face_path):
                print(f'Card image file missing: {face_filename}')
                continue
            try:
                face = Image.open(face_path).convert('RGBA')
                self.image_dict[(rank, suit)] = face
            except Exception as e:
                print(f'Unable to load card image: {face_filename}, Error: {e}')

    def generate_image(self):
        """
        Generate an image based on the current game state
        """
        self.draw_stock()
        self.draw_foundations()
        self.draw_wastes()
        # Optional: Add more elements like statistics, etc.
        self.canvas.save(self.output_path)
        print(f"Game image saved to {self.output_path}")

    def draw_stock(self):
        """
        Draw the stock pile on the canvas
        """
        x, y = MARGIN, 5 * MARGIN
        stock_width = STOCK_DELTA_X * (MAX_STOCK_DISPLAY - 1) + CARDWIDTH
        # Draw the rectangle frame for the stock pile
        stock_rect = [x, y, x + stock_width, y + CARDHEIGHT]
        self.draw.rectangle(stock_rect, outline=OUTLINE)
        # Add "Stock" text
        # self.draw.text((x + stock_width//2 - 20, y + CARDHEIGHT//2 - 10), "Stock", fill=(255,255,255), font=FONT)

        # Calculate the number of cards to display
        n = len(self.model.stock)
        deals_left = n // self.model.num_waste
        display_n = min(deals_left, MAX_STOCK_DISPLAY)
        delta_x = STOCK_DELTA_X

        if display_n > 0:
            for i in range(display_n):
                pos_x = x + i * delta_x
                pos_y = y
                self.canvas.paste(self.image_dict['blue'], (pos_x, pos_y), self.image_dict['blue'])
            remaining_deals = deals_left - display_n
            if remaining_deals > 0:
                # Add text for remaining deal counts
                text = f"+{remaining_deals}"
                text_pos = (x + display_n * delta_x + 10, y + CARDHEIGHT//2 - 10)
                self.draw.text(text_pos, text, fill=(255,255,255), font=FONT)
        else:
            # Display "Empty" text
            text = "Empty"
            text_pos = (x + CARDWIDTH//2 - 20, y + CARDHEIGHT//2 - 10)
            self.draw.text(text_pos, text, fill=(255,255,255), font=FONT)

    def draw_foundations(self):
        """
        Draw the foundation piles on the canvas
        """
        x, y = MARGIN + XSPACING, 5 * MARGIN
        for k in range(8):
            foundation_rect = [x, y, x + CARDWIDTH, y + CARDHEIGHT]
            self.draw.rectangle(foundation_rect, outline=OUTLINE)
            # Draw the top card in the foundation pile
            if len(self.model.foundations[k]) > 0:
                card = self.model.foundations[k][-1]
                img = self.image_dict.get((card.rank, card.suit))
                if img:
                    self.canvas.paste(img, (x, y), img)
            x += XSPACING

    def draw_wastes(self):
        """
        Draw the waste piles on the canvas
        """
        # Dynamically calculate the starting x position to evenly distribute waste piles
        num_waste = self.model.num_waste
        total_width = num_waste * XSPACING
        start_x = (self.canvas_width - total_width) // 2

        x, y = start_x, 5 * MARGIN + YSPACING
        for k in range(num_waste):
            # Draw the rectangle frame for the waste pile
            waste_rect = [x, y, x + CARDWIDTH, y + CARDHEIGHT]
            self.draw.rectangle(waste_rect, outline=OUTLINE)
            # Draw the cards in the waste pile
            current_y = y
            for card in self.model.waste[k]:
                if card.faceUp():
                    img = self.image_dict.get((card.rank, card.suit))
                else:
                    img = self.image_dict.get('blue')
                if img:
                    self.canvas.paste(img, (x, current_y), img)
                if card.faceUp():
                    current_y += OFFSET2
                else:
                    current_y += OFFSET1
            x += XSPACING

def image_export(output_dir='output', file_name='image.png'):
    """
    Export the current game state as an image.

    Parameters:
        output_dir (str): The directory where the image will be saved.
        file_name (str): The name of the image file.
    """
    # Initialize the game model with a custom number of waste piles
    model = Model(num_waste=8)  # Change this value to test different numbers of waste piles
    # Optionally, perform initial dealing or other game operations
    # For example:
    # model.dealUp()  # Deal face-up cards

    # Set the output image path and name
    card_dir = 'cards'  # Ensure this directory contains all card images

    # Ensure the output directory exists
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except Exception as e:
            print(f"Unable to create output directory {output_dir}: {e}")
            return

    # Complete file path
    output_path = os.path.join(output_dir, file_name)

    try:
        exporter = ImageExporter(model, card_dir=card_dir, output_path=output_path)
        exporter.generate_image()
    except Exception as e:
        print(f"Error generating game image: {e}")

if __name__ == "__main__":
    image_export()
