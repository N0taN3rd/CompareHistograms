import re
import urllib.request

import dateutil.parser
import requests
import json
import time

tokenizer = re.compile('(<[^>]+>|[a-zA-Z]+="[^"]*"|[;,])\\s*')

from util import get_and_process_thumbs,get_files,check_if_goodURI

class TimeMap:
    def __init__(self, timemap_uri):
        self.original = None
        self.timebundle = None
        self.timegate = None
        self.timemap = None
        self.first_memento = None
        self.last_memento = None
        self.mementos = {}
        self.__tokens = TimeMapTokenizer("http://web.archive.org/web/timemap/link/%s" % timemap_uri)
        link = self.get_next_link()
        while link is not None:
            if link[0] == 'memento':
                self.mementos[link[1]] = link[2]
            elif link[0] == 'original':
                self.original = link[2] if link is not None else None
            elif link[0] == 'timebundle':
                self.timebundle = link[2] if link is not None else None
            elif link[0] == 'timegate':
                self.timegate = link[2] if link is not None else None
            elif link[0] == 'timemap':
                self.timemap = link[2] if link is not None else None
            elif link[0] == 'first memento':
                self.mementos[link[1]] = link[2]
                self.first_memento = link[1] if link is not None else None
            elif link[0] == 'last memento':
                self.mementos[link[1]] = link[2]
                self.last_memento = link[1] if link is not None else None
            link = self.get_next_link()

    def get_next_link(self):
        uri = None
        datetime = None
        rel = None
        resource_type = None
        for token in self.__tokens:
            print(token)
            if token[0] == '<':
                uri = token[1:-1]
            elif token[:9] == 'datetime=':
                datetime = token[10:-1]
            elif token[:4] == 'rel=':
                rel = token[5:-1]
            elif token[:5] == 'type=':
                resource_type = token[6:-1]
            elif token == ';':
                None
            elif token == ',':
                return (rel, dateutil.parser.parse(datetime)
                if datetime is not None else None,
                        uri, resource_type)
            else:
                raise Exception('Unexpected timemap token', token)
        if uri is None:
            return None
        else:
            return (rel, dateutil.parser.parse(datetime)
            if datetime is not None else None,
                    uri, resource_type)

    def __getitem__(self, key):
        return self.mementos[key]


class TimeMapTokenizer:
    def __init__(self, timemap_uri):
        self.http = urllib.request.urlopen(timemap_uri)
        # self._tmfile = requests.get(timemap_uri).iter_lines()
        self.r = requests.get(timemap_uri)
        self._tmfile = self.r.iter_lines()
        # print(self.r.text)
        self._tokens = []
        self.lines = []
        self.size = 0
        self.cur = 0
        self.doIt()

    def doIt(self):
        for line in self._tmfile:
            print(line)
            self.lines.append(line.decode("utf-8"))
        self.size = len(self.lines)

    def __next__(self):
        if len(self._tokens) == 0:
            if self.cur == self.size:
                raise StopIteration
            line = self.lines[self.cur]
            self.cur += 1
            if self.cur == self.size:
                raise StopIteration
            self._tokens = tokenizer.findall(line)
        return self._tokens.pop(0)

    def __iter__(self):
        return self


def filterASI(f):
    return not "allTheSame_" in f and not "interval_" in f


if __name__ == '__main__':
    impath = "/home/john/wsdlims_ripped/ECIR2016TurkData/screenshots"  # args["ip"]
    compath = "/home/john/wsdlims_ripped/ECIR2016TurkData/composites"  # args["cp"]
    goodUris = []
    origuris = []
    with open("gooduris_20160225.txt", "r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
            goodUris.append(uri)

    with open("origuris.txt","r") as read:
        for uri in map(lambda line: line.rstrip("\n"), read):
           origuris.append(uri)



    for gu in sorted(goodUris):
        for ou in origuris:
           if "%s"%gu in ou:
               print(ou)
