#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : douyu.py
@Time    : 2022/11/30 上午10:32  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "斗鱼视频(DOUYU)"
        self.require = [("quickjs", "Function", "fn"), "execjs"]

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            aid = self.match("\/show\/(\w+)", p["parse"])
        else:
            aid = p["parse"]
        html = self.curl(f"https://v.douyu.com/show/{aid}")
        data = self.match("\$DATA\s*=\s*([^<]+?);", html)
        self.logging.debug(f"roomData: {data} \r\n")
        json = self.jsonParse(data)
        if "ROOM" in json:
            title = json["ROOM"]["name"]
            image = json["ROOM"]["pic"]
            duration = json["ROOM"]["duration"]
            vid = json["ROOM"]["point_id"]

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        aid = p["aid"]
        timestamp = self.time
        crypto = self.read(f"{self.abspath}/tool/javascript/crypto-js.min.js")
        url = f"https://www.douyu.com/swf_api/homeH5Enc?rids={vid}"
        getEnc = self.curl(url)
        json = self.loads(getEnc)
        assert json.get("error") == 0, "homeH5enc"
        jsEnc = json["data"][f"room{vid}"]
        evalString = """
                              //eval(Ee); 
                              var newString = "'" + Ee + "';";
                              var evalString = eval(newString);
                              evalString = evalString.replace(/(.*oog\(.*)/, "$1oog['test'] = function(a) { return 1; }");
                              eval(evalString);
            """
        jsDom = jsEnc.replace("eval(Ee);", evalString)
        dom = "let window = {},document  = {};"
        try:
            f = self.modules["fn"]("ub98484234", f"{crypto};{dom};{jsDom};")
            ub98484234 = f(vid, self.md5(timestamp), timestamp)
        except:
            ctx = self.modules["execjs"].compile(f"{crypto};{dom};{jsDom};")
            ub98484234 = ctx.call("ub98484234", vid, self.md5(timestamp), timestamp)

        self.logging.debug(f"ub98484234: {ub98484234} \r\n")
        postData = self.qsl(f"{ub98484234}&vid={aid}")

        getStream = self.curl(
            "https://v.douyu.com/api/stream/getStreamUrl",
            {"method": "post", "form": postData},
        )
        self.logging.debug(f"getStream: {getStream} \r\n")
        data = self.loads(getStream)

        assert data.get("error") == 0, "data"
        dicts = {"normal": "高清", "high": "超清", "super": "原画"}
        video = data["data"]["thumb_video"]
        s = self.sort([k for k, v in video.items() if v], dicts.keys())
        quality = [dicts[i] for i in s]
        show = self.data(quality, p["hd"])
        m3u8 = video[self.data(s, p["hd"])]["url"]
        playback = ext = "m3u8"
        return self.compact()
