import json
import os
import random
from collections import defaultdict
from datetime import datetime
from os import listdir
from os.path import isfile, join

import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


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


def getdatetime(imname):
    lhttp = imname.rfind("http")
    lastweb = imname.rfind("web", 0, lhttp)
    return datetime.strptime(imname[lastweb + 3:lhttp], "%Y%m%d%H%M%S")


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


def plot3(path, site):
    img = cv2.imread(path + site, cv2.IMREAD_COLOR)
    color = ('b', 'g', 'r')
    for i, col in enumerate(color):
        histr = cv2.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(histr, color=col)
        plt.xlim([0, 256])

    img = cv2.imread(path + site, cv2.IMREAD_UNCHANGED)
    chans = cv2.split(img)
    colors = ("b", "g", "r")
    plt.figure()
    plt.title("'Flattened' Color Histogram")
    plt.xlabel("Bins")
    plt.ylabel("# of Pixels")
    features = []

    # loop over the image channels
    for (chan, color) in zip(chans, colors):
        # create a histogram for the current channel and
        # concatenate the resulting histograms for each
        # channel
        hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
        features.extend(hist)

        # plot the histogram
        plt.plot(hist, color=color)
        plt.xlim([0, 256])
    plt.show()


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
        self.b = base
        self.base = getsite(base)
        if "composite" not in base:
            self.base_date = getdatetime(base).date().isoformat()
        self.results = []  # defaultdict(list)
        self.hist_type = None

    def __getitem__(self, site):
        return self.results[site]

    def dic_json(self):
        out = dict()
        out["histogramcomp"] = self.results
        return out

    def labels(self, points):
        labels = []
        for p in points:
            labels.append(str('%.5f' % p))
        return labels

    def labels2(self, points):
        labels = []
        count = 0
        length = len(points)
        for p in points:
            if count < length - 1:
                labels.append(str('%.5f' % p[1])+" "+p[0][0]+":"+p[0][1])
            else:
                labels.append(str('%.5f' % p[1])+" "+p[0])
            count += 1
        return labels

    def plot_dates(self, composite=None):
        width = 0.35
        compi = plt.imread("/home/john/wsdlims_ripped/ECIR2016TurkData/composites/"+composite)

        fig = plt.figure()

        fig.subplots_adjust(bottom=0.33, right=0.68)
        ax = fig.add_subplot(111)
        # ax.imshow(mpimg.imread("/home/john/wsdlims_ripped/ECIR2016TurkData/composites/" +self.b))
        #
        ind = np.arange(len(self.results))
        bottomLables = []
        plotpoints = []
        side = []
        total = 0.0
        for ret in self.results:
            bottomLables.append(ret[0][0] + ":" + ret[0][1])
            plotpoints.append(ret[1])
            side.append(ret)
            total += ret[1]

        barcolors = getColor(num=len(self.results))
        tlables = self.labels2(side)
        # bars = plt.bar(ind, plotpoints,width, color=barcolors)

        bars = ax.bar(ind, plotpoints,width, color=barcolors)
        #
        ax.set_xlim(-width, len(ind) + width)
        ax.set_ylim(0, 1.2)
        plt.ylabel('Correlation Similarity Scores')
        #
        if composite is not None:
            ax.set_title(composite)
        else:
            ax.set_title(self.b)
        #
        ax.set_xticks(ind + width)
        plt.setp(ax.set_xticklabels(bottomLables), rotation=90, fontsize=10)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
        # #   ncol=3, fancybox=True)
        ax.legend(bars, tlables, fontsize='x-small', loc='center left', bbox_to_anchor=(1, 0.5))
        imax = fig.add_subplot(222)
        imax.imshow(compi, aspect='auto')
        plt.axis('off')
        return fig

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
        bars = ax.bar(ind + width, plotpoints, color=barcolors)
        ax.set_xlim(-width, len(ind) + width)
        ax.set_ylim(0, 2)
        plt.ylabel('Correlation Similarity Scores')

        if composite is not None:
            ax.set_title(composite + "\nbase image date: " + self.base_date)
        else:
            ax.set_title(self.base + ':' + self.base_date)

        ax.set_xticks(ind + width)
        plt.setp(ax.set_xticklabels(bottomLables), rotation=45, fontsize=10)

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
        #   ncol=3, fancybox=True)
        ax.legend(bars, tlables, fontsize='small', loc='center left', bbox_to_anchor=(1, 0.5))
        return fig

    def add_ret(self, im, ret):
        self.results.append((im, ret))
        # self.results[im].append(ret)

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
        self.date_dt = getdatetime(image)  # type: datetime
        self.date = self.date_dt.date().isoformat()  # type: str
        self.id = self.site + ":" + self.date
        self.hists = {}  # type: dict
        self.hist_ret = {}  # type: dict[str,HistCompRet]
        self.mat = None  # type: np.ndarray
        self.path = None

    def __str__(self):
        return self.image

    def dic_json(self):
        out = dict()
        out["datetime"] = self.date
        out["results"] = self.hist_ret["Correlation"]
        return out

    def show(self):
        imm = mpimg.imread(self.path + self.image)
        image = plt.imshow(imm)
        plt.title(self.image)
        plt.show()

    def cv_read(self, path):
        self.path = path
        self.mat = cv2.imread(path + self.image, cv2.IMREAD_COLOR)
        self.hists["3d"] = get3dhisto(self.mat)
        # self.hists["hsv"] = gethsvhisto(self.mat)

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
            # histret.add_ret(oim.date, cv2.compareHist(self.hists["hsv"], oim.hists["hsv"], m))
        histret.hist_type = "3d"
        self.hist_ret[mname] = histret

    def compare_self(self):
        return cv2.compareHist(self.hists["3d"], self.hists["3d"], cv2.HISTCMP_CORREL)

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
        self.composite = None  # type: str
        self.average = None  # type: float
        self.date_results = None  # type: HistCompRet

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

    def compare_hists_dates(self, path=None, p=None, out=None):
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)

        self.date_results = HistCompRet("Correlation", self.composite)
        totalSum = 0.0
        c = 0
        for i in rang:
            if i + 1 < length:
                ret = cv2.compareHist(self.images[i].hists["3d"], self.images[i + 1].hists["3d"],
                                      cv2.HISTCMP_CORREL)

                im1 = plt.imread(path+self.images[i].image)
                im2 = plt.imread(path+self.images[i+1].image)

                # fig,ax = plt.subplots(im2.shape[0]*2,im2.shape[1]*2,sharey=True)
                fig,axs = plt.subplots(2,sharey=True)
                fig.set_size_inches(10,10,forward=True)
                axs[0].imshow(im1,aspect='auto')
                axs[0].set_title(self.images[i].site_date())
                axs[0].set_xticks([])
                axs[0].set_yticks([])
                plt.axis('off')
                axs[1].imshow(im2,aspect='auto')
                axs[1].set_xticks([])
                axs[1].set_yticks([])
                axs[1].set_title(self.images[i+1].site_date())

                plt.figtext(x=fig.get_figwidth()/2,y=0,s="score=%f"%ret)
                # axs[i].set_subtitle()
                plt.axis('off')
                plt.show()


                # ax = fig.add_subplot(1,3,1)
                # ax.imshow(im1,aspect='auto')
                # plt.axis('off')
                # ax2 = fig.add_subplot(1,3,2)
                # ax2.imshow(im2,aspect='auto')
                # plt.axis('off')
                # plt.show()
                totalSum += ret
                c += 1
                if path is not None:
                    out.write(path+self.images[i].image+", "+path+self.images[i+1].image+" %f"%ret+"\n")

                self.date_results.add_ret((self.images[i].date, self.images[i + 1].date),
                                          ret)
            # else:
                # print("last ", self.images[i].site_date())


        # print(type(totalSum))
        # print(totalSum, totalSum / length)
        self.average = totalSum / c

        if p is not None:
            out.write(p+"/"+self.composite+" %f"%self.average+"\n")
            out.write("\n")
        self.date_results.add_ret("Average", self.average)

    def plot(self):
        if self.date_results is None:
            fname = self.composite[0:self.composite.index('.png')] + '_color.pdf' if self.composite is not None else \
                self.site + "_color.pdf"
            savedir = os.getcwd() + "/plots/" + fname

            pdf = PdfPages(savedir)
            for im in self.images:
                if self.composite is not None:
                    fig = im.plot(composite=self.composite)
                else:
                    fig = im.plot()
                pdf.savefig(fig)
                plt.close(fig)
            pdf.close()

    def show(self):
        shows = []
        self.compare_hists_dates()



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

    def __contains__(self, item: str):
        try:
            self.imageGroups[item]
        except KeyError:
            return False
        return True

    def has_site(self, site):
        try:
            self.imageGroups[site]
        except KeyError:
            return False
        return True

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

    def calc_comp_hist_date(self,path=None, p=None, out=None):
        for site, img in self.imageGroups.items():
            if img.valid_for_comp() and img.has_composite():
                img.group_cvread()
                img.compare_hists_dates(path,p,out)
                img.clean_up()
                self.imageGroupsCalulated[site] = img

    # fname = "/home/john/PycharmProjects/CompareHistograms/plots/methodDates/%s.pdf"%self.methodName
    #     savedir = os.getcwd() + "/plots/" + fname
    #     pdf = PdfPages(fname)
    #     for _, v in self.imageGroupsCalulated.items():
    #         dr = v.date_results
    #
    #
    #         pdf.savefig(fig)
    #         plt.close(fig)
    #     pdf.close()
    #     # image = mpimg.imread("/home/john/wsdlims_ripped/ECIR2016TurkData/composites/" + v.composite)
    #     # plt.imshow(image)
    #
    #     plt.show()
    #     plt.close(fig)

    def plot_dates(self):
        savedir = "/home/john/PycharmProjects/CompareHistograms/plots/methodDates/%s.pdf"%self.methodName
        pdf = PdfPages(savedir)
        for _, v in self.imageGroupsCalulated.items():
            dr = v.date_results
            fig = dr.plot_dates(composite=v.composite)
            pdf.savefig(fig)
            plt.close(fig)
        pdf.close()



    def showPerComp(self, out):
        methodTotal = 0.0
        count = 0.0
        for k,v in self.imageGroupsCalulated.items():
            out.write(v.composite+" %f"%v.average+"\n")
            methodTotal += v.average
            count += 1.0
        out.write(self.methodName+" average=%f"%(methodTotal/count)+"\n")

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
            print("plotting %s" % m)
            method.calc_comp_hists()
            method.plot()
