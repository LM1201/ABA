#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf')
import requests
import re
import logging

from GetInformation.GithubRepo import GithubRepo

class AnalysisTask:
    (GETFILE) = range(1)

class AnalysisInformation:

    count = 0
    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化爬取所需要的信息'
        AnalysisInformation.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg = GithubRepo(user=user, repo=repo)
        self.initlog()

    def log(self,type):
        import json
        if not os.path.exists(self.logfile):
            load_dict={'getfiles': False}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            load_f.close()
            if type == AnalysisTask.GETFILE:
                load_dict['getfiles'] = True
            logging.info(load_dict)
            self.getfiles = load_dict['getfiles']
        # print "++++++++++++++++++++++++++++",load_dict
        with open(self.logfile, "w") as dump_f:
            json.dump(load_dict, dump_f)
            dump_f.close()

    def initlog(self):
        self.logfile = self.pyg.logfiledirpath + "/Analysis.txt"
        self.getfiles = False
        self.getpatchs = False
        self.javafiletypes = False
        self.xmlfiletypes = False

        self.allresult={}

        self.log(None)
        self.outputfile = self.pyg.logfiledirpath + "/AnalysisOutput.txt"

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
        AnalysisInformation.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg =repo
        self.initlog()

    def getAll(self,mongodb=False):
        coll = self.pyg.analysis_coll
        if mongodb:
            coll.remove({})
        if not self.getfiles:
            self.logger.info("getfiles...")
            coll.remove({})
            self.getfile()
        if coll.find_one():
            self.allresult=coll.find_one()
        else:
            self.logger.info("getfiles...")
            self.getfile()



    def getfile(self):
        self.filenamedict={}
        coll=self.pyg.filechanges_coll
        if coll.find_one():
            self.logger.info("find_one")
        for filechange in coll.find():
            if "files" in filechange.keys():
                filenames = [file["filename"] for file in filechange["files"]]
            # print {filechange["sha"]:filenames}
                self.filenamedict[filechange["sha"]]=filenames
        coll2=self.pyg.issue_pull_commit_coll
        for pull in coll2.find():
            for commit in  pull["commits"]:
                for sha in commit['sha']:
                    if sha not in self.filenamedict.keys():
                        filenames=[filename.replace("__",".").replace("_","/") for filename in commit[sha]["filenames"]]
                        self.filenamedict['sha']=filenames
                        # print commit[sha]["filenames"]
                        # print filenames
        self.logger.info(("commit总数",len(self.filenamedict)))
        num=0
        self.filenumberdict={}

        for k,v in self.filenamedict.items():
            num+=len(v)
            if len(v)==0:
                pass
            else:
                if len(v)<10:
                    self.filenumberdict[str(len(v))]=self.filenumberdict.get(str(len(v)),0)+1
                else:
                    self.filenumberdict["else"] =self.filenumberdict.get("else",0)+1

                #         self.filenumberdict["20"]+=1
        if len(self.filenamedict)>0:
            self.logger.info(("filechanges", float(num)/len(self.filenamedict)))
        self.logger.info(("filenumberdict", self.filenumberdict))

        # genHistogrampic(data=self.filenumberdict)
        # genPiechartpic(data=self.filenumberdict)

        self.filenamenumber={}
        for k, v in self.filenamedict.items():
            for filename in  v:
                self.filenamenumber[filename]=self.filenamenumber.get(filename,0)+1
        self.logger.info(("filenamenumber",len(self.filenamenumber)))
        # genHistogrampic(data=self.filenamenumber)
        # genPiechartpic(data=self.filenamenumber)
        self.filetypes = ["java", "xml", "gradle", "jar", "so", "aar", "png", "jpg", "keystore", "zip", "rar",
                          "md", "txt", "bat", "classpath", "project", "gitignore", "pro", "properties", "yml",
                          "gradlew", "sh", "yaml", "CONTRIBUTORS", "LICENSE", "gnucash","groovy","kt","html",
                          "other","json","h","class","c","js","svg","cs","cpp","iml","ttf","gif","swift",
                          "graphql","apk","aidl","css","hpp","mk"]

        self.filenametype = {}
        for filename in self.filenamenumber.keys():
            for ty in self.filetypes:
                if str(filename).endswith(ty):
                    self.filenametype[ty]=self.filenametype.get(ty,0)+1
        # genHistogrampic(data=self.filenametype)
        # genPiechartpic(data=self.filenametype)
        self.logger.info(("filenametype",self.filenametype))
        self.filenametypenumber = {}
        self.othertype=[]
        for filename,v in self.filenamenumber.items():
            # print filename, v
            intype = False
            for ty in self.filetypes:
                if str(filename).endswith(ty):
                    intype=True
                    # print int(v),self.filenametypenumber.get(ty,0)
                    self.filenametypenumber[ty] = self.filenametypenumber.get(ty, 0) + int(v)
            if not intype:
                print filename
                self.othertype.append(filename)
                    # print self.filenametypenumber[ty]
        # genHistogrampic(data=self.filenametypenumber)
        # genPiechartpic(data=self.filenametypenumber)
        self.logger.info(("filenametypenumber", self.filenametypenumber))

        self.logger.info("javafiletypes...")
        self.javaresult_1,self.otherjavas = self.javaresult(self.filenamenumber)
        # print result["other"]
        # genHistogrampic(data=result)
        # genPiechartpic(data=result)
        self.logger.info(self.javaresult_1)
        self.javaresult_2,self.otherjavas= self.javaresult(self.filenamenumber,weight=True)
        self.logger.info(self.javaresult_2)

        # print result["other"]
        # genHistogrampic(data=result)
        # genPiechartpic(data=result)

        self.logger.info("xmlfiletypes...")
        self.xmlresult_1,self.otherxmls = self.xmlresult(self.filenamenumber)
        self.logger.info(self.xmlresult_1)
        # print result["other"]
        # genHistogrampic(data=result)
        # genPiechartpic(data=result)

        self.xmlresult_2,self.otherxmls = self.xmlresult(self.filenamenumber, weight=True)
        self.logger.info(self.xmlresult_2)
        # print result["other"]
        # genHistogrampic(data=result)
        # genPiechartpic(data=result)

        self.allresult={"name":self.filenamedict,"number":self.filenumberdict,
                        "type":self.filenametype,"typenumber":self.filenametypenumber,
                        "java_1":self.javaresult_1,"java_2":self.javaresult_2,"xml_1":self.xmlresult_1,"xml_2":self.xmlresult_2,
                        "othertype":self.othertype,"otherjava":self.otherjavas,"otherxml":self.otherxmls}
        print self.allresult.values()
        # if not self.allresult.values() == [{}, {}, {}, {}, {}, {}, {}, {}]:
        coll = self.pyg.analysis_coll
        coll.insert(self.allresult)
        self.log(AnalysisTask.GETFILE)

    def javaresult(self,javafilenamesmap,weight=False):
        'java 结果 reduce 1'
        result = {}
        otherjava=[]
        javasuffix=['Test', 'Activity', 'Fragment', 'Adapter', 'View', 'Helper', 'Utils',
                    'Manager', 'Service', 'Listener', 'Layout', 'Loader', 'Factory',
                    'Task', 'Provider', 'Handler', 'Util', 'Dialog', 'Holder', 'Item',
                    'Exception', 'Client', 'Parser', 'Tests', 'Model', 'Impl', 'Builder',
                    'Controller', 'Receiver', 'Info', 'Presenter', 'Event', 'Type', 'Request',
                    'List', 'Drawable', 'Module', 'Callback', 'Generator', 'Preference',
                    'Source', 'Animator', 'Data', 'Processor', 'Wrapper', 'Stream', 'Compat',
                    'Filter', 'Resolver', 'Reader', 'State', 'Cache', 'Button', 'Base', 'Text',
                    'Result', 'Application', 'Response', 'Operation', 'Table', 'Config', 'Bar',
                    'Action', 'Animation', 'Command', 'Delegate', 'Renderer', 'Resource', 'Target',
                    'Decoder', 'Message', 'Thread', 'Context', 'Rule', 'Settings', 'Detector',
                    'Key', 'Entity', 'Column', 'Span', 'Indicator', 'Interface', 'Behavior',
                    'Store', 'Player', 'Object', 'Constants', 'Options', 'Logger', 'Method',
                    'Patch', 'Set', 'Creator', 'Picker', 'Property', 'Proxy', 'Stub',
                    'Interceptor', 'File', 'Api', 'Runner', 'Layer', 'Converter', 'Widget',
                    'Class', 'Header', 'Extractor', 'Transformer', 'Inflater', 'Pager', 'Case',
                    'Connection', 'Writer', 'Page', 'Map', 'Menu', 'Job', 'Strategy', 'Validator',
                    'Comparator', 'Pool', 'Dao', 'Value', 'Algorithm', 'Image', 'Content', 'Binder',
                    'Contract', 'Group', 'Storage', 'Configuration']

        for jfk, jfv in javafilenamesmap.items():
            if weight:
                jfv=1
            jfk = re.split("/", jfk)[-1]
            insuffix = False
            for suffix in javasuffix:
                if jfk.endswith(suffix+".java"):
                    insuffix=True
                    result[suffix]=result.get(suffix,0)+jfv
            if not insuffix and jfk.endswith(".java"):
                # print jfk
                otherjava.append(jfk)
                result["other"] = result.get("other", 0) + jfv
                # print jfk, jfv
        return result,otherjava

    def xmlresult(self,xmlfilenamesmap,weight=False):
        'xml 结果 reduce1'
        result = {}
        otherxml=[]
        xmlsuffix = ['Library', 'Name', 'Blogs', 'Posts', 'Strings', 'Tests', 'Comment', 'Options', 'Permissions', 'Button', 'Import', 'Data', 'Style', 'Providers', 'Manifest']
        for jfk, jfv in xmlfilenamesmap.items():
            if weight:
                jfv=1
            jfk = re.split("/", jfk)[-1]
            insuffix = False
            for suffix in xmlsuffix:
                if jfk.endswith(suffix+".xml"):
                    insuffix = True
                    result[suffix]=result.get(suffix,0)+jfv
            if not insuffix and jfk.endswith(".xml"):
                # print jfk
                otherxml.append(jfk)
                result["other"] = result.get("other", 0) + jfv
        return result,otherxml

if __name__=="__main__":
    # 初始化Github仓库
    repo= GithubRepo("owncloud","android")
    # 初始化爬取类
    crawl=AnalysisInformation(repo)
    crawl.getAll()
    print crawl.allresult
