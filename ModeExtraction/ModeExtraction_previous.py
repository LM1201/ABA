#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import os

import numpy as np
from gensim.models import word2vec

from GetInformation.GithubRepo import  GithubRepo


class ModeExtraction:
    '模式提取类,从diff里提取出主要的信息'
    count = 0

    def __init__(self, user="codinguser", repo="gnucash-android"):
        '初始化工作'
        self.pyg = GithubRepo(user=user, repo=repo)
        ModeExtraction.count+=1
        '在diffs5.txt 文件中存放必要的信息'
        if not os.path.exists(self.pyg.diffdirpath3):
            os.mkdir(self.pyg.diffdirpath3)
        self.difftextpredealfile = open(os.path.join(self.pyg.diffdirpath3,"diffs5.txt"), 'a')
        print self.difftextpredealfile

    def getsmailerchange(self):
        '加载词向量'
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        self.allmodel = word2vec.Word2Vec.load(self.pyg.diffmodelfilepath)
        self.javamodel = word2vec.Word2Vec.load(self.pyg.diffmodeljavafilepath)
        # self.xmlmodel = word2vec.Word2Vec.load(self.pyg.diffmodelxmlfilepath)

        'commit的数据集'
        print self.shaset

        '查找diff information'
        coll = self.pyg.diffinfocoll
        '解析查找到的信息'
        for data in coll.find():
            if data["name"] in self.shaset:
                for key, value in data["diff"].items():
                    print key
                    self.difftextpredealfile.writelines(key + "\n")
                    'xml文件跳过'
                    if key.endswith("xml"):
                        pass
                    else:
                        for k, v in value.items():
                            print k,
                            self.difftextpredealfile.writelines(k + "\n")
                            if len(v) > 20:
                                pass
                            else:
                                '如果距离小于5或10，写如文件'
                                for it in self.dealdiff(v)[2]["5"]:
                                    self.difftextpredealfile.write("\t")
                                    self.difftextpredealfile.writelines(it)
                                    self.difftextpredealfile.writelines("\n")
                                    # for it in self.dealdiff(v)[2]["10"]:
                                    #     self.difftextpredealfile.write("\t\t")
                                    #     self.difftextpredealfile.writelines(it)
                                    #     self.difftextpredealfile.writelines("\n")
                                    # for it in self.dealdiff(v)[2]["15"]:
                                    #     self.difftextpredealfile.write("\t\t")
                                    #     self.difftextpredealfile.writelines(it)
                                    #     self.difftextpredealfile.writelines("\n")
                                    # for vv in v:0
                                    #     print vv
        # print coll.find_one()
        self.difftextpredealfile.close()


    def dealdiff(self,v=[]):
        add=[]
        delete=[]
        smailar0={"0":[],"5":[],"10":[],"15":[],"20":[],"other":[]}
        for sentence in v:
            if sentence.startswith("+"):
                add.append(sentence)
            if sentence.startswith("-"):
                delete.append(sentence)
        # print add
        # print delete
        if add==[]:
            pass
            print "**role:delete**",
            print delete
        if delete==[]:
            pass
            print "**role:add**",
            # print add

        if not add==[] and  not delete==[]:
            # print add
            # print delete
            for sa in add:
                nsa= sa.replace("<", " ").replace(">", " ").replace("}", " ").replace(",", " ") \
                    .replace("!", " ").replace("\"", " ") \
                    .replace("\\", " ").replace("(", " ").replace(")", " ").replace(";", " ").replace("=", " ").replace(
                    "@+", " ").replace("@", " ") \
                    .replace('\t', '').replace('\n', '').replace("\r", " ").replace("\s", " ").replace("   ",
                                                                                                       " ").replace(
                    "  ", " ").replace("/", " ") \
                    .replace("{", " ").replace("}", " ").replace("(", " ").replace(")", " ")

                for sd in delete:
                    nsd = sd.replace("<", " ").replace(">", " ").replace("}", " ").replace(",", " ") \
                    .replace("!", " ").replace("\"", " ") \
                    .replace("\\", " ").replace("(", " ").replace(")", " ").replace(";", " ").replace("=", " ").replace(
                    "@+", " ").replace("@", " ") \
                    .replace('\t', '').replace('\n', '').replace("\r", " ").replace("\s", " ").replace("   ",
                                                                                                       " ").replace(
                    "  ", " ").replace("/", " ") \
                    .replace("{", " ").replace("}", " ").replace("(", " ").replace(")", " ")
                    if  self.getsentencesmaliar(nsa,nsd)==0:
                        smailar0["0"].append((sa,sd))
                    elif self.getsentencesmaliar(nsa,nsd)<=5:
                        smailar0["5"].append((sa,sd))
                    elif self.getsentencesmaliar(nsa,nsd)<=10:
                        smailar0["10"].append((sa,sd))
                    elif self.getsentencesmaliar(nsa, nsd) <= 15:
                        smailar0["15"].append((sa,sd))
                    elif self.getsentencesmaliar(nsa, nsd) <= 20:
                        smailar0["20"].append((sa,sd))
                    else:
                        smailar0["other"].append((sa,sd))
        return add,delete,smailar0


    def getsentencesmaliar(self,scenceA,scenceB):
        am = self.allmodel
        import numpy as np
        f1=scenceA.split()
        f2=scenceB.split()
        n1 = len(scenceA.split())
        n2 = len(scenceB.split())
        # 创建一个距离矩阵
        dist = np.zeros(n1 * n2)
        for i in range(n1):
            for j in range(n2):
                try:
                    t1=am.wv[f1[i]]
                except KeyError:
                    # print f1[i]
                    t1=am.wv["+"]
                try:
                    t2=am.wv[f2[j]]
                except:
                    t2 = am.wv["-"]
                dist[i * n2 + j] = self.euclid_dist(t1, t2)+0.01

        first_signature = np.ones(n1)
        second_signature = np.ones(n2)
        # print  "*****", dist
        return self.emd(dist,first_signature, second_signature)

    def euclid_dist(self,feature1, feature2):
        """计算欧氏距离"""
        if len(feature1) != len(feature2):
            print "ERROR: calc euclid_dist: %d <=> %d" % (len(feature1), len(feature2))
            return -1
        return np.sqrt(np.sum((feature1 - feature2) ** 2))

    def emd(self,dist, w1, w2):
        import numpy as np
        import rpy2.robjects as robjects
        # 从R中导入lp.transport()
        robjects.r['library']('lpSolve')
        transport = robjects.r['lp.transport']

        """R的transport()函数用来计算EMD"""
        # transport()的参数
        costs = robjects.r['matrix'](robjects.FloatVector(dist),
                                     nrow=len(w1), ncol=len(w2),
                                     byrow=True)
        row_signs = ["<"] * len(w1)
        row_rhs = robjects.FloatVector(w1)
        col_signs = [">"] * len(w2)
        col_rhs = robjects.FloatVector(w2)

        t = transport(costs, "min", row_signs, row_rhs, col_signs, col_rhs)
        flow = t.rx2('solution')

        dist = dist.reshape(len(w1), len(w2))
        flow = np.array(flow)
        work = np.sum(flow * dist)
        # print "***", (np.sum(flow)),work

        emd = (work+np.float64(2)) /( np.sum(flow)+np.float64(0.1))
        return emd

    def getsmailarword(self, word="activity", type="all", number=10):
        pass
    # class Role:
    #     def __init__(self, name=""):
    #         self.name=name
    # class Gainian:
    #     def __init__(self):
    #         self.roleList = []
    #     def addrole(self,role=Moshitiqu.Role()):
    #         self.roleList.append(role)

    shaset = set([u'df9a06e56d0100cb96f0c4dd4d09cf21d283be7a', u'47dcdaf8715ffaf90dbb0315f7aec7a282cb69c2',
                  u'ab88399cf5b05f7ed5ce182dd77a32b4c60f0632', u'f4624eecb51f74ed0db496f4eda9bf76299b59f6',
                  u'6c320cfca1ec671f0d31f42729db17ffb5b8f525', u'08e34b3c57f31bea8229a14dc26e936a3a5a5377',
                  u'7a5085db333e35c7936cd0abba8c4098960cea93', u'48ee4b049f10f44e02c948d118f2bc023efeb3fb',
                  u'42ce9b7f24751b8f18ba1b4707a149e9e3c3ac4f', u'0b29acd691a66fbf6c91a7fafbc487131cfcf2b6',
                  u'f28239b55a1147ce540d735dad1bed1a3ee3b90b', u'885f10da2b34167dfc1909d97035b5130d812b95',
                  u'a8357079eef4f0de4c8961309aac855b0f5aa3e2', u'56d37550baf148270c68356bb3e3acbe6145af34',
                  u'87498fbd2d10e945e6ef93266df3d4ab8a50332c', u'1f64c6ca00cee2f4940d22dda8d41f25a9e0ecb2',
                  u'7ee05a6773648447e0e593f767468482b7ac85ff', u'63d20ca96aa1f3030a5799b49d05617dda23d179',
                  u'eb6ad5a3eb776899498fbe4a21f0740df20176af', u'07dc9568723f19ea9f3bec4a002d795adb683207',
                  u'673774bb0b200ecd9fe81c4096f8f7579721602a', u'd5b873570a76809071211478f0c831f09ab07326',
                  u'921b63a5689d32c8ecfd45e31c09eff52be266e5', u'470fa0faf5877432e7477e904a390f488c503c29',
                  u'792b2da18dca17f7db26076d20ca531947ad2e69', u'4e95e9e0edab6c0a4659925b0b1776ac20b63e62',
                  u'7bc13b39ca0cd0e06b527d72c22a3cc9862509e2', u'4b90852f7168fc0a893911941e542fd14d9efca0',
                  u'9f2a57834fa89c997a8402798453c5dc7a17fdee', u'ad62cec2ac198bc2951e306ca05f754b51f9c357',
                  u'ec673cc6ce109118578893d85ca93468d092565c', u'932c38034613f05a7e9dd42f8d58522a57de8d3c',
                  u'b77f526fca4f7dac1e9aa1f0792612ef2d644d97', u'401c2d292c63c1f1575d91dafd0c281ceee7daea',
                  u'777ead9c25dfdf8c35174980ba88320ee4bb25c3', u'92a5a82173329b2bedfeffd88c06fbb8aa2d28be',
                  u'8413ef0a980293f4232e5d2b44f8ae416bdd0d7b', u'b43b5dd31da7f75f998360641dce5ce22c1d2a58',
                  u'111d1c2d5d8e57bf26c10972a44befbbd481e062', u'255505b6b9a318c3a44ae6706af1e9dd256412f8',
                  u'a1076dd9e4c471aba40e972a89189c4a46c398c2', u'97a1dca8b9bf3c03f88b03c4d45a69c759d751ef',
                  u'0e111daeb608c73a178d93b669acae78dddc5ccc', u'e6b619db1d36df79e0aec042aac1bb14ef4b2a60',
                  u'b522690da10fe1f7922ebad85df85f894f438891', u'9f1a68e737b755423a3164db700c1914d54e7e4f',
                  u'957a41712f4b103e9ca3ff72bc8500b3dbf6d0a0', u'c08c98c4f4d9cfb4913b2bd8ac25bd75311572f4',
                  u'48c8ca798e6929c974f6bff1cac706254099715b', u'ae6d8d48b4ee60eb99b9dca5ed3544bf574ae8ac',
                  u'904f30137d4cd15319d4b292ee18347f5a327640', u'c07ee99165aa0024819e294607ed0efe9cb91c04',
                  u'0aef6f5896d74221698feda72400000524ef2a93', u'896329da8306c13ec810c5678a4b3377c8aee215',
                  u'8b867b52bd7758c265167c4cfb04f1039a814188', u'47729837723f6ba603c5c1f444799ded27069dd9',
                  u'19a346bfd4886d7b4c252eb773aa307cb4256990', u'c9894bcc589eca048ce6b72dc18b9fe75047862f',
                  u'28a3b14873a29c9d17fa85e0262cbfd8bd759faf', u'66cc5332e67e04cb6ce00c558237ea32a77bc627',
                  u'62242ff79cb9d21ac08b8a2546e282fe674d1d61', u'e2e218194538ca389d6aef26dcfc1ba13a378434',
                  u'516f719e82465104de35ff42b9f6b041d92bf392', u'6d625ac6f6a6673485bf037d05de40b83292a890',
                  u'aed09ce8e706ce0a7ee1d7d058dcc8b53a9010aa', u'98e2674689d4a8a954be0b624c37d6776822dede',
                  u'de6afbc1fedfde3455e7126dc368265fb4b7eed3', u'fd7007ef21c50b1fb3b24d06ac63173b02832f5f',
                  u'dd78d159b72bf602114bbc5b695ba120064171ae', u'0415d936683f416a2bb778a949961defd0fbc12b',
                  u'903a29e86f98bbea1be4780f83f7a9c1f55d0220', u'8afab48e943768243fd369ec8427bc8b94217ba3',
                  u'6848f5189c35f5c82ce04c7f356fe74b1d1fc127', u'bcdab71c58f2ade300aa4cea23f0c9f728f26d88',
                  u'9fbf0365dd1c5b2e16273adfdcaf1c9414f7145d', u'17f61876ba17849f41538bdc4438482037f1dca6',
                  u'e95c6653ded13a9973f7bd7b2440e3f256f39694', u'd8b008740f659651714b9e3a0f997d62eae0f9b2',
                  u'36accb0f547047d158c3a2cc7c7f851a0df87c65', u'd3e9dcee9fe857c7f385427120ba8921a448138a',
                  u'cee56006d970d1be24c3c3c9bf7b43c33d980a31', u'9adaf901408e18a1390447bcab211b1a55989bf4',
                  u'7ae602de8467e9cdd5ecdcd43e4c447c8ef713ee', u'13ef64a5bd2be9ec0b3923c90a209d6a46745df1',
                  u'8daaf0066e2ed72fcfa54146be5d72247cbd0b97', u'739cb7bf43d26216fe1b66d7f63dc5c6637d36d5',
                  u'24555f0f2809b23b2fa549511b44cfaa88539056', u'17b4b8b2e22bb5d7cbda3b1745bbcf1407f1b10f',
                  u'dd6052dbdb11aac363892780d6d6970c885750a3', u'18a35b5efddd06f9f1de3f5ddd976ea9090e1274',
                  u'bb9637f97c3d81e6b5507ab7b042e47dbfa898eb', u'bc718bc214f2ce4a5f66bbf6528bca8422822e02',
                  u'c5814082cfc0205102b418b2866f30e20337dc42', u'8a61607a0da2abd7829c9b4e61a50f1289b2193d',
                  u'a54558220014c899ff09121c1a79fae1c2a13aa0', u'3a232c0151a89a9f18b0383e545830fb7533abd6',
                  u'6dd3dc944fb7f0ebb106475cadc5ab89cd4750ca', u'7e8010fca36d1101a6c60779961af0c06a0fecb7',
                  u'945fd36b6239a1fe01526d91797c37d36e700092', u'498bf48ba61cba71b0a88d7615f613d802494c6c',
                  u'e50124623962b31959df3fdaaa5fbe8f42e45b7e', u'5d6e801f6b24e55833adc76af43db927d7d86003',
                  u'5911aa6dba047b29cef535bc401002da2512171b', u'42817b593849fdb1853d724337c33836200d1e8e',
                  u'969da1a5b521bf0d8feea3881e705f2f81d5c10d', u'4a587640a54089ee36433c0ecea15b6e29a4c89b',
                  u'2d76e1f00ddd684179f4b97b54340eccb63a6daa', u'1794882757a37c108c4b4cf40f6876aa7a51c87d',
                  u'e00b20a4b933b2752c1d7468bf444395fe543c24', u'dac7a311ca38b7dc4f0d5084aaeeed4b81e618a7',
                  u'd88c6c88c3e66486e9bc822be18cda0feb5f3066', u'1cae0a3fa57040b2a8a43ee14c4956ab0abbadab',
                  u'40d759d595cd33d11dd8d6eca1bc447ec1290b60', u'6c4139e92639ae0ce7fb8f4d3a1112ef8a741db1',
                  u'4ee9bce2280feee0cf33eec9577ece86da8c135d', u'96ae1d10d3dd35bd3e112e7ccc49b3d05597a5ad',
                  u'1617d80aff45d2da5ef502a0ba06bd109d5c06f6', u'df48830e1b84a7bbcc8f040753f98d9ba6462e1c',
                  u'd0c6f542b0ebb194b447ccb818fc571111a945ec', u'9300844620b4ac84636a92a73ca8f8119f6c8bb5',
                  u'05ea0582cd8aded5c5a912ccb52c83540ff51136', u'4a34625499862ce17b29c02e26a3e3a8296037f0',
                  u'b3187d6d5edaa2aef2a4e4f499cc5d179cf3e014', u'041c4a3904ca6424ee07a62375ac14b7731e4b82',
                  u'710c2a95c813b4f4b14f3daac7dafe9864597e78', u'a74311a1cf6b2697d4511c5b8168944b451c95b6',
                  u'fd2c7a6f9a4f7f1c0a440955954e2eb143f87575', u'77d9323bd5cb4a1fb40fb9a894943a9e9d7a73c4',
                  u'4d754cf4e06ccb7d32a5da06fc259c8944dca9d7', u'7416cd376ab2183d61b63e73134c7841bd93cb6f',
                  u'7e31d1a4e95667adb9a6e834a4e2cba7db9ce162', u'46859ae6e64f39a6207c1074ba309db85ff8fe30',
                  u'6915fd516ee884b0ecb13cb83c4e937c345e5160', u'fa02d8ea9a16e97ae716dde03406be6727ce0b82',
                  u'f5e8cac3548e26caa463860a1eb96ebf3aa33087', u'a003d519d5647be31786f4e6b46d0399fc7bbf2a',
                  u'ade07dd6339597d8f1b4358710ae52afbb61d35e', u'c58e4bb2f5329aec00e283c97250ed6bcb774ad7',
                  u'cefbbb5603416fafbea70fe3ebb9cd0a688dc7d8', u'893bd1a9cb89671fa312414d2d36a4ec04d5a1d1',
                  u'e5daf4bf0b3fc7ab2897a06b87fed8366b2db353', u'8ecc38bc65d17ba87b18691a4f9e816615f33032',
                  u'c13a94c2b3c10893452200bbb630e15821281725', u'96a204564147d54ca0b2ec8b393fb5c3aa33c5d1',
                  u'123afcb7a1bd74e599342089f7f8b57568cdd4e9', u'd6310a65def44f8a1249a339a874da25b3c05836',
                  u'a6aa211734accf94664da91316cf6e26bed0de92', u'7b345af652ff83ae3c793438b500b314681fb5d1',
                  u'4893e8e45dfe980eb51710479a140df629dc9884', u'89f2ff570abd6702782c78af157c9926f6950344',
                  u'5d4e0fb47cac2080ebfe220f12a7684c30e57a59', u'd9c3605822a214b98f715bb5a7ba100abad5d8ed',
                  u'f1281e6e9285ff390074cf7064476da673f222ad', u'ce50ee116f18a373f30cb135ee48b5ad6c187db0',
                  u'52f72970eada423f10ed11359f628c5755545b24', u'f9b3a301af6b1a10e146a6a412efdb9f295db152',
                  u'2894466858715e5583932ff4751aa1c6eb5d2dde', u'ec23d695d2c0d5d500bf9057dc260299adfbf61d',
                  u'daf2e8ba4261d19b4b3c4eebee5a61773c86632b', u'589e74fdc3014d73091ed1a3ebecb0c2e16257aa',
                  u'0f121edb68f2f04e957bc9433e7531140a0bbe16', u'54cfecd61ce4cf4feaf78c0de1b747ed454c7beb',
                  u'eaeb5a3bafcecc798540830e1ed293fa37fb8565', u'95fc7786ab5b85bae3fcb66cd3c68bc9c9497e81',
                  u'5e05e52dc7f16025d6753a85489af53f8cc4a007'])


    def getIntentdiff(self):
        '查找diff information'
        coll = self.pyg.diffinfocoll
        '解析查找到的信息'
        All=""
        for data in coll.find():
            # if data["name"] in self.shaset:
                for key, value in data["diff"].items():
                    s= "#"+key+"#\n"
                    hasintent=False
                    for k,vlist in value.items():
                       for v in vlist:
                           import re
                           if  re.search( r'intent', v, re.M|re.I):
                                hasintent=True
                                s+= v+"\n"
                    if not hasintent:
                        s=""
                    All+=s
                    yield s

if __name__=="__main__":
    a= ModeExtraction()
    for x in a.getIntentdiff():
        print x

