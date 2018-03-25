import pylab;
from ActivityMngr import ActivityMngr;
import scipy.stats as stats;

class Actor(object):
    def __init__(self, nTrackId, actorMngr):
        self.activityMngr = ActivityMngr(self, actorMngr);
        self.nTrackId = nTrackId;
        self.nFrm_Width, self.nFrm_Height = 720, 640;        
        nFrames, FR = 1, 30.0; #FR = 1/33.33; #Frames/Millisecs @UnusedVariable
        self.dt = 1; #Pixels/Frame #nFrames/FR; #Frames/Secs (1/30) #Check Excel File
        self.nVel, self.nAcc, self.nHeading = '-', '-', '-';
        self.aVels, self.aFrames = [], [];
        self.nMaxWinLength = 20;  #Max Cache of Data to Store (max Window length)
        self.aPos, self.aPastPos = [], [];
        self.aX, self.aY = [], [];
        self.aVel_XY, self.nAvgVel = [], '-';
        self.mLastDists = dict();
        self.actorData = [];
        self.nFrame = -1;
        self.bMissing = False; #If the actor is currently on Screen
        self.sAction = None;
        self.minPosBB, self.maxPosBB = [], [];
        self.aAllX, self.aAllY, self.aAllV, self.aAllVX, self.aAllVY = [], [], [], [], [];
        self.aAllAcc, self.aAllHeading, self.aAllFrames = [], [], [];
        
    def updateActorData(self, nFrame, x1, y1, x2, y2, sAction):
        y1, y2 = self.nFrm_Height-y1, self.nFrm_Height-y2;
        [x1, y1, x2, y2] = self.remNegs(x1, y1, x2, y2);
        self.nFrame = nFrame; #Current Frame
        self.sAction = sAction;
        self.bMissing = False;
        self.minPosBB, self.maxPosBB = [x1, y1], [x2, y2];
        self.aPastPos = self.aPos;
        aPos2 = self.getPos(x1, y1, x2, y2);
        self.setWinData_Pos(list(aPos2));
        avgPos = self.getAvgPos_Win();
        if avgPos==[]: avgPos = aPos2;
        [nVel2, self.aVel_XY] = self.getVel(self.aPos, avgPos);
        self.setWinData_Vel(nVel2);
        self.nAvgVel = (self.nVel + nVel2)/2.0 if (self.nVel!='-' and nVel2!='-') else '-';
        nHeading = self.getHeading(self.aVel_XY);
        self.nAcc = self.getAcc(self.nVel, nVel2); #Acceleration
        if nHeading!='-': self.nHeading = nHeading; #Heading
        self.aPos = list(avgPos); #Position
        self.nVel = nVel2; #Velocity        
        
        
    def remNegs(self, x1, y1, x2, y2):
        x1 = 0 if x1<0 else x1;
        x2 = 0 if x2<0 else x2;
        y1 = 0 if y1<0 else y1;
        y2 = 0 if y2<0 else y2;
        return [x1, y1, x2, y2];
    
    def getActorData(self):
#         aPos = [self.aPos[0], 640-self.aPos[1]]; #self.aPos; #[self.aPos[0], 640-self.aPos[1]]
        self.aAllX.append(self.aPos[0]);
        self.aAllY.append(self.aPos[1]);
        self.aAllFrames.append(self.nFrame);      
#         if self.nVel!='-':
        self.aAllV.append(self.nVel);
        self.aAllVX.append(self.aVel_XY[0]);
        self.aAllVY.append(self.aVel_XY[1]);
#         if self.nAcc!='-':
        self.aAllAcc.append(self.nAcc);
#         if self.nHeading!='-':
        self.aAllHeading.append(self.nHeading);
