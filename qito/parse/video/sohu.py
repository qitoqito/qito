#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : sohu.py
@Time    : 2022/9/27 下午12:14  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "搜狐视频(SOHU)"

    def query(self):
        p = self.params
        if p["parse"].isdigit():
            vid = p["parse"]
        else:
            html = self.curl(p["parse"])
            vid = self.match(
                [
                    'data-vid="(\d+)"',
                    "\s+vid:(\d+),",
                    'var\s+vid="(\d+)"',
                    "vid:\s*'(\d+)'",
                    "vid\s*=\s*\\\\'(\d+)\\\\'",
                ],
                html,
            )
        assert vid, "vid"
        for i in range(2):
            site = int(i) + 1
            getInfo = self.curl(
                f"https://api.tv.sohu.com/v4/video/info/{vid}.json?api_key=f351515304020cad28c92f70f002261c&plat=17&site={site}"
            )
            data = self.loads(getInfo)
            if "data" in data:
                break
        self.logging.debug(f"getInfo: {getInfo} \r\n")
        assert "errorCode" not in data, data["statusText"]

        otype = "tv" if site == 1 else "my"
        title = data["data"]["video_name"]
        image = data["data"]["hor_w16_pic"]
        duration = data["data"]["total_duration"]

        context = {}
        ary = {"nor": "nor", "high": "hig", "super": "sup", "original": "original"}
        context["bytes"] = {
            ary[i]: data["data"]["clips_bytes_" + i]
            for i in ["nor", "high", "super", "original"]
            if "clips_bytes_" + i in data["data"]
        }
        return self.compact()

    def parse(self):
        p = self.params
        vid = p["vid"]
        timestamp = self.timestamp

        # h5_cc.gif上报,数据不卡顿
        muid = timestamp * 100 + 98
        uid = timestamp * 1000 + 99
        reportUrl = f"https://z.m.tv.sohu.com/h5_cc.gif?t={muid}&uid={uid}&position=play_fail_cookie&op=click&details=%7B%7D&nid=&url=http%253A%252F%252F127.0.0.1%252Fsohu%252Ftest.html&refer=&screen=1366x768&os=other&platform=Win32&passport=&vid={vid}&pid=1231223&channeled=1212130002&MTV_SRC=11050001"
        self.curl(reportUrl)

        if p.get("oytpe"):
            sites = [p["otype"]]
        else:
            sites = ["tv", "my"]

        for i in sites:
            site = 2 if i == "my" else 1
            playParams = {
                "vid": vid,
                "site": site,
                "appid": "tv",
                "api_key": "f351515304020cad28c92f70f002261c",
                "plat": "17",
                "sver": "1.0",
                "partner": "1",
                "uid": uid,
                "muid": muid,
                "_c": "1",
                "pt": "1",
                "qd": "680",
                "src": "11050001",
                "aid": "1231223",
            }
            api = "https://m.tv.sohu.com/phone_playinfo"
            getSource = self.curl({"url": api, "params": playParams}).replace(
                "http:", "https:"
            )
            data = self.loads(getSource)
            if "data" in data:
                break
        self.logging.debug(f"getVideo: {getSource} \r\n")
        assert "errorCode" not in data, data["statusText"]
        title = data["data"]["video_name"]
        image = data["data"]["hor_w16_pic"]
        duration = data["data"]["total_duration"]

        ary = ["nor", "hig", "sup", "original"]

        d = []
        e = []
        f = []
        segs = []
        for j in ary:
            if self.haskey(data, "data.urls.mp4.%s" % j):
                if len(data["data"]["urls"]["mp4"][j]) > 0:
                    d.append(j)
            if self.haskey(data, "data.urls.m3u8.%s" % j):
                if len(data["data"]["urls"]["m3u8"][j]) > 0:
                    e.append(j)
            if j in data["data"]["durations"]:
                if len(data["data"]["durations"][j]) > 0:
                    f.append(j)
        assert d, "lists"
        quality = d
        show = self.data(quality, p["hd"])
        mp4Data = data["data"]["urls"]["mp4"][show]
        durData = data["data"]["durations"][show]

        try:
            bt = p["context"]["bytes"][show].split(",")
            for i in tuple(zip(mp4Data, durData, bt)):
                segs.append(
                    {
                        "url": self.replace("\d+\.\d+\.\d+\.\d+", "data.vod.itc.cn", i[0]),
                        "duration": i[1],
                        "size": int(i[2]),
                    }
                )

        except:
            for i in tuple(zip(mp4Data, durData)):
                segs.append(
                    {
                        "url": self.sub("\d+\.\d+\.\d+\.\d+", "data.vod.itc.cn", i[0]),
                        "duration": i[1],
                    }
                )
        m3u8 = (
            data["data"]["urls"]["m3u8"][self.data(e, p["hd"])][0] + "&oth=&cd=&prod=h5"
        )
        mp4 = (
            data["data"]["urls"]["downloadUrl"][0][0]
            + "&qd=68001&src=11050001&ca=4&cateCode=101&_c=1&appid=tv&oth=&cd=&prod=h5"
        )
        playback = "m3u8"
        # 可能存在上报出错,重新上报一次
        self.curl(reportUrl)
        extra = {"replace": ["http:", "https:"]}
        return self.compact()
