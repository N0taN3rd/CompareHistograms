from collections import defaultdict
import cv2
import multiprocessing
import numpy as np
from scipy.spatial import distance as dist

debug = True



def getsite(imname):
    index = imname.find('http', imname.find('http') + 1)
    return imname[index:imname.index('.')]


def getdate(image):
    s = []
    lasthttp = image.find('http', image.find('http') + 1)
    saw = 0
    for c in image:
        if c.isdigit():
            s.append(c)
        saw += 1
        if saw == lasthttp:
            break
    return ''.join(s)


def get3dhisto(cvim):
    imHist = cv2.calcHist([cvim], [0, 1, 2], None, [8, 8, 8],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imHist, imHist).flatten()


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


class HistCompRet:
    def __init__(self, mname, base):
        self.mname = mname
        self.base = base
        self.rets = defaultdict(list)

    def __getitem__(self, site):
        return self.rets[site]

    def add_ret(self, im, ret):
        self.rets[im].append(ret)


class Image:
    def __init__(self, image):
        self.site = getsite(image)
        self.image = image
        self.site = getsite(image)
        self.date = getdate(image)
        self.id = self.site + self.date
        self.year = self.date[0:4]
        self.month = self.date[4:6]
        self.day = self.date[6:8]
        self.hour = self.date[8:10]
        self.minute = self.date[10:12]
        self.second = self.date[12:]
        self.hists = {}
        self.hist_ret = {}
        self.mat = None

    def __str__(self):
        return self.image

    def cv_read(self, path):
        self.mat = cv2.imread(path + self.image)
        self.hists["3d"] = get3dhisto(self.mat)
        self.hists["hsv"] = gethsvhisto(self.mat)

    def compare_hist(self, other, meths):
        for mname, m in meths:
            histRet = HistCompRet(mname, self.image)
            for oim in other:
                histRet.add_ret(oim.image, ("3d", cv2.compareHist(self.hists["3d"], oim.hists["3d"], m)))
                histRet.add_ret(oim.image, ("hsv", cv2.compareHist(self.hists["hsv"], oim.hists["hsv"], m)))
            self.hist_ret[mname] = histRet


class ImageGroup:
    def __init__(self, path, site):
        self.path = path
        self.site = site
        self.images = []
        self.hist_comp = (("Correlation", cv2.HISTCMP_CORREL),
                          ("Chi-Squared", cv2.HISTCMP_CHISQR),
                          ("Intersection", cv2.HISTCMP_INTERSECT),
                          ("Hellinger", cv2.HISTCMP_BHATTACHARYYA),
                          ("Kullback-Leibler divergence", cv2.HISTCMP_KL_DIV))

    def __str__(self):
        return self.site

    def __getitem__(self, index):
        return self.images[index]

    def __len__(self):
        return len(self.images)

    def add_im(self, im):
        self.images.append(im)

    def valid_for_comp(self):
        return len(self.images) >= 2

    def sort(self, key):
        self.images.sort(key=key)

    def group_cvread(self):
        if self.valid_for_comp():
            for im in self.images:
                im.cv_read(self.path)

    def compare_hists(self):
        if self.valid_for_comp():
            imset = set(self.images)
            for im in self.images:
                singlton = set()
                singlton.add(im)
                others = imset - singlton
                im.compare_hist(others, self.hist_comp)





class MethodIms:
    def __init__(self, method, path):
        self.imdic = {}
        self.methodName = method
        self.path = path
        self.totalsize = 0

    def __getitem__(self, site):
        return self.imdic[site]

    def __str__(self):
        return self.methodName

    def addim(self, image):
        site = getsite(image)
        try:
            imgroup = self.imdic[site]
        except KeyError:
            imgroup = ImageGroup(self.path, site)
            self.imdic[site] = imgroup
        self.totalsize += 1
        self.imdic[site].add_im(Image(image))

    def getimlist(self, image):
        return self.imdic[image]

    def keys(self):
        return self.imdic.keys()

    def items(self):
        return self.imdic.items()

    def values(self):
        return self.imdic.values()

    def size(self):
        return self.totalsize

    def sort(self, image):
        self.imdic[image].sort(key=lambda i: i.year)

    def calc_hists(self, im):
        imlist = self.imdic[im]
        imlist.group_cvread()
        imlist.compare_hists()

    def calc_all_hists(self):
        print(self.totalsize)

        good = list(filter(lambda x: x[1].valid_for_comp(), self.imdic.items()))
        print(len(good), len(good)/(multiprocessing.cpu_count()/3))

        print("num cpus=",multiprocessing.cpu_count())
        '''
        for i, img in good:
            print(i)
            img.group_cvread()
            img.compare_hists()
        '''

    def print(self):
        for site, ims in self.imdic.items():
            print(site)
            for i in ims:
                print(i)
