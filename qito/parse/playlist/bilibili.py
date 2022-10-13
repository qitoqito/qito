#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : bilibili.py
@Time    : 2022/10/12 下午7:42  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "哔哩哔哩剧集列表"

    def videoList(self, params):
        url=params["parse"]
        lists = []
        if "space.bilibili.com" in url:
            uid = self.match("space.bilibili.com\/(\d+)", url)
            for i in range(1000):
                page = i + 1
                u = f"https://api.bilibili.com/x/space/arc/search?mid={uid}&ps=30&tid=0&pn={page}&keyword=&order=pubdate"
                html = self.curl(u)
                json = self.loads(html)
                if json["code"] != 0:
                    break
                count = json["data"]["page"]["count"]
                y = count / 30
                vlist = self.column(json["data"]["list"]["vlist"], "aid")
                lists.extend(vlist)
                if page > y:
                    break
        elif "/md" in url:
            content = self.curl(url)
            seasonId = self.match('"season_id":(\d+)', content) or self.match(
                "\/md(\d+)", url
            )
            seasonUrl = (
                f"https://api.bilibili.com/pgc/web/season/section?season_id={seasonId}"
            )

            html = self.curl(seasonUrl)
            json = self.loads(html)
            assert json["code"] == 0, "data"
            lists = self.column(json["result"]["main_section"]["episodes"], "aid")

        elif "/av" in url:
            aid = self.match("\/av(\d+)", url)
            pageUrl = f"https://api.bilibili.com/x/player/pagelist?aid={aid}&jsonp=jsonp"
            html = self.curl(pageUrl)
            json = self.loads(html)
            assert json["code"] == 0, "data"
            lists = [
                f"https://www.bilibili.com/video/av{aid}?p={i + 1}"
                for i in range(len(json["data"]))
            ]
        else:
            html = self.curl(url)
            data = self.match("window.__INITIAL_STATE__=(\{.*?\});", html)
            json = self.loads(data)
            lists = [
                {"parse": str(i["cid"]), "title": "%s %s" % (i["title"], i["longTitle"])}
                for i in json["epList"]
            ]
        return {"data": lists, "category": "video", "type": "bilibili"}
