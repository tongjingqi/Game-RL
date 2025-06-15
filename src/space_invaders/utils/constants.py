SPACE_INVADERS_GAME_DESCR_GENERAL = '''The given image represents a simplified interface of the game Space Invaders. The enemy area is implicitly divided into a grid of cells, with the row and column numbers shown on the left and top sides of the grid respectively which you should strictly follow. Each cell is either empty or occupied by an incoming enemy which can be purple, blue or green. The ship is at the bottom row, aligned with one of the columns, which shoots the enemies using laser while dodging possible lasers from the enemies. 
'''

SHIP_SHOOT_DESCR = '''If the ship shoots, the enemy closest to the ship (i.e. the lowermost one) on the same column as the ship, if any, will be destroyed and disappear, adding points to the player's score and exposing the enemy behind (if any). Purple enemies are worth 30 points, blue enemies are worth 20 points, and green enemies are worth 10 points.
'''

SPACE_INVADERS_TIMES_SEQ_RULES = '''The enemies keep on uniformly moving in a certain direction (left or right). Carefully understand the time sequence rules below. 
- Consider the consecutive time intervals, denoted by t, t+1, t+2, ...
- During each time interval t:
  - The ship can shoot at most once.
  - The ship can move to another column before shooting.
  - The enemies keep still.
- At the very end of this time interval t, the enemies move one step in the direction they are moving, thus changing the columns they are on.

'''

# ---------------------------------------------------------------------------------------------------------------------------


INSTRUCTION_TO_GIVE_OPTION_NUM = '''Give the number of the correct option.\n'''