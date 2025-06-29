import json

# title_list = []  # 标题列表

# with open("./data/军报理论文章_2024-03-24.json",mode="r", encoding="utf-8") as file:
#     data_str = file.read()
#     json_data = json.loads(data_str)
#     for article in json_data:
#         title = article["title"]
#         if(len(title) > 4):
#             title_list.append(title)

content_list = []  # 内容列表
            
with open("./data/军报理论文章_2024-03-24.json",mode="r", encoding="utf-8") as file:
    data_str = file.read()
    json_data = json.loads(data_str)
    for article in json_data:
        content = article["content"]
        if len(content) > 32 and len(content) < 512:
            content_list.append(content)
        if len(content) > 512:
            cut_content = content[:512]
            stop_index = cut_content.rfind("。")  # 句号索引
            content_list.append(cut_content[:stop_index])

# 保存标题列表
# with open("./data/title.json", mode="w", encoding="utf-8") as file:
#     json.dump(title_list, file, ensure_ascii=False)

# 保存内容列表
with open("./data/content.json", mode="w", encoding="utf-8") as file:
    json.dump(content_list, file, ensure_ascii=False)

print('列表保存成功！')