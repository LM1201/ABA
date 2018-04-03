import re
class Entities(object):
    def __init__(self):
        super(Entities, self).__init__()
        self.AllEntities = []
        self.EntityNames = {}
    def append(self, entity):
        if entity.Name is not None:
            self.EntityNames[entity.Name] = entity
        for e in self.AllEntities:
            if (e.Name == entity.Name):
                self.AllEntities[self.AllEntities.index(e)]=entity
        if entity not in self.AllEntities:
            self.AllEntities.append(entity)
    def __getitem__(self, item):
        if item == '$':
            return anyentity('$')
        if item in self.EntityNames:
            return self.EntityNames[item]
        else:
            print("Entity name %s can not be found!" % (item))
            e=stringentity(item+"=(\"\")")
            self.append(e)
            return e
        for entity in self.AllEntities:
            if (entity.Name == item):
                return entity
        return None
class entity(object):
    def __init__(self,rule):
        self.Rule=rule
        self.Order=5
        self.Name=""
        self.Match=""
        self.entities=[]
        self.Core=None
    def parserule(self):
        pass
    def match(self,input):
        pass
    def __str__(self):
        return self.Rule
class anyentity(entity):
    def __init__(self,rule):
        super(anyentity, self).__init__(rule)
        self.parserule()
    def parserule(self):
        self.Name = '$'
        self.Match= '$'
    def match(self,input):
        result=[(99999,99999)];
        return self.Name, self.Match,result
class stringentity(entity):
    def __init__(self,rule):
        super(stringentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*\"((?:.)*?)\"\s*\)\s*")
        self.parserule()
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2= self.__entity_string.match(self.Rule[m.group(0).__len__():])
        self.Match=m2.group(1)
    def match(self,input):
        result=[];
        d=0
        while input.find(self.Match)>-1:
            temp=(d+input.find(self.Match),d+input.find(self.Match)+self.Match.__len__())
            result.append(temp)
            d+=input.find(self.Match)+self.Match.__len__()
            input=input[input.find(self.Match)+self.Match.__len__():]
        return self.Name, self.Match,result
class regexentity(entity):
    def __init__(self,rule):
        super(regexentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*/((?:.)*?)/\s*\)\s*")
        self.parserule()
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2= self.__entity_string.match(self.Rule[m.group(0).__len__():])
        print self.Rule
        self.Match=m2.group(1)
    def match(self,input):
        regex=re.compile(self.Match)
        return self.Name, self.Match, [m.span() for m in re.finditer(regex, input)]
