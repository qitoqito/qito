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
        serial = ""
        url = params["parse"]
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
            pageUrl = (
                f"https://api.bilibili.com/x/player/pagelist?aid={aid}&jsonp=jsonp"
            )
            html = self.curl(pageUrl)
            json = self.loads(html)
            assert json["code"] == 0, "data"
            lists = [
                f"https://www.bilibili.com/video/av{aid}?p={i + 1}"
                for i in range(len(json["data"]))
            ]
        elif "/BV" in url:
            bvid = self.match("\/(BV\w+)", url)
            aid = self.dec(bvid)
            pageUrl = (
                f"https://api.bilibili.com/x/player/pagelist?aid={aid}&jsonp=jsonp"
            )
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
            serial = self.haskey(json, "mediaInfo.title")
            lists = [
                {
                    "parse": str(i["cid"]),
                    "title": "%s %s" % (i["titleFormat"], i["longTitle"]),
                }
                for i in json["epList"]
            ]

        return {
            "data": lists,
            "category": "video",
            "type": "bilibili",
            "serial": serial,
        }

    def dec(self, x):
        # https://www.zhihu.com/question/381784377/answer/1099438784
        tr = {
            "f": 0,
            "Z": 1,
            "o": 2,
            "d": 3,
            "R": 4,
            "9": 5,
            "X": 6,
            "Q": 7,
            "D": 8,
            "S": 9,
            "U": 10,
            "m": 11,
            "2": 12,
            "1": 13,
            "y": 14,
            "C": 15,
            "k": 16,
            "r": 17,
            "6": 18,
            "z": 19,
            "B": 20,
            "q": 21,
            "i": 22,
            "v": 23,
            "e": 24,
            "Y": 25,
            "a": 26,
            "h": 27,
            "8": 28,
            "b": 29,
            "t": 30,
            "4": 31,
            "x": 32,
            "s": 33,
            "W": 34,
            "p": 35,
            "H": 36,
            "n": 37,
            "J": 38,
            "E": 39,
            "7": 40,
            "j": 41,
            "L": 42,
            "5": 43,
            "V": 44,
            "G": 45,
            "3": 46,
            "g": 47,
            "u": 48,
            "M": 49,
            "T": 50,
            "K": 51,
            "N": 52,
            "P": 53,
            "A": 54,
            "w": 55,
            "c": 56,
            "F": 57,
        }
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        r = 0
        for i in range(6):
            r += tr[x[s[i]]] * 58**i
        return (r - add) ^ xor

    def enc(self, x):
        table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        x = (int(x) ^ xor) + add
        r = list("BV1  4 1 7  ")
        for i in range(6):
            r[s[i]] = table[x // 58**i % 58]
        return "".join(r)
