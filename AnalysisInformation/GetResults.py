
import os
import json
import GetInformation.GetFilePathRoot
print GetInformation.GetFilePathRoot.get_root_dir()
from GetInformation.GithubRepo import  GithubRepo
from AnalysisInformation import AnalysisInformation
from GenPic import genHistogrampic as H
from GenPic import genPiechartpic as P
from pymongo import MongoClient
import csv
def drawpull():
    client = MongoClient()
    if not os.path.exists(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2")):
        os.mkdir(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2"))
    with open(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2", "pulls.csv"), "w") as f:
        ff = csv.writer(f)
        ff.writerow(["name", "count"])
        for name in client.database_names():
            db = client[name]
            if "issue_pull_commit" in db.collection_names():
                ff.writerow([name, str(db["issue_pull_commit"].count())])
def drawfilechanges():
    client = MongoClient()
    if not os.path.exists(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2")):
        os.mkdir(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2"))
    with open(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2", "filechanges.csv"), "w") as f:
        ff = csv.writer(f)
        ff.writerow(["name", "count"])
        for name in client.database_names():
            db = client[name]
            if "filechanges" in db.collection_names():
                ff.writerow([name, str(db["filechanges"].count())])
class GetResult:
    def __init__(self):
        self.mongodb=False
        # self.mongodb = True
    def getallresult(self):
        client = MongoClient()
        for dbname in client.database_names():
            user_repo= dbname.split("_")
            repo = GithubRepo(str(user_repo[0]), str(user_repo[1]))
            analysis = AnalysisInformation(repo)
            analysis.getAll(mongodb=self.mongodb)
            yield analysis.allresult

    def writetocsv(self,data,filename):
        with open(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2", filename), "w") as f:
            ff = csv.writer(f)
            ff.writerow(["key", "value"])
            for k, v in data.items():
                ff.writerow([k, v])
            f.close()

    def getallanalysis(self):
        # keys=['name', 'java_2', 'java_1', 'otherxml', 'number', 'othertype', 'xml_2', 'xml_1', 'typenumber','type', 'otherjava']
        self.name={}
        self.number={}
        self.typenumber={}
        self.type={}
        self.java_1={}
        self.java_2={}
        self.xml_1={}
        self.xml_2={}
        self.othertype=[]
        self.otherjava=[]
        self.otherxml=[]
        self.othertypes={}
        self.otherjavas={}
        self.otherxmls={}
        for allresult in self.getallresult():

            for k, v in allresult['name'].items():
                self.name[k]=self.name.get(k,0)+len(v)
            for k, v in allresult['number'].items():
                self.number[k] = self.number.get(k, 0) + v
            for k,v in allresult['type'].items():
                self.type[k]=self.type.get(k,0)+v
            for k,v in allresult['typenumber'].items():
                self.typenumber[k]=self.typenumber.get(k,0)+v
            for k, v in allresult['java_1'].items():
                self.java_1[k] = self.java_1.get(k, 0) + v
            for k, v in allresult['java_2'].items():
                self.java_2[k] = self.java_2.get(k, 0) + v
            for k, v in allresult['xml_1'].items():
                self.xml_1[k] = self.xml_1.get(k, 0) + v
            for k, v in allresult['xml_2'].items():
                self.xml_2[k] = self.xml_2.get(k, 0) + v

            for it in allresult['othertype']:
                self.othertype.append(it)
            for it in allresult['otherjava']:
                self.otherjava.append(it)
            for it in allresult['otherxml']:
                self.otherxml.append(it)

        for it in self.othertype:
            self.othertypes[it.split(".")[-1]] = self.othertypes.get(it.split(".")[-1], 0) + 1

        for it in self.otherjava:
            self.otherjavas[it]=1
        for it in self.otherxml:
            self.otherxmls[it]=1

        self.writetocsv(self.othertypes,"othertype.csv")
        self.writetocsv(self.otherjavas, "otherjavas.csv")
        self.writetocsv(self.otherxmls, "otherxmls.csv")

        self.writetocsv(self.name, "name.csv")
        self.writetocsv(self.number, "number.csv")
        self.writetocsv(self.type, "type.csv")
        self.writetocsv(self.typenumber, "typenumber .csv")

        self.writetocsv(self.java_1, "java_1.csv")
        self.writetocsv(self.java_2, "java_2.csv")
        self.writetocsv(self.xml_1, "xml_1.csv")
        self.writetocsv(self.xml_2, "xml_2.csv")


def analysisothers(suf=".java",csvfile="otherjavas.csv"):
    suffix = {}
    with open(os.path.join(GetInformation.GetFilePathRoot.get_root_dir(), "data2", csvfile), "r") as f:
        ff = csv.reader(f)
        headers = next(ff)
        for row in ff:
            ss=[]
            for char in str(row[0]):
                if 'A'<=char and 'Z'>= char:
                    ss=[]
                ss.append(char)
            filename=""
            for char in  ss:
                filename+=char
            if len(filename.split(suf)[0])>1:
                suffix[filename.split(suf)[0]]=suffix.get(filename.split(suf)[0],0)+1
    result=[]
    num=0
    for x in sorted(suffix.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
        num+=x[1]
    index = 0
    for x in sorted(suffix.items(), lambda x, y: cmp(x[1], y[1]), reverse=True):
        index+=x[1]
        if float(index)/num <0.75 and float(len(result))/len(suffix)<0.05 and x[1]>1:
            result.append(x[0])
    print float(len(result))/len(suffix)
    print result
    return result

if __name__ =="__main__":
    choose = 0
    if choose ==1:
        drawpull()
    elif choose ==2:
        drawfilechanges()
    elif choose == 3:
        GetResult().getallanalysis()
    elif choose ==4 :
        analysisothers(suf=".java", csvfile="otherjavas.csv")
    elif choose ==5:
        analysisothers(suf=".xml", csvfile="otherxmls.csv")
    pass


