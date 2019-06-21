# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 16:57:41 2018

@author: WIN10
"""

import requests 
from pyquery import PyQuery
from fake_useragent import UserAgent
import time
import pandas as pd
import numpy as np
import re
from selenium import webdriver  #模拟登陆

ua = UserAgent()

cookie_collect=[]

def req_header(text_url):
    global juzi_collect
    head_dic={}
    with open (text_url) as f:
        
        line_info=f.readlines()
        juzi_collect=line_info
        for i in line_info:
            #print(i.split(":",1)[1][0:-1])
            head_dic[i.split(":",1)[0]]=i.split(":",1)[1][0:-1]
    f.close()
    return head_dic

def refresh_cookie(driver_handle,num=2):

    driver.refresh()
    change_names=[i['name']+'='+i['value'] for i in driver_handle.get_cookies()]
    return ';'.join(change_names)




def log_in(head_array,log_name='15045632788',log_password='tb940708'): #返回一个cookie
    global driver
    driver = webdriver.Chrome()
    driver.get('https://www.tianyancha.com/login?from=https%3A%2F%2Fwww.tianyancha.com%2Fsearch%3Fkey%3D%25E7%25B2%25BE%25E7%25AE%2597')
    
    # 模拟登陆
    driver.find_element_by_xpath(
        ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input"). \
        send_keys(log_name)
    driver.find_element_by_xpath(
        ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[3]/input"). \
        send_keys(log_password)
    driver.find_element_by_xpath(
        ".//*[@id='web-content']/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[5]").click()
    
    time.sleep(3)
    
    #下面要更改所有要校验并且改动的cookies:    
    return refresh_cookie(driver)



"但是你得考虑下不能让他们用一套jieguo header啊，解决办法就是创建了几个进程，就复制几个"
"你还得考虑一个深拷贝和浅拷贝的问题"
def header_txt():  #返回一个tuple，index 0对应
    txt_company=req_header("head_request清洗脚本.txt")
    print("安好")
    txt_job=req_header("head_request招聘脚本2.txt") #这个是招聘系列的网址header
    return [txt_company,txt_job]


global info_record
info_record=[] #这个是针对每一个搜索词的记录
page=1
url_collect=[]
final_result=[] #这个的搜集的最终录入电子表格的信息
flag=0

def tianyan_page_collect(jieguo,company_name,origin='https://www.tianyancha.com/search?key='):

    jieguo['User-Agent']=ua.random
    #url=origin+company_name
    url=origin+company_name+'&rnd='+str(np.random.randint(999999))
    data={'key':company_name}
    print("公司名字：：   ",company_name)
    return_info=requests.get(url,headers=jieguo,data=data)
    #return_info=requests.get(url,data=data)
    print("怎么回事：：   ",return_info,return_info.text)
    #print(jieguo,return_info)
    jpy=PyQuery(return_info.text)
    
  
    
    company_list=jpy('#web-content > div > div.container-left > div.search-block > div.result-list >div').items()
    search_num=jpy('#search > span.num').text()
           
    #这里有一点需要注意，那就是可能触发反爬虫程序，如果触发，你的searh_num就会变成0了
    print("这是结果数量  ",search_num)
    if  len(search_num) == 0:
        if len(info_record)==0:
            print("要么是根本没有这个公司，要么是触发了反爬虫机制!!")
            return
        else:
            print("到搜索的最后一页了!!")
            return
        
    if int(search_num) >999999:
        print("页数太多!!")
        return
    #天眼只让免费查询100个，一页显示20个，你就按照100个查吧
  
    #global info_record
    global page
    global url_collect #用来定义去重
    global flag
    for it in  company_list:
        
        tp1=dict()
        tp1['公司名']=it('div.content > div.header > a').text()
        tp1['链接地址']=it('div.content > div.header > a').attr('href')       
        tp1['公司驻地']=it('span.site').text()
        tp1['注册时间']=it('div.content > div.info > div:nth-child(3) > span').text()
        if len(tp1['公司驻地'])==0:
            tp1['公司驻地']=it('div.site.-no-score > span').text()
        if len(tp1['公司名'])==0 and len(tp1['公司驻地'])==0:
            print("啊,已到达能查询的最大额度(100个或最大搜索量)")
            return        
        info_record.append(tp1)
    if int(search_num)>20:
        page+=1
        tianyan_page_collect(dict.copy(jieguo),company_name,origin='https://www.tianyancha.com/search/p'+str(page)+'?key=')
        
    
    return info_record


def city_avg_income():
    return

"下面这个函数目前来看似乎还没用到。。"
def tyc_num_trans(tyc_num): #传进来的是一个string，这部分是为了更改匹配tyc-num处理过的数据
    dict_tyc={'3':'1','9':'2','4':'3','8':'4','2':'5','5':'6','6':'7','1':'8','0':'9','7':'0'}#创建对应的字典 正常->转换
    dict_tyc2=dict([val,key] for key,val in dict_tyc.items())#转换->正常
    new_string=''
    for i in tyc_num:
        if i in dict_tyc2.keys():
            new_string+=dict_tyc2[i]
        else:
            new_string+=i
    return new_string
    
    

def process_func(params): #这里执行进程池里面的东西

    i=params[2]
    jieguo=params[0]
    jieguo2=params[1]
    jieguo['User-Agent']=ua.random
    
    data={'url':i['链接地址'],'_':str(np.random.randint(999999))}
       
    #***********************
    data2={"appId":"wx2ca32fcf7804bffc","nonceStr":"3lnxezkn7ty","timestamp":"1531881935","url":"https://www.tianyancha.com/company/24896215","signature":"呱呱"}
    #***********************

    jieguo['Cookie']=refresh_cookie(driver)
    req=requests.get(i['链接地址'],headers=jieguo,data=data)
    
    if req.status_code!=200:
        print("触发反爬虫机制！！")
        return 
    #上面这部分有待商榷，因为拼图验证码返回也是200
    jpy=PyQuery(req.text)
    i['工商注册号']=jpy('#_container_baseInfo > table.table.-striped-col.-border-top-none > tbody > tr:nth-child(1) > td:nth-child(2)').text()
    i['法人代表']=jpy('#_container_baseInfo > table:nth-child(1) > tbody > tr:nth-child(1) > td.left-col.shadow > div > div:nth-child(1) > div.humancompany > div.name > a').text()
    i['注册资本']=jpy('#_container_baseInfo > table:nth-child(1) > tbody > tr:nth-child(1) > td:nth-child(2) > div:nth-child(2)').attr('title')
    i['人员规模']=jpy('#_container_baseInfo > table.table.-striped-col.-border-top-none > tbody > tr:nth-child(5) > td:nth-child(4)').text()
    i['参保人数']=jpy('#_container_baseInfo > table.table.-striped-col.-border-top-none > tbody > tr:nth-child(7) > td:nth-child(2)').text()
    i['公司状态']=jpy('#_container_baseInfo > table:nth-child(1) > tbody > tr:nth-child(3) > td > div.num-opening').text()
    i['公司地址']=jpy('#_container_baseInfo > table.table.-striped-col.-border-top-none > tbody > tr:nth-child(8) > td:nth-child(2)').text()
    #已知每一页最多只能展示出20条信息
    #目前你就先考虑搜集 日期 和 收入吧
    #咱们就找最近100条 或者 1年 招聘信息吧！
    data_job={'ps':'20','pn':'1','name':i['公司名']}
    page_job=1
    job_collect=dict()
    flag_job=0 #跳出while的信号，只需要1次flag_job切换为1，就可以在搜索工作页面上结束工作啦
    url_job=""
    marker="正常"
    
    #print("当前公司是： ",i['公司名'])
    while(1): #这个遍历的每一页
        
        if len(job_collect)>100: #【条件3】已经搜集100个招聘信息了
            break
        data_job['pn']=str(page_job)
        url_job='https://www.tianyancha.com/pagination/recruit.xhtml?ps=20&'+'pn='+str(page_job)+'&name='+i['公司名']
        
        jieguo['Cookie']=refresh_cookie(driver)
        jieguo2['User-Agent']=ua.random
        
        re_job=requests.get(url_job,headers=jieguo2,data=data_job)
        if re_job.status_code!=200:
            print("**********************招聘信息无法看到咯,出现反爬机制********************")
            marker="爬虫禁止"
            #应该在下面实现验证码校验项目
            
            
            
            
            
            break
        #print("当前公司是： ",i['公司名'])
        if len(re_job.text)==0:
            print("无招聘信息，退出了",page_job)
            break
        jpy_job=PyQuery(re_job.text)
        #print("JPY当前公司是： ",i['公司名'])
        itm=jpy_job('table > tbody>tr')
        #print("当前公司是： ",i['公司名'])
        #print("公司名:",i['公司名'],"itm信息: ",itm,"itm.text",itm.text())
        if len(itm.text())==0:
            print("退出在第 ",page_job," 页")
            break
        itm=itm.items()        
        for it in itm: #这个遍历的是每一页的20个工作
            post_day=it('tr>td:nth-child(2)').text()
            #print("当前页面: ",page_job,"当前日期::: ",post_day)
            if len(post_day)==0: #【条件1】无数据了
                flag_job=1
                break
            post_day_timestamp=time.mktime(time.strptime(post_day, "%Y-%m-%d"))
            if time.time()-post_day_timestamp>31536000: #【条件2】距离今日超过1年，停止检索
                flag_job=1
                break
            shouru=it('tr>td:nth-child(4)').text()
            if len(re.findall(r"\d+",shouru))==0: #如果是 “面议” 这类词语
                print(shouru)
                continue
            job_collect[post_day+str(len(job_collect))]= shouru
        if flag_job==1:
            break #while 也break
        page_job+=1
    
    #接下来是统计一下所有工作的平均收入,这里可以做做文章比如收入招聘趋势啦等等
    #print("公司名::  ",i['公司名']," 工作有几个    ",len(job_collect))
    print(i['公司名'],"           ",len(job_collect))
    if len(job_collect)!=0:
        #print(i['公司名'],"           ",len(job_collect))
        total_salary=[]
        for k in job_collect.values():
            
            total_salary.append(np.mean([int(ea) for ea in re.findall(r"\d+",k)]) )
        
        avg_salary=np.mean(total_salary)   
        i['近年平均工资']=avg_salary
    else:
        #print(i['公司名'],"           ",len(job_collect))
        i['近年平均工资']='无法查询'
    i['爬虫状态']=marker
    #avg_income=np.mean(job_collect.values())
    return [i,job_collect]

    
"暂时不考虑url的去重"
"如果按照这个标准没有爬去到的话，说明是‘社会组织’标签"

"※你要针对每个公司的搜索，返回三个，1个是所有的sub页面的连接字典，一个是这个搜索结果返回了多少（这个用来判断这个公司的重名性）"

from multiprocessing import Process
from multiprocessing import Pool



"下面是单线程"

star=time.time()
process_num=7

head_array=header_txt()
new_cookie=log_in(head_array)
head_array[0]['Cookie']=new_cookie
head_array[1]['Cookie']=new_cookie

"※上面完成了 模拟登陆 + cookie获取更新"

yigeshuju=0
while(1):
    com_name=input("请输入查询名称: ")
    if com_name=="Q":
        break
    yigeshuju=tianyan_page_collect(jieguo=dict.copy(head_array[0]),company_name=com_name,origin='https://www.tianyancha.com/search?key=')
    if yigeshuju is None:
        print("重新查询")
    else:
        break
    

series_info=[[dict.copy(head_array[0])]+[dict.copy(head_array[1])]+[i] for i in yigeshuju ]
#series_info是将每一个和可以爬的url和需要的 详细内容 header，以及 对应的job header都封装起来
#这样由于是深拷贝，那么每个进程用的header都哇暖不变
aha=[]
for meige in series_info:
    
    result=process_func(meige)
    if result is None:
        print("****************被反爬了*************")
        print("****************被反爬了*************")
        print("****************被反爬了*************")
        print("****************被反爬了*************")
        print("****************被反爬了*************")
    aha.append(result)

print("耗时::: ",(time.time()-star),' 秒, 对于 ',len(yigeshuju),' 个url们')
#driver.quit()

    
    
    

    