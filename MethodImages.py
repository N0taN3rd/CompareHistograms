import json
import os
import random
import time
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
    lhttp = imname.rfind("http")
    lastweb = imname.rfind("web", 0, lhttp)
    return datetime.strptime(imname[lastweb + 3:lhttp], "%Y%m%d%H%M%S")


def get3dhisto(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [256, 256, 256],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist)


def get3dhisto8(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [8, 8, 8],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist).flatten()


def get3dhisto32(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [32, 32, 32],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist).flatten()


def get3dhisto64(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [64, 64, 64],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist).flatten()


def get3dhisto256(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [256, 256, 256],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist)


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
        else:
            self.base_date = None
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
                labels.append(str('%.5f' % p[1]) + " " + p[0][0] + ":" + p[0][1])
            else:
                labels.append(str('%.5f' % p[1]) + " " + p[0])
            count += 1
        return labels

    def plot_dates(self, composite=None):
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

        bars = axs[1].bar(ind, plotpoints, width, color=barcolors)
        #
        axs[1].set_xlim(-width, len(ind) + width)
        axs[1].set_ylim(0, 1)
        plt.ylabel('Correlation Similarity Scores')
        #
        if composite is not None:
            axs[1].set_title(composite)
        else:
            axs[1].set_title(self.b)
        #
        axs[1].set_xticks([])
        # plt.setp(axs[0].set_xticklabels(bottomLables), rotation=90, fontsize=10)

        box = axs[1].get_position()
        axs[1].set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # # ax.legend(bars, tlables,fontsize='small',loc='upper center', bbox_to_anchor=(0.5, 1.0),
        # #   ncol=3, fancybox=True)
        axs[1].legend(bars, tlables, fontsize='x-small', loc='center left', bbox_to_anchor=(1, 0.5))

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
            ax.set_title(composite)  # + "\nbase image date: " + self.base_date)
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
        self.histograms = {}  # type: dict
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
        self.histograms["3d"] = get3dhisto(self.mat)
        # self.hists["hsv"] = gethsvhisto(self.mat)

    def site_date(self):
        return self.id

    def clean(self):
        del self.mat
        del self.histograms

    def compare_hist(self, other: set, meths):
        (mname, m) = meths
        # for mname, m in meths:
        histret = HistCompRet(mname, self.image)
        for oim in other:
            histret.add_ret(oim.date, cv2.compareHist(self.histograms["3d"], oim.hists["3d"], m))
            # histret.add_ret(oim.date, cv2.compareHist(self.hists["hsv"], oim.hists["hsv"], m))
        histret.hist_type = "3d"
        self.hist_ret[mname] = histret

    def compare_self(self):
        return cv2.compareHist(self.histograms["3d"], self.histograms["3d"], cv2.HISTCMP_CORREL)

    def plot(self, composite=None):
        if composite is not None:
            return self.hist_ret["Correlation"].plot(composite=composite)
        else:
            return self.hist_ret["Correlation"].plot()

    def get_hist(self):
        return self.histograms['3d']

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

    def do8(self):

        self.group_cvread()
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)
        self.date_results = HistCompRet("Correlation", self.composite)

        end = time.time()

    def do32(self):
        start = time.time()
        self.group_cvread()
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)
        self.date_results = HistCompRet("Correlation", self.composite)

        end = time.time()

    def do64(self):
        self.group_cvread()
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)
        self.date_results = HistCompRet("Correlation", self.composite)

    def do256(self):
        self.group_cvread()
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)
        self.date_results = HistCompRet("Correlation", self.composite)

    def compare_dates_makepdf(self):
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)
        self.date_results = HistCompRet("Correlation", self.composite)
        totalSum = 0.0
        c = 0
        figs = []
        for i in rang:
            if i + 1 < length:
                ret = cv2.compareHist(self.images[i].get_hist(), self.images[i + 1].get_hist(),
                                      cv2.HISTCMP_CORREL)
                totalSum += ret
                c += 1
                figs.append(self.plot_impair_score(i, "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots/", ret))
                self.date_results.add_ret((self.images[i].date, self.images[i + 1].date),
                                          ret)

        # print(type(totalSum))
        # print(totalSum, totalSum / length)
        self.average = totalSum / c
        self.date_results.add_ret("Average", self.average)
        print(self.composite)
        figs.append(self.date_results.plot_dates(composite=self.composite))
        savedir = "/home/john/PycharmProjects/CompareHistograms/plots/composite_breakdowns/" + self.composite + \
                  "_bd.pdf"
        pdf = PdfPages(savedir)

        for fig in figs:
            pdf.savefig(fig)
        pdf.close()

        for fig in figs:
            plt.close(fig)

    def compare_hists_dates_groups(self):
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)

        self.date_results = HistCompRet("Correlation", self.composite)
        totalSum = 0.0
        c = 0
        for i in rang:
            if i + 1 < length:
                ret = cv2.compareHist(self.images[i].histograms["3d"], self.images[i + 1].histograms["3d"],
                                      cv2.HISTCMP_CORREL)

                totalSum += ret
                c += 1
                self.date_results.add_ret(
                        (self.images[i].date, self.images[i + 1].date),
                        ret)
                # else:
                # print("last ", self.images[i].site_date())

                # print(type(totalSum))
                # print(totalSum, totalSum / length)

    def compare_hists_dates(self, path=None, p=None, out=None):
        self.sort(key=lambda im: im.date_dt)
        length = len(self.images)
        rang = range(length)

        self.date_results = HistCompRet("Correlation", self.composite)
        totalSum = 0.0
        c = 0
        for i in rang:
            if i + 1 < length:
                ret = cv2.compareHist(self.images[i].histograms["3d"], self.images[i + 1].histograms["3d"],
                                      cv2.HISTCMP_CORREL)

                totalSum += ret
                c += 1
                if path is not None:
                    out.write(self.images[i].image + ", " + self.images[i + 1].image + " %f" % ret + "\n")
                    # self.show_impair_score(i, path, ret)

                self.date_results.add_ret((self.images[i].date, self.images[i + 1].date),
                                          ret)
                # else:
                # print("last ", self.images[i].site_date())

        # print(type(totalSum))
        # print(totalSum, totalSum / length)
        self.average = totalSum / c

        if p is not None:
            out.write(self.composite + " %f" % self.average + "\n")
            out.write("\n")
        self.date_results.add_ret("Average", self.average)

    def show_impair_score(self, i, path, ret):
        print(path + self.images[i].image, path + self.images[i + 1].image)
        im1 = plt.imread(path + self.images[i].image)
        im2 = plt.imread(path + self.images[i + 1].image)
        # fig,ax = plt.subplots(im2.shape[0]*2,im2.shape[1]*2,sharey=True)
        fig, axs = plt.subplots(2, sharey=True)
        fig.set_size_inches(10, 10, forward=True)
        axs[0].imshow(im1, aspect='auto', shape=im1.shape)
        axs[0].set_title(self.images[i].site_date())
        imv = "\n" + self.images[i].date + " compared to " + self.images[i + 1].date
        plt.suptitle(self.composite + imv + " simularity of %f" % ret)
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        plt.axis('off')
        axs[1].imshow(im2, aspect='auto', shape=im2.shape)
        axs[1].set_xticks([])
        axs[1].set_yticks([])
        axs[1].set_title(self.images[i + 1].site_date())
        # plt.text(x=5.0, y=-9.0, s="score=%f" % ret)
        plt.axis('off')
        plt.show()

    def plot_impair_score(self, i, path, ret):
        # print(path + self.images[i].image,path + self.images[i + 1].image)
        im1 = plt.imread(path + self.images[i].image)
        im2 = plt.imread(path + self.images[i + 1].image)
        # fig,ax = plt.subplots(im2.shape[0]*2,im2.shape[1]*2,sharey=True)
        fig, axs = plt.subplots(2, sharey=True)
        fig.set_size_inches(10, 10, forward=True)
        axs[0].imshow(im1, aspect='auto', shape=im1.shape)
        axs[0].set_title(self.images[i].site_date())
        imv = "\n" + self.images[i].date + " compared to " + self.images[i + 1].date
        plt.suptitle(self.composite + imv + " simularity of %f" % ret)
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        plt.axis('off')
        axs[1].imshow(im2, aspect='auto', shape=im2.shape)
        axs[1].set_xticks([])
        axs[1].set_yticks([])
        axs[1].set_title(self.images[i + 1].site_date())
        # plt.text(x=5.0, y=-9.0, s="score=%f" % ret)
        plt.axis('off')
        return fig

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

    def do_it(self):
        for site, img in self.imageGroups.items():
            if img.valid_for_comp() and img.has_composite():
                img.group_cvread()
                img.compare_dates_makepdf()
                img.clean_up()
                self.imageGroupsCalulated[site] = img

    def calc_comp_hist_date(self, path=None, p=None, out=None):
        for site, img in self.imageGroups.items():
            if img.valid_for_comp() and img.has_composite():
                img.group_cvread()
                img.compare_hists_dates(path, p, out)
                img.clean_up()
                self.imageGroupsCalulated[site] = img

    def getMethodAv(self, out):
        count = 0.0
        sum = 0.0
        for _, img in self.imageGroupsCalulated.items():
            count += 1.0
            sum += img.average
        out.write(self.methodName + " average %f" % (sum / count) + "\n")

    def sortBySimularity(self):
        new_list = sorted(self.imageGroupsCalulated.items(), key=lambda x: x[1].average)
        for site, group in new_list:
            print(self.methodName, group.site,group.average)
        print("___________________________________________________________________________")

    def full(self):
        for _, v in self.imageGroupsCalulated.items():
            v.compare_dates_makepdf()

    def plot_dates(self):
        savedir = "/home/john/PycharmProjects/CompareHistograms/plots/methodDates/%s.pdf" % self.methodName
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
        for k, v in self.imageGroupsCalulated.items():
            out.write(v.composite + " %f" % v.average + "\n")
            methodTotal += v.average
            count += 1.0
        out.write(self.methodName + " average=%f" % (methodTotal / count) + "\n")

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


