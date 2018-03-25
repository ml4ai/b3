import scipy.stats as stats;
from XmlActivity import XmlActivity;

class Approach(object):
    def __init__(self, actor1, actor2):
        self.actor1, self.actor2 = actor1, actor2;
        self.nPercent_DecD, self.nPercent_IncD = 0, 0;
        self.nPercent_PastD, self.nTotProb_IncD = -1, 0;
        self.nLastProb_IncD, self.nLastProb_DecD = 0, 0;
        self.nProb, self.nLastProb, self.nNonDecD = 0, 0, 0;
        self.nDist, self.nInitDist = 0, 0;
        self.nInitRange, self.nEndRange = -1, -1;
        self.nInit_Threshold, self.nEnd_Threshold = 0.9, 0.3;
        self.bStarted, self.bActive = False, False;
        self.xmlAct = XmlActivity(self.__class__.__name__);
        self.nPastProb = 0;
        self.aBeliefs = [];
        self.nAvgBelief = 0;
        
    def startAct(self, nFrame):
        self.aBeliefs = [];
        self.bStarted = True;
        self.nInitRange = nFrame;
#         print nFrame, "Starting Approach ", (self.actor1.nTrackId, self.actor2.nTrackId);
        
    def updateAct(self, nFrame):
        actor1, actor2 = self.actor1, self.actor2;
        if actor1.nVel=='-': return;
        if (nFrame) % 4!=0: return;
        self.nDist = actor1.getDist(actor2);
        nDiffDist = 0;
        if self.nPercent_PastD!=-1:
            nPercent_Dist = (1 - self.nDist/self.nInitDist);
            nDiffDist = nPercent_Dist - self.nPercent_PastD;
#             print self.nPercent_PastD, nPercent_Dist, actor1.nVel, actor1.nAvgVel;
            #Distance Decreasing
            if (nDiffDist > 0) and (actor1.nVel > 0):
                if self.nPercent_IncD > 0: 
                    self.nLastProb_IncD = self.nProb;
                    self.nPercent_IncD = 0;
                if self.nNonDecD > 0:
                    self.nLastProb_IncD = self.nProb;
                    self.nNonDecD = 0;
                self.nPercent_DecD += nDiffDist;
                nScale = (1-self.nLastProb_IncD);
                nPenalty = (1-self.nTotProb_IncD);
                self.nProb = self.nLastProb_IncD + stats.beta.cdf(self.nPercent_DecD, 10,100)*nScale*nPenalty;
            #Distance Increasing
            elif (nDiffDist < 0) and (actor1.nVel > 0):
                if self.nPercent_DecD > 0: 
                    self.nLastProb_DecD = self.nProb;
                    self.nPercent_DecD = 0;
                if self.nNonDecD > 0:
                    self.nLastProb_DecD = self.nProb;
                    self.nNonDecD = 0;
                self.nTotProb_IncD += -nDiffDist;
                self.nPercent_IncD += -nDiffDist;
                self.nProb = self.nLastProb_DecD - stats.beta.cdf(self.nPercent_IncD, 10,100)*self.nLastProb_DecD;
#                 print "Distance Increasing...";
            #Distance Non Decreasing
            elif (nDiffDist==0) or (actor1.nVel==0):
                if self.nPercent_DecD > 0: 
                    self.nLastProb_DecD = self.nProb;
                    self.nPercent_DecD = 0;
                if self.nNonDecD==0: self.nLastProb = self.nProb;
                self.nNonDecD += 1/100.0;
                self.nProb = self.nLastProb - stats.beta.cdf(self.nNonDecD, 3,4)*self.nLastProb;
#                 print "Distance Non Decreasing...";
        else:
            self.nInitDist = self.nDist;
        self.nPercent_PastD = (1 - self.nDist/self.nInitDist);
#         if actor2.nTrackId==127 or actor2.nTrackId==99:
#             print nFrame, actor1.nTrackId, "OtherSubject: ", actor2.nTrackId, "Distance: %.2f" % (self.nPercent_PastD*100), "ProbApproach: %.2f" % (self.nProb), actor1.nVel;
#         print nFrame, "Distance: %.2f" % (self.nPercent_PastD*100), "ProbApproach: %.2f" % (self.nProb);
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
#             print nFrame, "Approach belief of ", (self.actor1.nTrackId, self.actor2.nTrackId), " Above Threshold on subjects:",\
#                 "at position", self.actor1.aPos;
        #Belief Below the Threshold
        if (self.nProb < self.nEnd_Threshold) and (self.nPastProb >= self.nEnd_Threshold) and self.bActive:
            self.nEndRange = nFrame;
            self.bActive = False;
            self.bStarted = False;
            self.nProb = 0;
            self.nAvgBelief = sum(self.aBeliefs)/float(len(self.aBeliefs));
            self.writeXmlAct([self.nInitRange, self.nEndRange]);
            print "Approach", (self.nInitRange, self.nEndRange), self.actor1.nTrackId, self.actor2.nTrackId, self.nProb, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs);
#             print "Finished:", self.nInitRange, self.nEndRange, self.actor1.nTrackId, self.actor2.nTrackId, self.nProb, sum(self.aBeliefs)/float(len(self.aBeliefs)), max(self.aBeliefs); #, self.aBeliefs;
#             print "Approach Finished on subjects:", (self.actor1.nTrackId, self.actor2.nTrackId),\
#                 "with range:", [self.nInitRange, self.nEndRange], sum(self.aBeliefs)/float(len(self.aBeliefs)); #, self.aBeliefs;
        self.nPastProb = self.nProb;
        
    def writeXmlAct(self, aTimes, bOngoing=False): #Write XML Activity
        nScore = sum(self.aBeliefs)/float(len(self.aBeliefs));
        sP = "Person_";
        aActors = [sP+str(self.actor1.nTrackId), sP+str(self.actor2.nTrackId)];
        aActorsTimes = [aTimes, aTimes];
        self.xmlAct.writeXmlAct(aTimes, nScore, aActors, aActorsTimes, bOngoing);