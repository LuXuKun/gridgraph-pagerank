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
cacheLeft = gridLeft + gridLength + 150
memoryUp = cacheUp + 200
memoryLeft = cacheLeft
diskUp = memoryUp + 200
diskLeft = memoryLeft
CMWidth = 200
DWidth = CMWidth * 2
textInter = 100

cacheLeft_1 = cacheLeft + CMWidth + 10
memoryLeft_1 = memoryLeft + CMWidth + 10

class GV(GV_interface):
    def __init__(self, _sizeV, _cacheSize, _memorySize, P, Q):
        global sizeV, cacheSize, memorySize, PSquareNum, QSquareNum, PSquareLength
        global QSquareLength, CMDBlockWidth, CMBlockNum, DBlockNum, cacheBeginR, memoryBeginR, cacheBeginW, memoryBeginW
        global cacheReadMiss, cacheWriteMiss, memoryReadMiss, memoryWriteMiss
        sizeV = _sizeV
        cacheSize = _cacheSize
        memorySize = _memorySize
        PSquareNum = P
        QSquareNum = Q
        PSquareLength = 1. * gridLength / PSquareNum
        QSquareLength = 1. * gridLength / QSquareNum
        CMDBlockWidth = min(min(1. * CMWidth / cacheSize, PSquareLength), 50)
        CMBlockNum = CMWidth / CMDBlockWidth
        DBlockNum = DWidth / CMDBlockWidth

        cacheBeginR = 0
        cacheBeginW = 0
        memoryBeginR = 0
        memoryBeginW = 0
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
        self.cv.create_text(cacheLeft - 50, cacheUp + 10, text="cache")
        for i in range(0, cacheSize):
            self.cv.create_rectangle(cacheLeft + i * CMDBlockWidth, cacheUp,
                                     cacheLeft + (i + 1) * CMDBlockWidth, cacheUp + CMDBlockWidth)
            self.cv.create_text(cacheLeft + i * CMDBlockWidth + CMDBlockWidth / 2,
                                cacheUp + CMDBlockWidth / 2, text=str(i), tags=("cachetext_0"))  
            self.cv.create_rectangle(cacheLeft_1 + i * CMDBlockWidth, cacheUp,
                                     cacheLeft_1 + (i + 1) * CMDBlockWidth, cacheUp + CMDBlockWidth)
            self.cv.create_text(cacheLeft_1 + i * CMDBlockWidth + CMDBlockWidth / 2,
                                cacheUp + CMDBlockWidth / 2, text=str(i), tags=("cachetext_1"))        

        # draw memory
        self.cv.create_text(memoryLeft - 50, memoryUp + 10, text="memory")
        for i in range(0, memorySize):
            self.cv.create_rectangle(memoryLeft + i % CMBlockNum * CMDBlockWidth,
                                     memoryUp + math.floor(i / CMBlockNum) * CMDBlockWidth,
                                     memoryLeft + (i % CMBlockNum + 1) * CMDBlockWidth, 
                                     memoryUp + math.floor(i / CMBlockNum + 1) * CMDBlockWidth)
            self.cv.create_text(memoryLeft + i % CMBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                memoryUp + math.floor(i / CMBlockNum) * CMDBlockWidth + CMDBlockWidth / 2,
                                text=str(i), tags=("memorytext_0"))
            self.cv.create_rectangle(memoryLeft_1 + i % CMBlockNum * CMDBlockWidth,
                                     memoryUp + math.floor(i / CMBlockNum) * CMDBlockWidth,
                                     memoryLeft_1 + (i % CMBlockNum+ 1) * CMDBlockWidth, 
                                     memoryUp + math.floor(i / CMBlockNum + 1) * CMDBlockWidth)
            self.cv.create_text(memoryLeft_1 + i % CMBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                memoryUp + math.floor(i / CMBlockNum) * CMDBlockWidth + CMDBlockWidth / 2,
                                text=str(i), tags=("memorytext_1"))                

        # draw disk
        self.cv.create_text(diskLeft - 50, diskUp + 10, text="disk")
        for i in range(0, sizeV):
            self.cv.create_rectangle(diskLeft + i % DBlockNum * CMDBlockWidth,
                                     diskUp + math.floor(i / DBlockNum) * CMDBlockWidth,
                                     diskLeft + (i % DBlockNum + 1) * CMDBlockWidth, 
                                     diskUp + math.floor(i / DBlockNum + 1) * CMDBlockWidth)
            self.cv.create_text(diskLeft + i % DBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                diskUp + math.floor(i / DBlockNum) * CMDBlockWidth + CMDBlockWidth / 2, text=str(i))        

        # highlight grid
        self.cv.create_rectangle(0, 0, PSquareLength, PSquareLength, outline='red',
                                 width=0, tags=("highlight"))

        # highlight cache, memory, disk
        self.cv.create_rectangle(0, 0, CMDBlockWidth, CMDBlockWidth, outline='red',
                                 width=0, tags=("CMDhighlight"))

        font_size = 15
        # cache miss
        self.cv.create_text(cacheLeft + 60, cacheUp + CMDBlockWidth + 50,
                            text="read miss: " + str(0), font=("", font_size), tags=("crm"))
        self.cv.create_text(cacheLeft + 270, cacheUp + CMDBlockWidth + 50,
                            text="write miss: " + str(0), font=("", font_size), tags=("cwm"))

        # memory miss
        self.cv.create_text(memoryLeft + 60,
                            memoryUp + math.ceil(1. * memorySize / CMBlockNum) * CMDBlockWidth + 50,
                            text="read miss: " + str(0), font=("", font_size), tags=("mrm"))
        self.cv.create_text(memoryLeft + 270,
                            memoryUp + math.ceil(1. * memorySize / CMBlockNum) * CMDBlockWidth + 50,
                            text="write miss: " + str(0), font=("", font_size), tags=("mwm"))

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
        print "readCache {}".format(v)
        self.highlightCache(v - cacheBeginR)

    def writeCache(self, v):
        print "writeCache {}".format(v)
        self.highlightCache(v - cacheBeginW)

    def readMemory(self, curCacheBegin, v):
        print "readMemory {} {}".format(curCacheBegin, v)
        self.updateCacheReadMiss()
        self.setCacheBegin(curCacheBegin, 0)
        self.highlightMemory(v - memoryBeginR)

    def writeMemory(self, curCacheBegin, v):
        print "writeMemory {} {}".format(curCacheBegin, v)
        self.updateCacheWriteMiss()
        self.setCacheBegin(curCacheBegin, 1)
        self.highlightMemory(v - memoryBeginW)

    def readDisk(self, curCacheBegin, curMemoryBegin, v):
        print "readDisk {} {} {}".format(curCacheBegin, curMemoryBegin, v)
        self.updateCacheReadMiss()
        self.updateMemoryReadMiss()
        self.setCacheBegin(curCacheBegin, 0)
        self.setMemoryBegin(curMemoryBegin, 0)
        self.highlightDisk(v)

    def writeDisk(self, curCacheBegin, curMemoryBegin, v):
        print "writeDisk {} {} {}".format(curCacheBegin, curMemoryBegin, v)
        self.updateCacheWriteMiss()
        self.updateMemoryWriteMiss()
        self.setCacheBegin(curCacheBegin, 1)
        self.setMemoryBegin(curMemoryBegin, 1)
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
        self.cv.itemconfig('mwm', text="write miss: " + str(memoryWriteMiss))

    def setCacheBegin(self, v, isWrite):
        global cacheBeginR, cacheBeginW
        if isWrite:
            cacheBeginW = v
        else:
            cacheBeginR = v
        tag = "cachetext_1" if isWrite else "cachetext_0"
        left = cacheLeft_1 if isWrite else cacheLeft
        self.cv.delete(tag)
        for i in range(0, cacheSize):
            self.cv.create_text(left + i * CMDBlockWidth + CMDBlockWidth / 2,
                                cacheUp + CMDBlockWidth / 2, text=str(i + v), tags=(tag))
    
    def setMemoryBegin(self, v, isWrite):
        global memoryBeginR, memoryBeginW
        if isWrite:
            memoryBeginW = v
        else:            
            memoryBeginR = v
        tag = "memorytext_1" if isWrite else "memorytext_0"
        left = memoryLeft_1 if isWrite else memoryLeft
        self.cv.delete(tag)
        for i in range(0, memorySize):
            self.cv.create_text(left + i % CMBlockNum * CMDBlockWidth + CMDBlockWidth / 2,
                                memoryUp + math.floor(i / CMBlockNum) * CMDBlockWidth + CMDBlockWidth / 2,
                                text=str(i + v), tags=(tag))     

    def highlightCache(self, index):
        print "highlightCache {}".format(index)
        self.highlightCMD(cacheLeft + index % CMBlockNum * CMDBlockWidth,
                          cacheUp + math.floor(index / CMBlockNum) * CMDBlockWidth)
        
    def highlightMemory(self, index):
        print "highlightMemory {}".format(index)
        self.highlightCMD(memoryLeft + index % CMBlockNum * CMDBlockWidth,
                          memoryUp + math.floor(index / CMBlockNum) * CMDBlockWidth)
        
    def highlightDisk(self, v):
        print "highlightDisk {}".format(v)
        self.highlightCMD(diskLeft + v % DBlockNum * CMDBlockWidth,
                          diskUp + math.floor(v / DBlockNum) * CMDBlockWidth)

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
        # self.draw()

