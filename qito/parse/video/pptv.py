#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : pptv.py
@Time    : 2022/10/10 下午8:36  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "PP视频(PPTV)"

    def query(self):
        p = self.params
        if p["parse"].isdigit():
            vid = p["parse"]
        elif p["parse"].isalnum():
            url = f"http://v.pptv.com/show/{p['parse']}.html"
        else:
            url = p["parse"]
        if url:
            tvid = self.match("show\/(\w+)", url)
            html = self.curl(url)
            # vid = self.match(['video_id="(\d+)"', '"id"\s*:\s*(\d+)', "id=(\d+)"], html)

            vid = self.match('"(?:c|ps)id":"?(\d+)', html)
            title = self.match(
                ['<h3 class="tv-name">(.*?)<\/h3>', '"title"\s*:\s*"(.*?)"'], html
            )

            if not vid:
                vid = self.match("\/vod\/(\d+)\/", p["parse"])

        assert vid, "vid"

        if p.get("query"):
            webParams = {
                "platform": "atv",
                "canal": "9122",
                "ver": "3",
                "lang": "zh_CN",
                "type": "ppbox.launcher.vip",
                "gslbversion": "2",
                "userLevel": "0",
                "open": "0",
                "content": "need_drag",
                "zone": "8",
                "pid": "5701",
                "vvid": "a7c64007-b0a8-662c-1853-a29913676ca2",
                "version": "4",
                "username": "",
                "ppi": "302c3630",
                "salt": "pv",
                "segment": "a72e242e_a72e2676_1488784198",
                "o": "0",
                "sl": "1",
                "referrer": "",
                "pageUrl": "http://v.pptv.com/show/IZlEw10VDEqtK5M.html?rcc_src=B3",
                "duration": "1242",
                "r": "1488786625410",
                "scver": "1ebf7a076b88f0bc4efbdde483a91d104-2c05-1516711145&bppcataid=94",
            }
            webUrl = f"https://web-play.pptv.com/webplay3-0-{vid}.xml"
            content = self.curl(webUrl, {"params": webParams})
            self.logging.debug(f"getXmlInfo: {content} \r\n")

            title = self.match('nm="(.*?)"\s*', content)
            duration = self.match('dur="(\d+)"', content)

            rids = self.matchAll('rid="([^"\']+).mp4"\s*bitrate', content)
            fts = self.matchAll('ft="(\d+)"', content)

            if fts and fts[0] != "0":
                rids.reverse()
            context = {"rids": rids}
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        image = f"http://s1.pplive.cn/v/cap/{vid}/w640.jpg"
        wtype = "mhpptv"
        webParams = [
            {
                "platform": "atv",
                "canal": "9122",
                "ver": "3",
                "lang": "zh_CN",
                "type": wtype,
                "gslbversion": "2",
                "userLevel": "0",
                "open": "0",
                "content": "need_drag",
                "zone": "8",
                "pid": "5701",
                "vvid": "a7c64007-b0a8-662c-1853-a29913676ca2",
                "version": "4",
                "username": "",
                "ppi": "302c3630",
                "salt": "pv",
                "segment": "a72e242e_a72e2676_1488784198",
                "o": "0",
                "sl": "1",
                "referrer": "",
                "pageUrl": "http://v.pptv.com/show/IZlEw10VDEqtK5M.html?rcc_src=B3",
                "duration": "1242",
                "r": "1488786625410",
                "scver": "1ebf7a076b88f0bc4efbdde483a91d104-2c05-1516711145&bppcataid=94",
                "https": "true",
            },
            {
                "zone": "8",
                "pid": "5701",
                "vvid": "8302d118-c059-7770-eb8d-23578916ca2d",
                "version": "4",
                "username": "",
                "ppi": "302c3333",
                "type": wtype,
                "pageUrl": "http://v.pptv.com/show/tVZZ1j6kFFK1M5s.html",
                "o": "0",
                "referrer": "",
                "kk": "75247faf091ef78c60173239f4b0e8ed-5fe5-5a674f72",
                "sl": "1",
                "duration": "215",
                "r": "1516716394945",
                "scver": "1",
                "appplt": "flp",
                "appid": "pptv.flashplayer.vod",
                "appver": "3.4.3.3",
                "nddp": "1",
                "https": "true",
            },
        ]
        for i in webParams:
            url = f"https://web-play.pptv.com/webplay3-0-{vid}.xml"
            html = self.curl({"url": url, "params": i})
            if ".mp4" in html:
                break
        self.logging.debug(f"getXmlSource: {html} \r\n")
        # 如果出现message,可能是vid错误或者视频删除/隐藏
        message = self.match('code="(\d+)"\s*message="([^"]+)"', html)

        if message and message[0] != "301":
            raise NotImplementedError("hide")

        rids = self.matchAll('rid="([^"]+).mp4"\s*bitrate', html)
        fts = self.matchAll('ft="(\d+)"', html)

        if fts and fts[0] != "0":
            rids.reverse()

        ary = (
            ["流畅", "标清", "高清", "超清", "蓝光", "原画"]
            if len(rids) > 4
            else ["流畅", "高清", "超清", "蓝光"]
        )

        quality = ary[: len(rids)]
        rid = self.data(rids, p["hd"])
        show = self.data(quality, p["hd"])
        dt_lists = self.matchAll("<dt(.*?)<\/dt>", html, "S")
        if fts and fts[0] != "0":
            dt_lists.reverse()
        dt = self.data(dt_lists, p["hd"])

        # 获取资源的rid sh key相关信息
        info = self.matchAll(
            'rid="([^"]+)".*?<sh>([^\<]+)<\/sh>.*?<key.*?>([^\<]+)<\/key>', dt, "S"
        )
        match = self.matchAll(
            "<(\w+)[^\>]*>([^\<]+)<\/\w+>", dt.replace("<ip_serviceid/>", "")
        )
        ch = ""  # rid包含汉字

        if match:
            dicts = dict(match)
            sh = dicts["sh"]
            filename = self.match('rid="([^"]+)"', dt)
            key = dicts["key"]
        elif len(info) > 0:
            sh = info[0][1]
            key = info[0][2]
            filename = info[0][0]
        else:
            info = self.match("<sh>([^\<]+)<\/sh>.*?<key.*?>([^\<]+)<\/key>", dt, "S")
            sh = info[0]
            key = info[1]
            filename = rid + ".mp4"
            ch = "1"

        title = self.match('nm="(.*?)"\s*', html)

        duration = int(self.match('dur="(\d+)"', html))
        m3u8 = "https://{}/{}?type={}&k={}".format(
            sh, filename.replace(".mp4", ".m3u8"), wtype, key
        )
        ext = playback = "m3u8"
        try:
            size = int(
                self.data(self.matchAll('<dragdata.*?fs="([^"]+)', html), p["hd"])
            )
        except:
            pass

        return self.compact()
