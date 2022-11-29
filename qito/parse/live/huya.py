#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : huya.py
@Time    : 2022/11/29 下午11:04  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "虎牙直播(HUYA)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("com\/(\w+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://www.huya.com/{vid}"
            html = self.curl(url)
            b64 = self.match(r"stream: ({.+)\n.*?};", html)
            json = self.jsonParse(b64)
            data = json["data"][0]
            anchor = data["gameLiveInfo"]["nick"]
            title = data["gameLiveInfo"]["introduction"]
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        url = f"https://www.huya.com/{vid}"
        html = self.curl(url)
        b64 = self.match(r"stream: ({.+)\n.*?};", html)

        assert b64, "close"
        self.logging.debug(f"getStream: {b64} \r\n")
        json = self.jsonParse(b64)
        data = json["data"][0]
        vMultiStreamInfo = json["vMultiStreamInfo"]
        dicts = {i["sDisplayName"]: i["iBitRate"] for i in vMultiStreamInfo}
        quality = list(dicts.keys())[::-1]
        show = self.data(quality, p["hd"])
        ratio = dicts[show]
        anchor = data["gameLiveInfo"]["nick"]
        title = data["gameLiveInfo"]["introduction"]

        lists = data["gameStreamInfoList"][0]

        m3u8 = "{}/{}.{}?{}&ratio={}".format(
            lists["sHlsUrl"],
            lists["sStreamName"],
            lists["sHlsUrlSuffix"],
            lists["sHlsAntiCode"].replace("&amp;", "&"),
            ratio,
        )
        flv = "{}/{}.{}?{}&ratio={}".format(
            lists["sFlvUrl"],
            lists["sStreamName"],
            lists["sFlvUrlSuffix"],
            lists["sFlvAntiCode"].replace("&amp;", "&"),
            ratio,
        )
        playback = "m3u8"
        ext = "flv"

        return self.compact()
