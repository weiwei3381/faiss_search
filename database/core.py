# coding: utf-8
# @Time : 2025/6/8 14:35
# @Author : wowbat
# @File : core.py
# @Describe: 向量数据库的核心文件

import os, sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.')))  # 将运行时目录加入路径

import faiss, json, pickle
import numpy as np
from database import sql
from config import CONFIG
from utils import text as text_utils

dim = CONFIG.get('dim')  # 获取词向量维度
data_path = CONFIG.get('data_path')  # 获得数据存储路径
index_file = CONFIG.get('index_file')  # 索引文件名
cache_file = CONFIG.get('cache_file')  # 缓存文件名
default_section = CONFIG.get('default_section')  # 默认分区

# IndexIVFFlat倒排索引，IndexPQ量化
# METRIC_L2表示L2距离，生成空的index
empty_index = faiss.index_factory(dim, "Flat", faiss.METRIC_L2)
empty_index = faiss.IndexIDMap(empty_index)  # 对索引进行转化，转化为带id的索引

# 以下是3个全局变量
current_section = ""  # 当前切片名称
current_index = empty_index  # 当前使用的index
current_handled_cache = {}  # 初始化已处理过的内容缓存


def create_or_change_section(section_name: str):
    # 引用外部全局变量
    global current_section
    global current_index
    global current_handled_cache

    # 分区名录
    section_dir = os.path.join(data_path, section_name + "\\")
    if not os.path.exists(section_dir):
        os.mkdir(section_dir)
    current_section = section_name  # 修改全局变量，切换当前section
    # 获取对应section的索引和缓存文件
    index_file_path = os.path.join(section_dir, index_file)
    cache_file_path = os.path.join(section_dir, cache_file)
    # 如果已经存在数据，则读取已有数据, 否则转为空索引
    if os.path.exists(index_file_path):
        current_index = faiss.read_index(index_file_path)
    else:
        current_index = empty_index
    # 如果已经存在内容缓存，则读取内容缓存, 否则缓存清空
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "rb") as f:
            current_handled_cache = pickle.load(f)
    else:
        current_handled_cache = {}
    return section_dir


create_or_change_section(default_section)  # 切换到默认分区


def add_file_to_faiss(file_path: str, section: str = default_section):
    """
    将单个json文件加入faiss数据库
    @param file_path: json文件路径， json格式为[id: int, content: str]
    @param section: 分区名称
    @return:
    """
    if section is not None and section != current_section:
        create_or_change_section(section)
    embedding_list = []  # 需要处理的词向量内容
    cache_content_list = []  # 需要放入cache中的内容列表
    # 获取对应section的索引和缓存文件
    index_file_path = os.path.join(data_path, current_section + "\\", index_file)
    cache_file_path = os.path.join(data_path, current_section + "\\", cache_file)
    # 如果不存在文件，则抛出异常，否则读入文件信息到data_str中
    if not os.path.exists(file_path):
        raise Exception(f"File: {file_path} does not exists")
    if not os.path.isfile(file_path):
        raise Exception(f"The {file_path} is not file")
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            content_list = json.load(file) # 读入文件
        for ci in range(len(content_list)):
            item = content_list[ci]
            content = item.get('content')
            id = item.get('id')
            # 如果内容已经处理过，或者id不是整型，则跳过
            if current_handled_cache.get(content) or not isinstance(id, int):
                # todo 有优化空间，看能否通过id来去重
                continue
            embed_vec = text_utils.convert_embedding(content)  # 获得词向量
            cache_content_list.append(content)  # 加入缓存
            embedding_list.append({
                "id": id,
                "embedding": embed_vec
            })
            if ci % 100 == 99:
                print(f"Processed item: {ci + 1}/{len(content_list)}")
        vec_len = len(embedding_list)  # 向量的条数
        embedding_matrix = np.zeros([vec_len, dim])  # 根据list长度初始化词向量矩阵
        ids = np.arange(vec_len)  # 初始化id列表
        for i in range(vec_len):
            embedding_matrix[i, :] = embedding_list[i]["embedding"]  # 将词嵌入放到矩阵中去
            ids[i] = embedding_list[i]["id"]  # 把id放到ids列表中去
        current_index.add_with_ids(embedding_matrix, ids)  # 根据索引增加数据
        # 保存索引到文件
        faiss.write_index(current_index, index_file_path)
        print("Index file {} saved".format(index_file_path))
        # 保存缓存到文件
        for cache in cache_content_list:
            current_handled_cache[cache] = True
        with open(cache_file_path, "wb") as f:
            pickle.dump(current_handled_cache, f)
        print("Cache file {} saved".format(cache_file_path))
    except Exception as e:
        raise Exception(f"Put json in database in ERROR: {e}")
    finally:
        file.close()