#         if self.nVel!='-' and self.nAcc!='-' and self.nHeading!='-':
#             self.aX.append(aPos[0]);
#             self.aY.append(aPos[1]);
#             self.aV.append(self.nVel);
#             self.aAcc.append(self.nAcc);
#             self.aHeading.append(self.nHeading);
#             self.aFrames.append(self.nFrame);
        return [self.nTrackId, self.nFrame, self.aPos, self.nVel, self.nAcc, self.nHeading, self.aVel_XY];        
    
    def updateActivities(self, nFrame):
        self.activityMngr.updateActivities(nFrame);
        
    def check_Active(self):
        return self.activityMngr.check_Active();
    
    def vectors_to_Angle(self, aV1, aV2):
        mVect1 = pylab.matrix(aV1);
        mVect2 = pylab.matrix(aV2);
        nNorms = (pylab.norm(mVect1)*pylab.norm(mVect2));
        if nNorms==0: return "-";
        nAngle = pylab.arccos(mVect1*mVect2.T/nNorms);
        return float(nAngle);
    
    def setWinData_Pos(self, aPos):        
        self.aX.append(aPos[0]);
        self.aY.append(aPos[1]);
        if len(self.aX)>self.nMaxWinLength:
            del self.aX[0];
            del self.aY[0];
    
    def setWinData_Vel(self, nVel):
        if nVel!="-":
            self.aVels.append(nVel);
        if len(self.aVels)>self.nMaxWinLength:
            del self.aVels[0];
#         self.aFrames.append(self.nFrame);
#         if len(self.aFrames)>self.nMaxWinLength:
#             del self.aFrames[0];

    def getAvgPos_Win(self, nWin=5):
        if len(self.aX)<nWin: return [];
        avgX = sum(self.aX[(len(self.aX)-nWin):])/float(nWin);
        avgY = sum(self.aY[(len(self.aX)-nWin):])/float(nWin);
#         if self.nTrackId==6 and len(self.aAllFrames)<20:
#             print self.aX, avgX;
        return [avgX, avgY];        
    
    def getAvgVel_Win(self, nWin=3):
        if len(self.aVels)<nWin: return '-';
        return sum(self.aVels[:nWin])/float(nWin);
    
    def points_to_Dist(self, aPoint1, aPoint2):
        nThisX, nThisY = aPoint1[0], aPoint1[1];
        nOtherX, nOtherY = aPoint2[0], aPoint2[1];
        nDist = pylab.norm([nThisX-nOtherX, nThisY-nOtherY]);
        return nDist;        
        
    def getDist(self, otherActor):
        [x1, y1] = otherActor.minPosBB;
        [x2, y2] = otherActor.maxPosBB;
        aOtherPoint = self.getPos(x1, y1, x2, y2);
        nDist = self.points_to_Dist(self.aPos, aOtherPoint);
        return nDist;
    
    def getPos(self, x1, y1, x2, y2):
        nPosX = x1 + (x2-x1)/2.0;
        nPosY = y1 + (y2-y1)/2.0;
        return [nPosX, nPosY];
    
    def getVel(self, aPos1, aPos2):
        if aPos1==[]:
            return ['-', ['-','-']];
        nVelX = (aPos2[0]-aPos1[0])/self.dt;
        nVelY = (aPos2[1]-aPos1[1])/self.dt;
