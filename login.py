import base64
import re
import requests
from log1 import l
import json
from bs4 import BeautifulSoup
import execjs


# OCR
def ocrcaptcha(ocrPic):
    ocrAPI = 'http://tysbgpu.market.alicloudapi.com/api/predict/ocr_general/'
    appcode = '6e9b09015d5c4661234bb88de18097eb'
    Headers = {"Authorization": "APPCODE " + appcode}
    data = {
        "image": ocrPic,
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
    while ' ' in word:
        word = word.replace(' ', '')
    l.info(f'验证码为:{word}')
    return word


# 识别验证码函数
def getword():
    with open('captcha.png', 'rb')as captchaPic:
        base64_data = base64.b64encode(captchaPic.read())
        ocrPic = base64_data.decode()
        word = ocrcaptcha(ocrPic)
        return word


def getcaptcha(ses, captcha):
    '''
    获取验证码图片并写入到本地
    :param ses: session
    :param captcha: 验证码地址
    :return:
    '''
    response = ses.get(captcha)
    # print(ses.cookies.get_dict())
    with open('captcha.png', 'wb')as captchaPic:
        captchaPic.write(response.content)


def getargv(html):
    '''
    获取登录表单里面的两个参数
    :param html: 网页代码
    :return: list[lt,execution]
    '''
    key = re.findall(r'var pwdDefaultEncryptSalt = "(.*?)";', html)[0]
    soup = BeautifulSoup(html, 'html.parser')
    form = soup.find_all('form', id='casDynamicLoginForm')
    formstr = str(form[0])
    lt = re.findall(r'<input name="lt" type="hidden" value="(.*?)"/>', formstr)[0]
    execution = re.findall(r'<input name="execution" type="hidden" value="(.*?)"/>', formstr)[0]
    l.info(f'lt={lt}\texecution={execution}\tpwdDefaultEncryptSalt={key}')
    return [lt, execution, key]


def jiami(pwd, key):
    '''
    加密密码
    :param pwd: 初始密码
    :return: 加密后的
    '''
    vm = execjs.compile(open('./jiami.js').read() + open('./encrypt.js').read())
    js = '_etd2("{0}", "{1}")'.format(pwd, key)
    password = vm.eval(js)
    return password


def Login(loginapi, username, password, word, lt, execution, ses):
    '''
    提交登录表单部分
    :param loginapi: 提交表单的地址
    :param username: 用户名
    :param password: 加密过的密码
    :param word: 验证码
    :param lt:
    :param execution:
    :param ses: 会话(session)
    :return: 页面的response
    '''
    data = {
        'username': username,
        'password': password,
        'captchaResponse': word,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': execution,
        '_eventId': 'submit',
        'rmShown': 1
    }

    response = ses.post(url=loginapi, data=data, )
    # print(ses.cookies.get_dict())
    return response


# 登录
def login(username, pwd):
    captcha = 'https://pass.ujs.edu.cn/cas/captcha.html'
    loginapi = 'https://pass.ujs.edu.cn/cas/login'
    ses = requests.session()
    ses.headers = {
        'Host': 'pass.ujs.edu.cn',
        'Referer': 'https://pass.ujs.edu.cn/cas/login',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36 Edg/86.0.622.68'
    }
    # 初始化请求
    l.info('初始化')
    response = ses.get(loginapi)
    # ses.cookies['org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE'] = 'zh_CN'
    html = response.content.decode()
    # 验证码
    getcaptcha(ses, captcha)
    word = getword()
    # 表单参数获取
    argvs = getargv(html)
    lt = argvs[0]
    execution = argvs[1]
    key = argvs[2]
    # 获取加密后密码
    password = jiami(pwd, key)
    # 提交表单
    l.info('登录...')
    response = Login(loginapi=loginapi, execution=execution, password=password, lt=lt, ses=ses, word=word,
                     username=username)
    l.info(str(response.status_code))
    if '个人资料' in response.content.decode('utf-8'):
        l.info('登录成功!!!!')

    else:
        l.info('登录失败!!!!!')

    # with open("result.html", 'w', encoding='utf-8') as resHtml:
    #     resHtml.write(
    #         response.content.decode('utf-8').replace(' name="password" style="display:none;" ', 'name="password"'))

    # os.system('start result.html')


login(123456789, 'sb19876543')
