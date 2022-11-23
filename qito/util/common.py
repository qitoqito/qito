#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : common.py
@Time    : 2021/10/19 下午4:51  
"""

import re, requests, json, base64, time, hashlib, urllib, logging, os, logging, importlib, urllib3, random, execjs

from util import prepare, execute


class Common(execute.Execute, prepare.Prepare):
    def __init__(self):
        self.n = 0
        self.log = 1
        self.message = []
        self.path = os.path.abspath(os.path.dirname(__file__))
        self.cwd = os.getcwd()
        self.time = time.time()
        self.options = {"header": {}}
        self.modules = {}
        self.env = None
        self.time = int(time.time())
        self.timestamp = int(round(self.time * 1000))
        self.logging = logging
        self.urlParse = urllib.parse

    def set(self, k, v):
        setattr(self, k, v)

    def get(self, key):
        return getattr(self, key, None)

    def include(self):
        for i in self.require:
            try:
                if type(i) == tuple:
                    try:
                        m = importlib.import_module(f"{i[0]}.{i[1]}")
                        name = i[2] if len(i) == 3 else i[1]
                        self.modules[name] = m
                    except:
                        m = importlib.import_module(i[0])

                        if type(i[1]) in [tuple, list]:
                            for j in i[1]:
                                self.modules[j] = getattr(m, j)
                        else:
                            name = i[2] if len(i) == 3 else i[1]
                            self.modules[name] = getattr(m, i[1])

                else:
                    self.modules[i] = importlib.import_module(f"util.{i}")
            except:
                try:
                    self.modules[i] = importlib.import_module(i)
                except:
                    pass

    def haskey(self, data, key, value="", message=""):
        """
        判断多维数组data中有没有指定key键,或者键值是否与value一致
        :param data:
        :param key:
        :param value:
        :return:
        """
        for i in key.split("."):
            i = int(i) if i.isdigit() else i
            try:
                # data=data.get(i)
                data = data[i]
            except:
                if message:
                    raise AttributeError(message)
                else:
                    return ""
        if value:
            data = True if value == data else False
        return data

    def hasurl(self, link):
        """
        判断是不是url
        :param link:
        :return: true or false
        """
        return link.lower().startswith("http")

    def curl(self, params):
        data = ""
        json = ""
        if isinstance(params, str):
            params = {"url": params}
        response = params.get("response", None)
        method = params.get("method")
        module = requests.post if method == "post" else requests.get
        if params.get("form"):
            module = requests.post
            data = params["form"]
        elif params.get("json"):
            module = requests.post
            json = params["json"]
        verify = True if params.get("verify") else False
        if not verify:
            requests.packages.urllib3.disable_warnings()
        if self.get("proxy"):
            proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
        else:
            proxies = {}
        if params.get("headers"):
            headers = params["headers"]
        elif self.get("headers"):
            headers = self.headers
        else:
            headers = {}
        if (
            self.get("cookie")
            and not headers.get("Cookie")
            and not headers.get("cookie")
        ):
            if type(self.cookie) == dict:
                self.cookie = ";".join(
                    [" " + k + "=" + str(v) for k, v in self.cookie.items()]
                ).strip()
            headers["Cookie"] = self.cookie
        elif params.get("cookie"):
            if type(params["cookie"]) == dict:
                params["cookie"] = ";".join(
                    [" " + k + "=" + str(v) for k, v in params["cookie"].items()]
                ).strip()
            headers["Cookie"] = params["cookie"]

        if params.get("ua"):
            if params["ua"] == "ios":
                headers[
                    "User-Agent"
                ] = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/74.0.3729.155 Mobile/15E148 Safari/604.1"
            elif params["ua"] == "android":
                headers[
                    "User-Agent"
                ] = "Mozilla/5.0 (Linux; Android 9; Mi A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36"
            elif params["ua"] == "pc":
                headers[
                    "User-Agent"
                ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:67.0) Gecko/20100101 Firefox/67.0"
            if params["ua"] == "wechat":
                headers[
                    "User-Agent"
                ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) MicroMessenger/2.3.25(0x12031910) MacWechat Chrome/39.0.2171.95 Safari/537.36 NetType/WIFI WindowsWechat"
            else:
                headers["User-Agent"] = params["ua"]
        if not headers.get("user-agent") or not headers.get("User-Agent"):
            headers[
                "User-Agent"
            ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        if params.get("referer"):
            headers["Referer"] = params["referer"]
        args = dict(
            proxies=proxies,
            headers=headers,
            verify=False,
            timeout=params.get("timeout", 3000),
            params=params.get("params"),
        )
        if self.get("debug"):
            self.logging.debug(f"getUrl: {params['url']}")
            if data:
                self.logging.debug(f"reqData: ${self.dumps(data)}")
            if json:
                self.logging.debug(f"reqJson: ${self.dumps(json)}")
        if data:
            args["data"] = data
        elif json:
            args["json"] = json
        if response == "location":
            c = requests.head(
                params["url"],
                **args,
            )
            if c.headers.get("location"):
                location = c.headers["location"]

            else:
                d = module(params["url"], **args)
                location = d.url or params["url"]
            return location

        elif response == "cookie":
            c = module(params["url"], **args)
            return c.cookies.get_dict()
        elif response == "response":
            html = {}
            c = module(params["url"], **args)
            if params.get("decoding"):
                c.decoding = params["decoding"]
            elif params.get("encoding"):
                c.encoding = params["encoding"]
            if params.get("nobody"):
                html["content"] = ""
            else:
                if params.get("decoding"):
                    c.decoding = params["decoding"]
                elif params.get("encoding"):
                    c.encoding = params["encoding"]

                html["content"] = c.text
            co = c.cookies.get_dict()

            if not co and c.headers.get("Set-Cookie"):
                d = self.replace(["; ", ", "], "&", c.headers["Set-Cookie"])
                co = dict(urllib.parse.parse_qsl(d))
                try:
                    del co["path"]
                    del co["expires"]
                except:
                    pass

            html["cookie"] = co

            html["headers"] = dict(c.headers)
            return html
        else:
            c = module(params["url"], **args)
            if params.get("decoding"):
                c.decoding = params["decoding"]
            elif params.get("encoding"):
                c.encoding = params["encoding"]
            if response == "json":
                return c.json()
            else:
                return c.text

    def match(self, pattern, string, flags=0):
        """
        正则获取,只取一组数据
        :param pattern:
        :param string:
        :param flags:
        :return:
        """
        if flags == "S":
            flags = re.S
        elif flags == "I":
            flags = re.I
        elif flags == "L":
            flags = re.L
        elif flags == "M":
            flags = re.M
        elif flags == "U":
            flags = re.U
        elif flags == "X":
            flags = re.X
        else:
            flags = 0
        if not isinstance(pattern, list):
            pattern = [pattern]

        for m in pattern:
            try:
                fin = re.search(m, string, flags)
            except TypeError:
                fin = re.search(m, str(string), flags)
            if fin:
                if len(fin.groups()) > 1:
                    r = fin.groups()
                else:
                    try:
                        r = fin.group(1)
                    except:
                        r = fin.group(0)
                return r

        return ""

    def matchAll(self, pattern, string, flags=0):
        """
        正则匹配,获取全部数据
        :param pattern:
        :param string:
        :param flags:
        :return:
        """
        if flags == "S":
            flags = re.S
        elif flags == "I":
            flags = re.I
        elif flags == "L":
            flags = re.L
        elif flags == "M":
            flags = re.M
        elif flags == "U":
            flags = re.U
        elif flags == "X":
            flags = re.X
        else:
            flags = 0
        if not isinstance(pattern, list):
            pattern = [pattern]
        for m in pattern:
            try:
                fin = re.findall(m, string, flags)
            except TypeError:
                fin = re.findall(m, str(string), flags)
            if fin:
                return fin
        return []

    def loads(self, string):
        return json.loads(string)

    def dumps(self, lists, ensure=1):
        return json.dumps(lists, ensure_ascii=ensure)

    def data(self, params, n, key=""):
        """
        排序数组,获取相关键(n-1)的值
        :param params:
        :param n:
        :param key:
        :return:
        """
        num = int(n)
        length = len(params)
        if isinstance(params, dict):
            params = list(params.values())
        else:
            params = list(params)
        if num > length:
            array = [""] * (num - length)
            array.extend(params)
            params = array
        return params[num - 1][key] if key else params[num - 1]

    def domain(self, link):
        """
        获取域名前缀
        :param url:
        :return:
        """
        # v.qq.com
        # qq.com
        # v.qq.com.cn
        # qq-qq.com
        return self.match(["\w+\.(\w+)\.\w+.\w+\/", "(\w+(?:-\w+)*).\w+\/"], link)

    def build(self, s, f="&", t=0):
        if t:
            pass
        else:
            a = urllib.parse.urlencode(s)
            return a.replace(r"&", f)

    def md5(self, string):
        m2 = hashlib.md5()
        m2.update(str(string).encode("utf-8"))
        return m2.hexdigest()

    def sha1(self, string):
        return hashlib.sha1(str(string).encode("utf-8")).hexdigest()

    def sha256(self, string):
        return hashlib.sha256(str(string).encode("utf-8")).hexdigest()

    def column(self, lists, value, key=""):
        """
        参考PHP-column函数,返回数组中指定的一列说明
        :param lists:
        :param value:
        :param key:
        :return:
        """
        lists = lists.values() if type(lists) == dict else lists
        if key:

            try:
                if type(value) == list:
                    ary = {
                        i[key]: {j: i[j] for j in value} if value else i
                        for i in lists
                        if key in i
                    }

                else:
                    ary = {i[key]: i[value] if value else i for i in lists if key in i}
            except:
                ary = {}

        else:
            # ary = [i[value] if value else i for i in lists]
            ary = [i[value] for i in lists if value in i]
        return ary

    def urlencode(self, params):
        return urllib.parse.urlencode(params)

    def strftime(self, format, timestamp=""):
        return time.strftime(format, time.localtime(timestamp))

    def unquote(self, params):
        return urllib.parse.unquote(params)

    def quote(self, params):
        return urllib.parse.quote(params)

    def parseIni(self, iniPath):
        try:
            with open(iniPath) as fileObj:
                contents = fileObj.read()
            text = f"[ENV]{contents}[EOF]"
            dict = {}
            cookies = {}
            self.params = self.get("params") or {"category": ""}
            for i in self.matchAll(r"\[\s*(\w+)\s*\]([^\[]+)", text):
                col = [x for x in i[1].split("\n") if x]
                if "cookie" in i[0]:
                    dict[i[0]] = col
                elif i[0]:
                    dict[i[0]] = {}
                    for k in col:
                        d = self.match(r"(\w+)\s*=\s*([^\n]+)\s*", k)
                        dict[i[0]][d[0]] = d[1]
                else:
                    for k in col:
                        d = self.match(r"(\w+)\s*=\s*([^\n]+)\s*", k)
                        dict[d[0]] = d[1]

            if dict.get(self.params["category"]):
                for k, v in dict[self.params["category"]].items():
                    dict[k] = v
            if dict.get("cookie"):
                if type(dict["cookie"]) is list:
                    dict["cookies"] = dict["cookie"]
                    dict["cookie"] = random.choice(dict["cookies"])
                else:
                    dict["cookies"] = [dict["cookie"]]
            for k, v in dict.items():
                if k == "ENV":
                    for kk, vv in v.items():
                        self.set(kk, vv)
                else:
                    self.set(k, v)
            return dict
        except:
            return {}

    def getConfig(self, name):
        try:
            config = importlib.import_module(f"config.{name}")
            dict = {}
            for i in dir(config):
                if not i.startswith("__"):
                    self.set(i, getattr(config, i))
                    dict[i] = getattr(config, i)
            self.set(f"{name}Space", dict)
        except:
            pass

    def read(self, path, mode="r"):
        fp = open(path, mode)
        data = fp.read()
        fp.close()
        return data

    def write(self, path, data, mode="w"):
        fp = open(path, mode)
        data = fp.write(data)
        fp.close()
        return data

    def replace(self, pattern, repl, string):
        """
        文本替换
        :param pattern:
        :param repl:
        :param string:
        :return:
        """
        if isinstance(pattern, list):
            if isinstance(repl, list):
                for i in range(len(pattern)):
                    string = string.replace(pattern[i], repl[i])
            else:
                for i in range(len(pattern)):
                    string = string.replace(pattern[i], repl)
        else:
            string = string.replace(pattern, repl)
        return string

    def sub(self, pattern, repl, string, count=0, flags=0):
        """
        正则替换
        :param pattern:
        :param repl:
        :param string:
        :param count:
        :param flags:
        :return:
        """
        if isinstance(pattern, list):
            if isinstance(repl, list):
                for i in range(len(pattern)):
                    string = re.sub(pattern[i], repl[i], string, count=0, flags=0)
            else:
                for i in range(len(pattern)):
                    string = re.sub(pattern[i], repl, string, count=0, flags=0)
        else:
            string = re.sub(pattern, repl, string, count=0, flags=0)
        return string

    def jsonParse(self, s):
        try:
            s = json.loads(s)
        except:
            getTry = self.match(
                ["^try\s*\{\s*\n*\s*(\w+)", "^(\w+)\s*\n*\s*\(", "^(\w+\s*=)\s*\{"], s
            )
            if getTry:
                try:
                    s = json.loads(re.match(".*?({.*}).*", s, re.S).group(1))
                except:
                    c = execjs.compile(
                        """
                    function kk() {
                            return %s;
                        }
                        """
                        % s.replace(getTry, "cbData=")
                    )
                    s = c.call("kk")
                # e = quickjs.Function(
                #     "kk",
                #     """
                #     function kk() {
                #         return %s;
                #     }
                #     """
                #     % s.replace(getTry, "cbData="),
                # )
                #
                # s = e()
        return s

    def typeOf(self, variate, extra=""):
        type = None
        if isinstance(variate, int):
            type = "int"
        elif isinstance(variate, str):
            type = "str"
        elif isinstance(variate, float):
            type = "float"
        elif isinstance(variate, list):
            type = "list"
        elif isinstance(variate, tuple):
            type = "tuple"
        elif isinstance(variate, dict):
            type = "dict"
        elif isinstance(variate, set):
            type = "set"
        if extra:
            return type == extra
        else:
            return type

    def seconds(self, tm):
        spl = tm.split(":")
        count = len(spl)
        if count == 1:
            duration = int(tm)

        else:
            if count == 2:
                spl.insert(0, 0)
            try:
                duration = int(spl[0]) * 3600 + int(spl[1]) * 60 + int(spl[2])
            except:
                duration = int(spl[0]) * 3600 + int(spl[1]) * 60 + float(spl[2])

        return duration

    def unique(self, array):
        return list(set(array))

    def getArray(self, name):
        value = self.get(name)
        if value:
            if isinstance(value, list):
                return value
            else:
                return value.split("|")
        else:
            return []

    def b64encode(self, s):
        if not isinstance(s, bytes):
            s = s.encode()
        return bytearray(base64.b64encode(s)).decode()

    def b64decode(self, s, ignore=1):
        str = base64.b64decode(s)
        if ignore and isinstance(str, bytes):
            str = str.decode("utf-8", "ignore")
        return str