class sequenceentity(entity):
    def __init__(self,rule,context):
        super(sequenceentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*((?:.)*?)\s*\)\s*")
        self.context= context
        self.ex=set([])
        self.parserule()
    def append(self,entity):
        self.entities.append(self.context[entity])
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2 = self.__entity_string.match(self.Rule[m.group(0).__len__():])
        self.Match = m2.group(1)
        for name in self.Match.split(","):
            self.append(name.strip()[1:]),
    def calu0(self,All=[]):
        for i in range(All.__len__()):
            if i==0:
                temp=All[i]
            else:
                if All[i] == [(99999,99999)] and i+1<All.__len__():
                    temp = self.calu4(All[i], All[i+1],temp)
                else:
                    temp=self.calu3(temp,All[i])
                    if temp == None or temp == []:
                        temp = self.calu2(temp, All[i])
                    if temp == None or temp == []:
                        temp = self.calu1(temp, All[i])
        return temp

    def calu4(self,A=[],B=[],temp=[]):
        result=[]
        # print "qqqqqqqqqqqqq",temp,A,B,
        for a in temp:
            for b in B:
                if a[1]<=b[0]:
                    result.append((a[0],b[0]))
                    if a[1]<b[0]:
                        self.ex.add((a[0],b[1],a[1],b[0]))
        # print result,"qqqqqqqqqqq"
        return result

    def calu2(self,A=[],B=[]):
        result=[]
        for b in B:
            for a in A:
                t = b[0] - a[1]
                s = b[1]- a[0]
                if t>=0 and float(t)/s < 0.3:
                    result.append((a[0],b[1]))
        return result

    def calu3(self,A=[],B=[]):
        result=[]
        for b in B:
            for a in A:
                t = b[0] - a[1]
                if t==0:
                    result.append((a[0],b[1]))
        return result

    def calu1(self,A=[],B=[]):
        if A.__len__()>B.__len__():
            m=9999999;
            result=[]
            for b in B:
                min=None
                for a in A:
                    t=b[0]-a[1]
                    if t>=0 and t<m:
                        m=t
                        min=a
                if min is not None:
                    result.append((min[0],b[1]))
            return result
        else:
            m = 9999999;
            result = []
            for a in A:
                min = None
                for b in B:
                    t = b[0] - a[1]
                    if t >= 0 and t < m:
                        m = t
                        min = b
                if min is not None:
                    result.append((a[0], min[1]))
            return result
    def match(self,input):
        All=[]
        for entity in self.entities:
            # if type(entity) is anyentity:
            #     # print "__________________", entity.match(input)
            #     All.append([(99999,99999)])
            #     continue
            if entity == None:
                return
            results=entity.match(input)
            for result in results[2]:
              if result[0]<0 :
                  return
            All.append(results[2])
            if len(results) >3 and results[3] is not None:
                for x in results[3]:
                    self.ex.add(x)
        # print "+++++++++++++++++++++++++++++"
        # for  a in All:
        #     if a is not []:
        #         print a
            # for aa in a:
            #     print "+++++++++++",input[aa[0]:aa[1]]
            # print input[self.calu2(All)[0][0]:self.calu2(All)[0][1]]
        result=self.calu0(All)
        return self.Name, self.Match, result,self.ex
class mixentity(entity):
    def __init__(self,rule,context):
        super(mixentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*((?:.)*?)\s*\)\s*")
        self.context= context
        self.parserule()
    def append(self,entity):
        self.entities.append(self.context[entity])
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2 = self.__entity_string.match(self.Rule[m.group(0).__len__():])
        self.Match = m2.group(1)
        for name in self.Match.split("&"):
            self.append(name.strip()[1:]),
    def match(self,input):
        for entity in self.entities:
            if entity == None:
                return
            for result in entity.match(input)[2]:
              if result[0]<0 :
                  return
        start = 0
        end =0
        result=[]
        for entity in self.entities:
            while entity.match(input[start:end])[2] ==[] and end < input.__len__():
                end += 1
            if entity.match(input[start:end]):
                result.append((entity.match(input[start:end])[2]))
                end =0
        return self.Name, self.Match,result
class tableentity(entity):
    def __init__(self,rule,context):
        super(tableentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*((?:.)*?)\s*\)\s*")
        self.context= context
        self.ex=set([])
        self.parserule()
    def append(self,entity):
        self.entities.append(self.context[entity])
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2 = self.__entity_string.match(self.Rule[m.group(0).__len__():])
        self.Match = m2.group(1)
        for name in self.Match.split("|"):
            self.append(name.strip()[1:]),
    def match(self,input):
        for entity in self.entities:
            if entity == None:
                return
            results= entity.match(input)
            for result in results[2]:
              if result[0]>0 :
                  if len(results)>=3 and results[3] is not None:
                      print results[3],"xxxxxxxxxxx"
                      for x in results[3]:
                          self.ex.add(x)
                  return self.Name, self.Match,entity.match(input)[2],self.ex,entity.match(input)[:2]
