# 祖玛问答数据集生成器

这个模块用于生成祖玛风格的问答数据。玩家控制青蛙向轨道上的弹珠链发射彩色弹珠，目标是在弹珠到达终点黑洞前尽量消除它们。

一个游戏示例图片：

![游戏示例图片](zuma_dataset_example/images/0002.png)

## 游戏画面说明

- 青蛙用一个三角形表示，三角形中的彩色圆球表示下一发将要射出的弹珠。
- 彩色弹珠沿灰色轨道向黑洞滚动。
- 青蛙周围的虚线把画面划分成 8 个方向区域，部分题目会直接使用这些方向。
- 题目中的角度都以青蛙中心为原点，并以正 x 轴方向为 `0°`。

## 难度设计

结合本仓库中的设计，`plot_level` 主要由轨道长度和弹珠数量决定：

- `Easy`：轨道较短、弹珠较少
- `Medium`：轨道更长、弹珠更多
- `Hard`：轨道很长且弹珠密集

## 支持的题型

1. 询问青蛙下一发弹珠的颜色
2. 统计轨道上某种颜色弹珠的数量
3. 统计某个方向上相邻同色弹珠组的数量
4. 判断按给定角度射击时会命中什么颜色的弹珠
5. 预测按给定角度射击后的结果
6. 求一步内最优的消除策略

这些题型覆盖了 `Target Perception`、`State Prediction` 和 `Strategy Optimization`。

## 代码结构

- `gene_gamedata.py`：绘制轨道、青蛙和弹珠，并保存 `states/*.json`
- `gene_qa.py`：根据状态文件生成 QA
- `gene_dataset.py`：批量生成入口

## 运行方式

安装依赖：

```bash
pip install matplotlib numpy
```

当前脚本使用相对路径写入 `images/`、`states/` 和 `data.json`，且不会自动创建目录。比较稳妥的使用方式是：

1. 新建一个工作目录，并提前创建空的 `images/` 和 `states/`。
2. 将 `gene_gamedata.py`、`gene_qa.py`、`gene_dataset.py` 放到该目录中。
3. 运行：

```bash
python gene_dataset.py
```

如需调整生成规模，可直接修改 `gene_dataset.py` 里的 `dataset_size`。

## 纯文本 QA 数据转换

如果需要把该游戏的多模态 QA 数据转换为纯文本版本，可以在仓库根目录运行统一转换脚本：

```bash
python src/Code_for_text_data_derivative/convert_text_data.py --game zuma --data src/zuma/zuma_dataset_example/data.json --output src/zuma/zuma_dataset_example/data_text.json
```

转换脚本会读取每条数据对应的 `state` JSON，把可见游戏状态转换为文本并插入到原问题前面，默认输出的 `data_text.json` 不再保留 `image` 或 `state` 字段。

下面的纯文本状态片段与本 README 开头展示的示意图片对应：

```text
ZUMA STATE:
Track: {'plot_level': 'Medium', 'hole_position': {'x': -1.9336408014512254, 'y': -2.7464934542910426}}
Balls on track: [{'position': {'x': 2.325093698074389, 'y': -5.6107475945526035}, 'color': 'green'}, {'position': {'x': 1.736756 ...
Frog/shooter: {'position': {'x': 0.4042746249648226, 'y': -0.5988457693062086}, 'angle': -163, 'next_ball_color': 'green', 'afte ...
```

## 输出内容

- `images/*.png`：生成的游戏截图
- `states/*.json`：轨道、黑洞、青蛙、弹珠的位置和颜色信息
- `data.json`：问答数据
