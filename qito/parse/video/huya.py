#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : huya.py
@Time    : 2022/11/30 上午12:07  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "虎牙视频(HUYA)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("\/(\d+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://liveapi.huya.com/moment/getMomentContent?cal&videoId={vid}"
            html = self.curl(url)
            self.logging.debug(f"getMomentContent: {html} \r\n")
            json = self.loads(html)
            if json["status"] == 200:
                data = json["data"]
                title = data["moment"]["videoInfo"]["videoTitle"]
                image = data["moment"]["videoInfo"]["videoCover"]
                duration = 0
                for d in data["moment"]["videoInfo"]["videoDuration"].split(":"):
                    duration = duration * 60 + int(d)

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        url = f"https://liveapi.huya.com/moment/getMomentContent?cal&videoId={vid}"
        html = self.curl(url)
        self.logging.debug(f"getVideo: {html} \r\n")
        json = self.loads(html)
        assert json["status"] == 200, "data"
        data = json["data"]
        title = data["moment"]["videoInfo"]["videoTitle"]
        image = data["moment"]["videoInfo"]["videoCover"]

        duration = 0
        for d in data["moment"]["videoInfo"]["videoDuration"].split(":"):
            duration = duration * 60 + int(d)

        lists = self.column(data["moment"]["videoInfo"]["definitions"], "", "defName")

        quality = list(lists.keys())[::-1]
        show = self.data(quality, p["hd"])
        video = lists[show]

        mp4 = video["url"]
        m3u8 = video["m3u8"]
        size = int(video["size"])
        segs = [{"url": mp4, "duration": duration, "size": size}]
        return self.compact()
