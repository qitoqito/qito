#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : bilibili.py
@Time    : 2022/11/17 下午3:48  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "()"
        self.require = ["importlib"]

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("\/(\d+)", p["parse"])
            html = self.curl(p["parse"])

            cid = self.match('"room_id":(\d+)', html) or vid
        else:
            cid = p["parse"]
        assert cid, "cid"

        if p.get("query"):
            url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={cid}"
            getinfo = self.curl(url)
            self.logging.debug(f"getInfo: {getinfo} \r\n")
            json = self.loads(getinfo)
            if json["code"] == 0:
                title = json["data"]["room_info"]["title"]
                image = json["data"]["room_info"]["keyframe"]
                anchor = json["data"]["anchor_info"]["base_info"]["uname"]
        return self.compact()

    def parse(self):
        p = self.params
        assert p["cid"], "cid"
        cid = p["cid"]

        url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={cid}"
        getinfo = self.curl(url)
        self.logging.debug(f"getInfo: {getinfo} \r\n")
        json = self.loads(getinfo)

        assert json["code"] == 0, "data"

        title = json["data"]["room_info"]["title"]
        image = json["data"]["room_info"]["keyframe"]
        anchor = json["data"]["anchor_info"]["base_info"]["uname"]
        # assert json["data"]["room_info"]["live_status"] == 1, "close"
        liveStatus = json["data"]["room_info"]["live_status"]

        if liveStatus == 0:
            raise NotImplementedError("close")
        elif liveStatus == 2:

            self.params["category"] = "video"

            url = f"https://api.live.bilibili.com/live/getRoundPlayVideo?room_id={cid}&type=flv&a=0.9907983099110425"
            html = self.curl(url)
            self.logging.debug(f"getExtra: {html} \r\n")
            json = self.loads(html)
            assert json["code"] == 0, "data"

            title = json["data"]["title"]
            videoCid = json["data"]["cid"]
            imp = self.modules["importlib"].import_module("parse.video.bilibili")
            a = imp.Main()
            a.params = {
                "vid": videoCid,
                "hd": p["hd"],
            }
            return a.parse()

        elif liveStatus == 1:

            # ary = {"150": "高清", "250": "超清", "400": "蓝光", "10000": "原画"}
            # key = list(ary.keys())
            # quality = list(ary.values())
            # qn = self.data(key, p['hd'])
            # show = self.data(quality, p['hd'])
            #
            # url = 'https://api.live.bilibili.com/room/v1/Room/playUrl?cid=%s&qn=%s&platform=web' % (vid, qn)
            qn = 1000

            for i in range(2):
                url = (
                    "https://api.live.bilibili.com/room/v1/Room/playUrl?cid=%s&qn=%s&platform=pc"
                    % (cid, qn)
                )
                html = self.curl(url)

                json = self.loads(html)
                assert json["code"] == 0, "data"
                quality_description = json["data"]["quality_description"][::-1]
                qns = [i["qn"] for i in quality_description]
                quality = [i["desc"] for i in quality_description]
                qn = self.data(qns, p["hd"])
                if qn == 1000:
                    break
            self.logging.debug(f"getLive: {html} \r\n")
            show = self.data(quality, p["hd"])
            flv = json["data"]["durl"][0]["url"]
            ext = playback = "flv"
            extra = {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                    "Referer": url,
                }
            }
        return self.compact()
