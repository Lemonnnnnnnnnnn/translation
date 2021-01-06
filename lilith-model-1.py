import http.client
import hashlib
import urllib
import random
import json
import re
from datetime import datetime
import time

appid = '20201015000590183'  # 填写你的appid
secretKey = 'VVUMHEM_9yc7yN5dkhzo'  # 填写你的密钥
httpClient = None
myurl = '/api/trans/vip/translate'
fromLang = 'jp'  # 原文语种
toLang = 'zh'  # 译文语种
salt = random.randint(32768, 65536)
file_name = 'newgame.ks'
output_name = 'new.ks'


# 读一行写一行

# 匹配结果为true or false
def reMatch(str, isMatch):
    # 根据正则获取需要翻译的数组
    reHead = re.compile(r'\[NAME_[MW] n=".*?"]\\|\[NAME_TIPS_OFF]\\')
    reTail = re.compile(r'(.*?)(?=\[T_NEXT]\\)')
    if (re.match(reHead, str)): isMatch = True
    if (re.match(reTail, str) and isMatch == True):
        isMatch = False
    return isMatch


# 写入新文件
def writeFile(fileName, str):
    w = open(fileName, 'a+', encoding='utf-8')
    w.write(str)
    w.close()


# 发送请求
def sendHttp(myurl, appid, message, salt, secretKey, fromLang, toLang):
    # 处理特殊字符
    message = re.sub(r'\[ruby text=.*?]', '', message)

    # 处理尾部
    reTail = re.compile(r'(.*?)(?=\[T_NEXT]\\)')
    haveTail = re.match(reTail, message)
    if (haveTail):
        message = haveTail.group()

    sign = appid + message + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    url = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        message) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', url)

        # response是HTTPResponse对象
        response = httpClient.getresponse().read().decode("utf-8")
        result = json.loads(response)['trans_result'][0]['dst']
        if (haveTail):
            writeFile(output_name, result + '[T_NEXT]\\' + '\n')
        else:
            writeFile(output_name, result + '\n')

    except Exception as e:
        print(e)
        sendHttp(myurl, appid, message, salt, secretKey, fromLang, toLang)
    finally:
        if httpClient:
            httpClient.close()


# 读文件
def readFile(fileName):
    file = open(fileName, 'r', encoding='utf-8')
    isMatch = False
    for line in file.readlines():
        if (isMatch and not (re.match(r'\[NAME_[MW] n=".*?"]\\|\[NAME_TIPS_OFF]\\', line))):
            sendHttp(myurl, appid, line, salt, secretKey, fromLang, toLang)
            print(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
            time.sleep(1)
        else:
            writeFile(output_name, line)
        isMatch = reMatch(line, isMatch)

    file.close()

readFile(file_name)