class repeatentity(entity):
    def __init__(self,rule,context):
        super(repeatentity, self).__init__(rule)
        self.__entity_name = re.compile(r"^(\w+)\s*=\s*")  # 1 group
        self.__entity_string = re.compile("^\(\s*((?:.)*?)\s*\)\s*")
        self.context= context
        self.parserule()
    def append(self,entity):
        self.entities.append(self.context[entity])
    def parserule(self):
        m = self.__entity_name.match(self.Rule)
        self.Name = m.group(1)
        m2 = self.__entity_string.match(self.Rule[m.group(0).__len__():])
        self.Match = m2.group(1)
        times=re.compile("^\$(\w+)\{\s*(\d+)\s*,\s*(\d+)\s*\}")
        self.min= times.match(self.Match).group(2)
        self.max= times.match(self.Match).group(3)
        self.append(times.match(self.Match).group(1)),
    def match(self,input):
        for entity in self.entities:
            if entity == None:
                return
            for result in entity.match(input)[2]:
                if result[0] < 0:
                    return
        start = 0
        end = 0
        result = []
        i=0
        while i<self.max:
            while entity.match(input[start:end])[2] == [] and end < input.__len__():
                end += 1
            if entity.match(input[start:end]):
                if entity.match(input[start:end])[2] ==[]:
                    break
                result.append((entity.match(input[start:end])[2][0][0] + start, end))
                start = end
                i+=1
        if i>= int (self.min) and i<= int(self.max):
            return self.Name, self.Match, result
        else:
            return self.Name, self.Match, []
class Token:
    (STRING, REGEX, SEQUENCE, MIX, TABLE, REPEAT) = range(6)
class RegexToken:
    def __init__(self, regex, token, type=None):
        self.Regex = regex
        self.Token = token
        self.EntityType = type
class RegexCore(object):
    LogFile = None
    def __init__(self, rule=None):
        super(RegexCore, self).__init__()
        self.Entities = Entities()
        self.string=re.compile("^string\s*:\s*(.*)")
        self.regex=re.compile("^regex\s*:\s*(.*)")
        self.sequence=re.compile("^sequence\s*:\s*(.*)")
        self.mix=re.compile("^mix\s*:\s*(.*)")
        self.table=re.compile("^table\s*:\s*(.*)")
        self.repeat=re.compile("^repeat\s*:\s*(.*)")
        self.rulename=re.compile(".*\s*:\s*(\w+)\s*=\s*.*\s*")
        self.tnFileName = None
        self.list=[]
        if rule is not None:
            self.InitRule(rule);
    def InitRule(self, myfile):
        self.tnFileName = myfile
        import codecs
        file_object =codecs.open(myfile, 'r', encoding='utf-8')
        texts = file_object.read()
        # print texts
        print("success load src rules:%s" % (myfile))
        self.InitRuleText(texts)
        file_object.close()
    def check(self,text):
        return True
    def InitRuleText(self, text):
        tokenRegex = [RegexToken(self.string, Token.STRING, stringentity),
                      RegexToken(self.regex, Token.REGEX, regexentity),
                      RegexToken(self.sequence, Token.SEQUENCE, sequenceentity),
                      RegexToken(self.mix, Token.MIX, mixentity),
                      RegexToken(self.table, Token.TABLE, tableentity),
                      RegexToken(self.repeat, Token.REPEAT, repeatentity),
                      ]
        print "check:",
        if self.check(text):
            print "pass"
        else:
            print "no pass"
            return
        rules = [x.strip() for x in text.split('\n')]
        tree={}
        name={}
        for rule in rules:
            self.rulename = re.compile(".*:(\w+)\s*=\s*\((.*)\)\s*")
            if self.rulename.match(rule) is not None:
                sub=[]
                for x in  self.rulename.match(rule).group(2).replace("|"," ").replace("&"," ").replace(","," ").replace("{"," ").split(" "):
                    if x.startswith("$"):
                        sub.append( x[1:])
                name[self.rulename.match(rule).group(1)]=-1
                tree[self.rulename.match(rule).group(1)]=sub
        tree['$']=[]
        while tree.__len__()>0:
             print tree
             for k,v in tree.items():
                 if v==[]:
                     self.list.append(k)
                     del tree[k]
             for k,v in tree.items():
                 for l in self.list:
                     if l in v:
                         v.remove(l)
        print self.list
        for l in self.list:
            for rule in rules:
                if self.rulename.match(rule) is not None and self.rulename.match(rule).group(1)==l:
                    for token in tokenRegex:
                        mat = token.Regex.match(rule)
                        if mat is None: continue
                        if token.Token == Token.STRING or token.Token == Token.REGEX:
                            e=token.EntityType(mat.group(1))
                            e.Core=self
                            self.Entities.append(e)
                        else:
                            e = token.EntityType(mat.group(1),self.Entities)
                            e.Core = self
                            self.Entities.append(e)
    def match(self,input,keyword):
        if keyword not in self.list:
            return
        if self.Entities.EntityNames[keyword].match(input):
            return self.Entities.EntityNames[keyword].match(input)

