# UESTC 校园网自动认证登录（牛马专用版）

考虑到部分优秀学生（指我）科研努力，寒暑假回家也要猛猛学习，但是学校在放假后有时候会断电，教研室没有人在的情况下难以远程连接，特写了此脚本为祖国未来的人才保驾护航。（断电需要配置BIOS开启上电自启动，这个大家根据自己的电脑品牌自行Google）

该脚本是为了解决校园网不定时认证的问题，使用该脚本后电脑开机会自动检测校园网的连接，如果断开连接，则会自动重连；同时每隔一段时间检测网络情况，如果断开连接，也会自动重连，防止在家或者外地无法远程影响各位英才的科研发展。

## 介绍（正经版本）

轻量脚本，自动检测网络并在掉线时重登深澜 Portal，可选企业微信通知。

## 快速开始

1. 安装依赖：`py -m pip install -r requirements.txt`
2. 复制配置：`copy config.example.py config.py`
3. 编辑配置：`config.py` 中填入学号/密码，并根据实际网络设置：
   - 认证地址：主楼/研究院 `http://10.253.0.237`；寝室公寓 `http://10.253.0.235`
   - ac_id：主楼有线 `1`；寝室 `3`
   - domain：校园网 `@dx-uestc`（这个可能不需要，可以不填）；电信 `@dx`；移动 `@cmcc`
   - 可选：`test_ip`（默认 223.5.5.5）和 `test_urls`（HTTP 兜底探测列表）
4. 测试一次性登录：`py login_once.py`
5. 启动持续监控：`py always_online.py`

## 测试

1. 断开校园网
![alt text](fig/image.png)

2. 启动一次性登录脚本
![alt text](fig/image-2.png)

3. 持续监控
![alt text](fig/image-3.png)

## 开机自启（任选其一）

- 任务计划程序（管理员）  
  - 在 CMD：`schtasks /create /tn "UESTC-NET" /tr "\"%SystemRoot%\System32\pythonw.exe\" \"<项目路径>\\always_online.py\"" /sc onlogon /rl HIGHEST /f`
- NSSM 服务（自备 nssm.exe）：  
  `nssm install UESTC-NET "%SystemRoot%\System32\pythonw.exe" "<项目路径>\\always_online.py"`  
  `nssm set UESTC-NET AppDirectory "<项目路径>"`  
  `nssm set UESTC-NET Start SERVICE_AUTO_START`

## 微信通知（可选）

`config.py` 将 `notify_options['enabled']` 设为 `True` 并填入企业微信机器人 Webhook。

## 致谢

- [AutoLoginUESTC](https://github.com/b71db892/AutoLoginUESTC)
- [go-nd-portal](https://github.com/fumiama/go-nd-portal)
