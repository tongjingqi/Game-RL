import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

def draw_pyramid_2d(layers,plot_level):
    PLOT_LEVEL = {"Easy":3,"Medium":4,"Hard":5}
    fig, axs = plt.subplots(1, PLOT_LEVEL[plot_level], figsize=(25, 6))  # 增加图形的宽度和高度

    # 定义颜色映射
    color_map = {'P0': 'blue', 'P1': 'red', '--': 'none'}

    # 绘制每一层的数据
    for i, (layer_id, layer_data) in enumerate(layers.items()):
        ax = axs[i]  # 获取当前子图
        ax.set_title(f'Level {layer_id}', fontsize=40)  # 设置子图标题，减少字体大小
        
        # 设置坐标轴范围
        ax.set_xlim(-0.5, len(layer_data[0]) - 0.5)
        ax.set_ylim(-0.5, len(layer_data) - 0.5)
        
        # 设置坐标轴刻度
        ax.set_xticks(np.arange(len(layer_data[0])))
        ax.set_yticks(np.arange(len(layer_data)))
        ax.set_xticklabels([str(x) for x in range(len(layer_data[0]))], fontsize=40)
        ax.set_yticklabels([str(y) for y in range(len(layer_data))], fontsize=40)
        
        ax.invert_xaxis()
        ax.set_xlabel("x-axis", fontsize=30)
        ax.set_ylabel("y-axis", fontsize=30)
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')
        
        # 绘制圆形
        for x, row in enumerate(layer_data):
            for y, cell in enumerate(row):
                if cell != '--':
                    ax.scatter(x, y, s=2000, c=color_map[cell], marker='o', edgecolor='black')  # 调整y坐标

    # 调整子图间距
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2, wspace=0.3)
    # fig.savefig(save_path)
    buf = io.BytesIO()
    plt.savefig(buf, format="PNG")
    plt.close(fig)
    buf.seek(0)  # 将缓冲区的指针移动到开头
    
    # 从字节流中打开图像为Pillow的Image对象
    image = Image.open(buf)
    return image
    
def draw_pyramid_3d(plot_level,layers=None,reverse = False):
    # Define the colors for the balls
    color_map = {"P0": "blue", "P1": "red", "--": None}
    
    if layers == None:
        print("Nothing to plot")
        return

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')

    ball_radius = 0.6  # Radius of the balls

    # Draw each layer in 3D
    for level, grid in layers.items():
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell != "--":
                    # Calculate positions to align higher layers' balls on the center of lower layers
                    x = i + level * 0.5
                    y = j + level * 0.5
                    z = level  # Start z-axis from 0

                    # Draw a sphere to represent the ball
                    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                    sphere_x = ball_radius * np.cos(u) * np.sin(v) + x
                    sphere_y = ball_radius * np.sin(u) * np.sin(v) + y
                    sphere_z = ball_radius * np.cos(v) + z
                    ax.plot_surface(sphere_x, sphere_y, sphere_z, color=color_map[cell], edgecolor="k", linewidth=0.5)
                    
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=15, label='PLAYER_0'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='PLAYER_1')
    ]
    ax.legend(handles=legend_elements, loc='upper left',prop={'size': 20},markerscale=2.0)
    PLOT_LEVEL = {"Easy":3,"Medium":4,"Hard":5}
    ind_length = PLOT_LEVEL[plot_level]
    if reverse:
        ax.set_xlim(-1,ind_length)
        ax.set_ylim(ind_length,-1)
    else:
        ax.set_xlim(ind_length,-1)
        ax.set_ylim(-1,ind_length)

    ax.set_zlim(-0.5,ind_length)
    ax.set_xlabel("X-axis",fontsize=15)
    ax.set_ylabel("Y-axis",fontsize=15)
    ax.set_zlabel("Z-axis",fontsize=15)
    ax.set_xticks(range(0,ind_length))
    ax.set_yticks(range(0,ind_length))
    ax.set_zticks(range(0,ind_length)) 
    # if(plot_level == "Easy"):
    # elif(plot_level == "Medium"):
    #     ax.set_xticks(range(0,4)) 
    #     ax.set_yticks(range(0,4)) 
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='z', labelsize=15)
    # ax.set_title("3D View of the Pyramid",fontsize=20)
    # fig.savefig(save_path)
    buf = io.BytesIO()
    plt.savefig(buf, format="PNG")
    plt.close(fig)
    buf.seek(0)  # 将缓冲区的指针移动到开头
    
    # 从字节流中打开图像为Pillow的Image对象
    image = Image.open(buf)
    return image


    
