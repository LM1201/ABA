#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import requests

from GithubRepo import GithubRepo
from CrawlGithub import CrawlType
import os;
import pygraphviz as pgv
os.environ["PATH"]= r'D:\Program Files\graphviz-2.38\release\bin;'+os.environ["PATH"];

class DealTaskType:
    (BUG,DOWNRAW,DOWNDIFF) = range(3)
class DealMongo:
    '从数据库中读取信息，因为数据库中信息是全面的，而我们只需要一部分'
    count = 0

    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化'
        DealMongo.count += 1
        self.pyg = GithubRepo(user=user, repo=repo)
        self.initlog()

    def __init__(self, repo):
        '初始化'
        DealMongo.count += 1
        self.pyg = repo
        self.initlog()

    def log(self, type):
        import json
        if not os.path.exists(self.logfile):
            load_dict = {'bugs': False,"downraw":False,"downdiff":False }
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            if type == DealTaskType.BUG:
                load_dict['bugs'] = True
            if type == DealTaskType.DOWNRAW:
                load_dict['downraw'] = True
            if type == DealTaskType.DOWNDIFF:
                load_dict['downdiff'] = True

            logging.info(load_dict)
            self.bug = load_dict['bugs']
            self.downraw = load_dict['downraw']
            self.downdiff = load_dict['downdiff']
            load_f.close()

        with open(self.logfile, "w") as dump_f:
            json.dump(load_dict, dump_f)
            dump_f.close()

    def initlog(self):
        self.logfile = self.pyg.logfiledirpath + "/Deal.txt"
        self.bug = False
        self.downraw=False
        self.downdiff=False

        self.log(None)
        self.outputfile = self.pyg.logfiledirpath + "/DealOutput.txt"
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

    def get_isuue(self, label_type):
        for result in self.pyg.issues_coll.find():
            haspull = False
            inlabel = False
            if "pull_request" in result.keys():
                # print result["pull_request"]
                haspull = True
            labels = [label["name"] for label in result["labels"] if len(label) > 0]
            # print labels
            if label_type == DealTaskType.BUG:
                if "bug" in labels or "BUG" in labels or "Bug" in labels:
                    inlabel = True
            if haspull and inlabel:
                yield result

    def getNum(self,label_type):
        i=0
        for issue_num in self.get_isuue(label_type):
            i+=1
        return i

    def dealAll(self):
        self.logger.info((self.getNum(DealTaskType.BUG)))
        if not self.bug:
            self.logger.info("bug label处理中...")
            self.deal(DealTaskType.BUG)

        '下载源文件注释掉了,不然任务过于复杂，耗时过多'
        # if not self.downdiff:
        #     coll = self.pyg.issue_pull_commit_coll
        #     for result in coll.find():
        #         if "diff" in result.keys():
        #             self.download(DealTaskType.DOWNDIFF, result["diff"])
        # if not self.downraw:
        #     coll = self.pyg.issue_pull_commit_coll
        #     for result in coll.find():
        #         if "raw" in result.keys():
        #             self.download(DealTaskType.DOWNRAW, result["raw"])

    def deal(self,label_type):
        '处理issue信息'
        self.logger.debug(("deal",label_type))
        coll= self.pyg.issue_pull_commit_coll
        coll.remove({"type":label_type})
        num =0
        for result in self.get_isuue(label_type):
            num+=1
        print num
        i=0
        for result in self.get_isuue(label_type):
            i+=1
            self.logger.info(result)
            pull={"getfiles":{},"commits":[],"number":result["number"],"type":label_type}
            difffile = {}
            rawfile={}
            issue = {"title": result["title"], "body": result["body"], "labels":[label["name"] for label in result["labels"] if len(label) > 0], "comments": [], "events": []}
            num = result["number"]
            self.logger.info("num"+str(num))
            '爬取comments'
            self.logger.info(str(i)+", 爬取comments")
            if result["comments"] > 0:
                comments_url = self.pyg.issues_url + "/" + str(num) + "/comments"
                r = requests.get(url=comments_url, headers=self.pyg.headers)
                comments = r.json()
                issue["comments"] = [comment["body"] for comment in comments]
                # print getfiles

            '爬取events'
            self.logger.info(str(i)+", 爬取events")
            events_url = self.pyg.issues_url + "/" + str(num) + "/events"
            r = requests.get(url=events_url, headers=self.pyg.headers)
            events = r.json()
            issue["events"] = [event["event"] for event in events]

            commits=[]
            '爬取pull of this getfiles'
            self.logger.info(str(i)+", 爬取pull of this getfiles")
            pull_url = self.pyg.pulls_url + "/" + str(num)
            r = requests.get(url=pull_url, headers=self.pyg.headers)
            result = r.json()
            pull["pull_changes"]= (result["deletions"], result["additions"], )
            pull["files"]=result["changed_files"]

            '下载diff文件 of this pull'
            difffile[str(num)]=result["diff_url"]

            '爬取commits of this pull'
            self.logger.info(str(i)+ ", 爬取pull of this getfiles")
            pull_commits_url = self.pyg.pulls_url + "/" + str(num) + "/commits"
            r = requests.get(url=pull_commits_url, headers=self.pyg.headers)
            pull_commits = r.json()
            commit = {
                      "sha": [pull_commit["sha"] for pull_commit in pull_commits],
                      "message": [pull_commit["getpatchs"]["message"]  for pull_commit in pull_commits],
                      "commit_changes":(0,0,0)
                      }
            j=0
            for pull_commit in pull_commits:
                j+=1
                '爬取each getpatchs of commits'
                self.logger.info(str(i)+", " +str(j)+u", 爬取each getpatchs of commits")
                commit_url = self.pyg.commits_url + "/" + str(pull_commit["sha"])
                r = requests.get(url=commit_url, headers=self.pyg.headers)
                result = r.json()
                files = result["files"]
                commit["commit_changes"]=(result["stats"]["deletions"], result["stats"]["additions"], result["stats"]["total"])
                commit[pull_commit["sha"]] = {"filenames": [str(file["filename"].replace("/","_").replace(".","__")) for file in files],"comments":[]}
                for file in files:
                    # self.logger.debug(file)
                    commit[pull_commit["sha"]][str(file["filename"].replace("/","_").replace(".","__"))]={"file_changes":(file["deletions"], file["additions"], file["changes"])}
                    if "patch" in file.keys():
                        patch_name=pull_commit["sha"]+"+"+str(file["filename"].replace("/", "_").replace(".", "__"))
                        commit[pull_commit["sha"]][str(file["filename"].replace("/", "_").replace(".", "__"))]["patch"]=patch_name
                        patch_coll=self.pyg.patchs_coll
                        patch_coll.insert({patch_name:file["patch"]})
                    if not file["raw_url"] == None:
                        rawfile[str(file["filename"].replace("/","_").replace(".","__"))]=file["raw_url"]
                # print pull_commit["getpatchs"]["comment_count"]
                if pull_commit["getpatchs"]["comment_count"] > 0:
                    '爬取pull  comments'
                    self.logger.info("$. 爬取pull  comments")
                    comments_url = self.pyg.commits_url + "/" + pull_commit["sha"] + "/comments"
                    r = requests.get(url=comments_url, headers=self.pyg.headers)
                    comments = r.json()
                    commit[pull_commit["sha"]]["comments"]=[ comment["body"] for comment in comments]
                commits.append(commit)
            pull ["getfiles"]= issue
            pull["commits"]=commits
            pull["raw"]=rawfile
            pull["diff"]=difffile
            '写入数据库'
            self.logger.info(str(i)+"6. 写入数据库")
            coll.insert(pull)
        self.log(label_type)

    def download(self,dealtype,dict={}):
        if not os.path.exists(os.path.join(self.pyg.diffdirpath, "raw")):
            os.mkdir(os.path.join(self.pyg.diffdirpath, "raw"))
        if not os.path.exists(os.path.join(self.pyg.diffdirpath, "pull_diff")):
            os.mkdir(os.path.join(self.pyg.diffdirpath, "pull_diff"))

        for k,v in dict.items():
            self.logger.info(str(k) + str(v))
            r = requests.get(url=v, headers=self.pyg.headers)
            if dealtype ==DealTaskType.DOWNRAW:
                with open(os.path.join(self.pyg.diffdirpath, "raw", str(k)), 'w') as f:
                    f.write(str(r.text.replace("\r\n", "\n")))
                    f.close()
            elif dealtype == DealTaskType.DOWNDIFF:
                with open(os.path.join(self.pyg.diffdirpath, "pull_diff", str(k) + ".txt"), 'w') as f:
                    f.write(str(r.text).replace("\r\n", "\n"))
                    f.close()
        self.log(dealtype)

    '''
    getpatchs 的关系图
    连续提交的被省略
    保留6位sha
    '''
    def buildGraphofCommit(self):
        A = pgv.AGraph(directed=True, strict=True)
        nodes = {};
        temp = {}
        # temp["key"]=[1,2,{"12":"12"}]
        for result in self.pyg.commits_coll.find():
            new =True
            if len(result["parents"])==1:
                for key in temp.keys():
                    if temp[key][len(temp[key])-1]== result["sha"][0:6] :
                        temp[key].append(result["parents"][0]["sha"][0:6])
                        new = False
                if new:
                    temp[result["sha"][0:6]]=[result["sha"][0:6],result["parents"][0]["sha"][0:6]]
            else:
                if result["sha"][0:6] not in nodes:
                    A.add_node(result["sha"][0:6]);
                for key in temp.keys():
                    if temp[key][len(temp[key])-1]== result["sha"][0:6] :
                        A.add_edge(key,result["sha"][0:6]);
                for parent in result["parents"][0:6]:
                    if parent["sha"][0:6] not in nodes:
                        A.add_node(parent["sha"][0:6]);
                    A.add_edge(result["sha"][0:6], parent["sha"][0:6]);
                # nodes[result["sha"]]=result["sha"]

        A.graph_attr['epsilon'] = '0.001'
        # print (A.string())  # print dot file to standard output
        A.write(os.path.join(self.pyg.picfiledirpath,'GraphOfCommit.dot'))
        A.layout('dot')  # layout with dot
        A.draw(os.path.join(self.pyg.picfiledirpath,'GraphOfCommit.svg'))

if __name__ == "__main__":
    repo = GithubRepo("owncloud", "android")
    deal = DealMongo(repo)
    # deal.buildGraphofCommit()
    deal.dealAll()


