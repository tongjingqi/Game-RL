from utils.constants import (
    MINECRAFT_RULE_GENERAL,
    SCENERY_RECOG_TASK,
    CROSS_RIVER_TASK,
    CLIME_OBTAIN_TASK,
    OBTAIN_TASK
)
from utils.gen_chocies import (
    form_options,
    enumerate_items
)
from ursina import *
from PIL import Image
from typing import List, Tuple, Dict, Optional
import random
from pathlib import Path
import numpy as np
import json
import os

class MinecraftQAGenerator:
    def __init__(self, output_dir='minecraft_dataset', space_ub: Tuple[int, int, int] = (5, 5, 5)):
        self.app = Ursina()
        self.sample_count = 0
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'states'), exist_ok=True)
        
        self.space_ub = space_ub
        self.ALL_SCENERY_TYPES = {
            'stone': {'name': 'Stone', 'texture': 'stone'},
            'brick': {'name': 'Brick', 'texture': 'bricks'},
            'gold_ore': {'name': 'Gold Ore', 'texture': 'gold_ore'},
            'diamond_ore': {'name': 'Diamond Ore', 'texture': 'diamond_ore'},
            'tnt': {'name': 'TNT', 'texture': 'tnt'},
            'pumpkin': {'name': 'Pumpkin', 'texture': 'pumpkin'},
            'ladder': {'name': 'Ladder', 'texture': 'ladder'},
            'tree': {'name': 'Tree', 'texture': None},
            'river': {'name': 'River', 'texture': None},
            'lava': {'name': 'Lava', 'texture': None}
        }
        self.CANDIDATE_SCENERY_TYPES = self.ALL_SCENERY_TYPES.copy()
        del self.CANDIDATE_SCENERY_TYPES['tree']
        del self.CANDIDATE_SCENERY_TYPES['stone']

        self.sky = None
        self.sceneries: Dict[str, List[Tuple]] = {}
        self.entities: List[Entity] = []
        camera.position = (10, 10, -10)
        camera.look_at(Vec3(0, 0, 0))
        camera.parent = scene

        self.occupied_positions = set()
        self.centroid_positions = set()
        # DirectionalLight(parent=scene, y=2, z=3, shadows=True)
        # AmbientLight(parent=scene, color=color.rgba(100, 100, 100, 0.1))
        self.texture_path = Path('assets/textures/block')
        if not self.texture_path.exists():
            raise FileNotFoundError(f"Texture directory not found: {self.texture_path}")
        self.textures = {}
        self._load_textures()

        self.create_cube_funcs = {
            'brick': self._create_brick,
            'gold_ore': self._create_gold_ore,
            'diamond_ore': self._create_diamond_ore,
            'tnt': self._create_tnt,
            'pumpkin': self._create_pumpkin,
            'ladder': self._create_ladder,
            'river': self._create_river,
            'lava': self._create_lava
        }

    def _load_textures(self):
        texture_files = {
            'stone': ['stone.png'],
            'brick': ['bricks.png'],
            'gold_ore': ['gold_ore.png'],
            'diamond_ore': ['diamond_ore.png'],
            'tnt': ['tnt_top.png', 'tnt_bottom.png', 'tnt_side.png'],
            'pumpkin': ['pumpkin_top.png', 'pumpkin_side.png'],
            'ladder': ['ladder.png']
        }
        for _, files in texture_files.items():
            for file in files:
                texture_name = file.split('.')[0]
                texture_path = str(self.texture_path / file)
                if texture_name == 'bricks':
                    self.textures['brick'] = load_texture(texture_path)
                    continue
                self.textures[texture_name] = load_texture(texture_path)
        
        # read asset/texture/block/lava_still.png into an Image, which is 64*1280
        lava_still_path = self.texture_path / 'lava_still.png'
        lava_still_img = Image.open(lava_still_path)
        # cut the top 64*64 part of the image into a new image
        lava_still_top_img = lava_still_img.crop((0, 0, 64, 64))
        self.textures['lava_still_top'] = Texture(lava_still_top_img)

    def _surround_with_quads(self, position: Tuple[int, int, int], texture: Texture, delta=0.5):
        x, y, z = position
        self.entities.append(Entity(model='quad', texture=texture, position=(x - delta, y, z), rotation_y=90, double_sided=True))
        self.entities.append(Entity(model='quad', texture=texture, position=(x + delta, y, z), rotation_y=90, double_sided=True))
        self.entities.append(Entity(model='quad', texture=texture, position=(x, y, z + delta), rotation_y=180, double_sided=True))
        self.entities.append(Entity(model='quad', texture=texture, position=(x, y, z - delta), double_sided=True))
    def _top_with_quad(self, position: Tuple[int, int, int], texture: Texture, delta=0.5):
        x, y, z = position
        self.entities.append(Entity(model='quad', texture=texture, position=(x, y + delta, z), rotation_x=90))
    def _bottom_with_quad(self, position: Tuple[int, int, int], texture: Texture, delta=0.5):
        x, y, z = position
        self.entities.append(Entity(model='quad', texture=texture, position=(x, y - delta, z), rotation_x=90))

    def _is_position_occupied(self, pos: Tuple[int, int, int], size: Tuple[int, int, int]) -> bool:
        x, y, z = pos
        width, height, depth = size
        for dx in range(width):
            for dy in range(height):
                for dz in range(depth):
                    check_pos = (x + dx, y + dy, z + dz)
                    if check_pos in self.occupied_positions:
                        return True
        return False
    def _mark_position_occupied(self, pos: Tuple[int, int, int], size: Tuple[int, int, int], count_in_centroid=True):
        x, y, z = pos
        width, height, depth = size
        for dx in range(width):
            for dy in range(height):
                for dz in range(depth):
                    self.occupied_positions.add((x + dx, y + dy, z + dz))
                    if count_in_centroid:
                        self.centroid_positions.add((x + dx, y + dy, z + dz))
    def _find_valid_position(self, size: Tuple[int, int, int], allow_stack=False, range_constraint: Optional[Tuple[Tuple[int,int], Tuple[int,int], Tuple[int,int]]] = None) -> Tuple[int, int, int]:
        avail = []
        if allow_stack:
            for x in range(-self.space_ub[0], self.space_ub[0] + 1):
                for y in range(0, self.space_ub[1] + 1):
                    for z in range(-self.space_ub[2], self.space_ub[2] + 1):
                        if (y == 0 or self._is_position_occupied((x, y-1, z), (1, 1, 1))) and not self._is_position_occupied((x, y, z), size):
                            avail.append((x, y, z))
        else:
            for x in range(-self.space_ub[0], self.space_ub[0] + 1):
                for z in range(-self.space_ub[2], self.space_ub[2] + 1):
                    if not self._is_position_occupied((x, 0, z), size):
                        avail.append((x, 0, z))
        
        if range_constraint:
            x_range, y_range, z_range = range_constraint
            avail = [pos for pos in avail if x_range[0] <= pos[0] <= x_range[1] and y_range[0] <= pos[1] <= y_range[1] and z_range[0] <= pos[2] <= z_range[1]]
        
        assert avail, "无法找到有效的放置位置"
        return random.choice(avail)
    
    def _place_stone(self, position: Tuple[int, int, int]):
        self.entities.append(Entity(model='cube', texture=self.textures['stone'], position=position))
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['stone'].append(self.entities[-1].position)
    def _place_brick(self, position: Tuple[int, int, int]):
        self.entities.append(Entity(model='cube', texture=self.textures['brick'], position=position))
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['brick'].append(self.entities[-1].position)
    def _place_gold_ore(self, position: Tuple[int, int, int]):
        self.entities.append(Entity(model='cube', texture=self.textures['gold_ore'], position=position))
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['gold_ore'].append(self.entities[-1].position)
    def _place_diamond_ore(self, position: Tuple[int, int, int]):
        self._mark_position_occupied(position, (1, 1, 1))
        self.entities.append(Entity(model='cube', texture=self.textures['diamond_ore'], position=position))
        self.sceneries['diamond_ore'].append(self.entities[-1].position) 
    def _place_tnt(self, position: Tuple[int, int, int]):
        self._top_with_quad(position, self.textures['tnt_top'])
        self._bottom_with_quad(position, self.textures['tnt_bottom'])
        self._surround_with_quads(position, self.textures['tnt_side'])
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['tnt'].append(position)
    def _place_pumpkin(self, position: Tuple[int, int, int]):
        self._top_with_quad(position, self.textures['pumpkin_top'])
        self._bottom_with_quad(position, self.textures['pumpkin_side'])
        self._surround_with_quads(position, self.textures['pumpkin_side'])
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['pumpkin'].append(position)
    def _place_ladder(self, position: Tuple[int, int, int]):
        self.entities.append(Entity(model='cube', texture=self.textures['stone'], position=position))
        x, y, z = position
        self._surround_with_quads((x, y, z), self.textures['ladder'], delta=0.51)
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['ladder'].append(position)
    def _place_river(self, position: Tuple[int, int, int], dir_vector: Tuple[int, int, int], width: int, texture=None):
        assert dir_vector in [(1, 0, 0), (0, 0, 1)], "河流只能是水平或垂直的"
        x, y, z = position
        dx, dy, dz = dir_vector
        length = 50
        for t in range(-length//2, length//2 + 1):
            for w in range(-((width-1)//2), width//2 + 1):
                self._mark_position_occupied((x + t*dx + w*dz, -1, z + t*dz + w*dx), (1, 1, 1), count_in_centroid=False)
                self._mark_position_occupied((x + t*dx + w*dz, 0, z + t*dz + w*dx), (1, 1, 1), count_in_centroid=False)
                self.entities.append(Entity(model='cube', color=color.azure, texture=texture, position=(x + t*dx + w*dz, -1, z + t*dz + w*dx), scale=(1, 0.7, 1)))
                self.sceneries['river'].append((x + t*dx + w*dz, -1, z + t*dz + w*dx))
        self._mark_position_occupied(position, (1, 1, 1), count_in_centroid=True)
    def _place_lava(self, position: Tuple[int, int, int]):
        self.entities.append(Entity(model='cube', color=color.yellow, position=position, scale=(1, 0.7, 1), texture=self.textures['lava_still_top']))
        self._mark_position_occupied(position, (1, 1, 1))
        self.sceneries['lava'].append(position)
    
    def _create_stone(self) -> Entity:
        position = self._find_valid_position((1, 1, 1))
        self._place_stone(position)
    def _create_brick(self): 
        two_blocks = random.choice([True, False])
        if two_blocks:
            is_vertical = random.choice([True, False])
            if is_vertical:
                dv = (0, 1, 0)
            else:
                dv = random.choice([(1, 0, 0), (0, 0, 1)])
            position = self._find_valid_position((1+dv[0], 1, 1+dv[2]))
            self._place_brick(position)
            self._place_brick((position[0]+dv[0], position[1], position[2]+dv[2]))
        else:
            position = self._find_valid_position((1, 1, 1))
            self._place_brick(position)
    def _create_gold_ore(self):
        two_blocks = random.choice([True, False])
        if two_blocks:
            is_vertical = random.choice([True, False])
            if is_vertical:
                dv = (0, 1, 0)
            else:
                dv = random.choice([(1, 0, 0), (0, 0, 1)])
            position = self._find_valid_position((1+dv[0], 1, 1+dv[2]))
            self._place_gold_ore(position)
            self._place_gold_ore((position[0]+dv[0], position[1], position[2]+dv[2]))
        else:
            position = self._find_valid_position((1, 1, 1))
            self._place_gold_ore(position)
    def _create_diamond_ore(self):
        two_blocks = random.choice([True, False])
        if two_blocks:
            is_vertical = random.choice([True, False])
            if is_vertical:
                dv = (0, 1, 0)
            else:
                dv = random.choice([(1, 0, 0), (0, 0, 1)])
            position = self._find_valid_position((1+dv[0], 1, 1+dv[2]))
            self._place_diamond_ore(position)
            self._place_diamond_ore((position[0]+dv[0], position[1], position[2]+dv[2]))
        else:
            position = self._find_valid_position((1, 1, 1))
            self._place_diamond_ore(position)
    def _create_tnt(self):
        position = self._find_valid_position((1, 1, 1))
        self._place_tnt(position)
    def _create_pumpkin(self):
        position = self._find_valid_position((1, 1, 1))
        self._place_pumpkin(position)
    def _create_ladder(self):
        is_two_blocks = True
        if is_two_blocks:
            position = self._find_valid_position((1, 2, 1))
            self.entities.append(Entity(model='cube', texture=self.textures['stone'], position=position))
            self.entities.append(Entity(model='cube', texture=self.textures['stone'], position=(position[0], position[1] + 1, position[2])))
            self._place_ladder(position)
            self._place_ladder((position[0], position[1] + 1, position[2]))
        else:
            position = self._find_valid_position((1, 1, 1))
            self.entities.append(Entity(model='cube', texture=self.textures['stone'], position=position))
            self._place_ladder(position)
            
    def _create_river(self, is_x: bool):
        width = random.randint(1, 3)
        texture = random.choice(['white_cube', None])
        if is_x:
            z = random.randint(-self.space_ub[2], self.space_ub[2])
            self._place_river((0, 0, z), (1, 0, 0), width, texture=texture)
        else:
            x = random.randint(-self.space_ub[0], self.space_ub[0])
            self._place_river((x, 0, 0), (0, 0, 1), width, texture=texture)
    def _create_lava(self):
        is_two_blocks = random.choice([True, False])
        if is_two_blocks:
            dv = random.choice([(1, 0, 0), (0, 0, 1)])
            avail = []
            for x in range(-self.space_ub[0], self.space_ub[0] + 1):
                for z in range(-self.space_ub[2], self.space_ub[2] + 1):
                    if not self._is_position_occupied((x, -1, z), (dv[0]+1, 1, dv[2]+1)):
                        avail.append((x, -1, z))
            position = random.choice(avail)
            self._place_lava(position)
            self._place_lava((position[0]+dv[0], position[1], position[2]+dv[2]))
        else:
            avail = []
            for x in range(-self.space_ub[0], self.space_ub[0] + 1):
                for z in range(-self.space_ub[2], self.space_ub[2] + 1):
                    if not self._is_position_occupied((x, -1, z), (1, 1, 1)):
                        avail.append((x, -1, z))
            position = random.choice(avail)
            self._place_lava(position)
    
    def _create_ground(self, size=50, use_white_cube=False, ban_white_cube=False):
        if use_white_cube and ban_white_cube:
            raise ValueError("Cannot use white cube and ban white cube at the same time")
        if random.random() < 0.5:
            texture, c = 'grass', random.choice([color.brown, color.green])
        else:
            texture = 'white_cube' if use_white_cube else random.choice(['white_cube', None]) if not ban_white_cube else None
            c = color.random_color()
        for x in range(-size//2, size//2):
            for z in range(-size//2, size//2):
                if self._is_position_occupied((x, -1, z), (1, 1, 1)):
                    continue
                self.entities.append(Entity(model='cube', texture=texture, position=(x, -1, z), scale=(1, 1, 1), color=c))
    def _create_land(self, size=50):
        texture, c = 'grass', color.green
        for x in range(-size//2, size//2):
            for z in range(-size//2, size//2):
                if self._is_position_occupied((x, -1, z), (1, 1, 1)):
                    continue
                self.entities.append(Entity(model='cube', texture=texture, position=(x, -1, z), scale=(1, 1, 1), color=c))
                self._mark_position_occupied((x, -1, z), (1, 1, 1), count_in_centroid=False)
    
    def _clear_scene(self):
        if self.sky:
            destroy(self.sky)
        for entity in self.entities:
            destroy(entity)
        self.entities.clear()
        self.occupied_positions.clear()
        self.centroid_positions.clear()
        for scenery_type in self.ALL_SCENERY_TYPES.keys():
            self.sceneries[scenery_type] = []
    
    def gen_scenery_qa(self, show_labels: bool = False) -> Dict:
        self._clear_scene()
        num_scenery = random.randint(3, 5)
        self.sky = Sky() if random.random() < 0.5 else None
        selected_scenery = random.sample(list(self.CANDIDATE_SCENERY_TYPES.keys()), num_scenery)
        has_water_feature = 'river' in selected_scenery or 'lava' in selected_scenery
        has_ground = has_water_feature or random.choice([True, False])
        has_ground = True
        self.has_ground = has_ground
        if 'river' in selected_scenery:
            self._create_river(is_x=random.choice([True, False]))
        if 'lava' in selected_scenery:
            self._create_lava()
        if has_ground:
            self._create_ground()
        for i, scenery_type in enumerate(selected_scenery):
            if scenery_type == 'river' or scenery_type == 'lava':
                continue
            self.create_cube_funcs[scenery_type]()

        if show_labels:
            for scenery_type, positions in self.sceneries.items():
                if not positions:
                    continue
                x_mean = np.mean([pos[0] for pos in positions])
                z_mean = np.mean([pos[2] for pos in positions])
                y_max = np.max([pos[1] for pos in positions])
                y = y_max + 1
                print('Adding label:', scenery_type, (x_mean, y, z_mean))
                self._add_label((x_mean, y, z_mean), self.CANDIDATE_SCENERY_TYPES[scenery_type]['name'])
        
        self._adjust_camera(dis_range=(18, 21), phi_range=(40, 60))
        idx, options = self._generate_options(selected_scenery)
        selected_scenery_names = [self.CANDIDATE_SCENERY_TYPES[s]['name'] for s in selected_scenery]
        selected_scenery_names = [name.lower() if name != 'TNT' else name for name in selected_scenery_names]
        question = MINECRAFT_RULE_GENERAL + SCENERY_RECOG_TASK + form_options(options)
        analysis = f"Looking carefully at the scene, we can see:\n"
        # analysis = f"Looking carefully at the scene, we can see {enumerate_items(selected_scenery_names, 'and')} in the scene. Therefore, the correct option number is {ans+1}."
        for s in selected_scenery_names:
            if s == 'brick':
                analysis += '- red-colored bricks'
            elif s == 'gold ore':
                analysis += '- block embedded with gold-colored stone, which is gold ore'
            elif s == 'diamond ore':
                analysis += '- block embedded with blue-green stone, which is diamond ore'
            elif s == 'TNT':
                analysis += '- red block resembling dynamite'
            elif s == 'pumpkin':
                analysis += '- yellow block resembling a pumpkin'
            elif s == 'ladder':
                analysis += '- wooden ladder attached to block(s)'
            elif s == 'river':
                analysis += '- a blue river spanning the screen'
            elif s == 'lava':
                analysis += '- lava consisting of orange and yellow'
            else:
                raise ValueError(f"Unknown scenery name: {s}")
            analysis += '\n'
        analysis += f'\nTo sum up, the scene contains {enumerate_items(selected_scenery_names, "and")}. Therefore, the correct option number is {idx+1}.'
        self.sample_count += 1
        return {
            'data_id': f'minecraft-{self.sample_count:05d}-scenery_recog',
            'qa_type': 'StateInfo',
            'question_id': 1,
            'question_description': 'Ask to recognize the sceneries in the scene.',
            'image': self._take_screenshot(),
            'state': self._save_state({'sceneries': selected_scenery_names}),
            'plot_level': {3: 'Easy', 4: 'Medium', 5: 'Hard'}[num_scenery],
            'qa_level': 'Easy',
            'question': question,
            'answer': idx+1,
            'analysis': analysis,
            'options': options,
        }
    
    def _create_scenery(self, scenery_type: str, position: Tuple[int, int, int]) -> List[Entity]:
        if scenery_type == 'stone':
            return [self._create_stone(position)]
        elif scenery_type == 'brick':
            return self._create_brick(position, random.choice([True, False]))
        elif scenery_type == 'gold_ore':
            return self._create_ore(position, 'gold_ore', random.choice([True, False]))
        elif scenery_type == 'diamond_ore':
            return self._create_ore(position, 'diamond_ore', random.choice([True, False]))
        elif scenery_type == 'tnt':
            return [self._create_tnt(position)]
        elif scenery_type == 'pumpkin':
            return [self._create_pumpkin(position)]
        elif scenery_type == 'ladder':
            return self._create_ladder(position, random.randint(1, 2))
        elif scenery_type == 'tree':
            return self._create_tree(position)
        elif scenery_type == 'river':
            return self._create_river(position, random.choice([True, False]))
        elif scenery_type == 'lava':
            return self._create_lava(position, random.randint(1, 2))
    
    def _add_label(self, position: Tuple[int, int, int], text: str):
        x, y, z = position
        Text(text=text, position=(x, y, z), origin=(0, 0), background=True)    

    def _overlook_center(self, center: Tuple[int, int, int], dis_range: Tuple, phi_range: Tuple):
        distance = random.uniform(*dis_range)
        phi = random.uniform(*phi_range)
        theta = random.uniform(0, 360)
        camera.position = (
            center[0] + distance * np.sin(np.radians(phi)) * np.cos(np.radians(theta)),
            center[1] + distance * np.cos(np.radians(phi)),
            center[2] + distance * np.sin(np.radians(phi)) * np.sin(np.radians(theta))
        )
        camera.look_at(Vec3(*center), up=Vec3(0, 1, 0))
        
    def _adjust_camera(self, dis_range: Tuple = (13, 20), phi_range: Tuple = (40, 70)):
        positions = list(self.centroid_positions)
        if not positions:
            return
        center = np.mean(positions, axis=0)
        self._overlook_center(center, dis_range, phi_range)

    def _generate_options(self, correct_scenery: List[str], num_options=8) -> Tuple[int, List[str]]:
        options = []
        correct_names = [self.CANDIDATE_SCENERY_TYPES[s]['name'] for s in correct_scenery]
        correct_option = ', '.join(sorted(correct_names))
        options.append(correct_option)
        all_scenery = list(self.ALL_SCENERY_TYPES.keys())
        if 'stone' in all_scenery:
            all_scenery.remove('stone')
        while len(options) < num_options:
            wrong_scenery = random.sample(all_scenery, len(correct_scenery))
            wrong_names = [self.ALL_SCENERY_TYPES[s]['name'] for s in wrong_scenery]
            wrong_option = ', '.join(sorted(wrong_names))
            if wrong_option not in options:
                options.append(wrong_option)
        random.shuffle(options)
        idx = options.index(correct_option)
        if random.random() < 0.5:
            for i in range(len(options)):
                options[i] = options[i].split(', ')
                random.shuffle(options[i])
                options[i] = ', '.join(options[i])
        return idx, options
    
    def gen_cube_count_qa(self) -> Dict:
        self._clear_scene()
        self.sky = Sky() if random.random() < 0.5 else None
        x_dim = random.randint(2, 6)
        y_dim = random.randint(1, 4)
        z_dim = random.randint(2, 6)
        pos = self._find_valid_position((x_dim, y_dim, z_dim))
        if random.choice([True, False]):
            self._create_ground(ban_white_cube=True)
        base_x, base_y, base_z = pos
        block_color = color.random_color()
        for dx in range(x_dim):
            for dy in range(y_dim):
                for dz in range(z_dim):
                    block_pos = (base_x + dx, base_y + dy, base_z + dz)
                    self.entities.append(Entity(model='cube', texture='white_cube',color=block_color,position=block_pos))
                    self._mark_position_occupied(block_pos, (1, 1, 1))
        self._adjust_camera(dis_range=(16, 23))
        question = MINECRAFT_RULE_GENERAL + 'How many cubes are there in total in the scene?'
        answer = x_dim * y_dim * z_dim
        analysis = f'From the scene we can easily see that the cubes form a big cuboid. Looking at the top of it, we know that the length and the width are {x_dim} and {z_dim} respectively. Besides, we can see that the height is {y_dim}. Therefore, the total number of cubes is {x_dim} x {z_dim} x {y_dim} = {answer}. The answer is {answer}.'
        if answer <= 30:
            plot_level = 'Easy'
        elif answer <= 70:
            plot_level = 'Medium'
        else:
            plot_level = 'Hard'
        self.sample_count += 1
        return {
            'data_id': f'minecraft-{self.sample_count:05d}-cube_count',
            'qa_type': 'StateInfo',
            'question_id': 2,
            'question_description': 'Ask how many cubes are there in total.',
            'image': self._take_screenshot(),
            'state': self._save_state({
                'x_blocks': x_dim,
                'y_blocks': y_dim,
                'z_blocks': z_dim,
            }),
            'plot_level': plot_level,
            'qa_level': 'Medium',
            'question': question,
            'answer': answer,
            'analysis': analysis
        }

    def _take_screenshot(self) -> str:
        self.app.step()
        img_path = os.path.join('images', f'{self.sample_count:05d}.png')
        self.app.screenshot(os.path.join(self.output_dir, img_path), defaultFilename=False)
        return img_path
    def _save_state(self, state = []):
        json_path = os.path.join('states', f'{self.sample_count:05d}.json')
        with open(os.path.join(self.output_dir, json_path), 'w') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        return json_path
        
    def gen_cross_fluid_qa(self) -> Dict:
        """
        Ask how many blocks are minecraft to cross the fluid by bridging over it.
        """
        self._clear_scene()
        self.sky = Sky() if random.random() < 0.5 else None
        is_x = random.choice([True, False])
        fluid_width = random.randint(1, 4)
        if is_x:
            z = random.randint(-self.space_ub[2], self.space_ub[2])
            self._place_river((0, 0, z), (1, 0, 0), fluid_width, texture='white_cube')
        else:
            x = random.randint(-self.space_ub[0], self.space_ub[0])
            self._place_river((x, 0, 0), (0, 0, 1), fluid_width, texture='white_cube')
        dis = random.randint(1, 3)
        postion = (0, -1, z - fluid_width//2 - dis) if is_x else (x - fluid_width//2 - dis, -1, 0)
        self.entities.append(Entity(model='cube', color=color.red, position=postion))
        self._mark_position_occupied(postion, (1, 1, 1), count_in_centroid=True)
        self._create_land()
        self._adjust_camera(dis_range=(17, 22))
        question = MINECRAFT_RULE_GENERAL + CROSS_RIVER_TASK
        answer = fluid_width
        analysis = f'Based on the rules, the player can build a bridge on the river by placing blocks in it. To have the minimum number of blocks, the bridge should just be vertical to the river bank and the answer is the width of the river. We can see the width of the river is {fluid_width}. Therefore, the answer is {fluid_width}.'
        self.sample_count += 1
        return {
            'data_id': f'minecraft-{self.sample_count:05d}-cross_river',
            'qa_type': 'TransitionPath',
            'question_id': 3,
            'question_description': 'Ask the minimum number of blocks needed to cross the river.',
            'image': self._take_screenshot(),
            'state': self._save_state({
                'river_direction': 'x' if is_x else 'z',
                'river_width': fluid_width,
                'player_position': list(postion)
            }),
            'plot_level': 'Easy' if fluid_width <= 2 else 'Medium' if fluid_width == 3 else 'Hard',
            'qa_level': 'Medium',
            'question': question,
            'answer': answer,
            'analysis': analysis
        }
    
    def gen_climb_qa(self) -> Dict:
        """
        Ask how many blocks are needed to build to reach a pumpkin.
        The total height must allow player's upper body (2 blocks tall) 
        to be at least level with the pumpkin.
        """
        self._clear_scene()
        self.sky = Sky() if random.random() < 0.5 else None
        self._create_ground(use_white_cube=True)
        x = random.randint(-self.space_ub[0], self.space_ub[0])
        z = random.randint(-self.space_ub[2], self.space_ub[2])
        num_stones = random.randint(0, 4)
        with_ladder = random.choices([True, False], weights=[0.3, 0.7])[0]
        c = color.random_color()
        for y in range(num_stones):
            self.entities.append(Entity(model='cube', texture='white_cube', color=c, position=(x, y, z)))
            if with_ladder:
                self._place_ladder((x, y, z))
            self._mark_position_occupied((x, y, z), (1, 1, 1))
        
        block = random.choice(['pumpkin', 'gold ore', 'diamond ore'])
        {'pumpkin': self._place_pumpkin, 'gold ore': self._place_gold_ore, 'diamond ore': self._place_diamond_ore}[block]((x, num_stones, z))

        # Calculate required blocks (pumpkin_height - player_height)
        # Player needs to reach height of num_stones + 1 (pumpkin)
        # Player is 2 blocks tall, so subtract 2 from required height
        required_blocks = max(0, (num_stones + 1) - 2) if not with_ladder else 0
        self._adjust_camera()
        question = MINECRAFT_RULE_GENERAL + CLIME_OBTAIN_TASK.format(block=block)
        if num_stones == 0:
            analysis = f'The {block} is on the ground, so the player does not need to build any blocks to reach it. So the answer is 0.'
        elif with_ladder:
            analysis = f"From the image we can see that ladders are attached to the block(s) under the {block}. The player can climb the ladders to reach the {block} if needed. Therefore, he doesn't need to consume any blocks. So the answer is 0."
        elif num_stones == 1:
            analysis = f'From the image we can see that there are no ladders, yet there is only one block under the {block}. Thus the {block} is at a height of 2 blocks, same as the upper body of the player. Therefore, the player does not need to build any blocks to reach the {block}. So the answer is 0.'
        else:
            analysis = f'From the image we can see that there are no ladders, and the {block}, on the top of {num_stones} block(s), is at a height of {num_stones + 1} block(s). The player is 2 blocks tall. Therefore, the player needs to build {num_stones + 1} - 2 = {required_blocks} block(s) under his feet to reach the {block}. The answer is {required_blocks}.'
        self.sample_count += 1
        return {
            'data_id': f'minecraft-{self.sample_count:05d}-climb',
            'qa_type': 'StateInfo',
            'question_id': 4,
            'question_description': 'Ask the minimum number of blocks needed to reach a block (pumpkin/gold ore/diamond ore), considering the possibility of using existing ladders.',
            'image': self._take_screenshot(),
            'state': self._save_state({
                'pumkin_position': list((x, num_stones, z)),
                'blocks_under_pumpkin': num_stones,
                'blocks_with_ladder': with_ladder,
            }),
            'plot_level': 'Easy' if num_stones <= 1 else 'Medium' if num_stones <= 3 else 'Hard',
            'qa_level': 'Medium', 
            'question': question,
            'answer': required_blocks,
            'analysis': analysis
        }
    
    def gen_cross_river_climb_qa(self) -> Dict:
        """
        Combination of river crossing and climbing.
        """
        self._clear_scene()
        self.sky = Sky() if random.random() < 0.5 else None
        # Create river (always along x-axis)
        river_width = random.randint(1, 4)
        z = 0
        self._place_river((0, 0, z), (1, 0, 0), river_width, texture='white_cube')
        same_side = random.choices([True, False], weights=[0.3, 0.7])[0]
        
        dis = random.randint(1, 2)
        if same_side:
            player_pos = (0, -1, -river_width//2 - dis)
            self.entities.append(Entity(model='cube', color=color.red, position=player_pos))
            self._mark_position_occupied(player_pos, (1, 1, 1), count_in_centroid=True)
            self._create_land()
            pumpkin_position = self._find_valid_position(
                (1, 1, 1),
                range_constraint=((-self.space_ub[0], self.space_ub[0]), (0, 0), (-self.space_ub[2], -(river_width//2) - 1))
            )
        else:
            player_pos = (0, -1, -river_width//2 - dis)
            self.entities.append(Entity(model='cube', color=color.red, position=player_pos))
            self._mark_position_occupied(player_pos, (1, 1, 1), count_in_centroid=True)
            self._create_land()
            pumpkin_position = self._find_valid_position(
                (1, 1, 1),
                range_constraint=((-self.space_ub[0], self.space_ub[0]), (0, 0), ((river_width//2) + 1, self.space_ub[2]))
            )
        
        x, _, z = pumpkin_position
        stone_height = random.randint(0, 4)
        stone_color = color.random_color()
        with_ladder = random.choices([True, False], weights=[0.3, 0.7])[0]
        for y in range(stone_height):
            self.entities.append(Entity(model='cube', texture='white_cube', color=stone_color, position=(x, y, z)))
            if with_ladder:
                self._place_ladder((x, y, z))
            self._mark_position_occupied((x, y, z), (1, 1, 1))
        
        block = random.choice(['pumpkin', 'gold ore', 'diamond ore'])
        {'pumpkin': self._place_pumpkin, 'gold ore': self._place_gold_ore, 'diamond ore': self._place_diamond_ore}[block]((x, stone_height, z))

        self._adjust_camera(dis_range=(24.5, 28), phi_range=(40, 60))
        # Calculate total blocks needed
        blocks_for_river = river_width
        blocks_for_climbing = max(0, (stone_height + 1) - 2) if not with_ladder else 0  # +1 for pumpkin, -2 for player height
        total_blocks = blocks_for_river + blocks_for_climbing
        
        question = MINECRAFT_RULE_GENERAL + OBTAIN_TASK.format(block=block)
        
        if same_side:
            answer = blocks_for_climbing
            analysis = f"First, from the scene we can see that the player and the {block} are on the same side of the river. So the river doesn't matter. "
        else:
            answer = total_blocks
            analysis = f"First, from the scene we can see that the player and the {block} are on the opposite sides of the river. So the player needs to cross the river first. "
            analysis += f"Based on the rules, the player can build a bridge on the river by placing blocks in it. To have the minimum number of blocks, the bridge should just be vertical to the river bank and the number of the blocks needed is the width of the river, which is {blocks_for_river}. "
            analysis += "Suppose the player has crossed the river. "
        if stone_height == 0:
            analysis += f"The {block} is on the ground, so the player does not need to build any blocks to reach it. So the player need to consume a minimum of {blocks_for_river} block(s). The answer is {answer}."
        elif with_ladder:
            analysis += f"From the image we can see that ladders are attached to the block(s) under the {block}. The player can climb the ladders to reach the {block} if needed. Therefore, he doesn't need to consume any blocks to reach the {block}. So the player needs to consume a minimum of {answer} block(s). The answer is {answer}."
        elif stone_height == 1:
            analysis += f"From the image we can see that there are no ladders, yet there is only one block under the {block}. Thus the {block} is at a height of 2 blocks, same as the upper body of the player. Therefore, the player does not need to build any blocks to reach the {block}. So the player needs to consume a minimum of {answer} block(s). The answer is {answer}."
        else:
            analysis += f"From the image we can see that there are no ladders, and the {block}, on the top of {stone_height} blocks, is at a height of {stone_height + 1} blocks. The player is 2 blocks tall. Therefore, the player needs to build {stone_height + 1} - 2 = {blocks_for_climbing} block(s) under his feet to reach the {block}."
            if same_side:
                analysis += f"So the player needs to consume a minimum of {blocks_for_climbing} block(s). The answer is {answer}."
            else:
                analysis += f"So the player needs to consume a minimum of {blocks_for_river} + {blocks_for_climbing} = {total_blocks} block(s). The answer is {answer}."
        self.sample_count += 1
        return {
            'data_id': f'minecraft-{self.sample_count:05d}-cross_river_climb',
            'qa_type': 'StrategyOptimization',
            'question_id': 5,
            'question_description': 'Ask the minimum number of blocks needed to reach a block (pumpkin/gold ore/diamond ore) that may require crossing a river, considering the possibility of using existing ladders.',
            'image': self._take_screenshot(),
            'state': self._save_state({
                'river_direction': 'x',
                'river_width': river_width,
                'player_position': list(player_pos),
                'pumkin_position': list(pumpkin_position),
                'player_pumpkin_same_side': same_side,
                'blocks_under_pumpkin': stone_height,
                'blocks_with_ladder': with_ladder,
            }),
            'plot_level': 'Easy' if river_width + stone_height <= 3 else 'Medium' if river_width + stone_height <= 6 else 'Hard',
            'qa_level': 'Hard',
            'question': question,
            'answer': answer,
            'analysis': analysis
        }

if __name__ == "__main__":
    minecraft_QA_generator = MinecraftQAGenerator(
        output_dir='minecraft_dataset_test', space_ub=(3, 3, 4)
    )
    for i in range(10):
        # qa_dict = minecraft_QA_generator.gen_scenery_qa()
        # qa_dict = minecraft_QA_generator.gen_cube_count_qa()
        # qa_dict = minecraft_QA_generator.gen_cross_fluid_qa()
        # qa_dict = minecraft_QA_generator.gen_climb_qa()
        qa_dict = minecraft_QA_generator.gen_cross_river_climb_qa()
        for k, v in qa_dict.items():
            print(f'{k}: {v}')
