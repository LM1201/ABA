#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re

import requests
import logging
from GithubRepo import GithubRepo

class CrawlType:
    (ISSUE, COMMIT, COMMENT, EVENT, PULL, FILECHANGE) = range(6)
'爬取类'
class CrawlGithub:
    '爬取类'
    count = 0
    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化爬取所需要的信息'
        CrawlGithub.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg = GithubRepo(user=user, repo=repo)
        self.initlog()

    def log(self,type):
        import json
        if not os.path.exists(self.logfile):
            load_dict={'commits': False, 'events': False, 'comments': False, 'issues': False, 'pulls': False,"filechanges":False}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()

        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            if type == CrawlType.ISSUE:
                load_dict['issues'] = True
            if type == CrawlType.COMMIT:
                load_dict['commits'] = True
            if type == CrawlType.COMMENT:
                load_dict['comments'] = True
            if type == CrawlType.PULL:
                load_dict['pulls'] = True
            if type == CrawlType.EVENT:
                load_dict['events'] = True
            if type == CrawlType.FILECHANGE:
                load_dict['filechanges'] = True
            logging.info(load_dict)
            self.issue = load_dict['issues']
            self.commit = load_dict['commits']
            self.comment = load_dict['comments']
            self.pull = load_dict['pulls']
            self.event = load_dict['events']
            self.filechange = load_dict['filechanges']
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        load_f.close()
    def initlog(self):
        self.logfile = self.pyg.logfiledirpath + "/Crawl.txt"
        self.issue = False
        self.commit = False
        self.comment = False
        self.pull = False
        self.event = False
        self.filechange = True
        self.log(None)
        self.outputfile = self.pyg.logfiledirpath + "/CrawlOutput.txt"
        import logging
        # 创建一个logger
        self.logger = logging.getLogger(self.pyg.name)
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

    def __init__(self,repo):
        '初始化爬取所需要的信息'
        CrawlGithub.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg =repo
        self.initlog()
    def getlink(self, rlink):
        for it in rlink.split(","):
            if "next" in it:
                p = re.compile('<(.*)>; rel=\"next\"')
                m = re.search(p, it)
                print m.group(1)
                return m.group(1)
    def getAll(self):
        if not self.issue:
            self.logger.info("issues分页处理中...")
            self.pyg.issues_coll.remove({})
            self.getall(self.pyg.issues_url, self.pyg.issues_coll, CrawlType.ISSUE)
        if not self.comment:
            self.logger.info("comments分页处理中...")
            self.pyg.comments_coll.remove({})
            self.getall(self.pyg.comments_url, self.pyg.comments_coll, CrawlType.COMMENT)
        if not self.commit:
            self.logger.info("commits分页处理中...")
            self.pyg.commits_coll.remove({})
            self.getall(self.pyg.commits_url, self.pyg.commits_coll, CrawlType.COMMIT)
        if not self.pull:
            self.logger.info("pulls分页处理中...")
            self.pyg.pulls_coll.remove({})
            self.getall(self.pyg.pulls_url, self.pyg.pulls_coll, CrawlType.PULL)
        if not self.event:
            self.logger.info("events分页处理中...")
            self.pyg.events_coll.remove({})
            self.getall(self.pyg.events_url, self.pyg.events_coll, CrawlType.EVENT)

        if not self.filechange:
            self.logger.info("filechange分页处理中..")
            self.getAllfilechaneg()

    def getall(self,start_url,coll,type):
        '获取所有的并存入数据库中'
        print start_url,coll,type
        i = 0
        while True:
            # try:
                i += 1
                self.logger.info("正在处理第" + str(i) + "分页...")
                response = requests.get(url=start_url, headers=self.pyg.headers, params=self.pyg.params)
                self.logger.info(response)
                results = response.json()

                if results==[]:
                    break
                print results
                coll.insert(results)

                if "Link" not in response.headers.keys():
                    self.logger.info((response.headers.keys(),"link not in response.haaders处理完毕..."))
                    break
                rlink = response.headers['Link']
                if i==1:
                    self.logger.info("开始和结束分页"+str(rlink))

                self.logger.info(rlink)
                start_url = self.getlink(rlink)
                self.logger.info(start_url)

                if start_url==None :
                    self.logger.info("处理完毕...")
                    break
            # except Exception, Argument:
            #     print i, start_url,Argument
        self.log(type)
        self.logger.info("所有共" + str(i) + "分页")

    def gebugcommit(self):
        coll = self.pyg.commits_coll
        xs= coll.find({},no_cursor_timeout=True)
        for x in xs:
            bug=False
            fix=False
            xiufu=False
            message=x["getpatchs"]["message"]
            if "bug" in message or "Bug" in message or "BUG" in message:
                bug=True
            if "fix" in message or "Fix" in message or "FIX" in message:
                fix=True
            if u"修复" in message :
                xiufu = True
            # print filechange_coll.find_one({"sha":x["sha"]}) ==None
            if bug or fix or xiufu:
                yield x
        xs.close()

    def getAllfilechaneg(self):
        num= 0
        for x in self.gebugcommit():
            num+=1
        print num
        filechange_coll =self.pyg.filechanges_coll
        index = 0
        for x in self.gebugcommit():
            index+=1
            if filechange_coll.find_one({"sha":x["sha"]}) ==None:
                try:
                    filechange_url=self.pyg.commits_url+"/"+x["sha"]
                    r = requests.get(url=filechange_url, headers=self.pyg.headers)
                    result=r.json()
                    filechange_coll.insert(result)
                    self.logger.info((index,num,"sha"+x["sha"]))
                except:
                    print "except"
        self.log(CrawlType.FILECHANGE)

if __name__=="__main__":
    # 初始化Github仓库
    repo= GithubRepo("owncloud","android")
    repo.printInfo()
    # 初始化爬取类
    crawl=CrawlGithub(repo)
    crawl.getAll()
