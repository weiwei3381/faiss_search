# coding: utf-8
# @Time : 2025/6/8 10:36
# @Author : wowbat
# @File : text.py
# @Describe: 与文本处理相关的工具类

import os, sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.'))) # 将运行时目录加入路径

import faiss, json
import ollama
import numpy as np
from random import randint

from config import CONFIG


def convert_embedding(text: str):
    """
    将文本转换为词向量
    @param text: 需要转换的文本
    @return: 词向量
    """
    dim = CONFIG.get('dim')  # 获取词向量维度
    embed_model = CONFIG.get('embedding_model')  # 获取embedding模型名称
    embed_vector = []  # 默认为空
    try:
        response = ollama.embed(model=embed_model, input=[text])  # 拿到模型响应
        embed_vector = np.array(response["embeddings"][0], dtype=np.float32).reshape(1, dim) # 转换为词向量
    except Exception as e:
        print("出现错误：", e)

    return embed_vector


def get_extname_from_file(file: str):
    """
    获取文件扩展名，例如“.json”
    @param file: 文件完整路径
    @return: 全小写的文件扩展名，例如“.pdf”
    """
    # 例如对于文件：r"D:\迅雷下载\python-docx.pdf"
    # 获取文件名全称
    basename = os.path.basename(file.lower())  # 输出为：python-docx.pdf
    # 获取文件扩展名
    extname = os.path.splitext(basename)[1]  # 输出为：.pdf
    return extname



if __name__ == "__main__":
    embedding = convert_embedding("进一步强化信息主导的作用")
    print(embedding)
