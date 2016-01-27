import argparse
import timeit
from collections import defaultdict
from os import listdir
from os.path import isfile, join
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from MethodImages import MethodIms, AllMethods, Why


import csv
from collections import Counter


def getMethod(compstr):
    return compstr[:compstr.find("_")]


def getSite(comp):
    return comp[comp.find("_") + 1:comp.rfind("_")]


def getComp(compstring: str):
    comp = compstring[compstring.rfind("/") + 1:]
    return comp


class Result:
    def __init__(self):
        # comp = getComp(base)
        # self.method = getMethod(comp)
        self.comp_method = {}  # type: dic
        # self.count(base)

    def count(self, tocount):
        # print(tocount)
        stripped = getComp(tocount)
        method = getMethod(stripped)
        site = getSite(stripped)
        if self.comp_method.get(site) is None:
            # print("first time seeing ",method)
            self.comp_method[site] = Counter()
            self.comp_method[site][method] += 1
        else:
            # print(self.comp_method)
            self.comp_method[site][method] += 1

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


def all_same():
    ap = argparse.ArgumentParser()
    ap.add_argument("-ip", required=True, help="Path to the images")
    ap.add_argument("-cp", required=False, help="Path to the images")
    ap.add_argument("-m", required=False, help="which method todo")
    ap.add_argument("-type", required=False, help="which histogram type desired {3d: rbg, hsv: hue saturation value}")
    args = vars(ap.parse_args())

    print("hello")

    impath = args["ip"]
    compath = args["cp"]
    why = Why("/home/john/composites_for_report", impath, compath)
    why.show()


def do_comp():
    ret = Result()
    with open('/home/john/Downloads/Batch_2114373_batch_results.csv', 'r') as o:
        reader = csv.DictReader(o)

        for item in reader:
            if "image1" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image1src'])
            elif "image2" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image2src'])
            elif "image3" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image3src'])
            elif "image4" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image4src'])
            elif "image5" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image5src'])
            elif "image6" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image6src'])
            elif "image7" in item['Answer.selectedThumbnail1']:
                ret.count(item['Input.image7src'])
            else:
                ret.count(item['Input.image8src'])

            if "image1" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image1src'])
            elif "image2" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image2src'])
            elif "image3" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image3src'])
            elif "image4" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image4src'])
            elif "image5" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image5src'])
            elif "image6" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image6src'])
            elif "image7" in item['Answer.selectedThumbnail2']:
                ret.count(item['Input.image7src'])
            else:
                ret.count(item['Input.image8src'])

            if "image1" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image1src'])
            elif "image2" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image2src'])
            elif "image3" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image3src'])
            elif "image4" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image4src'])
            elif "image5" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image5src'])
            elif "image6" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image6src'])
            elif "image7" in item['Answer.selectedThumbnail3']:
                ret.count(item['Input.image7src'])
            else:
                ret.count(item['Input.image8src'])

            if "image1" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image1src'])
            elif "image2" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image2src'])
            elif "image3" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image3src'])
            elif "image4" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image4src'])
            elif "image5" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image5src'])
            elif "image6" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image6src'])
            elif "image7" in item['Answer.selectedThumbnail4']:
                ret.count(item['Input.image7src'])
            else:
                ret.count(item['Input.image8src'])

    # ap = argparse.ArgumentParser()
    # ap.add_argument("-ip", required=True, help="Path to the images")
    # ap.add_argument("-cp", required=False, help="Path to the images")
    # ap.add_argument("-m", required=False, help="which method todo")
    # ap.add_argument("-type", required=False, help="which histogram type desired {3d: rbg, hsv: hue saturation value}")
    # args = vars(ap.parse_args())
    #
    # print("hello")

    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    print(compath)

    files = get_files(impath, test=None)
    compisits = get_files(compath, lambda f: "allTheSame" not in f)

    method_composites = defaultdict(dict)

    for comp in compisits:
        site = comp[comp.find("_") + 1:comp.rfind("_")]
        if len(site) != 3:
            method_composites[comp[:comp.index("_")]][site] = comp

    impath += "/"
    methods = {'random': MethodIms('random', impath, method_composites["random"]),
               'temporalInterval': MethodIms('temporalInterval', impath, method_composites["temporalInterval"]),
               'alSum': MethodIms('alSum', impath, method_composites["alSum"]),
               'interval': MethodIms('interval', impath, method_composites["interval"])}

    for item in files:
        index = item.index('_')
        m = item[0:index]
        methods.get(m).add_image(item)

    # with open('method256v2.txt','w+') as out:
    # start = time.time()
    # s_t = timeit.default_timer()

    level = {}


    # level[]
    #
    # for m, method in methods.items():
    #     print("plotting %s"%m)
    #     method.calc_comp_mapFigs()
    # method.calc_all_hists()
    # method.do_it()
    # out.write(m+"\n")
    # method.sortBySimularity()
    # method.calc_comp_hist_date(impath,compath,out)
    # method.getMethodAv(out)
    # method.showPerComp(out)
    # method.plot_dates()
    # method.do_it()
    # method.plot_dates()

    alSum = methods.get('alSum')

    for site, mcount in sorted(ret.comp_method.items(), key=lambda x: x[0]):
            mfind = max(mcount.items(), key=lambda x: x[1])

            it = "turkers choose: " + mfind[0]
            list = []
            for method, count in sorted(mcount.items(),key=lambda x:x[1],reverse=True):
                list.append(method+"-"+str(count))
            joined = ', '.join(list)
            level[site] = it+": "+joined

    for site, group in alSum.imageGroups.items():

        if group.valid_for_comp() and group.has_composite():
            print(site)
            try:
                levelString = level[site]
            except KeyError:
                levelString = None
            asumfigs = group.other(levelString)
            print("got asum site figs")
            interval = methods.get('interval')
            savedir = "/home/john/PycharmProjects/CompareHistograms/plots/" + site + \
                      "_alSumBD.pdf"
            pdf = PdfPages(savedir)
            figs = []
            for fig in asumfigs:
                pdf.savefig(fig)
                figs.append(fig)

            group.clean_up2()


            try:
                isite = interval[site].other()
            except ZeroDivisionError:
                 print("there was an div zero exception for interval")
                 for fig in figs:
                    plt.close(fig)
                 pdf.close()
                 continue
            except KeyError:
                for fig in figs:
                    plt.close(fig)
                pdf.close()
                continue

            for fig in isite:
                pdf.savefig(fig)
                figs.append(fig)
            print("got interval site figs")
            interval[site].clean_up2()


            try:
                 tisite = methods.get('temporalInterval')[site].other()
            except ZeroDivisionError:
                 print("there was an div zero exception for temporalInterval")
                 for fig in figs:
                    plt.close(fig)
                 pdf.close()
                 continue
            except KeyError:
                for fig in figs:
                    plt.close(fig)
                pdf.close()
                continue



            methods.get('random')[site].clean_up2()
            print("got random site figs")

            for fig in tisite:
                pdf.savefig(fig)
                figs.append(fig)
            methods.get('temporalInterval')[site].clean_up2()
            print("got temporal site figs")
            pdf.close()
            print("done generating pdf for site")

            for fig in figs:
                plt.close(fig)
            del figs
            del pdf


