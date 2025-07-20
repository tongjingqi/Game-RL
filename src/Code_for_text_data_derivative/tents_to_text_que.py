import json
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
data=read_json('data.json')
for line in data:
    statePath = line['state']
    stateData = read_json(statePath)
    width, height = stateData['size']
    # 计算每行和每列中的帐篷数量
    row_tent_counts = [0] * height
    col_tent_counts = [0] * width
    all_tents = stateData['tent_positions'] + stateData['removed_tents']
    for tx, ty in all_tents:
        row_tent_counts[tx] += 1
        col_tent_counts[ty] += 1   
    #line['question'] = 'Grid:\n'+grid+"\n(Each block is 'O'(red), 'X'(blue) or ' '(white).)\n"+line['question']
    line['question'] = 'Grid:\nThis is a gird with a width of '+str(width)+' and a height of '+str(height)+'.\n'+\
    'The tent positions are:' + str(stateData['tent_positions']) + '\n'+\
    'The tree positions are:' + str(stateData['tree_positions']) + '\n'+\
    'The black numbers on top of each column correspond to the column indices, which range from 0 to ' + str(width-1) + ' from left to right.\n'+\
    'The black numbers on the left of each row correspond to the row indices, which range from 0 to ' + str(height-1) + ' from top to bottom.\n'+\
    'The blue numbers on top of each column are (starting from column 0):' + str(col_tent_counts) + '\n'+\
    'The blue numbers on the left of each row are (starting from row 0):' + str(row_tent_counts) + '\n' + line['question']

    del line['state']
with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)
    