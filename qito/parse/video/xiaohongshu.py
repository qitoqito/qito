#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : xiaohongshu.py
@Time    : 2022/11/28 下午4:00  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "小红书视频(XIAOHONGSHU)"

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            vid = self.match("item\/(\w+)", p["parse"])
        else:
            vid = p["parse"]
        self.auth()
        return self.compact()

    def parse(self):
        p = self.params
        assert p["vid"], "vid"
        vid = p["vid"]
        html = self.curl(
            {
                "url": "https://www.xiaohongshu.com/discovery/item/6382364d0000000018013c1a",
                "cookie": self.cookie or self.auth(),
                "decoding": "uft8",
            }
        )

        data = self.jsonParse(
            self.match(r"__INITIAL_SSR_STATE__\s*=\s*([^\<]+)<", html)
        )
        noteInfo = self.haskey(data, "NoteView.noteInfo")
        assert noteInfo, "data"
        title = noteInfo["title"]
        image = "https:" + noteInfo["imageList"][0]["url"]
        mp4 = noteInfo["video"]["url"]
        duration = noteInfo["video"]["duration"]

        return self.compact()

    def auth(self):
        cookies = "extra_exp_ids=ios_wx_launch_open_app_origin,h5_video_ui_exp3,wx_launch_open_app_duration_origin,ques_clt2"

        headers = {
            "Host": "www.xiaohongshu.com",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:107.0) Gecko/20100101 Firefox/107.0",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "referer": "https://www.xiaohongshu.com/web-login/canvas?redirectPath=http%3A%2F%2Fwww.xiaohongshu.com%2Fdiscovery%2Fitem%2F6382364d0000000018013c1a",
            "content-type": "application/json",
            "origin": "https://www.xiaohongshu.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers",
        }

        data = {
            "id": "6a73595fed4e97dac920e9788f1922a8",
            "sign": "713c02f1ffc1412d6a76c53e3a5eca9ce72ac06f4c4c880944f40e7c7e56313287f1e9374ce45962f06653e37edd19f3563b167595fd402e698295e04cb44f02fee3bbefb07df78ff76672856ff0e458b034eabe207fecb2234f396af2fb991f6b53d321b37858331765b2ce93b0c73255b6b20adb2517ec0d815fa0097fe39d317bba73458df208d7e1729f1b6da90ee268efe6442d9720ed4b37ada0ce7dd69d1410c6ab2ea32022b9a980a4416a7a4f86fad8da9cb32ad0453f46d3d1928c3c0f78a37885139e1a9a4b205acb3b239548f02926935aae291dc4d21c3b86ecfe46f963a5bb773859c26e9360e9408a0a91fb33a84e6dbf089b500df3586be5baab6bf3999416ad55e37c40c7bf956251c724a9093d1ad0f3df20185411adabd39b0039634f516858d60f6e4521b4bc7743cba45c4b9d27a2b1eed68c50b934050da89e8f2e6eda6ad9171f9ede2cf9f486f59c00c26a4b952763dfcc05727a6f19e633979a8d67c9fd3dd9aa26696b84c457893d966f9b1756cb49ec082c17578a21c01c690652a513670af7084c5605bc3863380e255451658c41fb5d5bd312e2e88e159e39fe4e3318bd171d135c7803f325e8f4c3e2055cbd75a54279acf0870e3215301d6ca44288c469aedda2836bc2423c227118c53c8cc1df12a9c065f849ca4b0e31376ac65072dfbe4f0f7c46e1feb4ad3b6a8338b769ab8baec4ab929b4353ba811f595756af221c6fb9bce0e5fbfde731b16abc75c293d7c036869d592c1becf4cdedef2c93edcab3d5852681ac22ccd29b139ff15e6ffa4eedbbf5a709480a192ebd6dcc0a7c94bfabeebdec2726371b9fe93313e0a316258e63019d4f8f4c3b7116e828d4601f39c482c79922fb901e21fdd2b1ed1d07808a36ddb234ae6208923f8b88733f5f53c883e1e92e8e3832b627438b6ecd0360efdcf421a3d682f18a148851f0f7cea1589678d805ea3f4934bef5b7503ee95db196c5f0542b4d06d9ef30507f3fac6bc466b54a950b3fbe374ab7ffacf5d0107d2265cb0bcdc12c8e60507996a908410d70577909ad0d5ad6b3a9e500c70c6d8625731d977f89fc211c46fc6641d240e092b075a4f7e377d1bbf5a709480a192ebd6dcc0a7c94bfabeebdec2726371b9fe93313e0a316258e63019d4f8f4c3b7116e828d4601f39c482c79922fb901e21fdd2b1ed1d07808a36ddb234ae6208923f8b88733f5f53c883e1e92e8e3832b6fdc8d68b2905c927b9846ec7d2a4fcfad34920e46f8d80726b0a8dc6241c1c88a59cf31eac2dda12cff8705ecebf2f95243ed772eaabf3e6c28dec4feb6817c6a34c8e1e9e59351a31b9b144b2a7516f0c32bd2c88bba99a15da9491605c225cef8a94938c35e092037d8db827811f816a568a78b3cb779c0f2ab3f85335c577a48b7d69bd4f55ab1686ecdb6ed2712197c1bef2dfa9274bbef5b7503ee95db196c5f0542b4d06d9ef30507f3fac6bc466b54a950b3fbe374ab7ffacf5d0107d2265cb0bcdc12c8e60507996a908410d70577909ad0d5ad6b3a9e500c70c6d86837dd4c3ac792182ea5ce5dd697ffa05028451955d70e829892991d95ee040462d4ae669ed39bf2e4cb79f93dab3888102bf764f8320f9aa1a0eea5740d3e5ee42eeb22ac4ac6b975f1a45243f52d0b3959377256265807d8cd0900876f1ed046ef7851b9ba91a35c3f600f9371d07ed6cf6cf76a9c1efb32e94bb9b45ce065bda114c6c5551c1c71f9878091009e426b8a8cdcbe5c5d62c413657b023d71c6ce2d1976f8d613e8db8a8cdcbe5c5d62c413657b023d71c6c19392a720588b62d6f89aa22a406677cff79b0daf7232964fee6ec89b600c672f2019a0ce334ec3d32dd0a9e8ec1ebd4c96b3610a48b16f12592e3f75d03bfbc93f7c3b25247cfe27ce6e2d0f3ed9911e7b5eb3ce7819d141148dfccf0c10a9cadbbd181abfafc9da50f8098bf421ed16f51ba4a2e264e6021feb6e3215a382aa8491c7b54b92125",
        }
        url = "https://www.xiaohongshu.com/fe_api/burdock/v2/shield/registerCanvas?p=cc"
        cookies = self.curl(
            {"url": url, "headers": headers, "response": "cookie", "json": data}
        )
        return cookies
