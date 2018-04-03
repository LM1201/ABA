#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import GetFilePathRoot
from pymongo import MongoClient
class GithubRepo:
    '一个GithubRepo对应一个Android爬取项目'
    count = 0
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token ef373502bf40d0705e70a73d4935390bde7aebf8",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    }

    pacth_headers = {
        "Accept": "application/vnd.github.VERSION.patch",
        "Authorization": "token ef373502bf40d0705e70a73d4935390bde7aebf8",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    }
    params = {
        "state": "all"
    }
    def __init__(self, user="codinguser", repo="gnucash-android"):
        '项目初始化'
        GithubRepo.count += 1
        '初始化基本信息'
        # 用户名
        self.user = user
        # 仓库名
        self.repo = repo
        # GithubRepo名
        self.name = self.user + "_" + self.repo
        # 项目根目录名称
        '初始化爬取使用的url'
        self.init_url()
        '初始化爬取存储路径'
        self.init_filepath()
        '初始化数据库名称'
        self.init_mongodb_coll()

    def init_url(self):
        '初始化爬取所使用的url '
        # https: // api.github.com / repos /codinguser/gnucash-android/issues
        self.issues_url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/issues"
        self.commits_url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/commits"
        self.comments_url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/comments"
        self.pulls_url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/pulls"
        self.events_url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/events"

    def init_filepath(self):
        self.data_dir = os.path.join(GetFilePathRoot.get_root_dir(), "data", self.name)
        if not os.path.exists(os.path.join(GetFilePathRoot.get_root_dir(), "data")):
            os.mkdir(os.path.join(GetFilePathRoot.get_root_dir(), "data"))
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        '初始化爬取类的文件存储路径'
        # 存储 getfiles 的文件名称与位置
        self.allissuesnumfilename = self.name+ "_" + "allissuesnum.txt"
        self.allissuesnumfilepath = os.path.join(self.data_dir, self.allissuesnumfilename)
        # 存储提交的commitsha 的文件名称 与位置
        self.allcommitshafilename = self.name + "_" + "allscommitssha.txt"
        self.allcommitshafilepath = os.path.join(self.data_dir, self.allcommitshafilename)
        # 不同目录，目录不存在则创建
        self.diffdirpath = os.path.join(self.data_dir,"diff1")
        self.diffdirpath2 = os.path.join(self.data_dir,"diff2")
        self.diffdirpath3 = os.path.join(self.data_dir,"diff3")
        if not os.path.exists(self.diffdirpath):
            os.mkdir(self.diffdirpath)
        if not os.path.exists(self.diffdirpath2):
            os.mkdir(self.diffdirpath2)
        if not os.path.exists(self.diffdirpath3):
            os.mkdir(self.diffdirpath3)
        # self.init_processing_corpus_filepath()
        self.picfiledirpath= os.path.join(self.data_dir,"pic")
        if not os.path.exists(self.picfiledirpath):
            os.mkdir(self.picfiledirpath)
        self.logfiledirpath = os.path.join(self.data_dir, "log")
        if not os.path.exists(self.logfiledirpath):
            os.mkdir(self.logfiledirpath)

    def init_processing_corpus_filepath(self):
        'previous and not use again keep for save time to deal the probale bug'
         # 初始化语料处理类的文件存储路径
        self.difffilename = self.name + "_" + "difftext"
        self.diffpredealfilename = self.name+ "_" + "diffpredealtext"
        self.directoryfilename = self.name+ "_" + "directory.txt"
        self.diffmodelfilename = self.name + "_" + "diff.model"

        self.difffilepath = os.path.join(self.data_dir,"corpus", self.difffilename)
        self.diffpredealfilepath = os.path.join(self.data_dir,"corpus", self.diffpredealfilename)
        self.directoryfilepath = os.path.join(self.data_dir,"corpus" ,self.directoryfilename)
        self.diffmodelfilepath = os.path.join(self.data_dir,"corpus", self.diffmodelfilename)

        self.diffjavafilename = self.name+ "_" + "difftext_java"
        self.diffpredealjavafilename = self.name + "_" + "diffpredealtext_java"
        self.directoryjavafilename = self.name + "_" + "directory_java.txt"
        self.diffmodeljavafilename = self.name + "_" + "diff_java.model"
        self.diffjavafilepath = os.path.join(self.data_dir,"corpus", self.diffjavafilename)
        self.diffpredealjavafilepath = os.path.join(self.data_dir,"corpus",self.diffpredealjavafilename)
        self.directoryjavafilepath = os.path.join(self.data_dir,"corpus",self.directoryjavafilename)
        self.diffmodeljavafilepath = os.path.join(self.data_dir, "corpus",self.diffmodeljavafilename)

        self.diffxmlfilename = self.name + "_" + "difftext_xml"
        self.diffpredealxmlfilename = self.name+ "_" + "diffpredealtext_xml"
        self.directoryxmlfilename = self.name + "_" + "directory_xml.txt"
        self.diffmodelxmlfilename = self.name + "_" + "diff_xml.model"


    def init_mongodb_coll(self):
        '初始化语料处理的数据库'
        '打开数据库'
        self.mongodb_name=self.name
        self.comments_coll = self.openmongdb("comments")
        self.issues_coll = self.openmongdb("issues")
        self.commits_coll = self.openmongdb("commits")
        self.pulls_coll=self.openmongdb("pulls")
        self.events_coll=self.openmongdb("events")

        self.filechanges_coll = self.openmongdb("filechanges")
        self.issue_pull_commit_coll = self.openmongdb("issue_pull_commit")
        self.patchs_coll = self.openmongdb("patchs")

        self.analysis_coll = self.openmongdb("analysis")

        self.issues_info3_coll = self.openmongdb("issuesinfo3")
        self.diff_info_coll = self.openmongdb("diffinfo")

    def openmongdb(self, collname='comments'):
        client = MongoClient()
        db = client[self.mongodb_name]
        coll = db[collname]
        return coll
    def printInfo(self):
        print "name:",self.name
        print "data_dir:",self.data_dir
        print "url:"
        print self.issues_url
        print self.commits_url
        print self.headers
        print "mongodb"
        print self.comments_coll
        print self.issues_coll
        print self.commits_coll
        print self.filechanges_coll
        print self.issue_pull_commit_coll
        print self.patchs_coll
        print self.analysis_coll
        print self.issues_info3_coll
        print self.diff_info_coll
if __name__=="__main__":
    # 初始化Github仓库
    repo= GithubRepo("owncloud","android")
    repo.printInfo()