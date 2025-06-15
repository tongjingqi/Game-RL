import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import numpy as np
import json
import os

# 球类
class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.color = self.generate_random_color()
        self.radius = radius

    def generate_random_color(self):
        np.random.seed()  # 使用当前时间作为种子
        return np.random.choice(['red', 'yellow', 'blue', 'green'])

    def draw(self, ax):
        circle = patches.Circle((self.x, self.y), self.radius, facecolor=self.color, edgecolor='black')
        ax.add_patch(circle)

# 轨道类
class Track:
    def __init__(self, nearest_point, width, curve_func, *curve_params):
        self.nearest_point = nearest_point
        self.width = width
        self.curve_func = curve_func
        self.curve_params = curve_params
        self.plot_level = "Medium"

    def draw(self, ax, num_balls):
        # 生成曲线路径
        if 10 <= num_balls <= 15:
            len = np.random.uniform(0.5, 1)
            self.plot_level = "Easy"
        elif 15 < num_balls <= 30:
            len = np.random.uniform(1, 1.5)
            self.plot_level = "Easy"
        elif 30 < num_balls <= 55:
            len = np.random.uniform(1.5, 2)
            self.plot_level = "Medium"
        elif 55 < num_balls <= 75:
            len = np.random.uniform(2, 2.5)
            self.plot_level = "Medium"
        elif 75 < num_balls <= 100:
            len = np.random.uniform(2.5, 3)
            self.plot_level = "Hard"
        else:
            len = 3
            self.plot_level = "Hard"
        t = np.linspace(0, len, 2000)
        curve_x, curve_y = self.curve_func(t, self.nearest_point, *self.curve_params)
        
        # 计算法向量并生成轨道的两条边界
        dx = np.gradient(curve_x, t)
        dy = np.gradient(curve_y, t)
        normal_x = -dy / np.sqrt(dx**2 + dy**2)
        normal_y = dx / np.sqrt(dx**2 + dy**2)
        left_x = curve_x + normal_x * self.width / 2
        left_y = curve_y + normal_y * self.width / 2
        right_x = curve_x - normal_x * self.width / 2
        right_y = curve_y - normal_y * self.width / 2
        
        # 创建 Path 对象并绘制
        path_data = [
            (mpath.Path.MOVETO, (left_x[0], left_y[0])),
            *[(mpath.Path.LINETO, (lx, ly)) for lx, ly in zip(left_x[1:], left_y[1:])],
            (mpath.Path.LINETO, (right_x[-1], right_y[-1])),
            *[(mpath.Path.LINETO, (rx, ry)) for rx, ry in zip(right_x[:-1][::-1], right_y[:-1][::-1])],
            (mpath.Path.CLOSEPOLY, (left_x[0], left_y[0]))
        ]
        codes, verts = zip(*path_data)
        path = mpath.Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='lightgray', edgecolor='black', linewidth=1)
        ax.add_patch(patch)

        return curve_x, curve_y

# 孔洞类
class Hole:
    def __init__(self, point, radius):
        self.point = point
        self.radius = radius

    def draw(self, ax):
        circle = patches.Circle(self.point, self.radius, facecolor='black', edgecolor='black')
        ax.add_patch(circle)

# 青蛙类
class Frog:
    def __init__(self, point, ball_radius):
        self.x, self.y = point
        self.base = 4*ball_radius
        self.height = 6*ball_radius
        self.ball_radius = ball_radius
        self.color = self.generate_random_color()
        self.next_color = self.generate_random_color()
        self.angle = np.random.randint(-179, 180)

    def generate_random_color(self):
        np.random.seed()  # 使用当前时间作为种子
        return np.random.choice(['red', 'yellow', 'blue', 'green'])

    def draw(self, ax):
        # 绘制长等腰白色三角形
        angle_rad = np.radians(self.angle)
        top_point = (
            self.x + self.height * 2/3 * np.cos(angle_rad),
            self.y + self.height * 2/3 * np.sin(angle_rad)
        )
        left_point = (
            self.x - self.base/2 * np.cos(angle_rad - np.pi/2) - self.height * 1/3 * np.cos(angle_rad),
            self.y - self.base/2 * np.sin(angle_rad - np.pi/2) - self.height * 1/3 * np.sin(angle_rad)
        )
        right_point = (
            self.x + self.base/2 * np.cos(angle_rad - np.pi/2) - self.height * 1/3 * np.cos(angle_rad),
            self.y + self.base/2 * np.sin(angle_rad - np.pi/2) - self.height * 1/3 * np.sin(angle_rad)
        )
        triangle = patches.Polygon([
            top_point, left_point, right_point
        ], facecolor='white', edgecolor='black')
        ax.add_patch(triangle)

        # 绘制圆形，表示将要发出的球的颜色
        circle = patches.Circle((self.x, self.y), self.ball_radius, facecolor=self.color, edgecolor='black')
        ax.add_patch(circle)

        # 绘制方位分区射线
        direction_angles = [22.5, -22.5, 67.5, -67.5, 112.5, -112.5, 157.5, -157.5]  # 对应八个方位的中心角度
        line_length = 20 # 射线长度
        
        for angle in direction_angles:
            rad = np.radians(angle)
            end_x = self.x + line_length * np.cos(rad)
            end_y = self.y + line_length * np.sin(rad)
            ax.plot([self.x, end_x], [self.y, end_y], 'k--', alpha=0.3)

