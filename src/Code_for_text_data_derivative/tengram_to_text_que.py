import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import os
from typing import Dict, List, Tuple, Any
import random
from dataclasses import dataclass, asdict
import colorsys
from matplotlib.colors import rgb2hex, hex2color

@dataclass
class PuzzleConfig:
    grid_size: int
    num_seeds: int
    num_pieces_to_remove: int
    
@dataclass
class QAPair:
    data_id: str
    qa_type: str
    question_id: int
    question_description: str
    image: str
    state: str
    plot_level: str
    qa_level: str
    question: str
    answer: int
    analysis: str
    options: List[str]

@dataclass
class Piece:
    id: int
    width: int
    height: int
    cells: List[Tuple[int, int]]

class TengramGenerator:
    def __init__(self, config: PuzzleConfig):
        self.config = config
        self.grid = np.zeros((config.grid_size, config.grid_size), dtype=int)
        self.seeds = []
        self.pieces = []
        self.pieceMaxWidth = 0
        self.pieceMaxHeight = 0
        self.removed_pieces = []

    def assign_cells_to_seeds(self) -> None:
        """Assign each cell to closest seed point"""
        for i in range(self.config.grid_size):
            for j in range(self.config.grid_size):
                min_dist = float('inf')
                closest_seed = 0
                for idx, (seed_x, seed_y) in enumerate(self.seeds):
                    dist = (i - seed_x)**2 + (j - seed_y)**2
                    if dist < min_dist:
                        min_dist = dist
                        closest_seed = idx + 1  # 1-based indexing
                self.grid[i, j] = closest_seed
        self.calc_pieces()
    
    def calc_pieces(self) -> None:
        """Assign value to self.pieces after calling assign_cells_to_seeds"""
        self.pieces = []
        self.pieceMaxHeight=0
        self.pieceMaxWidth=0
        minxes=[self.config.grid_size]*self.config.num_seeds
        minyes=[self.config.grid_size]*self.config.num_seeds
        maxxes=[0]*self.config.num_seeds
        maxyes=[0]*self.config.num_seeds
        for piece_id in range(1, self.config.num_seeds + 1):
            cells = np.argwhere(self.grid == piece_id)
            minx = min(cells[:, 0])
            miny = min(cells[:, 1])
            maxx = max(cells[:, 0])
            maxy = max(cells[:, 1])
            minxes[piece_id-1]=minx
            minyes[piece_id-1]=miny
            maxxes[piece_id-1]=maxx
            maxyes[piece_id-1]=maxy
            height = maxx - minx + 1
            width = maxy - miny + 1
            self.pieceMaxWidth=max(self.pieceMaxWidth,width)
            self.pieceMaxHeight=max(self.pieceMaxHeight,height)
            
            # crop grid to piece
            cellArray = np.zeros((height, width), dtype=int)
            for cell in cells:
                cellArray[cell[0]-minx, cell[1]-miny] = piece_id
            self.pieces.append(Piece(piece_id, width, height, cellArray))

    def get_removed_grid(self) -> List[List[int]]:
        """Return the grid with removed pieces"""
        # Plot removed pieces
        widthNeeded = -1
        heightNeeded = -1
        for piece in self.removed_pieces:
            widthNeeded += self.pieces[piece-1].width + 1
            heightNeeded = max(heightNeeded, self.pieces[piece-1].height)

        removed_grid = np.zeros((heightNeeded, widthNeeded), dtype=int)
        currentWidth = 0
        for piece in self.removed_pieces:
            pieceWidth = self.pieces[piece-1].width
            pieceHeight = self.pieces[piece-1].height
            piece_cells = self.pieces[piece-1].cells
            removed_grid[0:pieceHeight, currentWidth:currentWidth+pieceWidth] = piece_cells
            
            currentWidth += pieceWidth + 1
        
        return removed_grid
import json
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
data=read_json('data.json')
for line in data:
    statePath = line['state']
    stateData = read_json(statePath)
    grid = stateData['grid']
    gridStr = '\n'.join([f'row {index}: ['+', '.join(map(str,row))+']' for index,row in enumerate(grid)])
    del line['state']
    config=stateData['config']
    generator=TengramGenerator(PuzzleConfig(config['grid_size'],config['num_seeds'],config['num_pieces_to_remove']))
    generator.seeds=stateData['seeds']
    generator.assign_cells_to_seeds()
    generator.removed_pieces=stateData['removed_pieces']
    removed_grid=generator.get_removed_grid()
    removed_gridStr = '\n'.join([f'row {index}: ['+', '.join(map(str,row))+']' for index,row in enumerate(removed_grid)])
    line['question'] = 'Main Board:\n'+gridStr+'\nRemoved Pieces Board:\n'+removed_gridStr+'\n(Each number represents index of the piece the cell belongs to. 0 means this cell is empty, and same number means belong to same piece. Indexes are 0-based, row first)\n'+line['question']
with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)
    