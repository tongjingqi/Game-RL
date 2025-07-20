import json
import os

color_mapping = {
    0: "white",
    1: "gray",
    2: "red"
}

def grid_to_text(grid):
    """将网格转换为文本表示形式"""
    text_grid = []
    for row in grid:
        # 将数字转换为字符表示
        text_row = ['#' if cell == 1 else '0' if cell == 0 else '&' for cell in row]
        # 添加行注释
        row_str = "['" + "', '".join(text_row) + "'], # Row" + str(len(text_grid))
        text_grid.append(row_str)
    
    # 组合成完整的网格文本
    grid_text = "grid = [\n    " + "\n    ".join(text_grid) + "\n]"
    return grid_text

def transform_grid_to_table(data_json_path):
    # Read the original data.json file
    with open(data_json_path, 'r') as f:
        data_items = json.load(f)
    
    results = []
    
    # Process each item in the data.json file
    for item in data_items:
        # Get the state file path
        state_path = item["state"]
        
        # Check if the state file exists
        if not os.path.exists(state_path):
            print(f"Warning: State file not found at {state_path}")
            continue
        
        # Read the state file
        with open(state_path, 'r') as f:
            state_data = json.load(f)
        
        grid = state_data["grid"]
        rows = state_data["rows"]
        cols = state_data["cols"]

        # 生成网格的文本表示
        grid_text = grid_to_text(grid)        

        # Create result object
        new_json = {
            "grid_table": grid_text,
            "grid_rows": rows,
            "grid_cols": cols
        }
        
        item["question"] = """The grid image that you need is described in json format as follows:
        The json contains the following fields:
        - grid_table: A 2d list of grid cells, where each cell has:
          - row: The row index (0-based)
          - col: The column index (0-based) 
          - block_color: The color of the cell (0 for white, # for gray, & for red in the grid visualization)
        - grid_rows: Total number of rows in the grid
        - grid_cols: Total number of columns in the grid
        
        The grid visualization:
        """ + json.dumps(new_json) + """
        Please answer the question based on the grid table.
        """+item["question"]

        results.append(item)

    return results


def save_results(results, output_path):
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":

    data_json_path = "data.json"
    output_path = "data_text.json"
    results = transform_grid_to_table(data_json_path)
    save_results(results, output_path)
    
    print(f"Transformed {len(results)} grid(s) to table format and saved to {output_path}")