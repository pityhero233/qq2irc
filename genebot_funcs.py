#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import urllib.request
import socket
from time import strftime
import time
import pickle
import os
import feedparser
import re
import json
import gzip
import urllib

import requests
from bs4 import BeautifulSoup as bs
#imp.reload(sys)
# sys.setdefaultencoding('utf8')
filters = re.compile(r'<[^>]+>',re.S)
times = strftime("%H:%M:%S")
reminder = {}
news = feedparser.parse('https://www.solidot.org/index.rss').entries
lastPublished = ""
startoday = one_day = two_day = three_day = four_day = ''
forecast = []
super_lock = False
#reminder = pickle.load('reminders.pkl')FIXME

irc = 'irc.freenode.net'



# Check https://regex101.com/r/A326u1/5 for reference
DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)" # http basic authentication [optional]
    r"(?:(?:(?=\S{0,253}(?:$|:))" # check full domain length to be less than or equal to 253 (starting after http basic auth, stopping before port)
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+" # check for at least one subdomain (maximum length per subdomain: 63 characters), dashes in between allowed
    r"(?:[a-z0-9]{1,63})))" # check for top level domain, no dashes allowed
    r"|localhost)" # accept also "localhost" only
    r"(:\d{1,5})?", # port [optional]
    re.IGNORECASE
)
SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$", # scheme: http(s) or ftp(s)
    re.IGNORECASE
)

def validate_url(url: str):
    url = url.strip()

    if not url:
        raise Exception("No URL specified")

    if len(url) > 2048:
        raise Exception("URL exceeds its maximum length of 2048 characters (given length={})".format(len(url)))

    result = urllib.parse.urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        raise Exception("No URL scheme specified")

    if not re.fullmatch(SCHEME_FORMAT, scheme):
        raise Exception("URL scheme must either be http(s) or ftp(s) (given scheme={})".format(scheme))

    if not domain:
        raise Exception("No URL domain specified")

    if not re.fullmatch(DOMAIN_FORMAT, domain):
        raise Exception("URL domain malformed (domain={})".format(domain))

    return url

def killHTMLTags(raw):
    return filters.sub('',raw)



def refreshNews():
    global news
    news = feedparser.parse('https://www.solidot.org/index.rss').entries

def getWeather(cityname):
    global forecast,startoday,one_day,two_day,three_day,four_day
    #访问的url，其中urllib.parse.quote是将城市名转换为url的组件
    url = 'http://wthrcdn.etouch.cn/weather_mini?city='+urllib.parse.quote(cityname)
    #发出请求并读取到weather_data
    weather_data = urllib.request.urlopen(url).read()
    #以utf-8的编码方式解压数据
    weather_data = gzip.decompress(weather_data).decode('utf-8')
    #将json数据转化为dict数据
    weather_dict = json.loads(weather_data)
    print(weather_dict)
    if weather_dict.get('desc') == 'invilad-citykey':
        print("输入的城市名有误")
    elif weather_dict.get('desc') =='OK' :
        forecast = weather_dict.get('data').get('forecast')
        startoday = '城市：'+weather_dict.get('data').get('city') +' ' \
                  +'日期：'+forecast[0].get('date') + ' '\
                  +'温度：'+weather_dict.get('data').get('wendu') + '℃ ' \
                  +'高温：'+forecast[0].get('high') + '℃ ' \
                  +'低温: '+forecast[0].get('low') + '℃ ' \
                  +'风向：'+forecast[0].get('fengxiang') +' '\
                  +'风力：'+forecast[0].get('fengli') + ' '\
                  +'天气：'+forecast[0].get('type') + ' '\
                  +'感冒：'+weather_dict.get('data').get('ganmao') + ' '
        print("STARTODAY="+startoday)
        one_day    ='日期：'+forecast[1].get('date')+' ' \
                   +'天气：'+forecast[1].get('type')+' '\
                   +'高温：'+forecast[1].get('high')+' '\
                   +'低温：'+forecast[1].get('low')+' '\
                   +'风向：'+forecast[1].get('fengxiang')+' '\
                   +'风力：'+forecast[1].get('fengli')+' '

        two_day   = '日期：' + forecast[2].get('date') + ' ' \
                  + '天气：' + forecast[2].get('type') + ' ' \
                  + '高温：' + forecast[2].get('high') + ' ' \
                  + '低温：' + forecast[2].get('low') + ' ' \
                  + '风向：' + forecast[2].get('fengxiang') + ' ' \
                  + '风力：' + forecast[2].get('fengli') + ' '

        three_day = '日期：' + forecast[3].get('date') + ' ' \
                  + '天气：' + forecast[3].get('type') + ' ' \
                  + '高温：' + forecast[3].get('high') + ' ' \
                  + '低温：' + forecast[3].get('low') + ' ' \
                  + '风向：' + forecast[3].get('fengxiang') + ' ' \
                  + '风力：' + forecast[3].get('fengli') + ' '

        four_day  = '日期：' + forecast[4].get('date') + ' ' \
                  + '天气：' + forecast[4].get('type') + ' ' \
                  + '高温：' + forecast[4].get('high') + ' ' \
                  + '低温：' + forecast[4].get('low') + ' ' \
                  + '风向：' + forecast[4].get('fengxiang') + ' ' \
                  + '风力：' + forecast[4].get('fengli') + ' '
def getTitle(website):
    try:
        r = requests.get(website)
        soup = bs(r.content,'lxml')
        return (soup.select_one('title').text)
    except:
        return "error"
