# import pylab;
import scipy.stats as stats;

class Chase1(object):
    def __init__(self, actor):
        self.actor = actor;
        self.nInitRange, self.nEndRange = -1, -1;
        self.nInit_Threshold, self.nEnd_Threshold = 0.8, 0.1;
        self.bStarted, self.bActive = False, False;
        self.nProb, self.nPastProb = 0, 0;
        self.nLag_Time = 500; #Lag Chase1 Time (in Num. of Frames)
        self.nTime = 0;
        self.aBeliefs = [];
        
    def startAct(self, nFrame):
        self.aBeliefs = [];
        self.bStarted = True;
        self.nInitRange = nFrame;
#         print nFrame, "Starting Loiter...";
    
    def updateAct(self, nFrame):
        #Prob Run
        nProbRun = self.actor.activityMngr.run.nProb;
        #Prob Time
        if (self.nTime <= self.nLag_Time): self.nTime += 1;
        nTime = self.nTime/float(self.nLag_Time);
        nProb_Time = (1-stats.beta.cdf(nTime, 3,4));
        #Final Prob Belief
        self.nProb = nProb_Time*nProbRun;
#         print nFrame, self.actor.nTrackId, "nVel: %.2f" % (self.actor.nVel), "nProbRun: %.2f" % (nProbRun*100), \
#         "nTime: %.2f" % (nTime), "nProb_Time: %.2f" % (nProb_Time*100), "Prob: %.2f" % (self.nProb*100);
        self.checkBelief_Threshold(nFrame);
        
    def update_Missing_Actor(self, nFrame):
        if not(self.bStarted): return;
        #Prob Time
        if (self.nTime <= self.nLag_Time): self.nTime += 1;
        nTime = self.nTime/float(self.nLag_Time);
        nProb_Time = (1-stats.beta.cdf(nTime, 3,4));
        #Final Prob Belief
        self.nProb = nProb_Time;
#         print nFrame, self.actor.nTrackId, "nTime: %.2f" % (nTime), "nProb_Time: %.2f" % (nProb_Time*100), \
#         "Prob: %.2f" % (self.nProb*100);
        self.checkBelief_Threshold(nFrame);
        
    def checkBelief_Threshold(self, nFrame):
        if self.bActive:
            self.aBeliefs.append(self.nProb);
        #Belief Above the Threshold
        if (self.nProb >= self.nInit_Threshold) and (self.nPastProb < self.nInit_Threshold) and not(self.bActive):
#             self.nInitRange = nFrame;
            self.bActive = True;
            print "Chase1 Activated on subject:", self.actor.nTrackId;
#             print nFrame, "Loiter Belief Above Threshold...";
        #Belief Below the Threshold
        if (self.nProb < self.nEnd_Threshold) and (self.nPastProb >= self.nEnd_Threshold) and self.bActive:
            self.nEndRange = nFrame;
            self.bActive = False;
            self.bStarted = False;
            self.nProb = 0;
#             print "Chase1 on subject:", self.actor.nTrackId,\
#                 "Finished with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
#             print self.actor.nTrackId, self.nInitRange, self.nEndRange, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;