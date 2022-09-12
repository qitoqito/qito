#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : youku.py
@Time    : 2022/9/4 下午5:01  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "优酷剧集列表"

    def videoList(self, params):
        url = params["parse"]
        if url.startswith("http"):
            vid = self.match(["id_([^\"'\.]+)\.", "sid\/([^\"']+)\/v.swf"], url)
        else:
            vid = url

        s = self.curl(
            {
                "url": f"https://search.youku.com/api/search?appScene=show_episode&showIds={vid}&appCaller=h5"
            }
        )
        data = self.loads(s)

        playlist = self.column(data["serisesList"], "videoId")
        return {"data": playlist, "category": "video", "type": "youku"}
