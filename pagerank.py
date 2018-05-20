#!/usr/bin/python
import visual
import time

class PageRank:
    def __init__(self, P, Q, filename, GV, cacheSize, memSize):
        self.damping_factor=0.85
        self.max_iterations=200
        self.min_delta=0.00001
        self.Q=Q
        self.P=P
        self.filename=filename
        self.GV = GV
        self.V=0
        self.data=[]
        self.pr=[]
        self.deg=[]
        
        #added by luxu, used for run pagerank per grid
        self.converged=0
        self.iterations=0
        self.newpr=[]
        self.xQ=0
        self.yQ=0
        self.xP=0
        self.yP=0
        #end by luxu
        
        #HFQ begin
        self.write_disk_time = 0
        self.read_disk_time = 0
        self.write_mem_time = 0
        self.read_mem_time = 0
        # memory address - P(x2, y2) in Q (x1, y1) = x1 * Q + y1 + x2 * P + y2
        self.LLCbegin = 0
        self.LLCend = 0
        self.MEMbegin = 0
        self.MEMend = 0
        self.LLCSize = cacheSize
        self.MEMSize = memSize
        #HFQ end

    def getV(self):
        return self.V

    def preprocess(self):
        self.data=[[[] for i in range(0,self.Q)] for j in range(0,self.Q)]
        tmp=self.P/self.Q
        for i in range(0,self.Q):
            for j in range(0,self.Q):
                self.data[i][j]=[[[] for i1 in range(0,tmp)] for j1 in range(0,tmp)] 

        inputfile=open(self.filename,"r")
        line=inputfile.readline()
        
        self.V=map(int,line.split())[0]
        self.pr=[1.0 for i in range(0,self.V)]
        self.newpr=[0.0 for i in range(0,self.V)]
        self.deg=[0 for i in range(0,self.V)]

        hashQ=self.V/self.Q
        hashP=self.V/self.P
        line=inputfile.readline()
        while line and line != '\n':
            edge=map(int,line.split(','))
            if(edge[0]>=self.V or edge[1]>=self.V):
                print 'error:vertex num too large!'
                break
            xQ=edge[0]/hashQ
            yQ=edge[1]/hashQ
            xP=(edge[0]%hashQ)/hashP
            yP=(edge[1]%hashQ)/hashP
            #HFQ:read edges
            address = self.getMemAddress(xQ, yQ, xP, yP)
            # self.readDisk(address)
            self.data[xQ][yQ][xP][yP].append((edge[0],edge[1]))
            self.deg[edge[0]]+=1
            line=inputfile.readline()
        inputfile.close()


    # just used for test
    def do_print(self):
        print self.V
        for i in range(0,self.Q):
            for j in range(0,self.Q):
                for i1 in range(0,self.P/self.Q):
                    for j1 in range(0,self.P/self.Q):
                        print self.data[i][j][i1][j1],
                        print ' , ',
                print ' | ',
            print ' '


    def StreamEdges(self,newpr,GV):
        P=self.P
        Q=self.Q
        Ps=P/Q
        data=self.data
        deg=self.deg
        pr=self.pr
        for y1 in range(0,Q):
            for x1 in range(0,Q):
                for y2 in range(0,Ps):
                    for x2 in range(0,Ps):
                        # to do: tell mem/cache we want to access P(x2,y2) in Q(x1,y1)
                        for t in data[x1][y1][x2][y2]:
                            self.readData(x1, y1, x2, y2);
                            newpr[t[1]]+=(pr[t[0]]/deg[t[0]])
                            if GV:
                                GV.highlight(t[0],t[1])
                            

    def StreamVertices(self,newpr):
        diff=0
        for i in range(0,self.V):
            newpr[i]=1-self.damping_factor+self.damping_factor*newpr[i]
            # write disk
            diff+=abs(newpr[i]-self.pr[i])
            #HFQ: update vertex write to disk
            #FIXME:
            address = self.getMemAddressofVertex(i)
            self.writeDisk(address)
        return diff


    def do_pagerank(self,GV=None):
        converged=0
        iterations=0
        while not converged:
            if(iterations>self.max_iterations):
                print 'error: exceed the max_iterations!'
                break
            newpr=[0.0 for i in range (0,self.V)]
            self.StreamEdges(newpr,GV)
            diff=self.StreamVertices(newpr)
            self.pr=newpr
            converged=(diff/self.V)<=self.min_delta
            iterations+=1
        print self.pr
        print 'finished after '+str(iterations)+' iterations'


    def do_pagerank_per_grid(self,GV=None,index=0,rankContinue=False):
        # print "per grid index:{} continue:{} {} {}".format(index, rankContinue, self.xP, self.yP)
        if self.converged:
            print self.pr
            print 'finished after '+str(self.iterations)+' iterations!'
            return
        if self.iterations > self.max_iterations:
            print 'iteration time has exceeded!'
            return
        #print 'x1: '+str(self.xQ)+' y1: '+str(self.yQ)+' x2: '+str(self.xP)+' y2: '+str(self.yP)
        i = -1
        for tu in self.data[self.xQ][self.yQ][self.xP][self.yP]:
            i += 1
            if (i < index):
                continue

            self.readData(self.xQ,self.yQ,self.xP,self.yP);
            self.newpr[tu[1]]+=(self.pr[tu[0]]/self.deg[tu[0]])
            if GV:
                # print 'edge is '+str(tu[0])+','+str(tu[1])
                GV.highlight(tu[0],tu[1])
                if i == len(self.data[self.xQ][self.yQ][self.xP][self.yP]) - 1:
                    break
                if rankContinue:
                    GV.sleep(1, lambda: self.do_pagerank_per_grid_continue(GV, index + 1))
                else:
                    GV.sleep(300, lambda: self.do_pagerank_per_grid(GV, index + 1))

        Ps=self.P/self.Q

        self.xP += 1
        if self.xP >= Ps:
            self.xP=0
            self.yP+=1
        if self.yP >=Ps:
            self.yP=0
            self.xQ+=1
        if self.xQ >= self.Q:
            self.xQ=0
            self.yQ+=1
        if self.yQ >= self.Q:
            self.xQ=0
            self.yQ=0
            self.xP=0
            self.yP=0
            diff=self.StreamVertices(self.newpr)
            self.pr=self.newpr
            self.newpr=[0.0 for i in range(0,self.V)]
            self.converged=(diff/self.V)<=self.min_delta
            self.iterations+=1
            if self.converged:
                print self.pr
                print 'finished after '+str(self.iterations)+' iterations!'

    def do_pagerank_per_grid_continue(self,GV,index=0):
        if (index):
             self.do_pagerank_per_grid(GV,index,True)           
        while (not self.converged) and (self.iterations <= self.max_iterations):
            self.do_pagerank_per_grid(GV,0,True)

    # HFQ begin
    def getMemAddress(self, x1, y1, x2, y2):
        return x2 * self.Q + y2 + x1 * self.P + y1
    
    #Fix Me
    def getMemAddressofVertex(self,i):
        return 0

    #@params
    # SB HFQ luan gei can shu
    # cacheBegin: self.cacheBegin
    # cacheEnd: self.cacheEnd 
    # memBegin: self.memBegin
    # memEnd: self.memEnd
    def readCache(self, address):
        self.GV.readCache(address)

    def writeCache(self, address):
        self.GV.writeCache(address)

    def readMem(self, address):
        self.read_mem_time += 1
        self.GV.readMemory(self.LLCbegin, address)

    def writeMem(self, address):
        self.write_mem_time += 1
        self.GV.writeMemory(self.LLCbegin, address)
    
    def readDisk(self, address):
        self.read_disk_time += 1
        self.GV.readDisk(self.LLCbegin, self.MEMbegin, address)

    def writeDisk(self, address):
        self.write_disk_time += 1
        self.GV.writeDisk(self.LLCbegin, self.MEMbegin, address)

    def inLLC(self, x1, y1, x2, y2):
        address = self.getMemAddress(x1, y1, x2, y2)
        return address >= self.LLCbegin and address < self.LLCend

    def inMem(self, x1, y1, x2, y2):
        address = self.getMemAddress(x1, y1, x2, y2)
        return address >= self.MEMbegin and address < self.MEMend

    def readData(self, x1, y1, x2, y2):
        address = self.getMemAddress(x1, y1, x2, y2)
        if self.inLLC(x1, y1, x2, y2):
            self.readCache(address)
            return
        if self.inMem(x1, y1, x2, y2):
            self.LLCbegin = address
            self.LLCend = address + self.LLCSize
            self.readMem(address)
            self.writeCache(address)
            return
        self.LLCbegin = address
        self.LLCend = address + self.LLCSize
        self.MEMbegin = address
        self.MEMend = address + self.MEMSize
        self.readDisk(address)
        self.writeMem(address)
        self.writeCache(address)

    def writeData(self, x1, y1, x2, y2):
        address = self.getMemAddress(x1, y1, x2, y2)
        if self.inLLC(x1, y1, x2, y2):
            self.writeCache(address)
            return
        if self.inMem(x1, y1, x2, y2):
            self.LLCbegin = address
            self.LLCend = address + self.LLCSize
            self.writeMem(address)
            return
        self.LLCbegin = address
        self.LLCend = address + self.LLCSize
        self.MEMbegin = address
        self.MEMend = address + self.MEMSize
        self.writeDisk(address)
    # HFQ end
