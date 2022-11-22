# QITO音乐视频下载器

qito: 基于python3编写的视频解析器

---

## 安装使用

```
pip3 install qito
```
## 在线升级

```
qito upgrade
```
## 源升级
```
pip3 install --upgrade qito
```
### 全局配置

```
iniPath: 自定义ini文件夹路径, 默认为qito/ini
MAC:qito config -ip xxx路径

filePath: 自定义文件下载路径, 默认为cwd路径/download
MAC:qito config -fp xxx路径

```

### INI配置

以qq为例,配置文件名为qq.ini,存放在设定iniPath路径即可

如需请求cookie,在ini设置cookie节点即可

```
[cookie]
xxx=xxxx;
```

# 使用说明:
#### 默认打印JSON (Parse)
```
MAC: qito air$ qito https://www.bilibili.com/video/BV1Jx411r76d/
{'hd': 6, 'type': 'bilibili', 'category': 'video', 'choose': False, 'playlist': False, 'iniPath': False, 'filePath': False, 'urls': ['https://www.bilibili.com/video/BV1Jx411r76d/'], 'parse': 'https://www.bilibili.com/video/BV1Jx411r76d/', 'site': 'bilibili', 'page': 1, 'aid': 9196627, 'title': '【补帧向/AMV】一花一草一世界', 'image': 'http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg', 'vid': 15195741, 'streams': {'flv': 'http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv', 'segs': [{'url': 'http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv', 'duration': 127.9, 'size': 30695642}], 'mp4': 'http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-48.mp4'}, 'playback': 'mp4', 'extra': {'headers': {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0', 'Referer': 'https://www.bilibili.com/video/'}, 'playback': 'flv'}, 'otype': 'video', 'quality': ['流畅 360P', '清晰 480P', '高清 720P', '高清 1080P'], 'multirates': 4, 'ext': 'flv', 'show': '高清 1080P', 'duration': 127.9, 'code': 0}
```
#### -f --format : 格式转换 (FFMPEG format)
```
MAC: qito https://www.bilibili.com/video/BV1Jx411r76d/ -j
{
  "hd": 6,
  "type": "bilibili",
  "category": "video",
  "choose": false,
  "playlist": false,
  "iniPath": false,
  "filePath": false,
  "urls": [
    "https://www.bilibili.com/video/BV1Jx411r76d/"
  ],
  "parse": "https://www.bilibili.com/video/BV1Jx411r76d/",
  "site": "bilibili",
  "title": "【补帧向/AMV】一花一草一世界",
  "vid": 15195741,
  "aid": 9196627,
  "image": "http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg",
  "page": 1,
  "streams": {
    "segs": [
      {
        "url": "http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv",
        "duration": 127.9,
        "size": 30695642
      }
    ],
    "flv": "http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv",
    "mp4": "http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-48.mp4"
  },
  "playback": "mp4",
  "show": "高清 1080P",
  "ext": "flv",
  "duration": 127.9,
  "otype": "video",
  "extra": {
    "headers": {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0",
      "Referer": "https://www.bilibili.com/video/"
    },
    "playback": "flv"
  },
  "quality": [
    "流畅 360P",
    "清晰 480P",
    "高清 720P",
    "高清 1080P"
  ],
  "multirates": 4
}

```

