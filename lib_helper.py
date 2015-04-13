import sublime
import os
import hashlib
import sys


# 读取文件
def read_file(path):
    f = open(path, "r")
    content = f.read()
    f.close()
    return content


# 写入文件
def write_file(path, content):
    f = open(path, "w+")
    f.write(content)
    f.close()


# 检测文件后缀
def check_file_ext(filename,ext):
    if filename==None:
        return False
    arr=os.path.splitext(filename)
    if len(arr)<2:
        return False
    ext1 = arr[1][1:]
    if ext1 == ext:
        return True
    else:
        return False


def md5(str):
    return hashlib.md5(str.encode(sys.getfilesystemencoding())).hexdigest()


# 是否sublime 3
def is_ST3():
    return sublime.version()[0] == '3'


# 加载插件配置
def load_settings(name):
    return sublime.load_settings(name+".sublime-settings")
