#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests,json,sys,MongoOperation
sys.path.append('C:/Users/Administrator/Desktop')
mongoOp=MongoOperation.MongoOperation()
#
#
#
#
#
#获取版块索引
r=requests.get('http://wireless.tianya.cn/v/proxy/qing/getLeftNavByTopLevel')
print(r.json())
print('=================================================================')
rjson=dict(r.json())
data=rjson['data']
lst=data['list']
m=lst[0]
sublist=m['sublist']
list_num=len(sublist)
#temp_num=0
#title_content=[]
#遍历每个版块
for temp_num in range(list_num):
    n=sublist[temp_num]
    BlockId=str(n['id'])
    payload={'categoryId':BlockId,'pageSize':100,'orderBy':2}
    try:
        block_r=requests.get('http://wireless.tianya.cn/v/forumStand/list',params=payload)
    except Exception as e:
            while block_r.status_code!=200:
                block_r=requests.get('http://wireless.tianya.cn/v/forumStand/list',params=payload)
    #print(block_r.json())
    print('=================================================================')
    #获取每个版块的文章索引
    rjson=dict(block_r.json())
    if rjson['success']!=1:
        temp_num-=1
        continue
    passage_list=rjson['data']['list']
    #print(len(passage_list))
    #listCount=0
    block_title_content=[]
    #遍历板块下的每篇文章
    '''先打三篇'''
    #for listCount in range(3):
    for listCount in range(len(passage_list)):
    #len(passage_list):
        noteId=passage_list[listCount]['noteId']
        title=passage_list[listCount]['title']
        forumStand='forumStand/list/'+str(BlockId)
        payload={'categoryId':BlockId,'noteId':noteId,'pageNo':1,'sourceAddress':forumStand}
        try:
            r=requests.get('http://wireless.tianya.cn/v/forumStand/content',params=payload)
        except Exception as e:
            while r.status_code!=200:
                r=requests.get('http://wireless.tianya.cn/v/forumStand/content',params=payload)
        rjson=dict(r.json())
        print(rjson)
        if rjson['message']=='帖子不存在'or rjson['success']!=1:
            continue
        #if comment_data:
        comment_data=rjson['data']
        comment_list=comment_data['list']
        #else:
            #comment_list=[]
        category_name=comment_data['categoryName']
        writer=comment_data['authorId']
        passage_title=comment_data['title']
        #print(comment_data)
        #print(comment_list)
        #print(writer)
        #print(passage_title)
        #print(len(comment_list))
        #replyCount=0
        con=''
        #遍历文章内容
        for replyCount in range(len(comment_list)):
        #len(comment_list):
            tempc=dict(comment_list[replyCount])
            tempcon=tempc['con']
            if tempcon!='已删除' :
                con+=tempcon
            #replyCount+=1
        block_title_content.append({'categoryName':category_name,'passage title':passage_title,'content':con})
        #存储部分
        mongoOp.insert(block_title_content)
        #listCount+=1
        #print(con)
        #print(title_content)
    #temp_num+=1
