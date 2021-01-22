import base64
import re
import requests
from log1 import l
import json
from bs4 import BeautifulSoup
import execjs


def showRedirectHistory(response):
    reditList = response.histroy
    text = f'重定向次数:{len(reditList)}\n'
    l.info(text)
    for item in reditList:
        l.info(f'重定向链接:{item.headers["location"]}')


class Login():
    def __init__(self, ocrAppCode):
        """
        初始化
        :param ocrAppCode: 阿里云OCR的Appcode
        """
        self.AppCode = ocrAppCode

    def __GetcaptchaWord(self, Base64Pic):
        l.info('开始识别验证码')
        ocrAPI = 'http://tysbgpu.market.alicloudapi.com/api/predict/ocr_general/'
        appcode = self.AppCode
        Headers = {"Authorization": "APPCODE " + appcode}
        data = {
            "image": Base64Pic,
            "configure":
                {
                    "min_size": 16,  # 图片中文字的最小高度，单位像素
                    "output_prob": "true",  # 是否输出文字框的概率
                    "output_keypoints": "false",  # 是否输出文字框角点
                    "skip_detection": "false",  # 是否跳过文字检测步骤直接进行文字识别
                    "without_predicting_direction": "false"  # 是否关闭文字行方向预测
                }
        }
        data = json.dumps(data)
        response = requests.post(ocrAPI, data=data, headers=Headers)
        res = response.content.decode()
        # print(res)
        jsondata = json.loads(res)
        word = jsondata['ret'][0]['word']
        # 去除空格
        while ' ' in word:
            word = word.replace(' ', '')
        l.info(f'验证码为:{word}')
        return word

    def __getcaptcha(self, captchaApi):
        '''
        请求验证码
        :param captchaApi: 请求地址
        :return: byte类型的图片
        '''
        l.info('开始请求验证码')
        response = self.ses.get(captchaApi)
        # print(ses.cookies.get_dict())
        return response.content

    def __getargv(self, html):
        '''
        获取登录表单里面的两个参数和密码加密参数
        :param html: 网页代码
        :return: list[lt,execution,密码加密的key]
        '''
        l.info('匹配登录表单参数...')
        key = re.findall(r'var pwdDefaultEncryptSalt = "(.*?)";', html)[0]
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find_all('form', id='casDynamicLoginForm')
        formstr = str(form[0])
        lt = re.findall(r'<input name="lt" type="hidden" value="(.*?)"/>', formstr)[0]
        execution = re.findall(r'<input name="execution" type="hidden" value="(.*?)"/>', formstr)[0]
        l.info(f'lt={lt}\texecution={execution}\tpwdDefaultEncryptSalt={key}')
        return [lt, execution, key]

    def __encrypt(self, password, key):
        l.info('加密密码....')
        '''
        加密密码
        :param password: 初始密码
        :return: 加密后的
        '''
        vm = execjs.compile(open('./jiami.js').read() + open('./encrypt.js').read())
        js = '_etd2("{0}", "{1}")'.format(password, key)
        password = vm.eval(js)
        return password

    def __loginPost(self, loginapi, username, passwordEncrypt):
        l.info('提交登录请求...')
        '''
        提交登录表单部分
        :param loginapi: 提交表单的地址
        :param username: 用户名
        :param passwordEncrypt: 加密后的密码
        :return: 页面的response
        '''
        data = {
            'username': username,
            'password': passwordEncrypt,
            'captchaResponse': self.captchaWord,
            'lt': self.lt,
            'dllt': 'userNamePasswordLogin',
            'execution': self.execution,
            '_eventId': 'submit',
            'rmShown': 1
        }

        response = self.ses.post(url=loginapi, data=data, )
        # print(ses.cookies.get_dict())
        return response

    def Login(self, username, password):
        """
        登录方法
        :param username: 学号
        :param password: 密码
        :return: 成功返回会话session,失败返回None.
        """
        captchaApi = 'https://pass.ujs.edu.cn/cas/captcha.html'
        loginapi = 'https://pass.ujs.edu.cn/cas/login'
        self.ses = requests.session()
        self.ses.headers = {
            'Host': 'pass.ujs.edu.cn',
            'Referer': 'https://pass.ujs.edu.cn/cas/login',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.68'
        }
        response = self.ses.get(loginapi)
        html = response.content.decode()

        pic = self.__getcaptcha(captchaApi)
        base64_data = base64.b64encode(pic)
        base64pic = base64_data.decode()
        self.captchaWord = self.__GetcaptchaWord(base64pic)

        while len(self.captchaWord) != 4:
            l.warn('验证码识别失败,重试中...')
            self.captchaWord = self.__GetcaptchaWord(base64pic)

        argvs = self.__getargv(html)
        self.lt = argvs[0]
        self.execution = argvs[1]
        self.key = argvs[2]

        passwordEncrypt = self.__encrypt(password=password, key=self.key)

        # 提交表单
        l.info('登录...')
        response = self.__loginPost(loginapi=loginapi, username=username, passwordEncrypt=passwordEncrypt)
        l.info(str(response.status_code))
        responseHtml = response.content.decode('utf-8')
        if '个人资料' in responseHtml:
            l.info('登录成功!!!!')
            # showRedirectHistory(response)
            return self.ses
            # return cookiedict
        elif '您提供的用户名或者密码有误' in responseHtml:
            l.warn('账号密码错误')
            return None
        elif '无效的验证码' in responseHtml:
            l.warn('验证码有误!!')
            return None
        else:
            print(responseHtml)
            l.error('未知错误\n登录失败!!!!!')
            return None
