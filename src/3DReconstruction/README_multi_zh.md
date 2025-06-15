# 3D 重建游戏多问题数据集生成器

这是一个用于生成 3D 重建游戏相关问答数据集的工具的增强版本。与原始版本不同，这个生成器能够为每个游戏状态（图片）生成多种类型的问题，使得最后的数据集中图片数量少于问答对总数。

## 安装依赖：
```bash
pip install -r requirements.txt
```

依赖包括：

- Python 3.6+
- NumPy >= 1.19.0
- Matplotlib >= 3.3.0
- tqdm >= 4.65.0

## 游戏规则

与原始版本相同，规则包括：

1. 游戏空间：在 3x3x3 的立方体网格中进行
2. 坐标系统：位置 (x,y,z) 的范围是 1 到 3，其中 (1,1,1) 位于前-左-底部
3. 位置规则：每个位置最多只能放置一个体素
4. 连接规则：所有体素必须面对面相连
5. 体素限制：有最大可添加体素数量限制
6. 放置规则：新体素只能放在与现有体素相邻的位置
7. 投影规则：
   - 正视图 (Z-Y)：从X轴负方向观察（前到后），Y轴为水平，Z轴为垂直
   - 侧视图 (Z-X)：从Y轴正方向观察（左到右），X轴为水平，Z轴为垂直
   - 投影中的单元格如果该视线上有体素则显示为1
8. 胜利条件：使用不超过限制数量的体素匹配目标投影

## 与原始版本的区别

本版本的主要特点：

1. **一对多映射**：每个游戏状态（图片）会生成多个不同类型的问题
2. **效率提升**：减少了生成的图片和状态文件数量，同时保持问答对数量不变
3. **一致性增强**：连续的问答对会对应同一个游戏状态，便于评测和理解
4. **ID命名改进**：使用了新的ID命名方式，使得问答对与游戏状态之间的对应关系更加清晰

## 数据集生成原理

多问题生成器的工作流程：

1. 首先生成指定数量的游戏状态（每个状态包含一张图片和一个状态文件）
2. 对每个游戏状态生成所有6种类型的问题（填空题和选择题）
3. 最终数据集中的问答对数量 = 游戏状态数量 × 6

## 难度说明

与原始版本相同，游戏包含两种难度级别：

### 1. 问题难度（qa_level）
根据问题类型固定的难度级别：

- Easy 难度：计数(Count)和位置检查(Position)问题
- Medium 难度：投影检查(Projection)和动作结果(ActionOutcome)问题
- Hard 难度：策略优化(StrategyOptimization)和转换路径(TransitionPath)问题

### 2. 立体结构难度（plot_level）
根据体素数量定义的难度级别：

- Easy：3-5 个体素
- Medium：6-10 个体素
- Hard：11-15 个体素

### 难度分配

你可以通过 --level-ratios 参数设置游戏状态的难度分布比例：

- 格式：x:y:z（例：0.2:0.2:0.6）
- 三个数字分别代表 Easy:Medium:Hard 的比例
- 可以缺省最多一个值，缺省值会自动计算（保证总和为 1）
- 如果不设置，默认平均分配（每种难度各占三分之一）

## 使用方法

### 命令行参数

```bash
python multi_gen.py [参数]
```

可用参数：

- `--total-states N`：生成 N 个游戏状态（默认：100）
  - 生成的问答对数量将是 N * 6
- `--level-ratios RATIOS`：设置难度级别的比例
  - 格式：0.2:0.2:0.6
  - 可以缺省最多一个值
- `--output PATH`：设置输出目录（默认：reconstruction_dataset）

### 使用示例

1. 生成 50 个游戏状态（结果为 300 个问答对），采用默认难度分布：
```bash
python multi_gen.py --total-states 50
```

2. 设置难度级别比例：
```bash
# 生成20个游戏状态，难度比例为 Easy:Medium:Hard = 0.2:0.2:0.6
python multi_gen.py --total-states 20 --level-ratios 0.2:0.2:0.6

# 缺省第一个值，自动计算为 0.4:0.2:0.4
python multi_gen.py --total-states 20 --level-ratios :0.2:0.4
```

## 输出格式

生成的数据集将保存在 `reconstruction_dataset` 目录下：

```
reconstruction_dataset/
├── data.json           # 数据集文件
├── images/             # 可视化图片（数量等于游戏状态数）
│   └── reconstruction_state_*.png
└── states/             # 状态文件（数量等于游戏状态数）
    └── reconstruction_state_*.json
```

### 数据集格式

每个问题条目包含以下字段：
- data_id：数据标识符（格式：reconstruction_state_XXXXX_qa_TYPE_YYYYY）
- qa_type：问题类型（StateInfo/ActionOutcome/StrategyOptimization/TransitionPath）
- question_id：问题编号
- question_description：问题类型描述
- image：图片路径
- state：状态文件路径
- plot_level：立体结构难度级别（Easy/Medium/Hard）
- qa_level：问题难度级别（Easy/Medium/Hard）
- question：问题描述
- answer：答案
- analysis：解析
- options：选项（仅选择题）

### 状态文件格式

与原始版本相同：
```json
{
   "voxel_positions": [[1,1,1], [1,2,1], [2,2,1]],  // 当前结构中的体素位置列表
   "target_yz_projection": [                        // Y-Z投影（正视图）矩阵
      [1, 1, 0],  // z = 1 层（底层）的投影
      [0, 1, 0],  // z = 2 层（中层）的投影
      [1, 0, 0]   // z = 3 层（顶层）的投影
   ],
   "target_xz_projection": [                        // X-Z投影（侧视图）矩阵
      [1, 1, 0],  // z = 1 层（底层）的投影
      [1, 0, 0],  // z = 2 层（中层）的投影
      [0, 0, 1]   // z = 3 层（顶层）的投影
   ],
   "remaining_voxels": 2                            // 剩余可用的体素数量
}
```

## 与原版的对比

| 特性 | 原始版本 (main.py) | 多问题版本 (multi_gen.py) |
|------|-------------------|-------------------------|
| 问答对与图片关系 | 1:1 (每个问答对一张图片) | 6:1 (每个图片6个问答对) |
| 生成100个问答对所需图片 | 100张 | 约17张 |
| 问题类型分布 | 可自定义不同类型比例 | 每个状态生成所有6种类型 |
| 命令行参数 | --total, --qa-types, --type-ratios, --level-ratios | --total-states, --level-ratios |
| 文件命名 | reconstruction_XXXXX | reconstruction_state_XXXXX_qa_TYPE_YYYYY |

## 注意事项

1. 每个游戏状态会生成6个不同类型的问题，总问答对数量是游戏状态数的6倍
2. 难度级别比例控制的是游戏状态的分布，而不是问答对的分布
3. 如果需要大量数据，建议先生成少量样本进行验证
4. 图片和状态文件会自动保存在 `reconstruction_dataset` 目录下
