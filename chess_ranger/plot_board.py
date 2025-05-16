from PIL import Image, ImageDraw, ImageFont

class ChessBoardImage:
    def __init__(self, fen):
        self.board_size = 8
        self.cell_size = 60  # 每个格子的大小
        border_width = 10  # 边框宽度
        label_padding = 20  # 文本标签与棋盘边缘的距离
        font_size = 16  # 标签字体大小
        
        # 使用 truetype 加载特定字体文件，如果需要的话可以指定路径
        self.font = ImageFont.truetype("arial.ttf", font_size) if 'truetype' in dir(ImageFont) else ImageFont.load_default()
        
        # 创建带有额外空间用于边框和坐标的图像
        image_width = (self.board_size * self.cell_size) + border_width * 2 + label_padding
        image_height = (self.board_size * self.cell_size) + border_width * 2 + label_padding
        self.image = Image.new('RGB', (image_width, image_height), 'white')
        self.draw = ImageDraw.Draw(self.image)
        
        self.load_pieces()
        self.draw_board(border_width, label_padding)

        # 设置初始位置以便放置棋子，考虑到边框和坐标
        offset_x = border_width + label_padding // 2
        offset_y = border_width + label_padding // 2
        self.set_up_board(fen, offset_x, offset_y)

    def draw_board(self, border_width, label_padding):
        colors = ["white", "gray"]
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size + border_width + label_padding // 2
                y1 = row * self.cell_size + border_width + label_padding // 2
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = colors[(row + col) % 2]
                self.draw.rectangle([x1, y1, x2, y2], fill=color)

        # 绘制边框线
        self.draw.rectangle(
            [border_width + label_padding // 2 - 1, border_width + label_padding // 2 - 1,
             self.board_size * self.cell_size + border_width + label_padding // 2,
             self.board_size * self.cell_size + border_width + label_padding // 2],
            outline='black', width=2
        )

        # 添加行号（从下到上为1-8），并确保它们水平居中
        for i in range(self.board_size):
            y = self.board_size * self.cell_size - i * self.cell_size + border_width + label_padding // 2 -self.cell_size//2
            text = str(i + 1)
            left, top, right, bottom = self.font.getbbox(text)  # 获取字符的边界框以确定高度和宽度
            text_width = right - left
            text_height = bottom - top
            x = border_width - text_width // 2  # 水平居中：边框宽度减去文本宽度的一半
            self.draw.text((x, y - text_height // 2), text, fill='black', font=self.font)

         # 添加列号（从左到右a-h），并确保它们下对齐
        for i in range(self.board_size):
            x = i * self.cell_size + border_width + label_padding // 2 + self.cell_size // 2
            text = chr(ord('a') + i)
            left, top, right, bottom = self.font.getbbox(text)  # 获取字符的边界框以确定高度和宽度
            text_width = right - left
            text_height = bottom - top

            # 计算y坐标使得文本下对齐
            y = self.board_size * self.cell_size + border_width + label_padding + 5 # 图像底部加上边框和填充

            # 将文本绘制在指定位置，并使用 'ms' 锚点参数来实现下对齐
            self.draw.text((x - text_width // 2, y), text, fill='black', font=self.font, anchor='ms')

    def load_pieces(self):
        pieces = {
            "R": "rook", "N": "knight", "B": "bishop", "Q": "queen", "K": "king", "P": "pawn"
        }
        self.piece_images = {}
        for key, value in pieces.items():
            image_path = f"plot_image/{value}.png"  # 假设所有棋子图像都是同一颜色
            img = Image.open(image_path)
            img = img.resize((self.cell_size, self.cell_size), Image.LANCZOS)
            self.piece_images[key] = img

    def set_up_board(self, fen, offset_x, offset_y):
        rows = fen.split('/')
        board_setup = []
        for r, row in enumerate(rows):
            col = 0
            for piece in row:
                if piece.isdigit():
                    col += int(piece)
                elif piece.isalpha():  # 如果是字母，则放置相应的棋子
                    piece_type = piece.upper()
                    board_setup.append((piece_type, col, r))
                    col += 1

        for piece, col, row in board_setup:
            x = col * self.cell_size + offset_x
            y = row * self.cell_size + offset_y
            piece_image = self.piece_images[piece]
            self.image.paste(piece_image, (x, y), mask=piece_image)

    def save_image(self, filename="chessboard.png"):
        self.image.save(filename)
        print(f"Chessboard saved as {filename}")

if __name__ == "__main__":
    fen_string = "8/1K6/8/3B4/1N5B/2N2P2/N1N5/BB2Q3"
    chess_board = ChessBoardImage(fen_string)
    chess_board.save_image("output_chessboard_with_border.png")