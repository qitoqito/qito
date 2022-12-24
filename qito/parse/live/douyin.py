#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : douyin.py
@Time    : 2022/9/11 下午4:03  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "抖音直播(DOUYIN)"
        self.require = [("quickjs", "Function", "fn"), "execjs", "importlib"]

    def query(self):
        p = self.params
        nonece = self.md5(self.timestamp)[:21]
        if self.hasurl(p["parse"]):
            if "live.douyin.com" in p["parse"]:
                html = self.curl(
                    {
                        "url": p["parse"],
                        "cookie": f"__ac_nonce={nonece}; __ac_signature={self.getSign(nonece)};",
                    }
                )
                vid = self.match(["room_id%3D(\d+)", "roomId%22%3A%22(\d+)"], html)
                # vid = self.match("\/(\d+)", p["parse"])
            else:
                url = self.curl({"url": p["parse"], "response": "location"})
                vid = self.match("\/(\d+)", url)

        else:
            vid = p["parse"]
        if p.get("query"):
            url = f"https://webcast.amemv.com/webcast/room/reflow/info/?verifyFp=&type_id=0&live_id=1&room_id={vid}&sec_user_id=&app_id=1128&msToken="
            for i in range(3):
                html = self.curl(
                    {
                        "url": url,
                        # 'from':'',
                    }
                )
                if html:
                    break
            data = self.jsonParse(html)
            try:
                data = self.jsonParse(html)
                room = self.haskey(data, "data.room")
                title = room["title"]
                image = room["cover"]["url_list"][0]
                anchor = room["owner"]["nickname"]
            except:
                pass
        return self.compact()

    def parse324(self):

        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        url = f"https://live.douyin.com/562472165700"

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        extra = {"headers": {"remove": 1}}

        url = f"https://webcast.amemv.com/webcast/room/reflow/info/?verifyFp=verify_lapkms6y_MR3gmPCh_HHZ8_43fo_9eHH_qTz7VcpSlEOM&type_id=0&live_id=1&room_id={vid}&sec_user_id=MS4wLjABAAAAKM11dO6WJPb4aIIMy5_1OhPMlGYQcpExYPPjmcr2kMg&app_id=1128&msToken=Eb6dqCrkr399cQX_ZdvGApjwqt7nRy1YBAD2ZHLzWMYdSQnTDBMCkOrBrq-0bmIjLu7NvC-fvwBX6qjeRzxRpETz0IHiHo_uJ7hA7QIlEmWBWEuljKEZ&X-Bogus=DFSzKIVOEWkANV9-SkKBqBjIVU1x"
        for i in range(6):
            html = self.curl(
                {
                    "url": url,
                    "cookie": "s_v_web_id=verify_lc1sgmon_fjzIuO03_pzK3_4ycj_8GJg_S7s0MwHiGR90",
                    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0",
                }
            )
            if html:
                break
        data = self.jsonParse(html)

        assert self.haskey(data, "data.room.status") == 2, "close"
        room = self.haskey(data, "data.room")
        title = room["title"]
        image = room["cover"]["url_list"][0]
        anchor = room["owner"]["nickname"]
        stream = ""

        if "fifa_skin" in self.haskey(room, "background.uri") and self.haskey(
            room, "episode_extra.match_room_info.match_data.match_id"
        ):
            roomId = self.haskey(
                room, "episode_extra.match_room_info.match_data.match_id"
            )
            html = self.curl(
                {
                    "url": f"https://live.douyin.com/fifaworldcup/{roomId}?enter_from_merge=web_share_link&enter_method=web_share_link"
                }
            )
            json = self.match(r'id="RENDER_DATA"\s*.+?>([^\<]+)', html)
            data = self.jsonParse(self.unquote(json))
            for k, v in data.items():
                a = self.jsonParse(v)
                if self.haskey(a, "roomRes"):
                    room2 = self.haskey(a, "roomRes.newRoomInfo.room")
                    stream = room2["stream_url"]
                    camera = self.haskey(
                        a, "roomRes.newRoomInfo.room.episode_extra.camera_infos"
                    )
                    if camera:
                        lang = []
                        eee = 1
                        for abc in camera:
                            lang.append(
                                {
                                    "url": f"https://live.douyin.com/fifaworldcup/{roomId}.html",
                                    "langcode": eee,
                                    "language": abc["title"],
                                }
                            )
                            eee += 1
                            if p.get("language") and (
                                p["language"] == abc["title"]
                                or p["language"] == str(eee)
                            ):
                                stream = abc["stream_info"]
                                language = abc["title"]
                        extra["language"] = lang

                    #

        if not stream:
            stream = room["stream_url"]

        try:
            streamData = self.loads(
                stream["live_core_sdk_data"]["pull_data"]["stream_data"]
            )["data"]

            qualitys = list(
                filter(
                    lambda x: x in streamData.keys(),
                    ["md", "ld", "sd", "hd", "uhd", "origin"],
                )
            )

            qualitys.sort(key=["md", "ld", "sd", "hd", "uhd", "origin"].index)
            show1 = self.data(qualitys, p["hd"])
            dict = {
                "md": "清晰",
                "ld": "标清",
                "sd": "高清",
                "hd": "超清",
                "uhd": "蓝光",
                "origin": "原画",
            }
            quality = [dict[i] for i in qualitys]
            show = dict[show1]
            main = streamData[show1]["main"]
            flv = main["flv"]
            m3u8 = main["hls"]
        except:
            resolution_name = stream["resolution_name"]
            flvUrl = stream["flv_pull_url"]
            qualitys = list(flvUrl.keys())[::-1]
            qualitys.sort(key=["SD1", "SD2", "HD1", "FULL_HD1", "ORIGION"].index)
            quality = [resolution_name[i] for i in qualitys]
            show = self.data(quality, p["hd"])
            resolution = self.data(qualitys, p["hd"])
            flv = flvUrl[resolution]
            m3u8 = stream["hls_pull_url_map"][resolution]

        ext = "flv"
        playback = "m3u8"

        return self.compact()

    def getSign(self, nonce):
        js = self.read(self.abspath + "/tool/javascript/douyin.sign.js")
        try:
            ctx = self.modules["execjs"].compile(js)
            sign = ctx.call("get_sign", nonce)
        except:
            sign = "_02B4Z6wo00f011STaVgAAIDC0rtM.EB46GtUom3AALaN5qKTFC4qCqg-fvNhWfGihyk9zChBBYW39vA2w5aTK14w48Hspeg-fFmRHS3.KMjtyBBTNms0LNJ-dqHdw-e6dy08s1j8YLPSsWx479"
        return sign
