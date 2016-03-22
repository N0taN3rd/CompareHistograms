import json
import re

import requests
from datetime import date

from dominateColor import get_colour_name

tokenizer = re.compile('(<[^>]+>|[a-zA-Z]+="[^"]*"|[;,])\\s*')

from util import get_files, check_if_goodURI

from datetime import date
import csv

import math
import numpy as np
from collections import defaultdict, Counter


def filterASI(f):
    return not "allTheSame_" in f and not "interval_" in f


def long():
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    goodUris = []
    origuris = []
    with open("gooduris_20160225.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            goodUris.append(uri)

    with open("origuris.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            origuris.append(uri)

    compisits = get_files(impath, lambda f: filterASI(f) and check_if_goodURI(f, goodUris))
    useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.01'
    session = requests.Session()
    session.headers.update({'User-Agent': useragent})
    got = {}
    gotURIs = []
    with open("tms2.json", "w+") as out:
        out.write("{ tms:[")
        for it in sorted(origuris):
            # tm = TimeMap("www.%s"%it)
            # print(tm.mementos)
            request = session.get("http://web.archive.org/web/timemap/json/www.%s" % it)
            # got[it] = {"tmuri":"http://web.archive.org/web/timemap/json/www.%s"%it,'uri':it,"tms":json.loads(
            # request.text)}
            try:
                got = json.loads(request.text)
                jsn = json.dumps(got)
                print(jsn + "\n")
                out.write("[" + jsn + "],\n")
                gotURIs.append(it)
            except ValueError:

                print(request.text)
                print(request.headers)
                print("\n\n")
    session.close()


class Memento:
    def __init__(self, date):
        self.date = date


def prossTMArray(tmArr):
    ret = []
    for subArr in tmArr:
        print(subArr, type(subArr))
        if isinstance(subArr, list):
            print(subArr)
            return prossTMArray(subArr)
        else:
            return None


class TM:
    def __init__(self, tmar):
        self.tmar = tmar
        self.urlKey = None
        self.mementos = []
        self.numMentos = 0
        self.prosses()

    def getURIKey(self):
        return ''.join(reversed(self.urlKey))

    def timeSpan(self):
        d0 = self.mementos[0]
        dend = self.mementos[len(self.mementos) - 1]
        tdelta = dend - d0
        return tdelta.days

    def timeSpanAfter(self, year):
        after = list(filter(lambda x: x.year >= year, self.mementos))
        d0 = after[0]
        dend = after[len(after) - 1]
        tdelta = dend - d0
        return tdelta.days

    def numMementosAfter(self, year):
        print("Menentos after year ",year)
        print("its length is ",len(list(filter(lambda x: x.year >= year, self.mementos))))
        print("original its length is ",len( self.mementos))
        return len(list(filter(lambda x: x.year >= year, self.mementos)))

    def prosses(self):
        c = 0
        # print(self.tmar.pop(0))
        for item in self.tmar:
            item.pop(0)
            for i in item:
                c += 1
                # print(i)
                s = i[0]
                sstr = s.rstrip("/)")
                sstr = sstr.split(',')
                self.urlKey = sstr
                # print(sstr)
                if sstr is None:
                    print("BAAAADDDD", s)
                # 2001 12 16 00 47 59
                # 2013 15 10 37 51 00
                ds = i[1][0:8]
                try:
                    d = date(int(ds[0:4]), int(ds[4:6]), int(ds[6:8]))
                    self.mementos.append(d)
                    # print(d)
                except ValueError:
                    print("badd", ds, i[1], i[1][0:8], i)

        self.mementos = list(filter(lambda x: x is not None and x.year != 2016, self.mementos))
        self.mementos.sort()
        self.numMentos = len(self.mementos)

class cs:
        def __init__(self, row):
            self.site = row['site']
            self.alSum = row['alsum']
            self.random = row['random']
            self.temporal = row['temporal']
            self.aVr = row['aVrDif']
            self.aVt = row['aVtDiff']
            self.ctcRsim = None
            self.ctcTsim = None
            self.otoRsim = None
            self.otoTsim = None
            self.tmTimeSpan = None
            self.tmNumMementos = None
            self.tmTimeSpan2k = None
            self.tmNumM2k = None
            self.tmTimeSpan05k = None
            self.tmNumM05k = None
            self.won = {}

        def setTMInfo(self,timeSpan,numTM,timeSpan2k,num2k,timeSpan05,num05):
            self.tmTimeSpan = timeSpan
            self.tmNumMementos = numTM
            self.tmTimeSpan2k = timeSpan2k
            self.tmNumM2k = num2k
            self.tmTimeSpan05k = timeSpan05
            self.tmNumM05k = num05

        def getRString(self):
            return "%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%s,%s,%s,%s\n" % (
            self.site, self.alSum, self.random, self.aVr,
            self.tmNumMementos, self.tmTimeSpan,
            self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k,
            self.tmTimeSpan05k,self.won.get('r',' '),
            self.otoRsim,self.ctcRsim,"random")


        def getTString(self):
            return "%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%s,%s,%s,%s\n" % (
            self.site, self.alSum, self.temporal, self.aVt,
            self.tmNumMementos, self.tmTimeSpan,
            self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k,
            self.tmTimeSpan05k,self.won.get('ti',' '),
            self.otoTsim,self.ctcTsim,"temporal")

        def outString(self):
            # print(type(self.won['Random']),type(self.won['TemporalInterval']),type(self.tmTimeSpan05k))
            # site,alsum,random,aVrDif,temporal,aVtDiff
            # s1 = "%s,%s,%s,%s,%s,%s,"%(self.site, self.alSum, self.random, self.aVr, self.temporal, self.aVt)
            # s2 ="%d,%d,%d,%d,%d,%d,"%(self.tmNumMementos, self.tmTimeSpan,self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k,self.tmTimeSpan05k)
            # s3 = "%s,%s\n"%(self.won['Random'],self.won['TemporalInterval'])
            #roto,toto,ctcr,ctct
            return "%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%s,%s,%s,%s,%s,%s\n" % (
            self.site, self.alSum, self.random, self.aVr, self.temporal, self.aVt,
            self.tmNumMementos, self.tmTimeSpan,
            self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k,
            self.tmTimeSpan05k,self.won.get('r',' '),self.won.get('ti',' '),
            self.otoRsim,self.otoTsim,self.ctcRsim,self.ctcTsim)

        def __str__(self):
            return self.site

def gsite(cstr):
    return cstr[cstr.find("_")+1:cstr.rfind("_")]


def generate():
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    with open("tms2.json", "r") as tm:
        it = json.load(tm)

    goodUris = []
    with open("gooduris_20160225.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            goodUris.append(uri)

    color = {} # type: dict[str,cs]
    with open("temporalPairs.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            color[row['site']] = cs(row)


    with open("compositeToComposite.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            arsim = row['alsumRandomSim']
            atsim = row['alsumTemporalSim']
            color[row['site']].ctcRsim = arsim
            color[row['site']].ctcTsim = atsim

    with open("alSumVSrandom_onetoone.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            arsim = row['average']
            color[row['site']].otoRsim = arsim

    with open("alSumVStemporalInterval_onetoone.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            arsim = row['average']
            color[row['site']].otoTsim = arsim


    with open("wins.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            if color.get(row['site'],None) is not None:
                color[row['site']].won['r'] = row['awr']
                color[row['site']].won['ti'] = row['awt']



    tms = it['tms']
    timeMaps = {}  # type: dict[str,TM]

    for s in tms:
        it = TM(s)
        timeMaps[it.getURIKey()] = it

    tmk = list(filter(lambda x: len(x) > 2, timeMaps.keys()))


    compisits = get_files(compath, lambda f: "allTheSame" not in f and check_if_goodURI(f, goodUris) and
                                             "interval" not in f)


    print(compisits)

    uniqueComposite = set()
    for c in compisits:
       uniqueComposite.add(gsite(c))
    compisits = sorted(list(uniqueComposite))


    # 640 641

            # self.site, self.alSum, self.random, self.aVr, self.temporal, self.aVt,
            # self.tmNumMementos, self.tmTimeSpan,
            # self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k, self.tmTimeSpan05k
            # self.won['Random'],
            # self.won['TemporalInterval']
    with open("allTm2.csv","w+") as out:
        out.write("site,ah,mh,mdif,nmemento,timespan,nummtwo,twotimespan,numof,timespanof,aWP,moto,mtcr,method\n")
        for c in sorted(compisits):
            # print(c)
            for tmkey in filter(lambda x: len(x) > 2, tmk):
                if tmkey in c:
                    print(timeMaps[tmkey].timeSpan(), timeMaps[tmkey].numMentos,
                          timeMaps[tmkey].timeSpanAfter(2000), timeMaps[tmkey].numMementosAfter(2000),
                          timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMementosAfter(2005))
                    cc = color[tmkey]
                    cc.setTMInfo(timeMaps[tmkey].timeSpan(), timeMaps[tmkey].numMentos,
                          timeMaps[tmkey].timeSpanAfter(2000), timeMaps[tmkey].numMementosAfter(2000),
                          timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMementosAfter(2005))
                    out.write(cc.getRString())
                    out.write(cc.getTString())
                    print("______________________________")



def histNormalizeWhole(score):
    for low,high in zip( np.arange(0,1.0,0.1), np.arange(0.1,1.1,0.1)):
        if low <= score <= high:
            return low


def difToRange(dif):
    #-0.89892 0.417491
    for low,high in zip( np.arange(-0.9,0.0,0.1), np.arange(-0.8,0.1,0.1)):
        # print("%.1f < %.1f < %.1f"%(low,dif,high))
        if low < dif < high:
            if high == -0.0:
                print("We have a negative -0.0")
            return high
    return histNormalizeWhole(dif)


def get_nrange(item):
    if -0.09 < item <= -0.009:
        return "[-0.1_0.0]"

    if -0.1 < item <= -0.0:
        return "[-0.1_0.0]"
    if -0.9 < item <= -0.7:
        return "[-0.8_-0.7]"
    if -0.7 < item <= -0.6:
        return "[-0.6_-0.5]"

    if -0.6 < item <= -0.5:
        return "[-0.6_-0.5]"

    if -0.5 < item <= -0.4:
        return "[-0.4_-0.3]"
    if -0.4 < item <= -0.3:
        return "[-0.4_-0.3]"

    if -0.3 < item <= -0.2:
        return "[-0.2_-0.1]"

    if -0.8 == item == -0.7:
        return "[-0.8_-0.7]"
    if -0.6 <= item <= -0.5:
        return "[-0.6_-0.5]"
    if -0.4 == item == -0.3:
        return "[-0.4_-0.3]"
    if -0.2 <= item <= -0.1:
        return "[-0.2_-0.1]"
    if -0.0 < item < 0.0:
        return "[-0.1_0.0]"

def get_range(item):
    if 0.0 < item < 0.2:
        return "[0.0_0.1]"
    if 0.2 <= item < 0.4:
        return "[0.2-0.3]"
    if 0.4 <= item < 0.6:
        return "[0.4-0.5]"
    if 0.6 <= item < 0.8:
        return "[0.6-0.7]"
    if 0.8 <= item < 1.0:
        return "[0.8-0.9]"
    return '1.0'

class tmdata:
    def __init__(self,row):
        self.site = row['site']
        self.ah = float(row['ah'])
        self.mh = float(row['mh'])
        self.mdif = float(row['mdif'])
        self.nmemento = row['nmemento']
        self.timespan = row['timespan']
        self.nummtwo = row['nummtwo']
        self.twotimespan = row['twotimespan']
        self.numof = row['numof']
        self.timespanof = row['timespanof']
        self.aWP = float(row['aWP'])
        self.moto = float(row['moto'])
        self.mtcr = float(row['mtcr'])
        self.method = row['method']

    def get_out_string(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s\n"%(self.site,self.ah,self.mh,self.mdif,self.nmemento,self.timespan,self.aWP,self.method)


class clr:
    def __init__(self,dic):
        self.name = dic['name']
        self.rgb = dic['rgb']
        self.percent = float(dic['percent'])


    def __lt__(self, other):
        if isinstance(other, clr):
            return self.percent < other.percent
        if isinstance(other,float):
            return  self.percent < other

    def __le__(self, other):
        if isinstance(other, clr):
            return self.percent <= other.percent
        if isinstance(other,float):
            return  self.percent <= other

    def __gt__(self, other):
        if isinstance(other, clr):
            return self.percent > other.percent
        if isinstance(other,float):
            return  self.percent > other

    def __ge__(self, other):
        if isinstance(other, clr):
            return self.percent >= other.percent
        if isinstance(other,float):
            return  self.percent >= other

    def __str__(self):
        return "%s,%.2f"%(self.name,self.percent)

class cdate:
    def __init__(self,d,percents):
        (year,month,day) = d.split("-")
        self.d = date(int(year),int(month),int(day))
        self.colors = sorted(list(map(lambda x:clr(x), percents)))

    def min_max(self):
        return (min(self.colors),max(self.colors))

    def __lt__(self, other):
        return self.d < other.d
    def __le__(self, other):
        return self.d <= other.d
    def __gt__(self, other):
        return self.d > other.d
    def __ge__(self, other):
        return self.d >= other.d

    def __str__(self):
        out = ''
        for c in sorted(self.colors,reverse=True):
            out +="["+ c.__str__()+"] "
        return "%s,%s"%(self.d.isoformat(),out)

class colorComp:
    def __init__(self,site,cs):
        self.site = site
        self.cds = []
        self.comp = cs['comp']
        for d,cpercent in cs['color'].items():
            self.cds.append(cdate(d,cpercent))
        self.cds.sort()


def mementorange(item):
     if item <= 100:
         return "mementos <= 100"
     if 100 < item <= 400:
         return "100 < mementos <= 400"
     if 400 < item <= 1000:
         return "400 < mementos <= 1000"
     if item > 1000:
         return "mementos > 1000"
if __name__ == '__main__':
    tmds = []
    grouper = defaultdict(list)
    with open("allTm2.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            tdata = tmdata(row)
            tdata.ah = histNormalizeWhole(tdata.ah)
            # print(tdata.ah,get_range(tdata.ah))
            tdata.ah=get_range(tdata.ah)
            # tdata.mh = histNormalizeWhole(tdata.mh)
            # print(tdata.mh,get_range(tdata.mh))

            tdata.mh=get_range(tdata.mh)
            tdata.aWP = histNormalizeWhole(tdata.aWP)
            # print(tdata.aWP,get_range(tdata.aWP))
            tdata.aWP = get_range(tdata.aWP)
            # tdata.mdif = difToRange(tdata.mdif)
            if tdata.mdif == -0.0 or "%1.1f"%tdata.mdif == "-0.0":
                tdata.mdif = abs(0.0)
            print(tdata.mdif,get_range(tdata.mdif))
            tdata.mdif=get_nrange(tdata.mdif)

            print("____________________________")
            tmds.append(tdata)
            grouper[tdata.aWP].append(tdata)


    with open("analysis/allTm3.csv","w+") as out:
        out.write("site,ah,mh,mdif,nmemento,timespan,aWP,method\n")
        for it in sorted(tmds,key=lambda x:x.site):
            out.write(it.get_out_string())

    # with open("analysis/windifnmtspan.csv","w+") as out:
    #     out.write("winp,dif,nmemento,tspan,m\n")
    #     for winp, group in sorted(grouper.items(),key=lambda x:x[0]):
    #         print("at %.1f we have %d items"%(winp,len(group)))
    #         difGroup = defaultdict(list)
    #         for g in group:
    #             difGroup[g.mdif].append(g)
    #         for dif,g in sorted(difGroup.items(),key=lambda x:x[0]):
    #             print("%1.1f"%dif)
    #             for it in g:
    #                 print(it.nmemento,it.timespan)
    #                 out.write("%.1f,%.1f,%s,%s,%s\n"%(winp,dif,it.nmemento,it.timespan,it.method))
    #
    #
    # with open("analysis/windifmcount.csv","w+") as out:
    #     out.write("winp,dif,mcount\n")
    #     for winp, group in sorted(grouper.items(),key=lambda x:x[0]):
    #         print("at %.1f we have %d items"%(winp,len(group)))
    #         difGroup = defaultdict(list)
    #         for g in group:
    #             difGroup[g.mdif].append(g)
    #         for dif,g in sorted(difGroup.items(),key=lambda x:x[0]):
    #             print("%1.1f"%dif)
    #             mgrouper = Counter()
    #             for it in g:
    #                 mgrouper[it.method] += 1
    #             for k,v in mgrouper.items():
    #                 out.write("%.1f,%.1f,%s,%d\n"%(winp,dif,k,v))





    # with open("colorResults.json","r") as o:
    #     colorResults = json.load(o)
    # mcolors = defaultdict(dict)
    # for method, results in colorResults.items():
    #     # print(method)
    #     for site, comp in results.items():
    #         # print(site,comp)
    #         mcolors[method][site]=colorComp(site,comp)
    #
    # for ((asite,acompt),(rsite,rcompt)),(tsite,tcompt) in \
    #             zip(zip(sorted(mcolors['alSum'].items(),key=lambda x:x[0]),sorted(mcolors['random'].items(),key=lambda x:x[0]))
    #                 ,sorted(mcolors['temporalInterval'].items(),key=lambda x:x[0])):
    #     # print(am,rm,tim)
    #     print(asite,acompt.comp)
    #     for ((a,r),t) in zip(zip(acompt.cds,rcompt.cds),tcompt.cds):
    #         print(a,r,t)
    #     # for site,cr in sites.items():
        #     print(site)
        #     for cds in cr.cds:
        #         print(cds)


            # for colors in comp.items():
            #     print(colors)
    # tmds = sorted(tmds,key=lambda x:x.mdif)
    # print(min(tmds,key=lambda x:x.mdif).mdif,max(tmds,key=lambda x:x.mdif).mdif)
    # print(-0.9 < -0.89892 < -0.8)
#
#
#
#     # only com
#     with open("onlyComTm2.csv","w+") as out:
#         out.write("site,ah,mh,mdif,nmemento,timespan,nummtwo,twotimespan,numof,timespanof,aWP,moto,mtcr,method\n")
#         for c in sorted(compisits):
#             # print(c)
#             for tmkey in filter(lambda x: len(x) > 2 and "com" in x, tmk):
#                 if tmkey in c:
#                     print( timeMaps[tmkey].timeSpan(), timeMaps[tmkey].timeSpanAfter(2000),
#                           timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMentos)
#                     cc = color[tmkey]
#                     cc.setTMInfo(timeMaps[tmkey].timeSpan(), timeMaps[tmkey].numMentos,
#                           timeMaps[tmkey].timeSpanAfter(2000), timeMaps[tmkey].numMementosAfter(2000),
#                           timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMementosAfter(2005))
#                     out.write(cc.getRString())
#                     out.write(cc.getTString())
#                     print("______________________________")
#
#     # no com
#     with open("noComTm2.csv","w+") as out:
#         out.write("site,ah,mh,mdif,nmemento,timespan,nummtwo,twotimespan,numof,timespanof,aWP,moto,mtcr,method\n")
#         for c in sorted(compisits):
#             # print(c)
#             for tmkey in filter(lambda x: len(x) > 2 and "com" not in x, tmk):
#                 if tmkey in c:
#                     print(timeMaps[tmkey].timeSpan(), timeMaps[tmkey].timeSpanAfter(2000),
#                           timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMementosAfter(2005))
#
#                     cc = color[tmkey]
#                     cc.setTMInfo(timeMaps[tmkey].timeSpan(), timeMaps[tmkey].numMentos,
#                           timeMaps[tmkey].timeSpanAfter(2000), timeMaps[tmkey].numMementosAfter(2000),
#                           timeMaps[tmkey].timeSpanAfter(2005), timeMaps[tmkey].numMementosAfter(2005))
#                     out.write(cc.getRString())
#                     out.write(cc.getTString())
#                     print("______________________________")
#
#
#
#                 # for guri in goodUris:
#                 #     if guri in timeMaps.keys():
#                 #         print(goodUris)
#
# print("__________________________________")
# if isinstance(s,list):
#
#  prossTMArray(s)
#  break


# if len(self.urlKey) == 3:
#     return '%s%s%s'%(self.urlKey[2],self.urlKey[1],self.urlKey[0])
# if len(self.urlKey) == 2:
#     return '%s%s'%(self.urlKey[1],self.urlKey[0])

# def prosses(self):
#     c = 0
#     for item in self.tmar:
#         print(item)
#         for i in item:
#             c+=1
#             # print(i)
#             sstr = i[0]
#             # print(sstr)
#             sstr = sstr.rstrip("/)")
#             sstr = sstr.split(',')
#             self.urlKey = sstr
#             ds = i[1][0:8]
#             print(i[0])
#             try:
#                 d = date(int(ds[0:4]), int(ds[4:6]), int(ds[6:8]))
#                 self.mementos.append(d)
#                 # print(d)
#             except ValueError:
#                 print("badd")
#
#     self.mementos.sort()
#     self.numMentos = c


#     for i in item:
#         print(i)
#         c += 1
#         sstr = i[0]
#         sstr = sstr.rstrip("/)")
#         sstr = sstr.split(',')
#         print(sstr)
#         if len(sstr) > 2:
#             site = sstr[2]
#             dotwhat = sstr[1]
#         else:
#             site = sstr[1]
#             dotwhat = sstr[0]
#         # 2001 12 16 00 47 59
#         # 2013 15 10 37 51 00
#         print(i[1][0:8],len(i[1][0:8]))
#         ds = i[1][0:8]
#         print(ds[0:4],ds[4:6],ds[6:8])
#         d = date(int(ds[0:4]),int(ds[4:6]),int(ds[6:8]))
#         print(d)
# for s in tms:
#     print(len(s))
#     it = TM(s)
#     timeMaps.append(TM(s))
#
# goodUris = []
# with open("gooduris_20160225.txt", "r") as read:
#     for uri in map(lambda line: line.rstrip("\n"), read):
#         goodUris.append(uri)
