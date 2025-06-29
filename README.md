# 向量数据库进行文本检索

## 总体思路

读取json文件后，使用ollama的embedding模型将文本转换为向量，然后用网络服务的形式提供访问，目前，embedding模型使用：`shaw/dmeta-embedding-zh`；网络服务框架使用：`Flask`。

规范的json格式如下：

```json
[
    {
        "id": "内容对应的数据库id",
        "content": "待索引内容"
    }
]
```


主要api如下：

## 主要api接口

### 在指定分区中增加json文件内容

接口url: http://127.0.0.1:5000/api/v1/add
method: post方法
body: 
```shell
{
    // json文件位置
    "file": "D:\\py_projects\\faiss_test\\data\\dir_test\\2.json",
    // 分区名称，默认为main
    "section": "main"
}
```

### 在指定分区中增加文件夹，增加文件夹中的所有json文件

接口url: http://127.0.0.1:5000/api/v1/batch

method: post方法

body:
```shell
{
    // json文件所在目录
    "dir": "D:/py_projects/faiss_test/data/dir_test/",
    // 分区名称，默认为main
    "section": "main"
}
```

### 在指定分区查询最相似的k个结果

接口url: 127.0.0.1:5000/api/v1/query

method: post方法

body:

```shell
{
    // 查询内容
    "text": "携手构建科技创新共同体",
    // 分区名称，默认为main
    "section": "main",
    // 返回最相似的结果数量，默认为20
    "k": 20
}
```

### 清空分区内容

接口url: 127.0.0.1:5000/api/v1/delete

method: post方法

body:

```shell
{
    // 清空分区的名称
    "section": "main"
}
```



