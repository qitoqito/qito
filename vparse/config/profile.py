#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : profile.py
@Time    : 2022/2/13 下午4:48  
"""
version = "1.0.0"
qitoFilter = "version|cookie|dir|exit|format|info|json|query|debug|proxy|http|timeout|download|merge|multi|dir|capture|geometry|loop|player|fullscreen|start|end|length|no_audio|no_video|volume|init|language|itag|ccode|password|encoder|name"
qitoCategory = {
    "live": {
        "heibaizhibo": ["heibaizhibo.com"],
        "qq": ["(live|now).qq.com"],
        "iqiyi": ["live.iqiyi.com\/(.*)"],
        "pps": ["gamelive.iqiyi.com", "x.pps.tv"],
        "zhuafan": ["www.zhuafan.live\/(\d+)"],
        "douyin": ["webcast.amemv.com\/"],
        "douyu": ["www.douyu.com\/(\d+)", "(douyu.com\/topic)"],
        "bilibili": ["(live.bilibili)"],
        "cctv": ["(cctv.com\/live)"],
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
