# import pylab;
import scipy.stats as stats;
from Approach import Approach;

class Chase2(object):
    def __init__(self, actor1, actor2):
        self.actor1, self.actor2 = actor1, actor2;
        self.nInitRange, self.nEndRange = -1, -1;
        self.nInit_Threshold, self.nEnd_Threshold = 0.8, 0.1;
        self.bStarted, self.bActive = False, False;
        self.nProb, self.nPastProb = 0, 0;
        self.nLag_Time = 500; #Lag Chase2 Time (in Num. of Frames)
        self.nTime = 0;
        self.aBeliefs = [];
        
    def startAct(self, nFrame):
        self.aBeliefs = [];
        self.bStarted = True;
        self.nInitRange = nFrame;
#         self.nInitRange = self.actor2.activityMngr.chase1.nInitRange;
#         print nFrame, "Starting Loiter...";
    
    def updateAct(self, nFrame):
        if self.actor2.bMissing: self.update_OtherMissing(nFrame);
        else: self.update_BothInScreen(nFrame);
        self.checkBelief_Threshold(nFrame);
        
    def update_OtherMissing(self, nFrame):
        #Prob Run
        nProbRun = self.actor1.activityMngr.run.nProb;
        #Prob Approach
        thisApproach = self.actor1.activityMngr.approach;
        if not(thisApproach.has_key(self.actor2)):
            thisApproach[self.actor2] = Approach(self.actor1, self.actor2);
        if not(thisApproach[self.actor2].bStarted):
            thisApproach[self.actor2].startAct(nFrame);
        thisApproach[self.actor2].updateAct(nFrame);
        nProbApproach = thisApproach[self.actor2].nProb;
        #Final Prob Belief
        self.nProb = nProbRun*nProbApproach;
        print nFrame, self.actor1.nTrackId, self.actor2.nTrackId, "nProbRun: %.2f" % (nProbRun*100), \
        "nProbApproach: %.2f" % (nProbApproach), "Prob: %.2f" % (self.nProb*100);
    
    def update_BothInScreen(self, nFrame):
        pass;
        
    def update_Missing_Actor(self, nFrame):
        if not(self.bStarted): return;
        #Prob Time
        if (self.nTime <= self.nLag_Time): self.nTime += 1;
        nTime = self.nTime/float(self.nLag_Time);
        nProb_Time = (1-stats.beta.cdf(nTime, 3,4));
        #Final Prob Belief
        self.nProb = nProb_Time;
        print nFrame, self.actor1.nTrackId, self.actor2.nTrackId, "nTime: %.2f" % (nTime), "nProb_Time: %.2f" % (nProb_Time*100), \
        "Prob: %.2f" % (self.nProb*100);
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
            print "Chase2 Finished on subjects:", (self.actor1.nTrackId, self.actor2.nTrackId),\
                "with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;