#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : setup.py
@Time    : 2022/9/27 下午8:54  
"""
# !/usr/bin/env python3
# -*- coding:UTF-8 -*-
from setuptools import setup

import os, codecs, platform
from qito.config.profile import version

REQ = [
    "requests",
    "pycryptodome",
    "pysocks",
    "pyexecjs",
    "coloredlogs",
    "cloudscraper",
    "demjson",
]


def find_packages(*tops):
    packages = []
    for d in tops:
        for root, dirs, files in os.walk(d, followlinks=True):
            if "__init__.py" in files:
                packages.append(root)
        # packages.extend(['vparse/temp',"vparse/cookie"])
    return packages


setup(
    name="qito",
    version=version,
    author="KEDAYA",
    author_email="ii@iippcc.com",
    url="https://github.com/qitoqito/qito",
    license="MIT",
    description="视频音乐下载播放器",
    packages=find_packages("qito"),
    package_data={"qito": ["parse/json/*.json", "parse/javascript/*.*"]},
    python_requires=">=3.5",
    long_description="""基于Python,视频、音乐、直播下载器,支持YouKu、QQ、Iqiyi等""",
    classifiers=["License :: OSI Approved :: MIT License"],
    platforms="any",
    requires=[],
    install_requires=[],
    entry_points={
        "console_scripts": [
            "qito=qito.__main__:main",
        ]
    },
)