if __name__=="__main__":
    input='''
+  final String action = getIntent () .getAction () ;
+  if ( action != null && action.equals ( Intent.ACTION_INSERT_OR_EDIT ) )
+  Intent createTransactionIntent = new Intent ( this.getApplicationContext () , TransactionsActivity.class ) ;
+  createTransactionIntent.setAction ( Intent.ACTION_INSERT_OR_EDIT ) ;
+  createTransactionIntent.putExtra ( TransactionsListFragment.SELECTED_ACCOUNT_ID , accountRowId ) ;
+  startActivity ( createTransactionIntent ) ;
+  Intent createTransactionIntent = new Intent ( this.getApplicationContext () , TransactionsActivity.class ) ;
-  Intent restartIntent = new Intent ( this.getApplicationContext () , TransactionsActivity.class ) ;
+  createTransactionIntent.setAction ( Intent.ACTION_INSERT_OR_EDIT ) ;
+  createTransactionIntent.putExtra ( TransactionsListFragment.SELECTED_ACCOUNT_ID , mAccountId ) ;
+  createTransactionIntent.putExtra ( NewTransactionFragment.SELECTED_TRANSACTION_ID , transactionId ) ;
+  startActivity ( createTransactionIntent ) ;
-  Intent restartIntent = new Intent ( this.getApplicationContext () , TransactionsActivity.class ) ;
+  restartIntent.setAction ( Intent.ACTION_VIEW ) ;
+  restartIntent.putExtra ( TransactionsListFragment.SELECTED_ACCOUNT_ID , accountRowId ) ;
+  startActivity ( restartIntent ) ;
'''

    core = RegexCore('test')
    core.LogFile = open("test.log", "w")
    result = core.match(input, "change_Intent_intent")
    if result is not None and result[2] != []:
        print result
        for x in result[2]:
            if len(result)>=3 and result[3] is not None:
                min=99999
                temp=None
                for r in result[3]:
                    if x[0]<=r[0] and x[1]>=r[1]:
                        tm=r[0]-x[0]+x[1]-r[1]
                        if tm < min:
                            min =tm
                            temp =r
            print x,temp
            if temp is not None:
                print "\t","$"+input[x[0]:temp[2]]
                print input[temp[2]:temp[3]]
                print "\t","$" , input[temp[3]:x[1]]

    a = ModeExtraction()
    for x in a.getIntentdiff():
        input = x
        result = core.match(input, "change_Intent_intent1")
        if result is not None and result[2] != []:
            print input
            print result
            for x in result[2]:
                if len(result)>=3 and result[3] is not None:
                    min=99999
                    temp=None
                    for r in result[3]:
                        if x[0]<=r[0] and x[1]>=r[1]:
                            tm=r[0]-x[0]+x[1]-r[1]
                            if tm < min:
                                min =tm
                                temp =r
                # print x,temp
                if temp is not None:
                    print  input[x[0]:temp[2]],
                    # print input[temp[2]:temp[3]]
                    print  input[temp[3]:x[1]]
                else:
                    print input[x[0]:x[1]]
    from ModeExtraction_previous import graph

    graph.buildGraph(core, "change_Intent_intent")

    #     print x+"sssssssssssssssssssssssssssss"
    #     result=core.match(input,"Intent_intent_change")
    #     if result[2] != []:
    #         start  = result[2][0][0]
    #         end =result[2][len(result[2])-1][1]
    #         print "ZZZZZZZZZZZZZZ"+input[start:end]+"ZZZZZZZZZZZZZZ"


