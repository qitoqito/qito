#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : youku.py
@Time    : 2021/10/19 下午7:10  
"""
import template


class Main(template.Template):
    def __init__(self):
        super(Main, self).__init__()
        self.title = "优酷(YOUKU)"

    def query(self):

        p = self.params
        if self.hasurl(p["parse"]):
            if "v_nextstage" not in p["parse"]:
                url = p["parse"]
            else:
                url = self.curl({"url": p["parse"], "response": "location"})
            vid = self.match(["id_([^\"'\.]+)\.", "sid\/([^\"']+)\/v.swf"], url)
            if vid.isdigit():
                vid = "X" + self.b64encode(str(4 * int(vid)))
        elif p["parse"].isdigit():
            vid = "X" + self.b64encode(str(4 * int(p["parse"])))
        else:
            vid = p["parse"]

        if p.get("query"):
            ccode = p.get("ccode", "0524")
            try:
                utid = self.curl(
                    {
                        "url": "http://log.mmstat.com/eg.js",
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0",
                            "Referer": "https://g.alicdn.com/alilog/oneplus/blk.html",
                        },
                        "response": "cookie",
                    },
                )["cna"]
            except:
                utid = "qyiUGD8MHWkCARudQQu7gaFM"
            params = {
                "vid": vid,
                "ccode": ccode,
                "client_ip": "192.168.1.1",
                "utid": utid,
                "client_ts": self.timestamp,
                "ckey": "115#1dCil11O1TaNcv6zGfND1Cso311GLyAi1/2Wsi/gdl1it86z19WZy56NE8P1IvvCtU/8yPZQi/WJ1aU4AWNcaLBfOZPQOSAPetT4yWZQgbvJhEz4vBN4+5yAurrQ/jfyet/4yWZQiQ+ghZz8OWNcaTpjurPdvOoNPKxRLp+2i7lL1FGYdPYMTT9cxCNRlGg0kxHucjHqect+1pQNBWMKLRoQD1ZDrSxQ+F6RY5gk0Bmywzgc8WLIgwd2piFbn1q6EWcfZc1Wg5bS6ancr86G4xLB9BSOV9noSrKFv5r4lzKO8RWkfVdXHmIATO1SsV5RtVQCAcMDKsROmJbQy8ozjXN+EK4p3CZSxTcnDRaAr/TrOZSCIXoXN8k3EkUCh1QV3dpRqjRzsM4qBS36s8JOXl9VM4+QJ0+DLRJUKP3J11CNo0odneVsS52H58CYeEqN",
            }

            html = self.curl(
                {
                    "url": "https://ups.youku.com/ups/get.json",
                    "params": params,
                    "referer": f"http://v.youku.com/v_show/id_{vid}.html",
                }
            )
            self.logging.debug(f"getInfo: {html} \r\n")
            data = self.loads(html)
            if "video" in data["data"]:
                pay = data["data"]["show"]["pay"]
                title = data["data"]["video"]["title"]

                image = data["data"]["video"]["logo"]
                duration = data["data"]["video"]["seconds"]

        return self.compact()

    def parse(self):

        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        timestamp = self.timestamp
        utid = ""
        if self.get("cookie"):
            utid = self.match("cna=([^;]+);", self.cookie)
        else:
            try:
                utid = self.curl(
                    {
                        "url": "http://log.mmstat.com/eg.js",
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0",
                            "Referer": "https://g.alicdn.com/alilog/oneplus/blk.html",
                        },
                        "response": "cookie",
                    },
                )["cna"]
            except:
                pass

        if not utid:
            utid = "qyiUGD8MHWkCARudQQu7gaFM"
        ccode = p.get("ccode") or "0524"

        params = {
            "vid": vid,
            "ccode": ccode,
            "client_ip": "192.168.1.1",
            "utid": utid,
            "client_ts": timestamp,
            "ckey": "099#4a8781f72f29ab250a484c1bf330aa99#82",
            "ptoken": "",
            "stoken": "",
            # "extag": "EXT-X-PRIVINF",
            "needbf": "1",
            "encryptR_client": "MzujwsgiTomoWckrTxQvuw==",
            "key_index": "key01",
            "app_ver": "8.0.5.9181",
            "os_ver": "win_6.1-64",
            "pid": "ywebapp",
            "mac": "94de805741f",
            "rid": "7",
            # "drm_type": "3",
            # "h265": "1",
            "master_m3u8": "1",
            "play_ability": "4352",
            "preferClarity": "99",
            "wintype": "interior",
            "p": "1",
            "appname": "iku",
            "avs": "8.0.5.9181",
            "bt": "pc",
            "aw": "a",
            "site": "1",
            "fu": "0",
            "vs": "1.0",
            "os": "win_6.1-64",
            "rst": "mp4",
            "dq": "intelligent",
            "guid": "100000000000000000005F6601C594DE805741F0",
        }
        html = self.curl(
            {"url": "https://ups.youku.com/ups/get.json", "params": params}
        )
        self.logging.debug(f"getVideo: {html} \r\n")
        json = self.loads(html.replace("http:", "https:"))

        assert "error" not in json, "data"
        # pay = json["data"].get("show").get("pay")
        pay = self.haskey(json, "data.show.pay")
        title = json["data"]["video"]["title"]
        image = json["data"]["video"]["logo"]
        duration = json["data"]["video"]["seconds"]
        lang = []
        if self.haskey(json, "data.dvd.audiolang"):
            language = []
            for i in json["data"]["dvd"]["audiolang"]:

                language.append(
                    {
                        "url": f"https://v.youku.com/v_show/id_{i['vid']}.html",
                        "langcode": i["langcode"],
                        "language": i["lang"],
                    }
                )
                if i["langcode"] == self.params.get("language") and title:
                    title = "{}[{}]".format(title, i["lang"])
            extra = {"language": language}
            lang = self.column(json["data"]["dvd"]["audiolang"], "langcode")

        ary = [
            "3gphd",
            "3gphdv2",
            "flvhd",
            "flvhdv2",
            "mp4sd",
            "mp4sdv2",
            "mp4hd",
            "hd",
            "mp4hdv2",
            "mp4hd2",
            "hd2",
            "mp4hd2v2",
            "mp4hd3",
            "mp4hd3v2",
        ]
        lang = lang or ["ja", "en", "in", "kr", "yue", "guoyu", "default"]
        langDict = {}
        for lk in json["data"]["stream"]:
            if lk["audio_lang"] in langDict:
                langDict[lk["audio_lang"]].append(lk)
            else:
                langDict[lk["audio_lang"]] = []

        encodeid = vid.replace("=", "")
        vidStream = []

        for k, v in langDict.items():
            if encodeid in self.dumps(vid):
                vidStream = v
                break

        # 获取 stream[lang] 数据
        if self.params.get("language") in langDict:
            stream = langDict[self.params["language"]]
        elif vidStream:
            stream = vidStream
        elif "default" in langDict:
            stream = langDict["default"]
        else:
            stream = self.data(langDict, p["hd"])

        streamList = []
        quality = []
        for kn in ary:
            for kb in stream:
                if kb["stream_type"] == kn:
                    streamList.append(kb)
                    quality.append(kb["stream_type"])
        show = self.data(quality, p["hd"])

        fileDict = self.data(streamList, p["hd"])
        segs = []
        for v in fileDict["segs"]:
            if "cdn_url" in v:
                segs.append(
                    {
                        "url": v["cdn_url"],
                        "duration": v["total_milliseconds_video"] / 1000,
                        "size": int(v["size"]),
                    }
                )

        m3u8 = fileDict["m3u8_url"]
        if len(segs) == 0 and m3u8:
            segs = [{"url": m3u8}]
            ext = "m3u8"
        if segs[0]["url"].find(".flv") > 0:
            ext = "flv"
        playback = "m3u8"

        return self.compact()
