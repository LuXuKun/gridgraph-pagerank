#!/usr/bin/python

import visual
import pagerank

filename = 'input'

if __name__ == "__main__":
    P=2
    Q=1
    cacheSize=1
    memorySize=1

    inputfile = open(filename, "r")
    line = inputfile.readline()
    sizeV = map(int, line.split())[0]
    inputfile.close()
    GV = visual.GV(sizeV,cacheSize,memorySize,P,Q)

    pagerank=pagerank.PageRank(P,Q,filename,GV)
    pagerank.preprocess()

    # pagerank.do_pagerank(GV)
    # Change the 1st parameter of the following function to "next step". DO NOT delete lambda
    GV.setButton(lambda: 1, lambda: pagerank.do_pagerank(GV))

    GV.draw()
