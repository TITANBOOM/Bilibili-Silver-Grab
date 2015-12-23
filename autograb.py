#!/usr/bin/env python
#coding:utf-8
# Author:  Beining --<i#cnbeining.com>
# Co-op: SuperFashi
# Purpose: Auto grab silver of Bilibili
# Created: 10/22/2015
# https://www.cnbeining.com/
# https://github.com/cnbeining

import sys
import os
import requests
import getopt
from json import loads
import datetime
import time
import re
import logging
import traceback
try:
    import biliocr
    from PIL import Image
except ImportError:
    pass

# Dual support
try:
    input = raw_input
except NameError:
    pass

# LATER
#BAIDU_KEY =

#----------------------------------------------------------------------
def logging_level_reader(LOG_LEVEL):
    """str->int
    Logging level."""
    return {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }.get(LOG_LEVEL)

#----------------------------------------------------------------------
def generate_16_integer():
    """None->str"""
    from random import randint
    return str(randint(1000000000000000, 9999999999999999))

#----------------------------------------------------------------------
def safe_to_eval(string_this):
    """"""
    pattern = re.compile(r'^[\d\+\-\s]+$')
    match = pattern.match(string_this)
    if match:
        return True
    else:
        return False

#----------------------------------------------------------------------
def get_new_task_time_and_award(headers):
    """dict->tuple of int
    time_in_minutes, silver"""
    random_r = generate_16_integer()
    url = 'http://live.bilibili.com/FreeSilver/getCurrentTask?r=0.{random_r}'.format(random_r = random_r)
    response = requests.get(url, headers=headers)
    a = loads(response.content.decode('utf-8'))
    logging.debug(a)
    if a['code'] == 0:
        return (a['data']['minute'], a['data']['silver'])

#----------------------------------------------------------------------
def get_captcha_from_live(headers):
    """dict,str->str
    get the captcha link"""
    random_t = generate_16_integer()  #save for later
    url = 'http://live.bilibili.com/FreeSilver/getCaptcha?t=0.{random_t}'.format(random_t = random_t)
    response = requests.get(url, stream=True, headers=headers)
    filename = random_t + ".jpg"
    with open(filename, "wb") as f:
        f.write(response.content)
    result = os.path.abspath(filename)
    logging.debug(result)
    return result

#----------------------------------------------------------------------
def image_link_ocr(image_link):
    res = biliocr.procimg(image_link)
    os.remove(image_link)
    logging.debug(res)
    return res

#----------------------------------------------------------------------
def send_heartbeat(headers):
    """"""
    random_t = generate_16_integer()
    url = 'http://live.bilibili.com/freeSilver/heart?r=0.{random_t}'.format(random_t = random_t)
    response = requests.get(url, headers=headers)
    a = loads(response.content.decode('utf-8'))
    if a['code'] != 0:
        return False
    elif response.status_code != 200:
        print('错误：心跳发送失败！') # Probably never see this
        return False
    else:
        return True

#----------------------------------------------------------------------
def get_award(headers, captcha):
    """dict, str->int/str"""
    url = 'http://live.bilibili.com/freeSilver/getAward?r=0.{random_t}&captcha={captcha}'.format(random_t = generate_16_integer(), captcha = captcha)
    response = requests.get(url, headers=headers)
    a = loads(response.content.decode('utf-8'))
    if response.status_code != 200 or a['code'] != 0:
        print(a['msg'])
        return [int(a['code']), 0]
    else:
        return [int(a['data']['awardSilver']), int(a['data']['silver'])]

#----------------------------------------------------------------------
def award_requests(headers):
    url = 'http://live.bilibili.com/freeSilver/getSurplus?r=0.{random_t}'.format(random_t = generate_16_integer())
    response = requests.get(url, headers=headers)
    a = loads(response.content.decode('utf-8'))
    if response.status_code != 200 or a['code'] != 0:
        return False
    else:
        return True

