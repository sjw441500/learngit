#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests,json,sys,jieba,numpy
from sklearn import feature_extraction
from numpy import *
from scipy.spatial import distance
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora,models,similarities
from sklearn.cluster import KMeans,MeanShift,estimate_bandwidth
import re
##这个地方toplevel12对应的是版块1和2的参数
##toplevel3567对应的事版块3567的参数
##因为版块12结构一样，3567结构一样，所以处理方式一样
Toplevel_12={'1':'%E5%A4%A9%E6%B6%AF%E4%B8%BB%E7%89%88','2':'%E5%A4%A9%E6%B6%AF%E7%BD%91%E4%BA%8B'}
Toplevel_3567={'3':'?topLevel=%E5%A4%A9%E6%B6%AF%E5%88%AB%E9%99%A2','5':'?','6':'?topLevel=%E8%81%8C%E4%B8%9A%E4%BA%A4%E6%B5%81','7':'?topLevel=%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%9B%AD'}
stopword=[line.strip() for line in open('D:\\tianya\\stopword.txt').readlines()]
wholeList=[]
corpus=[]
def pairwise(corpus,doc_id):
    topics=[model[c] for c in corpus]
    dense=numpy.zeros((len(topics),100),float)
    for ti,t in enumerate(topics):
        for tj,v in t:
            dense[ti,tj]=v
    pairwise=distance.squareform(distance.pdist(dense))
    largest=pairwise.max()
    for ti in range(leng(topics)):
        pairwise[ti,ti]=largest+1
    return pairwise[doc_id].argmin()
def Cluster(vectorized,cluster_num):
    km=KMeans(n_clusters=cluster_num,init='random',n_init=1,verbose=1)
    km.fit(vectorized)
    return km
def cutword(string=''):
    test=re.sub('\d','',string)
    text=re.sub('\s','',test)
    cut=list(jieba.cut(text,cut_all=False))
    aftercut=list(set(cut)-set(stopword))
    #if '\n' in aftercut:
        #aftercut.remove('\n')
    if '\u3000' in aftercut:
        aftercut.remove('\u3000')
    #if ' ' in aftercut:
        #aftercut.remove(' ')
    #print(aftercut)
    midcutup=[]
    for i in range(len(cut)):
        if cut[i] in aftercut:
            midcutup.append(cut[i])
    finalCut=[' '.join(x for x in midcutup)]
    return finalCut,midcutup
def tfidf(textlist=[]):
    vectorizer=CountVectorizer()
    transformer=TfidfTransformer()
    vectorized=vectorizer.fit_transform(textlist)
    tfidf=transformer.fit_transform(vectorized)
    word=vectorizer.get_feature_names()
    #print(tfidf)
    weight=tfidf.toarray()
    #print(weight)
    #for i in range(len(weight)):
        #print (u"-------这里输出第,"+str(i)+u",类文本的词语tf-idf权重------")
        #for j in range(len(word)):
            #print (word[j],weight[i][j])
    return weight,word
def get12(string=''):
    r=requests.get('http://wireless.tianya.cn/v/proxy/qing/getLeftNavByTopLevel?topLevel='+string)
    #print(r.json())
    print('=================================================================')
    rjson=dict(r.json())
    data=rjson['data']
    lst=data['list']
    m=lst[0]
    sublist=m['sublist']
    spider(sublist)
def get3567(string=''):
    r=requests.get('http://wireless.tianya.cn/v/proxy/qing/getLeftNavByTopLevel'+string)
    print(r.json())
    rjson=dict(r.json())
    data=rjson['data']
    lst=data['list']
    sublist=[]
    for m in range(len(lst)):
        sublist+=lst[m]['sublist']
    spider(sublist)
