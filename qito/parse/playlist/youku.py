#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : youku.py
@Time    : 2022/9/4 下午5:01  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "优酷剧集列表"

    def videoList(self, params):
        url = params["parse"]
        if url.startswith("http"):
            url = self.curl({"url": url, "response": "location"})
            vid = self.match("v_show/id_([^\.]+)", url)
        else:
            vid = url
        if vid:
            ccode = "0524"
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
                }
            )
            json = self.jsonParse(html)

            serial = self.haskey(json, "data.show.title")
            cover = self.haskey(json, "data.show.encodeid")
        if cover:
            s = self.curl(
            {
                "url": f"https://search.youku.com/api/search?appScene=show_episode&showIds={cover}&appCaller=h5"
            }
        )
            data = self.loads(s)
            playlist = self.column(data["serisesList"], "videoId")
        return {
            "data": playlist,
            "category": "video",
            "type": "youku",
            "serial": serial,
        }
