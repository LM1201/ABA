#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import sys;
reload(sys);
import logging
sys.setdefaultencoding('utf-8');
import requests
from GithubRepo import GithubRepo
import GetFilePathRoot
import csv

class FindAndroidRepos:
    '爬取类'
    count = 0
    if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(), "data2")):
        os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(), "data2"))
    resultfile = os.path.join(GetFilePathRoot.get_root_dir(), "data2", "Find.csv")

    def __init__(self):
        '初始化爬取所需要的信息'
        FindAndroidRepos.count += 1
        # 初始化 使用的项目 GithubRepo
        self.initlog()

    def initlog(self):
        import GetFilePathRoot

        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(),"data2")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(),"data2"))
        self.outputfile = os.path.join(GetFilePathRoot.get_root_dir(),"data2","FindOutput.txt")

        if os.path.exists(self.resultfile):
            import shutil
            import time
            print time.time()
            shutil.copyfile(self.resultfile, self.resultfile+str(time.time())+".bak")

        with open(self.resultfile, "w") as f:
            ff = csv.writer(f)
            ff.writerow(["full_name","language","size","description","homepage","url","forks","watchers","open_issue"])
        print GetFilePathRoot.get_root_dir()
        print self.outputfile
        # 创建一个logger
        self.logger = logging.getLogger('Crawl')
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

    def getlink(self, rlink):
        for it in rlink.split(","):
            if "next" in it:
                p = re.compile('<(.*)>; rel=\"next\"')
                m = re.search(p, it)
                return m.group(1)

    def getAll(self,start_url="https://api.github.com/search/repositories?q=topic:Android+language:Java&sort=stars&order=desc"):
        i=0
        j=0
        k=0
        l=0
        while True:
            i += 1
            self.logger.info("正在处理第" + str(i) + "分页...")
            response = requests.get(url=start_url, headers=GithubRepo.headers, params=GithubRepo.params)
            self.logger.info(response)
            rlink = response.headers['link']
            start_url = self.getlink(rlink)
            if start_url is not None:
                self.logger.info("next url : "+start_url)
            results = response.json()
            l = results["total_count"]
            for result in results["items"]:
                k+=1
                try:
                    contents_url="https://api.github.com/repos/"+result["full_name"]+"/commits"
                    r = requests.get(url=contents_url, headers=GithubRepo.headers, params=GithubRepo.params)
                    contents = r.json()
                    if len(contents)>0:
                        check_url= contents[0]["getpatchs"]["tree"]["url"]+"?recursive=10"
                        print check_url
                        r = requests.get(url=check_url, headers=GithubRepo.headers, params=GithubRepo.params)
                        checks=r.json()
                        hasmani=False
                        haslayout=False
                        for tree in checks["tree"]:
                            if tree["path"].endswith("src/main/AndroidManifest.xml"):
                                hasmani = True
                                break
                        for tree in checks["tree"]:
                            if tree["path"].endswith("src/main/res/layout"):
                                haslayout =True
                                break
                        if hasmani and haslayout:
                            j+=1
                            self.logger.info(("is Android project", i,j,k,l))
                            # self.logger.debug([content["name"] for content in contents])
                            with open(self.resultfile, "a") as f:
                                import csv
                                ff=csv.writer(f)
                                ff.writerow([str(result["full_name"]),str(result["language"]),str(result["size"]),str(result["description"]),
                            str(result["homepage"]),str(result["html_url"]), str(result["forks_count"]),str(result["watchers_count"]),
                            str(result["open_issues_count"])])
                except Exception,Argument:
                    print i, start_url,Argument
            if i == 1:
                self.logger.info("开始和结束分页" + str(rlink))
            if start_url== None:
                self.logger.info("处理完毕...")
                break

if __name__=="__main__":
    find=FindAndroidRepos()
    find.getAll()
