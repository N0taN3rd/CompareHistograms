from collections import defaultdict

import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

from MethodImages import MethodIms
from imcomp import get_files
import webcolors




def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


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



def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0
    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        print(percent,color,"Closest colour name: %s"%closest_colour((color[0],color[1],color[2])))
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar

class ColorComposition:
    def __init__(self,percent,rgb,name):
        self.percent = percent
        self.rgb = rgb
        self.name = name

class ImgroupColor:
    def __init__(self,imgroup):
        self.imgroup = imgroup
        self.site_color = {}

    def find_it(self):
        pass



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
                # show our color bart
                plt.figure()
                plt.axis("off")
                plt.imshow(bar)
                plt.figure()
                plt.axis("off")
                plt.imshow(image)
                plt.show()
