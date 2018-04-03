#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import os
import re

import gensim.corpora
import matplotlib.pyplot as plt
import networkx as nx
from gensim.models import word2vec

from GetInformation.GithubRepo import GithubRepo


class ProcessingCorpus:
    '处理语料'
    count = 0
    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化，其中 notes 表示注释，thedata 表示数据'
        ProcessingCorpus.count += 1
        self.pyg = GithubRepo(user=user, repo=repo)
        self.isnotejava = False
        self.isnotexml = False
        self.notes = []
        self.type = "All"
        self.thedata = []
        self.sourcefilename = ""
        self.targetfilename = ""

    def gendiffpredealtxt(self, type="all", stragy=0):
        '预处理'
        print "预处理..."
        # 类型
        self.type = type
        # 确定源文件和目标问题
        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.targetfilename = self.pyg.diffpredealfilepath
            self.sourcefilename = self.pyg.difffilepath
        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.targetfilename = self.pyg.diffpredealjavafilepath
            self.sourcefilename = self.pyg.diffjavafilepath
        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.targetfilename = self.pyg.diffpredealxmlfilepath
            self.sourcefilename = self.pyg.diffxmlfilepath
        print self.sourcefilename, "->", self.targetfilename
        # 如果预期文件存在，则覆盖
        if os.path.exists(self.targetfilename):
            os.remove(self.targetfilename)
        self.difftextpredealfile = open(self.targetfilename, 'a')
        # 如果源文件存在，则进行处理
        if os.path.exists(self.sourcefilename):
            i = 0
            j = 0
            f = open(self.sourcefilename, 'r')
            line = f.readline()
            i += 1
            j += 1

            while line:
                line = f.readline()
                i += 1
                if re.search("/\*", line, re.I):
                    self.isnotejava = True
                if re.search("//", line, re.I) \
                        and not re.search("http://", line, re.I) and not re.search("https://", line,
                                                                                   re.I) and not re.search("file://",
                                                                                                           line, re.I):
                    temp = re.split("//", line, re.I)
                    temps = ""
                    for s in temp[:-1]:
                        temps += s
                    # print "[",line,"->",temps,"]"
                    line = temps
                    j += 1

                if re.search("<!--", line, re.I):
                    self.isnotexml = True
                    # print line
                    pass
                if self.isnotejava or self.isnotexml:
                    j += 1
                    self.notes.append(line)
                else:
                    if stragy == 0:
                        newline = line.replace("<", " < ").replace(">", " > ").replace("{", " { ").replace("}", " } ") \
                            .replace(",", " , ").replace("!", " ! ").replace("+", "+ ").replace("-", "- ").replace("\"",
                                                                                                                   " \" ") \
                            .replace("(", " ( ").replace(")", " ) ").replace(";", " ; ").replace("=",
                                                                                                 " = ").replace(
                            "\n", " ").replace("\s", " ").replace("\r", " ") \
                            .replace("\t", " ").replace("   ", " ").replace("  ", " ").replace("|", " | "). \
                            replace("= =", "==").replace(
                            "! =", "!=").replace("!  =", "!=").replace("< =", "<=").replace("> =", ">=") \
                            .replace("{ }", "{}").replace("{  }", "{}").replace("( )", "()").replace("(  )",
                                                                                                     "()").replace(
                            "* =", "*=").replace("+ =", "+=").replace("- =", "-=").replace(".", ". ")
                    elif stragy == 1:
                        newline = line.replace("<", " ").replace(">", " ").replace("}", " ").replace(",", " ") \
                            .replace("!", " ").replace("+", " ").replace("-", " ").replace("\"", " ") \
                            .replace("\\", " ").replace("(", " ").replace(")", " ").replace(";", " ").replace("=",
                                                                                                              " ").replace(
                            "@+", " ").replace("@", " ") \
                            .replace('\t', '').replace('\n', '').replace("\r", " ").replace("\s", " ").replace("   ",
                                                                                                               " ").replace(
                            "  ", " ").replace("/", " ") \
                            .replace("{", " ").replace("}", " ").replace("(", " ").replace(")", " ").replace(
                            "||", " ").replace("&&", " ")
                    if not newline == " ":
                        pass
                        self.difftextpredealfile.write(newline + "\n")
                if re.search("\*/", line, re.I):
                    self.isnotejava = False
                if re.search("-->", line, re.I):
                    self.isnotexml = False
                    # print self.notes
            f.close()
            self.difftextpredealfile.close()
            print "处理了" + str(i) + "代码，", "注释", j, "行"

    def gendiffpicture(self, word="activity", type="all", size=3):
        '生成词向量模型和diff的图片'
        print "生成词向量模型"
        self.type = type
        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.sourcefilename = self.pyg.diffmodelfilepath
        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.sourcefilename = self.pyg.diffmodeljavafilepath
        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.sourcefilename = self.pyg.diffmodelxmlfilepath

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        model = word2vec.Word2Vec.load(self.sourcefilename)

        G = nx.Graph()
        blacknode = set([])

        def get(startwordlist):
            result = []
            for word in startwordlist:
                y2 = model.most_similar(word)  # 20个最相关的
                for item in y2:
                    if not item[0] in blacknode:
                        result.append(item[0])
                        G.add_node(item[0])
                        G.add_weighted_edges_from([(word, item[0], item[1])])
                blacknode.add(word)
            return result

        start = [word]
        i = 0;
        while True:
            i += 1;
            if i == size:
                break
            result = get(start)
            print result
            start = result
        for node in G.nodes():
            print node
        pos = nx.spring_layout(G)
        nx.draw(G, pos=pos, node_color="r", with_labels=True, node_size=900, font_size=10)
        plt.show()

    def genmodel(self, type="all"):
        '生成词向量模型'
        print "生成词向量模型"
        self.type = type
        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.targetfilename = self.pyg.diffmodelfilepath
            self.sourcefilename = self.pyg.diffpredealfilepath

        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.targetfilename = self.pyg.diffmodeljavafilepath
            self.sourcefilename = self.pyg.diffpredealjavafilepath
        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.targetfilename = self.pyg.diffmodelxmlfilepath
            self.sourcefilename = self.pyg.diffpredealxmlfilepath
        print self.sourcefilename, "->", self.targetfilename

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        sentences = word2vec.Text8Corpus(self.sourcefilename)  # 加载语料
        model = word2vec.Word2Vec(sentences, size=200)  # 训练skip-gram模型; 默认window=5
        # 保存模型，以便重用
        model.save(self.targetfilename)

    def gendirectory(self, type="all"):
        '生成字典'
        print "生成字典"
        self.type = type
        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.targetfilename = self.pyg.directoryfilepath
            self.sourcefilename = self.pyg.diffpredealfilepath
        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.targetfilename = self.pyg.directoryjavafilepath
            self.sourcefilename = self.pyg.diffpredealjavafilepath
        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.targetfilename = self.pyg.directoryxmlfilepath
            self.sourcefilename = self.pyg.diffpredealxmlfilepath
        print self.sourcefilename, "->", self.targetfilename

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        sentences = word2vec.Text8Corpus(self.sourcefilename)  # 加载语料
        dictionary = gensim.corpora.Dictionary(sentences)
        print len(dictionary)
        dictionary.save_as_text(self.targetfilename, sort_by_word=True)

    def gendiffsanitizationtxt(self, type="all"):
        '过滤出合适的语料'
        print "过滤出合适的语料..."
        self.type = type

        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.targetfilename = self.pyg.difffilepath
        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.targetfilename = self.pyg.diffjavafilepath
        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.targetfilename = self.pyg.diffxmlfilepath

        if os.path.exists(self.targetfilename):
            os.remove(self.targetfilename)
        self.difftextfile = open(self.targetfilename, 'a')
        self.sourcefilename = self.pyg.diffdirpath
        print self.sourcefilename, "->", self.targetfilename

        list_dirs = os.walk(self.pyg.diffdirpath)
        for root, dirs, files in list_dirs:
            i = 0
            for f in files:
                i += 1
                print "处理第" + str(i) + "个",
                path = os.path.join(root, f)
                self.getcodedifffromtxt(path)
            print "共处理" + str(i) + "个文件"
        self.difftextfile.close()

    def getcodedifffromtxt(self, filepath):
        '从文本中获取代码的不同'
        f = open(filepath)
        line = f.readline()

        self.thedata = []
        start = False
        print "正在处理...:", filepath
        while line:
            line = f.readline()
            if line.startswith("Subject"):
                start = True
            if "---\n" == line:
                start = True
            if line.startswith("diff"):
                start = False
                fn = line.split()
                # print fn
                try:
                    if fn[2][2:] == fn[3][2:]:
                        ft = fn[2][2:]
                        # print ft
                        for td in self.thedata:
                            if td[0].startswith(".../"):
                                tt = td[0][4:]
                                if ft.endswith(tt):
                                    td[0] = ft
                        if self.type == "all" or self.type == "All":
                            if ft.endswith(".jar") or ft.endswith(".so") or ft.endswith(".aar") or ft.endswith(
                                    "png") or ft.endswith("jpg") or ft.endswith(".keystore") \
                                    or ft.endswith(".zip") or ft.endswith(".rar") \
                                    or ft.endswith(".md") or ft.endswith(".txt") \
                                    or ft.endswith(".bat") or ft.endswith(".classpath") or ft.endswith(".project") \
                                    or ft.endswith(".gitignore") or ft.endswith("pro") or ft.endswith(".properties") \
                                    or ft.endswith("yml") or ft.endswith("gradlew") or ft.endswith(
                                ".sh") or ft.endswith(".gnucash") \
                                    or ft.endswith("CONTRIBUTORS") or ft.endswith("yaml") or ft.endswith("LICENSE"):
                                start = True
                            elif ft.endswith(".java") or ft.endswith(".xml") or ft.endswith(".gradle"):
                                pass
                                print ft
                            else:
                                print ft
                                import time
                                time.sleep(10)
                        elif self.type == "java" or self.type == "Java":
                            if not ft.endswith(".java"):
                                start = True
                            else:
                                print ft
                        elif self.type == "xml" or self.type == "Xml":
                            if not ft.endswith(".xml"):
                                start = True
                            else:
                                print ft
                except:
                    print "except"
                    import time
                    time.sleep(10)

            if start == False:
                newline = line.replace(", ", ",").replace("}", " } ").replace(";", " ; ")

                if line.startswith("+++") or line.startswith("---"):
                    pass
                elif line.startswith("diff"):
                    pass
                elif line.startswith("similarity index"):
                    pass
                elif line.startswith("From"):
                    pass
                elif line.startswith("Date:"):
                    pass
                elif line.startswith("new file mode"):
                    pass
                elif line.startswith("deleted file mode"):
                    pass
                elif line.startswith("rename from"):
                    pass
                elif line.startswith("rename to"):
                    pass
                elif line.startswith("index"):
                    pass
                elif line.startswith("\ No newline at end of file"):
                    pass
                elif re.search("@@(\s*)(\-[0-9]+,[0-9]+)(\s)*(\+[0-9]+,[0-9]+)(\s*)@@", line, re.I):
                    df = re.split("@@", line)
                    if not df[2] == '\n':
                        self.difftextfile.write(df[2])
                else:
                    self.difftextfile.write(newline)
            if start == True:
                if re.search("(\s*)\\|(\s* )([0-9]+)(\+*\-*)", line, re.I):
                    temp = re.split("\\|", "".join(line.replace("+", " ").replace("-", " ").split()))
                    self.thedata.append(temp)
                else:
                    pass
        f.close()

    def getsmailarword(self, word="activity", type="all", number=10):
        '获得相似单词'
        print "获得相似单词"
        self.type = type
        if self.type == "All" or self.type == "all":
            print "类型是所有..."
            self.sourcefilename = self.pyg.diffmodelfilepath

        elif self.type == "Java" or self.type == "java":
            print "类型是Java..."
            self.sourcefilename = self.pyg.diffmodeljavafilepath

        elif self.type == "Xml" or self.type == "xml":
            print "类型是Xml..."
            self.sourcefilename = self.pyg.diffmodelxmlfilepath
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        model = word2vec.Word2Vec.load(self.sourcefilename)
        return model.most_similar(word, topn=number)  # 20个最相关的
