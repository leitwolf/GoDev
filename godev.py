#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2015-02-25 11:23:48
# 

import os.path
import sublime
import sublime_plugin
from . import lib_helper
from . import common
from . import module_pane


# 初始化插件
def init():
    common.init()
    module_pane.init()


# 设置
class GodevSettingsCommand(sublime_plugin.WindowCommand):
    def run(self):
        # 先判断用户设置是否存在
        userpath=sublime.packages_path()+"/User/GoDev.sublime-settings"
        default_path=sublime.packages_path()+"/GoDev/GoDev.sublime-settings"
        if not os.path.exists(userpath):
            data=lib_helper.read_file(default_path)
            lib_helper.write_file(userpath,data)
        self.window.open_file(userpath)


def plugin_loaded():
    sublime.set_timeout(init, 200)

