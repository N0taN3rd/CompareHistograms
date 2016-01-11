import json
from collections import defaultdict
from datetime import datetime
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import cv2
import os
import random

def getColor(num=None):
    if num is not None:
        colors = []
        for i in range(num):
            colors.append("#%06x" % random.randint(0, 0xFFFFFF))
        return colors
    else:
        return "#%06x" % random.randint(0, 0xFFFFFF)


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

    return imname[begin_index:end_index]


def getdate(imname: str):
    """
        :returns : datetime
    """
    lhttp = imname.rfind("http")
    lastweb = imname.rfind("web", 0, lhttp)
    convert_time = None
    try:
        convert_time = datetime.strptime(imname[lastweb + 3:lhttp], "%Y%m%d%H%M%S")
    except:
        print(imname)
    return convert_time


def get3dhisto(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [8, 8, 8],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist).flatten()


def getsplithisto(cvim):
    bgrhist = {}
    chans = cv2.split(cvim)
    colors = ("b", "g", "r")
    for chan, color in zip(chans, colors):
        bgrhist[color] = cv2.calcHist([chan], [0], None, [256], [0, 256])
    return bgrhist


def gethsvhisto(cvim):
    hsv = cv2.cvtColor(cvim, cv2.COLOR_BGR2HSV)
    return cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])


def get_files(path, test=None):
    if test is None:
        print("None", " ", path)
        for f in listdir(path):
            if isfile(join(path, f)):
                yield f
    else:
        for f in listdir(path):
            if isfile(join(path, f)) and test(f):
                yield f


class HistCompRet:
    def __init__(self, mname, base):
        self.mname = mname
        self.base = getsite(base)
        self.base_date = getdate(base).date().isoformat()
        self.results = [] #defaultdict(list)
        self.hist_type = None

    def __getitem__(self, site):
        return self.results[site]

    def dic_json(self):
        out = dict()
        out["histogramcomp"] = self.results
        return out

    def labels(self,points):
        labels = []
        for p in points:
            labels.append(str('%.5f'%p))
        return labels

    def plot(self, composite=None):
        width = 0.35
        fig = plt.figure()
        fig.subplots_adjust(bottom=0.18)
        ax = fig.add_subplot(111)
        ind = np.arange(len(self.results))
        bottomLables = []
        plotpoints = []
        for ret in self.results:
            bottomLables.append(ret[0])
            plotpoints.append(ret[1])

        barcolors = getColor(num=len(self.results))
        tlables = self.labels(plotpoints)
        bars = ax.bar(ind+width,plotpoints, color=barcolors)
        ax.set_xlim(-width, len(ind)+width)
        ax.set_ylim(0, 2)
        plt.ylabel('Correlation Similarity Scores')

        if composite is not None:
            ax.set_title(composite+"\nbase image date: "+self.base_date)
        else:
            ax.set_title(self.base+':'+self.base_date)

        ax.set_xticks(ind+width)
        plt.setp(ax.set_xticklabels(bottomLables), rotation=45, fontsize=10)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
        #   ncol=3, fancybox=True)
        ax.legend(bars,tlables,fontsize='small',loc='center left', bbox_to_anchor=(1, 0.5))
        return fig




    def add_ret(self, im, ret):
        self.results.append((im,ret))
        #self.results[im].append(ret)

    def print(self):
        print(self.mname)
        print(self.base + ":" + self.base_date)
        print(self.hist_type)
        for k in self.results:
            print(k)
        print(self.to_json())

    def to_json(self):
        return json.dumps(self, default=lambda c: c.__dict__, sort_keys=False, indent=2)


class Image:
    def __init__(self, image):
        self.image = image  # type: str
        self.site = getsite(image)  # type: str
        self.date = getdate(image).date().isoformat()  # type: str
        self.id = self.site + ":" + self.date
        self.hists = {}  # type: dict
        self.hist_ret = {}  # type: dict[str,HistCompRet]
        self.mat = None

    def __str__(self):
        return self.image

    def dic_json(self):
        out = dict()
        out["datetime"] = self.date
        out["results"] = self.hist_ret["Correlation"]
        return out

    def cv_read(self, path):
        self.mat = cv2.imread(path + self.image)
        self.hists["3d"] = get3dhisto(self.mat)
        #self.hists["hsv"] = gethsvhisto(self.mat)

    def site_date(self):
        return self.id

    def clean(self):
        del self.mat
        del self.hists

    def compare_hist(self, other: set, meths):
        (mname, m) = meths
        # for mname, m in meths:
        histret = HistCompRet(mname, self.image)
        for oim in other:
            histret.add_ret(oim.date, cv2.compareHist(self.hists["3d"], oim.hists["3d"], m))
           #histret.add_ret(oim.date, cv2.compareHist(self.hists["hsv"], oim.hists["hsv"], m))
        histret.hist_type = "3d"
        self.hist_ret[mname] = histret

    def plot(self, composite=None):
        if composite is not None:
            return self.hist_ret["Correlation"].plot(composite=composite)
        else:
            return self.hist_ret["Correlation"].plot()


def compare_self(self, meths):
    for mname, m in meths:
        histret = self.hist_ret[mname]
        histret.add_ret((self.site_date(), self.site_date()),
                        ("3d", cv2.compareHist(self.hists["3d"], self.hists["3d"], m)))


def to_json(self):
    rets = []
    for _, v in self.hist_ret.items():
        rets.append(v.to_json())
    return json.dumps(rets, sort_keys=False, indent=2)


