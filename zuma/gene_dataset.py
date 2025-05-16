import os
from gene_gamedata import draw_game
from gene_qa import generate_qa

def main():
    # 调用 draw_game 20 次，即生成 20 张图，每张图 5 个问题
    dataset_size = 100
    for i in range(dataset_size):
        print(i)
        draw_game("spiral", 0.3, 0.2)

    # 遍历 states 文件夹中的所有 JSON 文件
    state_files = sorted(
        [f for f in os.listdir("states") if f.endswith(".json")],
        key=lambda x: int(x.split(".")[0])
    )

    # 遍历每个 state 文件名，调用 generate_qa
    for state_file in state_files:
        state_path = os.path.join("states", state_file)  # 获取完整路径
        generate_qa(state_path)  # 直接传递文件名

if __name__ == "__main__":
    main()
