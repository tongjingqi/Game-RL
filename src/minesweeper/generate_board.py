# generate_board.py

from minesweeper import Minesweeper  # Import the Minesweeper class from another file
from PIL import Image, ImageDraw, ImageFont

def generate_board_image(game, font_path=None):
    """
    Generate an image of the current Minesweeper board.
    The output image resolution is 480x640, the board fills the image as much as possible, includes a title, 
    and draws row and column numbers outside the board.
    """
    # Fixed image resolution
    image_width = 480
    image_height = 640
    title_height = image_height - image_width  # Height of the title area

    # Calculate appropriate cell_size to maximize board fill
    max_board_width = image_width - 80  # Leave margins for row and column labels
    max_board_height = image_height - title_height - 40  # Position the board close to the bottom
    cell_size = min(max_board_width // game.cols, max_board_height // game.rows)

    board_width = game.cols * cell_size
    board_height = game.rows * cell_size

    # Create canvas
    img = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(img)

    # Set fonts
    title_font_size = 45  # Increase title font size
    cell_font_size = int(cell_size * 0.4)  # Adjust font size dynamically based on cell size
    number_font_size = int(cell_size * 0.3)  # Font size for row/column numbers
    font_path = "font/Arial.ttf"  # Specify font

    title_font = ImageFont.truetype(font_path, title_font_size)
    cell_font = ImageFont.truetype(font_path, cell_font_size)
    number_font = ImageFont.truetype(font_path, number_font_size)

    # Draw title
    title = "Minesweeper Board"
    title_bbox = title_font.getbbox(title)  # Use getbbox to calculate text dimensions
    text_width, text_height = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
    title_x = (image_width - text_width) // 2
    title_y = (title_height - text_height) // 2
    draw.rectangle([0, 0, image_width, title_height], fill="white")  # Title background color
    draw.text((title_x, title_y), title, fill="black", font=title_font)

    # Starting position of the board area
    offset_x = 40  # Leave space for row numbers on the left
    offset_y = image_height - board_height - 40  # Position the board close to the bottom

    # Set number color mapping
    num_color = {
        1: "blue", 2: "green", 3: "red",
        4: "purple", 5: "maroon", 6: "turquoise",
        7: "black", 8: "gray"
    }

    # Draw row numbers and tick marks
    for r in range(game.rows):
        # Position row numbers closer to the board
        number_x = offset_x - cell_size * 0.3
        number_y = offset_y + r * cell_size + cell_size // 2
        draw.text((number_x, number_y), str(r), fill="black", font=number_font, anchor="mm")
        
        # Draw tick marks close to the left of the board
        tick_x1 = offset_x - 5
        tick_x2 = offset_x
        tick_y = offset_y + r * cell_size + cell_size // 2
        draw.line([(tick_x1, tick_y), (tick_x2, tick_y)], fill="black", width=1)

    # Draw column numbers and tick marks
    for c in range(game.cols):
        # Position column numbers closer to the board
        number_x = offset_x + c * cell_size + cell_size // 2
        number_y = offset_y - cell_size * 0.4  # Position closer to the top of the board
        draw.text((number_x, number_y), str(c), fill="black", font=number_font, anchor="mm")
        
        # Draw tick marks close to the top of the board
        tick_y1 = offset_y - 5
        tick_y2 = offset_y
        tick_x = offset_x + c * cell_size + cell_size // 2
        draw.line([(tick_x, tick_y1), (tick_x, tick_y2)], fill="black", width=1)

    # Draw the board
    for r in range(game.rows):
        for c in range(game.cols):
            x0, y0 = offset_x + c * cell_size, offset_y + r * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size

            if not game.revealed[r][c]:
                color = (192, 192, 192)
                draw.rectangle([x0, y0, x1, y1], fill=color)
                if game.flagged[r][c]:
                    draw.text((x0 + cell_size // 2, y0 + cell_size // 2), "F", fill="red", font=cell_font, anchor="mm")
            else:
                color = (255, 255, 255)
                draw.rectangle([x0, y0, x1, y1], fill=color)
                if game.mine_board[r][c] > 0:
                    text_color = num_color.get(game.mine_board[r][c], "black")
                    # Draw the number
                    draw.text((x0 + cell_size // 2, y0 + cell_size // 2), str(game.mine_board[r][c]), fill=text_color, font=cell_font, anchor="mm")

            draw.rectangle([x0, y0, x1, y1], outline="black")

    return img

if __name__ == "__main__":
    # Create a dynamically sized Minesweeper game
    rows, cols, mines = 5, 5, 5  # Dynamically set the board size
    game = Minesweeper(rows, cols, mines)
    game.reveal(0, 0)

    # Generate the image
    board_image = generate_board_image(game)

    # Display and save the image
    board_image.show()
    board_image.save("minesweeper.png")
