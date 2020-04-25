#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
import urllib.request
import sys
import socket
from time import strftime
import time
import pickle
import os
import feedparser
import random
import re
import json
import gzip
import urllib
import threading
import requests
from bs4 import BeautifulSoup as bs
from multiprocessing.connection import Listener, Client
qq_addr = ("127.0.0.1",6240)
listener = Listener(qq_addr, authkey=b'toirc_password')
sendcomm_addr = ("127.0.0.1",6241)
sendcomm = None

filters = re.compile(r'<[^>]+>',re.S)
times = strftime("%H:%M:%S")
reminder = {}
chats = [("-","-","no message")]
news = feedparser.parse('https://www.solidot.org/index.rss').entries
lastPublished = ""
startoday = one_day = two_day = three_day = four_day = ''
forecast = []
super_lock = False


irc = 'irc.freenode.net'

port = 6667
channel = '#jasonfamily'
sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.connect((irc, port))
print(sck.recv(4096).decode())
sck.send('NICK GeneBot\r\n'.encode())
sck.send('USER GeneBot GeneBot GeneBot :GeneBot Better\r\n'.encode())
sck.send(('JOIN ' + channel + '\r\n').encode())

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

def send(string):
    sck.send((str+'\r\n').encode())
    print('sent' , str+'\r\n')

def push(string):
    string.replace("\r"," ")
    string.replace("\n"," ")
    sck.send((u'PRIVMSG #jasonfamily :'+string+u'\r\n').encode())
    print((u'PRIVMSG #jasonfamily :'+string+u'\r\n'))

def refreshNews():
    news = feedparser.parse('https://www.solidot.org/index.rss').entries

def say(word):
    if True:#HACK
        if len(word)<=225:
            push(word)
        else:
            n=0
            while n<len(word):
                if n+225<len(word):
                    push(word[n:(n+225)])
                    n=n+225
                    time.sleep(0.2)
                else:
                    push(word[n:])
                    n=len(word)
    else:
        push("包含不文明字符，已放弃")

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

def thCoolQ():
    global chats,listener,sendcomm_addr,sendcomm
    print("now you can start main Nonebot program...")
    conn = listener.accept()
    print("Connected with Nonebot.(1/2)")
    time.sleep(2)
    sendcomm = Client(sendcomm_addr,authkey=b'toirc_password')
    print("Connected with Nonebot.(2/2)")
    print("Mutual Connection Established.")

    time.sleep(5)
    while True:
        (commtype,nick, content) = conn.recv()
        if commtype=="msg":
            print("new message: "+nick+" says "+content)
            push(nick+" says: "+content)
            chats.append((time.strftime("%Y-%m-%d %H:%M:%S"), nick, content))
        if commtype=="err":
            push("error in doing prev action.")

t = threading.Thread(target=thCoolQ,args=())
t.start()

