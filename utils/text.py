# coding: utf-8
# @Time : 2025/6/8 10:36
# @Author : wowbat
# @File : text.py
# @Describe: 与文本处理相关的工具类

import os, sys

from utils.embed import convert_embedding

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.'))) # 将运行时目录加入路径

if __name__ == "__main__":
    embedding = convert_embedding("进一步强化信息主导的作用")
    print(embedding)
