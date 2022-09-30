#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : __main__.py
@Time    : 2022/9/10 下午1:39
"""
from argparse import ArgumentParser

import coloredlogs, re, importlib, traceback, logging, json, sys, os, traceback, time

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from main import Parse


def cmd():
    parser = ArgumentParser(
        description="A simple video downloader written in python",
        usage="qito [OPTIONS] URL [URL...]",
    )

    parser.add_argument(
        "-V", "--version", action="store_true", help="Print version and exit"
    )
    parser.add_argument(
        "-c", "--cookie", default="", type=str, help="Cookie [file.txt/Netscape Cookie]"
    )
    parser.add_argument(
        "-e",
        "--exit",
        default=False,
        action="store_true",
        help="End process when parsing playlist error",
    )
    parser.add_argument("-f", "--format", default="", help="Video format")
    parser.add_argument(
        "-i", "--info", default=False, action="store_true", help="Print all information"
    )
    parser.add_argument(
        "-j", "--json", default=False, action="store_true", help="Print json"
    )

    parser.add_argument(
        "-q",
        "--query",
        default=False,
        action="store_true",
        help="Print video information only",
    )
    parser.add_argument(
        "-r", "--hd", type=int, help="Video resolution selection [1,2, ...]"
    )
    parser.add_argument(
        "-s", "--debug", default=False, action="store_true", help="Print  messages"
    )

    parser.add_argument("-t", "--type", help="Parsing type,Add when urls is not a URL")

    parser.add_argument("-v", "--category", help="Site category [video/music/live]")
    parser.add_argument(
        "-x", "--proxy", default=False, help="Proxy option [http/https/socks5]"
    )
    parser.add_argument("-y", "--http", default=False, help="Http proy")
    parser.add_argument(
        "-z",
        "--timeout",
        default=False,
        type=int,
        help="Set httpGet timeout seconds, default 6s",
    )
    playlist_grp = parser.add_argument_group("Playlist options")

    playlist_grp.add_argument(
        "-b",
        "--choose",
        default=False,
        help="Choose which range when the urls is a playlist",
    )
    playlist_grp.add_argument(
        "-l",
        "--playlist",
        default=False,
        action="store_true",
        help="Add when urls is playlist",
    )

    download_grp = parser.add_argument_group("Download options")
    download_grp.add_argument(
        "-d", "--download", default=False, action="store_true", help="Download"
    )

    download_grp.add_argument(
        "-m", "--merge", default=True, action="store_false", help="Do not merge videos"
    )
    download_grp.add_argument(
        "-n",
        "--name",
        default=False,
        type=str,
        help="Video downloaded with the FileName you want",
    )
    download_grp.add_argument(
        "-u",
        "--multi",
        default=False,
        type=int,
        help="Multi-threaded download, default 10",
    )
    download_grp.add_argument("-w", "--dir", default=False, help="Storage folder")
    download_grp.add_argument(
        "-a",
        "--capture",
        default=False,
        action="store_true",
        help=" Download clips only",
    )
    player_grp = parser.add_argument_group("Player options")
    player_grp.add_argument(
        "-g",
        "--geometry",
        default=False,
        help="Adjust the initial window position or size,For example,1366 or 50﹪",
    )
    player_grp.add_argument(
        "-lo",
        "--loop",
        default=False,
        help="Loop",
    )
    player_grp.add_argument(
        "-p",
        "--player",
        default=False,
        help="Directly play the video with PLAYER like mpv",
    )

    player_grp.add_argument(
        "-fs",
        "--fullscreen",
        default=False,
        action="store_true",
        help="Fullscreen playback",
    )
    player_grp.add_argument(
        "-ts", "--start", default=False, help="Seek to given time position"
    )
    player_grp.add_argument(
        "-te", "--end", default=False, help="Stop at given absolute time"
    )
    player_grp.add_argument(
        "-tl",
        "--length",
        default=False,
        help="Stop after a given time relative to the start time",
    )
    player_grp.add_argument(
        "-na",
        "--no_audio",
        default=False,
        action="store_true",
        help="Do not play sound",
    )
    player_grp.add_argument(
        "-nv",
        "--no_video",
        default=False,
        action="store_true",
        help="Do not play video",
    )
    player_grp.add_argument(
        "-vo",
        "--volume",
        default=False,
        help="Volume",
    )
    extra_grp = parser.add_argument_group("Extra options")
    extra_grp.add_argument(
        "-init",
        "--init",
        default=False,
        help="Initial setup, backup or restore user.py",
    )
    extra_grp.add_argument(
        "-o", "--language", default=False, help="Select language options"
    )
    # 额外
    extra_grp.add_argument(
        "-itag", "--itag", default=False, help="Youtube itag, 137[,value]"
    )
    extra_grp.add_argument("-ccode", "--ccode", default=False, help="Youku ccode")
    extra_grp.add_argument("-ip", "--iniPath", default=False, help="Config iniPath")
    extra_grp.add_argument("-fp", "--filePath", default=False, help="Config filePath")
    extra_grp.add_argument(
        "-pwd", "--password", default=False, help="Encryption password for video"
    )
    extra_grp.add_argument(
        "-enc",
        "--encoder",
        default=False,
        help="Select the video option to encode",
    )

    parser.add_argument("urls", type=str, nargs="*", help="video urls")

    args = parser.parse_args()
    if args.version:
        from config.profile import version

        sys.exit(version)
    elif args.capture:
        args.download = True
        if not args.start:
            print("Please set the start time")
            sys.exit()
    return args


def main():
    params = vars(cmd())
    if not params["urls"]:
        sys.exit("usage: qito [OPTION]... URL...")

    # logging.basicConfig(handlers=[log.ColorHandler()])
    FIELD_STYLES = dict(
        asctime=dict(color="green"),
        hostname=dict(color="magenta"),
        levelname=dict(color="green"),
        filename=dict(color="magenta"),
        name=dict(color="red"),
        threadName=dict(color="green"),
    )

    LEVEL_STYLES = dict(
        debug=dict(color="green"),
        info=dict(color="cyan"),
        warning=dict(color="yellow"),
        error=dict(color="red"),
        critical=dict(color="red"),
    )

    coloredlogs.install(
        level="DEBUG",
        fmt="%(levelname)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s",
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES,
    )
    if params.get("debug"):
        logging.root.setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("chardet").setLevel(logging.WARNING)
    else:
        logging.root.setLevel(logging.WARNING)
    try:
        for parse in params["urls"]:
            params["parse"] = parse
            Parse(params)
    except (AssertionError, IndexError) as e:
        info = sys.exc_info()
        try:
            err = traceback.extract_tb(info[2])[1]
        except:
            err = traceback.extract_tb(info[2])[0]
        error = {
            "message": str(e),
            "file": err[0],
            "line": err[1],
            "function": err[2],
            "code": err[3],
        }
        logging.warning(error)
        # logging.error(e.message)
    except (NotImplementedError, KeyError, NameError, AttributeError, TypeError) as e:
        logging.error(e.message)
        if params["exit"]:
            sys.exit()
    except KeyboardInterrupt:
        print("\r\n")
        logging.warning("ctrl c!")
        sys.exit()


if __name__ == "__main__":
    main()
