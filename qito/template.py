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
        self.getConfig("profile")
        # 处理proxy代理模块
        if params.get("proxy"):
            self.proxy = params["proxy"]
        if params.get("debug"):
            self.debug = 1
        self.run()

    def run(self):
        parse = {}
        if self.get("iniPath"):
            ini = self.parseIni(f'{self.iniPath}/{self.params["type"]}.ini')
            config = self.parseIni(f"{self.iniPath}/config.ini")

        else:
            ini = self.parseIni(f'{self.abspath}/ini/{self.params["type"]}.ini')
            config = self.parseIni(f"{self.abspath}/ini/config.ini")

        # for k, v in ini.items():
        #     self.set(k, v)
        # for k, v in config.items():
        #     self.set(k, v)

        if self.params.get("cookie"):
            self.cookie = self.params["cookie"]
        if self.params.get("proxy"):
            self.proxy = self.params["proxy"]

        if self.get("require"):
            self.include()
        try:
            query = self.query()
        except:
            query = {}

        try:
            if self.params.get("query"):
                parse = {**self.params, **query}

            else:

                self.params = {**self.params, **query}
                parse = self.parse()
                parse = {**self.params, **parse}

            self.data = parse
            if self.data.get("title"):
                self.data["title"] = self.sub(
                    "[’!\"#$%&'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+",
                    "",
                    self.data["title"],
                )
            if "show" in parse:
                self.prepare_quality(parse)
            if self.params.get("download") and not self.params.get("query"):
                self.execute_init()
            elif self.params.get("player") and not self.params.get("query"):
                self.execute_init()
            elif self.params.get("info") and not self.params.get("query"):
                self.execute_init()
            elif self.params.get("json"):
                if self.get("jsonFilter"):
                    filter = self.jsonFilter.split("|")
                    parse = dict([k, v] for k, v in parse.items() if k not in filter)
                print(json.dumps(parse, indent=2, ensure_ascii=False))
            else:
                parse["code"] = 0
                if self.get("jsonFilter"):
                    filter = self.jsonFilter.split("|")
                    parse = dict([k, v] for k, v in parse.items() if k not in filter)
                print(parse)
        except AssertionError as e:
            print(e)
        except NotImplementedError as e:
            print(e)

    def compact(self):
        func = sys._getframe(1).f_code.co_name
        getLocals = sys._getframe(1).f_locals
        # params = getattr(self, f"prepare_{func}")(self.params["category"])
        params = self.prepare_compact()
        inter = set(params).intersection(set(getLocals.keys()))
        return self.prepare_stream(getLocals, inter, func)