def combine_image(save_path,image1,image2):
    # image1 = Image.open(image1_path)
    # image2 = Image.open(image2_path)
    image2 = image2.resize((1200,300))
    # print("image1:",image1.size)
    # print("image2:",image2.size)
    crop_box = (0,155,1200,1020)
    image1 = image1.crop(crop_box)
    new_image = Image.new('RGBA', (image1.width, image1.height + image2.height))
    new_image.paste(image2, (0, 0))
    new_image.paste(image1, (0, image2.height))
    new_image = new_image.resize((550,550))
    new_image.save(save_path)
    
def combine_image_generate(id,layers,plot_level,example = False):
    if example:
        path = f"pyramidchess_dataset_example/images/board_{str(id).zfill(5)}.png"
    else:
        path = f"pyramidchess_dataset/images/board_{str(id).zfill(5)}.png"
    image1 = draw_pyramid_3d(layers=layers,plot_level=plot_level)
    image2 = draw_pyramid_2d(layers=layers,plot_level=plot_level)
    combine_image(path,image1,image2)



def test():
    # layers = {
    # 0: [
    #     [
    #         "P0",
    #         "P0",
    #         "P0",
    #         "P0",
    #         "P1"
    #     ],
    #     [
    #         "P0",
    #         "--",
    #         "P0",
    #         "P1",
    #         "P1"
    #     ],
    #     [
    #         "P1",
    #         "P1",
    #         "P1",
    #         "P0",
    #         "P0"
    #     ],
    #     [
    #         "P0",
    #         "P0",
    #         "P1",
    #         "P1",
    #         "P0"
    #     ],
    #     [
    #         "P1",
    #         "P1",
    #         "P0",
    #         "P0",
    #         "P1"
    #     ]
    # ],
    # 1: [
    #     [
    #         "--",
    #         "--",
    #         "P0",
    #         "P1"
    #     ],
    #     [
    #         "--",
    #         "--",
    #         "P0",
    #         "P1"
    #     ],
    #     [
    #         "P0",
    #         "P1",
    #         "--",
    #         "--"
    #     ],
    #     [
    #         "P0",
    #         "P0",
    #         "--",
    #         "--"
    #     ]
    # ],
    # 2: [
    #     [
    #         "--",
    #         "--",
    #         "--"
    #     ],
    #     [
    #         "--",
    #         "--",
    #         "--"
    #     ],
    #     [
    #         "P1",
    #         "--",
    #         "--"
    #     ]
    # ],
    # 3: [
    #     [
    #         "--",
    #         "--"
    #     ],
    #     [
    #         "--",
    #         "--"
    #     ]
    # ],
    # 4: [
    #     [
    #         "--"
    #     ]
    # ]
    # }   
    layers = {
    0: [
        [
            "P0",
            "P1",
            "P0",
            "P0"
        ],
        [
            "P1",
            "P0",
            "P1",
            "P0"
        ],
        [
            "P0",
            "P0",
            "P1",
            "P1"
        ],
        [
            "P1",
            "P0",
            "P0",
            "P1"
        ]
    ],
    1: [
        [
            "P0",
            "P0",
            "P1"
        ],
        [
            "P0",
            "P1",
            "P0"
        ],
        [
            "P1",
            "P0",
            "P1"
        ]
    ],
    2: [
        [
            "P1",
            "P0"
        ],
        [
            "P1",
            "P1"
        ]
    ],
    3: [
        [
            "P1"
        ]
    ]
}
#     layers = {
#     0: [
#         ["--","P0","--"],
#         ["P0","P1","P1"],
#         ["P0","P0","P1"]
#     ],
#     1: [
#         ["--","--"],
#         ["P1","P0"]
#     ],
#     2: [
#         ["--"]
#     ]
# }
    combine_image_generate(id=123,layers=layers,plot_level="Medium",example=True)
    
