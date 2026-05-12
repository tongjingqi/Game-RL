import json
import os

color_mapping = {
    0: "white",
    1: "gray",
    2: "red"
}

def grid_to_table(grid):
    """Convert the grid to a row-major symbolic table."""
    text_grid = []
    for row in grid:
        text_row = ['#' if cell == 1 else '0' if cell == 0 else '&' for cell in row]
        text_grid.append(text_row)
    return text_grid

def transform_grid_to_table(data_json_path):
    # Read the original data.json file
    with open(data_json_path, 'r', encoding='utf-8') as f:
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
        with open(state_path, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        grid = state_data["grid"]
        rows = state_data["rows"]
        cols = state_data["cols"]

        # 生成网格的文本表示
        grid_table = grid_to_table(grid)        

        # Create result object
        new_json = {
            "grid_table": grid_table,
            "grid_rows": rows,
            "grid_cols": cols
        }
        
        item["question"] = """The grid image that you need is described in json format as follows:
        The json contains the following fields:
        - grid_table: A 2D row-major list of grid cells. The row index and column index are 0-based.
          - "0" means a white empty cell.
          - "#" means a gray cell occupied by a previously placed tetromino.
          - "&" means a red cell occupied by the active falling tetromino.
        - grid_rows: Total number of rows in the grid
        - grid_cols: Total number of columns in the grid
        
        The grid visualization:
        """ + json.dumps(new_json) + """
        Please answer the question based on the grid table.
        """+item["question"]

        results.append(item)

    return results


def save_results(results, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    data_json_path = "data.json"
    output_path = "data_text.json"
    results = transform_grid_to_table(data_json_path)
    save_results(results, output_path)
    
    print(f"Transformed {len(results)} grid(s) to table format and saved to {output_path}")
