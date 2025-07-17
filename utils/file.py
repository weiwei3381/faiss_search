# coding: utf-8
# @Time : 2025/6/29 20:37
# @Author : wowbat
# @File : file.py
# @Describe: 与文件相关的工具类
import os, sys
if __name__ == "__main__":
    # 将运行时目录加入路径
    sys.path.append(os.path.dirname(os.path.abspath('.')))

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
    extname = get_extname_from_file(r"D:\迅雷下载\python-docx.pdf")
    print(extname)



