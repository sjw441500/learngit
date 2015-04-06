import requests,json,sys,jieba
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from gensim import corpora,models,similarities
from sklearn .cluster import KMeans
##这个地方toplevel12对应的是版块1和2的参数
##toplevel3567对应的事版块3567的参数
##因为版块12结构一样，3567结构一样，所以处理方式一样
Toplevel_12={'1':'%E5%A4%A9%E6%B6%AF%E4%B8%BB%E7%89%88','2':'%E5%A4%A9%E6%B6%AF%E7%BD%91%E4%BA%8B'}
Toplevel_3567={'3':'?topLevel=%E5%A4%A9%E6%B6%AF%E5%88%AB%E9%99%A2','5':'?','6':'?topLevel=%E8%81%8C%E4%B8%9A%E4%BA%A4%E6%B5%81','7':'?topLevel=%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%9B%AD'}
stopword=[line.strip() for line in open('D:\\tianya\\stopword.txt').readlines()]
wholeList=[]
corpus=[]
def Cluster(vectorized,cluster_num):
    km=KMeans(n_clusters=cluster_num,init='random',n_init=1,verbose=1)
    km.fit(vectorized)
    return km
def cutword(text=''):
    cut=list(jieba.cut(text,cut_all=False))
    aftercut=list(set(cut)-set(stopword))
    if '\n' in aftercut:
        aftercut.remove('\n')
    if '\u3000' in aftercut:
        aftercut.remove('\u3000')
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
    weight=tfidf.toarray()
    for i in range(len(weight)):
        print (u"-------这里输出第,"+str(i)+u",类文本的词语tf-idf权重------")
        for j in range(len(word)):
            print (word[j],weight[i][j])
    return vectorized
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
                while block_r.status_code!=200:
                    block_r=requests.get('http://wireless.tianya.cn/v/forumStand/list',params=payload)
        #print(block_r.json())
        print('==========================block'+str(temp_num)+'=======================================')
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
        for listCount in range(3):
        ######in range(len(passage_list)):
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
            #print(rjson)
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
                tempc=dict(comment_list[replyCount])
                tempcon=tempc['con']
                if tempcon!='已删除' :
                    con+=tempcon
            cutcon,corcut=cutword(text=con)
            #print('======================'+str(listCount)+'===================')
            wholeList+=cutcon
            corpus.append(corcut)
            block_title_content.append({'categoryName':category_name,'passage title':passage_title,'content':con})
            #words="/".join(jieba.cut(con))
            #print(words)
            #存储部分
            #mongoOp.insert(block_title_content)
def getTopics():
    global corpus
    dictionary=corpora.Dictionary(corpus)
    model=models.ldamodel.LdaModel(corpus,num_topics=100,id2word=dictionary.token2id)
    topics=[model[c] for c in corpus]
    return topics
def main():
    global wholeList
    get4()
    vectorized=tfidf(wholeList)
    km=Cluster(vectorized,3)
    print(km.cluster_centers_)
    


        
    
        
    
    
    
    
    
    
