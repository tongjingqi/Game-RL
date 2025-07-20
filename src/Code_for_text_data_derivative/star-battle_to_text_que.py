import json

def read_json_data(json_path):
    with open(json_path,"r",encoding="utf-8") as f:
        data = json.load(f)
    return data

data=read_json_data("data.json")
for line in data:
    StatePath=line["state"]
    StateData=read_json_data(StatePath)

    regions=StateData["regions"]
    stars=StateData["stars"]

    regions_converted = [
        [(x, y) for x, y in region]  # 将每个子列表中的 [x, y] 转换为 (x, y)
        for region in regions
    ]

    stars_converted = [(x, y) for x, y in stars]

    RegionsDes="\n".join([f"Region {idx} has the following cells:{cells}" for idx,cells in enumerate(regions_converted)])
    StarsDes=f"Some stars have already been placed in the following cells:{stars_converted}"

    StateString="The current state of this star-battle puzzle are as follows:\n"+RegionsDes+"\n"+StarsDes+"\n"

    question=line["question"]
    id=line["question_id"]

    if id==2:
        index=question.find("Given the current state")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")
    elif id==3:
        index=question.find("In the current puzzle state")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")
    elif id==4:
        index=question.find("Based on the current puzzle state")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")
    elif id==1:
        index=question.find("Now")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")
    else:
        print("invalid id!")

with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)