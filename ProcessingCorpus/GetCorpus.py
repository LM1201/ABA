#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8') #允许打印unicode字符
from GetInformation.GithubRepo import  GithubRepo
from GetPatches import GetPatches
from GetInformation import GetFilePathRoot
from pymongo import MongoClient

class GetCorpus:
    def __init__(self):
        self.initlog()
    def initlog(self):
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(), "data2")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(), "data2"))
        self.outputfile = os.path.join(GetFilePathRoot.get_root_dir(), "data2","CorpusOutput.txt")
        import logging
        # 创建一个logger
        self.logger = logging.getLogger("corpus")
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

    def clearall(self):
        client = MongoClient()
        for dbname in client.database_names():
            user_repo = dbname.split("_")
            self.logger.info(user_repo)
            if len(user_repo)<2:
                continue
            repo = GithubRepo(str(user_repo[0]), str(user_repo[1]))
            crawl = GetPatches(repo)
            crawl.cleardiff()
    def getallresult(self):
        i =0
        client = MongoClient()
        num = len(client.database_names())
        for dbname in client.database_names():
            i+=1
            print "------------------------------------------------------"
            print i,num,float(i)/num
            import time
            if i % 100==0:
                time.sleep(5)
            print "------------------------------------------------------"
            user_repo= dbname.split("_")
            self.logger.info(user_repo)
            if len(user_repo)<2:
                continue
            repo = GithubRepo(str(user_repo[0]), str(user_repo[1]))
            crawl = GetPatches(repo)
            crawl.getAll()
    def loadcorpus(self):
        corpus_root = str(os.path.join(GetFilePathRoot.get_root_dir(), "data"))
        ##中文目录乱码
        corpus_root = unicode(corpus_root, "GB2312")
        self.logger.info(corpus_root)

        pattern_1 = r".*/diff1/.*\.txt"
        pattern_2 = r".*/diff2/.*\.txt"
        pattern_3 = r".*/diff3/.*\.txt"
        from nltk.corpus.util import LazyCorpusLoader
        from nltk.corpus import PlaintextCorpusReader
        self.logger.info("加载语料库")
        self.diff1 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_1)
        self.diff2 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_2)
        self.diff3 = LazyCorpusLoader(corpus_root, PlaintextCorpusReader, pattern_3)
        self.logger.info("加载完毕")

if __name__ =="__main__":
    count =2
    if count==0:
        GetCorpus().clearall()
    elif count ==1:
        GetCorpus().getallresult()
    elif count ==2:
        print "loadcorpus"
        GetCorpus().loadcorpus()





