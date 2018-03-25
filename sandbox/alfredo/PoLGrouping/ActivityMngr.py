from Exchange import Exchange1, Exchange2;  # @UnusedImport
from Approach import Approach;
from Loiter import Loiter;
from Meet import Meet;
from Run import Run;
from Chase1 import Chase1;
from Chase2 import Chase2;
from WaitAndMeet1 import WaitAndMeet1;
from WaitAndMeet2 import WaitAndMeet2;
# import math, pylab;

class ActivityMngr(object):
    def __init__(self, actor, actorMngr):
        self.actor = actor;
        self.aActors = actorMngr.aActors;
        self.aActive_Actors = actorMngr.aActive_Actors;
        self.nFrame = -1;
        self.approach = dict();
        self.meet = dict();
        self.loiter = None;
        self.run = None;
        self.chase1 = None;
        self.chase2 = dict();
        self.waitAndMeet1 = None;
        self.waitAndMeet2 = dict();
        self.aActs = [self.approach, self.meet, self.loiter, 
                      self.run, self.chase1, self.chase2, 
                      self.waitAndMeet1, self.waitAndMeet2];
        
    def updateActivities(self, nFrame):
#         if self.actor.nTrackId!=126 or nFrame<4900 or nFrame>5090: return;
#         if self.actor.nTrackId!=19 or nFrame<4886: return;
#         if self.actor.nTrackId!=53: return;
#         if self.actor.nTrackId!=99: return;
#         self.printCurrentActors(nFrame);
#         if self.actor.nTrackId!=99 or nFrame<200 or nFrame>800: return;
        if self.actor.nTrackId==24:
            nAvgVel = self.actor.getAvgVel_Win(nWin=10);
            if nAvgVel<3:
                print nFrame, nAvgVel;
        self.nFrame = nFrame;
# #         self.update_Approach();
# #         self.update_Loiter();
# #         self.update_WaitAndMeet1();
# #         self.update_WaitAndMeet2();
#         self.update_Meet();
#         self.update_Run();
#         self.update_Chase1();
#         self.update_Chase2();
                      
    def check_Active(self): #Called only when this Actor is Missing
        for act in self.aActs:
            if type(act)==dict:
                for nTrackId in act:
                    if act[nTrackId].bStarted: return True;
            elif act!=None and act.bStarted: return True;
            
    def select_Approach_Actors(self): #By Distance Closing within Approach Zone & Person's Field of View
        if self.actor.bMissing: return [];
        aOtherActors = [];
        for otherActor in self.aActive_Actors.values():
#             if otherActor.nTrackId!=81: continue;
            if otherActor==self.actor or otherActor.bMissing: continue;
            if self.actor.aPastPos==[] or otherActor.aPastPos==[]: continue;
            if not(otherActor.activityMngr.loiter.bStarted): continue; #TEMPORAL CODE [Later make an ApproachToLoiter activity]
            nPastDist = self.actor.points_to_Dist(self.actor.aPastPos, otherActor.aPastPos);
            nNewDist = self.actor.points_to_Dist(self.actor.aPos, otherActor.aPos);
            nDistOtherActor = self.actor.getDist(otherActor);
            bClosingDist = nNewDist<nPastDist;
            bApproachZone = nDistOtherActor<100 and nDistOtherActor>30;
            bNotCreated = not(self.approach.has_key(otherActor.nTrackId));
            if bClosingDist and bApproachZone and bNotCreated and self.actor.checkFOV(otherActor.aPos):
                aOtherActors.append(otherActor);
#                 print self.nFrame, "Person", self.actor.nTrackId, "Approaching to:", otherActor.nTrackId, nDistOtherActor;#"Pos:", otherActor.aPos; #, aActorTracksId;
#                 print self.nFrame, self.actor.nTrackId, otherActor.nTrackId, self.actor.nHeading, pylab.rad2deg(self.actor.nHeading), self.actor.aPastPos, self.actor.aPos, otherActor.aPos;
        return aOtherActors;

    def update_Approach(self):
        #Selection/Creation Phase
        aOtherActors = self.select_Approach_Actors();
        for otherActor in aOtherActors:
            nOtherTrackId = otherActor.nTrackId;
            self.approach[nOtherTrackId] = Approach(self.actor, otherActor);
        for nOtherTrackId in self.approach:
            #Initialization Phase
            otherActor = self.aActors[nOtherTrackId];
            if not(self.approach[nOtherTrackId].bStarted) and self.actor.nAvgVel>0:
                if not(otherActor.activityMngr.loiter.bStarted): continue; #TEMPORAL CODE [Later make an ApproachToLoiter activity]
                nPastDist = self.actor.points_to_Dist(self.actor.aPastPos, otherActor.aPastPos);
                nNewDist = self.actor.points_to_Dist(self.actor.aPos, otherActor.aPos);
                nDistOtherActor = self.actor.getDist(otherActor);
                bApproachZone = nDistOtherActor<100 and nDistOtherActor>30;
                bClosingDist = nNewDist<nPastDist;
                if bApproachZone and bClosingDist:
