#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : douyu.py
@Time    : 2022/11/30 上午12:24  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "斗鱼直播(DOUYU)"
        self.require = [("quickjs", "Function", "fn"), "execjs", "importlib"]

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            cid = self.match("\/(\d+)", p["parse"])
        else:
            cid = p["parse"]

        if cid:
            html = self.curl(
                {"url": f"https://www.douyu.com/{cid}", "encoding": "utf8"}
            )
        else:
            html = self.curl(p["parse"])
        vid = self.match(
            [
                "ROOM.room_id\s*=\s*(\d+)",
                "room_id\s*=\s*(\d+)",
                '"room_id.?":(\d+)',
                "data-onlineid=(\d+)",
            ],
            html,
        )
        title = self.match('Title-headlineH2">([^<]+)<', html)
        anchor = self.match('Title-anchorName" title="([^"]+)"', html)

        if not anchor or not title:
            url = f"https://open.douyucdn.cn/api/RoomApi/room/{vid}"
            content = self.curl({"url": url, "encoding": "utf8"})

            self.logging.debug(f"getInfo: {content} \r\n")
            json = self.loads(content)

            if json["error"] == 0:
                anchor = json["data"]["owner_name"]
                title = json["data"]["room_name"].replace("\t", "")
                image = json["data"]["room_thumb"]

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        timestamp = str(self.time)

        crypto = self.read(f"{self.abspath}/tool/javascript/crypto-js.min.js")
        url = f"https://www.douyu.com/swf_api/homeH5Enc?rids={vid}"
        get_enc = self.curl(url)
        json = self.loads(get_enc)
        assert json.get("error") == 0, "homeH5enc"
        jsEnc = json["data"][f"room{vid}"]
        replaceString = """ 
                              var newString = "'" + Ee + "';";
                              var evalString = eval(newString);
                              evalString = evalString.replace(/(.*oog\(.*)/, "$1oog['test'] = function(a) { return 1; }");
                              eval(evalString);
            """
        jsDom = jsEnc.replace("eval(Ee);", replaceString)

        dom = "let window = {},document  = {};"

        try:
            f = self.modules["fn"]("ub98484234", f"{crypto};{dom};{jsDom};")
            ub98484234 = f(vid, self.md5(timestamp), timestamp)

        except:
            ctx = self.modules["execjs"].compile(f"{crypto};{dom};{jsDom};")
            ub98484234 = ctx.call("ub98484234", vid, self.md5(timestamp), timestamp)

        self.logging.debug(f"ub98484234: {ub98484234} \r\n")
        h5Url = f"https://www.douyu.com/lapi/live/getH5Play/{vid}"
        rateTemp = 0
        postData = self.qsl(
            f"{ub98484234}&cdn=&rate={rateTemp}&ver=Douyu_219042402&iar=1&ive=0"
        )

        source = self.curl(
            {
                "url": f"https://www.douyu.com/lapi/live/getH5Play/{vid}",
                "method": "post",
                "form": postData,
                "encoding": "utf8",
            }
        )
        self.logging.debug(f"getLive: {source} \r\n")
        playJson = self.loads(source)
        if playJson["error"] == 0:
            multirates = self.column(playJson["data"]["multirates"], "", "name")
            quality = list(multirates.keys())[::-1]
            show = self.data(quality, p["hd"])
            rate = multirates[show]["rate"]
            if rateTemp != rate:
                postData = self.qsl(
                    f"{ub98484234}&cdn=&rate={rateTemp}&ver=Douyu_219042402&iar=1&ive=0"
                )

                request = {"method": "post", "form": postData, "encoding": "utf8"}
                source = self.curl(h5Url, request)
                playJson = self.loads(source)

            flv = f"{playJson['data']['rtmp_url']}/{playJson['data']['rtmp_live']}"
            ext = playback = "flv"

            # 获取M3U8
            rateUrl = "https://m.douyu.com/api/room/ratestream"
            rateDict = self.qsl(f"{ub98484234}&ver=219032101&rid={vid}&rate={rate}")

            request = {"method": "post", "form": rateDict, "decoding": "utf8"}

            rateSource = self.curl(rateUrl, request)
            self.logging.debug(f"ratestream: {rateSource} \r\n")
            streamDict = self.loads(rateSource)
            if streamDict["code"] == 0:
                m3u8 = streamDict["data"]["url"]
                playback = "m3u8"

        elif playJson["error"] == -5:
            vod_url = f"https://www.douyu.com/swf_api/getRoomCloseVod/{vid}"

            get_vod = self.curl(vod_url)
            self.logging.debug(f"getRoomCloseVod: {get_vod} \r\n")
            roomJson = self.loads(get_vod)
            info = roomJson.get("lastVidInfo")

            if info:
                self.params["category"] = "video"
                vid = info["vid"]
                aid = self.match("show\/(\w+)", info["url"])
                imp = self.modules["importlib"].import_module("parse.video.douyu")
                a = imp.Main()
                a.modules = self.modules
                a.params = {"vid": vid, "hd": p["hd"], "aid": aid}
                return a.parse()
        extra = {"remove": 1}
        return self.compact()
