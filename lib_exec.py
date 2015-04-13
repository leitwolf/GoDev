#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2015-04-03 22:33:05
# 

# 
# subprocess简化操作
# 

import os
import os.path
import sys
import re
import subprocess
import threading
import sublime
import functools

class Exec(object):

    # args={cmd,shell,work_dir,env,on_data,on_finish,sync}
    # cmd str or [] must set
    # shell bool default:False
    # work_dir str default:""
    # env {} default:{} 
    # on_data function default:None 有输出数据时调用
    # on_error function default:None 有错误信息时调用
    # on_finish function default:None 命令完成时调用
    # sync bool default:False 是否是同步
    def __init__(self, args):
        super(Exec, self).__init__()
        self.killed=False
        self.finished=False
        # 分解参数
        cmd=args["cmd"]
        shell=args.get("shell",False)
        work_dir=args.get("work_dir","")
        env=args.get("env",{})
        self._on_data=args.get("on_data",None)
        self._on_error=args.get("on_error",None)
        self._on_finish=args.get("on_finish",None)
        sync=args.get("sync",False)

        # 在Windows中隐藏控制窗口
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 处理环境变量
        proc_env = os.environ.copy()
        proc_env.update(env)
        for k, v in proc_env.items():
            proc_env[k] = os.path.expandvars(v).encode(sys.getfilesystemencoding())
        
        # 启动外部进程
        self.proc=subprocess.Popen(cmd,
            cwd=work_dir,
            shell=shell,
            env=proc_env,
            startupinfo=startupinfo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # 启动另外的线程来处理反馈信息
        t=threading.Thread(target=self.read_stdout)
        t.start()

        t2=threading.Thread(target=self.read_stderr)
        t2.start()

        # 是否同步
        if sync:
            self.proc.wait()


    # 读取输出数据
    def read_stdout(self):
        while self._check_finish() is None:
            data = self.proc.stdout.readline()
            data=str(data,sys.getfilesystemencoding())
            if data != "":
                if self._on_data:
                    self._on_data(data)
    

    # 读取错误数据
    def read_stderr(self):
        while self._check_finish() is None:
            data = self.proc.stderr.readline()
            data=str(data,sys.getfilesystemencoding())
            data=data.replace("\n","").replace("\r","")
            if data != "":
                print("[GoDev] error:"+data)
                if self._on_error:
                    self._on_error(data)
        

    # 检测程序是否完成
    def _check_finish(self):
        returncode=self.proc.poll()
        if returncode is None:
            return returncode
        # print(returncode)
        if self._on_finish and not self.finished:
            self.finished=True
            self._on_finish(self)
        self.proc.stdout.close()
        return returncode


    # 杀掉当前进程
    def kill(self):
        if not self.killed:
            self.killed = True
            if self.proc and self.poll():
                self.proc.terminate()            
            self._on_data = None
            self._on_finish = None


    # 程序是否运行完
    def poll(self):
        return self.proc.poll() == None


    # 进程返回码
    def exit_code(self):
        return self.proc.poll()
