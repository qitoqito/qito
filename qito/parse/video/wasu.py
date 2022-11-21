#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : wasu.py
@Time    : 2022/11/21 下午3:48  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "()"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match(r"id\/(\d+)", p["parse"])
        else:
            vid = p["parse"]
        html = self.curl(
            f"https://www.wasu.cn/Play/show/id/{vid}" 
        )
        image = self.match("_playpic\s*=\s*'([^']+)',", html)
        title = self.match("ali_vodName\s*=\s*'(.*?)',", html)
        duration = self.match("_playDuration\s*=\s*'([^']+)',", html)
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        xml = self.curl(
            {"url": f"http://www.wasu.cn/Api/getPlayInfoById/id/{vid}/datatype/xml"}
        )
        self.logging.debug(f"getXml: {xml} \r\n")
        videoList = self.matchAll(
            "<hd\d+>\s*<bitrate>(\d+)<\/bitrate>\s*<video>(aHR[^\<]+)<\/video>\s*<\/hd\d+>",
            xml,
        )

        duration = ""
        if videoList:
            duration = self.match("<duration>(\d+)<\/duration>", xml)
            bitrate = [int(k[0]) for k in videoList]
            bitrate.sort()
            quality = [self.resolution(i) for i in bitrate]
            show = self.data(quality, p["hd"])
            rate = str(self.data(bitrate, p["hd"]))
            for i in videoList:
                if rate == i[0]:
                    base = i[1]
                    break
        else:
            url = f"https://www.wasu.cn/Play/show/id/{vid}"
            html = self.curl(url, {"encoding": "utf8"})
            base = self.match("_playUrl = '([^\/]+?)',", html)
        assert base, "lists"
        getVideoUrl = f"http://apiontime.wasu.cn/Auth/getVideoUrl?id={vid}&cdndomain=cnc&url={base}"

        getVideoSource = self.curl(getVideoUrl)
        self.logging.debug(f"getVideo: {getVideoSource} \r\n")
        enc = self.match('CDATA\[([^\]"]+)\]\]', getVideoSource)

        dec = self.stream_code(enc)
        sign = self.sha1(vid + "-----w-----" + "19")

        mp4 = (
            "%s&vid=%s&cid=19&version=MIPlayer_V1.7.0&category=2018050300001&sign=%s"
            % (
                self.sub(
                    "/http.+\/pcsan12/", "http://padvod-h5-bj.wasu.cn/pcsan12", dec
                ),
                vid,
                sign,
            )
        )

        segs = [{"url": mp4, "duration": duration}]
        return self.compact()

    def resolution(self, x):
        if x >= 1500000:
            q = "1080p"
        elif x >= 1000000:
            q = "720p"
        elif x >= 700000:
            q = "超清"
        elif x >= 400000:
            q = "高清"
        else:
            q = "标清"
        return q

    def stream_code(self, params1):
        if params1.find(".mp4") > 0:
            return params1
        else:
            return self.stream_auth(params1)

    def stream_auth(self, param1):
        param2 = self.md5("wasu!@#48217#$@#1")
        loc7 = self.md5(param2[0:16])
        loc8 = self.md5(param2[16:32])
        loc11 = loc7 + self.md5(loc7 + param1[0:4])
        loc12 = len(loc11)
        param1 = self.b64decode(param1[4:], 0)
        loc13 = len(param1)

        loc14 = []
        loc15 = []
        loc16 = 0
        while loc16 < 128:
            loc14.append(loc16)
            loc15.append(ord(loc11[loc16 % loc12]) & 255)
            loc16 += 1

        loc16 = 0
        loc17 = 0
        loc19 = 0
        while loc16 < 128:
            loc17 = (loc17 + loc14[loc16] + loc15[loc16]) % 128
            loc19 = loc14[loc16]
            loc14[loc16] = loc14[loc17]
            loc14[loc17] = loc19
            loc16 += 1

        loc17 = 0
        loc16 = 0
        loc18 = 0
        loc20 = []
        while loc16 < loc13:
            loc18 = (loc18 + 1) % 128
            loc17 = (loc17 + loc14[loc18]) % 128
            loc19 = loc14[loc18]
            loc14[loc18] = loc14[loc17]
            loc14[loc17] = loc19
            loc20.append(
                chr(param1[loc16] & 255 ^ loc14[(loc14[loc18] + loc14[loc17]) % 128])
            )
            loc16 += 1

        return ("".join(loc20))[26:]
