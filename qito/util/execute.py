#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : download.py
@Time    : 2022/8/9 下午6:32  
"""
import time, importlib, os, sys, logging, json, subprocess, threading, requests
from pathlib import Path


class Execute:
    def execute_init(self):
        if not self.data.get("info"):
            self.execute_directory()
        self.execute_console()
        self.block = 12 if sys.platform in ["win32"] else 32  # 终端█显示数目
        self.data["threading"] = []  # 多线程存储
        self.data["output"] = []
        self.data["multi"] = self.data.get("multi") or 10
        self.data["title"] = self.data.get("title") or self.data["title"]
        if self.data.get("info"):
            self.execute_info()
        elif self.data.get("player"):
            self.execute_player()
        else:
            self.execute_download()
        print("\n")

    def execute_directory(self):
        self.data["dir"] = (
            self.data.get("dir")
            or self.get("filePath")
            or f"{self.cwd}/download/{self.data['category']}/{self.data['type']}"
        )
        # if self.data.get("dir"):
        #     self.data["dir"] = self.data["dir"]
        # elif self.get("filePath"):
        #     self.data["dir"] = self.filePath
        # else:
        #     self.data[
        #         "dir"
        #     ] = f"{self.cwd}/download/{self.data['category']}/{self.data['type']}"

        if self.data["dir"].startswith("."):
            self.data["dir"] = f'{self.cwd}{self.data["dir"][1:]}'

        folder = [z for z in self.data["dir"].split("/") if z]
        for s in folder:
            if s in ["%category", "%type", "%vid", "%title"] and s[1:] in self.data:
                self.data["dir"] = self.data["dir"].replace(s, self.data[s[1:]])
            elif s[0] == "%":
                self.data["dir"] = self.data["dir"].replace(s, time.strftime(s))
        if not Path(self.data["dir"]).exists():
            os.makedirs(self.data["dir"])

    def execute_console(self):
        if self.data.get("name"):
            self.data["title"] = self.data["name"]
        print("{}:{}{}".format("Web", 17 * " ", self.title))
        for i in [
            "site",
            "title",
            "image",
            "vid",
            "aid",
            "cid",
            "uid",
            "anchor",
            "parse",
            "category",
            "hd",
            "format",
        ]:
            if self.data.get(i):
                print(
                    "{}:{}{}".format(i.capitalize(), (20 - len(i)) * " ", self.data[i])
                )

        print("Stream:")
        print(f"    - Ext:           {self.data['ext']}")
        if self.data.get("playback"):
            print(f"      Playback:      {self.data['playback']}")
        if self.data.get("pay"):
            print(f"      Pay:           {self.data['pay']}")
        if self.data.get("size"):
            size = round(int(self.data["size"]) / 1024 / 1024, 2)
            print(f"      Size:          {size}M [{self.data['size']} Bytes]")
        if self.data.get("duration"):
            print(f"      Duration:      {self.data['duration']}s")
        if self.data.get("quality"):
            if self.data.get("description"):
                print(f"      Description:   {self.data['description']}")
            print(f"      Quality:       {self.data['quality']}")
            print(f"      Show:          {self.data['show']}")
            print(f"      Multirates:    {self.data['multirates']}")

        if self.data["streams"].get("segs"):
            print(f'      Length:        {len(self.data["streams"]["segs"])}')
        if self.get("iniPath"):
            print(f'      Ini:           {self.iniPath}/{self.data["type"]}.ini')
        if self.data.get("dir"):
            print(f'      Dir:           {self.data["dir"]}')


    def execute_info(self):
        print("Location:")
        print(
            "    - {}:{}{}".format(
                self.data["playback"],
                (14 - len(self.data["playback"])) * " ",
                self.data["streams"][self.data["playback"]],
            )
        )
        if (
            len(self.data["streams"]["segs"]) == 1
            and self.data["ext"] == self.data["playback"]
        ):
            pass
        else:
            for k, v in enumerate(self.data["streams"]["segs"]):
                print(
                    "      part[{}]:{}{} {}".format(
                        (k + 1),
                        (14 - len(f"part[{k + 1}]")) * " ",
                        v["url"],
                        f"[{v.get('size')}]" if v.get("size") else "",
                    )
                )
        if self.data["extra"].get("adaptive"):
            for k, v in enumerate(self.data["extra"]["adaptive"]):
                print(
                    "      itag[{}]:{}{} {}".format(
                        v["itag"],
                        (14 - len(f"part[{v['itag']}]")) * " ",
                        v["url"],
                        f"[{v.get('contentLength')}]" if v.get("contentLength") else "",
                    )
                )
        sys.exit("\r")

    def execute_player(self):
        if self.data["streams"].get("segs") and len(self.data["streams"]["segs"]) == 1:
            self.data["target"] = self.data["streams"]["segs"][0]["url"]
        else:
            self.data["target"] = self.data["streams"][self.data["playback"]]
        # self.data["target"] = self.data["streams"][self.data["playback"]]
        # 播放
        if "temp" in [self.haskey(self.data, "extra.player"), self.data["player"]]:
            self.player_temp()
        elif self.data.get("itag") and ":" in self.data["itag"]:
            self.player_itag()
        elif self.data["player"] == "mpv":
            self.player_mpv()

    def execute_download(self):
        if self.data["extra"].get("adaptive"):
            self.download_youtube()
        elif self.data["category"] == "live":
            self.download_live()
        elif self.data["ext"] == "m3u8":
            self.download_m3u8()
        else:
            self.download_segs()

    def execute_export(self):
        cmd = self.cmd
        if self.proxy and self.proxy != "ignore":
            merged = []
            callback = cmd[0]
            del cmd[0]
            for opt in cmd:
                if opt[0:1] == "--":
                    merged.append(opt)
                elif opt[0] in ["-", '"', "'"]:
                    merged.append(opt)
                else:
                    merged.append(repr(opt))
            if sys.platform in ["win32"]:
                export = [
                    "set",
                    f"https_proxy={self.http.replace('socks5', 'https')}",
                    "&&",
                    "set",
                    f"http_proxy={self.http.replace('socks5', 'http')}",
                    "&&",
                    "set",
                    f"all_proxy={self.proxy}",
                    "&&",
                    callback,
                ]
            else:
                export = [
                    "export",
                    f"https_proxy={self.http.replace('socks5', 'https')}",
                    f"http_proxy={self.http.replace('socks5', 'http')}",
                    f"all_proxy={self.proxy}",
                    "&&",
                    callback,
                ]
            call = export + merged
            cmd = " ".join(call).replace("'", '"')
            subprocess.call(cmd, env=self.env, shell=True)
        else:
            subprocess.call(
                cmd,
                env=self.env,
            )

    def player_mpv(self):
        call = ["mpv", self.data["target"]]

        if self.data.get("title"):
            call.extend(
                [
                    f'--title="{self.title}: {self.data["title"].strip()}"',
                    f'--force-media-title="{self.data["title"].strip()}"',
                ]
            )
        if self.data["playback"] in ["m3u8", "hls"]:
            call.extend(
                [
                    "--demuxer-lavf-o="
                    + "protocol_whitelist=[file,http,https,tls,rtp,tcp,udp,crypto,httpproxy]",
                ]
            )
        if self.haskey(self.data, "extra.referer"):
            call.extend(["--referrer=" + self.data["extra"]["referer"]])
        if self.haskey(self.data, "extra.useragent"):
            call.extend(["--user-agent=" + self.data["extra"]["useragent"]])
        if self.haskey(self.data, "extra.headers"):

            extra = self.data["extra"]
            if "Accept-Language" in extra["headers"]:
                del extra["headers"]["Accept-Language"]
            if not extra["headers"].get("remove"):
                call.extend(
                    [
                        '--http-header-fields="{}"'.format(
                            ",".join(
                                [
                                    "{}:{}".format(k, v)
                                    for k, v in extra["headers"].items()
                                ]
                            )
                        )
                    ]
                )

        if self.data.get("loop"):
            call.extend(["--loop=" + self.data["loop"]])
        if self.data.get("fullscreen"):
            call.extend(["--fs"])
        if self.data.get("start"):
            call.extend(["--start=" + self.data["start"]])
            if self.data.get("length"):
                call.extend(["--length=" + self.data["length"]])
        if self.data.get("end"):
            call.extend(["--end=" + self.data["end"]])
        if self.data.get("geometry"):
            call.extend(["--geometry=" + self.data["geometry"]])
        if self.data.get("no_video"):
            call.extend(["--no-video"])
        if self.data.get("no_audio"):
            call.extend(["--no-audio"])
        if self.data.get("volume"):
            call.extend(["--volume=" + self.data["volume"]])
        if self.data.get("audio_file"):
            call.extend([f'--audio-file="{self.data["audio_file"]}"'])
        if self.data.get("mime_type"):
            pass

        if self.proxy and self.proxy != "ignore":
            env = os.environ.copy()
            if self.proxy.startswith("socks"):
                call.extend(["--ytdl-raw-options=" + f"proxy=[{self.proxy}]"])
        print("\r")
        print(f"PlayBack: {self.data['target']}")
        self.cmd = call
        self.execute_export()

    def download_segs(self):
        show = f"[{self.data['show']}]" if self.data.get("show") else ""
        self.data["format"] = self.data.get("format") or self.data["ext"]
        self.data["filename"] = f"{self.data['title']}{show}.{self.data['format']}"
        self.data["path"] = f"{self.data['dir']}/{self.data['filename']}"

        if self.data.get("capture"):
            if len(self.data["streams"]["segs"]) == 1:
                self.data["target"] = self.data["streams"]["segs"][0]["url"]
                self.download_format()
            else:
                self.data["target"] = self.data["streams"][self.data["playback"]]
                self.download_format()

            return
        if Path(self.data["path"]).exists():
            self.data["filename"] = self.data["filename"]
            print(f'Exists: {self.data["path"]}', end="")
            return
        self.data["text"] = []
        reload = self.data["extra"].get("reload", 0)

        for k, v in enumerate(self.data["streams"]["segs"]):
            filename = f"{self.data['title']}{show}_{k}.{self.data['ext']}"
            self.data["threading"].append(
                {"filename": filename, "idx": k + 1, "target": v["url"]}
            )
            self.data["text"].append(f"{self.data['dir']}/{filename}")

        self.download_multi()
        # 单段视频,如果指定格式与原本格式一致,跳过FFMPEG转码
        if len(self.data["streams"]["segs"]) == 1 and self.data["ext"] == self.data.get(
            "format"
        ):
            os.rename(f"{self.data['dir']}/{filename}", self.data["path"])
        else:
            self.download_merge()

        print("\r")

    def download_multi(self):
        """
        多线程分段下载
        指定获取self.data["threading"]
        列表子对象dict{'target':'','idx':'','filename':''}
        target:分段链接
        idx:分段编号
        filename:分段存储名

        :param self:
        :return:
        """

        self.data["idxs"] = len(self.data["threading"])
        execute_md5 = []

        for nn in range(100):

            if self.data["ext"] == "m3u8":
                for i in self.data.get("text"):
                    if Path(f"{i}_temp").exists():
                        os.remove(Path(f"{i}_temp"))
                time.sleep(1)
            if nn > 0 and len(execute_md5) < 1:
                break

            threads = []
            # signal.signal(signal.SIGINT, execute_handler)
            # just = len(threading.enumerate())

            if self.data["extra"].get("retry") and nn > 0:
                try:
                    retry = self.imp.parse(self, self.data)
                    self.data = {**self.data, **retry}
                except:
                    pass

            for v in self.data["threading"]:
                if len(execute_md5) > 0:
                    # 网络原因未下载到的分段,在这边会重新加到线程下载
                    if self.md5(v["filename"]) in execute_md5:
                        if self.data["extra"].get("reload"):
                            try:
                                self.data["extra"]["idx"] = v["idx"]
                                self.imp.reload(self)
                                v["target"] = self.data["streams"]["segs"][
                                    v["idx"] - 1
                                ]["url"]
                                r = "\r[%s / %d] |- %s -|  " % (
                                    v["idx"],
                                    self.data.get("idxs", 1),
                                    "reloading",
                                )
                                print("\r{}".format(r), end="")
                            except:
                                pass

                        t = threading.Thread(
                            target=self.download_file,
                            args=(v["target"], v["filename"], v["idx"]),
                        )
                        threads.append(t)

                else:
                    t = threading.Thread(
                        target=self.download_file,
                        args=(v["target"], v["filename"], v["idx"]),
                    )
                    threads.append(t)

            for t in threads:
                t.setDaemon(True)
                t.start()
                num = self.data["multi"]
                if self.data["extra"].get("multi"):
                    num = min(num, self.data["extra"]["multi"])

                while True:
                    if len(threading.enumerate()) <= num:
                        break
            for t in threads:
                t.join()

            #
            # for t in threads:
            #     t.setDaemon(True)
            #     t.start()
            #     num = min(len(threads), self.data["multi"])
            #     while True:
            #         if len(threading.enumerate()) <= num:
            #             break
            # try:
            #
            #     while threads:
            #         for t in threads:
            #             if not t.isAlive():
            #                 threads.remove(t)
            #         time.sleep(0.1)
            # except:
            #     pass

            # threading.BoundedSemaphore(self.data["multi"])
            # for t in threads:
            #     t.setDaemon(True)
            #     t.start()
            #     while True:
            #         if len(threading.enumerate()) <= self.data["multi"]:
            #             break
            #
            # while True:
            #     lock = 0
            #     if len(threading.enumerate()) > just:
            #         lock = 1
            #     if lock:
            #         time.sleep(0.1)
            #     else:
            #         break

            # 获取文件夹中已下载的分段,网络原因导致未下载的分段,循环后重新下载
            # 检查文件名md5,避免文件名包含特殊字符串,正则匹配错误
            time.sleep(0.5)
            files = os.listdir(str(self.data["dir"]))
            files_md5 = [self.md5(i) for i in files]

            execute_md5 = [self.md5(i["filename"]) for i in self.data["threading"]]
            for i in files_md5:
                if i in execute_md5:
                    execute_md5.remove(i)

            if len(execute_md5) < 1:
                break

    def download_file(self, target="", filename="", idx=""):

        """
        :param self:
        :param target: 下载文件链接
        :param filename: 下载文件名
        :param idx: 下载文件编号
        :return:
        """
        target = target or self.data.get("target")
        filename = filename or self.data.get("filename")
        idx = idx or self.data.get("idx", 1)
        if self.data.get("idxs"):
            n = str(idx).zfill(len(str(self.data["idxs"])))
        else:
            n = 1
        path = f'{self.data["dir"]}/{filename}'
        file = Path(path)
        tempname = f"{filename}_temp"
        temp = Path(f"{path}_temp")

        if file.exists():
            r = "\r[%s / %d] |- %s -|  " % (
                n,
                self.data.get("idxs", 1),
                "finish",
            )
            print("\r{}".format(r), end="")
            return
        elif temp.exists():
            temp_size = temp.stat().st_size
        else:
            temp_size = 0

        headers = self.data["extra"]["headers"].copy()
        headers["Range"] = f"bytes={temp_size}-"
        if self.proxy == "ignore":
            proxies = {"http": None, "https": None}
        elif self.proxy:
            if self.proxy.startswith("socks"):
                self.execute_proxy(self.proxy)
                proxies = None
            else:
                proxies = {"http": self.proxy, "https": self.proxy}
        else:
            proxies = None

        try:
            response = requests.get(
                target, stream=True, headers=headers, proxies=proxies
            )
        except:
            try:
                response = requests.get(
                    target, stream=True, headers=headers, proxies=proxies
                )
            except:
                r = "\r[%s / %d] |- %s -|  " % (
                    n,
                    self.data.get("idxs", 1),
                    "ConnectionError",
                )
                print("\r{}".format(r), end="")
                return

        try:
            # 文件剩余大小
            total_size = int(response.headers["Content-Length"])
        except:
            r = "\r[%s / %d] |- %s -|  " % (
                n,
                self.data.get("idxs", 1),
                "contentLengthError",
            )
            print("\r{}".format(r), end="")
            return

        # 文件大小
        if "Content-Range" in response.headers:
            content_range = int(response.headers["Content-Range"].split("/")[1])
        else:
            content_range = total_size

        if content_range == 0:
            return
        # if temp_size > content_range:
        #     os.remove(temp)
        #     temp_size = 0
        # 下载初始时间,参数
        st = time.time()
        start = time.perf_counter()
        temp_data = temp_size

        with open(temp, "ab") as fp:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    mt = time.time()
                    if mt - st > 0.1:
                        speed = (temp_size - temp_data) / 1024 / (mt - st)
                        if speed < 10 and self.data["extra"].get("reload"):
                            return
                        temp_data = temp_size
                        st = mt
                        rate = temp_size / content_range
                        number = int(self.block * rate)
                        r = "\r[%s / %d] |-%s%s-|%d%%  %skb/s %sM/%sM " % (
                            n,
                            self.data.get("idxs", 1),
                            "█" * number,
                            "-" * (self.block - number),
                            int(rate * 100),
                            "%.2f" % speed,
                            "%.2f" % (temp_size / 1024 / 1024),
                            "%.2f" % (content_range / 1024 / 1024),
                        )
                        if self.data.get("download"):
                            print("\r{}".format(r), end="")
                    fp.write(chunk)

        # print("\r")
        # 判断下载文件有效性,多线程m3u8切片太多错误,暂停使用
        if self.data["ext"] == "m3uq8":
            os.rename(temp, path)
        else:
            if os.path.getsize(temp) != 0 and os.path.getsize(temp) == content_range:
                os.rename(temp, path)
            else:
                os.remove(temp)
                time.sleep(0.5)
                return
                # self.retry += 1
                # if self.retry < 10:
                #     os.remove(temp)
                #     # self.retry = 0
                # else:
                #     r = "\r[%s / %d] |- %s -|  " % (
                #         n,
                #         self.data.get("idxs", 1),
                #         "错误过多",
                #     )
                #     print("\r{}".format(r), end="")
                #     return
        # 输出平均速度
        end = time.perf_counter()
        velocity = total_size / 1024 / (end - start)
        r = "\r[%s / %d] |-%s-|%d%%  %skb/s %sM/%sM " % (
            n,
            self.data.get("idxs", 1),
            "█" * self.block,
            100,
            "%.2f" % velocity,
            "%.2f" % (content_range / 1024 / 1024),
            "%.2f" % (content_range / 1024 / 1024),
        )
        print("\r{}".format(r), end="")

    def download_merge(self):
        """
        分段合并
        合并完成后,将删除所有切片或分段
        :param self:
        :return:
        """

        if self.data.get("text"):
            error = 0
            for i in self.data["text"]:
                if not Path(i).exists():
                    error = 1
            if error:
                self.download_multi()
        print(f"\nMerging: video {self.data['filename']} using ffmpeg\n")
        txt = Path(f"{self.data['dir']}/{int(time.time())}.txt")

        with open(str(txt), "w") as fp:
            fp.write("\n".join(["file '{}'".format(i) for i in self.data["text"]]))
        fp.close()
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-safe",
            "0",
            "-y",
            "-f",
            "concat",
            "-i",
            str(txt),
            "-c",
            "copy",
        ]
        if self.data.get("format") in ["mp4"]:
            cmd.extend(["-bsf:a", "aac_adtstoasc"])

        cmd.extend([self.data["path"]])

        try:
            subprocess.call(
                cmd,
                env=self.env,
            )
            for i in self.data["text"]:
                try:
                    os.remove(i)
                except:
                    pass
            os.remove(txt)
        except:
            logging.error("ffmpeg error!")

    def download_m3u8(self):
        """
        m3u8下载
        playback必须为m3u8
        :param self:
        :return:
        """
        show = f"[{self.data['show']}]" if self.data.get("show") else ""
        self.data["format"] = self.data.get("format", "mp4")
        # ext = "mp4"
        self.data["filename"] = f"{self.data['title']}{show}.{self.data['format']}"
        self.data["path"] = f"{self.data['dir']}/{self.data['filename']}"
        url = self.data["streams"][self.data["ext"]]

        print(f"M3U8: {url}")

        if self.data.get("capture"):
            self.data["target"] = url
            self.download_format()
            return

        if Path(self.data["path"]).exists():
            self.data["filename"] = self.data["filename"]
            print(f'Exists: {self.data["path"]}', end="")
            return

        if (
            Path(f"{self.data['dir']}/{self.data['title']}{show}.mp4")
            and self.data["format"] != "mp4"
        ):
            self.data["input"] = f"{self.data['dir']}/{self.data['title']}{show}.mp4"
            self.download_ffmpeg()
            return

        try:
            html = self.curl({"url": url, "headers": self.data["extra"]["headers"]})

        except:
            try:
                html = self.curl({"url": url, "headers": self.data["extra"]["headers"]})
            except:
                sys.exit("M3u8UrlError")

        if self.data["extra"].get("replace"):
            html = self.replace(
                self.data["extra"]["replace"][0],
                self.data["extra"]["replace"][1],
                html,
            )
        lists = self.matchAll(
            "\#(?:EXTINF|extinf):([^,]+),\s*\r*\n*([^\r|\n|\s]+)", html
        )

        assert lists, "M3u8Error"

        self.data["idxs"] = len(lists)
        ts_lists = [k[1] for k in lists]
        # 如果ts分段非http开头
        url_path = url.rsplit("/", 1)[0] + "/"
        if not ts_lists[0].startswith("http"):
            ts_lists = [f"{url_path}{k}" for k in ts_lists]
        self.data["text"] = []

        for k, v in enumerate(ts_lists):
            filename = f"{self.data['title']}{show}_{k}.ts"
            self.data["threading"].append(
                {
                    "filename": filename,
                    "target": v,
                    "idx": k + 1,
                }
            )
            self.data["text"].append(f"{self.data['dir']}/{filename}")
        self.download_multi()
        self.download_merge()

    def download_ffmpeg(self):
        cmd = [
            "ffmpeg",
            "-i",
            self.data["input"],
            "-vcodec",
            "copy",
            "-acodec",
            "copy",
        ]
        if self.data.get("format") in ["mp4"]:
            cmd.extend(["-bsf:a", "aac_adtstoasc"])

        cmd.extend([self.data["path"]])
        try:
            subprocess.call(
                cmd,
                env=self.env,
            )

        except:
            logging.error("ffmpeg error!")

    def download_live(self):
        """
        直播下载,直接使用ffmpeg录制
        :param self:
        :return:
        """
        show = f"[{self.data['show']}]" if self.data.get("show") else ""

        if self.data["ext"] == "hls":
            ext = self.data.get("format") or "mp4"
            self.data["target"] = self.data["streams"]["m3u8"]
            self.data["filename"] = f"{self.data['title']}{show}.{ext}"

        else:
            ext = self.data.get("format") or self.data["ext"]
            rtime = time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())
            self.data["target"] = self.data["streams"][self.data["ext"]]
            self.data["filename"] = (
                f"{self.data['title']} - {self.data['anchor']}{show} - {rtime}.{ext}"
                if self.data.get("anchor")
                else f"{self.data['title']}{show} - {rtime}.{ext}"
            )
        self.data["path"] = f"{self.data['dir']}/{self.data['filename']}"

        if Path(self.data["path"]).exists():
            pass
            # sys.exit("已下载")

        headers = []
        if self.data["extra"].get("headers"):
            for k, v in self.data["extra"]["headers"].items():
                headers.append("-headers")
                headers.append(f"{k}:{v}")

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-protocol_whitelist",
            "file,http,https,tls,rtp,tcp,udp,crypto,httpproxy",
        ]
        if headers:
            cmd.extend(
                [
                    "-user_agent",
                    self.data["extra"]["headers"].get("User-Agent")
                    or self.data["extra"]["headers"].get("user-agent"),
                ]
            )
            cmd.extend(headers)
        cmd.extend(["-i", self.data["target"]])
        cmd.extend(
            [
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                "-bsf:a",
                "aac_adtstoasc",
                self.data["path"],
            ]
        )
        self.cmd = cmd
        self.execute_export()

    def download_youtube(self):
        """
        Youtube下载
        全局变量itag:当以a:b形式时,a和b不允许同时为video或audio,下载后自动ffmpeg合并
            当以a(,b(,c))形式存在时,将会下载a(b(c))分段
            当为video或者audio时,会下载所有itag为video或者audio的分段
            当为all时,会下载所有itag
        不存在全局变量itag,将下载指定分辨率的mp4资源
        :param self:
        :return:
        """

        if self.data.get("itag"):
            if ":" in self.data["itag"] or self.data["itag"] in ["large"]:
                lists = self.column(self.data["extra"]["adaptive"], "", "itag")
                if self.data["itag"] in ["large"]:
                    itags = []
                    lar = {"video": {}, "audio": {}}
                    for kk, vv in lists.items():
                        if "video" in vv["mimeType"] and "avc1" in vv["mimeType"]:
                            lar["video"][int(vv["contentLength"])] = kk
                        elif "audio/webm" in vv["mimeType"]:
                            lar["audio"][int(vv["contentLength"])] = kk
                    itags.append(lar["video"][sorted(lar["video"].keys())[-1]])
                    itags.append(lar["audio"][sorted(lar["audio"].keys())[-1]])
                else:
                    itags = self.data["itag"].split(":")
                print("Itag:", itags)
                cmd = ["ffmpeg", "-hide_banner"]
                self.data["idxs"] = 2
                audio = video = ""
                for k, v in enumerate(itags):
                    info = lists[int(v)]
                    mtype = self.match("(\w+)\/(\w+)", info["mimeType"])
                    filename = f"{self.data['title']}_itag_{v}.{mtype[1]}"
                    self.data["output"].append(filename)
                    if mtype[0] == "audio":
                        audio = v
                    else:
                        video = v

                    self.data["threading"].append(
                        {
                            "filename": filename,
                            "target": info["url"],
                            "idx": k + 1,
                            "ext": mtype[1],
                        }
                    )

                assert audio and video, "video or audio"

                if self.data.get("capture"):
                    timelength = self.data.get("length")
                    start = self.seconds(self.data["start"])
                    end = self.seconds(self.data["end"]) if self.data.get("end") else ""

                    if timelength:
                        t = f"[{self.data['start']}-{timelength}]"
                    else:
                        t = (
                            f"[{self.data['start']}x{self.data['end']}]"
                            if end
                            else f"[{start}]"
                        )

                    self.data["output"] = []
                    # 实验性,用ffmpeg录制itag片段
                    ext = self.data.get("format") or "mp4"

                    merge_name = f"{self.data['title']}_merge_{video}_{audio}{t}.{ext}"

                    if Path(f'{self.data["dir"]}/{merge_name}').exists():
                        print("File exists skip Download!")
                    else:
                        for i in self.data["threading"]:
                            self.data["target"] = i["target"]
                            self.data["filename"] = i["filename"]
                            self.data["format"] = i["ext"]

                            self.download_format()
                        del self.data["target"]
                        merge_name = f"{self.data['title']}_merge_{video}_{audio}{self.data['substr']}.{ext}"

                    self.data["format"] = ext
                    for i in self.data["output"]:
                        cmd.extend(["-i", f'{self.data["dir"]}/{i}'])

                else:
                    merge_name = f"{self.data['title']}_merge_{video}_{audio}.{self.data.get('format', 'mp4')}"
                    if Path(f"{self.data['dir']}/{merge_name}").exists():
                        print("File exists skip Download!")
                    else:
                        self.download_multi()
                    for i in self.data["threading"]:
                        cmd.extend(["-i", f'{self.data["dir"]}/{i["filename"]}'])

                self.data["filename"] = merge_name

                cmd.extend(
                    [
                        "-strict",
                        "-2",
                        "-acodec",
                        "copy",
                        "-vcodec",
                        "copy",
                        f"{self.data['dir']}/{merge_name}",
                    ]
                )

                if not Path(f"{self.data['dir']}/{merge_name}").exists():

                    subprocess.call(
                        cmd,
                        env=self.env,
                    )
                    if self.data.get("capture"):
                        # if True:
                        for i in self.data["output"]:
                            try:
                                os.remove(Path(f'{self.data["dir"]}/{i}'))
                            except:
                                pass
                else:
                    print("ffmpeg ok!")
            else:

                lists = self.column(self.data["extra"]["adaptive"], "", "itag")

                if self.data["itag"] == "all":
                    itags = list(lists.keys())
                elif self.data["itag"] == "audio":
                    itags = [i for i in lists if "audio" in lists[i]["mimeType"]]
                elif self.data["itag"] == "video":
                    itags = [i for i in lists if "video" in lists[i]["mimeType"]]
                else:
                    itags = self.data["itag"].split(",")

                self.data["idxs"] = len(itags)
                for k, v in enumerate(itags):
                    try:
                        info = lists[int(v)]
                        mtype = self.match("(\w+)\/(\w+)", info["mimeType"])
                        self.data["threading"].append(
                            {
                                "filename": f"{self.data['title']}_itag_{v}.{mtype[1]}",
                                "target": info["url"],
                                "idx": k + 1,
                            }
                        )
                    except:
                        pass

                self.download_multi(self)

        else:
            show = f"[{self.data['show']}]" if self.data.get("show") else ""
            self.data["filename"] = f"{self.data['title']}{show}.{self.data['ext']}"
            self.data["target"] = self.data["streams"][self.data["ext"]]
            self.data["path"] = f"{self.data['dir']}/{self.data['filename']}"
            self.download_file()

    def download_format(self):
        """
        视频转码或截取视频片段
        :param self:
        :return:
        """
        start = end = change = temp = ""
        timelength = self.data.get("length")
        self.data["format"] = self.data.get("format") or "mp4"
        if self.data.get("start"):
            start = self.seconds(self.data["start"])
            end = self.seconds(self.data["end"]) if self.data.get("end") else ""

            if timelength:
                t = f"[{self.data['start']}-{timelength}]"
            else:
                t = (
                    f"[{self.data['start']}x{self.data['end']}]"
                    if end
                    else f"[{start}]"
                )
            # 设置文件名
            output = self.sub(
                ".(\w+)$", f"{t}.{self.data['format']}", self.data["filename"]
            )
            self.data["output"].append(output)
            self.data["substr"] = t
        else:
            output = self.sub(
                ".(\w+)$", f".{self.data['format']}", self.data["filename"]
            )

        if not Path(f"{self.data['dir']}/{output}").exists():

            if self.data.get("capture"):
                cmd = [
                    "ffmpeg",
                    "-hide_banner",
                    "-user_agent",
                    self.data["extra"]["headers"].get("User-Agent")
                    or self.data["extra"]["headers"].get("user-agent"),
                    "-protocol_whitelist",
                    "file,http,https,tls,rtp,tcp,udp,crypto,httpproxy",
                ]
                # M3U8内容替换
                if self.data["playback"] == "m3u8" and self.data["extra"].get(
                    "replace"
                ):
                    try:
                        html = self.curl(
                            {
                                "url": self.data["target"],
                                "headers": self.data["extra"]["headers"],
                            }
                        )

                        html = self.replace(
                            self.data["extra"]["replace"][0],
                            self.data["extra"]["replace"][1],
                            html,
                        )
                        temp = f"{self.data['dir']}/{int(time.time())}-{self.data['vid']}-{self.data['type']}.m3u8"
                        with open(temp, "w") as fp:
                            fp.write(html)
                        fp.close()
                        change = self.data["target"]
                        self.data["target"] = temp
                        cmd = [
                            "ffmpeg",
                            "-hide_banner",
                            "-protocol_whitelist",
                            "file,http,https,tls,rtp,tcp,udp,crypto,httpproxy",
                        ]

                    except:
                        pass

                else:
                    headers = []
                    for k, v in self.data["extra"]["headers"].items():
                        headers.append("-headers")
                        headers.append(f"{k}:{v}")

                    cmd.extend(headers)

                cmd.extend(["-i", self.data["target"]])

                if self.data.get("format") == "mp4":
                    cmd.extend(["-bsf:a", "aac_adtstoasc"])

            else:
                cmd = [
                    "ffmpeg",
                    "-i",
                    f"{self.data['dir']}/{self.data['filename']}",
                    "-strict",
                    "-2",
                ]

            if start:
                cmd.extend(["-ss", str(start)])

                if timelength:
                    cmd.extend(["-t", str(timelength)])
                elif end:
                    cmd.extend(["-to", str(end)])

                cmd.extend(["-c", "copy"])

            cmd.append(f"{self.data['dir']}/{output}")

            print(f"\r视频转码中")
            self.cmd = cmd
            call = self.execute_export()

            if temp:
                os.remove(Path(temp))
                self.data["target"] = change
        else:
            print(f"\r视频转码完成")
