#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : sohu.py
@Time    : 2022/12/6 上午10:58  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "搜狐视频剧集(SOHU)"

    def videoList(self, params):
        url = params["parse"]

        if url.startswith("http"):
            vid = self.match("v\/([^.]+)", url)
        else:
            vid = url
        url = f"https://tv.sohu.com/v/{vid}.html"
        html = self.curl(
            {
                "url": url,
                # 'from':'',
            }
        )

        playlistId = self.match(r'playlistId\s*=\s*"(\d+)"', html)
        a = f"https://pl.hd.sohu.com/videolist?playlistid={playlistId}&o_playlistId=&pianhua=0&pagenum=1&pagesize=300&order=0&cnt=1&pageRule=2&withPgcVideo=1&withLookPoint=1&ssl=0&preVideoRule=3&_=1670295414041"
        b = self.curl(
            {
                "url": a,
                # 'from':'',
            }
        )
        c = self.jsonParse(b)
        playlist = [f"https:{i['pageUrl']}" for i in c["videos"]]
        serial = self.haskey(c, "albumName")
        return {"data": playlist, "category": "video", "type": "sohu", "serial": serial}