class Why:
    def __init__(self, path, impath, compath):
        self.path = path
        self.impath = impath + "/"
        self.compath = compath + "/"
        self.sites = defaultdict(list)

    def shit(self):
        with open(self.path, "r+") as o:
            for line in map(lambda s: s.rstrip("\n"), o):
                if "_200" not in line:
                    print(line, getsite(line))
                    self.sites[getsite(line)].append(line)
            o.close()
            print("done with line print")

            # for p in ["/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots
            # /random_httpwebarchiveorgweb20120623124738httpwwwadventuresinestrogenblogspotcom.png",
            #           "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots
            # /alSum_httpwebarchiveorgweb20120624122540httpwwwadventuresinestrogenblogspotcom.png"]:
            #     im1 = plt.imread(p)
            #     plt.imshow(im1)
            #     plt.show()

            for site in self.estrogen:
                print("_____________________________________")
                print(site)
                print(site)
                print("--------------------------------------")
                im1 = plt.imread(site)
                plt.imshow(im1, aspect='auto')
                plt.show()
                # for k, l in self.sites.items():
                #     print(k)
                #
                #     for site in l:
                #         print("_____________________________________")
                #         print(site)
                #         print(self.impath+site)
                #         print("--------------------------------------")
                #         im1 = plt.imread(self.impath + site)
                #         plt.imshow(im1)
                #         plt.show()

    def setaxis(self, ax, img, title):
        ax.imshow(img, aspect='auto', shape=img.shape)
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])

    def make_fig(self, axs, ims, titles):
        pass

    def show(self):

        pdf = PdfPages("/home/john/allSame2.pdf")
        estrogencomp = self.compath + "allTheSame_adventuresinestrogenblogspotcom_composite.png"
        estrogen = [
            "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"
            "/random_httpwebarchiveorgweb20120623124738httpwwwadventuresinestrogenblogspotcom.png",
            "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"
            "/alSum_httpwebarchiveorgweb20120624122540httpwwwadventuresinestrogenblogspotcom.png"]

        composite_image = plt.imread(estrogencomp)

        estrogenhits = []
        estrogenims = []
        for s in estrogen:
            estrogenhits.append(get3dhisto(cv2.imread(s, cv2.IMREAD_COLOR)))
            estrogenims.append(plt.imread(s))

        (estrogenff, estrogenss, estrogenfs) = \
            (cv2.compareHist(estrogenhits[0], estrogenhits[0], cv2.HISTCMP_CORREL),
             cv2.compareHist(estrogenhits[1], estrogenhits[1], cv2.HISTCMP_CORREL),
             cv2.compareHist(estrogenhits[0], estrogenhits[1], cv2.HISTCMP_CORREL))

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], estrogenims[0], "random_adventuresinestrogenblogspotcom:" + getdate(
                estrogen[0]).date().isoformat() + " self compare %f" % estrogenff)
        self.setaxis(axs[1], composite_image, "allTheSame_adventuresinestrogenblogspotcom_composite.png")
        pdf.savefig(fig)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], estrogenims[1], "alSum_adventuresinestrogenblogspotcom:" + getdate(
                estrogen[1]).date().isoformat() + " self compare %f" % estrogenss)
        self.setaxis(axs[1], composite_image, "allTheSame_adventuresinestrogenblogspotcom_composite.png")
        pdf.savefig(fig)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], estrogenims[0], "alSum_adventuresinestrogenblogspotcom:" + getdate(
                estrogen[0]).date().isoformat() + " top image vs bottom %f" % estrogenfs)
        self.setaxis(axs[1], estrogenims[1], "random_adventuresinestrogenblogspotcom:" + getdate(
                estrogen[0]).date().isoformat() + " bottom vs top %f" % cv2.compareHist(estrogenhits[1],
                                                                                        estrogenhits[0],
                                                                                        cv2.HISTCMP_CORREL))
        pdf.savefig(fig)

        # plt.show()

        firtdowncomp = self.compath + "allTheSame_firstdownsportsbarcom_composite.png"
        firstsport = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots" \
                     "/temporalInterval_httpwebarchiveorgweb20090418174148httpwwwfirstdownsportsbarcom.png"
        fistsporthist = get3dhisto(cv2.imread(firstsport, cv2.IMREAD_COLOR))
        fistsporthistself = cv2.compareHist(fistsporthist, fistsporthist, cv2.HISTCMP_CORREL)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], plt.imread(firstsport), "temporalInterval_firstdownsportsbarcom:"
                     + getdate("temporalInterval_httpwebarchiveorgweb20090418174148httpwwwfirstdownsportsbarcom.png")
                     .date().isoformat() + " self compare %f" % fistsporthistself)
        self.setaxis(axs[1], plt.imread(firtdowncomp), "allTheSame_firstdownsportsbarcom")

        pdf.savefig(fig)

        ihacomcomp = self.compath + "allTheSame_ihacomcn_composite.png"
        ihancomcn = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots" \
                    "/alSum_httpwebarchiveorgweb20100414212212httpwwwihacomcn.png"
        ihancomcnhist = get3dhisto(cv2.imread(ihancomcn, cv2.IMREAD_COLOR))
        ihancomcnhistself = cv2.compareHist(ihancomcnhist, ihancomcnhist, cv2.HISTCMP_CORREL)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], plt.imread(ihancomcn), "alSum_ihacomcn:"
                     + getdate("alSum_httpwebarchiveorgweb20100414212212httpwwwihacomcn.png")
                     .date().isoformat() + " self compare %f" % ihancomcnhistself)
        self.setaxis(axs[1], plt.imread(ihacomcomp), "allTheSame_ihacomcn_composite")

        pdf.savefig(fig)

        bwjdesigncomcomp = self.compath + "allTheSame_bwjdesigncom_composite.png"
        bwjdesigncom = [
            "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"
            "/alSum_httpwebarchiveorgweb20080917221554httpwwwbwjdesigncom.png",
            "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"
            "/interval_httpwebarchiveorgweb20081222092616httpwwwbwjdesigncom.png"]

        bwjdesigncomhits = []
        bwjdesigncomims = []
        for s in bwjdesigncom:
            bwjdesigncomhits.append(get3dhisto(cv2.imread(s, cv2.IMREAD_COLOR)))
            bwjdesigncomims.append(plt.imread(s))

        (bwjdesigncomff, bwjdesigncomss, bwjdesigncomfs) = \
            (cv2.compareHist(bwjdesigncomhits[0], bwjdesigncomhits[0], cv2.HISTCMP_CORREL),
             cv2.compareHist(bwjdesigncomhits[1], bwjdesigncomhits[1], cv2.HISTCMP_CORREL),
             cv2.compareHist(bwjdesigncomhits[0], bwjdesigncomhits[1], cv2.HISTCMP_CORREL))

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], bwjdesigncomims[0], "alSum_bwjdesigncom:"
                     + getdate("alSum_httpwebarchiveorgweb20080917221554httpwwwbwjdesigncom.png")
                     .date().isoformat() + " self compare score %f" % bwjdesigncomff)
        self.setaxis(axs[1], plt.imread(bwjdesigncomcomp), "allTheSame_bwjdesigncom_composite")

        pdf.savefig(fig)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], bwjdesigncomims[1], "interval_bwjdesigncom:"
                     + getdate("alSum_httpwebarchiveorgweb20080917221554httpwwwbwjdesigncom.png")
                     .date().isoformat() + " self compare score %f" % bwjdesigncomss)
        self.setaxis(axs[1], plt.imread(bwjdesigncomcomp), "allTheSame_bwjdesigncom_composite")

        pdf.savefig(fig)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], bwjdesigncomims[0], "alSum_bwjdesigncom:"
                     + getdate("alSum_httpwebarchiveorgweb20080917221554httpwwwbwjdesigncom.png")
                     .date().isoformat() + " top vs bottom %f" % bwjdesigncomfs)
        self.setaxis(axs[1], bwjdesigncomims[1], "interval_bwjdesigncom:"
                     + getdate("alSum_httpwebarchiveorgweb20080917221554httpwwwbwjdesigncom.png")
                     .date().isoformat() + " bottom vs top %f" % cv2.compareHist(bwjdesigncomhits[1],
                                                                                 bwjdesigncomhits[0],
                                                                                 cv2.HISTCMP_CORREL))
        pdf.savefig(fig)
        oafbcacomp = self.compath + "allTheSame_oafbca_composite.png"
        oafbca = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots" \
                 "/interval_httpwebarchiveorgweb20140926201207httpwwwoafbca.png"
        oafbcahist = get3dhisto(cv2.imread(oafbca, cv2.IMREAD_COLOR))
        oafbcahistself = cv2.compareHist(oafbcahist, oafbcahist, cv2.HISTCMP_CORREL)

        fig, axs = plt.subplots(2)
        fig.set_size_inches(15, 15, forward=True)
        self.setaxis(axs[0], plt.imread(oafbca),
                     "interval_oafbca:" + getdate("interval_httpwebarchiveorgweb20140926201207httpwwwoafbca.png")
                     .date().isoformat() + " self compare score %f" % oafbcahistself)

        self.setaxis(axs[1], plt.imread(oafbcacomp), "allTheSame_oafbca_composite")

        pdf.savefig(fig)

        pdf.close()
