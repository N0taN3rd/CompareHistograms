import json
import re

import requests

tokenizer = re.compile('(<[^>]+>|[a-zA-Z]+="[^"]*"|[;,])\\s*')

from util import get_files, check_if_goodURI

from datetime import date
import csv

from collections import defaultdict


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
            self.tmTimeSpan05k,self.won.get('Random',' '),
            self.otoRsim,self.ctcRsim,"random")


        def getTString(self):
            return "%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%s,%s,%s,%s\n" % (
            self.site, self.alSum, self.temporal, self.aVt,
            self.tmNumMementos, self.tmTimeSpan,
            self.tmNumM2k, self.tmTimeSpan2k, self.tmNumM05k,
            self.tmTimeSpan05k,self.won.get('TemporalInterval',' '),
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
            self.tmTimeSpan05k,self.won.get('Random',' '),self.won.get('TemporalInterval',' '),
            self.otoRsim,self.otoTsim,self.ctcRsim,self.ctcTsim)

        def __str__(self):
            return self.site



def gsite(cstr):
    return cstr[cstr.find("_")+1:cstr.rfind("_")]

if __name__ == '__main__':
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


    with open("tileDifRedo.csv","r") as read:
        reader = csv.DictReader(read)
        for row in reader:
            awon = int(row['awon'])
            mwon = int(row['mwom'])
            m = row['method']
            color[row['site']].won[m] = str(round(awon/(awon+mwon),2))



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
