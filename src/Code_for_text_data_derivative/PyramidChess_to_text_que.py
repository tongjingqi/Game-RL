import json
from optparse import OptionParser

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

    
def convert_dict_to_str(data):
    """
    将字典转换为字符串
    """
    output_lines = []
    # 遍历字典，按数字顺序排序
    for level_key in sorted(data, key=int):
        output_lines.append(f"Level {level_key}:")
        # 遍历该level下的每一行，行号作为坐标
        for row_index, row in enumerate(data[level_key]):
            # 替换 P0 和 P1
            new_row = []
            for value in row:
                if value == "P0":
                    new_row.append("Blue")
                elif value == "P1":
                    new_row.append("Red")
                else:
                    new_row.append(value)
            # 将行坐标和转换后的行拼接起来，后面加个逗号（如示例所示）
            output_lines.append(f"Row{row_index} {new_row},")
        # 每个Level后增加一个空行
        output_lines.append("")
    return "\n".join(output_lines)

def main():
    parser = OptionParser()
    parser.add_option('-p', '--path',        default='data.json',          help='json file path',                   action='store', type='string', dest='path')
    (options, args) = parser.parse_args()
    data=read_json(options.path)
    for line in data:
        statePath = line['state']
        stateData = read_json(statePath)
        QuestionStr = convert_dict_to_str(stateData)
        line['question'] = 'Image:\n'+"Blue ball:PLAYER_0\nRed ball:PLAYER_1\n"+QuestionStr+line['question']
        del line['state']
    with open('data_text.json', 'w') as f:
        json.dump(data, f, indent=4)
        
if __name__ == "__main__":
    main()