def get4():
    r=requests.get('http://wireless.tianya.cn/v/forumRelation/leftNavById?leftNavId=62')
    print(r.json())
    rjson=dict(r.json())
    data=rjson['data']
    lst=data['list']
    sublist=[]
    for m in range(len(lst)):
        for n in range(len(lst[m]['children'][0]['children'])):
            sublist.append(lst[m]['children'][0]['children'][n])
    spider(sublist)
def spider(sublist=[]):
    global wholeList
    global corpus
    list_num=len(sublist)
    #temp_num=0
    #title_content=[]
    #遍历每个版块
    for temp_num in range(3):
    #######range(list_num):
        n=sublist[temp_num]
        BlockId=str(n['id'])
        payload={'categoryId':BlockId,'pageSize':100,'orderBy':2}
        try:
            block_r=requests.get('http://wireless.tianya.cn/v/forumStand/list',params=payload)
        except Exception as e:
                blocknumber=0
                while block_r.status_code!=200 and blocknumber<3:
                #and blocknumber<3:
                    block_r=requests.get('http://wireless.tianya.cn/v/forumStand/list',params=payload)
                    blocknumber+=1
        print('==========================block'+str(temp_num)+'=======================================')
        #获取每个版块的文章索引
        rjson=dict(block_r.json())
        if rjson['success']!=1:
            temp_num-=1
            continue
        passage_list=rjson['data']['list']
        #print(len(passage_list))
        #block_title_content=[]
        #遍历板块下的每篇文章
        for listCount in range(4):
        ######in range(len(passage_list)):
            noteId=passage_list[listCount]['noteId']
            title=passage_list[listCount]['title']
            forumStand='forumStand/list/'+str(BlockId)
            payload={'categoryId':BlockId,'noteId':noteId,'pageNo':1,'sourceAddress':forumStand}
            try:
                r=requests.get('http://wireless.tianya.cn/v/forumStand/content',params=payload,timeout=5)
            except Exception as e:
                continue
            rjson=dict(r.json())
            #print(rjson)
            if rjson['message']=='帖子不存在'or rjson['success']!=1:
                continue
            comment_data=rjson['data']
            comment_list=comment_data['list']
            category_name=comment_data['categoryName']
            #writer=comment_data['authorId']
            passage_title=comment_data['title']
            con=''
            #遍历文章内容
            for replyCount in range(len(comment_list)):
                tempc=dict(comment_list[replyCount])
                try:
                    tempcon=tempc['con']
                    if tempcon!='已删除' :
                        con+=tempcon
                except Exception:
                    continue
            cutcon,corcut=cutword(string=con)
            print(corcut)
            print('======================'+str(listCount)+'===================')
            wholeList+=cutcon
            corpus.append(corcut)
            #block_title_content.append({'categoryName':category_name,'passage title':passage_title,'content':con})
            
            #存储部分
            #mongoOp.insert(block_title_content)
def getTopics():
    global corpus
    #print(corpus)
    dictionary=corpora.Dictionary(corpus)
    dictionary.save_as_text('D:/tianya/tianyaproject/tmp/tianya1.txt')
    thisCorpus=[dictionary.doc2bow(text) for text in corpus]
    print(thisCorpus)
    corpora.MmCorpus.serialize('D:/tianya/tianyaproject/tmp/tianya1.mm', thisCorpus)
    #下面这部分在处理大规模数据的时候报错
    model=models.ldamodel.LdaModel(corpus=thisCorpus,num_topics=100,id2word=dictionary,alpha=1)
    #topics=[model[c] for c in thisCorpus]
    return model,thisCorpus
def main():
    global wholeList
    get12(string=Toplevel_12['1'])
    #weight,word=tfidf(wholeList)
    model,mycorpus=getTopics()
    topics=[model[c] for c in mycorpus]
    counts=numpy.zeros(100)
    for doc_top in topics:
        for ti,_ in doc_top:
            counts[ti]+=1
    words=model.print_topics(num_topics=50)
    for f in words:
        print(f+'\n')

    


        
    
        
    
    
    
    
    
    