#                     print self.nFrame, "Person", self.actor.nTrackId, "Approaching to:", otherActor.nTrackId, nDistOtherActor;#"Pos:", otherActor.aPos; #, aActorTracksId;
                    self.approach[nOtherTrackId].startAct(self.nFrame);
            #Updating Phase
            bMissing_OtherActor = otherActor.bMissing;
            bNotChase2 = not(self.chase2.has_key(otherActor)) or not(self.chase2[otherActor].bActive);
            if bMissing_OtherActor and bNotChase2: #If the other subject dissapeared, then Kill this Approach (copied from Meet activity)
                self.approach[nOtherTrackId].nProb = 0;
                self.approach[nOtherTrackId].checkBelief_Threshold(self.nFrame);
#                 print "Killing actor", nTrackId;
                continue;
            if self.actor.bMissing: #If the subject dissapeared from screen
                self.approach[nOtherTrackId].update_Missing_Actor(self.nFrame);
            elif self.approach[nOtherTrackId].bStarted: #elif has started
                self.approach[nOtherTrackId].updateAct(self.nFrame);
            
    def printCurrentActors(self, nFrame):
        aActorTracksId = [];
        for actor in self.aActive_Actors.values():
            if actor.bMissing: continue;
            aActorTracksId.append(actor.nTrackId);
        aActorTracksId.sort();
        print nFrame, aActorTracksId;
    
    def update_Loiter(self):
        #Selection/Creation Phase
        if self.loiter==None: 
            self.loiter = Loiter(self.actor);
        #Initialization Phase
        if not(self.loiter.bStarted) and self.actor.getAvgVel_Win(nWin=3)==0:
            self.loiter.startAct(self.nFrame);
        #Updating Phase            
        if self.actor.bMissing: #If the subject dissapeared from screen
            self.loiter.update_Missing_Actor(self.nFrame);
        elif self.loiter.bStarted: #elif has started
            self.loiter.updateAct(self.nFrame);
    
    def update_Meet(self):
        #Selection/Creation Phase
        aOtherActors = self.select_Meet_Actors();
        for otherActor in aOtherActors:
            nOtherTrackId = otherActor.nTrackId;
            self.meet[nOtherTrackId] = Meet(self.actor, otherActor);
        for nOtherTrackId in self.meet:
            #Initialization Phase
            otherActor = self.aActors[nOtherTrackId];
            if not(self.meet[nOtherTrackId].bStarted):
                bBoth_LowSpeed = self.actor.nAvgVel <  30 and otherActor.nAvgVel < 30;
                bCloseDist = self.actor.getDist(otherActor)<30;
                bLoiter = self.loiter.bActive;
                if bCloseDist and bLoiter and bBoth_LowSpeed:
#                     print self.nFrame, "Person", self.actor.nTrackId, "Meeting with:", otherActor.nTrackId, otherApproach[nTrackId].nInitRange, otherApproach[nTrackId].nProb;
                    self.meet[nOtherTrackId].startAct(self.nFrame);
            #Updating Phase
            bMissing_OtherActor = otherActor.bMissing;
            if bMissing_OtherActor: #If the other subject dissapeared, then Kill this Meet
                self.meet[nOtherTrackId].nProb = 0;
                self.meet[nOtherTrackId].checkBelief_Threshold(self.nFrame);
                continue;
            if self.actor.bMissing: #If the subject dissapeared from screen
                self.meet[nOtherTrackId].update_Missing_Actor(self.nFrame);
            elif self.meet[nOtherTrackId].bStarted: #elif has started
                self.meet[nOtherTrackId].updateAct(self.nFrame);
                
    def select_Meet_Actors(self):
        if self.actor.bMissing: return [];
        aOtherActors = [];
        for otherActor in self.aActive_Actors.values():
            if otherActor==self.actor or otherActor.bMissing: continue;
            bBoth_LowSpeed = self.actor.nAvgVel <  30 and otherActor.nAvgVel < 30;
            bCloseDist = self.actor.getDist(otherActor)<30;
            bLoiter = self.loiter.bActive;
            bNotCreated = not(self.meet.has_key(otherActor.nTrackId));
            if bCloseDist and bLoiter and bBoth_LowSpeed and bNotCreated:
                aOtherActors.append(otherActor);
