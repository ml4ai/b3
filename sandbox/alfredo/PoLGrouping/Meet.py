import pylab;
import scipy.stats as stats;
from XmlActivity import XmlActivity;

class Meet(object):
    def __init__(self, actor1, actor2):
        self.actor1 = actor1;
        self.actor2 = actor2;
        self.aInitPos = [];
        self.nInitRange = -1;
        self.nEndRange = -1;
        self.bStarted = False;
        self.nProb, self.nPastProb = 0, 0;
        self.nMaxStart_Time = 10; #Init Meet Time (in Num. of Frames)
        self.nMaxDist = 100; #Max Distance from Meet Zone (and between A & B)
        self.nTime = 0;
        self.nInit_Threshold, self.nEnd_Threshold = 0.8, 0.3;
        self.bStarted, self.bActive = False, False;
        self.xmlAct = XmlActivity(self.__class__.__name__);
        self.aBeliefs = [];
        
    def startAct(self, nFrame):
        nX = (self.actor1.aPos[0] + self.actor2.aPos[0])/2.0;
        nY = (self.actor1.aPos[1] + self.actor2.aPos[1])/2.0;
        self.aInitPos = [nX, nY];
        self.aBeliefs = [];
        self.bStarted = True;
        self.nInitRange = self.actor1.activityMngr.loiter.nInitRange;
#         self.nInitApproach = self.actor2.activityMngr.approach[self.actor1.nTrackId].nInitRange;
#         print nFrame, "Starting Meet at:", self.aInitPos;
    
    def getMeetDist(self, aNewPos):
        [nNewX, nNewY] = aNewPos;
        [nInitX, nInitY] = self.aInitPos;
        nDist = pylab.norm([nInitX-nNewX, nInitY-nNewY]);
        return nDist;
    
    def updateAct(self, nFrame):
        actor1 = self.actor1;
        actor2 = self.actor2;
        #Prob Time
        self.nTime += 1;
        nProb_Time = 1;
        if self.nTime <= self.nMaxStart_Time:
            nTime = self.nTime/float(self.nMaxStart_Time);
            nProb_Time = stats.beta.cdf(nTime, 3,4);
        #Prob Distance between A & B
        nDist = actor1.getDist(actor2);
        nDistN = nDist/float(self.nMaxDist);
        nProb_Dist_AB = (1 - stats.beta.cdf(nDistN, 3,4));
        #Prob Distence from Meet Zone
        nDist = self.getMeetDist(actor1.aPos);
        nDistN = nDist/float(self.nMaxDist);
        nProb_Dist_MeetZone = (1 - stats.beta.cdf(nDistN, 3,4));
        #Final Prob Belief
        self.nProb = nProb_Time*nProb_Dist_AB*nProb_Dist_MeetZone;
#         print nFrame, "Vel: %.2f" % (actor1.nVel), "Dist: %.2f" % (nDist), "nProb_Dist_AB: %.2f" % (nProb_Dist_AB*100), "nProb_Dist_MeetZone: %.2f" % (nProb_Dist_MeetZone*100), "nProb_Time: %.2f" % (nProb_Time*100), "Prob: %.2f" % (self.nProb*100);
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
#             print nFrame, "Meet Belief Above Threshold...";
        #Belief Below the Threshold
        if (self.nProb < self.nEnd_Threshold) and (self.nPastProb >= self.nEnd_Threshold) and self.bActive:
            self.nEndRange = nFrame;
            self.bActive = False;
            self.bStarted = False;
            self.nProb = 0;
#             self.writeXmlAct([self.nInitRange, self.nInitApproach], True);
#             self.writeXmlAct([self.nInitRange, self.nEndRange]);
#             print "Meet on subjects:", (self.actor1.nTrackId, self.actor2.nTrackId),\
#                 "Finished with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), self.aBeliefs;
#             print (self.nInitRange, self.nInitApproach, self.nEndRange), self.actor1.nTrackId, self.actor2.nTrackId, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;
        
    def writeXmlAct(self, aTimes, bOngoing=False): #Write XML Activity
        nScore = sum(self.aBeliefs)/float(len(self.aBeliefs));
        sP = "Person_";
        aActors = [sP+str(self.actor1.nTrackId), sP+str(self.actor2.nTrackId)];
        aActorsTimes = [aTimes, aTimes];
        self.xmlAct.writeXmlAct(aTimes, nScore, aActors, aActorsTimes, bOngoing);
        