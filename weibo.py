# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 20:11:26 2018

@author: 15282
"""
import requests
import math
import re
import os
from selenium import webdriver
# 
headers = {
    "Cookies":'_T_WM=a02a23854d978343869e247a3b321196; WEIBOCN_FROM=1110006030; TMPTOKEN=6iWva0uXbreGiUhPr0lzn44OaVzbTQjBVtrE1PEQbzyWxEzpSDoa396H2emKgW41; SUB=_2A253o7x2DeRhGeNG6FsY-CzIwjyIHXVVb8Q-rDV6PUJbkdANLVH_kW1NS0MyJG0rHuuFKnbi_sB8Zx3lIvKVNIPC; SUHB=05i684jgY6_iUN; SCF=Aq2xMUsTVfZvNGXGJsfXRDQfTk9k5BecnA85BRY8ISmD7ZwR890ACF4hwrlpQNrC_MgVij9lnVptNC9zQN9JJEs.; SSOLoginState=1520946214; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1076031732927460%26fid%3D1076031732927460%26uicode%3D10000011',
   "User-Agent":'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
}

#删除不必要的字符
pattern1 = re.compile(r'(回复)?<a.*?</a>:?')
pattern2 = re.compile(r'<span.*?</span>')
pattern3 = re.compile(r'^回复:')

#存储路径
path = "D:/uids/";
#根据userid找到该userid关注的人
def get_pattern(user_id):
    page = 1;
    #new_uids存放该id关注的人 并返回
    new_uids = []; 
    
    #首先获取关注总人数 并确定多少网页
    raw_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_'+user_id+'&page='+str(page);
    #单独爬取第一页 为了获取total
    
    total = 0
    try:    
        r = requests.get(raw_url,headers = headers)
        json_text = r.json()
        total = json_text['data']['cardlistInfo']['total']
        total = math.ceil(int(total)/20) #一页20个关注人
    except:
        print(raw_url)
        print("not total")
        return None  #如果该用户没有任何关注 则直接返回
    #爬取关注人列表
    for page in range(1,total+1):
        raw_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_'+user_id+'&page='+str(page);
        try:
            r2 = requests.get(raw_url,headers = headers)
            json_text2 = r2.json()
            user2 = json_text2['data']['cards'][-1]['card_group']   #这里为一个group
            
            for d in user2:
                uid = d['user']['id']
                new_uids.append(str(uid))
        except:
            print(raw_url)
            print("get pattern error")
            continue
    #写入文件
    filename = path + "train.txt";
    with open(filename,'a',encoding = "utf8") as f:
        for id in new_uids:
            f.write(user_id)
            f.write(" ")
            f.write(id)
            f.write("\r\n")
    return new_uids;
#以某个用户为中心爬取他关注的好友 再爬取他关注的好友的关注的好友 依次类推
def getuids():
    if not os.path.exists(path):
        os.makedirs(path)
    f = open(path+"train.txt",'w');
    f.close();
    f = open(path+"user2id.txt","w");
    f.close()
    totaluids = ["1537790411"]; #存放总的uid 用于爬取微博
    preuids = ["1537790411",] #用于迭代

    for i in range(1,3):
        newuids = [];
        for id in preuids:
            temp = get_pattern(str(id)) #获取他关注的好友
            if temp is None:
                continue
            newuids.extend(temp)
        preuids = newuids;
        totaluids.extend(newuids)
    #写入文件
    filename = path+"user2id.txt";
    index = 1;
    totaluids = list(set(totaluids))
    with open(filename,'a',encoding = "utf8") as f:
        for id in totaluids:
            f.write(id);
            f.write(" ");
            f.write(str(index));
            f.write("\r\n")
            index = index+1
    return totaluids
    
def filter_emoji(desstr,restr=''):  
    try:  
        co = re.compile(u'[\U00010000-\U0010ffff]')  
    except re.error:  
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')  
    return co.sub(restr, desstr)        
def get_weibo(user_id):
    raw_weibo = [] #放微博
    
    #获取containerid
    user_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + user_id
    try:
        r = requests.get(user_url,headers = headers)
        json_text = r.json()
    except:
        print(user_url)
        print("获取containerid失败")
        return None
    #我也不懂为啥这里两个网页居然不一样 看见bug这样写的 不怎么规范
    try:   
        containerid = json_text['data']['tabsInfo']['tabs'][1]['containerid']
    except:
        containerid = json_text['data']['tabsInfo']['tabs']["1"]['containerid']

    page = 1;
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid={}&page={}'.format(user_id,containerid,page)

    total_pages = 0;
    #获取总微博数
    try:
        r = requests.get(weibo_url,headers = headers)
        #print(weibo_url)
        json_text = r.json()
        total_weibos = json_text['data']['cardlistInfo']['total']
        total_pages = math.ceil(total_weibos/10)
    except:
        print(weibo_url)
        print("获取weibo total失败")
        return None;
    total_pages = min(total_pages,80);
    for page in range(1,total_pages+1):
        weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid={}&page={}'.format(user_id,containerid,page)
        
        
        try:
            r= requests.get(weibo_url,headers = headers)
            json_text = r.json()
            datas = json_text['data']['cards']
            for d in datas:
                try:
                    uid = d['itemid'].split('_-_')[-1]
                    #除去无用的
                    text = d['mblog']['text']
                    text = re.sub(pattern1,'',text,0)
                    text = re.sub(pattern2,'',text,0)
                    text = filter_emoji(text)
                    if uid != '' and text.strip() != "" and text.strip() != " ":
                        #uids.append(uid)
                        raw_weibo.append(text)
                except:
                    continue
        except:
            print(weibo_url)
            print("获取weibo失败")
            continue
        finally:
            r.close()
    #写入文件
    f1 = open(text_path,'w',encoding = 'utf8')
    f1.close()
    f1 = open(text_path,'a',encoding = 'utf8')
    for weibo in raw_weibo:
         f1.write(weibo)
         f1.write("\r\n")
    f1.close()


if __name__ =="__main__":
    #获取他关注人的信息
    #totaluids = getuids()
    #get_weibo("1537790411")
    with open(r"D:\uids\user2id.txt",'r') as f:
        t = f.read()
    tt = t.split()
    t = tt[0:-1:2]
    for id in t:
        text_path = path + str(id) + '.txt';
        if not os.path.exists(text_path):

            print(id)
            get_weibo(id)
        
    