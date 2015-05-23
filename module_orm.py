#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: lonewolf
# Date: 2015-04-09 20:21:57
#

#
# 生成mysql表model
#

import os.path
import threading
import configparser
import sublime
import sublime_plugin
from . import common
from . import module_pane
from . import pymysql
from . import lib_helper


# 类型对照表{mysql->go}
_TYPE = {
    "tinyint": "int8",
    "smallint": "int16",
    "int": "int",
    "mediumint": "int32",
    "bigint": "int64",
    "decimal": "float64",
    "float": "float32",
    "double": "float64",
    "date": "time.Time",
    "datetime": "time.Time",
    "timestamp": "time.Time",
    "time": "time.Time",
    "char": "string",
    "varchar": "string",
    "tinytext": "string",
    "text": "string",
    "mediumtext": "string",
    "longtext": "string",
}

# 模板
_TEMPLATE = """package models

import (
    "github.com/astaxie/beego/orm"
)

type {{table_name}} struct {
{{structs}}
}

func (t *{{table_name}}) TableName() string {
    return "{{table_name_str}}"
}

func init() {
    orm.RegisterModel(new({{table_name}}))
}
"""


# 工具类,首字母大写
def first_upper(text):
    return text[0].upper() + text[1:]


# 读取配置文件
def read_config():
    (name, path) = common.get_project_info(False)
    config_file = path + "/orm.config"
    if not os.path.exists(config_file):
        module_pane.console_output(
            "Config file " + config_file + " not exists!")
        return None

    parser = configparser.ConfigParser()
    # 必须要有一个setion [mysql]
    try:
        parser.read(config_file)
    except Exception:
        module_pane.console_output(
            "There must be a section [mysql] in " + config_file)
        return None

    ret = {}
    if parser.has_section("mysql"):
        section = "mysql"
        db = parser.get(section, "db", fallback="")
        if db == "":
            # 不能没有db
            module_pane.console_output("Must have a option \"db\"")
            return None
        ret["db_type"] = "mysql"
        ret["host"] = parser.get(section, "host", fallback="localhost")
        ret["port"] = parser.getint(section, "port", fallback=3306)
        ret["user"] = parser.get(section, "user", fallback="root")
        ret["password"] = parser.get(section, "password", fallback="")
        ret["db"] = db
        # model所放位置，相对于项目目录
        ret["models_place"] = path + "/" + \
            parser.get(section, "models_place", fallback="models")
    return ret


# 处理mysql
# 返回表结构列表[item,...]，错误时返回None
# item (table_name,column_len,type_len,rows)
# rows [(column,type,comment),...]
def handle_mysql(host, port, user, password, db):
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, passwd=password, db=db)
    except Exception as e:
        module_pane.console_output(str(e))
        return None

    cursor = conn.cursor()

    tables = []

    # 查询表列表
    cursor.execute("select table_name from information_schema.tables where table_schema='" +
                   db + "' and table_type='base table'")
    table_names = []
    for row in cursor:
        table_names.append(row[0])

    # 查询表结构
    for table_name in table_names:
        module_pane.console_output("table " + table_name)
        cursor.execute("select COLUMN_NAME,DATA_TYPE,CHARACTER_MAXIMUM_LENGTH,NUMERIC_PRECISION,NUMERIC_SCALE,EXTRA from information_schema.columns where table_schema='" +
                       db + "' and table_name='" + table_name + "'")
        column_len = 0
        type_len = 0
        columns = []
        valid = True
        for t in cursor:
            column_name = t[0]
            data_type = t[1]
            max_len = t[2]
            precision = t[3]
            scale = t[4]
            extra = t[5]

            # 首字母大写
            column = first_upper(column_name)
            type1 = _TYPE.get(data_type, "")

            # 找不到对应的类型
            if type1 == "":
                module_pane.console_output(
                    "[ERRO] orm: data type (" + data_type + ") not found!")
                valid = False
                break

            comment = '`orm:"column(' + column_name + ')'
            if extra == "auto_increment":
                column = "Id"
                comment += ';auto"'
            if data_type == "decimal":
                comment += ';digits(' + str(precision) + \
                    ');decimals(' + str(scale) + ')'
            elif data_type == "date" or data_type == "datetime" or data_type == "time":
                comment += ';type(' + data_type + ')'
            elif data_type == "timestamp":
                comment += ';type(timestamp);auto_now'
            elif data_type == "char" or data_type == "varchar":
                comment += ';size(' + str(max_len) + ')'
            comment += '"`'

            if len(column) > column_len:
                column_len = len(column)

            if len(type1) > type_len:
                type_len = len(type1)

            columns.append((column, type1, comment))
        if valid:
            tables.append((table_name, column_len, type_len, columns))

    # 关闭数据连接
    cursor.close()
    conn.close()

    return tables


# 建立mysql表对应的model文件
class GodevOrmBeegoCommand(sublime_plugin.WindowCommand):

    def run(self):
        # 先检测是否可运行
        (name, path) = common.get_project_info(False)
        if len(name) == 0:
            sublime.status_message("Current file not in GOPATH.")
            return

        t = threading.Thread(target=self.doit)
        t.start()

    def doit(self):
        config = read_config()
        if config is None:
            module_pane.console_output("[ERROR] Build database structs FAIL!")
            return

        self.config = config
        if config["db_type"] == "mysql":
            self.do_mysql()

    # 处理mysql数据库
    def do_mysql(self):
        module_pane.console_output("Start read database structs")
        host = self.config["host"]
        port = self.config["port"]
        user = self.config["user"]
        password = self.config["password"]
        db = self.config["db"]
        models_place = self.config["models_place"]
        tables = handle_mysql(host, port, user, password, db)
        if tables is None:
            module_pane.console_output("[ERROR] Build database structs FAIL!")
            return

        for t in tables:
            table_name = t[0]
            column_len = t[1]
            type_len = t[2]
            rows = t[3]
            structs = ""
            l = len(rows)
            for i in range(0, l):
                row = rows[i]
                s = "    %-" + str(column_len) + "s %-" + \
                    str(type_len) + "s %s"
                # print(s)
                structs += s % (row[0], row[1], row[2])
                if i < (l - 1):
                    structs += "\n"
            text = _TEMPLATE
            text = text.replace("{{table_name}}", first_upper(table_name))
            text = text.replace("{{table_name_str}}", table_name)
            text = text.replace("{{structs}}", structs)
            # print(text)
            # 保存
            savepath = models_place + "/" + table_name + ".go"
            lib_helper.write_file(savepath, text)

        module_pane.console_output("[SUCCESS] Build database structs SUCCESS!")
