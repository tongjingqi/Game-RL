PLAYER_0 = 0
PLAYER_1 = 1
MAX_TURN_NUM = {'Easy':13,'Medium': 29, 'Hard': 54}
PLOT_LEVEL = {'Easy': 3,'Medium': 4, 'Hard': 5}
NUM_BALLS = {'Easy': 7,'Medium': 15, 'Hard': 27}

import random

class grid():
    def __init__(self,level,id,legal,board_level):
        self.Level = level   #Level of grid in pyramid
        self.Position = [int(id/(board_level-level)),int(id%(board_level-level))] 
        
        self.Available = True  #If this place has a ball
        self.Legal = legal    #If this place can put a ball
        self.Can_be_taken = False  #If the ball here can be taken
        
        self.Base = []      #Balls under the ball
        self.Color = None   
        self.Upper = 0       #How many balls have pressed the ball
        
        self.counted = False

    def put(self,color):
        if self.Legal:
            self.Available = False
            self.Legal = False
            self.Can_be_taken = True
            
            self.Color = color
            for item in self.Base:
                item.Can_be_taken = False
                item.Upper += 1
            return True
        else:
            return False
        
    def take(self):
        if not self.Available:
            self.Available = True
            self.Legal = True
            self.Can_be_taken = False
            
            self.Color = None
            for item in self.Base:
                item.Upper -= 1
                if item.Upper == 0:
                    item.Can_be_taken = True
            return True
        else:
            return False
        
class Board(object):
    def __init__(self,level=4):
        self.Level = level
        self.Board=[]
        for i in range(level):
            num_plot = (level-i)**2
            if i == 0:
                sub_board = [grid(0,id,True,level) for id  in range(num_plot)]
            else:
                sub_board = [grid(i,id,False,level) for id  in range(num_plot)]
                
            self.Board.append(sub_board)
        self.construct_layer(self.Board)
        self.counter = 0
        
    def print_board_2D(self):
        for level in range(self.Level):
            print("Level:",level)
            count = 0
            string = ''
            for item in self.Board[level]:
                if item.Color is None:
                    string += "--  "
                elif item.Color == PLAYER_0:
                    string += "P0  "
                else:
                    string += "P1  "
                count += 1
                if(count == self.Level-level):
                    print(string)
                    count = 0
                    string = ''
                    
    def board_dict(self):
        board_dict = dict()
        for level in range(self.Level):
            count = 0
            whole_list = []
            row_list = []
            for item in self.Board[level]:
                if item.Color is None:
                    row_list.append("--")
                elif item.Color == PLAYER_0:
                    row_list.append("P0")
                else:
                    row_list.append("P1")
                count += 1
                if(count == self.Level-level):
                    count = 0
                    whole_list.append(row_list)
                    row_list = []
            board_dict[level] = whole_list
        return board_dict
          
    def __getitem__(self,index):
        i,j,k = index
        i,j,k = int(i),int(j),int(k)
        level = self.Level
        if i>=0 and i<level:
            num = j * (level-i) + k
            if num < (level-i) * (level-i):
                return self.Board[i][j*(level-i)+k]
        raise ValueError("Index out of bound")
    
    def construct_layer(self,Board):
        for level in range(self.Level):
            if level == 0:
                continue
            else:
                for item in Board[level]:
                    position = item.Position
                    base_level = level - 1
                    item.Base.append(Board[base_level][position[0]*(self.Level-base_level)+position[1]])
                    item.Base.append(Board[base_level][(position[0]+1)*(self.Level-base_level)+position[1]])
                    item.Base.append(Board[base_level][position[0]*(self.Level-base_level)+(position[1]+1)])
                    item.Base.append(Board[base_level][(position[0]+1)*(self.Level-base_level)+(position[1]+1)])
                # for item in Board[level]:
                #     print("item:",item.Position)
                #     for base in item.Base:
                #         print(base.Position)
        
                    
    def take_put_check(self,stop_mode=False):
        take_pos = []
        
        for level in range(self.Level):
            if level == 0:
                continue
            else:
                for item in self.Board[level]:
                    take_flag = 1    #when four balls in base(which construct 2x2 block) is the same color, should operate take action
                    put_flag = 1    #when four balls in base(which construct 2x2 block) is not the same color, the upper level get a spot to put
                    color = item.Base[0].Color
                    for base in item.Base:
                        if base.Available == True:
                            item.Legal = False
                            take_flag = 0
                            put_flag = 0
                            break
                        if base.Color !=color:
                            take_flag = 0
                    if take_flag:
                        for base in item.Base:
                            if stop_mode == True:
                                take_pos.append(base)
                            else:
                                if base.Can_be_taken == True:
                                    if not base in take_pos:
                                        take_pos.append(base)
                        continue
                    
                    if put_flag:
                        if item.Available == True:
                            item.Legal = True
            
        return take_pos
    
    def find_all_legal(self):
        legal_pos = []
        for level in range(self.Level):
            for item in self.Board[level]:
                if item.Legal:
                    legal_pos.append(item)
        return legal_pos
    
    def all_pos(self):
        pos = []
        for level in range(self.Level):
            for item in self.Board[level]:
                pos.append(item)
        return pos
    
    def all_avl_pos(self):
        pos = []
        for level in range(self.Level):
            for item in self.Board[level]:
                if item.Available:
                    pos.append(item)
        return pos
    
    def count_balls(self):
        balls = []
        for level in range(self.Level):
            balls.append(0)
        counter = 0
        for level in range(self.Level):
            for item in self.Board[level]:
                if not item.Available:
                    balls[level] += 1
                    counter += 1
        return balls,counter
    