class ImageGroup:
    def __init__(self, path, site):
        self.path = path
        self.site = site
        self.images = []  # type: list[Image]
        self.hist_comp = ("Correlation", cv2.HISTCMP_CORREL)
        # ("BHATTACHARYYA", cv2.HISTCMP_BHATTACHARYYA))
        self.composite = None

    def __str__(self):
        return self.site

    def __getitem__(self, index):
        return self.images[index]

    def __len__(self):
        return len(self.images)

    def dic_json(self):
        out = dict()  # type: dict
        if self.composite is not None:
            out["site_composite"] = self.composite
        out["site_images"] = self.images
        return out

    def add_im(self, im):
        self.images.append(im)

    def valid_for_comp(self):
        return len(self.images) >= 2

    def has_composite(self):
        return self.composite is not None

    def sort(self, key):
        self.images.sort(key=key)

    def group_cvread(self):
        for im in self.images:
            im.cv_read(self.path)

    def compare_hists(self):
        imset = set(self.images)
        for im in self.images:
            singlton = set()
            singlton.add(im)
            others = imset - singlton
            im.compare_hist(others, self.hist_comp)

    def plot(self):
        fname = self.composite[0:self.composite.index('.png')]+'_color.pdf' if self.composite is not None else \
            self.site+"_color.pdf"
        savedir = os.getcwd()+"/plots/"+fname

        pdf = PdfPages(savedir)
        for im in self.images:
            if self.composite is not None:
                fig = im.plot(composite=self.composite)
            else:
                fig = im.plot()
            pdf.savefig(fig)
            plt.close(fig)
        pdf.close()

    def clean_up(self):
        for im in self.images:
            im.clean()

    def to_json(self):
        return json.dumps(self, default=lambda c: c.dic_json(), sort_keys=False, indent=4)


class MethodIms:
    def __init__(self, method, path, composites):
        self.imageGroups = {}  # type: dict[str,ImageGroup]
        self.methodName = method  # type: str
        self.path = path  # type: str
        self.totalSize = 0
        self.composites = composites  # type: dict[str,str]
        self.imageGroupsCalulated = {}  # type: dict[str,ImageGroup]

    def __getitem__(self, site):
        return self.imageGroups[site]

    def __str__(self):
        return self.methodName

    def dic_json(self):
        """
        :rtype: dict
        :return: dictionary of items to be serialized to json
        """
        out = dict()
        out["imageGroups"] = self.imageGroupsCalulated
        return out

    def sites(self):
        return self.imageGroups.keys()

    def composite_to_im(self, composites, igroup, site):
        if "_200" not in site:
            try:
                igroup.composite = self.composites[site]
            except KeyError:
                pass

    def add_image(self, image):
        site = getsite(image)
        try:
            self.imageGroups[site]
        except KeyError:
            igroup = ImageGroup(self.path, site)
            self.composite_to_im(self.composites, igroup, site)
            self.imageGroups[site] = igroup

        self.totalSize += 1
        self.imageGroups[site].add_im(Image(image))

    def calc_all_hists(self):
        for site, img in self.imageGroups.items():
            if img.valid_for_comp():
                img.group_cvread()
                img.compare_hists()
                img.clean_up()

    def calc_comp_hists(self):
        for site, img in self.imageGroups.items():
            if img.valid_for_comp() and img.has_composite():
                img.group_cvread()
                img.compare_hists()
                img.clean_up()
                self.imageGroupsCalulated[site] = img
        print(self.methodName, len(self.imageGroupsCalulated))

    def plot(self):
        for _, v in self.imageGroupsCalulated.items():
            v.plot()

    def to_json(self):
        return json.dumps(self, default=lambda c: c.dic_json(), sort_keys=False, indent=2)


class AllMethods:
    def __init__(self, impath, compath):
        self.impath = impath
        self.compath = compath
        self.files = None
        self.compisits = None
        self.method_composites = defaultdict(dict)
        self.methods = None  # type: dict[str,MethodIms]

    def __getitem__(self, site):
        return self.methods[site]

    def dic_json(self):
        """
        :rtype: dict
        :return: dictionary of items to be serialized to json
        """
        out = dict()
        out["methods"] = self.methods
        return out

    def pull_images(self):
        print("pulling images")
        self.files = get_files(self.impath, test=None)
        self.compisits = get_files(self.compath, lambda f: "allTheSame" not in f)
        for comp in self.compisits:
            site = comp[comp.find("_") + 1:comp.rfind("_")]
            if len(site) != 3:
                self.method_composites[comp[:comp.index("_")]][site] = comp
        self.impath += "/"
        self.methods = {'random': MethodIms('random', self.impath, self.method_composites["random"]),
                        'temporalInterval': MethodIms('temporalInterval', self.impath,
                                                      self.method_composites["temporalInterval"]),
                        'alSum': MethodIms('alSum', self.impath, self.method_composites["alSum"]),
                        'interval': MethodIms('interval', self.impath, self.method_composites["interval"])}

        for item in self.files:
            index = item.index('_')
            m = item[0:index]
            self.methods.get(m).add_image(item)

    def calc_all_hists(self):
        for _, method in self.methods.items():
            method.calc_all_hists()

    def calc_comp_hists(self):
        for mn, method in self.methods.items():
            print("calculating histogram and comparing them for method %s" % mn)
            method.calc_comp_hists()

    def to_json(self):
        print("converting results to json")
        return json.dumps(self, default=lambda c: c.dic_json(), sort_keys=False, indent=1)

    def plot(self):
        for m, method in self.methods.items():
            print("plotting %s"%m)
            method.calc_comp_hists()
            method.plot()
