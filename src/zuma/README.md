# 祖玛游戏数据集

## 游戏介绍

直接看<https://www.bilibili.com/video/BV1B64y147pg/>

## 数据集构造方式

需要matplotlib, numpy
把gene_gamedata.py, gene_qa.py, gene_dataset.py放进zuma_dataset文件夹（或者你自己创建的文件夹中，它会在它的工作文件夹中生成数据集）
在gene_dataset.py中，修改dataset_size(默认200，即200张图，每张图有多个问题)，运行即可
