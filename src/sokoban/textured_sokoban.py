import os
from sokoban import SokobanBoard
from sokoban_texture_handler import SokobanTextureHandler

class TexturedSokobanBoard(SokobanBoard):
    """扩展SokobanBoard类，添加自定义贴图支持"""
    
    def __init__(self, grid, player_x, player_y, texture_handler=None):
        """初始化带贴图的推箱子游戏板
        
        Args:
            grid: 游戏网格
            player_x: 玩家X坐标
            player_y: 玩家Y坐标
            texture_handler: 贴图处理器，如果为None则创建一个新的
        """
        # 调用父类构造函数
        super().__init__(grid, player_x, player_y)
        
        # 初始化贴图处理器
        self.texture_handler = texture_handler if texture_handler else SokobanTextureHandler()
    
    def save_board(self, path: str, add_grid=True):
        """使用贴图渲染游戏板并保存
        
        覆盖父类的方法，使用贴图渲染而不是matplotlib
        
        Args:
            path: 输出图像路径
            add_grid: 是否添加网格线
        """
        # 使用贴图处理器渲染游戏板
        self.texture_handler.render_board(self, path, add_grid)
        print(f"游戏板已渲染并保存至: {path}")

# 修改generate_random_board函数以支持贴图
def generate_textured_random_board(size, texture_handler=None, num_boxes=None, check_solvable=True, max_attempts=10):
    """生成带贴图的随机推箱子游戏板
    
    Args:
        size: 游戏板大小
        texture_handler: 贴图处理器
        num_boxes: 箱子数量
        check_solvable: 是否检查可解性
        max_attempts: 最大尝试次数
    
    Returns:
        TexturedSokobanBoard: 带贴图的游戏板
    """
    from sokoban import generate_random_board
    
    # 使用原始函数生成游戏板
    board = generate_random_board(size, num_boxes, check_solvable, max_attempts)
    
    # 创建带贴图的游戏板
    textured_board = TexturedSokobanBoard(board.grid.copy(), board.player_x, board.player_y, texture_handler)
    
    return textured_board

def setup_game_with_custom_textures(screenshot_path=None):
    """设置带自定义贴图的游戏
    
    Args:
        screenshot_path: 截图文件路径，可选
    
    Returns:
        TexturedSokobanBoard: 配置好贴图的游戏板
    """
    # 创建贴图处理器
    texture_handler = SokobanTextureHandler()
    
    if screenshot_path and os.path.exists(screenshot_path):
        # 如果提供了截图，则从中提取贴图
        print(f"从截图中提取贴图: {screenshot_path}")
        texture_handler.extract_textures_from_screenshot(screenshot_path)
        texture_handler.create_combined_textures()
        texture_handler.make_textures_blend_naturally()
    else:
        print("使用默认贴图")
    
    # 生成带贴图的随机游戏板
    board = generate_textured_random_board(6, texture_handler, num_boxes=2)
    
    return board

# 演示用法示例
if __name__ == "__main__":
    # 检查是否提供了截图路径作为命令行参数
    import sys
    screenshot_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 设置游戏
    board = setup_game_with_custom_textures(screenshot_path)
    
    # 保存渲染后的游戏板
    board.save_board("custom_textured_board.png")
    
    print("游戏已设置完成，请查看生成的图像文件。")