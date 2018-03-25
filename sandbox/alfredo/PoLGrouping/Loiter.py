import pylab;
import scipy.stats as stats;
from XmlActivity import XmlActivity;

class Loiter(object):
    def __init__(self, actor):
        self.actor = actor;
        self.aInitPos = [];
        self.nMaxDist = 150;
        self.nInitRange, self.nEndRange = -1, -1;
        self.nInit_Threshold, self.nEnd_Threshold = 0.8, 0.1;
        self.bStarted, self.bActive = False, False;
        self.nProb, self.nPastProb = 0, 0;
        self.nMaxStart_Time = 200; #Init Loiter Time (in Num. of Frames)
        self.xmlAct = XmlActivity(self.__class__.__name__);
        self.nTime = 0;
        self.aBeliefs = [];
        
    def startAct(self, nFrame):
        self.aBeliefs = [];
        self.aInitPos = self.actor.aPos;
        self.bStarted = True;
        self.nInitRange = nFrame;
        print nFrame, "Starting Loiter for person ", self.actor.nTrackId;
    
    def getLoiterDist(self, aNewPos):
        [nNewX, nNewY] = aNewPos;
        [nInitX, nInitY] = self.aInitPos;
        nDist = pylab.norm([nInitX-nNewX, nInitY-nNewY]);
        return nDist;
    
    def updateAct(self, nFrame):
        actor = self.actor;
        #Prob Time
        self.nTime += 1;
        nProb_Time = 1;
        if self.nTime <= self.nMaxStart_Time:
            nTime = self.nTime/float(self.nMaxStart_Time);
            nProb_Time = stats.beta.cdf(nTime, 3,4);
        #Prob Distance
        nDist = self.getLoiterDist(actor.aPos);
        nDistN = nDist/float(self.nMaxDist);
        nProb_Dist = (1 - stats.beta.cdf(nDistN, 3,4));
        #Final Prob Belief
        self.nProb = nProb_Time*nProb_Dist;
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
            self.xmlAct.setNewID();
#             print nFrame, "Loiter Belief Above Threshold on subject:", self.actor.nTrackId;
        #Belief Below the Threshold
        if (self.nProb < self.nEnd_Threshold) and (self.nPastProb >= self.nEnd_Threshold) and self.bActive:
            self.nEndRange = nFrame;
            self.bActive = False;
            self.bStarted = False;
            self.nProb = 0;
            self.writeXmlAct([self.nInitRange, self.nEndRange]);
            print "Loiter on subjects:", self.actor.nTrackId,\
                "Finished with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), self.aBeliefs;
#             print self.actor.nTrackId, self.nInitRange, self.nEndRange, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;
        
    def writeXmlAct(self, aTimes, bOngoing=False): #Write XML Activity
        nScore = sum(self.aBeliefs)/float(len(self.aBeliefs));
        aActors = ["Person_"+str(self.actor.nTrackId)];
        aActorsTimes = [aTimes];
        self.xmlAct.writeXmlAct(aTimes, nScore, aActors, aActorsTimes, bOngoing);