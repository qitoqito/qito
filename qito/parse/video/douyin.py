#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : douyin.py
@Time    : 2022/11/12 下午1:23  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "抖音视频(DOUYIN)"

    def query(self):
        p = self.params
        if not self.hasurl(p["parse"]) and not p["parse"].isdigit():
            p["parse"] = f"https://v.douyin.com/{p['parse']}/"

        if self.hasurl(p["parse"]):
            url = self.curl({"url": p["parse"], "response": "location"})

            aid = self.match(["\/video\/(\d+)", "mid=(\d+)"], url)
            api = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aid}"

            html = self.curl(api)

            json = self.loads(html)

            video = self.haskey(json, "item_list.0.video", "", "data")

            vid = video["vid"]
            image = video["origin_cover"]["url_list"][0]
            title = json["item_list"][0]["desc"]
            return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        url = f"http://i.snssdk.com/video/urls/1/toutiao/mp4/{p['vid']}?watermark=0&h265=0&nobase64=1"
        html = self.curl(url)
        json = self.loads(html)

        data = self.haskey(json, "data", "", "data")
        videoList = data["video_list"]
        lists = self.column(videoList, "", "definition")
        assert lists, "lists"
        image = data["poster_url"]
        duration = data["video_duration"]
        quality = list(lists.keys())
        show = self.data(quality, p["hd"])
        mp4 = lists[show]["main_url"]
        size = lists[show]["size"]
        return self.compact()
