#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : mgtv.py
@Time    : 2022/8/30 上午2:08  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "芒果视频(MGTV)"

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            vid = self.match("\/(\d+)\.", p["parse"])
        else:
            vid = p["parse"]

        if p.get("query"):
            url = f"https://pcweb.api.mgtv.com/video/info?vid={vid}"
            html = self.curl(url)
            self.logging.debug(f"getInfo: {html} \r\n")
            json = self.loads(html)
            if self.haskey(json, "data.info"):
                info = json["data"]["info"]
                title = info["videoName"]
                image = info["videoImage"]
                duration = self.seconds(info["time"])
        return self.compact()

    def parse(self):
        p = self.params

        timestamp = self.timestamp
        assert p["vid"], "vid"
        vid = p["vid"]

        params = {
            "abroad": "0",
            "appVersion": "5.5.1",
            "clipId": "",
            "device": "iPhone",
            "dname": "abcdefg",
            "guid": "898839756384243712",
            "keepPlay": "1",
            "localPlayVideoId": "0",
            "localVideoWatchTime": "0",
            "mac": "e4b87ad76c79eb1183bfffcbcda3887ea6e819e2",
            "osType": "ios",
            "osVersion": "9.3.2",
            "seqId": "436ee82f7f5027eb051c7f402235d1b8",
            "source": "1",
            "ticket": "",
            "videoId": vid,
        }
        url = "http://mobile-bjyg.api.mgtv.com/v7/video/getSource?{}".format(
            self.urlencode(params)
        )

        html = self.curl(
            {
                "url": "http://mobile-bjyg.api.mgtv.com/v7/video/getSource",
                "params": params,
                "headers": {
                    "useragent": "MGTV-iPhone-appstore/5.5.1 (iPhone; iOS 9.3.2; Scale/2.00)",
                    "encoding": "utf8",
                },
            }
        )
        self.logging.debug(f"getSource: {html} \r\n")
        data = self.loads(html)


        assert data["data"], data["msg"]

        adparams = self.loads(data["data"]["adParams"])

        pay = adparams["v"]["ispay"]
        title = data["data"]["videoName"]
        duration = data["data"]["time"]

        stream = data["data"]["videoSources"]
        vodList = [i for i in stream if i["url"]]
        column = self.column(vodList, "", "name")
        lists = list(column.values())[::-1]
        assert lists, "lists"
        quality = list(column.keys())[::-1]
        show = self.data(quality, p["hd"])
        vodDict = column[show]

        hlsUrl = f'https://disp.titan.mgtv.com{vodDict["url"]}&ver=0.2.21092&chk=b1e323d526786a667cf809f2e4bb2e25&guid=898839756384243712'
        size = int(vodDict["fileSize"])
        if pay:
            hlsUrl = self.sub("arange=\d+", "arange=0", hlsUrl)
        m3u8 = ""
        for z in range(3):
            hlsSource = self.curl(
                {
                    "url": hlsUrl,
                    "headers": {
                        "useragent": "MGTV-iPhone-appstore/5.5.1 (iPhone; iOS 9.3.2; Scale/2.00)",
                        "encoding": "utf8",
                    },
                }
            )
            hlsJson = self.loads(hlsSource)
            if hlsJson["info"].startswith("http"):
                m3u8 = hlsJson["info"]
                break
        self.logging.debug(f"getM3u8: {hlsSource} \r\n")
        assert m3u8, "m3u8"
        extra = {
            "headers": {
                "Accept-Language": "zh-cn",
                "X-Playback-Session-Id": "D11C5818-6A9D-401F-9F8E-E1093AFA2A46",
                "Accept": "*/*",
                "User-Agent": "AppleCoreMedia/1.0.0.16E227 (iPhone; U; CPU OS 12_2 like Mac OS X; zh_cn)",
                "Referer": m3u8,
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        }

        ext = playback = "m3u8"

        return self.compact()

    def encode_tk2(self, s):
        string = self.self.replace(
            ["+", "/", "="], ["_", "~", "-"], self.self.b64encode(s)
        )
        return string[::-1]
