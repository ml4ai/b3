import pylab;
import numpy as np;
import pandas as pd;

class Individual_Attrs(object):
    def __init__(self, dfIndAttrs):
        self.dfIndAttrs = dfIndAttrs;
        
    def getIndividual_Attrs(self, nWinLen):
        self.dfIndAttrs['AvgPosX'], self.dfIndAttrs['AvgPosY'] = float('nan'), float('nan');
        self.dfIndAttrs['SpeedX'], self.dfIndAttrs['SpeedY'] = float('nan'), float('nan');
        self.dfIndAttrs['Speed'] = float('nan');
        self.dfIndAttrs['AccX'], self.dfIndAttrs['AccY'] = float('nan'), float('nan');
        self.dfIndAttrs['Acc'] = float('nan');
        self.dfIndAttrs['Heading'] = float('nan');
        self.dfIndAttrs['WithinDist'] = False;
        self.dfIndAttrs['Time_WithinDist'] = 0;
#         self.dfIndAttrs = self.getPositions(self.dfIndAttrs);
        for nTrackId, dfTrack in self.dfIndAttrs.groupby(['TrackId']):  # @UnusedVariable
            dfTrack = self.getAvgPositions(dfTrack, nWinLen);
            dfTrack = self.getSpeeds(dfTrack);
            dfTrack = self.getAccelerations(dfTrack);
            dfTrack = self.getHeadings(dfTrack);
            dfTrack = self.getWithinDist(dfTrack);
            dfTrack = self.getTime_WithinDist(dfTrack);
            self.dfIndAttrs.update(dfTrack);
    
#     def getPositions(self, dfTrack):
#         dfTrack['PosX'] = dfTrack['MinX'] + (dfTrack['MaxX'] - dfTrack['MinX'])/2.0;
#         dfTrack['PosY'] = dfTrack['MinY'] + (dfTrack['MaxY'] - dfTrack['MinY'])/2.0;
#         return dfTrack;
    
    def getAvgPositions(self, dfTrack, nWinLen):
        dfTrack['AvgPosX'] = pd.rolling_mean(dfTrack["PosX"], nWinLen);
        dfTrack['AvgPosY'] = pd.rolling_mean(dfTrack["PosY"], nWinLen);
        return dfTrack;
    
    def getSpeeds(self, dfTrack):
        dfTrack['SpeedX'] = pd.rolling_apply(dfTrack["AvgPosX"], 2, self.getLastDiff);
        dfTrack['SpeedY'] = pd.rolling_apply(dfTrack["AvgPosY"], 2, self.getLastDiff);
        dfTrack['Speed'] = np.sqrt(dfTrack['SpeedX']**2 + dfTrack['SpeedY']**2);
        return dfTrack;
    
    def getAccelerations(self, dfTrack):
        dfTrack['AccX'] = pd.rolling_apply(dfTrack["SpeedX"], 2, self.getLastDiff);
        dfTrack['AccY'] = pd.rolling_apply(dfTrack["SpeedY"], 2, self.getLastDiff);
        dfTrack['Acc'] = np.sqrt(dfTrack['AccX']**2 + dfTrack['AccY']**2);
        return dfTrack;
    
    def getHeadings(self, dfTrack):
        nLastHeading = float('nan');
        for i,speedXY in zip(dfTrack["Heading"].keys(), dfTrack[["SpeedX", "SpeedY"]].values):
            nHeading = self.getHeading(speedXY);
            if not(np.isnan(nHeading)):
                nLastHeading = nHeading;
            dfTrack["Heading"][i] = nLastHeading;
        return dfTrack;
    
    def getWithinDist(self, dfTrack):
        nMaxDist, nMinSpeed = 10, 1.2;
        aLastPos, bWithinDist = None, False;
        for i, aAttr in zip(dfTrack["WithinDist"].keys(), 
                            dfTrack[["AvgPosX", "AvgPosY", "Speed"]].values):
            if bWithinDist==False and not(np.isnan(aAttr[2])) and aAttr[2]<=nMinSpeed:
                aLastPos = aAttr[:2];
            if aLastPos!=None:
                nDist = np.sqrt((aAttr[0]-aLastPos[0])**2 + (aAttr[1]-aLastPos[1])**2);
                bWithinDist = (nDist<=nMaxDist);
                aLastPos = None if not(bWithinDist) else aLastPos;
            dfTrack["WithinDist"][i] = bWithinDist;
        return dfTrack;
    
    def getTime_WithinDist(self, dfTrack):
        nTime = 0;
        for i, bWithinDist in zip(dfTrack["Time_WithinDist"].keys(), dfTrack["WithinDist"].values):
            if bWithinDist: nTime = nTime + 1;
            else: nTime = 0;
            dfTrack["Time_WithinDist"][i] = nTime;
        return dfTrack;
    
    def getLastDiff(self, x):
        if(not(np.isnan(x[-1])) and not(np.isnan(x[-2]))): nDiff = (x[-1] - x[-2]);
        else: nDiff = float('nan');
        return nDiff;
    
    def vectors_to_Angle(self, aV1, aV2):
        mVect1 = pylab.matrix(aV1);
        mVect2 = pylab.matrix(aV2);
        nNorms = (pylab.norm(mVect1)*pylab.norm(mVect2));
        if nNorms==0: return float('nan');
        nAngle = pylab.arccos(mVect1*mVect2.T/nNorms);
        return float(nAngle);
    
    def getHeading(self, aVel_XY):
        aVel_XY = [aVel_XY[0], aVel_XY[1]];
        if np.isnan(aVel_XY[0]): return float('nan');
        aVel_XY = list(aVel_XY);
        aVel_XY[1] = -aVel_XY[1];
        nHeading = self.vectors_to_Angle([1,0], aVel_XY);
        if not(np.isnan(nHeading)) and aVel_XY[1]<0:
            nHeading = pylab.pi + (pylab.pi - nHeading);
        return nHeading;
        