# 游戏轨道类
class ZumaGame:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.balls = []

    def draw(self, frogpoint, holepoint, track, num_balls, ball_radius, output_prefix):
        curve_x, curve_y = track.draw(self.ax, num_balls)
        hole_x, hole_y = holepoint
        track_info = {
            "plot_level": track.plot_level,
            "hole_position": {"x": hole_x, "y": hole_y}
        }

        # 绘制孔洞
        hole = Hole(holepoint, 2*ball_radius)
        hole.draw(self.ax)

        # 绘制青蛙
        frog = Frog(frogpoint, ball_radius)
        frog.draw(self.ax)

        # 收集青蛙信息
        frog_info = {
            "position": {"x": frog.x, "y": frog.y},
            "angle": frog.angle,
            "next_ball_color": frog.color,
            "after_next_ball_color": frog.next_color
        }

        # 从最远端开始生成球
        ball_centers_x = [curve_x[-1]]
        ball_centers_y = [curve_y[-1]]
        
        # 计算每个新球的中心位置
        k = len(curve_x) - 1
        for i in range(1, num_balls):
            prev_x, prev_y = ball_centers_x[-1], ball_centers_y[-1]
            for j in range(k - 1, -1, -1):
                next_x, next_y = curve_x[j], curve_y[j]
                distance = np.sqrt((next_x - prev_x)**2 + (next_y - prev_y)**2)
                if distance >= 2 * ball_radius:
                    ball_centers_x.append(next_x)
                    ball_centers_y.append(next_y)
                    k = j
                    break
        
        # 放置球并收集信息
        ball_data = []
        for x, y in zip(ball_centers_x, ball_centers_y):
            ball = Ball(x, y, ball_radius)
            self.balls.append(ball)
            ball.draw(self.ax)
            ball_data.append({"position": {"x": x, "y": y}, "color": ball.color})

        game_data = {
            "track": track_info,
            "frog": frog_info,
            "balls": ball_data
        }

        # 保存图像到文件
        self.ax.set_xlim(min(curve_x) - 1.5*ball_radius, max(curve_x) + 1.5*ball_radius)
        self.ax.set_ylim(min(curve_y) - 1.5*ball_radius, max(curve_y) + 1.5*ball_radius)
        self.ax.axis("off")
        picture_path = f"images/{output_prefix}.png"
        self.fig.savefig(
            picture_path,
            dpi=100,
            bbox_inches="tight",  # 防止裁剪内容
            pad_inches=0  # 不添加额外空白
        )
        # print(f"Game image saved to {picture_path}")

        # 保存 JSON 数据到文件
        json_path = f"states/{output_prefix}.json"
        with open(json_path, "w") as json_file:
            json.dump(game_data, json_file, indent=4)
        # print(f"Game data saved to {json_path}")

        # plt.xlim(-15, 15)
        # plt.ylim(-15, 15)
        # plt.show()
        plt.close(self.fig)

        return game_data

    # 波浪形曲线函数
    @staticmethod
    def wave_curve(t, y_center, amplitude, frequency):
        return t, y_center + amplitude * np.sin(frequency * t)
    
    # 螺旋线函数
    @staticmethod
    def spiral_curve(t, point, b):
        p,q = point
        a = np.sqrt(p**2 + q**2) - b*np.arctan2(q, p)
        theta = t * 2 * np.pi +  np.arctan2(q, p)
        r = a + b * theta
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y

    # 心形线函数
    @staticmethod
    def heart_curve(t, point):
        x = 16 * np.sin(t)**3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        return x, y

    # 椭圆曲线函数
    @staticmethod
    def ellipse_curve(t, point, a, b):
        x = a * np.cos(t)
        y = b * np.sin(t)
        return x, y
    
# 自定义绘制函数
def draw_game(curve_type, ball_radius, *curve_params):
    # 创建输出文件夹
    os.makedirs("images", exist_ok=True)
    os.makedirs("states", exist_ok=True)

    # 自动生成文件序号
    existing_files = os.listdir("images")
    max_index = max(
        [int(f.split('.')[0]) for f in existing_files if f.endswith(".png")], 
        default=0
    )
    output_prefix = f"{max_index + 1:04d}"  # 格式化为四位序号

    game = ZumaGame()
    x = np.random.uniform(1.5, 3) * np.random.choice([-1, 1])
    y = np.random.uniform(1.5, 3) * np.random.choice([-1, 1])
    holepoint = (x, y)
    x = np.random.uniform(-1, 1)
    y = np.random.uniform(-1, 1)
    frogpoint = (x, y)
    num_balls = np.random.randint(10, 135)

    if curve_type == 'spiral':
        track = Track(holepoint, 2*ball_radius, game.spiral_curve, *curve_params)
    elif curve_type == 'heart':
        track = Track(holepoint, 2*ball_radius, game.heart_curve, *curve_params)
    elif curve_type == 'ellipse':
        track = Track(holepoint, 2*ball_radius, game.ellipse_curve, *curve_params)
    else:
        raise ValueError("Unsupported curve type")
    
    game_data = game.draw(frogpoint, holepoint, track, num_balls, ball_radius, output_prefix)
    # print(json.dumps(game_data, indent=4))
    # return game_data

# 创建游戏实例并绘制
# 示例：绘制螺旋线轨道，放置 70 个球，球半径为 0.3
# draw_game('spiral', 0.3, 0.2)