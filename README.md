# Jiangda Portal Automatic Login
 江大登录门户的py模拟登陆实现

## 过程解析:
1. 初次请求登录门户(get):
>https://pass.ujs.edu.cn/cas/login
2. 请求验证码(get): 
>https://pass.ujs.edu.cn/cas/captcha.html
3. 再次用请求登录门户(post),并提交登录表单.

三次请求如果都成功并且无错误,应该返回成功登陆后的界面.

### post表单内容解析：
```
username: 1234567890
password: gfgwDALwERl0MuTBfg+U/m81JBDbksfasfTj8msH9HqqKztL+3lIhePVsFD5GXoDi7DYyQs7YoeN1Yz0RlMhegECvXfiIsQ=
captchaResponse: aphc
lt: LT-958050-a0kzJW9kweaskdgfHJdaY1Ug7oHe2eQ1611227557350-OC02-cas
dllt: userNamePasswordLogin
execution: e2s1
_eventId: submit
rmShown: 1
```
+ username: 学号
+ password: 加密后的密码
+ captchaResponse: 验证码
+ lt: 一串奇怪的字符,在第一次请求的response里面,可以用正则表达式`<input name="lt" type="hidden" value="(.*?)"/>`匹配到.
+ dllt: 固定值
+ execution: 奇怪的字符,使用正则表达式`<input name="execution" type="hidden" value="(.*?)"/>`匹配
+ _eventId: 固定值
+ rmShown: 固定值

### 密码加密解析:
只是将网页的js代码稍作整理提取,有兴趣的大佬可以研究一下具体的加密过程(其实是我不会).
其中的加密函数`_etd2()`需要
两个参数:
+ 密码
+ pwdDefaultEncryptSalt

其中pwdDefaultEncryptSalt可以用正则表达式`var pwdDefaultEncryptSalt = "(.*?)";`匹配.

我已经将加密的代码整理为两个js文件,使用时候只需要运行jiami.js里面的`_etd2()`函数并且传入相应的参数,获取函数返回值即可.

## 注意事项
+ 三次请求应该是同一个session完成

## 请求示例:
~~详见login.py~~

重写了login.py,建议使用loginRe.py
+ 调用登陆模块示例:
+++ ```import loginRe
import getpass

if __name__ == '__main__':
    username = input('学号: ')
    pwd = getpass.getpass("密码: ")
    lg = loginRe.Login('6e9b090sdad5c1234d0bbb88de18097eb')
    lg.Login(username=username, password=pwd)

```
#### tip:
阿里云ocr识别请自行申请接口key. [戳我传送](https://market.aliyun.com/products/57124001/cmapi020020.html)

用到的模块:
```
import base64
import re
import requests
from log1 import l
import json
from bs4 import BeautifulSoup
import execjs
```
不要吐槽那个log1.py,只是为了好看,其实就是个带颜色的print()大佬可以自行改写(捂脸)

模拟登陆的用途:应该没什么用吧 (bushi)

仅供学习交流,应该不至于被叫去喝茶吧? (逃)


