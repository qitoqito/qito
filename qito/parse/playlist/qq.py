#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : qq.py
@Time    : 2022/9/8 下午10:51  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "腾讯剧集列表"

    def videoList(self, params):
        cover = ""
        if params["parse"].startswith("http"):
            cover = self.match("cover\/(\w+)", params["parse"])
            vid = self.match(
                ["vid=(\w+)", "/(\w+)$", "cover\/\w+\/(\w+)"],
                params["parse"],
            )
            html = self.curl(params["parse"])
            if not vid:
                vid = self.match(
                    [
                        "&vid=(\w+)",
                        "vid:\s*[\"'](\w+)",
                        "vid\s*=\s*[\"']\s*(\w+)",
                        '"vid":"(\w+)"',
                    ],
                    html,
                )
        else:
            vid = params["parse"]
        if vid and not cover:
            u = f"https://m.v.qq.com/play.html?cid=&vid={vid}&ptag=v_qq_com%23v.play.adaptor%233"
            h = self.curl(
                {
                    "url": u,
                }
            )
            cover = self.match(["cid%22%3A%22(\w+)", "cid\s*=\s*'(\w+)'"], h)

        s = self.curl(
            {
                "url": f"https://node.video.qq.com/x/api/float_vinfo2?cid={cover}",
                # 'from':'',
            }
        )
        d = self.jsonParse(s)
        serial = d["c"]["title"]
        playList = d["c"]["video_ids"]
        return {"data": playList, "category": "video", "type": "qq", "serial": serial}
