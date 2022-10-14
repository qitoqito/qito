#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ixigua.py
@Time    : 2022/10/14 上午8:44  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "西瓜视频(IXIGUA)"

    def query(self):
        p = self.params
        if p["parse"].isdigit():
            p["parse"] = f"https://www.ixigua.com/i{p['parse']}/"
        if self.hasurl(p["parse"]):

            p["parse"] += "&wid_try=1" if "?" in p["parse"] else "?wid_try=1"
            html = self.curl(
                {
                    "url": p["parse"],
                    "encoding": "utf-8",
                    "cookie": "__ac_nonce=05348ace2003276552d00",
                }
            )
            context = {"html": html}

            vid = self.match(['"video_id"\s*:\s*"(\w+)"'], html)
            title = self.match(
                'title\s*data-react-helmet="true"\>([^-]+)', html
            ).strip()
        else:
            vid = p["parse"]
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        try:
            if self.haskey(p, "context.html"):
                html = p["context"]["html"]
            else:

                html = self.curl(p["parse"])

            ssrData = self.match("_SSR_HYDRATED_DATA\s*=\s*([^\<]+)", html)

            self.logging.debug(f"getJson: {ssrData} \r\n")
            assert ssrData, "data"

            json = self.loads(ssrData.replace(":undefined", ':"undefined"'))

            packerData = self.haskey(
                json, "anyVideo.gidInformation.packerData.video"
            ) or self.haskey(json, "anyVideo.gidInformation.packerData")
            videoList = packerData["videoResource"]["normal"]["video_list"]

            lists = self.column(videoList.values(), "", "definition")

            quality = list(sorted(lists, key=lambda x: x[0]))

            show = self.data(quality, p["hd"])

            mp4 = self.b64decode(lists[show]["main_url"])

            size = lists[show]["size"]

            duration = packerData["videoResource"]["dash"]["video_duration"]
            title = packerData["episodeInfo"]["title"]
            image = packerData["episodeInfo"]["coverList"][0]["url"]

        except:
            url = f"http://i.snssdk.com/video/urls/1/toutiao/mp4/{vid}?watermark=0&h265=0&nobase64=1"
            html = self.curl(url)
            self.logging.debug(f"getStaticVideo: {html} \r\n")
            json = self.loads(html)
            assert "data" in json, "rule"
            videoList = json["data"]["video_list"]
            lists = self.column(videoList.values(), "", "definition")
            assert lists, "lists"
            quality = list(lists.keys())
            show = self.data(quality, p["hd"])
            mp4 = lists[show]["main_url"]
            segs = [{"url": mp4, "size": lists[show]["size"]}]
            image = json["data"]["poster_url"]
            duration = json["data"]["video_duration"]
        return self.compact()
