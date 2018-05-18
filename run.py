#!/usr/bin/python

import visual
import pagerank

if __name__ == "__main__":
    P=2
    Q=1
    cacheSize=1
    memorySize=1

    pagerank=pagerank.PageRank(P,Q,'input')
    pagerank.preprocess()

    GV=visual.GV(pagerank.getV(),cacheSize,memorySize,P,Q)

    #pagerank.do_pagerank(GV)
    #added by luxu, run pagerank per grid
    for i in range(100):
        pagerank.do_pagerank_per_grid(GV)
