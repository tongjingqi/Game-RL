# 3D 重建游戏问答数据集生成器

这是一个用于生成 3D 重建游戏相关问答数据集的工具。该工具可以生成多种类型的问题，包括填空题和选择题，用于测试对 3D 重建游戏规则和策略的理解。

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

## 难度说明

游戏中存在两种不同的难度级别：

### 1. 问题难度（qa_level）
这是根据问题类型固定的难度级别：

- Easy 难度：
  - Count：计算当前结构中的体素数量
  - Position：检查特定位置是否有体素

- Medium 难度：
  - Projection：检查当前结构的投影是否匹配目标视图
  - ActionOutcome：预测添加指定体素后的投影矩阵

- Hard 难度：
  - StrategyOptimization：计算达到目标所需的最少体素数量
  - TransitionPath：选择正确的体素添加序列以满足目标投影

### 2. 立体结构难度（plot_level）
这是根据体素数量来定义的难度级别：

- Easy：3-5 个体素，需要填 3 个
- Medium：6-10 个体素，需要填 4 个
- Hard：11-15 个体素，需要填 5 个

### 难度分配

你可以通过 --level-ratios 参数设置问题的难度（plot_level）分布比例：

- 格式：x:y:z（例：0.2:0.2:0.6）
- 三个数字分别代表 Easy:Medium:Hard 的比例
- 可以缺省最多一个值，缺省值会自动计算（保证总和为 1）
- 如果不设置，默认平均分配（每种难度各占三分之一）

## 问题数量分配

生成器支持两种问题数量分配方式：

1. 平均分配（默认）：
   - 如果没有指定问题类型比例，则平均分配给 6 种问题类型
   - 例如：总数 100 个问题，每种类型约 16-17 个
   - 余数会从前往后依次分配给各类型

2. 按比例分配：
   - 通过 --type-ratios 参数指定每种类型的比例
   - 比例之和必须等于 1
   - 会精确计算每种类型的问题数量
   - 例如：指定 count=0.2 时，生成 100 个问题中会有 20 个 count 类型的问题

注意：
- 使用比例分配时，最后一个类型会分配剩余的问题数量，以确保总数正确
- 建议每种类型至少生成 1 个问题，以保证数据集的多样性

## 问题类型

1. StateInfo 类型
   - Count：计算当前结构中的体素数量
   - Position：检查特定位置是否有体素
   - Projection：检查当前结构的投影是否匹配目标视图

2. ActionOutcome 类型
   - 预测在当前结构上添加指定体素后的投影矩阵（正视图或侧视图）
   - 答案需要以3x3矩阵的形式给出投影模式

3. TransitionPath 类型
   - 从多个选项中选择正确的体素添加序列，使得能满足目标投影
   - 考虑连通性、投影匹配和体素数量限制

4. StrategyOptimization 类型
   - 计算达到目标所需的最少体素数量
   - 如果当前结构已满足目标投影，则返回 0
   - 否则返回达到目标所需的最少体素数量

## 使用方法

### 命令行参数

```bash
python main.py [参数]
```

可用参数：

- `--total N`：生成 N 个问题（默认：100）
- `--qa-types TYPE1 TYPE2 ...`：指定要生成的具体问题类型（可多选）
  - count：计数问题
  - position：位置检查
  - projection：投影匹配
  - action_outcome：动作结果
  - strategy_optimization：策略优化
  - transition_path：转换路径
- `--type-ratios RATIOS`：设置问题类型的比例
  - 格式：0.2:0.2:0.2:0.2:0.1:0.1
  - 六个数字分别对应：count, position, projection, action_outcome, strategy_optimization, transition_path
  - 比例之和必须等于1
- `--level-ratios RATIOS`：设置难度级别的比例
  - 格式：0.2:0.2:0.6
  - 可以缺省最多一个值

### 使用示例

1. 生成 100 个问题，全采用默认配置（即：问题种类平均、问题难度平均）：
```bash
python main.py --total 100
```

2. 生成特定类型的问题：
```bash
python main.py --total 100 --qa-types count position projection
```

3. 使用自定义问题类型比例：
```bash
python main.py --total 100 --type-ratios 0.2:0.2:0.2:0.2:0.1:0.1
```

4. 设置难度级别比例：
```bash
# 生成100个问题，难度比例为 Easy:Medium:Hard = 0.2:0.2:0.6
python main.py --total 100 --level-ratios 0.2:0.2:0.6

# 缺省第一个值，自动计算为 0.4:0.2:0.4
python main.py --total 100 --level-ratios :0.2:0.4
```

5. 组合使用多个参数：
```bash
python main.py --total 100 \
    --type-ratios 0.2:0.2:0.2:0.2:0.1:0.1 \
    --level-ratios 0.2:0.2:0.6
```

### Python API 使用

```python
from QAGenerator import ThreeDReconstructionQAGenerator

# 创建生成器实例
generator = ThreeDReconstructionQAGenerator()

# 使用默认设置生成数据集
generator.generate_all_datasets(total_samples=100)

# 可选：使用自定义问题类型比例
custom_ratios = {
    'count': 0.2,
    'position': 0.2,
    'projection': 0.2,
    'action_outcome': 0.2,
    'strategy_optimization': 0.1,
    'transition_path': 0.1
}

# 可选：使用自定义难度比例
level_ratios = [0.2, 0.2, 0.6]  # Easy, Medium, Hard

# 生成自定义数据集
generator.generate_all_datasets(
    total_samples=100,
    type_ratios=custom_ratios,
    plot_level_ratios=level_ratios
)
```

## 输出格式

生成的数据集将保存在 `reconstruction_dataset` 目录下：

```
reconstruction_dataset/
├── data.json           # 数据集文件
├── images/             # 可视化图片
│   └── reconstruction_*.png
└── states/            # 状态文件
    └── reconstruction_*.json
```

### 数据集格式

每个问题条目包含以下字段：
- data_id：数据标识符
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

### 状态文件（states/*.json）格式
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
- voxel_positions：列表中每个元素是一个 [x,y,z] 坐标，表示当前结构中已有的体素位置
- target_yz_projection：3x3 矩阵，表示正视图（从X轴负方向看）的目标投影
   * 每行代表一个z坐标层（从上到下分别是 z = 3, 2, 1）
   * 每行中的元素代表该层上的y坐标（从左到右是 y = 1, 2, 3）
   * 1 表示该位置在投影上可见，0 表示不可见
- target_xz_projection：3x3 矩阵，表示侧视图（从Y轴正方向看）的目标投影
   * 每行代表一个z坐标层（从上到下分别是 z = 3, 2, 1）
   * 每行中的元素代表该层上的x坐标（从左到右是 x = 1, 2, 3）
   * 1 表示该位置在投影上可见，0 表示不可见
- remaining_voxels：整数，表示还可以添加的体素数量

## 注意事项

1. 生成的问题数量应该合理，建议每种类型至少生成 1 个问题
2. 问题类型比例之和必须等于 1
3. 难度级别比例之和必须等于 1
4. 图片和状态文件会自动保存在 `reconstruction_dataset` 目录下
5. 可以通过调整参数来控制不同类型问题的比例和难度
