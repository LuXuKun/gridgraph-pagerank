#!/usr/bin/python
import visual

class PageRank:
    def __init__(self, P, Q, filename):
        self.damping_factor=0.85
        self.max_iterations=200
        self.min_delta=0.00001
        self.Q=Q
        self.P=P
        self.filename=filename
        self.V=0
        self.data=[]
        self.pr=[]
        self.deg=[]

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
                            newpr[t[1]]+=(pr[t[0]]/deg[t[0]])
                            if GV:
                                GV.highlight(t[0],t[1])
                            


    def StreamVertices(self,newpr):
        diff=0
        for i in range(0,self.V):
            newpr[i]=1-self.damping_factor+self.damping_factor*newpr[i]
            diff+=abs(newpr[i]-self.pr[i])
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

