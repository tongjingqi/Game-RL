import json
def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
data=read_json('data.json')
for line in data:
    statePath = line['state']
    stateData = read_json(statePath)
    grid = str(stateData['board'])
    # gridStr = '\n'.join([''.join(map(str,row)) for row in grid])
    # line['question'] = 'Grid:\n'+gridStr+"\n(Each block is 'O'(red), 'X'(blue) or ' '(white).)\n"+line['question']
    line['question'] = 'Grid:\n'+grid+"\n(Each block is 'O'(red), 'X'(blue) or ' '(white).)\n"+line['question']
    del line['state']
with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)
    