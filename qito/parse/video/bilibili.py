#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : bilibili.py
@Time    : 2022/10/7 下午1:10  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "哔哩哔哩视频(BILIBILI)"

    def query(self):
        p = self.params
        aid = ""
        page = 1
        vid=""
        if p["parse"].startswith("av"):
            p["parse"] = "https://www.bilibili.com/video/%s" % p["parse"]
        if p["parse"].startswith("BV"):
            p["parse"] = "https://www.bilibili.com/video/%s" % p["parse"]
        elif p["parse"].startswith("ep"):
            p["parse"] = "https://www.bilibili.com/bangumi/play/%s" % p["parse"]
        if p["parse"].startswith("http"):
            url = self.curl({"url": p["parse"], "response": "location"})
            if "bangumi" in url:

                html = self.curl(
                    {
                        "url": url,
                        "useragent": "ios",
                        "encode": "gzip",
                        "encoding": "utf8",
                    }
                )
                vid = self.match(
                    [
                        # "(\d+)-\d+-\d+.m4s",
                        "\d+\/(\d+)-.+?\.(?:mp4|flv)",
                        # '"cid":(\d+)',
                        "cid=(\d+)",
                        'cid="(\d+)',
                    ],
                    html,
                )
                if vid == "0":
                    vid = ""
                if not vid:
                    loadded = self.match("window.__INITIAL_STATE__=(\{.*?\});", html)
                    if loadded:
                        loadJson = self.loads(loadded)
                        vid = loadJson["epInfo"]["cid"]
                        if vid == -1:
                            vid = loadJson["epList"][0]["cid"]

                title = self.match(
                    [
                        '"share_copy"\s*:\s*"([^"]+)"',
                        '<h1 title="(.*?)">',
                        '"h1Title":"(.*?)"',
                        '"title":"(.*?)"',
                    ],
                    html,
                ).replace("\u002F", "/")
                image = self.match('property="og:image" content="([^"]+)"', html)
                if image:
                    image = image.replace("\u002F", "/")
            elif self.match("\/BV", url):
                bvid = self.match("\/(BV\w+)", url)
                bvUrl = f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}"
                page = self.match(["\?p=(\d+)", "_(\d+).h"], url) or 1
                page = int(page)
                getBvSource = self.curl(bvUrl)
                self.logging.debug(f"getBvSource: {getBvSource} \r\n")
                bvJson = self.loads(getBvSource)
                if bvJson["code"] == 0:
                    aid = bvJson["data"]["aid"]
                    image = bvJson["data"]["pic"]
                    title = bvJson["data"]["title"]
                    cidData = bvJson["data"]["pages"][page - 1]
                    vid = cidData["cid"]
                    if "part" in cidData and page > 1:
                        title = "%s--%s" % (title, cidData["part"])
                else:
                    aid = self.dec(bvid)

            elif "video" in url:
                aid = self.match("\/video\/av(\d+)", url)
                page = self.match(["_(\d+).h", "\?p=(\d+)"], url) or 1

        else:
            vid = p["parse"]

        if aid and not vid:
            page = int(page)
            viewUrl = "http://api.bilibili.com/view?appkey=12737ff7776f1ade&batch=1&page={}&id={}".format(
                page, aid
            )

            getViewSource = self.curl(viewUrl)

            self.logging.debug(f"getInfo: {getViewSource} \r\n")
            if "Document is not exists" in getViewSource:
                raise NotImplementedError("hide")
            elif "Access denied" in getViewSource:
                raise NotImplementedError("cookie")
            else:
                data = self.loads(getViewSource)
                vid = data["cid"]
                image = data["pic"]
                title = data["title"]

                if "partname" in data and page > 1:
                    title = "{}--{}".format(title, data["partname"])
        return self.compact()

    def parse(self):
        timestamp = self.timestamp
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        token = ""
        if self.cookie:
            getToken = self.curl(
                f"https://api.bilibili.com/x/player/playurl/token?cid={vid}&aid=91275169"
            )
            tokenJson = self.loads(getToken)
            token = self.haskey(tokenJson, "data.token")

        # sk = {"appkey": "YvirImLGlLANCLvM", "appsecret": "JNlZNgfNGKZEpaDTkCdPQVXntXhuiJEM"}
        # sk = {"appkey": "bb3101000e232e27", "appsecret": "36efcfed79309338ced0380abd824ac1"}
        # sk = {"appkey": "07da50c9a0bf829f", "appsecret": "25bdede4e1581c836cab73a48790ca6e"}
        # sk = {"appkey": "4409e2ce8ffd12b8", "appsecret": "59b43e04ad6965f34319062b478f83dd"}
        sk = {
            "appkey": "iVGUTjsxvpLeuDCf",
            "appsecret": "aHRmhWMLkdeMuILqORnYZocwMBpMEOdt",
        }

        otype = "video"
        qn = 80

        mParams = [
            ("appkey", sk["appkey"]),
            ("build", "4140"),
            ("buvid", "ef5efdc0452641eb235cd424dfa03660"),
            ("cid", vid),
            ("device", "phone"),
            ("otype", "json"),
            ("platform", "html5"),
            ("qn", qn),
            ("type", "mp4"),
        ]
        mEncrypt = self.urlencode(mParams)
        mUrl = "https://app.bilibili.com/v2/playurl?%s&sign=%s" % (
            mEncrypt,
            self.md5(mEncrypt + sk["appsecret"]),
        )

        mSource = self.curl(mUrl)

        mJson = self.loads(mSource)

        if "message" in mJson:
            if mJson["message"] not in ["Video is hidden."]:
                raise NotImplementedError(mJson["message"])
            else:
                otype = "bangumi"

                mParams = [
                    ("cid", vid),
                    ("module", "bangumi"),
                    ("otype", "json"),
                    ("platform", "html5"),
                    ("player", "1"),
                    ("qn", qn),
                    ("ts", timestamp),
                    ("type", "mp4"),
                ]
                mEncrypt = self.urlencode(mParams)
                mSign = self.md5(mEncrypt + "9b288147e5474dd2aa67085f716c560d")

                mUrl = (
                    "https://bangumi.bilibili.com/player/web_api/playurl?%s&sign=%s"
                    % (
                        mEncrypt,
                        mSign,
                    )
                )
                mSource = self.curl(mUrl)
                mJson = self.loads(mSource)

        self.logging.debug(f"mSource: {mSource} \r\n")

        assert "8986943" not in mSource, "area"
        assert "durl" in mJson, "lists"

        mp4 = mJson["durl"][0]["url"]

        flvQn = 80
        for i in range(2):
            if otype == "video":
                flvParams = [
                    ("appkey", sk["appkey"]),
                    ("build", "4140"),
                    ("buvid", "ef5efdc0452641eb235cd424dfa03660"),
                    ("cid", vid),
                    ("device", "phone"),
                    ("otype", "json"),
                    ("platform", "html5"),
                    ("qn", flvQn),
                    ("quality", flvQn),
                    ("type", "flv"),
                ]

                flvEncrypt = self.urlencode(flvParams)

                flvUrl = "https://interface.bilibili.com/v2/playurl?%s&sign=%s" % (
                    flvEncrypt,
                    self.md5(flvEncrypt + sk["appsecret"]),
                )
                if token:
                    flvUrl += f"&utoken={token}"
            else:
                flvParams = [
                    ("cid", vid),
                    ("module", "bangumi"),
                    ("otype", "json"),
                    ("platform", "html5"),
                    ("player", "1"),
                    ("qn", flvQn),
                    ("ts", timestamp),
                    ("type", "flv"),
                ]
                flvEncrypt = self.urlencode(flvParams)
                flvSign = self.md5(flvEncrypt + "9b288147e5474dd2aa67085f716c560d")

                flvUrl = (
                    "https://bangumi.bilibili.com/player/web_api/playurl?%s&sign=%s"
                    % (flvEncrypt, flvSign)
                )

            getFlvSource = self.curl(flvUrl)
            getFlvJson = self.loads(getFlvSource)
            qns = sorted(getFlvJson["accept_quality"])

            flvQn = self.data(qns, p["hd"])
            if flvQn >= qn and not self.cookie:
                break
        self.logging.debug(f"getFlvSource: {getFlvSource} \r\n")

        duration = getFlvJson["timelength"] / 1000
        if "url" in getFlvJson["durl"]:
            segs = [
                {
                    "url": getFlvJson["durl"]["url"],
                    "duration": duration,
                    "size": int(getFlvJson["durl"]["size"]),
                }
            ]
        else:
            segs = [
                {
                    "url": i["url"],
                    "duration": i["length"] / 1000,
                    "size": int(i["size"]),
                }
                for i in getFlvJson["durl"]
            ]
        ext = "flv" if segs[0]["url"].find(".flv") > 0 else "mp4"

        quality = getFlvJson["accept_description"][::-1]
        dicts = dict(
            zip(getFlvJson["accept_quality"], getFlvJson["accept_description"])
        )
        quality = [dicts[i] for i in qns]
        # 1800p+分辨率要会员cookie
        regx = f"-1-{flvQn}"
        if p["hd"] > 4 and regx not in segs[0]["url"] and not self.cookie:
            quality = quality[:4]
        show = self.data(quality, p["hd"])

        extra = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0",
                "Referer": "https://www.bilibili.com/video/",
            }
        }
        if len(segs) == 1 and ext == "flv":
            flv = segs[0]["url"]
            extra["playback"] = "flv"
        return self.compact()

    def dec(x):
        # https://www.zhihu.com/question/381784377/answer/1099438784
        tr = {
            "f": 0,
            "Z": 1,
            "o": 2,
            "d": 3,
            "R": 4,
            "9": 5,
            "X": 6,
            "Q": 7,
            "D": 8,
            "S": 9,
            "U": 10,
            "m": 11,
            "2": 12,
            "1": 13,
            "y": 14,
            "C": 15,
            "k": 16,
            "r": 17,
            "6": 18,
            "z": 19,
            "B": 20,
            "q": 21,
            "i": 22,
            "v": 23,
            "e": 24,
            "Y": 25,
            "a": 26,
            "h": 27,
            "8": 28,
            "b": 29,
            "t": 30,
            "4": 31,
            "x": 32,
            "s": 33,
            "W": 34,
            "p": 35,
            "H": 36,
            "n": 37,
            "J": 38,
            "E": 39,
            "7": 40,
            "j": 41,
            "L": 42,
            "5": 43,
            "V": 44,
            "G": 45,
            "3": 46,
            "g": 47,
            "u": 48,
            "M": 49,
            "T": 50,
            "K": 51,
            "N": 52,
            "P": 53,
            "A": 54,
            "w": 55,
            "c": 56,
            "F": 57,
        }
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        r = 0
        for i in range(6):
            r += tr[x[s[i]]] * 58**i
        return (r - add) ^ xor

    def enc(x):
        table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        x = (int(x) ^ xor) + add
        r = list("BV1  4 1 7  ")
        for i in range(6):
            r[s[i]] = table[x // 58**i % 58]
        return "".join(r)
