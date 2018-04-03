#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import numpy as np

reload(sys)
sys.setdefaultencoding('utf')
import csv
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus import PlaintextCorpusReader
from GetInformation import GetFilePathRoot
from gensim.models import word2vec
import logging

# + 清洗文本 sanitizationtxt
# + 预处理文本 predeal
# + 生成字典 directory
# + 生成词向量 model
# + 根据单词 diff图片：改进使用 dot
# + 获得单词的相似度 smailer
class ExtractModeTask:
    (EXTRACT, MERGE) = range(2)

class ExcateMode:
    count = 0
    def __init__(self):
        '初始化爬取所需要的信息'
        ExcateMode.count += 1
        # 初始化 使用的项目 GithubRepo
        self.initlog()
        self.loaddiff()
    def loaddiff(self):
        corpus_root = str(os.path.join(GetFilePathRoot.get_root_dir(), "data"))
        ##中文目录乱码
        corpus_root = unicode(corpus_root, "GB2312")
        self.logger.info(corpus_root)
        pattern_1 = r".*/diff1/.*\.txt"
        self.logger.info("加载语料库 lazyload")
        self.diff1 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_1)
        self.logger.info("加载语料库 完毕")

    def log(self,type):
        import json
        if not os.path.exists(self.logfile):
            load_dict={'extract': False,'merge':False}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            print load_dict
            load_f.close()
            if type == ExtractModeTask.MERGE:
                load_dict['merge'] = True
            if type == ExtractModeTask.EXTRACT:
                load_dict['extract'] = True

            logging.info(load_dict)
            self.merge = load_dict['merge']
            self.extract = load_dict['extract']

        # print "++++++++++++++++++++++++++++",load_dict
        with open(self.logfile, "w") as dump_f:
            json.dump(load_dict, dump_f)
            dump_f.close()

    def initlog(self):
        self.logfile =  os.path.join(GetFilePathRoot.get_root_dir(),"data2","ExtractModel.txt")
        print self.logfile

        self.merge =False
        self.extract =False

        self.start_prefix = "##### start"
        self.change_prefix = "###### change :"
        self.name_prefix = "###### name :"
        self.end_prefix = "##### end"
        self.model_corpus_java_file = os.path.join(GetFilePathRoot.get_root_dir(), "data4", "model_corpus_java")
        modelfile = self.model_corpus_java_file
        self.model = word2vec.Word2Vec.load(modelfile)

        self.log(None)
        self.outputfile =  os.path.join(GetFilePathRoot.get_root_dir(),"data2","ExtractModelOutput.txt")
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(), "data4")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(), "data4"))
        self.merge_extract_java_file = os.path.join(GetFilePathRoot.get_root_dir(), "data4", "merge_extract_java.txt")



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
        # with open("test_1","r") as f:
        #     file= f.read()
        #     sents = file.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        #     ## 进行处理
        #     dealsents = self.getpredeal(sents=sents)
        #     all = self.getexcate(dealsents)
        # return
        self.logger.info("deal java")
        if not self.extract:
            self.logger.info("extract")
            self.getsents()


    def getfile(self,type="java"):
        fileids=self.diff1.fileids()
        for file in fileids:
            print file
            yield file,self.diff1.raw(file)

    def getsha(self,string):
        from hashlib import sha1
        ss= sha1(string)
        return  ss.hexdigest()

    def getsents(self,type="java"):
        self.logger.info("getsents")
        import json
        # 存储 diff1的语料处理后的模型
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(),"data5")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(),"data5"))
        # 记录原始文件和模型提取结果的映射
        self.sha_name_file=os.path.join(GetFilePathRoot.get_root_dir(),"data2","extract_sha_name_csv")
        i=0
        self.logger.info(i)
        for name,file in self.getfile(type):
            i+=1
            self.logger.info((i,name))
            sents= file.replace("\r\n","\n").replace("\r","\n").split("\n")
            ## 进行处理
            dealsents = self.getpredeal(sents=sents)
            result = self.getexcate(dealsents)
            # 保存的文件 csv
            with open(self.sha_name_file, "a") as f:
                ff = csv.writer(f)
                ff.writerow([self.getsha(name), name])
                f.close()
            if os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(),"data5",self.getsha(name)+".json")):
                continue
            with open(os.path.join(GetFilePathRoot.get_root_dir(),"data5",self.getsha(name))+".json","w") as dump_f:
                json.dump(result, dump_f)
                dump_f.close()
        self.log(ExtractModeTask.EXTRACT)
        return
    def getexcate(self,dealsents):
        all=[]
        commit = []
        file =[]
        change={'del':[],"add":[],"content":[],"diff":[]}
        commitstart = False
        for sent in dealsents:
            if self.start_prefix in sent:
                commitstart = True
            if commitstart == True:
                if self.change_prefix in sent:
                    pass
                elif self.name_prefix in sent:
                    if change !={'del':[],"add":[],"content":[],"diff":[]}:
                        file.append(change)
                        commit.append(file)
                        # print file
                        file =[]
                        change={'del':[],"add":[],"content":[],"diff":[]}
                elif self.start_prefix in sent:
                    pass
                    # print sent
                elif self.end_prefix in sent:
                    commitstart =False
                    if change!={'del':[],"add":[],"content":[],"diff":[]}:
                        file.append(change)
                        commit.append(file)
                        all.append(commit)
                        commit=[]
                        file = []
                        change={'del':[],"add":[],"content":[],"diff":[]}
                else:
                    import re
                    if re.search("(@@\s*\-[0-9]+,[0-9]+\s*\+[0-9]+,[0-9]+\s*@@)", sent, re.I):
                        sent = sent.replace(re.search("(@@\s*\-[0-9]+,[0-9]+\s*\+[0-9]+,[0-9]+\s*@@)", sent, re.I).group(1), "")
                        if change!={'del':[],"add":[],"content":[],"diff":[]}:
                            file.append(change)
                            change={'del':[],"add":[],"content":[],"diff":[]}
                        if sent.replace(" ","")!="":
                            if sent.startswith("-") and sent.replace("-","").replace(" ","")!="" :
                                change['del'].append(sent)
                            elif sent.startswith("+") and sent.replace("+","").replace(" ","")!="" :
                                change['add'].append(sent)
                            else:
                                if sent.replace("-","").replace(" ","")!="" and sent.replace("+","").replace(" ","")!="":
                                    change["content"].append(sent)
                    else:
                        if sent.replace(" ","")!= "":
                            if sent.startswith("-") and sent.replace("-","").replace(" ","") :
                                change['del'].append(sent)
                            elif sent.startswith("+") and sent.replace("+","").replace(" ","") :
                                change['add'].append(sent)
                            else:
                                if sent.replace("-", "").replace(" ", "") != "" and sent.replace("+", "").replace(" ",
                                                                                                                  "") != "":
                                     change["content"].append(sent)
        for commit  in all:
            # print  "aaaaaaa",commit
            for file in commit:
                # print "ffffffff" ,file
                for change in file:
                    # print "cccccccccccc",change
                    # print "            ",change['content']
                    change['diff']=self.getsmailer(change['add'],change['del'])
                    for diff in  change['diff']:
                        if diff[1] in change['add']:
                            # print "            remove add"
                            change['add'].remove(diff[1])
                        if diff[2] in change['del']:
                            # print "            remove del"
                            change['del'].remove(diff[2])
                    # print "            ", change['del']
                    # print "            ", change['add']
                    # for diff in  change['diff']:
                        # print "            dddddddd",diff
        return all
    def emd(self,dist, w1, w2):
        import numpy as np
        import rpy2.robjects as robjects
        # 从R中导入lp.transport()
        robjects.r['library']('lpSolve')
        transport = robjects.r['lp.transport']
        """R的transport()函数用来计算EMD"""
        # transport()的参数
        costs = robjects.r['matrix'](robjects.FloatVector(dist),
                                     nrow=len(w1), ncol=len(w2),
                                     byrow=True)
        row_signs = ["<"] * len(w1)
        row_rhs = robjects.FloatVector(w1)
        col_signs = [">"] * len(w2)
        col_rhs = robjects.FloatVector(w2)
        t = transport(costs, "min", row_signs, row_rhs, col_signs, col_rhs)
        flow = t.rx2('solution')
        dist = dist.reshape(len(w1), len(w2))
        flow = np.array(flow)
        work = np.sum(flow * dist)
        # print "***", (np.sum(flow)),work
        emd = (work+np.float64(2)) /( np.sum(flow)+np.float64(0.1))
        return emd

    def getsentencesmaliar(self, scenceA, scenceB):
        # 使用词向量获得语言相似度，有两个问题，1.时间。2.目前只训练了java
        am=self.model
        import numpy as np
        f1 = scenceA.split()
        f2 = scenceB.split()
        n1 = len(scenceA.split())
        n2 = len(scenceB.split())
        # 创建一个距离矩阵
        dist = np.zeros(n1 * n2)
        for i in range(n1):
            for j in range(n2):
                try:
                    t1 = am.wv[f1[i]]
                except KeyError:
                    continue
                    pass
                try:
                    t2 = am.wv[f2[j]]
                except:
                    continue
                    pass
                dist[i * n2 + j] = self.euclid_dist(t1, t2) + 0.01
        first_signature = np.ones(n1)
        second_signature = np.ones(n2)
        # print  "*****", dist
        return 1.0/(1+self.emd(dist, first_signature, second_signature))

    def euclid_dist(self, feature1, feature2):
        """计算欧氏距离"""
        if len(feature1) != len(feature2):
            print "ERROR: calc euclid_dist: %d <=> %d" % (len(feature1), len(feature2))
            return -1
        return np.sqrt(np.sum((feature1 - feature2) ** 2))

    def getsmailer(self,add=[],dele=[]):
        # 时间代价有点高
        result = []
        if len(add)<=len(dele):
            for sa in add:
                minvalue=0
                temp=("","")
                for sd in dele:
                    import difflib
                    seq = difflib.SequenceMatcher(None, sa, sd)
                    ratio = seq.ratio()
                    # print ratio,(nsa,nsd)
                    smailarvalue=ratio
                    if smailarvalue>minvalue:
                        minvalue = smailarvalue
                        temp=(sa,sd)
                if minvalue!=0:
                    result.append((minvalue, temp[0],temp[1]))
                    # print minvalue,self.getsentencesmaliar(temp[2],temp[3]), (temp[0],temp[1])
        elif len(add)>len(dele):
            for sd in dele:
                minvalue = 0
                temp = ("", "")
                for sa in add:
                    import difflib
                    seq = difflib.SequenceMatcher(None, sa, sd)
                    ratio = seq.ratio()
                    # print ratio, (nsa, nsd)
                    smailarvalue = ratio
                    if smailarvalue > minvalue:
                        minvalue = smailarvalue
                        temp = (sa,sd)
                if minvalue!=0:
                    result.append((minvalue, temp[0], temp[1]))
                    # print minvalue, self.getsentencesmaliar(temp[2], temp[3]), (temp[0], temp[1])
        return result
    def getpredeal(self,sents):
        # 加载停用词表
        newsents=[]
        comment=False
        for line in sents:
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
                if newline != None:
                    newline = " ".join(newline.split(" "))
                    newsents.append(newline)
                newline=None
        result=[]
        for line in newsents:
            newline=""
            for word in line.split(" "):
                if word != "":
                    newline+=word+" "
            result.append(newline)
        return result

if __name__=="__main__":
    # 初始化爬取类
    crawl=ExcateMode()
    count = 0
    if count ==0:
        crawl.getAll()