def add_directory_to_faiss(directory: str, section: str = default_section):
    """
    将目录中所有的json文件存到数据库中，该方法只遍历
    @param directory: 存有json的目录地址
    @param section: 对应的分区名称
    @return:
    """

    # 如果目录不存在，则抛出错误
    if not os.path.exists(directory) or not os.path.isdir(directory):
        raise Exception(f"ERROR: {directory} is not useful directory!")
    section = section or default_section
    # 切换到对应的分区
    if section != current_section:
        create_or_change_section(section)
    json_file_list = []  # 需要处理的json文件列表
    # 遍历目录第一层，不进行深度检索，加入到文件列表中
    for file in os.listdir(directory):
        abs_json_file = os.path.join(directory, file)
        # 过滤不是文件的对象
        if not os.path.isfile(abs_json_file):
            continue
        # 过滤不是json的文件
        if text_utils.get_extname_from_file(abs_json_file) != ".json":
            continue
        json_file_list.append(abs_json_file)
    for i in range(len(json_file_list)):
        print("Open the {}/{} json file".format(i+1, len(json_file_list)))
        ith_json_file = json_file_list[i]
        add_file_to_faiss(ith_json_file, section)  # 将文件存入faiss数据库中的指定section中


def query_text(text: str, k: int = 10, section: str = default_section):
    """
    在向量数据库中查询文本text对应最相似的k个id
    @param text: 查询的文本
    @param k: 需要查询最相似的k个文本
    @param section: 从对应的section中进行查询,存在默认值
    @return: k个最相似文本对应的索引id
    """
    if section is not None and section != current_section:
        create_or_change_section(section)
    query_embedding = text_utils.convert_embedding(text)  # 转换text为词向量
    distances, indices = current_index.search(query_embedding, k=k)
    return indices[0]


def delete_section(section_name: str):
    # 引用外部全局变量
    global current_section
    global current_index
    global current_handled_cache

    if section_name is None:
        return
    if section_name == current_section:
        current_section = ""
        current_index = empty_index
        current_handled_cache = {}
    section_dir = os.path.join(data_path, section_name + "/")
    if os.path.exists(section_dir):
        abs_index_file = os.path.join(section_dir, index_file)
        abs_cache_file = os.path.join(section_dir, cache_file)
        if os.path.isfile(abs_index_file):
            os.remove(abs_index_file)
            print("Index file {} is deleted".format(abs_index_file))
        if os.path.isfile(abs_cache_file):
            os.remove(abs_cache_file)
            print("Cache file {} is deleted".format(abs_cache_file))

if __name__ == '__main__':
    # add_file_to_faiss(r"D:\py_projects\faiss_test\data\test_data.json")
    # add_directory_to_faiss(r"D:\py_projects\faiss_test\data\dir_test")
    test_section_name = "title"
    # add_file_to_faiss(r"D:\py_projects\faiss_test\data\3.json", slice_name)
    indices = query_text("进一步具化信息先行理念", 5, test_section_name)
    for current_index in indices:
        print(current_index)