#                 print self.nFrame, "Person", self.actor.nTrackId, "Meeting with:", otherActor.nTrackId, otherApproach[nTrackId].nInitRange, otherApproach[nTrackId].nProb; #, "Pos:", otherActor.aPos;
        return aOtherActors;
    
    def update_Run(self):
        #Selection/Creation Phase
        if self.run==None: 
            self.run = Run(self.actor);
        #Initialization Phase
        if not(self.run.bStarted) and self.actor.getRun()>0.3:
            self.run.startAct(self.nFrame);
        #Updating Phase            
        if self.actor.bMissing: #If the subject dissapeared from screen
            self.run.update_Missing_Actor(self.nFrame);
        elif self.run.bStarted: #elif has started
            self.run.updateAct(self.nFrame);
            
    def update_Chase1(self):
        #Selection/Creation Phase
        if self.chase1==None: 
            self.chase1 = Chase1(self.actor);
        #Initialization Phase
        if not(self.chase1.bStarted) and self.run.bActive:
            self.chase1.startAct(self.nFrame);
        #Updating Phase
        if self.actor.bMissing: #If the subject dissapeared from screen
            self.chase1.update_Missing_Actor(self.nFrame);
        elif self.chase1.bStarted: #elif has started
            self.chase1.updateAct(self.nFrame);
            
    def update_Chase2(self):
        #Selection/Creation Phase
        aOtherActors = self.select_Chase2_Actors();
        for otherActor in aOtherActors:
            nTrackId = otherActor.nTrackId;
            self.chase2[nTrackId] = Chase2(self.actor, otherActor);
        for nOtherTrackId in self.chase2:
            #Initialization Phase
            otherActor = self.aActors[nOtherTrackId];
            if not(self.chase2[nOtherTrackId].bStarted):
                otherChase1 = otherActor.activityMngr.chase1;
                bOtherChase1 = otherChase1!=None and otherChase1.bActive;
                if self.run.bActive and bOtherChase1:
#                     print self.nFrame, "Person", self.actor.nTrackId, "Meeting with:", otherActor.nTrackId, otherApproach[nTrackId].nInitRange, otherApproach[nTrackId].nProb;
                    self.chase2[nOtherTrackId].startAct(self.nFrame);
            #Updating Phase
            if self.actor.bMissing: #If the subject dissapeared from screen
                self.chase2[nOtherTrackId].update_Missing_Actor(self.nFrame);
            elif self.chase2[nOtherTrackId].bStarted: #elif has started
                self.chase2[nOtherTrackId].updateAct(self.nFrame);
                
            
    def select_Chase2_Actors(self): #By having Run(thisPerson), Chase1(*,otherPerson) & within Person's Field of View (if still in screen)
        if self.actor.bMissing: return [];
        aOtherActors = [];
        for otherActor in self.aActive_Actors.values():
            if otherActor==self.actor: continue;
            otherChase1 = otherActor.activityMngr.chase1;
            bOtherChase1 = otherChase1!=None and otherChase1.bActive;
            bNotCreated = not(self.chase2.has_key(otherActor.nTrackId));
            bOtherMissing = otherActor.bMissing;
            if self.run.bActive and bNotCreated and bOtherChase1 and (bOtherMissing or self.actor.checkFOV(otherActor.aPos)):
                aOtherActors.append(otherActor);
