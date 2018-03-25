# import pylab;
import scipy.stats as stats;

class Run(object):
    def __init__(self, actor):
        self.actor = actor;
        self.nInitRange, self.nEndRange = -1, -1;
        self.nInit_Threshold, self.nEnd_Threshold = 0.6, 0.1;
        self.bStarted, self.bActive = False, False;
        self.nProb, self.nPastProb = 0, 0;
        self.nBuffer_Time = 2; #Init Run Time (in Num. of Frames)
        self.nTime = 0;
        self.aBeliefs = [];
        
    def startAct(self, nFrame):
        self.aBeliefs = [];
        self.bStarted = True;
        self.nInitRange = nFrame;
#         print nFrame, "Starting Loiter...";
    
    def updateAct(self, nFrame):
        #Prob Run
        nProbRun = self.actor.getRun();
        #Prob Time
        if (nProbRun > 0.3) and (self.nTime <= self.nBuffer_Time): self.nTime += 1;
        elif (self.nTime >= 0): self.nTime -= 1;
        nTime = self.nTime/float(self.nBuffer_Time);
        nProb_Time = stats.beta.cdf(nTime, 3,4);
        #Final Prob Belief
        self.nProb = (nProb_Time+nProbRun)/2.0; #nProb_Time*nProbRun;
#         print nFrame, "Vel: %.2f" % (actor.nVel), "Dist: %.2f" % (nDist), "nProb_Dist: %.2f" % (nProb_Dist*100), "nProb_Time: %.2f" % (nProb_Time*100), "Prob: %.2f" % (self.nProb*100);
        self.checkBelief_Threshold(nFrame);
        
    def update_Missing_Actor(self, nFrame):
        if not(self.bStarted): return;
        self.nProb = 0;
        self.checkBelief_Threshold(nFrame);
        
    def checkBelief_Threshold(self, nFrame):
        if self.bActive:
            self.aBeliefs.append(self.nProb);
        #Belief Above the Threshold
        if (self.nProb >= self.nInit_Threshold) and (self.nPastProb < self.nInit_Threshold) and not(self.bActive):
#             self.nInitRange = nFrame;
            self.bActive = True;
#             print nFrame, "Loiter Belief Above Threshold...";
        #Belief Below the Threshold
        if (self.nProb < self.nEnd_Threshold) and (self.nPastProb >= self.nEnd_Threshold) and self.bActive:
            self.nEndRange = nFrame;
            self.bActive = False;
            self.bStarted = False;
            self.nProb = 0;
#             print "Run on subject:", self.actor.nTrackId,\
#                 "Finished with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
#             print self.actor.nTrackId, self.nInitRange, self.nEndRange, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;