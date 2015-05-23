#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: lonewolf
# Date: 2015-04-03 18:07:05
#

#
# 控制面板模块
#

import sublime
import sublime_plugin

# 保存 pane与id，供外部查询{name=>id}
pane_id_list = {}

# pane所绑定到的窗口
_pane_binded_window = None

# 布局
_layout = {
    "cols": [0, 1],
    "rows": [0, 1],
    "cells": [[0, 0, 1, 1]]
}

# 面板列表
_pane_list = []


# 设置各个参数
def set_panes_args(layout, pane_list):
    global _layout, _pane_list
    _layout = layout
    _pane_list = pane_list


# 显示面板，没有就新建
def show_pane(pane_name):
    global _pane_binded_window
    if _pane_binded_window:
        window = _pane_binded_window
    else:
        window = sublime.active_window()
        _pane_binded_window = window
    if window.num_groups() == 1:
        window.run_command("set_layout", _layout)
    # 查找所在的group
    group = get_pane_group(pane_name)
    if group == 0:
        return
    prev_view = window.active_view_in_group(0)
    views = window.views_in_group(group)
    for view in views:
        if view.name() == pane_name:
            # 只显示，不焦点集中
            window.focus_view(view)
            window.focus_view(prev_view)
            return
    # 没有则新建
    view = window.new_file()
    view.set_name(pane_name)
    view.set_read_only(True)
    view.set_scratch(True)
    # view.run_command("toggle_setting", {"setting": "line_numbers"})
    # 放在后面
    window.set_view_index(view, group, len(views))
    window.focus_view(prev_view)
    # 保存其id
    pane_id_list[pane_name] = view.id()


# 关闭所有面板
def close_all_panes():
    if _pane_binded_window:
        window = _pane_binded_window
    else:
        window = sublime.active_window()
    # 所含有的组列表，并去重
    group_list = []
    for item in _pane_list:
        group_list.append(item["group"])
    group_list = list(set(group_list))
    # 先关闭文件
    for group in group_list:
        for view in window.views_in_group(group):
            window.focus_view(view)
            window.run_command("close_file")
    # 清空id列表
    pane_id_list.clear()
    # 恢复到一个窗口
    window.run_command(
        "set_layout", {"cells": [[0, 0, 1, 1]], "cols": [0.0, 1.0], "rows": [0.0, 1.0]})


# 发送信息到面板
def output_to_pane(pane_name, text, newline=True, erase=False):
    if _pane_binded_window is None:
        return
    window = _pane_binded_window
    group = get_pane_group(pane_name)
    if group == 0:
        return
    views = window.views_in_group(group)
    for view in views:
        if view.name() == pane_name:
            append_to_view(view, text, newline, erase)
            break


# 向一个view中添加内容
def append_to_view(view, text, newline, erase):
    if erase:
        view.run_command("select_all")
        view.run_command("right_delete")
    if view.size() > 0 and newline:
        view.run_command('append', {'characters': "\n", 'force': True})
    view.run_command(
        'append', {'characters': text, 'force': True, 'scroll_to_end': True})
    # 上面的不起作用，滚动到底部
    view.run_command("move_to", {"to": "eof"})


# 根据名称查找所在的group
def get_pane_group(pane_name):
    group = 0
    for item in _pane_list:
        if item["name"] == pane_name:
            group = item["group"]
    if group == 0:
        sublime.status_message("no group for pane -> " + pane_name)
    return group