class Pyramid_Chess_Random_Generate():
    def __init__(self,rand_turn_num,plot_level = "Medium",num_turns=None,max_turn=None):
        if plot_level in PLOT_LEVEL:
            self.Level = PLOT_LEVEL[plot_level]
        else:
            raise ValueError("plot level not fit")
        self.Chess_Board = Board(level=self.Level)
        self.Turn = PLAYER_0
        self.Num_balls = NUM_BALLS[plot_level]
        self.Balls = [self.Num_balls,self.Num_balls]
        if plot_level == "Hard":
            self.Balls[self.Turn] += 1
        if max_turn == None:
            self.Max_turn = MAX_TURN_NUM[plot_level]
        else:
            self.Max_turn = max_turn
        self.Rand = rand_turn_num
        self.Win_status = -1
        
        if rand_turn_num:
            self.Num_turns = random.randint(0,self.Max_turn-1)
        else:
            self.Num_turns = num_turns
            
    def refresh(self):
        self.Chess_Board = Board(level=self.Level)
        self.Turn = PLAYER_0
        self.Balls = [self.Num_balls,self.Num_balls]
        if self.Num_balls == 27:
            self.Balls[self.Turn] += 1
        self.Win_status = -1
        if self.Rand:
            self.Num_turns = random.randint(0,self.Max_turn-1)

        
    def getindex(self):
        index0 = input("Level:")
        index1 = input("axis0:")
        index2 = input("axis1:")
        return[index0,index1,index2]
        
    def change_turn(self):
        if self.Turn == PLAYER_0:
            self.Turn = PLAYER_1
        else:
            self.Turn = PLAYER_0
            
    def take_random(self,take_pos,pr_info):
        if pr_info:
            print(pr_info)
            print("take_happen:",self.Turn,self.Balls)
        if len(take_pos) <= 2:
            for item in take_pos:
                item.take()
            return len(take_pos),take_pos
        
        else:
            id =0
            for item in take_pos:
                id += 1
            num_take = len(take_pos)
            index = random.sample(range(0, num_take-1), 2)
            input1 = index[0]
            input2 = index[1]
            info = [take_pos[input1],take_pos[input2]]
            take_pos[input1].take()
            take_pos[input2].take()
            return 2,info
        
    def win_check(self):
        if self.Balls[self.Turn] == 0:
            self.change_turn()
            self.Win_status = self.Turn

        return self.Win_status
        
    def one_turn_random(self,pr_info):
        put_pos = self.Chess_Board.find_all_legal()
        index = random.randint(0,len(put_pos)-1)
        put_pos[index].put(self.Turn)
        put_info = put_pos[index]
        if pr_info:
            print(put_pos[index].Level,put_pos[index].Position)
        self.Balls[self.Turn] -= 1
        
        num_take = 0
        take_info = []
        take_pos = self.Chess_Board.take_put_check()
        if not take_pos == []:
            num_take,take_info = self.take_random(take_pos,pr_info=pr_info)
            pos_more = self.Chess_Board.take_put_check()
            while not (pos_more == []):
                if pr_info:
                    print("Warning:Mutiple take happen ")
                num_take,take_info = self.take_random(pos_more,pr_info=pr_info)
                pos_more = self.Chess_Board.take_put_check()
            self.Balls[self.Turn] += num_take 
        self.Chess_Board.counter += 1
        return put_info,num_take,take_info
        
        
            
    def generate(self,pr_info):
        turn = 0
        # self.Chess_Board.print_board_2D()
        max_turn_num = min(self.Max_turn,self.Num_turns)
        while(turn < max_turn_num):
            self.one_turn_random(pr_info=pr_info)
            if(self.win_check() != -1):
                break
            self.change_turn()
            turn += 1
            # self.Chess_Board.print_board_2D()
            if(turn == self.Max_turn):
                break   
        return self.Chess_Board
    
    def generate_stop_at_take(self,pr_info):
        turn = 0
        # self.Chess_Board.print_board_2D()
        max_turn_num = min(self.Max_turn,self.Num_turns)
        while(turn < max_turn_num):
            put_pos = self.Chess_Board.find_all_legal()
            index = random.randint(0,len(put_pos)-1)
            put_pos[index].put(self.Turn)
            if pr_info:
                print(put_pos[index].Level,put_pos[index].Position)
            self.Balls[self.Turn] -= 1
            
            num_take = 0
            take_pos = self.Chess_Board.take_put_check(stop_mode = True)
            if not take_pos == []:
                put_pos[index].take()
                take_point =  put_pos[index]  
                break
            self.Chess_Board.counter += 1
            
            if(self.win_check() != -1):
                self.refresh() 
                turn = 0
                continue
            self.change_turn()
            turn += 1
            # self.Chess_Board.print_board_2D()
            if(turn == self.Max_turn):
                self.refresh() 
                turn = 0
        return self.Chess_Board,take_point,self.Turn,take_pos

