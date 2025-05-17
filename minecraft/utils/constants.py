MINECRAFT_RULE_GENERAL = '''You are provided with a game interface that mimics "Minecraft", where all objects are composed of equal-sized cubes. Players build and explore in this world. They have numerous blocks and can place them following the basic placement rules of "Minecraft." In simple terms, players can place blocks around their current position, and new blocks must be adjacent to existing ones (i.e., sharing a common face). Placing blocks in fluids (such as river water) is allowed, replacing the fluid at that position directly with the block. Players can also sometimes remove blocks.
'''

SCENERY_RECOG_TASK = '''The scene contains several sceneries. Sceneries can be:
1. Bricks
2. Gold Ore (embedded with gold-colored stone)
3. Diamond Ore (embedded with blue-green stone)
4. TNT (like dynamite, a red block labeled "TNT")
5. Pumpkin (a yellow block resembling a pumpkin)
6. Ladder (not a block, but a wooden ladder attached to blocks, similar to those in "Minecraft")
7. River (beneath ground level, blue, spanning the screen. Specifically, rivers are sometimes presented in clearly bounded grids to allow players to discern the river's width)
8. Lava (beneath ground level, consisting of orange and yellow)

Please select the option that correctly describes the sceneries contained in the image.
'''

CROSS_RIVER_TASK = '''There is a river in the scene, and the player's position is marked in red. The player needs to cross the river. Note that the river is presented in clearly bounded grid forms to allow players to discern the river's width. Suppose the player cannot wade directly through the water nor can they make a horizontal jump to cross the river directly.

Question: If the player wants to cross the river, what is the minimum number of blocks they need to consume?'''

CLIMB_TO_PUMPKIN_TASK_SIMPLE = '''There is a pumpkin in the scene. To mine the pumpkin, the player's upper body (assuming the player is 2 blocks tall) must not be below the pumpkin's height. For example, if the pumpkin is located at a height of 2 blocks, the player can directly mine the pumpkin. However, if the pumpkin is at a height of 3 blocks, the player cannot mine it directly. The player can instead build blocks under his feet to raise his height. For instance, if the player builds 2 blocks under his feet, he will reach a height of 4 blocks.

Question: To obtain the pumpkin, what is the minimum number of blocks the player needs to consume?'''

CLIME_OBTAIN_TASK = '''There is a {block} block in the scene. If the {block} is simply on the ground (i.e., at the height of 1 blocks), the player can directly mine it. Otherwise, n (a positive integer) block(s) is/are under the {block} so that the {block} is a height of n+1. Under this circumstance:
- If there are ladders attached to the block(s) under the {block}, the player can climb up (if needed) and mine the {block} directly without consuming any blocks.
- If there are no ladders attached to the block(s) under the {block}. We should know that to mine the {block}, the player's upper body (assuming the player is 2 blocks tall) must not be below the {block}'s height. For example, if the {block} is located at a height of 2 blocks, the player can directly mine the {block}. However, if the {block} is at a height of 3 blocks, the player cannot mine it directly. The player can instead build blocks under his feet to raise his height. For instance, if the player builds 2 blocks under his feet, he will reach a height of 4 blocks.

Question: To obtain the {block}, what is the minimum number of blocks the player needs to consume?'''

OBTAIN_PUMPKIN_TASK = '''There is a river and a pumpkin in the scene, and the player's position is marked in red. Note that the river is presented in clearly bounded grid forms to allow players to discern the river's width. Suppose the player cannot wade directly through the water nor can they make a horizontal jump to cross the river directly.
Additionally, to mine the pumpkin, the player's upper body (assuming the player is 2 blocks tall) must not be below the pumpkin's height. For example, if the pumpkin is located at a height of 2 blocks, the player can directly mine the pumpkin. However, if the pumpkin is at a height of 3 blocks, the player cannot mine it directly. The player can instead build blocks under his feet to raise his height. For instance, if the player builds 2 blocks under his feet, he will reach a height of 4 blocks.

Question: To obtain the pumpkin, what is the minimum number of blocks the player needs to consume?'''

OBTAIN_TASK = '''There is a river and a {block} block in the scene, and the player's position is marked in red. Note that the river is presented in clearly bounded grid forms to allow players to discern the river's width. Suppose the player cannot wade directly through the water nor can they make a horizontal jump to cross the river directly.
Additionally, if the {block} is simply on the ground (i.e., at the height of 1 blocks), the player can directly mine it. Otherwise, n (a positive integer) block(s) is/are under the {block} so that the {block} is a height of n+1. Under this circumstance:
- If there are ladders attached to the block(s) under the {block}, the player can climb up (if needed) and mine the {block} directly without consuming any blocks.
- If there are no ladders attached to the block(s) under the {block}. We should know that to mine the {block}, the player's upper body (assuming the player is 2 blocks tall) must not be below the {block}'s height. For example, if the {block} is located at a height of 2 blocks, the player can directly mine the {block}. However, if the {block} is at a height of 3 blocks, the player cannot mine it directly. The player can instead build blocks under his feet to raise his height. For instance, if the player builds 2 blocks under his feet, he will reach a height of 4 blocks.
On rare occasions, the red sign indicating the player's position may be fully blocked by the blocks, thus making it invisible. In this case, we consider that the player and the {block} are on the same side of the river.

Question: To obtain the {block}, what is the minimum number of blocks the player needs to consume?'''