#
# alSum.calc_comp_mapFigs()
# for site, v in alSum.site_figs.items():
#     interval = methods.get('interval')
#     savedir = "/home/john/PycharmProjects/CompareHistograms/plots/" + site + \
#               "_bd.pdf"
#     pdf = PdfPages(savedir)
#     figs = []
#     for fig in v:
#         pdf.savefig(fig)
#         figs.append(fig)
#
#     isite = interval[site].other()
#     for fig in isite:
#         pdf.savefig(fig)
#         figs.append(fig)
#
#     rsite = methods.get('random')[site].other()
#     tisite = methods.get('temporalInterval')[site].other()
#
#     for fig in rsite:
#         pdf.savefig(fig)
#         figs.append(fig)
#
#     for fig in tisite:
#         pdf.savefig(fig)
#         figs.append(fig)
#     pdf.close()
#
#     for fig in figs:
#         plt.close(fig)




# end = time.time()
# e_t = timeit.default_timer()
#
# print("total time taken for 256 is %f"%(end-start))

# allsameFind = []
# f1 = "contigogobmx"
# f2 = "contigogobmx_200"
#
# alsum = methods['alSum']

# with open('method64v2binAv.txt','w+') as out:
#
#     for m, method in methods.items():
#             print("plotting %s"%m)
#             # method.do_it()
#             # out.write(m+"\n")
#             method.calc_comp_hist_date()
#             # method.calc_comp_hist_date(impath,compath,out)
#             method.getMethodAv(out)
#             # method.showPerComp(out)
#             # method.plot_dates()
#             # method.do_it()
#             # method.plot_dates()




# f2m.group_cvread()
# f2m.show()

# print(len(allsameFind))
#
# for found in allsameFind:
#     print(found)
#     found.group_cvread()
#     found.show()

'''

 for m, method in methods.items():
    print("plotting %s"%m)
    method.calc_comp_hists()
    method.plot()

alSum = methods['alSum']

alSum.calc_comp_hists()
alSum.plot()

it = alSum.imageGroups['alitoloeeiblogfacom']
it.group_cvread()
it.compare_hists()
it.plot()
alSum.calc_comp_hists()

for k, v in alSum.imageGroupsCalulated.items():
    for image in v.images:
        for kk, vv in image.hist_ret.items():
            vv.plot()
            break
        break
    break
'''

'''
for mname, method in methods.items():
    print("calculating histograms and comparing for %s" % mname)
    method.calc_comp_hists()
    print("writing results to file %s.json" % mname)
    with open("%s.json" % mname, "w+") as f:
        f.write(method.to_json())
        f.close()
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-ip", required=True, help="Path to the images")
    ap.add_argument("-cp", required=False, help="Path to the images")
    ap.add_argument("-m", required=False, help="which method do")
    args = vars(ap.parse_args())

    print("hello")

    impath = args["ip"]
    compath = args["cp"]

    all = AllMethods(impath, compath)

    all.pull_images()
    all.calc_comp_hists()

    with open("allrets4.json", "w+") as f:
        f.write(all.to_json())
        f.close()


if __name__ == "__main__":
    do_comp()
    # print(timeit.timeit('do_comp()',"from imcomp import do_comp", number=1))
    # ret = timeit.Timer(setup).timeit(1)
    # print(ret)
# do_comp()
# all_same()
