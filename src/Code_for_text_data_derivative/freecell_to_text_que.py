import json

def read_json_data(json_path):
    with open(json_path,"r",encoding="utf-8") as f:
        data = json.load(f)
    return data

data=read_json_data("data.json")
for line in data:
    StatePath=line["state"]
    StateData=read_json_data(StatePath)

    CascadeState=StateData["cascade_piles"]
    FreeCellState=StateData["free_cells"]
    FoundationState=StateData["foundation_piles"]

    CascadeDes="\n".join([f"From the bottom to the top,Cascade pile {idx} has the following cards:{pile}" for idx,pile in enumerate(CascadeState)])
    FreeCellDes="\n".join([f"Freecell {idx}:{pile}" for idx,pile in enumerate(FreeCellState)])
    FoundationDes="\n".join([f"From the bottom to the top,Foundation pile {idx} with suit {suit} has the following cards:{pile}" for idx,(suit,pile) in enumerate(FoundationState.items(),0)])

    StateString="The current state of the Freecell game are as follows:\n"+CascadeDes+"\n"+FreeCellDes+"\n"+FoundationDes+"\n"

    question=line["question"]
    id=line["question_id"]
    
    if id==1 or id== 3:
        index=question.find("Now")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")
    else:
        index=question.find("Which")
        if index != -1:
            modified_question=question[:index]+StateString+"Based on the rules and state described above,you are requried to answer the following question\n"+question[index:]
            line["question"]=modified_question
        else:
            print(f"Error when modifying question_id {id}")

with open('data_text.json', 'w') as f:
    json.dump(data, f, indent=4)   
    