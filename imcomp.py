import argparse
import timeit
from collections import defaultdict
from os import listdir
from os.path import isfile, join

from MethodImages import MethodIms, AllMethods, Why


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
    for m, method in methods.items():
        print("plotting %s"%m)
        # method.do_it()
        # out.write(m+"\n")
        method.calc_comp_hist_date()
        method.sortBySimularity()
        # method.calc_comp_hist_date(impath,compath,out)
        # method.getMethodAv(out)
        # method.showPerComp(out)
        # method.plot_dates()
        # method.do_it()
        # method.plot_dates()
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
