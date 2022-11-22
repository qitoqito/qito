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

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):

            if "live.douyin.com" in p["parse"]:
                html = self.curl(
                    {
                        "url": p["parse"],
                        "cookie": "__ac_nonce=0731e9abc003e9f166f7;  ",
                    }
                )
                vid = self.match(["room_id%3D(\d+)", "roomId%22%3A%22(\d+)"], html)

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

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]

        # url = f"https://live.douyin.com/{vid}"
        #
        # html = self.curl(
        #     {
        #         "url": url,
        #         "cookie": "__ac_nonce=0731e9abc003e9f166f7;  ",
        #     }
        # )
        # data = self.match(
        #     [
        #         'id="RENDER_DATA" type="application/json">([^\<]+)</script>',
        #         "__INIT_PROPS__\s*=\s*([^\<]+)</script>",
        #     ],
        #     html,
        # )
        # json=self.jsonParse(self.urlParse.unquote(data))
        # # print(json)
        # print(self.haskey(json,'app.initialState.roomStore.roomInfo.room'))
        url = f"https://webcast.amemv.com/webcast/room/reflow/info/?verifyFp=&type_id=0&live_id=1&room_id={vid}&sec_user_id=&app_id=1128&msToken=yMsIx7vWwDBG84R8-&X-Bogus=DFSzKIVOZriANtK4SQY19BjIVUIJ"
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

        if not stream:
            stream = room["stream_url"]

        try:
            streamData = self.loads(
                stream["live_core_sdk_data"]["pull_data"]["stream_data"]
            )["data"]
            qualitys = list(streamData.keys())
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
        extra = {"headers": {"remove": 1}}

        return self.compact()
