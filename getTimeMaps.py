import json
import re
import urllib.request

import dateutil.parser
import requests

tokenizer = re.compile('(<[^>]+>|[a-zA-Z]+="[^"]*"|[;,])\\s*')

from util import get_files, check_if_goodURI,get_and_process_thumbs

from datetime import datetime, date



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
    def __init__(self,date):
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

    def prosses(self):
        c = 0
        # print(self.tmar.pop(0))
        for item in self.tmar:
            print(item.pop(0))
            for i in item:
                c+=1
                # print(i)
                s = i[0]
                sstr = s.rstrip("/)")
                sstr = sstr.split(',')
                self.urlKey = sstr
                # print(sstr)
                if sstr is None:
                    print("BAAAADDDD",s)
                # 2001 12 16 00 47 59
                # 2013 15 10 37 51 00


                ds = i[1][0:8]

                try:
                    d = date(int(ds[0:4]), int(ds[4:6]), int(ds[6:8]))
                    self.mementos.append(d)
                    # print(d)
                except ValueError:
                    print("badd",ds)

        self.mementos.sort()
        self.numMentos = c


if __name__ == '__main__':
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    with open("tms2.json", "r") as tm:
        it = json.load(tm)

    goodUris = []
    with open("gooduris_20160225.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            goodUris.append(uri)
    tms = it['tms']
    timeMaps = {}

    for s in tms:
        it = TM(s)
        timeMaps[it.getURIKey()] = it

    print(timeMaps.keys())
    tmk = list(filter(lambda x: len(x) > 2,timeMaps.keys()))

    for guri in sorted(goodUris):
        if guri in tmk:
            print(guri)

    compisits = get_files(compath, lambda f: "allTheSame" not in f and check_if_goodURI(f, goodUris) and
                                             "interval" not in f)
    # 640 641

    for c in compisits:
        # print(c)
        for tmkey in filter(lambda x: len(x) > 2,tmk):
            if tmkey in c:
                print(c,tmkey)



    # for guri in goodUris:
    #     if guri in timeMaps.keys():
    #         print(goodUris)




print("__________________________________")
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