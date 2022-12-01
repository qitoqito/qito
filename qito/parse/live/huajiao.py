#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : huajiao.py
@Time    : 2022/12/1 下午9:44  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "花椒直播(HUAJIAO)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("\/(\d+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://www.huajiao.com/l/{vid}"
            turl = self.curl(url, {"response": "location"})
            assert turl != "https://www.huajiao.com/", "close"
            html = self.curl(url)
            keywords = self.match('name="keywords" content="([^"]+)"', html)
            spl = keywords.split(",")
            title = spl[0]
            anchor = spl[1]

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]

        url = f"https://www.huajiao.com/l/{vid}"
        turl = self.curl(url, {"response": "location"})
        assert turl != "https://www.huajiao.com/", "close"
        html = self.curl(url)
        keywords = self.match('name="keywords" content="([^"]+)"', html)
        spl = keywords.split(",")
        title = spl[0]
        anchor = spl[1]
        sn = self.match('"sn":"([^"]+)"', html)
        uid = self.match('"uid":"(\d+)"', html)

        sUrl = f"https://live.huajiao.com/live/substream?guid=aff3a83c325ea1db22262bc87361b590&platform=android&rand=0.8804918002581339&time={ self.timestamp}&version=1.0.0&sn={sn}&uid={uid}&liveid={vid}&encode=h265"
        substream = self.curl(sUrl)
        self.logging.debug(f"getLive: {substream} \r\n")
        json = self.loads(substream)
        assert json["errno"] == 0, "data"
        flv = json["data"]["h264_url"]
        ext = playback = "flv"
        return self.compact()
