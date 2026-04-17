# 3D 重建游戏问答数据集生成器

这是一个用于生成 3D 重建游戏问答数据集的工具。当前目录提供两种生成方式：

1. `main.py`：标准模式，通常按 1 个游戏状态对应 1 个问答对生成数据。
2. `multi_gen.py`：多问题模式，先生成游戏状态，再为每个状态生成全部 6 种问题模板。

一个游戏示例图片：

![游戏示例图片](reconstruction_dataset_example/images/reconstruction_00002.png)

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括：

- Python 3.6+
- NumPy >= 1.19.0
- Matplotlib >= 3.3.0
- tqdm >= 4.65.0

## 游戏规则

1. 游戏空间：在 3x3x3 的立方体网格中进行。
2. 坐标系统：位置 `(x, y, z)` 的范围是 1 到 3，其中 `(1,1,1)` 位于前-左-底部。
3. 位置规则：每个位置最多只能放置一个体素。
4. 连接规则：所有体素必须面连接。
5. 放置规则：新体素只能放在与现有体素相邻的位置。
6. 投影规则：
   - 正视图（Y-Z）：从 X 轴负方向观察。
   - 侧视图（X-Z）：从 Y 轴正方向观察。
   - 若某条视线上存在体素，则投影对应位置为 `1`，否则为 `0`。
7. 目标：在可添加体素数量限制内，使结构匹配目标投影。

## 难度说明

游戏包含两类难度：

### 问题难度（qa_level）

- `Easy`
  - `count`：计算当前结构中的体素数量。
  - `position`：判断某个位置是否有体素。
- `Medium`
  - `projection`：判断当前结构的投影与目标投影的匹配情况。
  - `action_outcome`：预测添加指定体素后的投影结果。
- `Hard`
  - `strategy_optimization`：计算达到目标所需的最少新增体素数。
  - `transition_path`：选择满足目标投影的正确体素添加序列。

### 立体结构难度（plot_level）

- `Easy`：3-5 个体素
- `Medium`：6-10 个体素
- `Hard`：11-15 个体素

`--level-ratios` 使用 `x:y:z` 格式，对应 `Easy:Medium:Hard`。最多可以缺省一个值，未写的值会自动补足到 1。

## 标准模式：`main.py`

```bash
python main.py [参数]
```

可用参数：

- `--total N`：生成 N 个问题，默认 `100`
- `--qa-types TYPE1 TYPE2 ...`：指定题型，可选 `count`、`position`、`projection`、`action_outcome`、`strategy_optimization`、`transition_path`
- `--type-ratios RATIOS`：题型比例，例如 `0.2:0.2:0.2:0.2:0.1:0.1`
- `--level-ratios RATIOS`：结构难度比例，例如 `0.2:0.2:0.6`
- `--output PATH`：输出目录，默认 `reconstruction_dataset`

示例：

```bash
python main.py --total 100
python main.py --total 100 --qa-types count position projection
python main.py --total 100 --type-ratios 0.2:0.2:0.2:0.2:0.1:0.1 --level-ratios 0.2:0.2:0.6
```

## 多问题模式：`multi_gen.py`

```bash
python multi_gen.py [参数]
```

该模式先生成游戏状态，再为每个状态生成全部 6 种问题，因此：

- 问答对与图片/状态文件的关系约为 `6:1`
- 总问答对数量 = `total_states × 6`

可用参数：

- `--total-states N`：生成 N 个游戏状态，默认 `100`
- `--level-ratios RATIOS`：结构难度比例，例如 `0.2:0.2:0.6`
- `--output PATH`：输出目录，默认 `reconstruction_dataset`

示例：

```bash
python multi_gen.py --total-states 50
python multi_gen.py --total-states 20 --level-ratios 0.2:0.2:0.6
```

## 输出格式

输出会写入 `--output` 指定的目录；如果不传，则默认写入 `reconstruction_dataset/`：

### 标准模式输出

```text
reconstruction_dataset/
├── data.json
├── images/
│   └── reconstruction_*.png
└── states/
    └── reconstruction_*.json
```

### 多问题模式输出

```text
reconstruction_dataset/
├── data.json
├── images/
│   └── reconstruction_state_*.png
└── states/
    └── reconstruction_state_*.json
```

每个数据条目包含这些字段：

- `data_id`
- `qa_type`
- `question_id`
- `question_description`
- `image`
- `state`
- `plot_level`
- `qa_level`
- `question`
- `answer`
- `analysis`
- `options`（仅选择题）

## 状态文件格式

```json
{
  "voxel_positions": [[1, 1, 1], [1, 2, 1], [2, 2, 1]],
  "target_yz_projection": [
    [1, 1, 0],
    [0, 1, 0],
    [1, 0, 0]
  ],
  "target_xz_projection": [
    [1, 1, 0],
    [1, 0, 0],
    [0, 0, 1]
  ],
  "remaining_voxels": 2
}
```

- `voxel_positions`：当前结构中的体素坐标列表
- `target_yz_projection`：正视图目标投影矩阵
- `target_xz_projection`：侧视图目标投影矩阵
- `remaining_voxels`：还可添加的体素数量

## 注意事项

1. `main.py` 支持自定义题型比例；`multi_gen.py` 固定为每个状态生成全部 6 种问题。
2. 题型比例之和应为 1。
3. 难度比例之和应为 1。
4. 若只想快速查看样例，可直接查看 `reconstruction_dataset_example/`。
