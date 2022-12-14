#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : le.py
@Time    : 2022/8/28 上午10:51  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "乐视剧集列表"

    def videoList(self, params):
        if params["parse"].startswith("http"):
            vid = self.match("\/vplay\/(\d+)", params["parse"])
            if not vid:
                cover = self.match("\/(\d+)", params["parse"])
        else:
            vid = params["parse"]
        serial = ""
        if vid:
            tvUrl = f"http://www.le.com/ptv/vplay/{vid}.html"
            tvSource = self.curl(
                {
                    "url": tvUrl,
                    # 'from':'',
                }
            )
            cover = self.match("pid\s*:\s*(\d+)", tvSource)
            serial = self.match('pTitle\s*:\s*"([^"]+)"', tvSource)

        url = f"http://d.api.m.le.com/detail/episode?pid={cover}&platform=pc&page=1&pagesize=2000&type=1&_=1565045426195"

        html = self.curl(url)
        json = self.loads(html)
        assert json["code"] == "200", "playlist"

        lists = [i["vid"] for i in json["data"]["list"]]
        if len(lists) and not serial:
            tvUrl = f"http://www.le.com/ptv/vplay/{lists[0]}.html"
            tvSource = self.curl(
                {
                    "url": tvUrl,
                    # 'from':'',
                }
            )
            serial = self.match('pTitle\s*:\s*"([^"]+)"', tvSource)

        return {"data": lists, "category": "video", "type": "le", "serial": serial}
