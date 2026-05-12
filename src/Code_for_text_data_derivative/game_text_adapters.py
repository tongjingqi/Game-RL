"""Game-specific visible-state renderers for text QA conversion.

Adapters should describe what the rendered image makes visible. They should not
blindly dump solution-only fields from state JSON files.
"""

from __future__ import annotations

import json
from typing import Any, Callable


Adapter = Callable[[dict[str, Any], dict[str, Any]], str]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _rows_table(rows: list[list[Any]], row_start: int = 0) -> str:
    return "\n".join(f"Row {idx + row_start}: {row}" for idx, row in enumerate(rows))


def _compact_grid(grid: list[list[Any]], symbols: dict[Any, str] | None = None) -> str:
    lines = []
    for row in grid:
        cells = [symbols.get(cell, str(cell)) if symbols else str(cell) for cell in row]
        lines.append(" ".join(cells))
    return "\n".join(lines)


def _prefix(title: str, body: str) -> str:
    return f"{title}\n{body.strip()}\n"


def text_2d_turing_machine(state: dict[str, Any], item: dict[str, Any]) -> str:
    rules = [
        (
            f"if state={r['state']} and symbol={r['symbol']}: "
            f"write {r['new_symbol']}, change to state {r['new_state']}, move direction {r['direction']}"
        )
        for r in state["rules"]
    ]
    body = (
        "Grid symbols:\n"
        f"{_rows_table(state['grid'])}\n\n"
        f"Head: {state['head']}\n\n"
        "Transition rules:\n" + "\n".join(rules)
    )
    return _prefix("2D TURING MACHINE STATE:", body)


