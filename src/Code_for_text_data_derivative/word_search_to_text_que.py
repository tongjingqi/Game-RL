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
    gridStr = '\n'.join([f'row {index+1}: ['+', '.join(map(str,row))+']' for index,row in enumerate(grid)])
    line['question'] = 'Grid:\n'+gridStr+'\n\n'+line['question']
    del line['state']
with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)
    