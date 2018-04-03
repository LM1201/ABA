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

class PatchesTask:
    (COMMIT,PULL) = range(2)

class GetPatches:
    count = 0
    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化爬取所需要的信息'
        GetPatches.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg = GithubRepo(user=user, repo=repo)
        self.initlog()

    def log(self,type):
        import json
        if not os.path.exists(self.logfile):
            load_dict={'commits': False,'pulls':False}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
                dump_f.close()
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            print load_dict
            load_f.close()
            if type == PatchesTask.COMMIT:
                load_dict['commits'] = True
            if type == PatchesTask.PULL:
                load_dict['pulls'] = True
            logging.info(load_dict)
            self.commit = load_dict['commits']
            self.pull = load_dict['pulls']
        # print "++++++++++++++++++++++++++++",load_dict
        with open(self.logfile, "w") as dump_f:
            json.dump(load_dict, dump_f)
            dump_f.close()

    def initlog(self):
        self.logfile = self.pyg.logfiledirpath + "/Patches.txt"
        self.commit = False
        self.pull = False
        # 和后面解析的是一致的
        self.start_prefix =  "##### start"
        self.change_prefix = "###### change :"
        self.name_prefix =   "###### name :"
        self.end_prefix =    "##### end"
        self.log(None)
        self.outputfile = self.pyg.logfiledirpath + "/PatchesOutput.txt"
        self.sha_name_file =self.pyg.data_dir+"/sha_name.csv"

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
        GetPatches.count += 1
        # 初始化 使用的项目 GithubRepo
        self.pyg =repo
        self.initlog()

    def cleardiff(self):
        import shutil
        if os.listdir(self.pyg.diffdirpath) is not None:
            shutil.rmtree(self.pyg.diffdirpath)
            os.mkdir(self.pyg.diffdirpath)
        if os.listdir(self.pyg.diffdirpath2) is not None:
            shutil.rmtree(self.pyg.diffdirpath2)
            os.mkdir(self.pyg.diffdirpath2)
        if os.listdir(self.pyg.diffdirpath3) is not None:
            shutil.rmtree(self.pyg.diffdirpath3)
            os.mkdir(self.pyg.diffdirpath3)
        if os.path.exists(self.logfile):
            os.remove(self.logfile)
        if os.path.exists(self.sha_name_file):
            os.remove(self.sha_name_file)

        for fh in self.logger.handlers:
            fh.close()


    def getAll(self):
        # return
        if not self.commit:
            self.logger.info("getcommits")
            self.getcommits()
        if not self.pull:
            self.logger.info("getpulls")
            self.getpulls()

        for fh in self.logger.handlers:
            fh.close()

    def getsha(self,string):
        from hashlib import sha1
        ss= sha1(string)
        return  ss.hexdigest()

    def getcommits(self):
        coll =self.pyg.filechanges_coll
        for x in coll.find():
            content=[]
            content.append(self.start_prefix)
            if "files" not in x.keys():
                continue
            if 'stats' not in x.keys():
                continue
            content.append(self.change_prefix+str([len(x['files']),x['stats']['deletions'],x['stats']['additions']]))
            self.logger.info([len(x['files']),x['stats']['deletions'],x['stats']['additions']])
            print "-------------------------------------------------------------------------------------"
            for file in x['files']:
                if 'filename' in file.keys() and "patch" in file.keys():
                    name = file['filename']
                    patch = file['patch']
                    if name.endswith("java") :
                        content.append(self.name_prefix+str(name))
                        content.append(patch)
                        self.logger.info("write java file patch")
                        jfp_name=str(name).replace("/","_").replace(".","__")
                        jfp_sha = self.getsha(jfp_name)
                        with open(self.sha_name_file,"a") as f:
                            ff = csv.writer(f)
                            ff.writerow([jfp_sha, jfp_name])
                            f.close()

                        with open(os.path.join(self.pyg.diffdirpath2,jfp_sha+".txt"),"w") as f:
                            f.write(patch)
                            f.close()
                    if name.endswith("xml") and 'filename' in file.keys() and "patch" in file.keys():
                        content.append(self.name_prefix+str(name))
                        content.append(patch)
                        self.logger.info("write xmfile patch")
                        jfp_name = str(name).replace("/", "_").replace(".", "__")
                        jfp_sha = self.getsha(jfp_name)
                        with open(self.sha_name_file, "a") as f:
                            ff = csv.writer(f)
                            ff.writerow([jfp_sha, jfp_name])
                            f.close()

                        with open(os.path.join(self.pyg.diffdirpath3,jfp_sha+".txt"),"w") as f:
                            f.write(patch)
                            f.close()
                    if name.endswith("java") or name.endswith("xml"):
                        self.logger.info(("patch-name",name))
                    # print "-------------------------------------------------------------------------------------"
                    # print "patch-content"
                    # print "-------------------------------------------------------------------------------------"
                    # print file['patch']
            self.logger.info("write to commit")
            content.append(self.end_prefix)
            with open(os.path.join(self.pyg.diffdirpath,str(x['sha'])+".txt"), "w") as f:
                for c in content :
                    f.write(c)
                    f.write("\n")
                f.close()
            self.log(PatchesTask.COMMIT)

    def getpulls(self):
        coll = self.pyg.issue_pull_commit_coll
        for x in coll.find():
            self.logger.info("commits 数量")
            self.logger.info(len(x['commits']))
            for commit in x['commits']:
                content = []
                content.append(self.start_prefix)
                for sha in commit['sha']:
                    content.append(self.change_prefix+str(commit["commit_changes"]))
                    self.logger.info(commit["commit_changes"])
                    for file in commit[sha]['filenames']:
                        if 'patch' not in commit[sha][file]:
                            break
                        name = commit[sha][file]['patch']
                        self.logger.info("patch-name")
                        self.logger.info(name)
                        patch_coll = self.pyg.patchs_coll
                        for p in patch_coll.find():
                            if name in p.keys():
                                patch = p[name]
                                # print p
                                break

                        # x2 = patch_coll.find_one({name: {"$ne": "null"}})
                        # print "patch-content"
                        # print "-------------------------------------------------------------------------------------"
                        # print x2.keys(),name
                        # patch= x2[name]

                        if 1==1:
                            if name.endswith("java"):
                                content.append(self.name_prefix+str(name))
                                content.append(patch)
                                self.logger.info("write java file patch")
                                jfp_name = str(name).replace("/", "_").replace(".", "__")
                                jfp_sha = self.getsha(jfp_name)
                                with open(self.sha_name_file, "a") as f:
                                    ff = csv.writer(f)
                                    ff.writerow([jfp_sha, jfp_name])
                                    f.close()
                                with open(os.path.join(self.pyg.diffdirpath2,jfp_sha + ".txt"),
                                          "w") as f:
                                    f.write(patch)
                                    f.close()
                            if name.endswith("xml"):
                                content.append(self.name_prefix+str(name))
                                content.append(patch)
                                self.logger.info("write xmfile patch")
                                jfp_name = str(name).replace("/", "_").replace(".", "__")
                                jfp_sha = self.getsha(jfp_name)
                                with open(self.sha_name_file, "a") as f:
                                    ff = csv.writer(f)
                                    ff.writerow([jfp_sha, jfp_name])
                                    f.close()
                                with open(os.path.join(self.pyg.diffdirpath3,  jfp_sha+ ".txt"), "w") as f:
                                    f.write(patch)
                                    f.close()
                            if name.endswith("java") or name.endswith("xml"):
                                self.logger.info(("patch-name", name))
                    self.logger.info("write to pull")
                    content.append(self.end_prefix)
                    # print content
                    with open(os.path.join(self.pyg.diffdirpath, "sha"+str(x['number']) + ".txt"), "a") as f:
                        for c in content:
                            # print c
                            f.write(c)
                            f.write("\n")
                        f.close()

if __name__=="__main__":
    # 初始化Github仓库
    repo= GithubRepo("owncloud","android")
    # 初始化爬取类
    crawl=GetPatches(repo)
    crawl.cleardiff()
    # crawl.getAll()

