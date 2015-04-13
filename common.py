#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2015-04-02 12:43:59
# 

import re
import subprocess
import sublime
from . import lib_helper


# 系统环境
goroot=""

# 初始化
def init():
    global goroot
    goroot=get_goroot()


# 获取goroot变量
def get_goroot():
    goroot=""
    args=["go","env"]
    process=subprocess.Popen(args,bufsize=0,stdout=subprocess.PIPE)
    output=process.stdout.read()
    output=str(output,"utf-8")
    if output=="":
        sublime.status_message("Go not install!")
    else:
        # 分析输出，得出go的环境
        arr=output.split("\n")
        for i in range(0, len(arr)):
            item=arr[i]
            # 去掉空白字符
            item=re.sub("\s","",item)
            # print(item)
            items=arr[i].split("=")
            if len(items)==2:
                k=items[0]
                v=re.sub("\"","",items[1])
                if k=="GOROOT":
                    goroot=v
                    break
    return goroot


# 获取GOPATH，返回数组 
def get_gopath_list(show_err):
    settings = lib_helper.load_settings("GoDev")
    gopath = settings.get("GOPATH", "")
    if len(gopath)==0:
        if show_err:
            sublime.error_message("GOPATH is no set!!")        
        return []
    if sublime.platform()=="windows":
        return gopath.split(";")
    else:
        return gopath.split(":")


# 获取项目信息 (name,path)
# check_go 是否检测是go文件
def get_project_info(check_go=True):
    filepath=sublime.active_window().active_view_in_group(0).file_name()
    name=""
    path=""
    if filepath and not check_go or lib_helper.check_file_ext(filepath,"go"):
        arr=get_gopath_list(False)
        # 检测是否在GOPATH中
        if arr:
            for i in range(0,len(arr)):
                p=arr[i]+"/src/"
                if filepath.startswith(p):
                    a=filepath[len(p):]
                    name=a.split("/")[0]
                    path=p+name
                    break
    return (name,path)

