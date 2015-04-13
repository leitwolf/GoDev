#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author: lonewolf
# Date: 2015-04-08 18:40:59
# 

import os.path
import functools
import datetime
import sublime
import sublime_plugin
from . import lib_helper

# 新建文件模板
FILE_TEMPLATE="""//
// Author: ${author}
// Date: ${date}
//
package ${package}
"""

# 新建文件
class GodevNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        self.window.run_command("hide_panel")
        title = "untitle"
        on_done = functools.partial(self.on_done, dirs[0])
        v = self.window.show_input_panel(
            "File Name:", title + ".go", on_done, None, None)
        v.sel().clear()
        v.sel().add(sublime.Region(0, len(title)))

    def on_done(self, path, name):
        filepath = os.path.join(path, name)
        if os.path.exists(filepath):
            sublime.error_message("Unable to create file, file exists.")
        else:
            code = FILE_TEMPLATE
            # add attribute
            settings = lib_helper.load_settings("GoDev")
            format = settings.get("date_format", "%Y-%m-%d %H:%M:%S")
            date = datetime.datetime.now().strftime(format)
            code = code.replace("${date}", date)
            author=settings.get("author", "Your Name")
            code = code.replace("${author}", author)
            # package
            package=os.path.split(path)[-1]
            code = code.replace("${package}", package)
            # save
            lib_helper.write_file(filepath, code)
            v=sublime.active_window().open_file(filepath)
            # cursor
            v.run_command("insert_snippet",{"contents":code})
            sublime.status_message("Go file create success!")

    def is_enabled(self, dirs):
        return len(dirs) == 1
