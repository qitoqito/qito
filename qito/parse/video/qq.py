#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : qq.py
@Time    : 2022/9/3 上午7:24
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "腾讯视频(QQ)"
        self.require = [
            "pyaes",
            "quickjs",
            ("Crypto.Util.Padding", ("pad", "unpad")),
            ("Crypto.Cipher", "AES"),
        ]

    def query(self):
        p = self.params
        if self.hasurl(p["parse"]):
            vid = self.match(
                ["vid=(\w+)", "/(\w+)$", "cover\/\w+\/(\w+)"],
                p["parse"],
            )
            html = self.curl(p["parse"])
            if not vid:
                vid = self.match(
                    [
                        "&vid=(\w+)",
                        "vid:\s*[\"'](\w+)",
                        "vid\s*=\s*[\"']\s*(\w+)",
                        '"vid":"(\w+)"',
                    ],
                    html,
                )
        else:
            vid = p["parse"]
        if p.get("query"):
            info = self.curl(
                {
                    "url": "https://vv.video.qq.com/getinfo",
                    "params": {
                        "charge": "0",
                        "vid": vid,
                        "defaultfmt": "auto",
                        "otype": "json",
                        "guid": "33fe1dbd31182cc02a7fcebb32df167c",
                        "platform": "10901",
                        "defnpayver": "1",
                        "appVer": "3.4.21",
                        "sdtfrom": "v1010",
                        "host": "v.qq.com",
                        "_rnd": self.timestamp,
                        "fhdswitch": "0",
                        "show1080p": "1",
                        "isHLS": "0",
                        "newplatform": "10901",
                        "defsrc": "2",
                        "tm": self.timestamp,
                        "sphttps": "v.qq.com",
                        "spwm": "4",
                        "ehost": f"https://v.qq.com/x/page/{vid}.html",
                    },
                }
            )
            self.logging.debug(f"getInfo: {info} \r\n")
            data = self.jsonParse(info)
            assert "msg" not in data, data["msg"]
            if "lnk" in data["vl"]["vi"][0]:
                vid = data["vl"]["vi"][0]["lnk"]
            title = data["vl"]["vi"][0]["ti"]
            duration = data["vl"]["vi"][0]["td"]

            image = f"http://puui.qpic.cn/vpic_cover/{vid}/{vid}_hz.jpg"

        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        timestamp = self.timestamp / 1000
        vid = p["vid"]
        if self.cookie:
            s = self.curl(
                {
                    "url": "https://access.video.qq.com/user/auth_refresh?vappid=11059694&vsecret=fdf61a6be0aad57132bc5cdf78ac30145b6cd2c1470b0cfe&type=wx&g_tk=&g_vstk=854964343&g_actk=87088392&callback=jQuery19109635376764129958_1662439073395&_=1662439073397",
                    "headers": {
                        "Host": "access.video.qq.com",
                        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:104.0) Gecko/20100101 Firefox/104.0",
                        "accept": "*/*",
                        "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                        "referer": "https://v.qq.com/",
                        "sec-fetch-dest": "script",
                        "sec-fetch-mode": "no-cors",
                        "sec-fetch-site": "same-site",
                        "te": "trailers",
                    },
                    "response": "response",
                }
            )
            # print(s['cookie'])
            if s.get("cookie").get("refresh_token"):
                self.cookie = s.get("cookie")

        # 解析路线
        vUrl = "https://vv.video.qq.com/getvinfo?"
        pUrl = "https://vd.l.qq.com/proxyhttp?"

        mp4 = ""
        platform = "10201"
        sdtfrom = "v1010"
        ctime = self.strftime("%Y-%m-%d %H:%M:%S", timestamp)

        refere = f"https://v.qq.com/x/page/{vid}.html"
        appver = "3.4.31"
        pid = self.md5(vid)
        guid = self.md5(f"{timestamp}{vid}")
        encryptVer = "8.1"
        cKey = self.ckey8(vid, platform, appver, guid, timestamp)
        image = f"http://puui.qpic.cn/vpic_cover/{vid}/{vid}_hz.jpg"

        onlyInfo = self.curl(
            {
                "url": vUrl,
                "params": {
                    "charge": "0",
                    "vid": vid,
                    "defaultfmt": "auto",
                    "otype": "json",
                    "guid": guid,
                    "platform": platform,
                    "defnpayver": "1",
                    "appVer": appver,
                    "sdtfrom": sdtfrom,
                    "host": "v.qq.com",
                    "ehost": refere,
                    "_rnd": timestamp,
                    "defn": "shd",
                    "fhdswitch": "0",
                    "show1080p": "1",
                    "isHLS": "0",
                    "newplatform": platform,
                    "tm": timestamp,
                    "encryptVer": encryptVer,
                    "cKey": cKey,
                    "sphttps": "v.qq.com",
                    "spwm": "4",
                },
                "referer": refere,
            }
        )

        self.logging.debug(f"getVideoInfo: {onlyInfo} \r\n")
        data = self.jsonParse(onlyInfo)

        ip = data["ip"]
        m3u8 = ""
        assert "msg" not in data, data["msg"]
        if "lnk" in data["vl"]["vi"][0]:
            vid = data["vl"]["vi"][0]["lnk"]
            cKey = self.ckey8(vid, platform, appver, guid, timestamp)
        # 判断其是否是会员vip

        drm = data["vl"]["vi"][0]["drm"]
        fvkey = data["vl"]["vi"][0]["fvkey"]
        vu = data["vl"]["vi"][0]["ul"]["ui"][0]["url"]
        fileDict = self.column(data["fl"]["fi"], "", "sname")

        quality = list(fileDict.keys())
        show = self.data(quality, p["hd"])

        stream = fileDict[show]
        fmt = str(stream["id"])
        flowid = f"{pid}_{fmt}"
        defn = stream["name"]
        title = data["vl"]["vi"][0]["ti"]
        if fmt[0:2] == "10":
            fp = f"p{fmt[2:]}"
        elif fmt[0:2] == "11":
            fp = f"p{fmt[1:]}s"
        else:
            fp = fmt
        # 分段数目
        fc = data["vl"]["vi"][0]["cl"]["fc"]
        duration = data["vl"]["vi"][0]["td"]
        pay = 1 if drm else ""

        if "msg" in data:
            assert data["msg"] not in (
                "vid is wrong",
                "vid status wrong",
            ), "hide"

        segs = []
        if not pay:
            fc = fc if fc != 0 else 1
            idxLen = int(float(duration) / 3000) + 1
            array = [[] for k in range(idxLen)]
            for i in range(fc):
                array[int(i / 10)].append(str(i + 1))
            idxs = ["|".join(j) for j in array if len(j)]
            for idx in idxs:

                vkeyUlr = f"{pUrl}buid=onlyvkey&vkeyparam=" + self.quote(
                    self.urlencode(
                        {
                            "otype": "ojson",
                            "vid": vid,
                            "format": fmt,
                            "idx": idx,
                            "vt": "116",
                            "sdtfrom": sdtfrom,
                            "platform": platform,
                            "guid": guid,
                            "flowid": flowid,
                            "charge": "0",
                            "linkver": "2",
                            "lnk": vid,
                            "tm": timestamp,
                            "referer": refere,
                            "ehost": refere,
                            "appVer": appver,
                            "host": "v.qq.com",
                            "sphttps": "1",
                            "encryptVer": encryptVer,
                            "cKey": cKey,
                        }
                    )
                )

                source = self.curl(vkeyUlr)
                self.logging.debug(f"getOnlyvkey: {source} \r\n")
                vSource = self.loads(source)
                vdata = self.loads(vSource["vkey"])
                assert "msg" not in vdata, "data"
                size = int(stream["fs"])
                z = 0
                for i in vdata["vl"]["vi"][0]["cl"]["ci"]:

                    if i.get("key"):
                        filename = f"{vid}.{fp}.{i['idx']}.mp4"
                        guidd = self.md5(f"{guid}{vid}{i['idx']}{ip}{timestamp}")
                        if fc == 1:
                            segs.append(
                                {
                                    "url": f"{vu}{filename}?sdtfrom={sdtfrom}&guid={guidd}&vkey={i['key']}",
                                    "duraion": duration,
                                }
                            )
                        else:
                            segs.append(
                                {
                                    "url": f"{vu}{filename}?sdtfrom={sdtfrom}&guid={guidd}&vkey={i['key']}",
                                    "duraion": data["vl"]["vi"][0]["cl"]["ci"][z]["cd"],
                                }
                            )
                            z += 1
                if len(segs) == 1:
                    mp4 = segs[0]["url"]
        if not mp4:

            try:

                defn = defn if self.cookie else "hd"
                for defn in [defn, "hd"]:

                    oUrl = f"{pUrl}buid=onlyvinfo&vinfoparam=" + self.quote(
                        self.urlencode(
                            {
                                "charge": 0,
                                "guid": guid,
                                "defaultfmt": "auto",
                                "otype": "ojson",
                                "platform": platform,
                                "sdtfrom": sdtfrom,
                                "defnpayver": 1,
                                "appVer": appver,
                                "host": "v.qq.com",
                                "refer": refere,
                                "ehost": refere,
                                "sphttps": 1,
                                "tm": timestamp,
                                "encryptVer": encryptVer,
                                "cKey": cKey,
                                "spwm": 4,
                                "vid": vid,
                                "defn": defn,
                                "fhdswitch": 1,
                                "show1080p": 1,
                                "isHLS": 1,
                                "onlyGetinfo": True,
                                "dtype": 3,
                                "sphls": 1,
                                "defsrc": 2,
                            }
                        )
                    )

                    onlyInfo = self.curl(oUrl)
                    self.logging.debug(f"onlyInfo: {onlyInfo} \r\n")
                    json = self.loads(onlyInfo)
                    if "vinfo" in json:
                        data = self.loads(json["vinfo"])
                        try:
                            turl = data["vl"]["vi"][0]["ul"]["ui"][0]
                            m3u8 = turl["url"] + turl["hls"]["pt"]
                            playback = "m3u8"
                            if len(segs) < 1:
                                segs.append({"url": m3u8, "duration": duration})
                        except:
                            pass

                    if not m3u8:
                        quality = list(fileDict.keys())[:2]
                        show = self.data(quality, p["hd"])
                    else:
                        break
            except:
                mUrl = f"{pUrl}buid=onlyvkey&vkeyparam=" + self.quote(
                    self.urlencode(
                        {
                            "otype": "ojson",
                            "vid": vid,
                            "format": "2",
                            "idx": "0",
                            "vt": "116",
                            "sdtfrom": sdtfrom,
                            "platform": platform,
                            "guid": guid,
                            "flowid": flowid,
                            "charge": "0",
                            "linkver": "2",
                            "lnk": vid,
                            "tm": timestamp,
                            "referer": refere,
                            "ehost": refere,
                            "appVer": appver,
                            "host": "v.qq.com",
                            "sphttps": "1",
                            "encryptVer": encryptVer,
                            "cKey": cKey,
                        }
                    )
                )
                mSource = self.curl(mUrl)
                mVkey = self.match(
                    ['"key\\\\":\\\\"(\w+)', '"key\\":\\"(\w+)'], mSource
                )
                if mVkey:
                    mp4 = "{}{}.mp4?sdtfrom={}&guid={}&vkey={}".format(
                        vu, vid, sdtfrom, guid, mVkey
                    )
                    if len(segs) < 1:
                        segs.append({"url": mp4, "duration": duration})
        if not mp4 and m3u8:
            ext = playback = "m3u8"
        extra = {
            "reload": 1,
            "params": {
                "platform": platform,
                "sdtfrom": sdtfrom,
                "format": fmt,
                "guid": guid,
                "flowid": flowid,
                "appver": appver,
                "encryptVer": encryptVer,
                "cKey": cKey,
            },
        }
        return self.compact()

    def ckey8(self, vid, platform, appver, guid, tm):
        loc3 = f"|{vid}|{tm}|mg3c3b04ba|{appver}|{guid}|{platform}|https://v.qq.com/x/page/{vid}.html|mozilla/5.0 (macintosh; intel mac os x 10.13; rv|https://v.qq.com/|Mozilla|Netscape|MacIntel|00|"
        loc4 = 0
        i = 0
        while i < len(loc3):
            char = ord(loc3[i])
            loc4 = self.intval32((loc4 << 5) - loc4 + char)
            loc4 &= loc4
            i = i + 1
        loc5 = f"|{loc4}{loc3}"
        key = "4f6bdaa39e2f8cb07f5e722d9edef314"
        iv = "01504af356e619cf2e42bba68c3f70f9"
        try:
            if self.modules.get("pyaes"):
                cbc = self.modules["pyaes"].AESModeOfOperationCBC(
                    bytes.fromhex(key), bytes.fromhex(iv)
                )
                x = 16 - len(loc5) % 16
                y = loc5.encode("utf-8") + x * chr(x).encode()
                blocks = [y[i : i + 16] for i in range(0, len(y), 16)]
                ciphertext = b""
                for b in blocks:
                    ciphertext = ciphertext + cbc.encrypt(b)
                output = bytes.hex(ciphertext).upper()
            else:
                output = bytes.hex(
                    self.modules["AES"]
                    .new(
                        bytes.fromhex(key),
                        self.modules["AES"].MODE_CBC,
                        bytes.fromhex(iv),
                    )
                    .encrypt(self.modules["pad"](loc5.encode("utf-8"), 16))
                ).upper()
        except:
            js = self.read(self.abspath + "/tool/javascript/aes.js")
            js += """
                        function encrypt(str,key,iv) {
                            var key = CryptoJS.enc.Hex.parse(key);
                            var iv = CryptoJS.enc.Hex.parse(iv); 
                            return CryptoJS.AES.encrypt(
                                str, key, {
                                    iv: iv,
                                    mode: CryptoJS.mode.CBC,
                                    padding: CryptoJS.pad.Pkcs7
                                }).ciphertext.toString().toUpperCase();
                        }  
                          """
            try:
                from quickjs import Function

                f = Function("encrypt", js)
                output = f(
                    loc5,
                    key,
                    iv,
                )

            except:
                import execjs

                ctx = execjs.compile(js)
                output = ctx.call(
                    "encrypt",
                    loc5,
                    key,
                    iv,
                )

        return output

    def intval32(self, val):
        maxint = 2147483647
        if not -maxint - 1 <= val <= maxint:
            val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        return val
