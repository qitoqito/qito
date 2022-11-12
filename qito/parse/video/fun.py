#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : fun.py
@Time    : 2022/10/19 上午9:03  
"""
import template


class Main(template.Template):
    def __init__(self):
        super().__init__()
        self.title = "风行视频(FUN)"
        self.require = ["execjs"]

    def query(self):
        p = self.params
        if p["parse"].startswith("http"):
            url = self.curl({"url": p["parse"], "response": "location"})
            html = self.curl({"url": url, "encoding": "utf-8"})

            vid = self.match('download_pc\s+tool_cli_link.*data-vid="(\d+)"', html)

            if not vid:
                vid = self.match("(\d+)", p["parse"])
            title = self.match(['class="cru-tit" title="([^<]+)"'], html)
            listJson = self.match(["window.list_json\s*=\s*(.*?);"], html)

            if listJson:
                listData = self.loads(listJson.replace("\\\\", "\\"))

                if "title" in listData:
                    image = listData["pic_poster"]
                    tvid = listData["mediaid"]

                else:
                    listJson = self.match(["window.vplayInfo\s*=\s*([^<]+?);"], html)
                    listData = self.loads(listJson.replace("\\\\", "\\"))
                    if "dvideos" in listData:
                        lists = self.column(
                            listData["dvideos"][0]["videos"], "", "videoid"
                        )
                        if int(vid) in lists:
                            data = lists[int(vid)]
                            image = data["still"]

        else:
            vid = p["parse"]
        if not title:
            urls = [
                f"http://api1.fun.tv/ajax/new_playinfo/video/{vid}/",
                f"http://api1.fun.tv/ajax/new_playinfo/gallery/{vid}/?user=funshion&clear=tv",
            ]
            for u in urls:
                html = self.curl({"url": u, "encoding": "utf8"})
                self.logging.debug("getPlayInfo: %s \r\n" % html)
                json = self.loads(html)
                if self.haskey(json, "status", 200) and json["data"]["name_cn"] != "":
                    title = json["data"]["name_cn"]

                    break
        return self.compact()

    def parse(self):
        p = self.params
        timestamp = self.timestamp
        assert p["vid"], "vid"
        vid = p["vid"]
        ary = ["video", "media"]
        data = ""
        for i in ary:
            url = (
                f"http://pv.funshion.com/v7/video/play/?id={vid}&cl=mweb&uc=111&user_id=0&token=&fudid=1490718135a84f1"
                if i == "video"
                else f"http://pm.funshion.com/v7/media/play/?id={vid}&cl=mweb&uc=111&user_id=0&token=&fudid=1490718135a84f1"
            )
            html = self.curl(url)
            data = self.loads(html)
            if data["retcode"] == "200":
                break
        self.logging.debug(f"getVideo: {html} \r\n")
        assert data, "data"
        playlist = []
        for value in data["playlist"]:
            if value["playinfo"][0]["codec"] != "h.265":
                if "isvip" in value["playinfo"][0]:
                    if value["playinfo"][0]["isvip"] != "1":
                        playlist.append(value)

                else:
                    playlist.append(value)
        quality = self.column(playlist, "name")
        lists = self.data(playlist, p["hd"])
        show = lists["name"]
        self.mozecname = self.getMoz(vid)
        self.logging.debug("mozecname: %s \r\n" % self.dumps(self.mozecname))
        try:
            playinfo = self.decodeJs(lists["playinfo"][0])
        except:
            playinfo = self.decodePy(lists["playinfo"][0])
        assert isinstance(playinfo, dict), "javascript"
        size = int(lists["playinfo"][0]["filesize"])
        mp4 = "http://jobsfe.funshion.com/play/v1/mp4/{}.mp4?token={}&vf={}".format(
            playinfo["hashid"],
            self.b64encode(playinfo["token"]),
            lists["playinfo"][0]["vf"],
        )
        # extra = {"remove": 1}
        return self.compact()

    def getMoz(self, vid):

        url = f"http://m.fun.tv/vplay/?vid={vid}"
        html = self.curl({"url": url, "useragent": "ios", "encoding": "utf-8"})
        ary = self.matchAll('src\s*=\s*"(\/[^.]+.js)"', html)
        ecname = []
        try:
            for i in ary:
                source = self.curl(f"http://m.fun.tv{i}")
                js = """ 
                             var mozEcName = [];
                             var e= %(workflow)s ;
                             var f = e.match(/eval\((.*)\)/)[1], h = /document\.mozEcName\.push\(\"(\w+)\"\)/g, g, j, k =  0 ;
                             eval("g= " + f  ); 
                             while ((j = h.exec(g)) != null) {
                                   mozEcName.push(j[1]);
                                   k++;
                               }

                            function moz(){
                                 return mozEcName 
                            } 
                            """ % {
                    "workflow": repr(source)
                }

                ctx = self.modules["execjs"].compile(js)
                ecname.extend(ctx.call("moz"))
        except:
            moz = ""
            for i in ary:
                source = self.curl(f"http://m.fun.tv{i}")
                encrypted = self.match("\}\((.*)\)", source)

                moz += eval("self.js2unpack(" + encrypted)
            ecname = self.matchAll('document.mozEcName.push\("(\w+)"\)', moz)
        return ecname

    def decodeJs(self, obj):
        js = """
        function fun(object, mozecname) {
    function e(e) {
        for (var t = '', i = '0123456789abcdef', o = 0; 3 >= o; o++) t += i.charAt(e >> 8 * o + 4 & 15) + i.charAt(e >> 8 * o & 15);
        return t
    }

    function t(e) {
        for (var t = (e.length + 8 >> 6) + 1, i = new Array(16 * t), o = 0; 16 * t > o; o++) i[o] = 0;
        for (var o = 0; o < e.length; o++) i[o >> 2] |= e.charCodeAt(o) << o % 4 * 8;
        return i[o >> 2] |= 128 << o % 4 * 8,
            i[16 * t - 2] = 8 * e.length,
            i
    }

    function i(e, t) {
        var i = (65535 & e) + (65535 & t),
            o = (e >> 16) + (t >> 16) + (i >> 16);
        return o << 16 | 65535 & i
    }

    function o(e, t) {
        return e << t | e >>> 32 - t
    }

    function n(e, t, n, r, a, s) {
        return i(o(i(i(t, e), i(r, s)), a), n)
    }

    function r(e, t, i, o, r, a, s) {
        return n(t & i | ~t & o, e, t, r, a, s)
    }

    function a(e, t, i, o, r, a, s) {
        return n(t & o | i & ~o, e, t, r, a, s)
    }

    function s(e, t, i, o, r, a, s) {
        return n(t ^ i ^ o, e, t, r, a, s)
    }

    function d(e, t, i, o, r, a, s) {
        return n(i ^ (t | ~o), e, t, r, a, s)
    }

    function l(o) {
        for (var n, l, p, c, h = t(o), u = 1732584193, f = -271733879, v = -1732584194, m = 271733878, y = 0; y < h.length; y += 16) n = u,
            l = f,
            p = v,
            c = m,
            u = r(u, f, v, m, h[y + 0], 7, -680876936),
            m = r(m, u, f, v, h[y + 1], 12, -389564586),
            v = r(v, m, u, f, h[y + 2], 17, 606105819),
            f = r(f, v, m, u, h[y + 3], 22, -1044525330),
            u = r(u, f, v, m, h[y + 4], 7, -176418897),
            m = r(m, u, f, v, h[y + 5], 12, 1200080426),
            v = r(v, m, u, f, h[y + 6], 17, -1473231341),
            f = r(f, v, m, u, h[y + 7], 22, -45705983),
            u = r(u, f, v, m, h[y + 8], 7, 1770035416),
            m = r(m, u, f, v, h[y + 9], 12, -1958414417),
            v = r(v, m, u, f, h[y + 10], 17, -42063),
            f = r(f, v, m, u, h[y + 11], 22, -1990404162),
            u = r(u, f, v, m, h[y + 12], 7, 1804603682),
            m = r(m, u, f, v, h[y + 13], 12, -40341101),
            v = r(v, m, u, f, h[y + 14], 17, -1502002290),
            f = r(f, v, m, u, h[y + 15], 22, 1236535329),
            u = a(u, f, v, m, h[y + 1], 5, -165796510),
            m = a(m, u, f, v, h[y + 6], 9, -1069501632),
            v = a(v, m, u, f, h[y + 11], 14, 643717713),
            f = a(f, v, m, u, h[y + 0], 20, -373897302),
            u = a(u, f, v, m, h[y + 5], 5, -701558691),
            m = a(m, u, f, v, h[y + 10], 9, 38016083),
            v = a(v, m, u, f, h[y + 15], 14, -660478335),
            f = a(f, v, m, u, h[y + 4], 20, -405537848),
            u = a(u, f, v, m, h[y + 9], 5, 568446438),
            m = a(m, u, f, v, h[y + 14], 9, -1019803690),
            v = a(v, m, u, f, h[y + 3], 14, -187363961),
            f = a(f, v, m, u, h[y + 8], 20, 1163531501),
            u = a(u, f, v, m, h[y + 13], 5, -1444681467),
            m = a(m, u, f, v, h[y + 2], 9, -51403784),
            v = a(v, m, u, f, h[y + 7], 14, 1735328473),
            f = a(f, v, m, u, h[y + 12], 20, -1926607734),
            u = s(u, f, v, m, h[y + 5], 4, -378558),
            m = s(m, u, f, v, h[y + 8], 11, -2022574463),
            v = s(v, m, u, f, h[y + 11], 16, 1839030562),
            f = s(f, v, m, u, h[y + 14], 23, -35309556),
            u = s(u, f, v, m, h[y + 1], 4, -1530992060),
            m = s(m, u, f, v, h[y + 4], 11, 1272893353),
            v = s(v, m, u, f, h[y + 7], 16, -155497632),
            f = s(f, v, m, u, h[y + 10], 23, -1094730640),
            u = s(u, f, v, m, h[y + 13], 4, 681279174),
            m = s(m, u, f, v, h[y + 0], 11, -358537222),
            v = s(v, m, u, f, h[y + 3], 16, -722521979),
            f = s(f, v, m, u, h[y + 6], 23, 76029189),
            u = s(u, f, v, m, h[y + 9], 4, -640364487),
            m = s(m, u, f, v, h[y + 12], 11, -421815835),
            v = s(v, m, u, f, h[y + 15], 16, 530742520),
            f = s(f, v, m, u, h[y + 2], 23, -995338651),
            u = d(u, f, v, m, h[y + 0], 6, -198630844),
            m = d(m, u, f, v, h[y + 7], 10, 1126891415),
            v = d(v, m, u, f, h[y + 14], 15, -1416354905),
            f = d(f, v, m, u, h[y + 5], 21, -57434055),
            u = d(u, f, v, m, h[y + 12], 6, 1700485571),
            m = d(m, u, f, v, h[y + 3], 10, -1894986606),
            v = d(v, m, u, f, h[y + 10], 15, -1051523),
            f = d(f, v, m, u, h[y + 1], 21, -2054922799),
            u = d(u, f, v, m, h[y + 8], 6, 1873313359),
            m = d(m, u, f, v, h[y + 15], 10, -30611744),
            v = d(v, m, u, f, h[y + 6], 15, -1560198380),
            f = d(f, v, m, u, h[y + 13], 21, 1309151649),
            u = d(u, f, v, m, h[y + 4], 6, -145523070),
            m = d(m, u, f, v, h[y + 11], 10, -1120210379),
            v = d(v, m, u, f, h[y + 2], 15, 718787259),
            f = d(f, v, m, u, h[y + 9], 21, -343485551),
            u = i(u, n),
            f = i(f, l),
            v = i(v, p),
            m = i(m, c);
        return e(u) + e(f) + e(v) + e(m)
    }

    function p(e) {
        var t,
            i,
            o,
            n,
            r,
            a,
            s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        for (o = e.length, i = 0, t = ''; o > i;) {
            if (n = 255 & e.charCodeAt(i++), i == o) {
                t += s.charAt(n >> 2),
                    t += s.charAt((3 & n) << 4),
                    t += '==';
                break
            }
            if (r = e.charCodeAt(i++), i == o) {
                t += s.charAt(n >> 2),
                    t += s.charAt((3 & n) << 4 | (240 & r) >> 4),
                    t += s.charAt((15 & r) << 2),
                    t += '=';
                break
            }
            a = e.charCodeAt(i++),
                t += s.charAt(n >> 2),
                t += s.charAt((3 & n) << 4 | (240 & r) >> 4),
                t += s.charAt((15 & r) << 2 | (192 & a) >> 6),
                t += s.charAt(63 & a)
        }
        return t
    }

    function c(e) {
        for (var t, i, o, n, r = new Array(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1), a = 0, s = e.length, d = ''; s > a;) {
            do t = r[255 & e.charCodeAt(a++)];
            while (s > a && -1 == t);
            if (-1 == t) break;
            do i = r[255 & e.charCodeAt(a++)];
            while (s > a && -1 == i);
            if (-1 == i) break;
            d += String.fromCharCode(t << 2 | (48 & i) >> 4);
            do {
                if (o = 255 & e.charCodeAt(a++), 61 == o) return d;
                o = r[o]
            } while (s > a && -1 == o);
            if (-1 == o) break;
            d += String.fromCharCode((15 & i) << 4 | (60 & o) >> 2);
            do {
                if (n = 255 & e.charCodeAt(a++), 61 == n) return d;
                n = r[n]
            } while (s > a && -1 == n);
            if (-1 == n) break;
            d += String.fromCharCode((3 & o) << 6 | n)
        }
        return d
    }

    function h(e) {
        var t = '',
            i = '',
            o = '';
        return 28 == e.length && e.lastIndexOf('0') == e.length - 1 ? (t = e.substr(0, 27) + '=', i = c(t), o = f(i), y(o)) : (t = e.substr(2, e.length - 2), i = c(t), f(i))
    }

    function u(e, t, i) {
        i = i || 'MRUV8iB1i3l8oaZU';
        var o = i + t + e;
        return o = F.util.hex_sha1(o), 'undefined' == typeof Base64 ? '' : Base64.encode('ak=' + i + '&sign=' + o + '&t=' + e)
    }

    function f(e) {
        for (var t = '', i = 0; i < e.length;) {
            var o = e.charCodeAt(i++),
                n = e.charCodeAt(i++);
            if (t += m(v(o, n).z1), t += m(v(o, n).z2), i == e.length - 1) {
                t += m(e.charCodeAt(i));
                break
            }
        }
        return t
    }

    function v(e, t) {
        var i = mozecname,
            o = 256,
            n = [
                0,
                0,
                0,
                0
            ],
            r = [],
            a = {};
        for (k in i) {
            r[i[k].charAt(i[k].length - 1)] = i[k]
        }
        for (var s = 0, d = r.length; d > s; s++) n[parseInt(r[s].substr(r[s].length - 1))] = parseInt(r[s].substr(0, r[s].length - 1), 16);
        return {
            z1: (e * n[0] + t * n[2]) % o,
            z2: (e * n[1] + t * n[3]) % o
        }
    }

    function m(e) {
        return String.fromCharCode(e)
    }

    function y(e) {
        var t,
            i,
            o,
            n = '';
        for (e += '', t = 0, i = e.length; i > t; t++) o = e.charCodeAt(t).toString(16).toLocaleUpperCase(),
            n += o.length < 2 ? '0' + o : o;
        return n
    }

    function _(e) {
        for (var t, i, o = 0; !t && 2 > o;) {
            if (t = h(e.infohash), 41 == t.length && /^[0-9a-f]*$/gi.test(t)) {
                for (var n = (t.substr(0, 40), 0), r = 0, a = t.length - 1; a > r; r++) n += parseInt(parseInt(t.substr(r, 1), 16), 10);
                var s = 15 & n;
                s.toString(16).toUpperCase() == t.substr(40) && (i = {
                    hashid: t.substr(0, 40),
                    token: h(e.token)
                })
            }
            i || (t = null, e.infohash = e.infohash_prev, e.token = e.token_prev),
                o++
        }
        return i
    }
    return _(object)
}


        """

        ctx = self.modules["execjs"].compile(js)
        return ctx.call("fun", obj, self.mozecname)

    def decodePy(self, obj):
        import binascii

        self.coeff = [0, 0, 0, 0]
        for i in self.mozecname:
            idx = int(i[-1])
            val = int(i[:-1], 16)
            self.coeff[idx] = val

        def d(t):
            e = 0
            o = 0
            n = 0
            while not e and 2 > n:
                e = i(t["infohash"])
                a = 0
                if 41 == len(e) and not self.match("([^\w+])", e):
                    for r in range(40):
                        a += int(e[r], 16)
                    d = 15 & a
                    f = hex(d)
                    if f[2:].upper() == e[40]:
                        o = {"hashid": e[0:40], "token": i(t["token"])}
                e = ""
                t["infohash"] = t["infohash_prev"]
                t["token"] = t["token_prev"]
                if not o:
                    o = t["token"]
                n += 1
            return o

        def i(t):
            length = len(t)
            if length == 28 and t[-1] == "0":
                i = t[0:27] + "="
                n = e(i)
                a = o(n)
                # f = r(a)
                f = binascii.hexlify(a.encode("utf8")).upper()
            else:
                i = t[2:length]
                n = e(i)
                f = o(n)
            return f

        def e(t):
            return self.b64decode(t, 0)

        def o(t):
            length = len(t)
            e = ""
            i = 0
            while i < length - 1:
                o = t[i]
                r = t[i + 1]
                i += 2
                hh = n(o, r)
                e += chr(hh[0])
                e += chr(hh[1])
                if i == length - 1:
                    e += chr(t[i])

            return e

        def n(t, e):
            z1 = (t * self.coeff[0] + e * self.coeff[2]) % 256
            z2 = (t * self.coeff[1] + e * self.coeff[3]) % 256
            return z1, z2

        return d(obj)

    def js2unpack(self, p, a, c, k, e=None, d=None):
        import re

        # https://stackoverflow.com/questions/2753878/how-to-evaluate-javascript-code-in-python
        # 还原 JavaScript eval
        while c:
            c -= 1
            if k[c]:
                p = re.sub("\\b" + self.baseN(c, a) + "\\b", k[c], p)
        return p

    def baseN(self, x, base):
        digs = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if x < 0:
            sign = -1
        elif x == 0:
            return digs[0]
        else:
            sign = 1

        x *= sign
        digits = []
        while x:
            digits.append(digs[int(x % base)])
            x = int(x / base)

        if sign < 0:
            digits.append("-")

        digits.reverse()

        return "".join(digits)

    def decode_packed_codes(self, code):
        import re

        def encode_base_n(num, n, table=None):
            FULL_TABLE = (
                "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            )
            if not table:
                table = FULL_TABLE[:n]

            if n > len(table):
                raise ValueError("base %d exceeds table length %d" % (n, len(table)))

            if num == 0:
                return table[0]

            ret = ""
            while num:
                ret = table[num % n] + ret
                num = num // n
            return ret

        pattern = r"}\('(.+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)"
        mobj = re.search(pattern, code)
        obfucasted_code, base, count, symbols = mobj.groups()
        base = int(base)
        count = int(count)
        symbols = symbols.split("|")
        symbol_table = {}

        while count:
            count -= 1
            base_n_count = encode_base_n(count, base)
            symbol_table[base_n_count] = symbols[count] or base_n_count

        return re.sub(
            r"\b(\w+)\b", lambda mobj: symbol_table[mobj.group(0)], obfucasted_code
        )
