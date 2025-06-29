# coding: utf-8
# @Time : 2025/6/9 20:31
# @Author : wowbat
# @File : sql.py
# @Describe: 模拟数据库

import os, sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.'))) # 将运行时目录加入路径

import pickle, json
from utils import text as text_utils

database = {}  # 用map模拟数据库
database_file_path = r"D:\py_projects\faiss_test\data\mySql.db"
if os.path.exists(database_file_path):
    with open(database_file_path, "rb") as f:
        database = pickle.load(f)

def add_json_to_mysql(file_path: str):
    with open(file_path, mode="r", encoding="utf-8") as file:
        content_str = file.read()  # 读入文件
        content_list = json.loads(content_str)
        for item in content_list:
            id = item['id']
            if id in database:
                continue
            content = item['content']
            database[id] = content
    with open(database_file_path, "wb") as f:
        pickle.dump(database, f)

def query_in_mysql(id:str):
    id = str(id)
    if id in database:
        return database[id]
    else:
        return ""

if __name__ == "__main__":
    dir = r"D:\py_projects\faiss_test\data\dir_test"
    for file in os.listdir(dir):
        abs_file = os.path.join(dir, file)
        # 过滤不是文件的对象
        if not os.path.isfile(abs_file):
            continue
        # 过滤不是json的文件
        if text_utils.get_extname_from_file(abs_file) != ".json":
            continue
        print(f"正在将{abs_file}加入数据库")
        add_json_to_mysql(abs_file)
