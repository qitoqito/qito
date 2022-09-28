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
        assert self.haskey(data, "data.room.status") == 2, "close"
        room = self.haskey(data, "data.room")
        title = room["title"]
        image = room["cover"]["url_list"][0]
        anchor = room["owner"]["nickname"]
        stream = room["stream_url"]
        resolution_name = stream["resolution_name"]
        flv_pull_url = stream["flv_pull_url"]
        qualitys = list(flv_pull_url.keys())[::-1]
        qualitys.sort(key=["SD1", "SD2", "HD1", "FULL_HD1", "ORIGION"].index)
        quality = [resolution_name[i] for i in qualitys]
        show = self.data(quality, p["hd"])
        resolution = self.data(qualitys, p["hd"])
        flv = flv_pull_url[resolution]
        m3u8 = stream["hls_pull_url_map"][resolution]
        ext = "flv"
        playback = "m3u8"
        return self.compact()