#         if self.nTrackId==3 and len(self.aAllFrames)<20:
#             print self.nFrame, aPos1, aPos2, nVelX, nVelY;
        aVel = [nVelX, nVelY];
        nVel = pylab.norm(aVel);
        return [nVel, aVel];
    
    def getAcc(self, nVel1, nVel2):
        if nVel1=="-" or nVel2=='-':
            return '-';
        nAcc = (nVel2-nVel1)/self.dt;
        return nAcc;
    
    def getHeading(self, aVel_XY):
        if aVel_XY[0]=='-': return '-';
        aVel_XY = list(aVel_XY);
        aVel_XY[1] = -aVel_XY[1];
        nHeading = self.vectors_to_Angle([1,0], aVel_XY);
        if nHeading!='-' and aVel_XY[1]<0:
            nHeading = pylab.pi + (pylab.pi - nHeading);
        return nHeading;
        
    
    def getRun(self):
        if self.nAvgVel=='-': return -1;
        nRun = abs(64 - self.nAvgVel)/32.0;
        nProb_Run = (1 - stats.beta.cdf(nRun, 3,4));
        if self.nAvgVel > 64: nProb_Run = 1;
        return nProb_Run;
    
    def getStandStill(self, nWin=3):
        nAvgVel = self.getAvgVel_Win(nWin);
        if nAvgVel=='-': return -1;
        nStand = nAvgVel/32.0;
        nProb_Stand = (1 - stats.beta.cdf(nStand, 3,4));
        nProb_Stand = (0.6 + nProb_Stand*0.4) if self.sAction=="stop" else nProb_Stand;
        return nProb_Stand;
    
    def getWalk(self):
        if self.nAvgVel=='-': return -1;
        nWalk = abs(32 - self.nAvgVel)/32.0;
        nProb_Walk = (1 - stats.beta.cdf(nWalk, 3,4));
        nProb_Walk = (0.6 + nProb_Walk*0.4) if self.sAction=="walk" else nProb_Walk;
        return nProb_Walk;
    
    def getSame_Vel(self, otherActor):
        if self.nAvgVel=='-' or otherActor.nAngVel=='-': return -1;
        nSame_Vel = abs(self.nAvgVel - otherActor.nAngVel)/100.0;
        nProb_SameVel = (1 - stats.beta.cdf(nSame_Vel, 3,4));
        return nProb_SameVel;
    
    def getSame_Angle(self, otherActor):
        aV1 = self.aVel_XY;
        aV2 = otherActor.aVel_XY;
        if len(aV1)==0 or len(aV2)==0: return -1;
        if aV1[0]=='-' or aV2[0]=='-': return -1;
        nAngle = self.vectors_to_Angle(aV1, aV2);
        if nAngle=='-': return -1;
        nSame_Angle = nAngle/pylab.pi;
        nProb_SameAngle = (1 - stats.beta.cdf(nSame_Angle, 3,4));
        return nProb_SameAngle;
    
    def checkFOV(self, aOther_Pt):
        #Get Angle (in Radians) Limits (and their Slopes)
        nAngView = pylab.deg2rad(25);
        if self.nHeading=='-': return False;
        aThis_Pt, aOther_Pt = list(self.aPos), list(aOther_Pt);
        nRad1, nRad2 = self.nHeading + nAngView, self.nHeading - nAngView;
        nSlope1, nSlope2, nMaxSlope = pylab.tan(nRad1), pylab.tan(nRad2), 10000;  # @UnusedVariable
        aThis_Pt[1], aOther_Pt[1] = self.nFrm_Height-aThis_Pt[1], self.nFrm_Height-aOther_Pt[1];
        aOther_Pt[0], b = (aOther_Pt[0] - aThis_Pt[0]), aThis_Pt[1];
        nOtherX, nOtherY = aOther_Pt[0], aOther_Pt[1];    
#         #Avoid Multiplications where the Slope is close to Infinite 
#         if abs(nSlope1) >= nMaxSlope:
#             y2 = nSlope2*nOtherX + b;
#             if nRad2 < pylab.pi/2.0: return (nOtherX>=0) and (nOtherY>=y2);
#             else: return (nOtherX<=0) and (nOtherY<=y2);
#         if abs(nSlope2) >= nMaxSlope:
#             y1 = nSlope1*nOtherX + b;
#             if nRad1 > (3*pylab.pi)/2.0: return (nOtherX>=0) and (nOtherY<=y1);
#             else: return (nOtherX<=0) and (nOtherY>=y1);
        #Check position of AngViews
        y1 = nSlope1*nOtherX + b;
        y2 = nSlope2*nOtherX + b;
        nUpLeft, nDownLeft = pylab.pi/2.0, (3*pylab.pi)/2.0;
        bAngView1_Left = (nRad1 > nUpLeft) and (nRad1 < nDownLeft); #AngView1 on Left Side
        bAngView2_Left = (nRad2 > nUpLeft) and (nRad2 < nDownLeft); #AngView2 on Left Side
        bBothLeft = (bAngView1_Left) and (bAngView2_Left);
        bBothRight = (bAngView1_Left==False) and (bAngView2_Left==False);
        bBothUp = (bAngView1_Left) and (bAngView2_Left==False);
        bBothDown = (bAngView1_Left==False) and (bAngView2_Left);
        if bBothLeft and (nOtherY >= y1) and (nOtherY <= y2): return True;
        if bBothRight and (nOtherY <= y1) and (nOtherY >= y2): return True;
        if bBothUp and (nOtherY >= y1) and (nOtherY >= y2): return True;
        if bBothDown and (nOtherY <= y1) and (nOtherY <= y2): return True;
        return False;
    