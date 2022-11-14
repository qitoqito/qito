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
        tvid = p["cid"]
        timestamp = self.timestamp
        t = timestamp * 1000
        try:
            if self.haskey(p, "context.tmts"):
                tmts = p["context"]["tmts"]
            else:
                tm = self.timestamp * 1000
                rand = self.md5(tm)
                key = "d5fb4bd9d50c4be6948c97edd7254b0e"
                src = "76f90cbd92f94a2e925d83e8ccd22cb7"
                sc = self.md5(f"{tm}{key}{vid}")
                url = f"https://cache.m.iqiyi.com/tmts/{tvid}/{vid}/?sc={sc}&src={src}&t={tm}"
                tmts = self.curl(url)

            self.logging.debug(f"getTmts: {tmts} \r\n")
            json = self.jsonParse(tmts)
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
        except:
            src = f"/vps?tvid={tvid}&vid={vid}&v=0&src=01012001010000000000&t={t}&k_tag=1&k_uid={self.md5(t)}&rs=1"

            vf = self.md5x(src)
            url = f"http://cache.video.qiyi.com/vps?tvid=385274600&vid=385274600&v=0&qypid=385274600_12&src=01012001010000000000&t=1668247341473&k_tag=1&k_uid=uxjgywyzvub06btmsonm9olkno2otqm7&rs=1&vf=1aef6bada250012cdf8967cb9f35e932"
            html = self.curl(url)
            self.logging.debug(f"getVps: {html} \r\n")
            json = self.loads(html)
            assert json["code"] == "A00000", "data"
            # for i in (json['data']['vp']['tkl'][0]['vs']):
            #     print(i)
            column = self.column(json["data"]["vp"]["tkl"][0]["vs"], "", "bid")
            vsize = self.column(json["data"]["vp"]["tkl"][0]["vs"], "bid", "vsize")

            quality = [str(vsize[k]) for k in sorted(vsize)]

            show = self.data(quality, p["hd"])
            data = column[int(show)]
            size = data["vsize"]
            du = json["data"]["vp"]["du"]
            segs = [{"url": f"{du}{i['l']}&pv=0.2"} for i in data["fs"]]

            ext = "f4v"
            try:
                bids = [100, 200, 300, 500, 600]
                iqiyiBid = self.data(bids, p["hd"])
                iqiyiBid = 620

                dashParams = {
                    "tvid": tvid,
                    "bid": iqiyiBid,
                    "vid": vid,
                    "src": "01080031010000000000",
                    "vt": "0",
                    "rs": "1",
                    "uid": "",
                    # "ori": "pcw",
                    "ps": "1",
                    "k_uid": "c55d485ee178762fe5e2135b9bddf52d",
                    "pt": "0",
                    "d": "0",
                    "s": "",
                    "lid": "",
                    "cf": "",
                    "ct": "",
                    "authKey": "",
                    "k_tag": "-1",
                    "ost": "undefined",
                    "ppt": "undefined",
                    "dfp": "",
                    "locale": "zh_cn",
                    "prio": '{"ff":"m3u8","code":2}',
                    "pck": "",
                    "k_err_retries": "0",
                    "up": "",
                    "qd_v": "2",
                    "tm": self.timestamp,
                    "qdy": "i",
                    "qds": "0",
                    "k_ft1": "755914244096",
                    # "k_ft4": "-1",
                    "k_ft5": "1",
                    "bop": '{"version":"10.0","dfp":""}',
                    "ut": "1",
                }
                dash = f"/dash?{self.urlencode(dashParams)}"

                vf = self.cmd5x(dash)

                url = f"http://cache.video.iqiyi.com{dash}&vf={vf}"

                html = self.curl(url)

                self.logging.debug(f"getVideo: {html} \r\n")
                data = self.loads(html)
                fmtDict = {"f4v": [], "ts": [], "265ts": [], "dash": []}
                for i in data["data"]["program"]["video"]:
                    if i["bid"] not in fmtDict[i["ff"]]:
                        fmtDict[i["ff"]].append(i["bid"])

                if fmtDict["265ts"]:
                    ff = fmtDict["265ts"]
                    fmt = "h265"
                    lists = {
                        "极速[H265]": "100",
                        "流畅[H265]": "200",
                        "高清[H265]": "300",
                        "720P[H265]": "500",
                        "1080P[H265]": "600",
                        "4K[H265]": "800",
                    }
                elif fmtDict["f4v"]:
                    ff = fmtDict["f4v"]
                    fmt = "f4v"
                else:
                    ff = fmtDict["ts"]
                    fmt = "h264"

                ff.sort()
                if p.get("encoder") == "h265":
                    lists = {
                        100: "H265_极速",
                        200: "H265_流畅",
                        300: "H265_高清",
                        500: "H265_720P",
                        600: "H265_1080P",
                        620: "H265_1080P50",
                        800: "H265_4k",
                    }

                elif p.get("encoder") == "dolby":
                    lists = {
                        100: "杜比_极速",
                        200: "杜比_流畅",
                        300: "杜比_高清",
                        500: "杜比_720P",
                        600: "杜比_1080P",
                        610: "杜比_1080P50",
                    }
                else:
                    lists = {
                        100: "极速",
                        200: "流畅",
                        300: "高清",
                        500: "720P",
                        600: "1080P",
                        610: "1080P50",
                    }

                assert "msg" not in data, "rule"
                assert "program" in data["data"], "data"
                quality = [lists[i] for i in ff]
                show = self.data(quality, p["hd"])
                info = tuple(
                    [i["url"], i["duration"], i["vsize"]]
                    for i in data["data"]["program"]["video"]
                    if "url" in i and "http" in i["url"]
                )
                m3u8, duration, size123 = info[0]

                playback = "m3u8"

                # ext = "hls"
                # extra = {"replace": ["http:", "https:"]}
                extra = {
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0",
                        "Accept": "*/*",
                        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                        "Referer": "https://www.iqiyi.com/v_19rr5aq6z8.html",
                        "Origin": "https://www.iqiyi.com",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                    }
                }
            except:
                pass

            # 获取m3u8

        return self.compact()


    def md5x(self, dash):
        return self.md5(dash + "1j2k2k3l3l4m4m5n5n6o6o7p7p8q8q9r")

    def cmd5x(self, dash):

        js = self.read(self.abspath + "/tool/javascript/iqiyi.cmd5x.js")

        try:
            from quickjs import Function

            f = Function("cmd5x", js)
            vf = f(dash)

        except:
            import execjs

            ctx = execjs.compile(js)
            vf = ctx.call("cmd5x", dash)
        return vf

    def temp(self, vid):
        path = f"{self.abspath}/temp/{vid}.m3u8"
        return path
