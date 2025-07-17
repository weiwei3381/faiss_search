# flask框架
import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath('.'))) # 将运行时目录加入路径

from flask import Flask, request, jsonify
from database import core
from flask_cors import CORS

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/api/v1/batch", methods=['POST'])
def add_directory():
    """
    将文件夹中所有json文件加入向量数据库，传入的参数为{"dir": "json文件目录"}
    @return:
    """
    # 确保使用POST方法处理
    if request.method != 'POST':
        return jsonify({
            "data": "error",
            "error": "Method not allowed"
        }), 405
    # 将接收数据强制转换为JSON格式, 如果转换不成功则返回400错误
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({
            "data": "error",
            "error": "No data provided"
        }), 400
    if "dir" not in data:
        return jsonify({
            "data": "error",
            "error": "Need 'dir' in request parameter"
        }), 400
    directory = data['dir']
    section = data.get("section", None)
    try:
        core.add_directory_to_faiss(directory, section)  # 将目录加入faiss中
    except Exception as e:
        return jsonify({
            "data": "error",
            "error": str(e)
        }), 200
    return jsonify({
        "info": "All json files in {} is processed success".format(directory),
        "error": ""
    }), 200


@app.route("/api/v1/add", methods=['POST'])
def add_file():
    # 确保使用POST方法处理
    if request.method != 'POST':
        return jsonify({
            "data": "error",
            "error": "Method not allowed"
        }), 405
    # 将接收数据强制转换为JSON格式, 如果转换不成功则返回400错误
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({
            "data": "error",
            "error": "No data provided"
        }), 400

    # 判断有没有传入分区名称
    section_name = data.get("section", None)
    # 如果传入的是单个文件，则对单个文件进行处理
    if "file" in data:
        # 获得文件
        file = data["file"]
        try:
            core.add_file_to_faiss(file, section_name)
        except Exception as e:
            return jsonify({
                "data": "error",
                "error": str(e)
            }), 200
        return jsonify({
            "data": "File {} is processed success".format(file),
            "error": ""
        }), 200


@app.route("/api/v1/query", methods=['POST'])
def query():
    """
    在向量数据库检索的api，传入的参数为{"text": "检索文本", section: "分区名称"}
    @return: {ids: [id1, id2]}，id1, id2等为正说明找到值，如果为-1则表示没有
    """
    # 确保使用POST方法处理
    if request.method != 'POST':
        return jsonify({
            "data": "error",
            "error": "Method not allowed"
        }), 405
    # 将接收数据强制转换为JSON格式, 如果转换不成功则返回400错误
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({
            "data": "error",
            "error": "No data provided"
        }), 400

    section_name = data.get("section", None)
    # 如果传入的是单个文件，则对单个文件进行处理
    if "text" in data:
        # 获得文件
        text = data["text"]
        try:
            k = 20 if "k" not in data else data['k']
            ids = core.query_text(text, k, section_name)
        except Exception as e:
            return jsonify({
                "data": "error",
                "error": str(e)
            }), 200
        print(text, "查询结果为:", ids.tolist())
        return jsonify({
            "data":{
                "ids": ids.tolist()
            },
            "error": ""

        }), 200

@app.route("/api/v1/delete", methods=['POST'])
def delete_section():
    """
    删除
    @return:
    """
    if request.method != 'POST':
        return jsonify({
            "data": "error",
            "error": "Method not allowed"
        }), 405
    # 将接收数据强制转换为JSON格式, 如果转换不成功则返回400错误
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({
            "data": "error",
            "error": "No data provided"
        }), 400

    section_name = data.get("section", None)
    core.delete_section(section_name)
    return jsonify({
        "data":"Section {} is deleted".format(section_name),
        "error": ""
    }), 200

app.run(debug=False)
# CORS(app, supports_credentials=True)  # 支持所有的跨域请求
CORS(app, origins=['http://localhost:1212', 'http://127.0.0.1:1212'])  # 支持指定的跨域请求
