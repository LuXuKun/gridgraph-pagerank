#!/usr/bin/python
from abc import ABCMeta, abstractmethod
from Tkinter import *
import threading
import warnings
import math


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

    # pass two functions for next and continue button
    @abstractmethod
    def setButton(self, nextFunc, continueFunc):
        pass

    @abstractmethod
    def readCache(self, v):
        pass

    @abstractmethod
    def writeCache(self, v):
        pass

    @abstractmethod
    def readMemory(self, curCacheBegin, v):
        pass

    @abstractmethod
    def writeMemory(self, curCacheBegin, v):
        pass

    @abstractmethod
    def readDisk(self, curCacheBegin, curMemoryBegin, v):
        pass

    @abstractmethod
    def writeDisk(self, curCacheBegin, curMemoryBegin, v):
        pass

width = 1100
height = 700

gridUp = 50
gridLeft = 50
gridLength = 400

cacheUp = gridUp 
cacheLeft = gridLeft + gridLength + 50
memoryUp = cacheUp + 200
memoryLeft = cacheLeft
diskUp = memoryUp + 200
diskLeft = memoryLeft
CMDWidth = 400
textInter = 100

class GV(GV_interface):
    def __init__(self, _sizeV, _cacheSize, _memorySize, P, Q):
        global sizeV, cacheSize, memorySize, PSquareNum, QSquareNum, PSquareLength
        global QSquareLength, CMDBlockWidth, CMDBlockNum, cacheBegin, memoryBegin
        global cacheReadMiss, cacheWriteMiss, memoryReadMiss, memoryWriteMiss
        sizeV = _sizeV
        cacheSize = _cacheSize
        memorySize = _memorySize
        PSquareNum = P
        QSquareNum = Q
        PSquareLength = gridLength / PSquareNum
        QSquareLength = gridLength / QSquareNum
        CMDBlockWidth = min(min(CMDWidth / cacheSize, PSquareLength), 50)
        CMDBlockNum = CMDWidth / CMDBlockWidth

        cacheBegin = 0
        memoryBegin = 0
        cacheReadMiss = 0
        cacheWriteMiss = 0
        memoryReadMiss = 0
        memoryWriteMiss = 0

        self.root = Tk()
        self.cv = Canvas(self.root,bg = 'white', width=width, height=height)

        # draw cache square
        for i in range(0, PSquareNum):
            for j in range(0, PSquareNum):
                self.cv.create_rectangle(gridLeft + j * PSquareLength, gridUp + i * PSquareLength,
                                         gridLeft + (j + 1) * PSquareLength,
                                         gridUp + (i + 1) * PSquareLength)

        # draw memory square
        for i in range(0, QSquareNum):
            for j in range(0, QSquareNum):
                self.cv.create_rectangle(gridLeft + j * QSquareLength, gridUp + i * QSquareLength,
                                         gridLeft + (j + 1) * QSquareLength,
                                         gridUp + (i + 1) * QSquareLength,
                                         width=5)
        
        # draw cache
        for i in range(0, cacheSize):
            self.cv.create_rectangle(cacheLeft + i * CMDBlockWidth, cacheUp,
                                     cacheLeft + (i + 1) * CMDBlockWidth, cacheUp + CMDBlockWidth)
            self.cv.create_text(cacheLeft + i * CMDBlockWidth + CMDBlockWidth / 2,
                                cacheUp + CMDBlockWidth / 2, text=str(i), tags=("cachetext"))        

        # draw memory
        for i in range(0, memorySize):
            self.cv.create_rectangle(memoryLeft + i % CMDBlockNum * CMDBlockWidth,
                                     memoryUp + i / CMDBlockNum * CMDBlockWidth,
                                     memoryLeft + (i % CMDBlockNum+ 1) * CMDBlockWidth, 
                                     memoryUp + (i / CMDBlockNum + 1) * CMDBlockWidth)
            self.cv.create_text(memoryLeft + i % CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                memoryUp + i / CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                text=str(i), tags=("memorytext"))                

        # draw disk
        for i in range(0, sizeV):
            self.cv.create_rectangle(diskLeft + i % CMDBlockNum * CMDBlockWidth,
                                     diskUp + i / CMDBlockNum * CMDBlockWidth,
                                     diskLeft + (i % CMDBlockNum + 1) * CMDBlockWidth, 
                                     diskUp + (i / CMDBlockNum + 1) * CMDBlockWidth)
            self.cv.create_text(diskLeft + i % CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                diskUp + i / CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2, text=str(i))        

        # highlight grid
        self.cv.create_rectangle(0, 0, PSquareLength, PSquareLength, outline='red',
                                 width=0, tags=("highlight"))

        # highlight cache, memory, disk
        self.cv.create_rectangle(0, 0, CMDBlockWidth, CMDBlockWidth, outline='red',
                                 width=0, tags=("CMDhighlight"))

        # cache miss
        self.cv.create_text(cacheLeft + 60, cacheUp + CMDBlockWidth + 50,
                            text="read miss: " + str(0), font=("", 20), tags=("crm"))
        self.cv.create_text(cacheLeft + 250, cacheUp + CMDBlockWidth + 50,
                            text="write miss: " + str(0), font=("", 20), tags=("cwm"))

        # memory miss
        self.cv.create_text(memoryLeft + 60,
                            memoryUp + math.ceil(1. * memorySize / CMDBlockNum) * CMDBlockWidth + 50,
                            text="read miss: " + str(0), font=("", 20), tags=("mrm"))
        self.cv.create_text(memoryLeft + 250,
                            memoryUp + math.ceil(1. * memorySize / CMDBlockNum) * CMDBlockWidth + 50,
                            text="write miss: " + str(0), font=("", 20), tags=("mwm"))

        # self.highlightCache(0)
        self.nextButton = Button(self.root, text ="next")
        self.nextButton.place(x=width - 300, y=height - 50)

        self.continueButton = Button(self.root, text ="continue")
        self.continueButton.place(x=width - 200, y=height - 50)

        self.cv.pack()
        # self.root.mainloop()


    def highlight(self, v0, v1):
        self.cv.coords('highlight',
                     gridLeft + int(1. * v1 / sizeV * PSquareNum) * PSquareLength,
                     gridUp + int(1. * v0 / sizeV * PSquareNum) * PSquareLength,
                     gridLeft + int(1. * v1 / sizeV * PSquareNum + 1) * PSquareLength,
                     gridUp + int(1. * v0 / sizeV * PSquareNum + 1) * PSquareLength)        
        self.cv.itemconfig('highlight', width=3)

    def unhighlight(self):
        self.cv.itemconfig('highlight', width=0)
        self.cv.itemconfig('CMDhighlight', width=0)
    
    def readCache(self, v):
        # print "readCache {}".format(v)
        self.highlightCache(v - cacheBegin)

    def writeCache(self, v):
        # print "writeCache {}".format(v)
        self.highlightCache(v - cacheBegin)

    def readMemory(self, curCacheBegin, v):
        # print "readMemory {} {}".format(curCacheBegin, v)
        self.updateCacheReadMiss()
        self.setCacheBegin(curCacheBegin)
        self.highlightMemory(v - memoryBegin)

    def writeMemory(self, curCacheBegin, v):
        # print "writeMemory {} {}".format(curCacheBegin, v)
        self.updateCacheWriteMiss()
        self.setCacheBegin(curCacheBegin)
        self.highlightMemory(v - memoryBegin)

    def readDisk(self, curCacheBegin, curMemoryBegin, v):
        # print "readDisk {} {} {}".format(curCacheBegin, curMemoryBegin, v)
        self.updateCacheReadMiss()
        self.updateMemoryReadMiss()
        self.setCacheBegin(curCacheBegin)
        self.setMemoryBegin(curMemoryBegin)
        self.highlightDisk(v)

    def writeDisk(self, curCacheBegin, curMemoryBegin, v):
        # print "writeDisk {} {} {}".format(curCacheBegin, curMemoryBegin, v)
        self.updateCacheWriteMiss()
        self.updateMemoryWriteMiss()
        self.setCacheBegin(curCacheBegin)
        self.setMemoryBegin(curMemoryBegin)
        self.highlightDisk(v)


    def updateCacheReadMiss(self):
        global cacheReadMiss
        cacheReadMiss += 1
        self.cv.itemconfig('crm', text="read miss: " + str(cacheReadMiss))

    def updateCacheWriteMiss(self):
        global cacheWriteMiss
        cacheWriteMiss += 1
        self.cv.itemconfig('cwm', text="write miss: " + str(cacheWriteMiss))

    def updateMemoryReadMiss(self):
        global memoryReadMiss
        memoryReadMiss += 1
        self.cv.itemconfig('mrm', text="read miss: " + str(memoryReadMiss))

    def updateMemoryWriteMiss(self):
        global memoryWriteMiss
        memoryWriteMiss += 1
        self.cv.itemconfig('mwm', text="read miss: " + str(memoryWriteMiss))

    def setCacheBegin(self, v):
        global cacheBegin
        cacheBegin = v
        self.cv.delete("cachetext")
        for i in range(0, cacheSize):
            self.cv.create_text(cacheLeft + i * CMDBlockWidth + CMDBlockWidth / 2,
                                cacheUp + CMDBlockWidth / 2, text=str(i + v), tags=("cachetext"))
    
    def setMemoryBegin(self, v):
        global memoryBegin
        memoryBegin = v
        self.cv.delete("memorytext")
        for i in range(0, memorySize):
            self.cv.create_text(memoryLeft + i % CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                memoryUp + i / CMDBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                text=str(i + v), tags=("memorytext"))     

    def highlightCache(self, index):
        # print "highlightCache {}".format(index)
        self.highlightCMD(cacheLeft + index % CMDBlockNum * CMDBlockWidth,
                          cacheUp + index / CMDBlockNum * CMDBlockWidth)
        
    def highlightMemory(self, index):
        # print "highlightMemory {}".format(index)
        self.highlightCMD(memoryLeft + index % CMDBlockNum * CMDBlockWidth,
                          memoryUp + index / CMDBlockNum * CMDBlockWidth)
        
    def highlightDisk(self, v):
        # print "highlightDisk {}".format(v)
        self.highlightCMD(diskLeft + v % CMDBlockNum * CMDBlockWidth,
                          diskUp + v / CMDBlockNum * CMDBlockWidth)

    def highlightCMD(self, x, y):
        self.cv.coords('CMDhighlight', x, y, x + CMDBlockWidth, y + CMDBlockWidth)        
        self.cv.itemconfig('CMDhighlight', width=3)

    def setButton(self, nextFunc, continueFunc):
        self.nextButton.configure(command = nextFunc)
        self.continueButton.configure(command = continueFunc)

    def draw(self):
        self.root.mainloop()

    def sleep(self, time, func):
        self.root.after(time, func)
        self.root.mainloop()