#### -d --download : 下载 (Download)
```
MAC: qito https://www.bilibili.com/video/BV1Jx411r76d/ -d
Web:                 哔哩哔哩视频(BILIBILI)
Site:                bilibili
Title:               补帧向一花一草一世界
Image:               http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg
Vid:                 15195741
Parse:               https://www.bilibili.com/video/BV1Jx411r76d/
Category:            video
Hd:                  6
Stream:
    - Ext:           flv
      Playback:      mp4
      Duration:      127.9s
      Quality:       ['流畅 360P', '清晰 480P', '高清 720P', '高清 1080P']
      Show:          高清 1080P
      Multirates:    4
      Length:        1
      Dir:           /Users/air/IPC/Project/Python/vv/qito/dw
[1 / 1] |-███████████████------------------|49%  586.04kb/s 14.49M/29.27M 
```
#### -i --info : 打印信息 (Print Info)
```
MAC: qito https://www.bilibili.com/video/BV1Jx411r76d/ -i
Web:                 哔哩哔哩视频(BILIBILI)
Site:                bilibili
Title:               补帧向一花一草一世界
Image:               http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg
Vid:                 15195741
Parse:               https://www.bilibili.com/video/BV1Jx411r76d/
Category:            video
Hd:                  6
Stream:
    - Ext:           flv
      Playback:      mp4
      Duration:      127.9s
      Quality:       ['流畅 360P', '清晰 480P', '高清 720P', '高清 1080P']
      Show:          高清 1080P
      Multirates:    4
      Length:        1
Location:
    - mp4:           http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-48.mp4
      part[1]:       http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv [30695642]
```
#### -q --query : 只获取链接信息 (Output only video information)
```
MAC: qito https://www.bilibili.com/video/BV1Jx411r76d/ -q
{'hd': 6, 'type': 'bilibili', 'category': 'video', 'choose': False, 'playlist': False, 'iniPath': False, 'filePath': False, 'urls': ['https://www.bilibili.com/video/BV1Jx411r76d/'], 'parse': 'https://www.bilibili.com/video/BV1Jx411r76d/', 'site': 'bilibili', 'page': 1, 'title': '【补帧向/AMV】一花一草一世界', 'aid': 9196627, 'vid': 15195741, 'image': 'http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg', 'code': 0}

```
#### -p --player : 播放器播放 (Directly play the video with PLAYER like mpv)
```
MAC: qito https://www.bilibili.com/video/BV1Jx411r76d/ -p mpv
Web:                 哔哩哔哩视频(BILIBILI)
Site:                bilibili
Title:               【补帧向/AMV】一花一草一世界
Image:               http://i0.hdslb.com/bfs/archive/f2b6833f8d732c6b624e11572b9b86afac7d9687.jpg
Vid:                 15195741
Parse:               https://www.bilibili.com/video/BV1Jx411r76d/
Category:            video
Hd:                  6
Stream:
    - Ext:           flv
      Playback:      mp4
      Duration:      127.9s
      Quality:       ['流畅 360P', '清晰 480P', '高清 720P', '高清 1080P']
      Show:          高清 1080P
      Multirates:    4
      Length:        1
      Dir:           /Users/air/IPC/Project/Github/qito/dw

PlayBack: http://upos-sz-mirrorhw.bilivideo.com/upgcxcode/41/57/15195741/15195741-1-80.flv
 (+) Video --vid=1 (h264 1280x720 60.000fps)
 (+) Audio --aid=1 (aac 2ch 48000Hz)
AO: [coreaudio] 48000Hz stereo 2ch floatp

```
### 额外参数

| A    | 选项    | 传参1    |   传参2  |  类型   |  示例  |  说明  |
|:-----|:----------|:----------|:----------|:----------|:----------|:----------|
| 1    | 分辨率    | -r    | --hd    | int   | 6    | 默认最高分辨率输出   |
| 2    | cookie    | -c    | --cookie    | string    | a=b;c=d    | 加cookie后,解析会带此cookie请求数据   |
| 3    | 播放列表    | -l    | --playlist    | bool    |      | 默认false,带此参数,会优先解析成剧集列表    |
| 4    | 列表选择   | -b    | --choose    | string    | a或a,b或a:b   | ,作为分隔符时,会解析a和b集 :作为分隔符时,会解析a到b的剧集    |
| 5    | 自定义文件名    | -n    | --name   | string   | 测试A    | 下载时的主体名称是 "测试A"    |
| 6    | 调试    | -s    | --debug   | bool    |      | 默认false,带此参数后,终端会输出相应请求    |