def text_3d_maze(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = [
        f"Grid size: {state.get('grid_size')}",
        f"Start position: {state.get('start_pos')}",
        f"Goal position: {state.get('goal_pos')}",
        "Visible cubes. Path-solution labels are omitted; only non-solution visual markers are listed:",
    ]
    for cube in state.get("cubes", []):
        roles = cube.get("roles", cube.get("role", []))
        if isinstance(roles, str):
            roles = [roles]
        visible_roles = [role for role in roles if role not in {"main_path", "alternative_path"}]
        body.append(f"- position={cube.get('pos')}, markers={visible_roles}")
    body.append("Visible ladders:")
    for ladder in state.get("ladders", []):
        body.append(f"- {ladder}")
    body.append(f"Numbered markers: {state.get('numbered_markers', [])}")
    body.append(f"Sequence points: {state.get('sequence_points', [])}")
    body.append("Branch point positions:")
    for branch in state.get("branches", []):
        body.append(f"- id={branch.get('branch_id')}, position={branch.get('pos')}")
    body.append(
        "Note: ordered route annotations and branch answer directions are intentionally omitted; reason from the visible graph and markers."
    )
    return _prefix("3D MAZE STATE:", "\n".join(body))


def text_3d_reconstruction(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        f"Current voxel positions: {state.get('voxel_positions', [])}\n"
        f"Remaining voxels: {state.get('remaining_voxels')}\n"
        "Target YZ/front projection:\n"
        f"{_rows_table(state.get('target_yz_projection', []))}\n"
        "Target XZ/side projection:\n"
        f"{_rows_table(state.get('target_xz_projection', []))}"
    )
    return _prefix("3D RECONSTRUCTION STATE:", body)


def text_chess_ranger(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        "Board grid:\n"
        f"{_rows_table(state.get('mine_board', []))}\n\n"
        f"Pieces: {state.get('pieces', [])}"
    )
    return _prefix("CHESS RANGER STATE:", body)


def text_freecell(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = ["Cascade piles:"]
    for idx, pile in enumerate(state.get("cascade_piles", [])):
        lines.append(f"Cascade {idx}: {pile}")
    lines.append(f"Free cells: {state.get('free_cells', [])}")
    lines.append(f"Foundation piles: {state.get('foundation_piles', {})}")
    return _prefix("FREECELL STATE:", "\n".join(lines))


def text_hue(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = [
        "Rows and columns are read from top-left with 0-based indexes unless the question states otherwise.",
        "Visible color board as RGB triples:",
        _rows_table(state.get("board", [])),
        f"Removed/blank positions visible in the puzzle: {state.get('removed_positions', [])}",
        f"Cell labels: {state.get('cell_labels', {})}",
        f"Gradient information visible from the board: {state.get('gradient_info', {})}",
    ]
    if state.get("extra_options"):
        lines.append(f"Extra candidate colors/options: {state.get('extra_options')}")
    lines.append("Hidden removed color answers are intentionally omitted.")
    return _prefix("HUE PUZZLE STATE:", "\n".join(lines))


def text_jewel2(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        f"Grid size: {state.get('rows')} rows x {state.get('cols')} columns.\n"
        "Board symbols/colors:\n"
        f"{_rows_table(state.get('chessboard', []))}\n"
        f"Total cleared so far: {state.get('total_cleared', 0)}"
    )
    return _prefix("JEWEL2 STATE:", body)


def _card_list(cards: list[Any]) -> str:
    return "[" + ", ".join(str(card) for card in cards) + "]"


def text_klondike(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = [
        f"Draw/stock pile: {len(state.get('draw', []))} face-down cards.",
        f"Waste/dump pile: {_card_list(state.get('dump', []))}",
        f"Foundation piles: {state.get('piles', [])}",
        "Tableau piles, left to right; '<Card Sprite...>' means a face-down card:",
    ]
    for idx, pile in enumerate(state.get("tableau", []), 1):
        lines.append(f"Tableau {idx}: {_card_list(pile)}")
    return _prefix("KLONDIKE STATE:", "\n".join(lines))


def text_langton_ant(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        "Grid cells: 0=white, 1=black. Coordinates use row and column from the top-left.\n"
        f"{_rows_table(state.get('grid', []))}\n\n"
        f"Ant: {state.get('ant')}\n"
        "Rules: on a white cell, turn right, flip the cell black, move forward; on a black cell, turn left, flip it white, move forward."
    )
    return _prefix("LANGTON ANT STATE:", body)


def text_lifegame(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        "Grid cells: 1=alive, 0=dead. Coordinates use row and column from the top-left.\n"
        f"{_rows_table(state.get('grid', []))}\n"
        "Apply the standard Conway's Game of Life rules unless the question specifies otherwise."
    )
    return _prefix("LIFE GAME STATE:", body)


def text_maze(state: dict[str, Any], item: dict[str, Any]) -> str:
    symbols = {0: ".", 1: "#", 2: "P", 3: "G"}
    body = (
        "Maze grid: #=wall, .=path, P=player, G=goal.\n"
        f"Size: {state.get('size')}\n"
        f"Player position: {state.get('playerPosition')}\n"
        f"Goal position: {state.get('endPosition')}\n"
        f"{_compact_grid(state.get('maze', []), symbols)}"
    )
    return _prefix("MAZE STATE:", body)


def text_minecraft(state: dict[str, Any], item: dict[str, Any]) -> str:
    visible_fields = []
    if "sceneries" in state:
        visible_fields.append(f"Visible sceneries: {state['sceneries']}")
    if {"x_blocks", "y_blocks", "z_blocks"} <= set(state):
        visible_fields.append(
            f"Block counts by axis/layer: x_blocks={state['x_blocks']}, y_blocks={state['y_blocks']}, z_blocks={state['z_blocks']}"
        )
    if "river_width" in state:
        visible_fields.append(f"River direction: {state.get('river_direction')}")
        visible_fields.append(f"River width in grid cells: {state.get('river_width')}")
    if "player_position" in state:
        visible_fields.append(f"Player position: {state.get('player_position')}")
    if "pumkin_position" in state:
        visible_fields.append(f"Target block position: {state.get('pumkin_position')}")
    if "blocks_under_pumpkin" in state:
        visible_fields.append(f"Blocks under the target block: {state.get('blocks_under_pumpkin')}")
    if "blocks_with_ladder" in state:
        visible_fields.append(f"Ladders attached under target block: {state.get('blocks_with_ladder')}")
    if "player_pumpkin_same_side" in state:
        visible_fields.append(f"Player and target are on the same side of the river: {state.get('player_pumpkin_same_side')}")
    return _prefix("MINECRAFT-LIKE SCENE STATE:", "\n".join(visible_fields) or _json(state))


def text_minesweeper(state: dict[str, Any], item: dict[str, Any]) -> str:
    rows = state["rows"]
    cols = state["cols"]
    board = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if state["flagged"][r][c]:
                row.append("F")
            elif state["revealed"][r][c]:
                row.append(str(state["mine_board"][r][c]))
            else:
                row.append(".")
        board.append(row)
    body = (
        f"Grid size: {rows} rows x {cols} columns.\n"
        "Cells: digit=visible clue, F=flagged, .=unrevealed. Hidden mines are not shown.\n"
        f"{_rows_table(board)}"
    )
    return _prefix("MINESWEEPER VISIBLE STATE:", body)


def text_pacman(state: dict[str, Any], item: dict[str, Any]) -> str:
    grid_size = state["grid_size"]
    if isinstance(grid_size, int):
        rows = cols = grid_size
    else:
        rows, cols = grid_size
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    for r, c in state.get("walls", []):
        grid[r][c] = "#"
    for r, c in state.get("beans", []):
        grid[r][c] = "o" if grid[r][c] == "." else grid[r][c] + "+o"
    pr, pc = state["pacman_position"]
    grid[pr][pc] = "P" if grid[pr][pc] == "." else grid[pr][pc] + "+P"
    for ghost in state.get("ghosts", []):
        gr, gc = ghost.get("position", ghost if isinstance(ghost, list) else (None, None))
        label = ghost.get("name", "Ghost")[0].upper() if isinstance(ghost, dict) else "G"
        grid[gr][gc] = label if grid[gr][gc] == "." else grid[gr][gc] + "+" + label
    body = (
        "Grid: #=wall, o=bean, P=Pacman, uppercase letters=ghost colors. Multiple entities in one cell are joined with '+'.\n"
        f"Pacman direction: {state.get('direction')}\n"
        f"{_rows_table(grid)}"
    )
    return _prefix("PACMAN STATE:", body)


def text_pyramid_chess(state: dict[str, Any], item: dict[str, Any]) -> str:
    return _prefix("PYRAMID CHESS STATE:", _json(state))


def text_rhythm_game(state: dict[str, Any], item: dict[str, Any]) -> str:
    rows, cols = state.get("rows", 0), state.get("cols", 0)
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    for block in state.get("block_info", []):
        row = int(block["row"]) - 1
        col = int(block["col"]) - 1
        if 0 <= row < rows and 0 <= col < cols:
            grid[row][col] = block["color"]
    body = (
        f"Grid size: {rows} rows x {cols} columns. Coordinates in the original task are 1-based.\n"
        f"Blocked/colored cells: {state.get('blocked_cell_num')}\n"
        "Grid entries are color/type labels, '.' means empty:\n"
        f"{_rows_table(grid, row_start=1)}"
    )
    return _prefix("RHYTHM GAME STATE:", body)


def text_rubiks_cube(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = [
        "Each face is a 3x3 grid. Columns are read left to right and rows are read bottom to top when the question uses that convention.",
        f"Color id mapping: {dict(enumerate(state.get('colors', [])))}",
    ]
    face_states = state.get("face_states")
    if face_states:
        for face in ["U", "D", "L", "R", "F", "B"]:
            if face in face_states:
                lines.append(f"Face {face}:")
                lines.append(_rows_table(face_states[face]["colors"]))
    else:
        for face, grid in state.get("faces", {}).items():
            lines.append(f"Face {face}:")
            lines.append(_rows_table(grid))
    return _prefix("RUBIK'S CUBE STATE:", "\n".join(lines))


def text_snake(state: dict[str, Any], item: dict[str, Any]) -> str:
    symbols = {0: ".", 1: "H", 2: "B", 3: "F"}
    body = (
        "Grid: .=empty, H=snake head, B=snake body, F=food. Coordinates use row and column from the top-left.\n"
        f"{_compact_grid(state.get('map', []), symbols)}"
    )
    return _prefix("SNAKE STATE:", body)


def text_sokoban(state: dict[str, Any], item: dict[str, Any]) -> str:
    symbols = {0: ".", 1: "#", 2: "B", 3: "T", 4: "*", 5: "P", 6: "+"}
    body = (
        "Grid: #=wall, .=empty, P=player, B=box, T=target, *=box on target, +=player on target.\n"
        f"Grid size: {state.get('grid_size')}\n"
        f"{_compact_grid(state.get('grid', []), symbols)}\n"
        f"Player: {state.get('player')}\n"
        f"Boxes: {state.get('boxes', [])}\n"
        f"Targets: {state.get('targets', [])}"
    )
    return _prefix("SOKOBAN STATE:", body)


def text_space_invaders(state: dict[str, Any], item: dict[str, Any]) -> str:
    rows = state.get("enemy_area_rows", state.get("enemy_rows", 0))
    cols = state.get("total_cols", state.get("enemy_cols", 0))
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    for enemy in state.get("enemies", []):
        x, y = int(enemy["x"]), int(enemy["y"])
        r = y - 1 if y >= 1 else y
        c = x - 1 if x >= 1 else x
        if 0 <= r < rows and 0 <= c < cols:
            grid[r][c] = enemy.get("color", "enemy")
    body = (
        f"Enemy area: {rows} rows x {cols} columns. Ship column: {state.get('ship_col')}.\n"
        "Grid entries are enemy colors; '.' means no enemy:\n"
        f"{_rows_table(grid, row_start=1)}"
    )
    return _prefix("SPACE INVADERS STATE:", body)


def text_spider_solitaire(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = [
        f"Stock pile count: {len(state.get('stock', []))}; stock cards are face down and not individually shown.",
        "Waste/tableau piles:",
    ]
    for idx, pile in enumerate(state.get("waste", []), 1):
        lines.append(f"Pile {idx}: {_card_list(pile)}")
    return _prefix("SPIDER SOLITAIRE STATE:", "\n".join(lines))


def text_star_battle(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        "Region grid; each number is a region index:\n"
        f"{_rows_table(state.get('regions', []))}\n"
        f"Currently placed stars: {state.get('stars', [])}\n"
        "Any hidden completed-board answer is intentionally omitted."
    )
    return _prefix("STAR BATTLE STATE:", body)


def text_sudoku(state: dict[str, Any], item: dict[str, Any]) -> str:
    board = [["." if cell in (0, None, "") else cell for cell in row] for row in state.get("board", [])]
    body = (
        f"Sudoku size: {state.get('size')}.\n"
        "Board, where '.' means empty:\n"
        f"{_rows_table(board)}\n"
        f"Region/color information: {state.get('colors', {})}"
    )
    return _prefix("SUDOKU STATE:", body)


def text_tangram(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        "Tangram grid; entries identify visible piece occupancy:\n"
        f"{_rows_table(state.get('grid', []))}\n"
        f"Configuration: {state.get('config', {})}\n"
        f"Removed pieces visible/asked about: {state.get('removed_pieces', [])}"
    )
    return _prefix("TANGRAM STATE:", body)


def text_tents(state: dict[str, Any], item: dict[str, Any]) -> str:
    width, height = state.get("size", [0, 0])
    grid = [["." for _ in range(width)] for _ in range(height)]
    for r, c in state.get("tree_positions", []):
        if 0 <= r < height and 0 <= c < width:
            grid[r][c] = "R"
    for r, c in state.get("tent_positions", []):
        if 0 <= r < height and 0 <= c < width:
            grid[r][c] = "T"
    all_final_tents = state.get("tent_positions", []) + state.get("removed_tents", [])
    row_targets = [0 for _ in range(height)]
    col_targets = [0 for _ in range(width)]
    for r, c in all_final_tents:
        if 0 <= r < height:
            row_targets[r] += 1
        if 0 <= c < width:
            col_targets[c] += 1
    body = (
        "Grid: R=tree, T=currently placed tent, .=empty.\n"
        f"{_compact_grid(grid)}\n"
        f"Row target tent counts: {row_targets}\n"
        f"Column target tent counts: {col_targets}\n"
        f"Tree positions: {state.get('tree_positions', [])}\n"
        f"Current tent positions: {state.get('tent_positions', [])}"
    )
    return _prefix("TENTS STATE:", body)


def text_tetris(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        f"Grid size: {state.get('rows')} rows x {state.get('cols')} columns.\n"
        "Board grid, where 0 usually means empty and nonzero values mean occupied/color cells:\n"
        f"{_rows_table(state.get('grid', []))}"
    )
    return _prefix("TETRIS STATE:", body)


def text_tictactoe(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = "Board:\n" + _rows_table(state.get("board", []))
    return _prefix("TICTACTOE STATE:", body)


def text_ultra_tictactoe(state: dict[str, Any], item: dict[str, Any]) -> str:
    lines = [
        "Ultra tic-tac-toe consists of 3x3 nine-grids; each nine-grid contains a 3x3 local board.",
        f"Rows: {state.get('rows')}, columns: {state.get('cols')}",
        f"Last step: {state.get('last_step')}",
        f"Total placed pieces: {state.get('total_steps')}",
        f"Marked middle cells: {state.get('middle_cell_count')}",
        "Visible pieces:",
    ]
    for piece in state.get("piece_info", []):
        lines.append(
            f"- nine_grid={piece.get('nine_grid')}, local_position={piece.get('position')}, player={piece.get('type')}"
        )
    lines.append("The hidden strategy hint is intentionally omitted.")
    return _prefix("ULTRA TICTACTOE STATE:", "\n".join(lines))


def text_word_search(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        f"Grid size: {state.get('size')}.\n"
        f"Question type: {state.get('question_type')}\n"
        "Letter grid:\n"
        f"{_rows_table(state.get('grid', []))}"
    )
    return _prefix("WORD SEARCH STATE:", body)


def text_zuma(state: dict[str, Any], item: dict[str, Any]) -> str:
    body = (
        f"Track: {state.get('track', [])}\n"
        f"Balls on track: {state.get('balls', [])}\n"
        f"Frog/shooter: {state.get('frog', {})}"
    )
    return _prefix("ZUMA STATE:", body)


ADAPTERS: dict[str, Adapter] = {
    "2d_turing_machine": text_2d_turing_machine,
    "3d_maze": text_3d_maze,
    "3dreconstruction": text_3d_reconstruction,
    "3DReconstruction": text_3d_reconstruction,
    "chess_ranger": text_chess_ranger,
    "freecell": text_freecell,
    "hue": text_hue,
    "jewel2": text_jewel2,
    "klondike": text_klondike,
    "langton_ant": text_langton_ant,
    "lifegame": text_lifegame,
    "maze": text_maze,
    "minecraft": text_minecraft,
    "minesweeper": text_minesweeper,
    "pacman": text_pacman,
    "PyramidChess": text_pyramid_chess,
    "pyramidchess": text_pyramid_chess,
    "rhythm_game": text_rhythm_game,
    "rubiks_cube": text_rubiks_cube,
    "snake": text_snake,
    "sokoban": text_sokoban,
    "space_invaders": text_space_invaders,
    "spider": text_spider_solitaire,
    "spider_solitaire": text_spider_solitaire,
    "star-battle": text_star_battle,
    "star_battle": text_star_battle,
    "sudoku": text_sudoku,
    "tangram": text_tangram,
    "tengram": text_tangram,
    "tents": text_tents,
    "tetris": text_tetris,
    "tictactoe": text_tictactoe,
    "ultra_tictactoe": text_ultra_tictactoe,
    "word_search": text_word_search,
    "zuma": text_zuma,
}


ALIASES = {
    "3dreconstruction": "3DReconstruction",
    "spider": "spider_solitaire",
    "star_battle": "star-battle",
    "tengram": "tangram",
}


def get_adapter(game: str) -> Adapter:
    normalized = ALIASES.get(game, game)
    if normalized not in ADAPTERS:
        raise KeyError(f"No text conversion adapter registered for game: {game}")
    return ADAPTERS[normalized]
