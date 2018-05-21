#!/usr/bin/python

import visual
import pagerank

filename = 'input'

if __name__ == "__main__":
    P=32
    Q=8
    cacheSize=8
    memorySize=16

    inputfile = open(filename, "r")
    line = inputfile.readline()
    sizeV = map(int, line.split())[0]
    inputfile.close()
    GV = visual.GV(sizeV,cacheSize,memorySize,P,Q)

    pagerank=pagerank.PageRank(P,Q,filename,GV,cacheSize,memorySize)
    pagerank.preprocess()
    pagerank.do_print()

    # pagerank.do_pagerank(GV)
    # Change the 1st parameter of the following function to "next step". DO NOT delete lambda
    GV.setButton(lambda: pagerank.do_pagerank_per_grid(GV), lambda: pagerank.do_pagerank_per_grid_continue(GV))

    #pagerank.do_pagerank(GV)
    #added by luxu, run pagerank per grid
    #for i in range(100):
    #    pagerank.do_pagerank_per_grid(GV)
    
    GV.draw()
