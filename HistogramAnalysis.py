from collections import defaultdict

from MethodComposites import MethodCompThums,CompositeOnly
from util import get_files,check_if_goodURI,get_and_process_thumbs


def thumbThumbAnalysis(alSum, m, m2):
    print("alSum vs %s" % m.methodName)
    with open("alSumVS%s_onetoone.csv" % m.methodName, "w+") as out:
        out.write("site,average\n")
        for (asite, athumbcomp), (msite, mthumbcomp) in zip(sorted(alSum.items(), key=lambda x: x[0]),
                                                            sorted(m.items(), key=lambda x: x[0])):
            print(asite, msite)
            athumbcomp.compareDates_vsOther_oneTOone(mthumbcomp, out=out)

    print("alSum vs %s" % m2.methodName)
    with open("alSumVS%s_onetoone.csv" % m2.methodName, "w+") as out:
        out.write("site,average\n")
        for (asite, athumbcomp), (msite, mthumbcomp) in zip(sorted(alSum.items(), key=lambda x: x[0]),
                                                            sorted(m2.items(), key=lambda x: x[0])):
            print(asite, msite)
            athumbcomp.compareDates_vsOther_oneTOone(mthumbcomp, out=out)


def temporalPairs(alsum,random,ti):
        alsum.calc_comp_hist_date()
        random.calc_comp_hist_date()
        ti.calc_comp_hist_date()
        with open("temporalPairs.csv","w+") as out:
            out.write("site,alsum,random,aVrDif,temporal,aVtDiff\n")
            for ((asite,acompt),(rsite,rcompt)),(tsite,tcompt) in \
                zip(zip(alsum.sorted_items(),random.sorted_items()),ti.sorted_items()):
                sout = "%s,%f,%f,%f,%f,%f\n"%(asite,acompt.average,rcompt.average,(acompt.average-rcompt.average),tcompt.average,(acompt.average-tcompt.average))
                out.write(sout)
                print(sout)


def composite_only_histogram(method_composites,path):
    composit_analysis = CompositeOnly(path,method_composites)
    with open("compositeToCompositeUnNormal.csv","w+") as out:
        out.write("site,alsumRandomSim,alsumTemporalSim\n")
        composit_analysis.do_comparison(out)


if __name__ == "__main__":
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    goodUris = []

    with open("gooduris_20160225.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            goodUris.append(uri)

    compisits = get_files(compath, lambda f: "allTheSame" not in f and check_if_goodURI(f, goodUris) and
                                             "interval" not in f)
    method_composites = defaultdict(dict)

    for comp in sorted(compisits):
        site = comp[comp.find("_") + 1:comp.rfind("_")]
        method_composites[comp[:comp.index("_")]][site] = comp

    composite_only_histogram(method_composites,compath)


    # files = get_and_process_thumbs(impath, method_composites, goodUris)
    # print(type(files))
    #
    # # print(method_composites)
    # impath += "/"
    #
    # methods = {'random': MethodCompThums('random', impath, files["random"]),
    #            'temporalInterval': MethodCompThums('temporalInterval', impath, files["temporalInterval"]),
    #            'alSum': MethodCompThums('alSum', impath, files["alSum"])}
    #
    # # thumbThumbAnalysis(methods['alSum'], methods['random'], methods['temporalInterval'])
    # temporalPairs(methods['alSum'], methods['random'], methods['temporalInterval'])