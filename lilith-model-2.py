# model2为artemis引擎，需要修改底层代码，失败，此python文件搁置

import http.client
import hashlib
import urllib
import random
import json
import re
from datetime import datetime
import requests
import time
import os

appid = '20201015000590183'  # 填写你的appid
secretKey = 'VVUMHEM_9yc7yN5dkhzo'  # 填写你的密钥
httpClient = None
myurl = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
fromLang = 'jp'  # 原文语种
toLang = 'zh'  # 译文语种
salt = random.randint(32768, 65536)


# 读一行写一行

# 匹配结果为true or false
def reMatch(str):
    # 根据正则获取需要翻译的数组
    rePattern = re.compile(r'\[.*?]')
    if (re.match(rePattern, str) or str == '\n' or str == '*last\n'):
        return False
    else:
        return True


# 写入新文件
def writeFile(dirNew, fileName, str):
    w = open(dirNew + '\\' + fileName, 'a+', encoding='utf-8')
    w.write(str)
    w.close()


# 发送请求
def sendHttp(myurl, appid, message, salt, secretKey, fromLang, toLang, fileName, dirNew):
    sign = appid + message + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        message) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        response = requests.get(myurl).json()['trans_result'][0]['dst']
        writeFile(dirNew, fileName, response + '\n')

    except Exception as e:
        print(e)
        sendHttp(myurl, appid, message, salt, secretKey, fromLang, toLang, fileName, dirNew)
    finally:
        if httpClient:
            httpClient.close()


# 读文件
def readFile():
    currentPath = os.getcwd()  # 获取当前路径*
    dirOrigin = currentPath + '\dirOrigin'
    # 创建新文件夹
    dirNew = currentPath + '\dirNew'
    if (not os.path.exists(dirNew)):
        os.makedirs(dirNew)

    # 遍历旧文件夹，翻译，写入新文件夹
    files = os.listdir(dirOrigin)
    for fileName in files:
        file = open(dirOrigin + '\\' + fileName, 'r', encoding='utf-8')
        # 从第n行开始读取
        for line in file.readlines():
            # 前一句匹配 并且 当前句不匹配，翻译
            if (reMatch(line)):
                sendHttp(myurl, appid, line, salt, secretKey, fromLang, toLang, fileName, dirNew)
                print(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
                time.sleep(1)
            #  前一句不匹配 或者 当前句匹配，不翻译
            else:
                writeFile(dirNew, fileName, line)

        file.close()


readFile()
