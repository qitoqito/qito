#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ixigua.py
@Time    : 2022/10/14 下午6:40  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "西瓜视频剧集列表"

    def videoList(self, params):
        if params["parse"].startswith("http"):
            cover = self.match("\/(\d+)", params["parse"])
        else:
            cover = params["parse"]
        json = self.curl(
            {
                "url": "https://www.ixigua.com/api/albumv2/details",
                "params": {"albumId": cover},
                "referer": "https://www.ixigua.com/",
                "response": "json",
            }
        )
        assert json["code"] == 200, "playlist"

        lists = [
            f'https://www.ixigua.com/{i["albumId"]}?id={i["episodeId"]}'
            for i in json["data"]["playlist"]
        ]
        return {"data": lists, "category": "video", "type": "ixigua"}
