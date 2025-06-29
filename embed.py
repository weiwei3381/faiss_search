import faiss, os, json
import ollama
import numpy as np
from random import randint
from config import CONFIG

dim = CONFIG.get('dim')  # 获取词向量维度
index_file_path = CONFIG.get('index_path')  # 获取索引文件位置
# IndexIVFFlat倒排索引，IndexPQ量化
# METRIC_L2表示L2距离
current_index = faiss.index_factory(dim, "Flat", faiss.METRIC_L2)
current_index = faiss.IndexIDMap(current_index)  # 对索引进行转化，转化为带id的索引
# 如果已经存在数据，则读取已有数据
if os.path.exists(index_file_path):
    current_index = faiss.read_index(index_file_path)



def add_data_file(file_path:str):
    """将单个文件加入数据

    :param str file_path: json文件路径，json格式为[id: int, embedding: float[]]
    """
    embedding_matrix = None  # 词向量矩阵
    data_str = ""  # 初始化读入的字符串
    # 如果不存在文件，则抛出异常，否则读入文件信息到data_str中
    if not os.path.exists(file_path):
        raise Exception("File do not exists")
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            data_str = file.read()  # 读入文件
        embedding_list = json.loads(data_str)  # 加载list文件
        embedding_matrix = np.zeros([len(embedding_list), dim])  # 根据list长度初始化零矩阵
        ids = np.arange(len(embedding_list)) # 初始化id列表 
        for i in range(len(embedding_list)):
            embedding = embedding_list[i]["embedding"]  # 拿到对应的词嵌入
            # 将词嵌入放到矩阵中去
            embedding_array = np.array(embedding)
            embedding_matrix[i,:] = embedding_array
            # 把id放到ids列表中去
            ids[i] = int(embedding_list[i]["id"])
        current_index.add_with_ids(embedding_matrix, ids) # 根据索引增加数据
        # 保存索引到文件
        faiss.write_index(current_index, index_file_path)
    except Exception as e:
        raise Exception("将文件转换加入到索引中出错")
    finally:
        file.close()


def query_text(text: str, k: int):
    """在向量数据库中查询文本text对应最相似的k个id

    :param str text: 查询的文本
    :param int k: 需要查询最相似的k个文本
    :return list: k个最相似文本对应的索引id
    """
    query_embedding = convert_embedding(text)  #转换text为词向量
    distances, indices = current_index.search(query_embedding, k=k)
    return indices


def query_embedding(embedding_str: str, k:int):
    """在向量数据库中查询词嵌入字符串最相似的k个id

    :param str embedding_str: 词嵌入字符串，需要json转换
    :param int k: 需要查询最相似的k个文本
    :return _type_: k个最相似文本对应的索引id
    """
    embedding = json.dumps(embedding_str)  # 词嵌入的列表
    embedding_array = np.array(embedding)
    distances, indices = current_index.search(query_embedding, k=k)
    return indices

    


def generateData():
    """生成索引数据

    :return _type_: _description_
    """
    
    # index.train(embedding_matrix) # 对索引进行预训练，索引结构的构建依赖于数据的统计特征（如聚类中心）
    current_index.add() # 添加数据

    # 设置搜索参数
    # nprobe指定了搜索时需要访问的聚类中心（Voronoi Cells）数量。
    # 在IVF索引中，数据集通过聚类被划分为多个子空间（每个子空间对应一个聚类中心），
    # 搜索时首先定位离查询向量最近的nprobe个子空间，然后在这些子空间内进行局部精确搜索。
    
    # 保存索引到文件
    faiss.write_index(current_index, "./my_index.index")
    return current_index
    
        
if __name__ == '__main__':
    # if os.path.exists("./my_index.index"):
    #     index = faiss.read_index("./my_index.index")
    # else:
    #     generateData()
    # index.nprobe = 8 # 16个聚类中心

    convert_embedding("我家大门常打开")
    
    print("=="*10)
    query_embedding = None
    query_title = input("请输入查询标题：")
    # with open('./embedding/query.json', mode='r', encoding='utf-8') as file:
    #     query_list = json.load(file)
    #     query = query_list[randint(0,len(query_list)-1)]
    #     query_embedding = np.array(query["embedding"],dtype=np.float32).reshape(1, 768)
    #     query_title = query["title"]
            
    response = ollama.embed(model='shaw/dmeta-embedding-zh', input=[query_title])
    query_embedding = np.array(response["embeddings"][0],dtype=np.float32).reshape(1,768)    # 执行查询
    # print(query_embedding)
    print("query:", query_title)
    distances, indices = current_index.search(query_embedding, k=10) # 返回Top10
    for i in indices[0]:
        print("**"*10)
        print(i)

    