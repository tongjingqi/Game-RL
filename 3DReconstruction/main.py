#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from QAGenerator import ThreeDReconstructionQAGenerator

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
    parser = argparse.ArgumentParser(description='3D重建游戏数据集生成器')
    
    parser.add_argument('--total', type=int, default=100,
                      help='要生成的问题总数（默认：100）')
    
    parser.add_argument('--qa-types', nargs='+',
                      choices=['count', 'position', 'projection', 'action_outcome', 
                              'strategy_optimization', 'transition_path'],
                      help='要生成的具体问题类型（可多选）')
    
    parser.add_argument('--type-ratios',
                      help='各问题类型的比例，格式：0.2:0.2:0.2:0.2:0.1:0.1（对应六种问题类型）')
    
    parser.add_argument('--level-ratios',
                      help='难度比例，格式：0.2:0.2:0.6，可以缺省最多一个值')
    
    parser.add_argument('--output', type=str, default='reconstruction_dataset',
                      help='输出目录路径（默认：reconstruction_dataset）')
    
    args = parser.parse_args()
    
    # 验证问题类型
    valid_types = ['count', 'position', 'projection', 'action_outcome', 
                  'transition_path', 'strategy_optimization']
    
    # 解析并验证参数
    try:
        # 解析比例设置
        type_ratios = None
        if args.type_ratios:
            values = args.type_ratios.split(':')
            if len(values) != len(valid_types):
                raise ValueError(f"问题类型比例格式错误，应为6个数字，用:分隔")
            type_ratios = {}
            for i, v in enumerate(values):
                if v:  # 如果值不为空
                    type_ratios[valid_types[i]] = float(v)
            # 验证比例之和是否接近1
            total = sum(type_ratios.values())
            if not (0.99 <= total <= 1.01):  # 允许1%的误差
                raise ValueError(f"问题类型比例之和应为1，当前为{total}")
                
        level_ratios = parse_ratio_string(args.level_ratios)
            
    except ValueError as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
    
    # 创建生成器实例
    generator = ThreeDReconstructionQAGenerator()
    
    # 根据指定的具体问题类型调整比例
    if args.qa_types:
        if type_ratios is None:
            type_ratios = {}
        # 将未指定的类型比例设为0
        for qt in valid_types:
            if qt not in args.qa_types:
                type_ratios[qt] = 0
        # 平均分配剩余比例
        remaining_ratio = 1.0 - sum(type_ratios.values())
        if remaining_ratio > 0:
            for qt in args.qa_types:
                if qt not in type_ratios:
                    type_ratios[qt] = remaining_ratio / len(args.qa_types)
    
    try:
        # 生成数据集
        generator.generate_all_datasets(
            total_samples=args.total,
            type_ratios=type_ratios,
            plot_level_ratios=level_ratios
        )
        
    except Exception as e:
        print(f"错误：生成数据集时出错 - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
