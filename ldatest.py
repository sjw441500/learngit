from gensim import corpora,models,similarities
import numpy as np
#mm文件是根据结构化数据形如[['天涯','测试','意义'],['沧海','支持','生活']……]生成的mm矩阵
corpus=corpora.MmCorpus('D:/tianya/tianyaproject/tmp/tianya.mm')
print(corpus)
#dict文件是格式为 id: word 的词典
id2word =corpora.Dictionary.load_from_text('D:/tianya/tianyaproject/tmp/tianya.txt')
print(id2word)
#建模，参数分别是从mm中提取的语料库和从id2word中提取的词典
model=models.hdpmodel.HdpModel(corpus,id2word)
