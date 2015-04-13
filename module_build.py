#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2015-04-08 21:06:25
# 

# 
# 构建，运行相关操作模块
# 

import os.path
import threading
import sublime
import sublime_plugin
from . import common
from . import lib_helper
from . import lib_exec
from . import module_pane


# 正在运行的实例{name,exec}
_running_list=[]


# 停止运行进程
def _stop_program(index):
    if index>=len(_running_list):
        return
    item=_running_list[index]
    item["exec"].kill()
    module_pane.console_output("["+item["name"]+"] STOPED!")
    del _running_list[index]


# 构建并运行
class GodevRunCommand(sublime_plugin.WindowCommand):

    def init(self):
        self.build_error=False

    def run(self):
        t=threading.Thread(target=self.doit)
        t.start()

    def doit(self):
        self.build_error=False
        (name,path)=common.get_project_info(False)

        # 检测当前程序是否在运行
        for i in range(0, len(_running_list)):
            item=_running_list[i]
            if item["name"]==name:
                _stop_program(i)
                break
        module_pane.console_output("Start building ["+name+"] ...")
        gopath = lib_helper.load_settings("GoDev").get("GOPATH", "")
        env={"GOPATH":gopath}
        args={"cmd":"go build "+name,
            "shell":True,
            "work_dir":path,
            "on_data":self.on_build_data,
            "on_error":self.on_build_error,
            "env":env,
            "sync":True
        }
        lib_exec.Exec(args)

        # 构建失败
        if self.build_error:
            module_pane.console_output("Build ["+name+"] FAIL!")
            self.build_error=False
            return
        
        # 构建成功
        module_pane.console_output("Build ["+name+"] SUCCESS!")

        # 开始运行
        module_pane.console_output("Start running ["+name+"]")
        args={"cmd":"./"+name,
            "shell":True,
            "work_dir":path,
            "env":env,
            "on_data":self.on_run_data,
            "on_finish":self.on_run_finish,
            "sync":False
        }
        exec1=lib_exec.Exec(args)
        instance={"name":name,"exec":exec1}
        _running_list.append(instance)


    def on_build_data(self, data):
        module_pane.console_output(data)

    # 构建错误
    def on_build_error(self, data):
        if not data.startswith("#"):
            self.build_error=True
            data="[ERROR]: "+data
        module_pane.console_output(data)

    def on_run_data(self, data):
        module_pane.console_output(data)

    def on_run_finish(self, exec1):
        print("finish")
        for i in range(0,len(_running_list)):
            item=_running_list[i]
            if item["exec"]==exec1:
                _stop_program(i)
                return

    def is_enabled(self):
        (name,path)=common.get_project_info(False)
        return len(name)>0


# 停止运行
class GodevStopCommand(sublime_plugin.WindowCommand):
    def run(self):
        t=threading.Thread(target=self.doit)
        t.start()

    def doit(self):
        if len(_running_list)==0:
            sublime.status_message("No running program.")
        elif len(_running_list)==1:
            _stop_program(0)
        else:
            show_list=[]
            for i in range(0,len(_running_list)):
                show_list.append(_running_list[i]["name"])
            on_done = functools.partial(_stop_program)
            sublime.active_window().show_quick_panel(show_list,on_done)

    def is_enabled(self):
        (name,path)=common.get_project_info(False)
        return len(name)>0


# 构建各个平台上的可执行文件
class GodevBuildCommand(sublime_plugin.WindowCommand):
    def run(self, goos, goarch):
        t=threading.Thread(target=self.doit,args=(common.goroot,goos,goarch))
        t.start()
    
    def doit(self, goroot, goos, goarch):
        (name,path)=common.get_project_info(False)
        platform=goos+"_"+goarch
        toolpath=goroot+"/pkg/tool/"+platform
        if not os.path.exists(toolpath):
            # 生成构建工具
            module_pane.console_output("Start building toolchain for ["+platform+"] ...")
            cmd="CGO_ENABLED=0 GOOS="+goos+" GOARCH="+goarch
            if sublime.platform=="windows":
                cmd+=" ./make.bat"
            else:
                cmd+=" ./make.bash"
            srcpath=goroot+"/src"
            args={"cmd":cmd,
                "shell":True,
                "work_dir":srcpath,
                "sync":True
            }
            lib_exec.Exec(args)

        # 开始构建
        module_pane.console_output("Start building ["+name+"] ...")
        cmd="CGO_ENABLED=0 GOOS="+goos+" GOARCH="+goarch+ " go build "+name
        gopath=lib_helper.load_settings("GoDev").get("GOPATH", "")
        env={"GOPATH":gopath}
        args={"cmd":cmd,
            "shell":True,
            "work_dir":path,
            "env":env,
            "sync":True
        }
        lib_exec.Exec(args)
        module_pane.console_output("Build ["+name+"] complete!")

    def is_enabled(self, goos, goarch):
        (name,path)=common.get_project_info(False)
        return len(name)>0
