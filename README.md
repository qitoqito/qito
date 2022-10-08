# QITO音乐视频下载器

qito: 基于python3编写的视频解析器

---

## 如何安装

```
pip3 install qito
```

### 全局配置

```
iniPath: 自定义ini文件夹路径, 默认为qito/ini
cwd: qito config -ip xxx路径

filePath: 自定义文件下载路径, 默认为cwd路径/download
cwd: qito config -fp xxx路径
```

### INI配置

以qq为例,配置文件名为qq.ini,存放在设定iniPath路径即可
如需设置请求cookie,在ini设置cookie节点即可

```
[cookie]
xxx=xxxx;
```
