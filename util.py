import random
from datetime import datetime
from os import listdir
from os.path import isfile, join
from collections import defaultdict
import cv2
import matplotlib.pyplot as plt
import numpy as np




def getsite(imname):
    end_index = imname.rfind(".png")
    hpslen = len("https")
    hpswlen = len("httpswww")
    hplen = len("http")
    hpwlen = len("httpwww")

    begin_index = imname.rfind("httpswww")

    if begin_index != -1:
        begin_index += hpswlen
    else:
        begin_index = imname.rfind("https")
        if begin_index != -1:
            begin_index += hpslen
        else:
            begin_index = imname.rfind("httpwww")
            if begin_index != -1:
                begin_index += hpwlen
            else:
                begin_index = imname.rfind("http")
                if begin_index != -1:
                    begin_index += hplen
    # print("orignal %s"%imname,"processed %s\n"%imname[begin_index:end_index])
    return imname[begin_index:end_index]


def getdate(imname: str):
    """
        :returns : str
    """
    lhttp = imname.rfind("http")
    lastweb = imname.rfind("web", 0, lhttp)
    convert_time = None
    try:
        convert_time = datetime.strptime(imname[lastweb + 3:lhttp], "%Y%m%d%H%M%S")
    except:
        print(imname)
    return convert_time


def getdatetime(imname):
    """
        :returns : datetime
    """
    lhttp = imname.rfind("http")
    lastweb = imname.rfind("web", 0, lhttp)
    return datetime.strptime(imname[lastweb + 3:lhttp], "%Y%m%d%H%M%S")


def getMethod(compstr):
    return compstr[:compstr.find("_")]


def getComp(compstring: str):
    comp = compstring[compstring.rfind("/") + 1:]
    return comp


def check_if_goodURI(file,filterList):
    for item in filterList:
        if item in file and "_200" not in file:
            return True
    return False

def check_if_hasComposite(file,composites):
    index = file.index('_')
    m = file[0:index]
    for c in composites[m].keys():
        if c in file:
            return True
    return False

def get_files(path, test=None):
    files = []
    if test is None:
        for f in listdir(path):
            if isfile(join(path, f)):
                files.append(f)
    else:
        for f in listdir(path):
            if isfile(join(path, f)) and test(f):
                files.append(f)
    return files


class MappedComp:
    def __init__(self,site,composite):
        self.site = site
        self.composite = composite
        self.imList = []

    def add_im(self,im):
        self.imList.append(im)

    def __str__(self):
        return "%s, %s, num images %d\n"%(self.site,self.composite,len(self.imList))


def get_and_process_thumbs(path,cdict,filterList):
    files = defaultdict(dict) # type: defaultdict(dict)
    for f in listdir(path):
        if isfile(join(path,f)) and check_if_goodURI(f,filterList) and "interval" not in f:
            index = f.index('_')
            m = f[0:index]
            for c,cs in cdict[m].items():
                if c in f:
                    try:
                        files[m][c]
                    except KeyError:
                        files[m][c] = MappedComp(c,cs)
                    files[m][c].add_im(f)
    return files


def getColor(num=None):
    if num is not None:
        colors = []
        for i in range(num):
            colors.append("#%06x" % random.randint(0, 0xFFFFFF))
        return colors
    else:
        return "#%06x" % random.randint(0, 0xFFFFFF)


def plot_dates_histRet(histCompRet, composite=None, levelString=None):
    width = 0.35
    compi = plt.imread("/home/john/wsdlims_ripped/ECIR2016TurkData/composites/" + composite)
    # fig, axs = plt.subplots(2, sharey=True)
    # fig.set_size_inches(15, 15, forward=True)
    # axs[0].imshow(compi,shape=compi.shape,aspect='equal')
    fig, axs = plt.subplots(2)
    fig.set_size_inches(15, 15, forward=True)
    axs[0].imshow(compi, aspect='equal')
    axs[0].set_xticks([])
    axs[0].set_yticks([])

    # fig.subplots_adjust(bottom=0.33, right=0.68)
    # ax = fig.add_subplot(111)
    # ax.imshow(mpimg.imread("/home/john/wsdlims_ripped/ECIR2016TurkData/composites/" +self.b))
    #
    ind = np.arange(len(histCompRet.results))
    bottomLables = []
    plotpoints = []
    side = []
    total = 0.0
    for ret in histCompRet.results:
        bottomLables.append(ret[0][0] + ":" + ret[0][1])
        plotpoints.append(ret[1])
        side.append(ret)
        total += ret[1]

    barcolors = getColor(num=len(histCompRet.results))
    tlables = histCompRet.labels2(side)
    # bars = plt.bar(ind, plotpoints,width, color=barcolors)

    bars = axs[1].bar(ind, plotpoints, width, color=barcolors)
    #
    axs[1].set_xlim(-width, len(ind) + width)
    axs[1].set_ylim(0, 1)
    plt.ylabel('Correlation Similarity Scores')
    #
    if composite is not None:
        if levelString is not None:
            axs[1].set_title(composite + "\n" + levelString + "\n")
        else:
            axs[1].set_title(composite)
    else:
        axs[1].set_title(histCompRet.b)
    #
    axs[1].set_xticks([])
    # plt.setp(axs[0].set_xticklabels(bottomLables), rotation=90, fontsize=10)

    box = axs[1].get_position()
    axs[1].set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
    # #   ncol=3, fancybox=True)
    axs[1].legend(bars, tlables, fontsize='x-small', loc='center left', bbox_to_anchor=(1, 0.5))

    return fig


def plot_histComp(histCompRef, composite=None):
    width = 0.35
    fig = plt.figure()
    fig.subplots_adjust(bottom=0.18)
    ax = fig.add_subplot(111)
    ind = np.arange(len(histCompRef.results))
    bottomLables = []
    plotpoints = []
    for ret in histCompRef.results:
        bottomLables.append(ret[0])
        plotpoints.append(ret[1])

    barcolors = getColor(num=len(histCompRef.results))
    tlables = histCompRef.labels(plotpoints)
    bars = ax.bar(ind + width, plotpoints, color=barcolors)
    ax.set_xlim(-width, len(ind) + width)
    ax.set_ylim(0, 2)
    plt.ylabel('Correlation Similarity Scores')

    if composite is not None:
        ax.set_title(composite)  # + "\nbase image date: " + self.base_date)
    else:
        ax.set_title(histCompRef.base + ':' + histCompRef.base_date)

    ax.set_xticks(ind + width)
    plt.setp(ax.set_xticklabels(bottomLables), rotation=45, fontsize=10)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
    #   ncol=3, fancybox=True)
    ax.legend(bars, tlables, fontsize='small', loc='center left', bbox_to_anchor=(1, 0.5))
    return fig
