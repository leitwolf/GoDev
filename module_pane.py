#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: lonewolf
# Date: 2015-04-08 18:45:53
#

import re
import os.path
import sublime
import sublime_plugin
from . import common
from . import lib_pane


# 初始化
def init():
    # panes
    layout = {
        "cols": [0, 1],
        "rows": [0, 0.75, 1],
        "cells": [[0, 0, 1, 1], [0, 1, 1, 2]]
    }
    pane_list = [
        {"group": 1, "name": "Console"}
    ]
    lib_pane.set_panes_args(layout, pane_list)


# 显示信息到控制面板
def console_output(text, newline=True, erase=False):
    pane_name = "Console"
    lib_pane.show_pane(pane_name)
    lib_pane.output_to_pane(pane_name, text, newline, erase)


# 关闭面板
class GodevClosepanesCommand(sublime_plugin.WindowCommand):

    def run(self):
        lib_pane.close_all_panes()


# 双击错误行跳转到定义处
class GodevPaneDoubleclickCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # 是否是在Console中双击
        console_id = lib_pane.pane_id_list.get("Console")
        if self.view.id() != console_id:
            # print("[GoDev] console_id no match.")
            return

        # 找出所在行
        line = ""
        for region in self.view.sel():
            if not region.empty():
                line = self.view.substr(self.view.line(region.a))
                break
        if line != "":
            # 找出行内文件信息
            m = re.match("^\[ERROR\]: ((\w|/|\.)+):(\d+):", line)
            if not m:
                print("no match")
                return
            (name, path) = common.get_project_info()
            path = os.path.join(path, m.group(1))
            line_num = m.group(3)
            if not os.path.exists(path):
                sublime.status_message("File not exists at %s" % (path))
                return
            # 在0中打开
            self.view.window().focus_group(0)
            self.view.window().open_file(
                path + ":" + line_num, sublime.ENCODED_POSITION)


# 当最后一个面板关闭时，要把相应的group也关闭
class PaneListener(sublime_plugin.EventListener):

    def on_close(self, view):
        console_id = lib_pane.pane_id_list.get("Console")
        if view.id() != console_id:
            return
        lib_pane.close_all_panes()
