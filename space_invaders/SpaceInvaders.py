import pygame
from PIL import Image
import random
import math
import os

TOP_BORDER = 60
LEFT_BORDER = 40
ENEMY_MOVE_DOWN = 55
ENEMY_SPACING_X = 70
BASE_SCREEN_HEIGHT = 600

color_RGB = {
    'red': (255, 0, 0),
    'blue': (0, 191, 255),
    'yellow': (255, 255, 0),
    'grey': (128, 128, 128),
    'pink': (255, 192, 203),
}


class Enemy:
    def __init__(self, row, col, enemy_type: int):
        self.row, self.col = row, col
        self.type = enemy_type
        self.score = {1: 30, 2: 20, 3: 10}[enemy_type]
        self.color = {1: 'purple', 2: 'blue', 3: 'green'}[enemy_type]

    def dump_dict(self) -> dict:
        return { 'x': self.row, 'y': self.col, 'color': self.color }
    
    @classmethod
    def from_dict(cls, enemy_dict: dict):
        return cls(
            enemy_dict['x'], enemy_dict['y'],
            {'purple': 1, 'blue': 2, 'green': 3}[enemy_dict['color']]
        )


class SpaceInvaders:
    def __init__(self, enemy_rows, enemy_cols, pad_col_num, enemy_area_rows, enemies=None, ship_col=None):
        assert enemy_rows in [3, 4, 5], "enemy_rows should be 3, 4 or 5"

        pygame.init()
        self.ENEMY_WIDTH = 47
        self.ENEMY_HEIGHT = 40
        self.SHIP_WIDTH = 50
        self.SHIP_HEIGHT = 42

        self.enemy_area_rows = enemy_area_rows
        self.total_columns = enemy_cols + 2 * pad_col_num
        self.enemy_cols = enemy_cols
        self.enemy_rows = enemy_rows

        self.screen_width = LEFT_BORDER + ENEMY_SPACING_X * (enemy_cols + 2 * pad_col_num)
        self.screen_height = (enemy_area_rows + 1) * ENEMY_MOVE_DOWN + TOP_BORDER
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.enemies: list[Enemy] = []
        self.enemies_on_row, self.enemies_on_col = {}, {}
        self.enemy_col_ids, self.enemy_row_ids = [], []
        
        img_path = "assets"
        img_type_num = random.randint(1, 2)
        self.enemy_images = {
            1: pygame.transform.scale(
                pygame.image.load(os.path.join(img_path, f"enemy1_{img_type_num}.png")), (self.ENEMY_WIDTH, self.ENEMY_HEIGHT)
            ),
            2: pygame.transform.scale(
                pygame.image.load(os.path.join(img_path, f"enemy2_{img_type_num}.png")), (self.ENEMY_WIDTH, self.ENEMY_HEIGHT)
            ),
            3: pygame.transform.scale(
                pygame.image.load(os.path.join(img_path, f"enemy3_{img_type_num}.png")), (self.ENEMY_WIDTH, self.ENEMY_HEIGHT)
            )
        }
        self.ship_image = pygame.transform.scale(
            pygame.image.load(os.path.join(img_path, "ship_orange.png")), (self.SHIP_WIDTH, self.SHIP_HEIGHT)
        )

        if enemies is not None:
            self.enemies = enemies
        else:
            self._generate_enemies()
        for enemy in self.enemies:
            if enemy.row not in self.enemy_row_ids:
                self.enemy_row_ids.append(enemy.row)
            if enemy.col not in self.enemy_col_ids:
                self.enemy_col_ids.append(enemy.col)
            self.enemies_on_row.setdefault(enemy.row, [])
            self.enemies_on_row[enemy.row].append(enemy)
            self.enemies_on_col.setdefault(enemy.col, [])
            self.enemies_on_col[enemy.col].append(enemy)
        
        if ship_col is not None:
            self.ship_x = ship_col
        else:
            self._generate_ship_position()

    def _generate_enemies(self):
        self.enemies.clear()
        positions = []
        self.start_r = random.randint(1, self.enemy_area_rows - self.enemy_rows + 1)
        self.start_c = random.randint(1, self.total_columns - self.enemy_cols + 1)
        for c in range(self.start_c, self.start_c + self.enemy_cols):
            tmp = list(range(self.start_r, self.start_r + self.enemy_rows + 1))
            if len(tmp) == 4:
                weights = [0.1, 0.2, 0.3, 0.5]
            elif len(tmp) == 5:
                weights = [0.1, 0.1, 0.2, 0.2, 0.4]
            elif len(tmp) == 6:
                weights = [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]
            high = random.choices(tmp, weights=weights)[0]
            for r in range(self.start_r, high):
                positions.append((r, c))

        for r, c in positions:
            if r == self.start_r:
                enemy_type = 1
            elif self.enemy_rows == 3 and r == self.start_r + 1 or self.enemy_rows == 4 and r == self.start_r + 1 or self.enemy_rows == 5 and r <= self.start_r + 2:
                enemy_type = 2
            else:
                enemy_type = 3
            enemy = Enemy(r, c, enemy_type)
            self.enemies.append(enemy)

    def _generate_ship_position(self):
        wo_enemy_col_ids = [c for c in range(1, self.total_columns + 1) if c not in self.enemy_col_ids]
        self.ship_x = random.choices(
            (random.choice(self.enemy_col_ids), random.choice(wo_enemy_col_ids)),
            weights=[0.8, 0.2]
        )[0]

    @classmethod
    def from_dict(cls, space_invaders_dict: dict):
        enemy_rows = space_invaders_dict['enemy_rows']
        enemy_cols = space_invaders_dict['enemy_cols']
        enemy_area_rows = space_invaders_dict['enemy_area_rows']
        pad_col_num = (space_invaders_dict['total_cols'] - enemy_cols) // 2
        enemies = [Enemy.from_dict(enemy_dict) for enemy_dict in space_invaders_dict['enemies']]
        ship_col = space_invaders_dict['ship_col']
        game = cls(enemy_rows, enemy_cols, pad_col_num, enemy_area_rows, enemies, ship_col)
        return game

    def dump_dict(self) -> dict:
        ret = {
            "enemy_rows": self.enemy_rows,
            "enemy_cols": self.enemy_cols,
            "enemy_area_rows": self.enemy_area_rows,
            "total_cols": self.total_columns,
            "ship_col": self.ship_x,
            "enemies": [enemy.dump_dict() for enemy in self.enemies],
        }
        return ret

    def weight_select_col(self, favar_weight=0.8):
        return random.choices(
            (random.choice(self.enemy_col_ids), random.choice([c for c in range(1, self.total_columns + 1) if c not in self.enemy_col_ids])),
            weights=[favar_weight, 1 - favar_weight]
        )[0]
    
    def weight_select_row(self, faver_weight=0.8):
        return random.choices(
            (random.choice(self.enemy_row_ids), random.choice([r for r in range(1, self.enemy_area_rows + 1) if r not in self.enemy_row_ids])),
            weights=[faver_weight, 1 - faver_weight]
        )[0]
    
    def weight_select_col_to_move_to(self, cur_col, favar_weight=0.8):
        return random.choices(
            (
                random.choice([c for c in self.enemy_col_ids if c != cur_col]) if len(self.enemy_col_ids) > 1 else cur_col,
                random.choice([c for c in range(1, self.total_columns + 1) if c not in self.enemy_col_ids])
            ),
            weights=[favar_weight, 1 - favar_weight]
        )[0]
        
    def coor_to_pixel_pos(self, row, col):
        x = (col - 1) * ENEMY_SPACING_X + LEFT_BORDER + ENEMY_SPACING_X // 2 - self.ENEMY_WIDTH // 2
        y = (row - 1) * ENEMY_MOVE_DOWN + TOP_BORDER + ENEMY_MOVE_DOWN // 2 - self.ENEMY_HEIGHT // 2
        return x, y

    def draw_scene(self, with_grid_line=True, output_path="game_scene.png"):
        if random.random() < 0.5:
            self.screen.fill((0, 0, 0))
        else:
            background = pygame.transform.scale(
                pygame.image.load("assets/background.jpg"), (self.screen_width, self.screen_height)
            )
            background.set_alpha(random.randint(150, 255))
            self.screen.blit(background, (0, 0))
        
        if with_grid_line:
            for c in range(1, self.total_columns + 1):
                line_x = (c - 1) * ENEMY_SPACING_X + LEFT_BORDER
                pygame.draw.line(self.screen, (255, 255, 255), (line_x, 0), (line_x, self.screen_height), 1)
            for r in range(1, self.enemy_area_rows + 2):
                line_y = (r - 1) * ENEMY_MOVE_DOWN + TOP_BORDER
                pygame.draw.line(self.screen, (255, 255, 255), (0, line_y), (self.screen_width, line_y), 1)

        font = pygame.font.SysFont(None, 50)
        color = random.choice(list(color_RGB.values()))
        for c in range(1, self.total_columns + 1):
            label = font.render(str(c), True, color)
            lx = (c - 1) * ENEMY_SPACING_X + LEFT_BORDER + (ENEMY_SPACING_X // 2) - (label.get_width() // 2)
            self.screen.blit(label, (lx, 15))
        for r in range(1, self.enemy_area_rows + 2):
            label = font.render(str(r), True, color)
            ly = (r - 1) * ENEMY_MOVE_DOWN + TOP_BORDER + (ENEMY_MOVE_DOWN // 2) - (label.get_height() // 2)
            self.screen.blit(label, (11, ly))
        
        for enemy in self.enemies:
            px, py = self.coor_to_pixel_pos(enemy.row, enemy.col)
            self.screen.blit(self.enemy_images[enemy.type], (px, py))
        
        ship_y = self.enemy_area_rows + 1
        ship_pixel_x, ship_pixel_y = self.coor_to_pixel_pos(ship_y, self.ship_x)
        # self.screen.blit(self.ship_image, (ship_pixel_x, BASE_SHIP_Y - (8 - self.enemy_area_rows) * self.SHIP_HEIGHT))
        self.screen.blit(self.ship_image, (ship_pixel_x, ship_pixel_y))
        
        pygame.image.save(self.screen, output_path)
        
        if self.screen_width * self.screen_height > 640 * 480:
            scale = math.sqrt(640 * 480 / (self.screen_width * self.screen_height))
            img = Image.open(output_path)
            img.thumbnail((int(img.width * scale), int(img.height * scale)))
            img.save(output_path)   

    def destroy_enemy(self, row, col):
        for enemy in self.enemies:
            if enemy.row == row and enemy.col == col:
                self.enemies.remove(enemy)
                self.enemies_on_row[row].remove(enemy)
                if len(self.enemies_on_row[row]) == 0:
                    del self.enemies_on_row[row]
                self.enemies_on_col[col].remove(enemy)
                if len(self.enemies_on_col[col]) == 0:
                    del self.enemies_on_col[col]
                break
    
    def leftmost_enemy_col(self):
        return min(self.enemies_on_col.keys()) 
    def rightmost_enemy_col(self):
        return max(self.enemies_on_col.keys())
    
    def left_distance_to_border(self):
        return self.leftmost_enemy_col() - 1
    def right_distance_to_border(self):
        return self.total_columns - self.rightmost_enemy_col()


if __name__ == '__main__':
    game = SpaceInvaders(enemy_rows=4, enemy_cols=6, pad_col_num=3, enemy_area_rows=8)
    game.draw_scene()