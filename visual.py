#!/usr/bin/python
from abc import ABCMeta, abstractmethod


# visualization module consists of 4 parts: grid, cache, memory and disk

class GV_interface:
    __metaclass__ = ABCMeta

    # sizeV indicates total size of input vertices
    # cacheSize & memorySize you know what they mean 
    # P & Q follow the defination in paper
    @abstractmethod
    def __init__(self, sizeV, cacheSize, memorySize, P, Q):
        pass

    # highlight a region in grid. v0 and v1 indicate the source vertice 
    # and destination vertice of an edge
    @abstractmethod
    def highlight(self, v0, v1):
        pass

    # cancel hightstatus of grid
    @abstractmethod
    def unhighlight(self):
        pass

    # read vertice v. will highlight the vertice in cache, memory or disk
    # Retrun: 0 in cache, 1 in memory, 2 in disk
    @abstractmethod
    def read(self, v):
        pass

    # write vertice v. will highlight the vertice in cache, memory or disk
    # Retrun: 0 in cache, 1 in memory, 2 in disk
    @abstractmethod
    def write(self, v):
        pass

    # set the beginning address of cache to v
    @abstractmethod
    def setCacheBegin(self, v):
        pass

    # same as setCacheBegin but for memory
    @abstractmethod
    def setMemoryBegin(self, v):
        pass

class GV(GV_interface):
    def __init__(self, sizeV, cacheSize, memorySize, P, Q):
        print "init GV"
    def highlight(self, v0, v1):
        print "highlight"
    def unhighlight(self):
        print "unhighlight"
    def read(self, v):
        print "read"
    def write(self, v):
        print "write"
    def setCacheBegin(self, v):
        print "setCacheBegin"
    def setMemoryBegin(self, v):
        print "setMemoryBegin"
