import os
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import matplotlib.pyplot as plt






# 在sokoban_texture_handler.py中简化坐标显示样式


# 加粗线条绘制数字，确保在背景上仍清晰可见
def draw_number(draw, num, x, y, color="#000000", size=12):
    """直接使用加粗线条绘制数字，不使用背景
    
    Args:
        draw: PIL Draw对象
        num: 要绘制的数字
        x, y: 中心坐标
        color: 数字颜色
        size: 数字大小
    """
    # 计算数字的起始位置
    x0 = x - size//2
    y0 = y - size
    
    # 粗线条确保可见性
    line_width = max(3, size // 4)
    
    # 根据数字绘制不同的形状
    if num == 0:
        # 绘制0 - 椭圆形
        draw.ellipse([x0, y0, x0 + size, y0 + size*2], outline=color, width=line_width)
    elif num == 1:
        # 绘制1 - 竖线
        center_x = x0 + size//2
        draw.line([(center_x, y0), (center_x, y0 + size*2)], fill=color, width=line_width)
    elif num == 2:
        # 绘制2 - 使用多段线条
        points = [
            (x0, y0),  # 左上
            (x0 + size, y0),  # 右上
            (x0 + size, y0 + size),  # 右中
            (x0, y0 + size),  # 左中
            (x0, y0 + size*2),  # 左下
            (x0 + size, y0 + size*2)  # 右下
        ]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=line_width)
    elif num == 3:
        # 绘制3 - 右侧竖线加三条横线
        draw.line([(x0, y0), (x0 + size, y0)], fill=color, width=line_width)  # 上横
        draw.line([(x0, y0 + size), (x0 + size, y0 + size)], fill=color, width=line_width)  # 中横
        draw.line([(x0, y0 + size*2), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 下横
        draw.line([(x0 + size, y0), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 右竖
    elif num == 4:
        # 绘制4 - 左上竖线、右侧竖线和中间横线
        draw.line([(x0, y0), (x0, y0 + size)], fill=color, width=line_width)  # 左上竖
        draw.line([(x0, y0 + size), (x0 + size, y0 + size)], fill=color, width=line_width)  # 中横
        draw.line([(x0 + size, y0), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 右竖
    elif num == 5:
        # 绘制5 - S形状
        draw.line([(x0 + size, y0), (x0, y0)], fill=color, width=line_width)  # 上横
        draw.line([(x0, y0), (x0, y0 + size)], fill=color, width=line_width)  # 左上竖
        draw.line([(x0, y0 + size), (x0 + size, y0 + size)], fill=color, width=line_width)  # 中横
        draw.line([(x0 + size, y0 + size), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 右下竖
        draw.line([(x0 + size, y0 + size*2), (x0, y0 + size*2)], fill=color, width=line_width)  # 下横
    elif num == 6:
        # 绘制6 - 左竖线加闭合的右下部
        draw.line([(x0, y0), (x0, y0 + size*2)], fill=color, width=line_width)  # 左竖
        draw.line([(x0, y0), (x0 + size, y0)], fill=color, width=line_width)  # 上横
        draw.line([(x0, y0 + size), (x0 + size, y0 + size)], fill=color, width=line_width)  # 中横
        draw.line([(x0 + size, y0 + size), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 右下竖
        draw.line([(x0 + size, y0 + size*2), (x0, y0 + size*2)], fill=color, width=line_width)  # 下横
    elif num == 7:
        # 绘制7 - 上横线加右斜线
        draw.line([(x0, y0), (x0 + size, y0)], fill=color, width=line_width)  # 上横
        draw.line([(x0 + size, y0), (x0, y0 + size*2)], fill=color, width=line_width)  # 斜线
    elif num == 8:
        # 绘制8 - 两个圆形
        draw.ellipse([x0, y0, x0 + size, y0 + size], outline=color, width=line_width)  # 上圆
        draw.ellipse([x0, y0 + size, x0 + size, y0 + size*2], outline=color, width=line_width)  # 下圆
    elif num == 9:
        # 绘制9 - 右竖线加闭合的左上部
        draw.line([(x0 + size, y0), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 右竖
        draw.line([(x0, y0), (x0 + size, y0)], fill=color, width=line_width)  # 上横
        draw.line([(x0, y0), (x0, y0 + size)], fill=color, width=line_width)  # 左上竖
        draw.line([(x0, y0 + size), (x0 + size, y0 + size)], fill=color, width=line_width)  # 中横
        draw.line([(x0, y0 + size*2), (x0 + size, y0 + size*2)], fill=color, width=line_width)  # 下横
class SokobanTextureHandler:
    """处理推箱子游戏的贴图资源和渲染"""
    
    def __init__(self, assets_folder="assets", texture_size=64):
        """初始化贴图处理器
        
        Args:
            assets_folder: 贴图资源文件夹
            texture_size: 贴图尺寸（默认64x64像素）
        """
        self.assets_path = assets_folder
        self.texture_size = texture_size
        
        # 确保资源目录存在
        os.makedirs(self.assets_path, exist_ok=True)
        
        # 贴图资源字典
        self.textures = {}
        
        # 初始加载必要的贴图（如果存在）或创建占位图
        self._init_textures()
    
    def _init_textures(self):
        """初始化或加载贴图资源"""
        texture_names = [
            "floor.jpg",    # 地板
            "wall.jpg",     # 墙壁
            "box.jpg",      # 箱子
            "target.jpg",   # 目标
            "player.jpg",   # 玩家
        ]
        
        for name in texture_names:
            file_path = os.path.join(self.assets_path, name)
            if os.path.exists(file_path):
                # 加载并调整尺寸
                try:
                    img = Image.open(file_path)
                    img = img.resize((self.texture_size, self.texture_size))
                    self.textures[name.split('.')[0]] = img
                    print(f"已加载贴图: {name}")
                except Exception as e:
                    print(f"加载贴图失败: {name} - {str(e)}")
                    self._create_placeholder(name)
            else:
                print(f"贴图不存在，创建占位图: {name}")
                self._create_placeholder(name)
    
    def _create_placeholder(self, name):
        """为缺失的贴图创建占位图"""
        texture_type = name.split('.')[0]
        img = Image.new('RGBA', (self.texture_size, self.texture_size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        if texture_type == "floor":
            # 浅褐色木地板
            img = Image.new('RGB', (self.texture_size, self.texture_size), "#D2B48C")
            # 添加木纹
            for i in range(0, self.texture_size, 8):
                draw.line([(0, i), (self.texture_size, i)], fill="#C19A6B", width=1)
                
        elif texture_type == "wall":
            # 砖墙
            img = Image.new('RGB', (self.texture_size, self.texture_size), "#CD853F")
            for y in range(0, self.texture_size, 16):
                for x in range(0, self.texture_size, 32):
                    offset = 16 if (y // 16) % 2 else 0
                    draw.rectangle([x + offset, y, x + offset + 30, y + 14], 
                                 outline="#8B4513", fill="#D2691E")
                    
        elif texture_type == "box":
            # 箱子
            img = Image.new('RGB', (self.texture_size, self.texture_size), "#DEB887")
            # 箱子边框
            draw.rectangle([2, 2, self.texture_size-3, self.texture_size-3], outline="#8B4513", width=2)
            # X标记
            draw.line([(10, 10), (self.texture_size-10, self.texture_size-10)], fill="#8B4513", width=3)
            draw.line([(10, self.texture_size-10), (self.texture_size-10, 10)], fill="#8B4513", width=3)
            
        elif texture_type == "target":
            # 目标点 - 绿色X
            img = Image.new('RGBA', (self.texture_size, self.texture_size), (0, 0, 0, 0))
            draw.line([(10, 10), (self.texture_size-10, self.texture_size-10)], fill="#00FF00", width=3)
            draw.line([(10, self.texture_size-10), (self.texture_size-10, 10)], fill="#00FF00", width=3)
            
        elif texture_type == "player":
            # 玩家
            img = Image.new('RGBA', (self.texture_size, self.texture_size), (0, 0, 0, 0))
            
            # 身体轮廓
            draw.ellipse((8, 8, self.texture_size-8, self.texture_size-8), fill="#3366CC")
            
            # 头部
            head_size = self.texture_size // 3
            head_top = self.texture_size // 4
            draw.ellipse((
                self.texture_size//2 - head_size//2,
                head_top,
                self.texture_size//2 + head_size//2,
                head_top + head_size
            ), fill="#FFD39B")
            
            # 眼睛
            eye_size = self.texture_size // 12
            draw.ellipse((
                self.texture_size//2 - head_size//4 - eye_size//2,
                head_top + head_size//3,
                self.texture_size//2 - head_size//4 + eye_size//2,
                head_top + head_size//3 + eye_size
            ), fill="#000000")
            
            draw.ellipse((
                self.texture_size//2 + head_size//4 - eye_size//2,
                head_top + head_size//3,
                self.texture_size//2 + head_size//4 + eye_size//2,
                head_top + head_size//3 + eye_size
            ), fill="#000000")
            
            # 嘴巴
            mouth_top = head_top + head_size//3 + head_size//4
            draw.arc(
                (self.texture_size//2 - head_size//3, mouth_top,
                 self.texture_size//2 + head_size//3, mouth_top + head_size//4),
                180, 360, fill="#000000", width=2
            )
        
        # 保存占位图并加载到贴图字典
        file_path = os.path.join(self.assets_path, name)
        img.save(file_path)
        self.textures[texture_type] = img
        print(f"已创建并保存占位图: {name}")
    
    def extract_textures_from_screenshot(self, screenshot_path, output_dir=None):
        """从游戏截图中提取贴图
        
        这个函数可以帮助从完整游戏截图中裁剪出各种元素的贴图
        
        Args:
            screenshot_path: 截图文件路径
            output_dir: 输出目录，默认为assets_path
        """
        if output_dir is None:
            output_dir = self.assets_path
            
        try:
            # 加载截图
            screenshot = Image.open(screenshot_path)
            
            # 显示图像并让用户选择裁剪区域
            plt.figure(figsize=(10, 10))
            plt.imshow(np.array(screenshot))
            plt.title("请记录要提取的区域坐标，按关闭按钮继续")
            plt.show()
            
            # 使用控制台交互，让用户输入坐标
            print("从截图中提取贴图:")
            print("请输入要提取的区域坐标 (左上x 左上y 右下x 右下y)，每种贴图一行")
            
            # 为每种贴图类型获取区域
            elements = ["floor", "wall", "box", "target", "player"]
            for element in elements:
                try:
                    print(f"\n提取 {element} 贴图:")
                    coords_input = input(f"请输入 {element} 的坐标 (左上x 左上y 右下x 右下y): ")
                    coords = list(map(int, coords_input.strip().split()))
                    
                    if len(coords) == 4:
                        left, top, right, bottom = coords
                        # 裁剪并保存
                        cropped = screenshot.crop((left, top, right, bottom))
                        # 调整为标准大小
                        cropped = cropped.resize((self.texture_size, self.texture_size))
                        # 保存
                        output_path = os.path.join(output_dir, f"{element}.jpg")
                        cropped.save(output_path)
                        print(f"已保存 {element} 贴图到 {output_path}")
                        
                        # 更新贴图字典
                        self.textures[element] = cropped
                    else:
                        print(f"坐标格式错误，跳过 {element}")
                except Exception as e:
                    print(f"提取 {element} 贴图时出错: {str(e)}")
            
            print("\n所有贴图提取完成！")
            
        except Exception as e:
            print(f"提取贴图过程出错: {str(e)}")
    
    def create_combined_textures(self):
        """创建组合贴图，如箱子在目标点上、玩家在目标点上等"""
        # 箱子在目标点上
        if "box" in self.textures and "target" in self.textures:
            box_img = self.textures["box"].copy()
            target_img = self.textures["target"].copy()
            
            # 确保target图像有透明通道
            if target_img.mode != 'RGBA':
                target_img = target_img.convert('RGBA')
            
            # 混合两个图像
            box_on_target = Image.alpha_composite(
                box_img.convert('RGBA'),
                target_img
            )
            
            # 保存组合贴图
            output_path = os.path.join(self.assets_path, "box_on_target.jpg")
            box_on_target.convert('RGB').save(output_path)
            self.textures["box_on_target"] = box_on_target
            print(f"已创建组合贴图: box_on_target")
            
        # 玩家在目标点上
        if "player" in self.textures and "target" in self.textures:
            player_img = self.textures["player"].copy()
            target_img = self.textures["target"].copy()
            
            # 确保两个图像都有透明通道
            if player_img.mode != 'RGBA':
                player_img = player_img.convert('RGBA')
            if target_img.mode != 'RGBA':
                target_img = target_img.convert('RGBA')
            
            # 混合两个图像
            player_on_target = Image.alpha_composite(
                player_img,
                target_img
            )
            
            # 保存组合贴图
            output_path = os.path.join(self.assets_path, "player_on_target.jpg")
            player_on_target.convert('RGB').save(output_path)
            self.textures["player_on_target"] = player_on_target
            print(f"已创建组合贴图: player_on_target")
    
    def apply_smooth_borders(self, texture_name, border_width=2):
        """为贴图应用平滑边框，使其与背景融合更自然
        
        Args:
            texture_name: 贴图名称
            border_width: 边框宽度
        """
        if texture_name not in self.textures:
            print(f"贴图不存在: {texture_name}")
            return
            
        img = self.textures[texture_name].copy()
        
        # 确保图像有透明通道
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # 创建带有透明度渐变的蒙版
        mask = Image.new('L', (self.texture_size, self.texture_size), 255)
        draw = ImageDraw.Draw(mask)
        
        # 边缘渐变
        for i in range(border_width):
            alpha = int(255 * (i / border_width))
            draw.rectangle(
                [i, i, self.texture_size-i-1, self.texture_size-i-1],
                outline=alpha
            )
        
        # 应用蒙版
        img.putalpha(mask)
        
        # 保存处理后的图像
        output_path = os.path.join(self.assets_path, f"{texture_name}_smooth.png")
        img.save(output_path)
        self.textures[f"{texture_name}_smooth"] = img
        print(f"已创建平滑边框贴图: {texture_name}_smooth")

     


    
    
    
    def render_board(self, sokoban_board, output_path, add_grid=True):
        """渲染游戏板，包含简化的坐标显示样式
        
        Args:
            sokoban_board: 推箱子游戏板对象
            output_path: 输出图像路径
            add_grid: 是否添加网格线
        """
        grid = sokoban_board.grid
        height, width = grid.shape
        
        # 为坐标腾出空间
        coord_space = 40  # 减小坐标区域宽度
        
        # 创建画布
        total_width = width * self.texture_size + coord_space
        total_height = height * self.texture_size + coord_space
        
        # 创建主画布，使用浅褐色作为默认背景
        board_img = Image.new('RGB', (total_width, total_height), "#E0C9A6")
        
        # 绘制游戏区域的边框
        draw = ImageDraw.Draw(board_img)
        draw.rectangle(
            [coord_space, coord_space, total_width, total_height],
            outline="#000000",
            width=2
        )
        
        # 使用地板贴图填充游戏区域
        if "floor" in self.textures:
            floor_tile = self.textures["floor"]
            for y in range(height):
                for x in range(width):
                    board_img.paste(
                        floor_tile, 
                        (coord_space + x * self.texture_size, coord_space + y * self.texture_size)
                    )
        
        # 元素映射字典
        element_map = {
            1: "wall",            # 墙
            2: "box",             # 箱子
            3: "target",          # 目标
            4: "box_on_target",   # 箱子在目标上
            5: "player",          # 玩家
            6: "player_on_target" # 玩家在目标上
        }
        
        # 渲染游戏元素
        for y in range(height):
            for x in range(width):
                cell = grid[y, x]
                if cell in element_map and element_map[cell] in self.textures:
                    texture = self.textures[element_map[cell]]
                    board_img.paste(
                        texture, 
                        (coord_space + x * self.texture_size, coord_space + y * self.texture_size), 
                        texture if texture.mode == 'RGBA' else None
                    )
        
        # 添加网格线和坐标
        if add_grid:
            # 绘制水平网格线
            for i in range(height + 1):
                y_pos = coord_space + i * self.texture_size
                draw.line(
                    [(coord_space, y_pos), (total_width, y_pos)], 
                    fill="#000000", width=2
                )
            
            # 绘制垂直网格线
            for i in range(width + 1):
                x_pos = coord_space + i * self.texture_size
                draw.line(
                    [(x_pos, coord_space), (x_pos, total_height)], 
                    fill="#000000", width=2
                )
            
            # 绘制顶部坐标（X轴）- 黑色数字，无背景
            for i in range(width):
                x = coord_space + i * self.texture_size + self.texture_size//2
                y = coord_space // 2
                
                # 直接绘制数字，无背景，使用黑色
                if i < 10:
                    # 单个数字居中显示
                    draw_number(draw, i, x, y, "#000000", 12)
                else:
                    # 双位数：分别绘制十位和个位
                    tens = i // 10
                    ones = i % 10
                    draw_number(draw, tens, x - 10, y, "#000000", 12)  # 十位数字
                    draw_number(draw, ones, x + 10, y, "#000000", 12)  # 个位数字
            
            # 绘制左侧坐标（Y轴）- 黑色数字，无背景
            for i in range(height):
                x = coord_space // 2
                y = coord_space + i * self.texture_size + self.texture_size//2
                
                # 直接绘制数字，无背景，使用黑色
                if i < 10:
                    # 单个数字居中显示
                    draw_number(draw, i, x, y, "#000000", 12)
                else:
                    # 双位数：分别绘制十位和个位
                    tens = i // 10
                    ones = i % 10
                    draw_number(draw, tens, x - 10, y, "#000000", 12)  # 十位数字
                    draw_number(draw, ones, x + 10, y, "#000000", 12)  # 个位数字
            
            # 左上角无标记，保持简洁
        
        # 保存渲染结果
        board_img.save(output_path)
        print(f"游戏板渲染完成，已保存至: {output_path}")
        return board_img
    def auto_extract_demo(self, screenshot_path):
        """演示自动从截图中提取贴图的方法
        
        Args:
            screenshot_path: 截图文件路径
        """
        try:
            # 加载截图
            screenshot = Image.open(screenshot_path)
            
            # 展示截图
            plt.figure(figsize=(12, 12))
            plt.imshow(np.array(screenshot))
            plt.title("分析的游戏截图")
            plt.show()
            
            # 这里应该有基于图像分析的算法来检测游戏元素
            # 由于这需要复杂的计算机视觉算法，这里简化处理
            print("自动分析截图中的游戏元素...")
            
            # 假设我们能够识别出一些典型元素的位置
            # 在实际应用中，这应该通过图像处理算法实现
            example_regions = {
                "floor": (100, 100, 164, 164),   # 示例坐标
                "wall": (200, 100, 264, 164),    # 示例坐标
                "box": (300, 100, 364, 164),     # 示例坐标
                "target": (400, 100, 464, 164),  # 示例坐标
                "player": (500, 100, 564, 164)   # 示例坐标
            }
            
            print("检测到以下游戏元素区域:")
            for element, region in example_regions.items():
                print(f"{element}: {region}")
            
            # 确认是否使用这些区域
            confirm = input("\n是否使用这些检测到的区域提取贴图？(y/n): ")
            if confirm.lower() != 'y':
                print("取消自动提取，请使用手动提取功能。")
                return
                
            # 提取并保存贴图
            for element, region in example_regions.items():
                left, top, right, bottom = region
                # 裁剪
                cropped = screenshot.crop((left, top, right, bottom))
                # 调整大小
                cropped = cropped.resize((self.texture_size, self.texture_size))
                # 保存
                output_path = os.path.join(self.assets_path, f"{element}.jpg")
                cropped.save(output_path)
                # 更新贴图字典
                self.textures[element] = cropped
                print(f"已提取并保存 {element} 贴图")
                
            # 创建组合贴图
            self.create_combined_textures()
            
            print("\n自动提取贴图完成！")
            
        except Exception as e:
            print(f"自动提取贴图过程出错: {str(e)}")
    
    def make_textures_blend_naturally(self):
        """处理所有贴图，使它们与背景融合更自然"""
        for texture_name in list(self.textures.keys()):
            # 只处理非组合贴图
            if "_on_" not in texture_name and "_smooth" not in texture_name:
                self.apply_smooth_borders(texture_name)
        
        # 重新创建组合贴图
        self.create_combined_textures()
        
        print("所有贴图处理完成，现在它们应该能与背景更自然地融合。")

# 使用示例
def demo_extract_and_render(screenshot_path, sokoban_board):
    """演示从截图提取贴图并渲染游戏板的完整流程"""
    # 创建贴图处理器
    handler = SokobanTextureHandler()
    
    # 从截图提取贴图
    handler.extract_textures_from_screenshot(screenshot_path)
    
    # 创建组合贴图
    handler.create_combined_textures()
    
    # 使贴图与背景融合更自然
    handler.make_textures_blend_naturally()
    
    # 渲染游戏板
    handler.render_board(sokoban_board, "rendered_board.png")
    
    print("\n演示完成！游戏板已渲染，贴图已保存。")