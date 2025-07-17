# coding: utf-8
# @Time : 2025/6/29 20:37
# @Author : wowbat
# @File : embed.py
# @Describe: 与词向量相关的方法
import os, sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.')))

import numpy as np
import ollama
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

def chat_with_LLM(text: str):
    pass


if __name__ == "__main__":
    # 将运行时目录加入路径
    sys.path.append(os.path.dirname(os.path.abspath('.')))
    vec = convert_embedding("这是最完美的一天")
    print(vec)