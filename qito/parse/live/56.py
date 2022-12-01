#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : 56.py
@Time    : 2022/12/1 下午9:58  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "千帆直播(56)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("\/(\d+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://qf.56.com/{vid}?union=56_home"
            html = self.curl(url)
            anchorInfo = self.match("pageInfo.anchor\s*=\s*([^\}]+)", html)
            if anchorInfo:
                anchor = self.match("nickName:\s*'([^']+)',", anchorInfo)
                title = f"{anchor}的直播间"
                image = self.match("cover:\s*'([^']+)',", anchorInfo)

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        url = f"https://qf.56.com/{vid}?union=56_home"
        html = self.curl(url)
        anchorRoom = self.match("pageInfo.anchorRoom\s*=\s*([^\}]+)", html)
        assert anchorRoom, "data"

        isLive = self.match("roomLive:\s*'([^']+)'", anchorRoom)
        assert isLive == "1", "close"

        anchorInfo = self.match("pageInfo.anchor\s*=\s*([^\}]+)", html)
        if anchorInfo:
            anchor = self.match("nickName:\s*'([^']+)',", anchorInfo)
            title = f"{anchor}的直播间"
            image = self.match("cover:\s*'([^']+)',", anchorInfo)

        match = self.matchAll("(rUrl|hUrl|lUrl)\s*:\s*'([^']+)'", html)
        lists = dict(match)

        assert lists, "lists"

        qualitys = list(lists.keys())

        try:
            qualitys.sort(key=["lUrl", "hUrl", "rUrl"].index)
        except:
            pass
        dicts = {"lUrl": "标清", "hUrl": "高清", "rUrl": "超清"}
        quality = [dicts[i] for i in qualitys]
        show = self.data(quality, p["hd"])
        flv = self.sub(
            ["\/\/(.*?)\/live", "\?", "get_url=\d+"],
            ["https://v-ngb.qf.56.com/live", ".flv?", "get_url=10"],
            lists[self.data(qualitys, p["hd"])],
        )

        ext = playback = "flv"
        return self.compact()
