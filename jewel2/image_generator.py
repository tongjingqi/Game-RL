from PIL import Image, ImageDraw, ImageFont
import os

from chessboard import Chessboard
from level import Level
from randomizer import SpecialRandom

def generate_jewel2_image(chessboard: list, total_cleared: int, font_path: str = "font/Arial.ttf", output_path: str = "images/jewel2.png"):
    """
    Generate an image of the current Jewel2 chessboard.
    The output image resolution is 480x640. The chessboard fills the image as much as possible, 
    including a title, row/column numbers, and tick marks outside the chessboard.

    Parameters:
    - chessboard: A 2D list representing the current chessboard elements.
    - total_cleared: An integer representing the total number of cleared elements.
    - font_path: Path to the font file. Default is "arial.ttf".
    - output_path: Path to save the generated image. Default is "images/jewel2.png".
    """
    # Ensure the save directory exists
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # Fixed image resolution
    image_width = 480
    image_height = 640
    title = "Jewel2 Game"

    # Load fonts
    try:
        title_font = ImageFont.truetype(font_path, 55)
        number_font = ImageFont.truetype(font_path, 20)
        cell_font = ImageFont.truetype(font_path, 30)
    except IOError:
        print(f"Font file '{font_path}' not found. Try using the default font.")
        title_font = ImageFont.load_default()
        number_font = ImageFont.load_default()
        cell_font = ImageFont.load_default()

    # Define chessboard parameters
    size = len(chessboard)  # Assume the chessboard is square
    left_margin = 60   # Left margin for row numbers and tick marks
    top_margin = 150   # Top margin for the title and column numbers
    right_margin = 20
    bottom_margin = 50

    # Calculate the maximum usable width and height for the chessboard
    available_width = image_width - left_margin - right_margin
    available_height = image_height - top_margin - bottom_margin

    # Calculate cell size to fill the chessboard as much as possible
    cell_size = min(available_width // size, available_height // size)

    # Actual chessboard width and height
    board_width = cell_size * size
    board_height = cell_size * size

    # Starting position of the chessboard
    board_x = left_margin
    board_y = top_margin

    # Create a white background image
    img = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(img)

    # Draw the title
    title_bbox = title_font.getbbox(title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (image_width - title_width) // 2
    title_y = 10  # Adjust as needed
    draw.text((title_x, title_y), title, fill="black", font=title_font)

    # Draw column numbers and tick marks
    for c in range(size):
        # Column numbers are drawn closer to the chessboard
        col_num = str(c)
        col_bbox = number_font.getbbox(col_num)
        col_width = col_bbox[2] - col_bbox[0]
        col_height = col_bbox[3] - col_bbox[1]
        col_x = board_x + c * cell_size + cell_size // 2 - col_width // 2
        col_y = board_y - 30 - col_height // 2
        draw.text((col_x, col_y), col_num, fill="black", font=number_font)

        # Draw tick marks just above the chessboard
        tick_y1 = board_y - 5
        tick_y2 = board_y
        tick_x = board_x + c * cell_size + cell_size // 2
        draw.line([(tick_x, tick_y1), (tick_x, tick_y2)], fill="black", width=1)

    # Draw row numbers and tick marks
    for r in range(size):
        row_num = str(r)
        row_bbox = number_font.getbbox(row_num)
        row_width = row_bbox[2] - row_bbox[0]
        row_height = row_bbox[3] - row_bbox[1]
        row_x = board_x - 30 - row_width // 2
        row_y = board_y + r * cell_size + cell_size // 2 - row_height // 2
        draw.text((row_x, row_y), row_num, fill="black", font=number_font)

        # Draw tick marks just to the left of the chessboard
        tick_x1 = board_x - 5
        tick_x2 = board_x
        tick_y = board_y + r * cell_size + cell_size // 2
        draw.line([(tick_x1, tick_y), (tick_x2, tick_y)], fill="black", width=1)

    # Define image paths for the elements
    element_images = {
        'A': 'images/A.png',
        'B': 'images/B.png',
        'C': 'images/C.png',
        'D': 'images/D.png',
        'E': 'images/E.png',
        'a': 'images/a_s.png',
        'b': 'images/b_s.png',
        'c': 'images/c_s.png',
        'd': 'images/d_s.png',
        'e': 'images/e_s.png',
        '+': 'images/cross.png',
        '|': 'images/bar.png',
        ' ': 'images/empty.png'  # Image for empty space (if needed)
    }

    # Draw the chessboard and its elements
    for r in range(size):
        for c in range(size):
            x0 = board_x + c * cell_size
            y0 = board_y + r * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            element = chessboard[r][c]

            # Load image for the element
            img_path = element_images.get(element, 'images/empty.png')
            element_img = Image.open(img_path)

            # Scale the image to fit within the cell
            element_img = element_img.resize((cell_size, cell_size), Image.Resampling.LANCZOS)

            # Paste the image into the chessboard cell
            img.paste(element_img, (x0, y0))

    # Draw the total cleared count
    cleared_text = f"Total Cleared: {total_cleared}"
    try:
        cleared_font = ImageFont.truetype(font_path, 30)
    except IOError:
        cleared_font = ImageFont.load_default()
    cleared_bbox = cleared_font.getbbox(cleared_text)
    cleared_width = cleared_bbox[2] - cleared_bbox[0]
    cleared_height = cleared_bbox[3] - cleared_bbox[1]
    cleared_x = (image_width - cleared_width) // 2
    cleared_y = image_height - cleared_height - 50  # 50 pixels from the bottom
    draw.text((cleared_x, cleared_y), cleared_text, fill="black", font=cleared_font)

    # Save the image
    img.save(output_path)
    print(f"The image has been saved to '{output_path}'.")

if __name__ == "__main__":
    # Initialize random generator
    randomizer = SpecialRandom()

    # Initialize the chessboard
    chessboard = Chessboard(randomizer)

    # Initialize the level
    level = Level(chessboard)

    # Generate the image
    generate_jewel2_image(chessboard.chessboard, level.total_cleared, font_path="font/Arial.ttf", output_path="image/jewel2.png")
