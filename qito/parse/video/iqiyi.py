#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : iqiyi.py
@Time    : 2022/9/26 下午7:26  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "爱奇艺视频(IQIYI)"

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            html = self.curl(p["parse"])
            vid = self.match(
                [
                    'data-player-videoid="(\w+)"',
                    '"vid":"(\w+)"',
                    "param['vid'] = \"(\w+)\"",
                ],
                html,
            )
            cid = self.match(
                [
                    "tvId:(\d+)",
                    'data-player-tvid="(\d+)"',
                    "param['tvid'] = \"(\d+)\"",
                    '"tvid":"(\d+)"',
                    '"tvId":(\d+)',
                ],
                html,
            )
            pay = 1 if self.match('"payMark":(\d+)', html) else 0
        else:
            string = self.replace(["|", ";", ",", "-", "_", ":"], "-", p["parse"])
            spl = string.split("-")
            if len(spl) == 2:
                vid = spl[0] if len(spl[0]) == 32 else spl[1]
                cid = spl[1] if len(spl[0]) == 32 else spl[0]
            elif len(spl[0]) == 32:
                cid = ""
            else:
                cid = spl[0]
        assert cid, "tvid"
        getBaseInfo = self.curl(
            {
                "url": f"https://mac.video.iqiyi.com/video/video/baseinfo/{cid}?src=01082001010000000000",
                "decoding": "utf8",
            },
        )
        self.logging.debug(f"baseInfo: {getBaseInfo} \r\n")
        baseJson = self.loads(getBaseInfo)

        if baseJson.get("data"):
            vid = baseJson["data"]["vid"]
            image = baseJson["data"]["imageUrl"].replace(".jpg", "_480_270.jpg")
            title = baseJson["data"]["name"]
            if "subtitle" in baseJson["data"]:
                title += " " + baseJson["data"]["subtitle"]
            pay = "1" if baseJson["data"]["payMark"] else ""
            duration = self.seconds(baseJson["data"]["duration"])
        else:
            getVideoInfo = self.curl(
                f"https://pcw-api.iqiyi.com/video/video/playervideoinfo?tvid={cid}"
            )
            self.logging.debug(f"videoInfo: {getVideoInfo} \r\n")
            data = self.loads(getVideoInfo)
            assert data.get("data"), "data"
            if not vid:
                source = data["data"]["vu"]
                html = self.curl(source)
                vid = self.match(
                    [
                        'data-player-videoid="(\w+)"',
                        '"vid":"(\w+)"',
                        "param['vid'] = \"(\w+)\"",
                    ],
                    html,
                )
                pay = 1 if self.match('"payMark":(\d+)', html) else 0
            image = data["data"]["vpic"]
            title = data["data"]["vn"]
            if "subt" in data["data"]:
                title += " " + data["data"]["subt"]

        tm = self.timestamp * 1000
        rand = self.md5(tm)
        key = "d5fb4bd9d50c4be6948c97edd7254b0e"
        src = "76f90cbd92f94a2e925d83e8ccd22cb7"
        sc = self.md5(f"{tm}{key}{vid}")
        url = f"https://cache.m.iqiyi.com/tmts/{cid}/{vid}/?sc={sc}&src={src}&t={tm}"
        tmts = self.curl(url)
        tmtsJson = self.loads(tmts)

        if self.haskey(tmtsJson, "data.ctl.configs"):
            configs = tmtsJson["data"]["ctl"]["configs"]
            vids = configs.get("19") or configs.get("10")
            if vids:
                vid = vids["vid"]
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        cid = p["cid"]
        if self.haskey(p, "context.tmts"):
            tmts = p["context"]["tmts"]
        else:
            tm = self.timestamp * 1000
            rand = self.md5(tm)
            key = "d5fb4bd9d50c4be6948c97edd7254b0e"
            src = "76f90cbd92f94a2e925d83e8ccd22cb7"
            sc = self.md5(f"{tm}{key}{vid}")
            url = (
                f"https://cache.m.iqiyi.com/tmts/{cid}/{vid}/?sc={sc}&src={src}&t={tm}"
            )
            tmts = self.curl(url)
        self.logging.debug(f"getTmts: {tmts} \r\n")
        json=self.jsonParse(tmts)
        assert json.get("code") == "A00000", "data"
        dicts = {"h265": {}, "h264": {}}
        for i in json["data"]["vidl"]:
            types = "h265" if i.get("fileFormat") == "H265" else "h264"
            dicts[types][i["vd"]] = i
        if p.get("encoder") == "h265":
            lists = dicts["h265"]
        else:

            lists = dicts["h264"]

        lists[json["data"]["vd"]] = {
            "screenSize": json["data"]["screenSize"],
            "m3u": json["data"]["m3u"],
        }
        vs = {int(v["screenSize"].split("x")[0]): k for k, v in lists.items()}

        vsize = sorted(vs.keys())
        quality = [str(vs[i]) for i in vsize]
        show = self.data(quality, p["hd"])
        data = lists[int(show)]
        m3u8 = data["m3u"]
        playback = ext = "m3u8"
        return self.compact()
