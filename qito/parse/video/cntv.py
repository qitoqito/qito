#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : cntv.py
@Time    : 2022/11/14 下午4:00  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "央视视频(CNTV)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            html = self.curl(p["parse"])
            vid = self.match(
                [
                    '"videoCenterId","(\w+)"',
                    'itemguid="(\w+)"',
                    'guid\s*=\s*"(\w+)"',
                    "initMyAray\s*=\s*'([^']+)'",
                ],
                html,
            )
        else:
            vid = p["parse"]
        assert vid, "vid"
        if p.get("query"):
            info = self.curl(f"http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={vid}")
            self.logging.debug(f"getVideoInfo: {info} \r\n")
            json = self.loads(info)
            if json["ack"] == "yes":
                title = json["title"]
                duration = json["video"]["totalLength"]
                image = json["video"]["chapters"][0]["image"]
        return self.compact()

    def parse(self):
        p = self.params
        vid = p["vid"]

        info = self.curl(
            f"http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={vid}&vn=2054&vc=&pcv=152438790&uid=&wlan="
        )
        self.logging.debug(f"getHttpVideoInfo: {info} \r\n")
        json = self.loads(info)
        assert "video" in json, "data"
        title = json["title"]
        duration = json["video"]["totalLength"]
        image = json["video"]["chapters"][0]["image"]

        ary = ["chapters", "chapters2", "chapters3", "chapters4", "chapters5", "chapters6"]
        qua = ["流畅", "标清", "高清", "超清"]
        videos = [json["video"][i] for i in ary if i in json["video"]]
        quality = qua[: len(videos)]
        show = self.data(quality, p["hd"])
        data = self.data(videos, p["hd"])
        m3u8 = json["hls_url"]
        playback = "m3u8"
        segs = [{"url": i["url"], "duration": i["duration"]} for i in data]
        
        return self.compact()
