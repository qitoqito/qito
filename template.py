#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : template.py
@Time    : 2022/02/13 下午4:52
"""

import time, importlib, os, sys, logging, json

from util import common

from pathlib import Path


class Template(common.Common):
    def __init__(self):
        super().__init__()
        self.title = "QITOER"

        self.proxy = ""
        self.cookie = ""
        self.abspath = os.path.abspath(os.path.dirname(__file__))
        self.cwd = os.getcwd()

    def init(self, params):
        self.params = params
        self.getConfig("config")
        # 处理proxy代理模块
        if params.get("proxy"):
            self.proxy = params["proxy"]

        self.run()

    def run(self):
        if self.get("iniPath"):
            ini = self.parseIni(f'{self.iniPath}/{self.params["type"]}.ini')
        else:
            ini = self.parseIni(f'{self.abspath}/ini/{self.params["type"]}.ini')

        for k, v in ini.items():
            self.set(k, v)

        if self.get("import"):
            self.include()
        try:
            query = self.query()
        except:
            query = {}

        if self.params.get("query"):
            parse = {**self.params, **query}

        else:
            self.params = {**self.params, **query}

            parse = self.parse()
            parse = {**self.params, **parse}

        self.data = parse
        if self.data.get("title"):
            self.data["title"] = self.data["title"].replace(r"，", "_")
        if "show" in parse:
            self.prepare_quality(parse)
        if self.params.get("download") and not self.params.get("query"):
            self.execute_init()
        elif self.params.get("player") and not self.params.get("query"):
            self.execute_init()
        elif self.params.get("dumps"):
            print(json.dumps(parse, indent=2, ensure_ascii=False))
        else:
            parse["code"] = 0
            print(parse)

    def compact(self):
        func = sys._getframe(1).f_code.co_name
        getLocals = sys._getframe(1).f_locals
        params = getattr(self, f"prepare_{func}")(self.params["category"])
        inter = set(params).intersection(set(getLocals.keys()))
        return self.prepare_stream(getLocals, inter, func)
