import math
from statistics import mean

import cv2
import numpy as np
from sklearn import metrics
from sklearn.cluster import KMeans
from dominateColor import getColorComposition2,ColorComposition
from skimage.measure import structural_similarity as ssim
from util import getsite, getdatetime
from datetime import datetime
histogram_comparison_method = ("Correlation", cv2.HISTCMP_CORREL)


def gethistogram(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [256, 256, 256],
                          [0, 256, 0, 256, 0, 256])
    return cv2.normalize(imhist, imhist,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX)


def get3dhisto64(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [256, 256, 256],
                          [0, 256, 0, 256, 0, 256])
    return imhist

    # return imhist
def getlavhisto(cvim):
    imhist = cv2.calcHist([cvim], [0, 1, 2], None, [100, 127, 127],
                          [0, 100, -127, 127, -127, 127])
    return cv2.normalize(imhist, imhist)

class CompositeColorResulst:
    """
    :type site: str
    :type composite: str
    :type results: dict[datetime,list[ColorComposition]]
    """
    def __init__(self,site, composite):
        self.site = site
        self.composite = composite
        self.results = {}  # type: dict(datetime,list[ColorComposition])

    def to_jdic(self):
        trans = {}
        for dt,cc in self.results.items():
            trans[dt.date().isoformat()] = cc
        return {"site": self.site, "comp":self.composite, "color":trans}

class CompositeThumbResults:
    def __init__(self, site, composite):
        self.site = site
        self.composite = composite
        self.results = []  # list
        self.av = None


    def __getitem__(self, site):
        return self.results[site]

    def add_ret(self, im, ret):
        self.results.append((im, ret))


