#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : pps.py
@Time    : 2022/12/1 下午3:26  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "奇秀直播(PPS)"

    def query(self):
        p = self.params
        if "gamelive.iqiyi.com" in p["parse"]:
            p["parse"] = self.curl(p["parse"], {"response": "location"})

        if self.hasurl(p["parse"]):

            vid = self.match("\/(\d+)", p["parse"])
        else:
            vid = p["parse"]

        url = f"https://x.pps.tv/room/{vid}"

        html = self.curl(url)
        uid = self.match(['"user_id"\s*:\s*"(\d+)"', "user_id=(\d+)"], html)
        title = self.loads(self.match('"room_name":("[^"]*"),', html))
        roomConfig = self.match("_room_config\s*=\s*([^;]+)", html)
        self.logging.debug(f"getRoomConfig: {roomConfig} \r\n")
        try:
            json = self.loads(roomConfig)
            anchor = json["anchor_info"]["nick_name"]
            title = json["live_info"]["live_title"]
            image = json["live_info"]["live_image"]
        except:
            pass

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        timestamp = self.time
        assert p["uid"], "uid"
        uid = p["uid"]
        url = "https://m-glider-xiu.pps.tv/v2/stream/get.json"
        ary = {
            "smooth": "标清",
            "high": "高清",
            "source": "超清",
        }
        quality = list(ary.values())
        show = self.data(quality, p["hd"])
        rate = self.data(ary.keys(), p["hd"])

        postData = {
            "anchor_id": uid,
            "app_key": "show_web_h5",
            "type_id": "1",
            "vid": "1",
            "version": "1.0.0",
            "platform": "1_10_101",
            "time": timestamp,
            "netstat": "wifi",
            "device_id": self.md5(uid),
            "bit_rate_type": rate,
            "protocol": "5",
        }
        postData["sign"] = self.getSign(postData)
        html = self.curl(url, {"method": "post", "form": postData})
        self.logging.debug(f"getJson: {html} \r\n")
        json = self.loads(html)

        assert json["code"] == "A00000", "close"
        flv = json["data"]["https_flv"]
        playback = ext = "flv"
        return self.compact()

    def getSign(self, params):
        # string=self.self.urlencode(params)+"w!ytDgy#lEXWoJmN4HPf"
        s = []
        for key in sorted(params.keys()):
            s.append(f"{key}:{params[key]}")
        s.append("w!ytDgy#lEXWoJmN4HPf")
        s = "".join(s)
        return self.sha1(s)