#----------------------------------------------------------------------
def read_cookie(cookiepath):
    """str->list
    Original target: set the cookie
    Target now: Set the global header"""
    print(cookiepath)
    try:
        cookies_file = open(cookiepath, 'r')
        cookies = cookies_file.readlines()
        cookies_file.close()
        return cookies
    except Exception:
        return ['']

#----------------------------------------------------------------------
def captcha_wrapper(headers):
    """"""
    captcha_link = get_captcha_from_live(headers)
    captcha_text = image_link_ocr(captcha_link)
    answer = ''
    if safe_to_eval(captcha_text):
        try:
            answer = eval(captcha_text)  #+ -
        except NameError:
            answer = ''
    return answer

#----------------------------------------------------------------------
def usage():
    """"""
    print("""Auto-grab

    -h: 帮助:
    这个。

    -c: Cookies:
    默认: ./bilicookies
    Cookie的位置

    -l: 除错log
    默认: INFO
    INFO/DEBUG
    """)

#----------------------------------------------------------------------
def main(headers = {}):
    """"""
    try:
        time_in_minutes, silver = get_new_task_time_and_award(headers)
    except TypeError:
        print('你今天的免费银瓜子已经领完了，明天再来吧~')
        exit()
    print('预计下一次领取需要{time_in_minutes}分钟，可以领取{silver}个银瓜子'.format(time_in_minutes = time_in_minutes, silver = silver))
    now = datetime.datetime.now()
    picktime = now + datetime.timedelta(minutes = time_in_minutes) + datetime.timedelta(seconds = 10)
    while (picktime - datetime.datetime.now()).seconds / 60 > 0 and ((picktime - datetime.datetime.now()).seconds / 60) <= 10:
        if not send_heartbeat(headers):
            print('还剩下'+str((picktime - datetime.datetime.now()).seconds / 60)+'分钟……')
            time.sleep(60)
    while not award_requests(headers):
        time.sleep(10)
    answer = 0
    award, nowsilver = [0, 0]
    print('开始领取！')
    for i in range(1, 11):
        answer = captcha_wrapper(headers)
        count = 1
        while answer == '':
            print('验证码识别错误，重试第'+str(count)+'次')
            answer = captcha_wrapper(headers)
            count += 1
        award, nowsilver = get_award(headers, answer)
        if award > 0:
            break
        else:
            print('错误，重试第{i}次'.format(i = i))
            time.sleep(5)
    print('成功！得到'+str(award)+'个银瓜子，你现在有'+str(nowsilver)+'个银瓜子')
    return award

if __name__=='__main__':
    argv_list = []
    argv_list = sys.argv[1:]
    cookiepath,LOG_LEVEL = '', ''
    try:
        opts, args = getopt.getopt(argv_list, "hc:l:",
                                   ['help', "cookie=", "log="])
    except getopt.GetoptError:
        usage()
        exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit()
        if o in ('-c', '--cookie'):
            cookiepath = a
            # print('aasd')
        if o in ('-l', '--log'):
            try:
                LOG_LEVEL = str(a)
            except Exception:
                LOG_LEVEL = 'INFO'
    logging.basicConfig(level = logging_level_reader(LOG_LEVEL))
    if cookiepath == '':
        cookiepath = './bilicookies'
    if not os.path.exists(cookiepath):
        print('Cookie文件未找到！')
        print('请将你的Cookie信息放到\"'+cookiepath+'\"里')
        exit()
    cookies = read_cookie(cookiepath)[0]
    if cookies == '':
        print('不能读取Cookie文件，请检查')
        exit()
    headers = {
        'accept-encoding': 'gzip, deflate, sdch',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.16 Safari/537.36',
        'authority': 'live.bilibili.com',
        'cookie': cookies,
    }
    while 1:
        try:
            main(headers)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print('错误！ {e}'.format(e = e))
            traceback.print_exc()
