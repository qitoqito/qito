#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : qq.py
@Time    : 2022/10/8 上午10:49  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "腾讯音乐(QQ)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            if "songid" in p["parse"]:
                vid = self.match(r"songid=(\w+)", p["parse"])
            elif "song/" in p["parse"]:
                vid = self.match(r"song\/(\w+)", p["parse"])
            elif "songDetail" in p["parse"]:
                vid = self.match(r"songDetail\/(\w+)", p["parse"])

        else:
            vid = p["parse"]
        mParams = {
            "hostUin": "0",
            "format": "jsonp",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "yqq",
            "needNewCode": "0",
            "data": '{"comm":{"ct":24,"cv":0},"songinfo":{"method":"get_song_detail_yqq","param":{"song_type":0,"song_mid":"%s"},"module":"music.pf_song_detail_svr"}}'
            % vid,
        }
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg?{}".format(self.urlencode(mParams))
        html = self.curl(url)
        self.logging.debug(f"getInfo: {html} \r\n")
        json = self.loads(html)
        assert json["songinfo"]["data"], "data"
        data = json["songinfo"]["data"]

        company = self.haskey(data, "info.company.content.0.value")
        genry = self.haskey(data, "info.genre.content.0.value")

        album = data["track_info"]["album"]["title"].strip()
        duration = data["track_info"]["interval"]
        cover = data["track_info"]["album"]["mid"]
        image = f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{cover}.jpg"
        title = data["track_info"]["title"].strip()
        cid = data["track_info"]["id"]
        publish = data["track_info"]["time_public"]
        language = data["info"]["lan"]["content"][0]["value"].strip()
        singer = " | ".join([i["title"].strip() for i in data["track_info"]["singer"]])
        return self.compact()

    def parse(self):
        p = self.params
        vid = p["vid"]
        params = {
            "hostUin": "0",
            "format": "jsonp",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "yqq",
            "needNewCode": "0",
            "data": '{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"7152021848","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"7152021848","songmid":["%s"],"songtype":[0],"uin":"","loginflag":1,"platform":"20"}},"comm":{"uin":"","format":"json","ct":24,"cv":0}}'
            % vid,
        }
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg?{}".format(self.urlencode(params))
        html = self.curl(url)
        self.logging.debug(f"getSong: {html} \r\n")
        json = self.jsonParse(html)
        try:
            m4a = (
                "http://isure.stream.qqmusic.qq.com/"
                + json["req_0"]["data"]["midurlinfo"][0]["purl"]
            )
            # print(m4a)
            playback = ext = "m4a"
        except:
            raise NotImplementedError("data")

        return self.compact()
