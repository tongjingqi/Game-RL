import json

def fen_to_custom_json_file(fen, output_path):
    """
    将FEN字符串转换为自定义格式的JSON文件。

    参数:
    fen (str): FEN表示法的字符串。
    output_path (str): 输出JSON文件的路径。
    """

    def parse_fen_to_board(fen):
        # Split the FEN string into ranks (rows)
        ranks = fen.split('/')
        
        # Initialize an empty board with zeros
        board_size = 8
        mine_board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        
        # Count pieces, including all non-empty squares.
        pieces_count = 0
        
        # Iterate over each rank from top to bottom as given by the FEN string
        for i, rank in enumerate(ranks):
            file_index = 0  # Column index within the current rank
            for char in rank:
                if char.isdigit():
                    # If the character is a digit, it represents the number of empty squares
                    file_index += int(char)
                else:
                    # Otherwise, place the piece on the board and increment the piece count
                    mine_board[i][file_index] = char.upper() if char.isupper() else char.lower()
                    pieces_count += 1
                    file_index += 1
        
        return pieces_count, mine_board
    
    # Parse the FEN string to get the board state and piece count
    pieces_count, mine_board = parse_fen_to_board(fen)

    # Create the custom JSON structure
    custom_json = {
        "pieces": pieces_count,
        "mine_board": mine_board
    }
    
    # Save the JSON data to the specified file path
    with open(output_path, 'w') as json_file:
        json.dump(custom_json, json_file, indent=4)

    print(f"JSON file has been created at {output_path}.")
