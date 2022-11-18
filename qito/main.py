#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
@File    : main.py
@Time    : 2022/2/13 下午6:14  
"""
import time, importlib, os, re, logging, sys, requests
from pathlib import Path

from util import common


class Parse(common.Common):
    def __init__(self, params):
        super().__init__()
        self.abspath = os.path.abspath(os.path.dirname(__file__))
        self.cwd = os.getcwd()
        if params.get("debug"):
            logging.basicConfig(
                format="%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s",
                level=logging.DEBUG,
            )

            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("chardet").setLevel(logging.WARNING)
        else:
            logging.basicConfig(
                format="%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s",
                level=logging.WARNING,
            )

        self.configuration()
        if params["parse"] == "config":
            if not Path(f"{self.abspath}/config/config.py").exists():
                content = 'iniPath=""\nfilePath=""'
                self.write(f"{self.abspath}/config/config.py", content)
                print("Created: config.py created successfully")
            else:
                print("Exists: config.py already exists")

            from config import config

            if params.get("iniPath"):
                config.iniPath = params["iniPath"]
            if params.get("filePath"):
                config.filePath = params["filePath"]

            content = "\n".join(
                [
                    f'{i}="{getattr(config, i, None)}"'
                    for i in [e for e in dir(config) if not e.startswith("_")]
                ]
            )
            self.write(f"{self.abspath}/config/config.py", content)
        elif params["parse"] == "upgrade":
            try:
                file = self.abspath + "/qito-main.zip"
                print(
                    "Downloading github package [https://github.com/qitoqito/qito/archive/refs/heads/main.zip]..."
                )
                r = requests.get(
                    "https://github.com/qitoqito/qito/archive/refs/heads/main.zip"
                )

                with open(file, "wb") as f:
                    f.write(r.content)
                    f.close()

            except:
                pass

            if os.path.exists(file):
                import zipfile
                import shutil

                zip = zipfile.ZipFile(file)
                print("The zip download is complete and will be unzipped soon...")
                for name in zip.namelist():
                    zip.extract(name, self.abspath)

                print("Moving files ...")
                if sys.version_info < (3, 8):
                    shutil.copytree(
                        self.abspath + "/qito-main/qito",
                        self.abspath,
                    )
                else:
                    shutil.copytree(
                        self.abspath + "/qito-main/qito",
                        self.abspath,
                        dirs_exist_ok=True,
                    )
            else:
                print("Download failed...")

        elif params["parse"] == "ini":
            pass
        elif params.get("playlist"):
            self.playList(params)
        else:
            self.working(params)

    def configuration(self):
        self.getConfig("config")
        self.getConfig("profile")
        self.getConfig("user")
        if self.get("iniPath"):
            ini = self.parseIni(f"{self.iniPath}/config.ini")
        else:
            ini = self.parseIni(f"{self.abspath}/ini/config.ini")

    def working(self, params):
        params["category"] = params.get("category") or self.get("category") or "video"
        params["hd"] = params.get("hd") or self.get("hd") or 6
        params["parse"] = str(params["parse"])
        if self.hasurl(params["parse"]):
            site = self.domain(params["parse"])
            if site in self.prepare_location():
                params["parse"] = self.curl(
                    {
                        "url": params["parse"],
                        "response": "location",
                    }
                )
            type = self.prepare_change(site)

            for k, v in self.prepare_category().items():
                if site in v:
                    if self.match(v[site], params["parse"]):
                        params["category"] = k
                        break
                else:
                    for k1, v1 in v.items():
                        if self.match(v1, params["parse"]):
                            type = k1
                            params["category"] = k
                            site = k1
                            break

        else:
            site = params["type"]

            type = self.prepare_change(site)

        if self.get("site") and site in self.siteChange.keys():
            type = self.siteChange[site]

        params["site"] = site
        params["type"] = type
        try:
            imp = importlib.import_module(f"parse.{params['category']}.{type}")
            self.imp = imp
            a = imp.Main()

            a.init(params)
        except ModuleNotFoundError as e:
            print(f'The parsing of {params["category"]}.{params["site"]} is not supported...')
        except ValueError as e:
            print(e)

        except KeyboardInterrupt:
            # ctrl + c 终止运行
            print("\r\n")
            logging.warning("End Process")
            sys.exit()

    def playList(self, params):
        domain = self.match(r"(\w+(?:-\w+)*).\w+\/", params["parse"])

        type = params.get("type") or domain
        category = params.get("category") or "video"
        # try:

        try:
            imp = importlib.import_module(f"parse.playlist.{type}")
            a = imp.Main()
            data = getattr(a, f"{category}List")(params)
            assert len(data["data"]) > 0, "lists"
            params["category"] = data.get("category")
            params["type"] = data.get("type")

            if params.get("choose"):
                params["choose"] = str(params["choose"])
                if ":" in params["choose"]:
                    spl = [i for i in params["choose"].split(":") if i]
                    start = int(spl[0]) - 1

                    if len(spl) > 1:
                        parseLists = data["data"][start : int(spl[1])]
                    else:
                        parseLists = data["data"][start:]

                else:
                    spl = params["choose"].split(",")
                    parseLists = []
                    for i in spl:
                        try:
                            parseLists.append(data["data"][int(i) - 1])
                        except:
                            pass
            else:
                parseLists = data["data"]

        except:
            parseLists = [params["parse"]]
        for i in parseLists:
            if isinstance(i, dict):
                params = {**params, **i}
            else:
                params["parse"] = i

            self.working(params)
        # except:
        #     pass
