from collections import defaultdict
from sklearn import metrics

import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans, estimate_bandwidth, MeanShift, DBSCAN, MiniBatchKMeans

from MethodImages import MethodIms
from imcomp import get_files
import webcolors




def closest_colour(requested_colour):
    # Euclidian distance in the RGB space.
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    # return the histogram
    return hist

def centroid_histogram2(labs):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(labs)) + 1)
    (hist, _) = np.histogram(labs, bins=numLabels)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    # return the histogram
    return hist


def plot_colors(hist, centroids):
    bar = np.zeros((50, 300, 3), dtype = "uint8")
    startX = 0
    for (percent,color) in zip(hist,centroids):
        endX = startX+(percent*300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
			color.astype("uint8").tolist(), -1)
        startX = endX

    return bar

class ColorComposition:
    """
    :type percent: float
    :type rgb: list[float]
    :type name: str
    """
    def __init__(self,percent,rgb,name):
        self.percent = percent
        self.rgb = rgb
        self.name = name

    def to_jdic(self):
        return {"name":self.name,"rgb":self.rgb,"percent":self.percent}

    def __str__(self):
        return "color: %s at %f percent"%(self.name,self.percent)


def old(impath):
    pass


def testClusters(image):
    bestSilhouette = -1
    bestClusters = 0
    bestLabels = None
    bestCenters = None

    for clusters in range(2, 10):
        # Cluster colours
        clt = MiniBatchKMeans(n_clusters = clusters)
        labs = clt.fit_predict(image)
        try:
            silhouette = metrics.silhouette_score(image, labs, metric='euclidean',sample_size=500)
            if silhouette > bestSilhouette:
                bestSilhouette = silhouette
                bestClusters = clusters
                bestLabels = clt.labels_
                bestCenters = clt.cluster_centers_

        except ValueError as ve:
            print(ve,clusters)
            if len(labs) == 1:
                bestLabels = labs
                bestCenters = clt.cluster_centers_
        del clt

    return bestClusters,bestLabels,bestCenters

def getColorComposition(impath):
    """
    :param impath: str
    :return: list[ColorComposition]
    """
    image = cv2.cvtColor(cv2.imread(impath, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    image2 = image.reshape((image.shape[0] * image.shape[1], 3))
    clt = MiniBatchKMeans(n_clusters=4)
    clt.fit(image2)
    hist = centroid_histogram2(clt.labels_)
    composition = [] # type: list[ColorComposition]
    for (percent, color) in zip(hist, clt.cluster_centers_):
        closest = closest_colour((color[0],color[1],color[2]))
        # print("Closest %s with percent %f"%(closest,percent))
        composition.append(ColorComposition(percent,color,closest))
    # print("____________________________")
    del image
    del image2
    del hist
    del clt
    return composition


def reduceColors(path):
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    (h, w) = image.shape[:2]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    clt = MiniBatchKMeans(n_clusters = 12)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]
    quant = quant.reshape((h, w, 3))
    quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
    return quant




def getColorComposition2(impath):
    """
    :param impath: str
    :return: list[ColorComposition]
    """
    # image = cv2.cvtColor(cv2.imread(impath, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    image = reduceColors(impath)
    # r = 512 / image.shape[1]
    # dim = (512, int(image.shape[0] * r))
    # image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    image2 = image.reshape((image.shape[0] * image.shape[1], 3))
    bestClusters,bestLabels,bestCenters = testClusters(image2)
    # clt = MiniBatchKMeans(n_clusters=6)
    # clt.fit(image2)
    composition = [] # type: list[ColorComposition]
    if bestLabels is not None:
        hist = centroid_histogram2(bestLabels)
        for (percent, color) in zip(hist, bestCenters):
            closest = closest_colour((color[0],color[1],color[2]))
            # print("Closest %s with percent %f"%(closest,percent))
            composition.append(ColorComposition(percent,color,closest))
        del hist
    del image
    del image2
    return composition

if __name__ == "__main__":
    print("me")
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    print(compath)

    files = get_files(impath, test=None)
    compisits = get_files(compath, lambda f: "allTheSame" not in f)

    method_composites = defaultdict(dict)

    for comp in sorted(compisits):
        # print(comp)
        site = comp[comp.find("_") + 1:comp.rfind("_")]
        # method_composites[comp[:comp.index("_")]][site] = comp
        if len(site) != 3:
            method_composites[comp[:comp.index("_")]][site] = comp
        # else:
        #     # plt.imread(compath)
        #     print(site,comp)
    # print(method_composites['alSum']['org'])
    impath += "/"
    methods = {'random': MethodIms('random', impath, method_composites["random"]),
               'temporalInterval': MethodIms('temporalInterval', impath, method_composites["temporalInterval"]),
               'alSum': MethodIms('alSum', impath, method_composites["alSum"]),
               'interval': MethodIms('interval', impath, method_composites["interval"])}
    """ :type dict(str,MethodIms) """

    for item in files:
        index = item.index('_')
        m = item[0:index]
        methods.get(m).add_image(item)

    alsum = methods['alSum']

    for site, img in alsum.imageGroups.items():
        if "_200" not in site and img.valid_for_comp() and img.has_composite():
            img.sort(key=lambda im: im.date_dt)
            for im in img.images:
                print(site,im.date_dt)
                image = cv2.cvtColor(cv2.imread(impath + im.image, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
                image2 = image.reshape((image.shape[0] * image.shape[1], 3))
                print(image.shape)
                print(image2.shape)
                clt = KMeans(n_clusters=5,n_jobs=2)
                clt.fit(image2)
                hist = centroid_histogram(clt)
                bar = plot_colors(hist, clt.cluster_centers_)
                break

