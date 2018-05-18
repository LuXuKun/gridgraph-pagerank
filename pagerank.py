#!/usr/bin/python
import visual

class PageRank:
    def __init__(self, P, Q, filename, GV):
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
        self.LLCSize = 0
        self.MEMSize = 0
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
            self.readMem(address)
            self.writeCache(address)
            self.LLCbegin = address
            self.LLCend = address + self.LLCSize
            return
        self.readDisk(address)
        self.writeMem(address)
        self.writeCache(address)
        self.LLCbegin = address
        self.LLCend = address + self.LLCSize
        self.MEMbegin = address
        self.MEMend = address + self.MEMSize

    def writeData(self, x1, y1, x2, y2):
        address = self.getMemAddress(x1, y1, x2, y2)
        if self.inLLC(x1, y1, x2, y2):
            self.writeCache(address)
            return
        if self.inMem(x1, y1, x2, y2):
            self.writeMem(address)
            return
        self.writeDisk(address)
    # HFQ end
