#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf')
import requests
import csv
import logging
from GetInformation.GithubRepo import GithubRepo
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus import PlaintextCorpusReader
from GetInformation import GetFilePathRoot
import matplotlib.pyplot as plt
import networkx as nx
import gensim.corpora
from gensim.models import word2vec

# + 清洗文本 sanitizationtxt
# + 预处理文本 predeal
# + 生成字典 directory
# + 生成词向量 model
# + 根据单词 diff图片：改进使用 dot
# + 获得单词的相似度 smailer
class DealCorpusTask:
    (JAVA_SANIT, JAVA_MERGE, JAVA_DICT, JAVA_MODEL, JAVA_PIC,
     XML_SANIT, XML_MERGE, XML_DICT, XML_MODEL, XML_PIC) = range(10)

class DealCorpus:
    count = 0
    def __init__(self):
        '初始化爬取所需要的信息'
        DealCorpus.count += 1
        # 初始化 使用的项目 GithubRepo
        self.initlog()
        self.loaddiff()
    def loaddiff(self):
        corpus_root = str(os.path.join(GetFilePathRoot.get_root_dir(), "data"))
        ##中文目录乱码
        corpus_root = unicode(corpus_root, "GB2312")
        self.logger.info(corpus_root)
        pattern_1 = r".*/diff1/.*\.txt"
        pattern_2 = r".*/diff2/.*\.txt"
        pattern_3 = r".*/diff3/.*\.txt"

        self.logger.info("加载语料库 lazyload")
        self.diff1 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_1)
        self.diff2 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_2)
        self.diff3 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_3)
        self.logger.info("加载语料库 完毕")
    def log(self,type):
        import json
        if not os.path.exists(self.logfile):
            load_dict={'java_sanit': False,'java_merge':False,'java_dict':False,'java_model':False,
                       'xml_sanit': False, 'xml_merge': False, 'xml_dict': False, 'xml_model': False,}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            print load_dict
            load_f.close()
            if type == DealCorpusTask.JAVA_DICT:
                load_dict['java_dict'] = True
            if type == DealCorpusTask.JAVA_MODEL:
                load_dict['java_model'] = True

            if type == DealCorpusTask.JAVA_MERGE:
                load_dict['java_merge'] = True
            if type == DealCorpusTask.JAVA_SANIT:
                load_dict['java_sanit'] = True

            if type == DealCorpusTask.XML_DICT:
                load_dict['xml_dict'] = True
            if type == DealCorpusTask.XML_MODEL:
                load_dict['xml_model'] = True

            if type == DealCorpusTask.XML_MERGE:
                load_dict['xml_merge'] = True
            if type == DealCorpusTask.XML_SANIT:
                load_dict['xml_sanit'] = True

            logging.info(load_dict)
            self.java_dict = load_dict['java_dict']
            self.java_model = load_dict['java_model']

            self.java_predeal = load_dict['java_merge']
            self.java_sanit = load_dict['java_sanit']

            self.xml_dict = load_dict['xml_dict']
            self.xml_model = load_dict['xml_model']

            self.xml_predeal = load_dict['xml_merge']
            self.xml_sanit = load_dict['xml_sanit']

        # print "++++++++++++++++++++++++++++",load_dict
        with open(self.logfile, "w") as dump_f:
            json.dump(load_dict, dump_f)
            dump_f.close()

    def initlog(self):
        self.logfile =  os.path.join(GetFilePathRoot.get_root_dir(),"data2","DealCorpus.txt")
        print self.logfile
        self.java_dict =False
        self.java_model=False
        self.java_pic= False
        self.java_predeal =False
        self.java_sanit =False
        self.xml_dict = False
        self.xml_model = False
        self.xml_pic = False
        self.xml_predeal = False
        self.xml_sanit = False
        self.log(None)
        self.outputfile =  os.path.join(GetFilePathRoot.get_root_dir(),"data2","DealCorpusOutput.txt")
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(), "data4")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(), "data4"))
        self.merge_corpus_java_file = os.path.join(GetFilePathRoot.get_root_dir(), "data4", "merge_corpus_java.txt")
        self.dict_corpus_java_file=os.path.join(GetFilePathRoot.get_root_dir(),"data4","java_dict_corpus.txt")
        self.model_corpus_java_file=os.path.join(GetFilePathRoot.get_root_dir(),"data4","model_corpus_java")


        import logging
        # 创建一个logger
        self.logger = logging.getLogger("DealCorpus")
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(self.outputfile)
        fh.setLevel(logging.DEBUG)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getAll(self):
        # return
        self.logger.info("deal java")
        if not self.java_sanit:
            self.logger.info("extract")
            self.getsents()
        if not self.java_predeal:
            self.logger.info("merge")
            self.mergecorpus()
        if not self.java_dict:
            self.logger.info("java_dict")
            self.getdict()
        if not self.java_model:
            self.logger.info("java_model")
            self.getmodel()


        self.logger.info("deal xml")
        if not self.xml_sanit:
            self.logger.info("xml_sanit")
        if not self.xml_predeal:
            self.logger.info("predeal")
        if not self.xml_dict:
            self.logger.info("xml_dict")
        if not self.xml_model:
            self.logger.info("xml_model")

    def mergecorpus(self,type="java"):
        if type =="java":
            rootDir=os.path.join(GetFilePathRoot.get_root_dir(),"data3")
            targetfile=self.merge_corpus_java_file
        i = 0
        num=len(os.listdir(rootDir))
        k = open(targetfile, 'w')
        for lists in os.listdir(rootDir):
            path = os.path.join(rootDir, lists)
            i+=1
            self.logger.info((float(i)/num,path))
            with open(path,"r") as f:
                # print f.read()
                k.write(f.read()+"\n")
        k.close()
        self.log(DealCorpusTask.JAVA_MERGE)
        pass


    def getdict(self,type="java"):
        if type == "java":
            self.sourcefilename=self.merge_corpus_java_file
            self.targetfilename=self.dict_corpus_java_file
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        sentences = word2vec.Text8Corpus(self.sourcefilename)  # 加载语料
        dictionary = gensim.corpora.Dictionary(sentences)
        print len(dictionary)
        dictionary.save_as_text(self.targetfilename, sort_by_word=True)
        if type=="java":
            self.log(DealCorpusTask.JAVA_DICT)

    def getmodel(self,type="java"):
        if type == "java":
            self.sourcefilename=self.merge_corpus_java_file
            self.targetfilename=self.model_corpus_java_file
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        sentences = word2vec.Text8Corpus(self.sourcefilename)  # 加载语料
        model = word2vec.Word2Vec(sentences, size=200)  # 训练skip-gram模型; 默认window=5
        # 保存模型，以便重用
        model.save(self.targetfilename)
        if type=="java":
            self.log(DealCorpusTask.JAVA_MODEL)
    def getfile(self,type="java"):
        if type == "java":
            fileids=self.diff2.fileids()
            for file in fileids:
                print file
                yield file,self.diff2.raw(file)
        if type == "xml":
            fileids = self.diff3.fileids()
            for file in fileids:
                print file
                yield file,self.diff3.raw(file)
    def getsha(self,string):
        from hashlib import sha1
        ss= sha1(string)
        return  ss.hexdigest()
    def getsents(self,type="java"):
        self.logger.info("getsents")
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(),"data3")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(),"data3"))
        self.sha_name_file=os.path.join(GetFilePathRoot.get_root_dir(),"data2","DealCorpus_sha_name_csv")
        i=0
        self.logger.info(i)
        for name,file in self.getfile(type):
            i+=1
            self.logger.info((i,name))
            sents= file.replace("\r\n","\n").replace("\r","\n").split("\n")
            result = self.getpredeal(sents=sents)
            with open(self.sha_name_file, "a") as f:
                ff = csv.writer(f)
                ff.writerow([self.getsha(name), name])
                f.close()
            if os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(),"data3",self.getsha(name))):
                continue
            with open(os.path.join(GetFilePathRoot.get_root_dir(),"data3",self.getsha(name)),"w") as f:
                f.write(result)
                f.close()
        self.log(DealCorpusTask.JAVA_SANIT)

    def getpredeal(self,sents):
        # 加载停用词表
        newsents=[]
        stop=["+","-","*","/","%","=","!",">","<","&","|","^","~","?","(",")","[","]","{","}",",",";"]
        comment=False
        for line in sents:
            import re
            if re.search("(@@\s*\-[0-9]+,[0-9]+\s*\+[0-9]+,[0-9]+\s*@@)", line, re.I):
                line= line.replace(re.search("(@@\s*\-[0-9]+,[0-9]+\s*\+[0-9]+,[0-9]+\s*@@)", line, re.I).group(1),"")
                # print line
            if line != u' ':
                newline =None
                if "//" in line:
                    newline = line[0:line.index("//")]
                if "/*" in line:
                    comment =True
                    newline = line[0:line.index("/*")]
                if "*/" in line:
                    newline=line[line.index("*/")+2:len(line) ]
                    # print newline
                    self.logger.info(newline)
                    comment = False
                if "/*"in line and "*/" in line:
                    if line.index("/*")<=line.index("*/"):
                        newline = line[0:line.index("/*")]+line[line.index("*/")+2:len(line)]
                        comment = False
                if comment or newline !=None:
                    pass
                else:
                    newline=line
                if newline !=None:
                    for s in stop:
                        if s in newline:
                            newline=" ".join(newline.split(s))
                    newline= newline.replace("\r\n", " ").replace("\n", " ").replace("\t", " ")
                    newline = " ".join(newline.split(" "))
                    newsents.append(newline)
                newline=None
        result=""
        for line in newsents:
            for word in line.split(" "):
                if word != "":
                    result+=word+" "
        return result


    def gendiffpicture(self, word="activity", type="java", size=3):
        if type=="java":
            modelfile = self.model_corpus_java_file
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        model = word2vec.Word2Vec.load(modelfile)
        G = nx.Graph()
        blacknode = set([])
        def get(startwordlist):
            result = []
            for word in startwordlist:
                y2 = model.most_similar(word,topn=6)  # 6个最相关的
                for item in y2:
                    if not item[0] in blacknode:
                        result.append(item[0])
                        G.add_node(item[0])
                        G.add_weighted_edges_from([(word, item[0], item[1])])
                blacknode.add(word)
            return result

        start = [word]
        i = 0;
        while True:
            i += 1;
            if i == size:
                break
            result = get(start)
            print result
            start = result
        for node in G.nodes():
            print node
        pos = nx.spring_layout(G)
        nx.draw(G, pos=pos, node_color="r", with_labels=True, node_size=900, font_size=10)
        plt.show()

    def getsmailarword(self, word="activity", type="java", number=10):
        '获得相似单词'
        if type == "java":
            modelfile = self.model_corpus_java_file
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        model = word2vec.Word2Vec.load(modelfile)
        return model.most_similar(word, topn=number)

if __name__=="__main__":
    # 初始化爬取类
    crawl=DealCorpus()
    count = 1
    if count ==0:
        crawl.getAll()
    elif count==1:
        # crawl.gendiffpicture(word="intent")
        # crawl.gendiffpicture(word="Intent")
        crawl.gendiffpicture(word=unicode("intent", "utf"))
    elif count == 2:
        for item in crawl.getsmailarword("intent"):
            print item