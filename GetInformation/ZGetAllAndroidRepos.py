#!/usr/bin/python
# -*- coding: UTF-8 -*-
from  FindAndroidRepos import  FindAndroidRepos
import GetFilePathRoot
import os
import logging
import csv
class GetAllAndroidRepos:
    count =0
    def __init__(self):
        if not os.path.exists(FindAndroidRepos.resultfile):
            print "FindAndroidRepos first",FindAndroidRepos.resultfile,"not exesit"
        # AndroidRepos.csv 放在该目录下
        self.readfile=os.path.join(GetFilePathRoot.get_root_dir(),"GetInformation", "")
        print self.readfile
        self.initlog()

    def log(self,item):
        import json
        if not os.path.exists(self.logfile):
            load_dict={}

            with open(self.readfile, "r") as f:
               ff = csv.reader(f.read().splitlines())
               i=0
               for it in ff:
                   i+=1
                   if i>1:
                       print it[0]
                       load_dict[it[0]] = False

            self.plan=load_dict
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            if item  in load_dict.keys():
                load_dict[item] = True
                logging.info(load_dict)
            self.plan = load_dict
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
    def initlog(self):
        if not os.path.exists(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2")):
            os.mkdir(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2"))
        self.logfile=os.path.join(GetFilePathRoot.get_root_dir(), "data2", "GetAll.txt")
        self.log(None)
        self.outputfile = os.path.join(GetFilePathRoot.get_root_dir(), "data2", "GetAllOutput.txt")
        import logging
        # 创建一个logger
        self.logger = logging.getLogger('Deal')
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
    def do(self):
        for k, v in self.plan.items():
            if v == False:
                self.logger.debug(k)
                user,repo = k.split("/")
                yield (k, v,user,repo)
    def doallcrawl(self):
        from CrawlGithub import CrawlGithub
        from GithubRepo import GithubRepo
        i=0
        import time
        for d in self.do():
            start = time.time()
            if "." in  str(d[3]):
                pass
            else:
                repo = GithubRepo(str(d[2]), str(d[3]))
                # repo.printInfo()
                # 初始化爬取类
                crawl = CrawlGithub(repo)
                crawl.getAll()
                print str(d[2]),str(d[3]),"." in repo.name
                self.log(str(d[0]))
            end =time.time()
            self.logger.info((d,(end-start)/60,(end-start)%60))
if __name__== "__main__":
    g=GetAllAndroidRepos()
    g.doallcrawl()
