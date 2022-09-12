#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : qq.py
@Time    : 2022/9/8 下午10:51  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "腾讯剧集列表"

    def videoList(self, params):
        if params["parse"].startswith("http"):
            cover = self.match("cover\/(\w+)", params["parse"])
        else:
            cover = params["parse"]

        s = self.curl(
            {
                "url": "https://pbaccess.video.qq.com/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=3000010&vplatform=2",
                "json": {
                    "page_params": {
                        "page_type": "detail_operation",
                        "page_id": "vsite_episode_list",
                        "id_type": "1",
                        "page_size": "50",
                        "cid": cover,
                        "vid": "",
                        "lid": "0",
                        "req_from": "web_mobile",
                        "page_context": "",
                    }
                },
                "cookie": {
                    "sd_cookie_crttime": "165235985518",
                    "vversion_name": "8.2.95",
                    "video_bucketid": "4",
                    "appid": "wxa75efa648b60994b",
                    "_video_qq_appid": "wxa75efa648b60994",
                },
                "headers": {
                    "Host": "pbaccess.video.qq.com",
                    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79;supportJDSHWK/1;",
                    "accept": "application/json",
                    "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                    "referer": "https://m.v.qq.com/",
                    "content-type": "application/json;charset=UTF-8",
                    "origin": "https://m.v.qq.com",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "te": "trailers",
                },
            }
        )
        data = self.jsonParse(s)
        playList = []

        for k in self.haskey(
            data, "data.module_list_datas.0.module_datas.0.item_data_lists.item_datas"
        ):
            playList.append(
                {
                    "parse": k["item_params"]["vid"],
                    "title": k["item_params"]["play_title"],
                }
            )
        return {"data": playList, "category": "video", "type": "qq"}
