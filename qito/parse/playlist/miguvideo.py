#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : miguvideo.py
@Time    : 2022/11/28 下午2:05  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "咪咕视频列表"

    def videoList(self, params):
        if params["parse"].startswith("http"):
            cover = self.match("=(\d+)", params["parse"])
        else:
            cover = params["parse"]
        url = f"https://program-sc.miguvideo.com/program/v3/cont/content-info/{cover}/1"
        html = self.curl(url)
        json = self.loads(html)
        lists = [
            {"title": i["name"], "parse": i["pID"]}
            for i in self.haskey(json, "body.data.datas")
        ]
        return {"data": lists, "category": "video", "type": "miguvideo"}