def board_generate(plot_level="Medium",pr_info=False,max_turn=None):
    chess = Pyramid_Chess_Random_Generate(rand_turn_num=True,plot_level=plot_level,max_turn=max_turn)
    board = chess.generate(pr_info=pr_info)
    return board

def board_generate_stop_at_take(plot_level="Medium",pr_info=False):
    chess = Pyramid_Chess_Random_Generate(plot_level=plot_level,rand_turn_num=False,num_turns = 100,max_turn = 100)
    board,take_point,turn,take_pos = chess.generate_stop_at_take(pr_info=pr_info)
    return board,take_point,turn,take_pos

def count_base_info(item):
    info = []
    steps = count_base(item,info)
    steps += 1
    return steps,info

def count_base(item,info,dict_info):
    """
    Calculate how many steps are required for an item to become legal for placement.
    Uses a recursive tree search approach to traverse through the Base list and 
    count how many steps it takes to reach an Available base.
    """
    # Initialize the count of steps to 0
    step_count = 0
    pos_count = 0
    # If the item has no Base, return 0 steps
    if not item.Base:
        return 0
    
    # Traverse through all Base items in the list
    for base in item.Base:
        if base.Available and (base.counted == False):
            # If the base is available, increment step count and recursively check its children
            base.counted = True
            step_count += 1
            pos_count += 1
            dict_info[base.Level].append(base.Position)
            step_count += count_base(base,info,dict_info)
        else:
            # If the base is not available, do not recurse further
            continue
    
    info[item.Level-1] += pos_count
    return step_count


def count_ball(board_dict):
    """
    Count the balls on the board and return the balls_list and total count.
    
    Args:
        board_dict (dict): A dictionary where keys are levels and values are 2D arrays
                           representing the board layout at each level.
                           "--" represents an empty slot, and "P0", "P1" represent balls.
    
    Returns:
        tuple: (balls_list, total_count)
               - balls_list: A list of tuples, where each tuple contains:
                   (number of balls on the level, detailed ball information).
                   Detailed ball information is a 2D list of (color, coordinate) for each ball.
               - total_count: Total number of balls across all levels.
    """
    # Map player identifiers to colors
    color_map = {
        "P0": "blue",
        "P1": "red",
        "--": None  # Represent empty slots
    }
    
    balls_list = []
    total_count = 0
    
    # Iterate over each level in the board dictionary
    for level, grid in board_dict.items():
        level = int(level)  # Convert level string to integer
        num_balls = 0
        detailed_info = []
        
        # Iterate through rows and columns of the grid
        for row_idx, row in enumerate(grid):
            detailed_row = []
            for col_idx, cell in enumerate(row):
                if cell != "--":  # If the slot is not empty
                    color = color_map[cell]
                    coordinate = (row_idx, col_idx)
                    detailed_row.append((color, coordinate))
                    num_balls += 1  # Increment the ball count
            detailed_info.append(detailed_row)
        
        # Add the count and details for this level to balls_list
        balls_list.append((num_balls, detailed_info))
        total_count += num_balls  # Update total count
    
    return balls_list, total_count

def test():
    board = board_generate(plot_level="Hard",pr_info=True)
    board.print_board_2D()
    
    