from XmlActivity import XmlActivity;

class WaitAndMeet2(object):
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
        self.nInit_Threshold, self.nEnd_Threshold = 0.8, 0.3; #0.8, 0.3
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
        self.nInitApproach = self.actor2.activityMngr.approach[self.actor1.nTrackId].nInitRange;
#         print nFrame, "Starting Meet at:", self.aInitPos;
    
    def updateAct(self, nFrame):
        actor1 = self.actor1;
        actor2 = self.actor2;
        #Prob Approach
        otherApproach = actor2.activityMngr.approach[actor1.nTrackId];
        nProbApproach = otherApproach.nProb if otherApproach.bActive else otherApproach.nAvgBelief;
        #Prob Meet
        meet = actor1.activityMngr.meet[actor2.nTrackId];
        nProbMeet = meet.nProb;
        #Final Prob Belief
        self.nProb = nProbMeet*nProbApproach;
#         print nFrame, (self.actor1.nTrackId, self.actor2.nTrackId), "nProbApproach: %.2f" % (nProbApproach*100), "nProbMeet: %.2f" % (nProbMeet*100), "Prob: %.2f" % (self.nProb*100), self.bActive;
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
            self.writeXmlAct([self.nInitRange, self.nInitApproach], True);
            self.writeXmlAct([self.nInitRange, self.nEndRange]);
#             print "WaitAndMeet2 on subjects:", (self.actor1.nTrackId, self.actor2.nTrackId),\
#                 "Finished with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)), self.aBeliefs;
            print "WaitAndMeet2", (self.nInitRange, self.nInitApproach, self.nEndRange), self.actor1.nTrackId, self.actor2.nTrackId, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
        self.nPastProb = self.nProb;
        
    def writeXmlAct(self, aTimes, bOngoing=False): #Write XML Activity
        nScore = sum(self.aBeliefs)/float(len(self.aBeliefs));
        sP = "Person_";
        aActors = [sP+str(self.actor1.nTrackId), sP+str(self.actor2.nTrackId)];
        aActorsTimes = [aTimes, aTimes];
        self.xmlAct.writeXmlAct(aTimes, nScore, aActors, aActorsTimes, bOngoing);
        