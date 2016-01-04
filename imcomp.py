from os import listdir
from os.path import isfile, join
from MethodImages import MethodIms, Image
import cv2
import numpy as np
from scipy.spatial import distance as dist
import matplotlib.pyplot as plt


def getActSite(imname):
    """
    :param imname: full image name string
    :return: string -> string
    """
    index = imname.find('http', imname.find('http') + 1)
    return imname[index:imname.index('.')]


def getdate(image):
    s = []
    lastHttp = image.find('http', image.find('http') + 1)
    saw = 0
    for c in image:
        if c.isdigit():
            s.append(c)
        saw += 1
        if saw == lastHttp:
            break
    d = "".join(s)
    date = (d[0:4], d[4:6], d[6:8], d[8:10], d[10:12], d[12:])
    return date


'''
HISTCMP_BHATTACHARYYA = 3
HISTCMP_CHISQR = 1

HISTCMP_CHISQR_ALT = 4

HISTCMP_CORREL = 0
HISTCMP_HELLINGER = 3
HISTCMP_INTERSECT = 2

HISTCMP_KL_DIV = 5
'''


def chi2_distance(histA, histB, eps=1e-10):
    d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                      for (a, b) in zip(histA, histB)])
    return d

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

class HistComp:
    def __init__(self, imlist, path):
        self.imlist = imlist
        self.path = path
        self.methods = {'random': MethodIms('random'), 'temporalInterval': MethodIms('temporalInterval'),
                        'alSum': MethodIms('alSum'), 'interval': MethodIms('interval')}
        self.cvims = {}
        self.hists3d = {}
        self.histsplit = {}
        for file in [f for f in listdir(path) if isfile(join(path, f))]:
            index = file.index('_')
            m = file[0:index]
            self.methods.get(m).addim(file)

def main():
    print("hello")

    imageName = "temporalInterval_httpwebarchiveorgweb20150924095627httpwwweggsbythebaycom.png"
    impath = "/home/john/wsdlims/"
    methods = {'random': MethodIms('random',impath), 'temporalInterval': MethodIms('temporalInterval',impath),
               'alSum': MethodIms('alSum',impath), 'interval': MethodIms('interval',impath)}

    hist_comp = (("Correlation", cv2.HISTCMP_CORREL),
                 ("Chi-Squared", cv2.HISTCMP_CHISQR),
                 ("Intersection", cv2.HISTCMP_INTERSECT),
                 ("Hellinger", cv2.HISTCMP_BHATTACHARYYA),
                 ("Kullback-Leibler divergence", cv2.HISTCMP_KL_DIV))

    files = [f for f in listdir(impath) if isfile(join(impath, f))]

    cvims = {}
    hists = {}
    histsplit = {}

    for item in files:
        index = item.index('_')
        m = item[0:index]
        methods.get(m).addim(item)

    alsum = methods['alSum']

    alsum.calc_all_hists()




    '''

    alsum.sort('httpbabeaboutiquecom')
    imlist = alsum['httpbabeaboutiquecom']

    base = imlist[3]


    for im in imlist.images:
        rim = cv2.imread(impath + im.image)
        cvims[im.id] = cv2.cvtColor(rim,cv2.COLOR_BGR2RGB)
        imHist = cv2.calcHist([rim], [0, 1, 2], None, [8, 8, 8],
                              [0, 256, 0, 256, 0, 256])
        imHist = cv2.normalize(imHist, imHist).flatten()
        hists[im.id] = imHist

    for mname, m in hist_comp:
        results = {}
        revese = False
        if mname in ("Correlation", "Intersection"):
            revese = True
        for im, hist in hists.items():
            d = cv2.compareHist(hists[base.id], hist, m)
            results[im] = d
        results = sorted([(v, k) for (k, v) in results.items()], reverse=revese)
        fig = plt.figure("Query")
        ax = fig.add_subplot(1, 1, 1)
        ax.imshow(cvims[base.id])
        plt.axis("off")

        fig = plt.figure("Results: %s " % mname + base.site)
        fig.suptitle(mname, fontsize=10)
        for i, (v, k) in enumerate(results):
            ax = fig.add_subplot(1, len(imlist), i + 1)
            ax.set_title("%.1f" % v)
            plt.imshow(cvims[k])
            plt.axis("off")
    plt.show()


'''

'''
for im in imlist:
    print(im, " ", im.year, " ", im.month, " ", im.day)
    image = cv2.imread(impath + im.image)
    cvims[im.image] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],
                        [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist).flatten()
    hists[im.image] = hist
    print(im, " ", im.image)

for compname, compmeth in hist_comp:
    results = {}
    reverse = False

    if compname in ("Correlation", "Intersection"):
        reverse = True

    for im, hist in hists.items():
        d = cv2.compareHist()
'''

'''
print("  ")
for k, v in methods.items():
    print(k, " ", v.methodName," ",v.totalsize)
    for imm, imlist  in v.items():
        print(imm,len(imlist))

        for imm in imlist:
            img = cv2.imread(impath+"/"+imm.image)
            hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
            plt.imshow(hist,interpolation = 'nearest')
            plt.show()

            cv2.imshow('image',img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            break
            print(imm," ",imm.date)
'''

if __name__ == "__main__":
    main()

'''
imdic = defaultdict(list)
for item in files:
        index = item.index('_')
        m = item[0:index]
        methods.get(m).addim(item)
        imdic[m].append(item)

 print("  ")
    for k, v in imdic.items():
        print(k, " ", len(v))
for item in files:
        for m in methods:
            if m in item:
                imdic[m].append(item)

    for k in imdic.keys():
        methList = imdic[k]
        print(k," ",len(methList))
'''