#                 print self.nFrame, "Person", self.actor.nTrackId, "Approaching to:", otherActor.nTrackId, nDistOtherActor;#"Pos:", otherActor.aPos; #, aActorTracksId;
#                 print self.nFrame, self.actor.nTrackId, otherActor.nTrackId, self.actor.nHeading, pylab.rad2deg(self.actor.nHeading), self.actor.aPastPos, self.actor.aPos, otherActor.aPos;
        return aOtherActors;
    
    def update_WaitAndMeet1(self):
        #Selection/Creation Phase
        if self.waitAndMeet1==None: 
            self.waitAndMeet1 = WaitAndMeet1(self.actor);
        #Initialization Phase
        if not(self.waitAndMeet1.bStarted) and self.loiter.bActive:
            self.waitAndMeet1.startAct(self.nFrame);
        #Updating Phase            
        if self.actor.bMissing: #If the subject dissapeared from screen
            self.waitAndMeet1.update_Missing_Actor(self.nFrame);
        elif self.waitAndMeet1.bStarted: #elif has started
            self.waitAndMeet1.updateAct(self.nFrame);
    
    def update_WaitAndMeet2(self):
        #Selection/Creation Phase
        aOtherActors = self.select_WaitAndMeet2_Actors();
        for otherActor in aOtherActors:
            nOtherTrackId = otherActor.nTrackId;
            self.waitAndMeet2[nOtherTrackId] = WaitAndMeet2(self.actor, otherActor);
        for nOtherTrackId in self.waitAndMeet2:
            #Initialization Phase
            otherActor = self.aActors[nOtherTrackId];
            if not(self.waitAndMeet2[nOtherTrackId].bStarted):
                nTrackId = self.actor.nTrackId;
                bWaitAndMeet1 = self.waitAndMeet1!=None and self.waitAndMeet1.bActive;
                otherApproach = otherActor.activityMngr.approach;
                bOtherApproach = otherApproach.has_key(nTrackId) and otherApproach[nTrackId].bStarted;
                if not(bWaitAndMeet1 and bOtherApproach): continue;
                self.update_Meet();
                bMeet = self.meet.has_key(nOtherTrackId) and self.meet[nOtherTrackId].bStarted;
                if bWaitAndMeet1 and bOtherApproach and bMeet:
#                     print self.nFrame, "Person", self.actor.nTrackId, "Meeting with:", otherActor.nTrackId, otherApproach[nTrackId].nInitRange, otherApproach[nTrackId].nProb;
                    self.waitAndMeet2[nOtherTrackId].startAct(self.nFrame);
            #Updating Phase
            bMissing_OtherActor = otherActor.bMissing;
            if bMissing_OtherActor: #If the other subject dissapeared, then Kill this Meet
                self.waitAndMeet2[nOtherTrackId].nProb = 0;
                self.waitAndMeet2[nOtherTrackId].checkBelief_Threshold(self.nFrame);
                continue;
            if self.actor.bMissing: #If the subject dissapeared from screen
                self.waitAndMeet2[nOtherTrackId].update_Missing_Actor(self.nFrame);
            elif self.waitAndMeet2[nOtherTrackId].bStarted: #elif has started
                self.waitAndMeet2[nOtherTrackId].updateAct(self.nFrame);
                
    def select_WaitAndMeet2_Actors(self):
        if self.actor.bMissing: return [];
        aOtherActors = [];
        for otherActor in self.aActive_Actors.values():
            if otherActor==self.actor or otherActor.bMissing: continue;
            nTrackId = self.actor.nTrackId;
            nOtherTrackId = otherActor.nTrackId;
            bWaitAndMeet1 = self.waitAndMeet1!=None and self.waitAndMeet1.bActive;
            otherApproach = otherActor.activityMngr.approach;
            bOtherApproach = otherApproach.has_key(nTrackId) and otherApproach[nTrackId].bStarted;
            if not(bWaitAndMeet1 and bOtherApproach): continue;
            self.update_Meet();
            bMeet = self.meet.has_key(nOtherTrackId) and self.meet[nOtherTrackId].bStarted;  
            bNotCreated = not(self.waitAndMeet2.has_key(otherActor.nTrackId)); 
            if bWaitAndMeet1 and bOtherApproach and bMeet and bNotCreated:
                aOtherActors.append(otherActor);
                print self.nFrame, "Person", self.actor.nTrackId, "Meeting with:", otherActor.nTrackId, otherApproach[nTrackId].nInitRange, otherApproach[nTrackId].nProb; #, "Pos:", otherActor.aPos;
        return aOtherActors;
        