class Thumbnail:
    def __init__(self, image, site=None):
        self.imageName = image  # type: str
        if site is not None:
            self.site = site  # type: str
        else:
            self.site = getsite(image)
        self.date_dt = getdatetime(image)  # type: datetime
        self.date = self.date_dt.date().isoformat()  # type: str
        self.id = self.site + ":" + self.date
        self.histogram = None
        self.hist_ret = None
        self.rawImage = None
        self.path = None
        self.numUniqueColor = None

    def __str__(self):
        return self.imageName

    @property
    def printable(self):
        return self.site + ":" + self.date

    def cv_read_rawim(self, path):
        self.path = path
        self.rawImage = cv2.imread(cv2.imread(path + self.imageName, cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)

    def cv_get_histogram(self, path):
        self.path = path
        print(self.imageName)
        self.rawImage = cv2.cvtColor(cv2.imread(path + self.imageName, cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
        self.histogram = gethistogram(self.rawImage)
        # self.numUniqueColor = cv2.countNonZero(self.histogram.flatten())

    def getColors(self):
        nonezero = self.histogram.nonzero() # type: np.nonzero


        (nzdim1, nzdim2,nzdim3) = self.histogram.nonzero()
        is1 = 0.0
        for ((r,g),b) in zip(zip(nzdim1,nzdim2),nzdim3):
            # print("[%d,%d,%d] %f"%(r,g,b,self.histogram[r,g,b]))
            is1 += self.histogram[r,g,b]

        dsum = 0.0
        for ((r,g),b) in zip(zip(nzdim1,nzdim2),nzdim3):
            # print("[%d,%d,%d] %f"%(r,g,b,self.histogram[r,g,b]/is1))
            dsum += self.histogram[r,g,b]/is1


        print("is 1?? ",dsum)

        #     print(self.histogram[nz])
        #
        # for it in np.nonzero(self.histogram):
        #     print(it)
        # for r in range(256):
        #     for g in range(256):
        #         for b in range(256):
        #             print("[%d,%d,%d]: "%(r,g,b),self.histogram[r,g,b])


    def get_dominate_colors(self):
        return getColorComposition2("/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots/"  + self.imageName)

    def getUniqueColors(self):
        image = cv2.imread(self.path + self.imageName, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        w_new = int(100 * w / max(w, h) )
        h_new = int(100 * h / max(w, h) )

        image = cv2.resize(image, (w_new, h_new))
        image_array = image.reshape((image.shape[0] * image.shape[1], 3))

        bestSilhouette = -1
        bestClusters = 0
        for clusters in range(2, 10):
            # Cluster colours
            clt = KMeans(n_clusters=clusters,n_jobs=2)
            clt.fit(image_array)

            # Validate clustering result
            if len(clt.labels_) > 1:
                silhouette = metrics.silhouette_score(image_array, clt.labels_, metric='euclidean')

                # Find the best one
                if silhouette > bestSilhouette:
                    bestSilhouette = silhouette
                    bestClusters = clusters

        return bestClusters


    def site_date(self):
        return self.id

    def clean_up(self):
        del self.histogram
        self.clean_rawim()


    def clean_rawim(self):
        if self.rawImage is not None:
            del self.rawImage


class CompositeThumbnails:
    def __init__(self, path, compmapping):
        self.path = path
        self.site = compmapping.site
        self.thumbnails = []  # type: list[Thumbnail]
        self.composite = compmapping.composite  # type: str
        self.average = None  # type: float
        self.date_results = None  # type: CompositeThumbResults
        self._process(compmapping)

    def __str__(self):
        return self.site

    def __getitem__(self, key):
        return self.thumbnails[key]

    def __len__(self):
        return len(self.thumbnails)

    def sort(self, key=None):
        if key is not None:
            self.thumbnails.sort(key=key)
        else:
            self.thumbnails.sort(key=lambda thumnail: thumnail.date_dt)

    def valid_for_comp(self):
        return len(self.thumbnails) >= 2 and self.composite is not None

    def has_composite(self):
        return self.composite is not None

    def get_dom_colors_(self):
        colorComp = CompositeColorResulst(self.site,self.composite) # type: CompositeColorResulst
        for thum in self.thumbnails:
            colorComp.results[thum.date_dt] = thum.get_dominate_colors()
        return colorComp


    def _process(self, compmapping):
        for thum in compmapping.imList:
            self.thumbnails.append(Thumbnail(thum, site=compmapping.site))

    def add_thumb(self, thumbnail):
        self.thumbnails.append(thumbnail)

    def group_cvhist(self):
        for im in self.thumbnails:
            im.cv_get_histogram(self.path)
            im.clean_up()
            break

    def group_image(self):
         for im in self.thumbnails:
            im.cv_read_rawim(self.path)

    def av_color(self):
        # it = []
        # for t in self.thumbnails:
        #     it.append(t.numUniqueColor)

        return mean(map(lambda x: x.getUniqueColors(), self.thumbnails))

    def compareDates_vsOther_oneTOone(self, other, out=None):
        self.sort()
        self.group_cvhist()
        print(type(other))
        other.group_cvhist()
        values = []
        for mythumb, otherThum in zip(self.thumbnails, other.thumbnails):
            ret = math.fabs(cv2.compareHist(mythumb.histogram, otherThum.histogram, cv2.HISTCMP_CORREL))
            values.append(ret)

        print("The average was %f for site %s\n" % (mean(values), self.site))
        if out is not None:
            out.write("%s,%f\n" % (self.site, mean(values)))
        self.clean_up()
        other.clean_up()

    def compare_hists_dates(self):
        self.sort()
        length = len(self.thumbnails)
        rang = range(length)

        self.date_results = CompositeThumbResults("Correlation", self.composite)
        values = []
        for i in rang:
            if i + 1 < length:
                ret = math.fabs(cv2.compareHist(self.thumbnails[i].histogram, self.thumbnails[i + 1].histogram,
                                                cv2.HISTCMP_CORREL))
                values.append(ret)

                self.date_results.add_ret((self.thumbnails[i].date, self.thumbnails[i + 1].date),
                                          ret)
        self.average = mean(values)
        self.date_results.av = self.average

    def compare_structure_dates(self):
        self.sort()
        length = len(self.thumbnails)
        rang = range(length)

        self.date_results = CompositeThumbResults("Structure", self.composite)
        values = []
        for i in rang:
            if i + 1 < length:
                ret = ssim(self.thumbnails[i].rawImage, self.thumbnails[i + 1].rawImage)
                values.append(ret)

                self.date_results.add_ret((self.thumbnails[i].date, self.thumbnails[i + 1].date),
                                          ret)
        self.average = mean(values)
        self.date_results.av = self.average

    def clean_up(self):
        for thum in self.thumbnails:
            thum.clean_up()


class MethodCompThums:
    def __init__(self, method, path, compMappings):
        self.compositThumbs = {}  # type: dict[str,CompositeThumbnails]
        self.methodName = method  # type: str
        self.path = path  # type: str
        self.totalSize = 0
        self.compMappings = compMappings  # type: dict[str,MappedComp]
        self.compositThumbsCalulated = {}  # type: dict[str,CompositeThumbnails]
        self.site_figs = {}
        self._process()

    def __getitem__(self, site):
        return self.compositThumbs[site]

    def __str__(self):
        return self.methodName

    def __contains__(self, item: str):
        try:
            self.compositThumbs[item]
        except KeyError:
            return False
        return True

    def sorted_items(self):
        return sorted(self.compositThumbs.items(), key=lambda x: x[0])

    def items(self):
        return self.compositThumbs.items()

    def get_composites_items(self):
        return self.compositThumbs.items()

    def sites(self):
        return self.compositThumbs.keys()

    def _process(self):
        print(type(self.compMappings))
        for site, compmap in self.compMappings.items():
            print(site, compmap)
            self.totalSize += 1
            self.compositThumbs[site] = CompositeThumbnails(self.path, compmap)



    def get_composite_dom_colors(self):
          """
          :rtype: dict[str,CompositeColorResulst]
          """
          dc_per_comp = {} # type: dict(str,CompositeColorResulst)
          for site, compthumb in self.compositThumbs.items():
              print("proccessing site ",site)
              dc_per_comp[site] = compthumb.get_dom_colors_()
          return dc_per_comp


    def get_histograms(self):
        for site, compthumb in self.compositThumbs.items():
            compthumb.group_cvhist()
            break

    def calc_comp_hist_date(self):
        for site, compthumb in self.compositThumbs.items():
            compthumb.group_cvhist()
            compthumb.compare_hists_dates()
            compthumb.clean_up()

    def calc_comp_structure_date(self):
        for site, compthumb in self.compositThumbs.items():
            compthumb.group_cvhist()
            compthumb.compare_hists_dates()
            compthumb.clean_up()

    #
    # def calc_comp_hist_date(self, path=None, p=None, out=None):
    #     for site, compthumb in self.compositThumbs.items():
    #         # print(self.methodName, site)
    #         if compthumb.valid_for_comp():
    #             compthumb.group_cvhist()
    #             compthumb.compare_hists_dates(path, p, out)
    #             compthumb.clean_up()
    #             self.compositThumbsCalulated[site] = compthumb

    def showPerComp(self, out):
        methodTotal = 0.0
        count = 0.0
        for k, v in self.compositThumbsCalulated.items():
            out.write(v.composite + " %f" % v.average + "\n")
            methodTotal += v.average
            count += 1.0
        out.write(self.methodName + " average=%f" % (methodTotal / count) + "\n")


class CompositeOnly:
    def __init__(self, path, method_composites):
        self.method_composites = method_composites
        self.path = path + "/"

    def do_comparison(self, out):
        alsum = sorted(self.method_composites['alSum'].items(), key=lambda x: x[0])
        random = sorted(self.method_composites['random'].items(), key=lambda x: x[0])
        temporal = sorted(self.method_composites['temporalInterval'].items(), key=lambda x: x[0])
        for ((asite, acomp), (rsite, rcomp)), (tsite, tcomp) in zip(zip(alsum, random), temporal):
            print(acomp, rcomp, tcomp)

            aHist = gethistogram(cv2.imread(self.path + acomp, cv2.IMREAD_COLOR))
            rHist = gethistogram(cv2.imread(self.path + rcomp, cv2.IMREAD_COLOR))
            tHist = gethistogram(cv2.imread(self.path + tcomp, cv2.IMREAD_COLOR))
            arSim = math.fabs(cv2.compareHist(aHist, rHist, cv2.HISTCMP_CORREL))
            atSim = math.fabs(cv2.compareHist(aHist, tHist, cv2.HISTCMP_CORREL))
            out.write("%s,%f,%f\n" % (asite, arSim, atSim))
            del aHist
            del rHist
            del tHist
