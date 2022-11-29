#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : acfun.py
@Time    : 2022/11/29 下午1:59  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "()"

    def query(self):
        p = self.params
        if not p["parse"].startswith("http"):
            if self.match("aa(\d+)", p["parse"]):
                p["parse"] = "https://www.acfun.cn/bangumi/%s" % p["parse"]
            elif self.match("ac(\d+)", p["parse"]):
                p["parse"] = "https://www.acfun.cn/v/%s" % p["parse"]

        if p["parse"].startswith("http"):
            aid = self.match(["ac(\d+)", "ac=(\d+)"], p["parse"])

            if not aid:
                otype = "bangumi"
                html = self.curl({"url": p["parse"], "encoding": "utf8"})

                vid = self.match(['"videoId":(\d+),', '"danmakuId":(\d+)'], html)
                image = self.match('"image":"([^"]+)",', html)
                title = self.match('"episodeName":"(.*?)"', html)

            else:
                otype = "video"
                html = self.curl({"url": p["parse"], "encoding": "utf8"})
                vid = self.match('"currentVideoId":(\d+),', html)
                title = self.match(
                    ["\<title\s*\>(.*?)\s*-\s*AcFun", '"title":"([^"]+)",'], html
                )
                image = self.match('"url":"(https:\/\/imgs.+?)",', html)

        else:
            vid = p["parse"]

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        aid = self.haskey(p, "aid")
        m3u8 = ""
        if p["parse"].startswith("http"):
            content = self.curl(p["parse"])
            videoInfo = self.match(
                [
                    "window.pageInfo\s*=(?:\s*window.videoInfo\s*=\s*)*(?:\s*window.bangumiData\s*=)*\s*(.*);\s*",
                    "window.pageInfo\s*=(?:\s*window.videoInfo\s*=\s*)*(?:\s*window.bangumiData\s*=)*\s*([^;]+)",
                ],
                content,
            )
            self.logging.debug(f"videoInfo: {videoInfo} \r\n")
            try:
                videoJson = self.loads(videoInfo)
                title = videoJson["title"]

                duration = videoJson["currentVideoInfo"]["durationMillis"] / 1000
                image = self.haskey(videoJson, "coverCdnUrls.0.url")

                try:
                    representation = self.loads(
                        videoJson["currentVideoInfo"]["ksPlayJson"]
                    )["adaptationSet"][0]["representation"]
                except:
                    representation = self.loads(
                        videoJson["currentVideoInfo"]["ksPlayJson"]
                    )["adaptationSet"]["representation"]

                try:

                    m3u8List = self.column(representation, "url", "qualityLabel")
                except:

                    lists = self.column(representation, "url", "bandwidth")

                    def label(bandwidth):
                        if bandwidth > 3000000:
                            q = "1080p"
                        elif bandwidth > 1500000:
                            q = "超清"
                        elif bandwidth > 900000:
                            q = "高清"
                        elif bandwidth > 400000:
                            q = "标清"
                        else:
                            q = "自动"
                        return q

                    m3u8List = {label(int(i)): lists[i] for i in lists}
                #

                quality = list(m3u8List.keys())

                ary = [
                    "自动",
                    "360P",
                    "标清",
                    "540P",
                    "高清",
                    "720P",
                    "720P60",
                    "超清",
                    "1080P",
                    "1080P+",
                    "1080P60",
                    "2160P",
                    "2160P60",
                ]
                try:
                    quality.sort(key=ary.index)
                except:
                    quality = quality.reverse()

                show = self.data(quality, p["hd"])
                m3u8 = m3u8List[show]
                segs = [{"url": m3u8}]
                ext = "m3u8"
                playback = "m3u8"
            except:
                pass 
        return self.compact()