while True:
    data = sck.recv(4096).decode()
    print(data)
    if data.find('PING') != -1:
        sck.send(('PONG ' + data.split() [1] + '\r\n').encode())
    elif data.find ( 'PRIVMSG' ) != -1:
        nick = data.split ( '!' ) [ 0 ].replace ( ':', '')
        #word = data.split ( ':' ) [ 2: ].strip()
        word = data[data.find(":",data.find(":")+1)+1:].replace("\r","").replace("\n","").strip()
        print("nick=",nick,",data=",data,"word=",word)
        # Basic Conversations ---------------------------------
        if (word=='hello'):
            push("hi!")
        if (word=='hi'):
            push("hello!")
        if (word[:4]=="echo"):
            say(word[5:])
        # Help ------------------------------------------------
        if (word=='help'):
            push("GeneBot V3.0")
            push("Part of an attempt to take back control of the Internet by @pityhero233")
            push("Current Functions： remind calc time hi hello news newsall weather rain exec search rain synthesis msg")
            push("For any questions please email: shizhengyu93@hotmail.com")
        if (word=='msg'):
            push("last message received at "+chats[-1][0]+" , sent by "+chats[-1][1]+" , he/she said "+chats[-1][2])
        if (word=='time'):
            push("Current Time of Server:"+time.strftime('%Y-%m-%d %H:%M:%S'))
        if (word[:6]=='remind'):
            try:
                _,tuser,tword = word.split(" ",)
                reminder[tuser]=nick+":"+tword+" ("+time.strftime('%Y-%m-%d %H:%M:%S')+")"
                push("Okay. I will remind "+tuser+" when he is around.")
            except:
                push("Faulty format. Remind cancelled. remind [user] [content].")
        if (word[:4]=='calc'):
            try:
                _,exp = word.split(" ",1)
                push("Ans = "+str(eval(exp)))
            except:
                push("calc is a basic calculator by eval function of IRC.")
                push("Error in dealing the expression.")
        if (word=='news'):
            try:
                refreshNews()
                if lastPublished!=news[0].published:
                    print("New news available … Pushing newest to you")
                    tot=0;totmax=len(news)-1;
                    # while news[tot].published!=lastPublished and tot<=totmax:
                    if True:
                        lastPublished = news[tot].published
                        inner = killHTMLTags(news[tot].summary)
                        title = killHTMLTags(news[tot].title)
                        ptime = news[tot].published
                        say(title)
                        time.sleep(0.1)
                        say(inner)
                        time.sleep(0.06)
                        say(ptime)
                        # tot=tot+1;
                else:
                    say("All news were read.")
                    say("Latest update time: "+lastPublished)
            except:
                say("Error in fetching news.")

        if (word=='newsall'):
            try:
                refreshNews()
                tot=0;totmax=len(news)-1
                tsummary = ""
                while tot<=5:#news[tot].published!=lastPublished and
                    lastPublished = news[tot].published
                    inner = killHTMLTags(news[tot].summary)
                    title = killHTMLTags(news[tot].title)
                    ptime = news[tot].published
                    tsummary = tsummary + "\n" + title
                    tot = tot + 1;
                say(tsummary)
                time.sleep(0.2)

                if tot==0:
                    say("All news were read.")
            except:
                print("Error in fetching news.")
        if (word[:7]=="weather"):
            cityname = "杭州"
            if len(word)>9:
                _,cityname = word.split(" ")
            try:
                getWeather(cityname)
                print('StArToDaY='+startoday)
                push(startoday)
                time.sleep(0.5)
                push(one_day)
            except:
                push("读取错误。")
        if (word=="rain"):
            cityname = "杭州"
            if len(word)>6:
                _,cityname = word.split(" ")
            try:
                getWeather(cityname)
                flag = False;
                for i in range(0,5):
                    if forecast[i].get('type').find('雨')!=-1:
                        push('第'+ str(i) +'天将会下'+forecast[i].get('type'))
                        flag=True

                if not flag:
                    push('No rain in recent 4 days')
            except:
                push("Error in reading")
        if (word[:4]=="exec"):
            if (nick.lower()=="theexclusivelyadmin" and not super_lock):
                push("access granted.")
                try:
                    _,para = word.split(" ",1)
                    os.system(para)
                except:
                    push("execution failed.")
            else:
                super_lock = True;
                push("access denied.")
                push("your attempt had been noted.")
        if (word[:5]=="music"): #mpc port
            if (word[6:]=="play") or word=="music":
                res = os.popen("mpc play")
                cnta = 0
                for line in res:
                    if len(line)>4 and cnta<2:
                        cnta=cnta+1
                        say(line)

            if (word[6:]=="pause"):
                res = os.popen("mpc pause")
                cnta = 0
                for line in res:
                    if len(line)>4 and cnta<2:
                        cnta=cnta+1
                        say(line)
            if (word[6:]=="add"):
                os.system("mpc clear")
                os.system("mpc add /")
                say("done.")
            if (word[6:12]=="search"):
                try:
                    typ,que = word[13:].split(" ")
                    res = os.popen("mpc search "+typ+" "+que)
                    cnta = 0
                    for line in res:
                        if len(line)>3:
                            cnta=cnta+1
                            if cnta==1:
                                say("first result: "+line)
                    say(str(cnta)+" results found.")
                except:
                    say("error in syntax: music search [field=any] [pattern]")
            if (word[6:16]=="searchplay"):
                try:
                    typ,que = word[17:].split(" ")
                    res = os.popen("mpc searchplay "+typ+" "+que)
                    cnta = 0
                    for line in res:
                        if len(line)>3:
                            cnta=cnta+1
                            if cnta==1:
                                say(line)
                except:
                    say("error in syntax: music searchplay [field=any] [pattern]")
            if (word[6:]=="next" or word[6:]=="n"):
                res = os.popen("mpc next")
                cnta = 0
                for line in res:
                    if len(line)>4 and cnta<2:
                        cnta=cnta+1
                        say(line)
            if (word[6:]=="prev" or word[6:]=="p"):
                res = os.popen("mpc prev")
                cnta = 0
                for line in res:
                    if len(line)>4 and cnta<2:
                        cnta=cnta+1
                        say(line)
            if (word[6:]=="shutffle" or word[6:]=="s"):
                res = os.popen("mpc shuffle")
                cnta = 0
                for line in res:
                    if len(line)>4 and cnta<2:
                        cnta=cnta+1
                        say(line)
            # if word[4:]=="http":
        #     say(nick+": "+getTitle(validate_url(word)))
        if (word[:9]=="synthesis"):
            os.system("echo \""+word[9:]+"\" |espeak")
            say("speaked out.")
        if (word[:4]=="send"):
            if (word.find(" ")<=0):
                say("Format incorrect. Usage: send [qqid] [content]")
            else:
                qqid = word.split(" ")[1]
                sendcomm.send(("SEND", qqid, word[6+len(qqid):]))

        if (word[0]=="@"):
            if (word[1]==" "):
                sendcomm.send(("SENDLAST", "", word[2:]))
            else:
                uname = word.split(" ")[0][1:]
                sendcomm.send(("SENDUSER", uname, word[len(uname)+2:]))

    elif data.find( 'JOIN')!=-1:
        for (tuser,tword) in reminder.items():
            if ((data).lower().find(tuser)!=-1):
                push(tuser+","+"有一条您的留言。")
                push(tword)
                reminder.pop(tuser)
        print('find done.')
