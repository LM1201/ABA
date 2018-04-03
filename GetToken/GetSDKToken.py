#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import GetFilePathRoot
import logging

class GetTaskType:
    (HTMLTOTXT,CLASS,METHOD)=range(3)

class GetSDKToken:
    count=0
    def __init__(self):
        GetSDKToken.count+=1
        self.sdk_docs=os.path.join(GetFilePathRoot.get_root_dir(), "sdk_docs_html", "reference")
        self.sdk_target = os.path.join(GetFilePathRoot.get_root_dir(), "sdk_docs_txt")
        self.sdk_result = os.path.join(GetFilePathRoot.get_root_dir(), "output")
        if not os.path.exists(self.sdk_target):
            os.mkdir(self.sdk_target)
        if not os.path.exists(self.sdk_result):
            os.mkdir(self.sdk_result)
        self.initlog()

    def log(self, type):
        import json
        if not os.path.exists(self.logfile):
            load_dict = {'htmltotxt': False, 'class': False, 'method': False}
            logging.info(load_dict)
            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)
        with open(self.logfile, 'r') as load_f:
            load_dict = json.load(load_f)
            if type == GetTaskType.HTMLTOTXT:
                load_dict['htmltotxt'] = True
            if type ==  GetTaskType.CLASS:
                load_dict['class'] = True
            if type == GetTaskType.METHOD:
                load_dict['method'] = True

            logging.info(load_dict)
            self.htmltotxttask = load_dict['htmltotxt']
            self.classsummarytask= load_dict['class']
            self.methonsummarytask = load_dict['method']

            with open(self.logfile, "w") as dump_f:
                json.dump(load_dict, dump_f)

    def initlog(self):
        self.htmltotxttask = False
        self.classsummarytask = False
        self.methonsummarytask = False
        self.logfile = self.sdk_result + "/GetSDK.txt"
        self.outputfile = self.sdk_result + "/GetSDKOutput.txt"
        self.log(None)
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

    def htmltotxt(self):
        list_dirs = os.walk(self.sdk_docs)
        i = 0
        for root, dirs, files in list_dirs:
            self.logger.info((i, root))
            for f in files:
                if f=="package-summary.html":
                    i=i+1
                    import shutil
                    shutil.copyfile(os.path.join(root, f), os.path.join(self.sdk_target, str(i) + ".txt"))
                # print os.path.join(root, f)
    def do(self):
        if not self.htmltotxttask:
            self.htmltotxt()
            self.log(GetTaskType.HTMLTOTXT)
        if not self.classsummarytask:
            self.classsummry()
            self.log(GetTaskType.CLASS)
        if not self.methonsummarytask:
            self.methodsummary()
            self.log(GetTaskType.METHOD)


    def classsummry(self):
        with open(os.path.join(self.sdk_result, "sdk_class_summry.txt"), "w") as asummry:
            list_dirs = os.listdir(self.sdk_target)
            print list_dirs
            for filename in list_dirs:
                txt = os.path.join(self.sdk_target, filename)

                with open(txt) as html_doc:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_doc)
                    for i in soup.find_all('h1'):
                        packagename = i.string
                        if packagename in ["Overview", "Android MIDI Terminology", "Writing a MIDI Application",
                                           "Creating a MIDI Virtual Device Service", "Using MIDI Over Bluetooth LE"]:
                            pass
                        else:
                            print i.string
                            asummry.write(i.string + "\n")
                    for i in soup.find_all('h2'):
                        if i.attrs == {}:
                            ul = i.next_element.next_element.next_element
                            if ul.name == "ul":
                                print "\t" + i.string
                                asummry.write("\t" + i.string + "\n")
                                for child in ul.descendants:
                                    if child.name == "a":
                                        print "\t\t" + child.string
                                        asummry.write("\t\t" + child.string + "\n")

    def methodsummary(self):
        with open(os.path.join(self.sdk_result, "sdk_method_summry.txt"), "w") as asummry:
            list_dirs = os.listdir(self.sdk_target)
            for filename in list_dirs:
                txt = os.path.join(self.sdk_target, filename)
                with open(txt) as html_doc:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_doc)
                    for i in soup.find_all('h1'):
                        packagename = i.string
                        if packagename in ["Overview", "Android MIDI Terminology", "Writing a MIDI Application",
                                           "Creating a MIDI Virtual Device Service", "Using MIDI Over Bluetooth LE"]:
                            pass
                        else:
                            print i.string
                            asummry.write(i.string + "\n")
                    for i in soup.find_all('h2'):
                        if packagename in ["Overview", "Android MIDI Terminology", "Writing a MIDI Application",
                                           "Creating a MIDI Virtual Device Service", "Using MIDI Over Bluetooth LE"]:
                            break
                        if i.attrs == {}:
                            ul = i.next_element.next_element.next_element
                            if ul.name == "ul":
                                print "\t" + i.string
                                if i.string == "Classes":
                                    asummry.write("\t" + i.string + "\n")
                                    ul = i.next_element.next_element.next_element
                                    for child in ul.descendants:
                                        if child.name == "a":
                                            asummry.write("\t\t" + child.string + "\n")
                                            print "\t\t" + child.string
                                            docpath = os.path.join(self.sdk_docs, str(packagename.replace(".",
                                                                                             "/")) + "/" + str(child.string) + ".html")
                                            with open(docpath) as classhtml:
                                                soup = BeautifulSoup(classhtml)
                                                for cls in soup.find_all('h2'):
                                                    if cls.string == "Protected Constructors" or cls.string == "Public Constructors":
                                                        print "\t\t\t" + "Constructors"
                                                        asummry.write("\t\t\t" + "Constructors" + "\n")
                                                        con = cls.next_element.next_element.next_element.next_element.next_element
                                                        for c in con.descendants:
                                                            if c.name == "h4":
                                                                s = ""
                                                                for string in c.strings:
                                                                    s += string
                                                                asummry.write(
                                                                    "\t\t\t\t" + ' '.join(
                                                                        s.replace("\t", "").replace(",", ", ").replace(
                                                                            u'\xa0', u' ').replace("\n",
                                                                                                   " ").split()) + "\n")
                                                                print "\t\t\t\t" + ' '.join(
                                                                    s.replace("\t", "").replace(",", ", ").replace(
                                                                        u'\xa0',
                                                                        u' ').replace(
                                                                        "\n", " ").split())
                                                        for sibling in con.next_siblings:
                                                            if sibling.name != None:
                                                                for c in sibling.descendants:
                                                                    if c.name == "h4":
                                                                        s = ""
                                                                        for string in c.strings:
                                                                            s += string
                                                                        asummry.write(
                                                                            "\t\t\t\t" + ' '.join(
                                                                                s.replace("\t", "").replace(",",
                                                                                                            ", ").replace(
                                                                                    u'\xa0', u' ').replace("\n",
                                                                                                           " ").split()) + "\n")
                                                                        print "\t\t\t\t" + ' '.join(
                                                                            s.replace("\t", "").replace(",",
                                                                                                        ", ").replace(
                                                                                u'\xa0', u' ').replace("\n",
                                                                                                       " ").split())
                                                    elif cls.string == "Public Methods":
                                                        asummry.write("\t\t\t" + "Public Method" + "\n")
                                                        print "\t\t\t" + "Method"
                                                        con = cls.next_element.next_element.next_element.next_element.next_element
                                                        for c in con.descendants:
                                                            if c.name == "h4":
                                                                s = ""
                                                                for string in c.strings:
                                                                    s += string
                                                                asummry.write(
                                                                    "\t\t\t\t" + ' '.join(
                                                                        s.replace("\t", "").replace(",", ", ").replace(
                                                                            u'\xa0', u' ').replace("\n",
                                                                                                   " ").split()) + "\n")
                                                                print "\t\t\t\t" + ' '.join(
                                                                    s.replace("\t", "").replace(",", ", ").replace(
                                                                        u'\xa0', u' ').replace("\n", " ").split())
                                                        for sibling in con.next_siblings:
                                                            if sibling.name != None:
                                                                for c in sibling.descendants:
                                                                    if c.name == "h4":
                                                                        s = ""
                                                                        for string in c.strings:
                                                                            s += string
                                                                        asummry.write(
                                                                            "\t\t\t\t" + ' '.join(
                                                                                s.replace("\t", "").replace(",",
                                                                                                            ", ").replace(
                                                                                    u'\xa0', u' ').replace("\n",
                                                                                                           " ").split()) + "\n")
                                                                        print "\t\t\t\t" + ' '.join(
                                                                            s.replace("\t", "").replace(",",
                                                                                                        ", ").replace(
                                                                                u'\xa0', u' ').replace("\n",
                                                                                                       " ").split())
                                                    elif cls.string == "Protected Methods":
                                                        asummry.write("\t\t\t" + "Protected Method" + "\n")
                                                        print "\t\t\t" + "Method"
                                                        con = cls.next_element.next_element.next_element.next_element.next_element
                                                        for c in con.descendants:
                                                            if c.name == "h4":
                                                                s = ""
                                                                for string in c.strings:
                                                                    s += string
                                                                asummry.write(
                                                                    "\t\t\t\t" + ' '.join(
                                                                        s.replace("\t", "").replace(",", ", ").replace(
                                                                            u'\xa0', u' ').replace("\n",
                                                                                                   " ").split()) + "\n")
                                                                print "\t\t\t\t" + ' '.join(
                                                                    s.replace("\t", "").replace(",", ", ").replace(
                                                                        u'\xa0',
                                                                        u' ').replace(
                                                                        "\n", " ").split())
                                                        for sibling in con.next_siblings:
                                                            if sibling.name != None:
                                                                for c in sibling.descendants:
                                                                    if c.name == "h4":
                                                                        s = ""
                                                                        for string in c.strings:
                                                                            s += string
                                                                        asummry.write(
                                                                            "\t\t\t\t" + ' '.join(
                                                                                s.replace("\t", "").replace(",",
                                                                                                            ", ").replace(
                                                                                    u'\xa0', u' ').replace("\n",
                                                                                                           " ").split()) + "\n")
                                                                        print "\t\t\t\t" + ' '.join(
                                                                            s.replace("\t", "").replace(",",
                                                                                                        ", ").replace(
                                                                                u'\xa0', u' ').replace("\n",
                                                                                                       " ").split())
                                                    elif cls.string == "Fields":
                                                        asummry.write("\t\t\t" + "Field" + "\n")
                                                        print "\t\t\t" + "Field"
                                                        con = cls.next_element.next_element.next_element.next_element.next_element
                                                        for c in con.descendants:
                                                            if c.name == "h4":
                                                                s = ""
                                                                for string in c.strings:
                                                                    s += string
                                                                asummry.write(
                                                                    "\t\t\t\t" + ' '.join(
                                                                        s.replace("\t", "").replace(",", ", ").replace(
                                                                            u'\xa0', u' ').replace("\n",
                                                                                                   " ").split()) + "\n")
                                                                print "\t\t\t\t" + ' '.join(
                                                                    s.replace("\t", "").replace(",", ", ").replace(
                                                                        u'\xa0',
                                                                        u' ').replace(
                                                                        "\n", " ").split())
                                                        for sibling in con.next_siblings:
                                                            if sibling.name != None:
                                                                for c in sibling.descendants:
                                                                    if c.name == "h4":
                                                                        s = ""
                                                                        for string in c.strings:
                                                                            s += string
                                                                        asummry.write(
                                                                            "\t\t\t\t" + ' '.join(
                                                                                s.replace("\t", "").replace(",",
                                                                                                            ", ").replace(
                                                                                    u'\xa0', u' ').replace("\n",
                                                                                                           " ").split()) + "\n")
                                                                        print "\t\t\t\t" + ' '.join(
                                                                            s.replace("\t", "").replace(",",
                                                                                                        ", ").replace(
                                                                                u'\xa0', u' ').replace("\n",
                                                                                                       " ").split())

                                                    # if i.string == "Classes":
                                                    elif cls.string == "Constants":
                                                        asummry.write("\t\t\t" + "Constant" + "\n")
                                                        print "\t\t\t" + "Contstant"
                                                        con = cls.next_element.next_element.next_element.next_element.next_element
                                                        for c in con.descendants:
                                                            if c.name == "h4":
                                                                s = ""
                                                                for string in c.strings:
                                                                    s += string
                                                                asummry.write(
                                                                    "\t\t\t\t" + ' '.join(
                                                                        s.replace("\t", "").replace(",", ", ").replace(
                                                                            u'\xa0', u' ').replace("\n",
                                                                                                   " ").split()) + "\n")
                                                                print "\t\t\t\t" + ' '.join(
                                                                    s.replace("\t", "").replace(",", ", ").replace(
                                                                        u'\xa0',
                                                                        u' ').replace(
                                                                        "\n", " ").split())
                                                        for sibling in con.next_siblings:
                                                            if sibling.name != None:
                                                                for c in sibling.descendants:
                                                                    if c.name == "h4":
                                                                        s = ""
                                                                        for string in c.strings:
                                                                            s += string
                                                                        asummry.write(
                                                                            "\t\t\t\t" + ' '.join(
                                                                                s.replace("\t", "").replace(",",
                                                                                                            ", ").replace(
                                                                                    u'\xa0', u' ').replace("\n",
                                                                                                           " ").split()) + "\n")
                                                                        print "\t\t\t\t" + ' '.join(
                                                                            s.replace("\t", "").replace(",",
                                                                                                        ", ").replace(
                                                                                u'\xa0', u' ').replace("\n",
                                                                                                       " ").split())

                                else:
                                    asummry.write("\t" + i.string + "\n")
                                    ul = i.next_element.next_element.next_element
                                    for child in ul.descendants:
                                        if child.name == "a":
                                            print "\t\t" + child.string
                                            asummry.write("\t\t" + child.string + "\n")
if __name__ == "__main__":
    get=GetSDKToken()
    get.do()
# getclass()
# Test2(root)

