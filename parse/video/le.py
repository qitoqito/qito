#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : le.com.py
@Time    : 2022/2/13 下午6:13  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "乐视视频(LE)"

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            vid = self.match("\/(\d+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            key = self.getKey(self.time)
            playParams = {
                "platid": "1",
                "splatid": "105",
                "tss": "ios",
                "id": vid,
                "detect": "0",
                "dvtype": "1000",
                "accessyx": "1",
                "domain": "m.le.com",
                "tkey": key,
                "devid": "6E622B75C984100A4495B527DCD5FB56F585580C",
                "source": "1001",
                "lang": "en",
                "region": "cn",
                "isHttps": "0",
            }
            content = self.curl(
                {
                    "url": "http://player-pc.le.com/mms/out/video/playJson.json",
                    "params": playParams,
                }
            )
            self.logging.debug(f"playJson: {content}")
            data = self.loads(content)
            if self.haskey(data, "msgs.playurl"):
                mid = data["msgs"]["playurl"]["mid"][1:-1]
                title = data["msgs"]["playurl"]["title"]
                image = sorted(data["msgs"]["playurl"]["picAll"].values())[-1]

        return self.compact()

    def parse(self):

        p = self.params
        assert p["vid"], "vid"
        pcode = "010210000"
        url = f"http://t.api.mob.app.letv.com/play?tm={self.time}&playid=0&tss=ios&pcode={pcode}&version=6.0&pid=93327&vid={p['vid']}&v=android&res=json&_debug=1"
        html = self.curl(url)
        self.logging.debug(f"getPlaySource: {html} \r\n")

        playJson = self.loads(html)
        assert self.haskey(playJson, "header.status", "1"), "data"
        ary = ["mp4", "180", "350", "1000", "800", "1300", "720p", "1080p", "1080p3m"]
        dispatch = playJson["body"]["videofile"]["infos"]
        lists = dict([[i.replace("mp4_", ""), dispatch[i]] for i in dispatch])
        quality = list(lists.keys())
        quality.sort(key=ary.index)
        show = self.data(quality, p["hd"])
        size = lists[show]["filesize"]
        m3u8Url = lists[show]["mainUrl"]
        mp4 = self.curl(
            {"url": m3u8Url.replace("tss=ios", "tss=no"), "response": "json"}
        )["location"]
        title = playJson["body"]["videoInfo"]["nameCn"]
        duration = playJson["body"]["videoInfo"]["duration"]
        image = list(playJson["body"]["videoInfo"]["picAll"].values())[-1]
        extra = {
            "headers": {
                "User-Agent": "LetvIphoneClient/9.23.3 (iPhone; iOS 13.7; Scale/2.00)",
                "Accept-Language": "zh-Hans-CN;q=1, en-CN;q=0.9",
            }
        }
        return self.compact()

    def getKey(self, t):
        for s in range(0, 8):
            e = 1 & t
            t >>= 1
            e <<= 31
            t += e
        return t ^ 185025305
