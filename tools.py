import json
import os.path


def split_json(file, store_dir, max_num=10000):
    start_id = 12345  # 初始id
    item_list = []
    with open(file, "r+", encoding="utf-8") as f:
        content_str = f.read()
        item_list = json.loads(content_str)
    accumulation = 0  # 单个json文件大小的累加值
    one_json_list = []  # 存入的单个json文件
    for i in range(len(item_list)):
        item = item_list[i]
        one_json_list.append({
            "id": str(start_id + i),
            "content": item['t']
        })
        accumulation += 1
        if accumulation >= max_num:
            filepath = os.path.join(store_dir, f"data_{i}.json")
            with open(filepath, "w+", encoding="utf-8") as f:
                # 存储内容后将累加值和单个json文件的list都清零
                json.dump(one_json_list, f, ensure_ascii=False)
                accumulation = 0
                one_json_list = []


def add_ids():
    start_id = 10086  # 初始id
    title_with_id = []  # 增加id
    with open("./data/title.json", "r+", encoding="utf-8") as f:
        content_str = f.read()
        title_list = json.loads(content_str)
        for i in range(len(title_list)):
            title_with_id.append({
                "id": str(start_id + i),
                "content": title_list[i]
            })
    with open("./data/test_data.json", "w+", encoding="utf-8") as f:
        f.write(json.dumps(title_with_id, ensure_ascii=False))


if __name__ == '__main__':
    # add_ids()
    split_json(r"D:\py_projects\faiss_test\data\indexes.json", r"D:\py_projects\faiss_test\data")
