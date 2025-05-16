#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from MultiQuestionGenerator import MultiQuestionGenerator

def parse_ratio_string(ratio_str):
    """解析难度比例字符串为列表"""
    if not ratio_str:
        return None
    try:
        values = ratio_str.split(':')
        if len(values) > 3:
            raise ValueError("难度比例格式错误，应为'0.2:0.2:0.6'")
        
        ratios = [0.0, 0.0, 0.0]
        # 处理缺省值
        if len(values) == 2:  # 缺省第一个值
            if values[0]:  # 第二个值
                ratios[1] = float(values[0])
            if values[1]:  # 第三个值
                ratios[2] = float(values[1])
            # 计算第一个值
            ratios[0] = 1.0 - ratios[1] - ratios[2]
        else:  # 完整指定三个值
            for i, v in enumerate(values):
                if v:  # 如果值不为空
                    ratios[i] = float(v)
        
        # 验证比例之和是否接近1
        total = sum(ratios)
        if not (0.99 <= total <= 1.01):  # 允许1%的误差
            raise ValueError(f"比例之和应为1，当前为{total}")
            
        return ratios
    except ValueError as e:
        raise e
    except:
        raise ValueError("比例格式错误")

def main():
    parser = argparse.ArgumentParser(description='3D重建游戏数据集生成器 (多问题版)')
    
    parser.add_argument('--total-states', type=int, default=100,
                      help='要生成的游戏状态总数（默认：100）')
    
    parser.add_argument('--level-ratios',
                      help='难度比例，格式：0.2:0.2:0.6，可以缺省最多一个值')
    
    parser.add_argument('--output', type=str, default='reconstruction_dataset',
                      help='输出目录路径（默认：reconstruction_dataset）')
    
    args = parser.parse_args()
    
    # 解析并验证参数
    try:
        level_ratios = parse_ratio_string(args.level_ratios)
    except ValueError as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
    
    # 创建生成器实例
    generator = MultiQuestionGenerator()
    
    try:
        # 生成数据集
        generator.generate_datasets(
            total_states=args.total_states,
            plot_level_ratios=level_ratios
        )
        
    except Exception as e:
        print(f"错误：生成数据集时出错 - {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
