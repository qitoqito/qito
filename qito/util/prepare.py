#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : col.py
@Time    : 2022/9/5 下午9:45  
"""


class Prepare:
    def prepare_location(self):
        """
        有些链接类型一样,必须通过跳转后地址才能获取正确的category
        :return:
        """
        return ["douyin"]

    def prepare_category(self):
        """
        获取链接类型
        :return:
        """
        lists = {
            "live": {
                "heibaizhibo": ["heibaizhibo.com"],
                "qq": ["(live|now).qq.com"],
                "iqiyi": ["live.iqiyi.com\/(.*)"],
                "pps": ["gamelive.iqiyi.com", "x.pps.tv"],
                "zhuafan": ["www.zhuafan.live\/(\d+)"],
                "douyin": ["webcast.amemv.com\/", "live.douyin.com"],
                "douyu": ["www.douyu.com\/(\d+)", "(douyu.com\/topic)"],
                "bilibili": ["(live.bilibili)"],
                "cntv": ["(cctv.com\/live)"],
                "longzhu": ["(?<!v.)longzhu.com\/(\w+)"],
                "laifeng": ["(v.laifeng.com)"],
                "huya": ["(www.huya.com)"],
                "huajiao": ["(huajiao.com\/l\/)"],
                "yy": ["(yy.com\/\d+\/\d+)"],
                "ixigua": ["(live.ixigua.com)"],
                "56": ["(qf.56.com)"],
                "pptv": ["(sports.pptv.com\/sportslive)"],
                "yizhibo": ["(yizhibo.com)"],
                "zhangyu": ["zhangyu(?:live)*.com\/(\d+)"],
                "huomao": ["huomao.com\/(?:mobile\/mob_live\/)*(\d+)"],
                "chushou": ["chushou.tv\/room/(\d+)"],
                "kuaishou": ["(live.kuaishou.com\/)(?!u\/\w+\/\w+)(?!playback\/)"],
                "twitch": ["(twitch.tv\/)(?!videos\/)(\w+)"],
                "zhanqi": [
                    "(?!videos)",
                    # "(?<!videos.)zhanqi.tv"
                ],
            },
            "music": {
                "bilibili": ["(bilibili.com\/audio)"],
                "qq": ["(y.qq.com)"],
                "netease": ["music.163.com\/(?:m|\#)*(?:\/)*song"],
                "migu": ["(c.migu.cn)", "(h5.nf.migu.cn)"],
                "kuwo": ["(bd.kuwo.cn\/play_detail)"],
                "kugou": ["(kugou.com\/song)"],
                "xiami": ["(xiami.com\/song)"],
                "taihe": ["(music.taihe.com)", "(music.baidu.com)"],
            },
        }
        return lists

    def prepare_change(self, site):
        """
        解析链接的type替换
        :param site:
        :return:
        """
        lists = {
            "douyutv": "douyu",
            "letv": "le",
            "toutiao": "ixigua",
            "iesdouyin": "douyin",
            "iq": "iqiyi",
            "toutiaoimg": "toutiao",
            "ppsport": "pptv",
            "365yg": "toutiao",
            "b23": "bilibili",
            "zhangyulive": "zhangyu",
            "cctv": "cntv",
            "gifshow": "kuaishou",
            "tianmao": "tmall",
            "tb": "taobao",
            "amemv": "douyin",
            "youtu": "youtube",
            "tudou": "youku",
        }

        if site in lists.keys():
            site = lists[site]
        return site

    def prepare_quality(self, params):
        if params["category"] == "live":
            pass
        elif params["category"] == "music":
            pass
        else:
            dicts = {
                "le": {"350": "流畅", "1000": "标清"},
                "youku": {"mp4sd": "标清"},
                "iqiyi": {
                    "96": "210p",
                    "100": "210p",
                    "1": "360P",
                    "200": "360P",
                    "2": "540p",
                    "21": "540p",
                    "300": "540p",
                    "14": "540p",
                    "75": "540p",
                    "4": "720p",
                    "17": "720p",
                    "500": "720p",
                    "5": "1080p",
                    "18": "1080p",
                    "600": "1080p",
                    "19": "4k",
                    "10": "4k",
                },
            }
        try:

            if self.get(f"{params['category']}Quality") and self.get(
                f"{params['category']}Quality"
            ).get(params["type"]):
                data = dict(
                    k.split(":")
                    for k in (
                        self.get(f"{params['category']}Quality")
                        .get(params["type"])
                        .split("|")
                    )
                )
            else:
                data = dicts[params["type"]]
            quality = params["quality"]
            params["quality"] = [data.get(k, k) if k in data else k for k in quality]
            if quality != params["quality"]:
                params["description"] = quality
            params["show"] = data.get(params["show"], params["show"])
        except:
            pass

        return params

    def prepare_compact(self):
        return [
            "uid",
            "cid",
            "ape",
            "vid",
            "aid",
            "language",
            "page",
            "streams",
            "pay",
            "playback",
            "context",
            "m3u8",
            "segs",
            "duration",
            "anchor",
            "mid",
            "cdn",
            "country",
            "m4a",
            "size",
            "show",
            "title",
            "ext",
            "playtype",
            "flv",
            "mp4",
            "hd",
            "mp3",
            "flac",
            "publish",
            "quality",
            "wav",
            "genre",
            "image",
            "singer",
            "otype",
            "artist",
            "album",
            "cover",
            "company",
            "extra",
            "upload",
        ]

    def prepare_stream(self, lists, stacks, funcName=""):
        r = {}
        if funcName in ["parse", "afresh"]:
            r["streams"] = {}
            if "ext" not in stacks:
                r["ext"] = "mp4"
            if "playback" not in stacks:
                r["playback"] = "mp4"

        if funcName == "extra":
            for index in stacks:
                r[index] = lists[index]
        else:
            for index in stacks:
                if lists[index]:
                    if index in ["quality"]:
                        r[index] = lists[index]
                        r["multirates"] = len(r[index])

                    elif index in [
                        "segs",
                        "live",
                        "music",
                        "mp4",
                        "m3u8",
                        "flv",
                        "mp3",
                        "m4a",
                        "flac",
                        "ape",
                        "m4v",
                        "wav",
                    ]:
                        r["streams"][index] = lists[index]

                    else:
                        r[index] = lists[index]

        if (
            funcName in ["parse", "afresh"]
            and not r["streams"].get("segs")
            and r["streams"].get(r["ext"])
        ):
            r["streams"]["segs"] = [{"url": r["streams"][r["ext"]]}]
            if r.get("duration"):
                r["streams"]["segs"][0]["duration"] = r["duration"]
            if r.get("size"):
                r["streams"]["segs"][0]["size"] = r["size"]

        # 设置extra headers
        if funcName in ["parse", "afresh"] and not r.get("extra"):
            r["extra"] = {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0"
                }
            }
        elif (
            r.get("extra")
            and not r["extra"].get("remove")
            and not r["extra"].get("headers")
        ):
            r["extra"]["headers"] = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0"
            }
        for k, v in list(r.items()):
            if not v:
                del r[k]
        return r
