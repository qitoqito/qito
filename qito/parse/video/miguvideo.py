#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : miguvideo.py
@Time    : 2022/11/14 下午4:18  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "咪咕视频(MIGUVIDEO)"
        self.appVersion = "2500090320"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("cid=(\d+)", p["parse"])
        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://webapi.miguvideo.com/gateway/playurl/v3/play/playurlh5?contId={vid}&rateType=3&clientId=&startPlay=true&channelId=0132_10010001005"
            html = self.curl(url)
            self.logging.debug(f"getInfo: {html} \r\n")
            json = self.loads(html)
            if json["code"] == "200":
                duration = json["body"]["content"]["duration"]
                title = json["body"]["content"]["contName"]
                pay = 1 if json["body"]["urlInfo"]["urlType"] == "trial" else ""
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        self.salt = f"{str(self.timestamp)[4:10]}96"
        rates = [2, 3, 4, 7] if self.cookie else [2, 3]
        url = f"https://play.miguvideo.com/playurl/v1/play/playurl?audio=false&contId={vid}&dolby=true&drm=true&flvEnable=false&h265=true&isMultiView=true&isRaming=0&isbox=false&nt=4&os=15.1.1&ott=false&rateType={self.data(rates,p['hd'])}&salt={self.salt}&serialNo=0&sign={self.getSign(vid)}&startPlay=true&timestamp={self.timestamp}&ua=iPhone13%2C3&vivid=1&vr=true&xavs2=true&xh265=true"

        html = self.curl(
            {"url": url, "encoding": "utf8", "headers": {"appVersion": "2500090310"}}
        )
        self.logging.debug(f"getPlayData: {html} \r\n")
        json = self.loads(html)
        assert json["code"] == "200", "data"
        duration = json["body"]["content"]["duration"]
        title = json["body"]["content"]["contName"]
        pay = "1" if json["body"]["urlInfos"][0]["urlType"] == "trial" else ""
        urlInfos = self.column(json["body"]["urlInfos"], "", "rateDesc")
        assert len(urlInfos) > 0, "lists"
        quality = list(urlInfos.keys())[::-1]
        show = self.data(quality, p["hd"])
        info = urlInfos[show]
        size = int(info["mediaSize"])
        m3u8 = info["url"]
        segs = [{"url": m3u8, "duration": duration}]
        ext = playback = "m3u8"
        return self.compact()

    def getSign(self, contId):
        tm = self.timestamp
        md5string = self.md5(f"{tm}{contId}{self.appVersion[:8]}")
        sign = self.md5(
            f"{md5string}9100fcd3470f4c0f88b403f12eaaf65amigu{self.salt[:4]}"
        )
        return sign
