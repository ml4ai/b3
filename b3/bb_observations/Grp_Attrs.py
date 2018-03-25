import pylab;  # @UnusedImport
import numpy as np;  # @UnusedImport
import pandas as pd;
from Grp_Detector import Grp_Detector;

class Grp_Attrs(object):
    def __init__(self, dfIndAttrs):
        self.dfIndAttrs = dfIndAttrs;
        self.dfGrp_Attrs = [];
        self.grp_Detector = Grp_Detector(dfIndAttrs);
        
    def getGrps(self):
        self.dfIndAttrs["GrpId"] = -1;
        for nFrame, dfFrame in self.dfIndAttrs.groupby(['Frame']):  # @UnusedVariable
            dfFrame = dfFrame[["TrackId", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY", "Frame"]].dropna();
            if len(dfFrame)==0: continue;
            aGrpsId = self.grp_Detector.findClusters(dfFrame);
            dfFrame["GrpId"] = pd.Series(aGrpsId, dfFrame.index);
            self.dfIndAttrs.update(dfFrame);
        
#     def getGrps(self):
#         for nFrame, dfFrame in self.dfIndAttrs.groupby(['Frame']):  # @UnusedVariable
#             dfFrame = dfFrame[["TrackId", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY", "Frame"]].dropna();
#             if len(dfFrame)==0: continue;
#             aGrpsId = self.grp_Detector.findClusters(dfFrame);            
#             dfGroupsTmp = dfFrame[["TrackId", "Frame"]];
#             dfGroupsTmp["GrpId"] = pd.Series(aGrpsId, dfGroupsTmp.index);
#             if len(self.dfGroups)==0: self.dfGroups = dfGroupsTmp;
#             else: self.dfGroups = self.dfGroups.append(dfGroupsTmp);
        
    def getGrp_Attrs(self): #, dfFrame, dfGroupsFrm):
        aData = [([],[],[],[],[],[],[],[],[],[],[],[])];
        aCols = ["GrpId", "Frame", "PosX", "PosY", "SpeedX", "SpeedY", "Speed", 
                 "Acc", "Heading", "GrpMembers", "InitFrm", "EndFrm"];
        self.dfGrp_Attrs = pd.DataFrame(aData, index=[], columns=aCols);
        for nFrame, dfFrame in self.dfIndAttrs.groupby(['Frame']):  # @UnusedVariable
            for nGrpId, dfFrm_Grp in dfFrame.groupby(['GrpId']):  # @UnusedVariable
                if nGrpId<0: continue;
                nPosX = dfFrm_Grp["AvgPosX"].mean();
                nPosY = dfFrm_Grp["AvgPosY"].mean();
                nSpeedX = dfFrm_Grp["SpeedX"].mean();
                nSpeedY = dfFrm_Grp["SpeedY"].mean();
                nSpeed = dfFrm_Grp["Speed"].mean();
                nAcc = dfFrm_Grp["Acc"].mean();
                nHeading = dfFrm_Grp["Heading"].mean();
                aMembers = sorted(dfFrm_Grp["TrackId"].tolist());
                sMembers = map(lambda x: str(int(x)), aMembers);
                sMembers = ",".join(sMembers);
                tData = (nGrpId, nFrame, nPosX, nPosY, nSpeedX, nSpeedY, nSpeed, 
                         nAcc, nHeading, sMembers, float("nan"), float("nan"));
                dfTmp = pd.DataFrame([tData], columns=aCols);
                self.dfGrp_Attrs = self.dfGrp_Attrs.append(dfTmp, ignore_index=True);
        #Specify Group Segments (Intervals where the group members don't change)
        for sMembers, dfGrp in self.dfGrp_Attrs.groupby(["GrpMembers"]):
            nInitFrm = dfGrp["Frame"][dfGrp.index[0]];
            nLastIdx = dfGrp.index[-1];
#             print "nLastIdx:", nLastIdx;
            nPastFrm = nInitFrm-1;
            for i,nFrm in enumerate(dfGrp["Frame"]):
                nIdx = dfGrp.index[i];
                if nFrm-1==nPastFrm:
                    dfGrp["InitFrm"][nIdx] = nInitFrm;
                elif nFrm-1!=nPastFrm:
                    dfGrp["InitFrm"][nIdx] = nInitFrm;
                    dfGrp["EndFrm"][nIdx] = nFrm;
                    if nIdx!=nLastIdx:
                        nInitFrm = dfGrp["Frame"][dfGrp.index[i+1]];
                if nLastIdx==nIdx:
                    dfGrp["EndFrm"][nIdx] = nFrm;
#                     print "EndFrm[",nIdx,"]:", nFrm;
                nPastFrm = nFrm;
            self.dfGrp_Attrs.update(dfGrp);
#         print self.dfGrp_Attrs;
#         for nFrame, dfFrame in self.dfIndAttrs.groupby(['Frame']):  # @UnusedVariable
#             for nGrpId, dfGrp in self.dfGrp.groupby(['GrpId']):  # @UnusedVariable            
#                 if len(self.dfGrp_Attrs)==0: self.dfGrp_Attrs = dfGrpTmp;
#                 else: self.dfGrp_Attrs = self.dfGrp_Attrs.append(dfGrpTmp);
        
        
#         self.dfGroups = self.grp_Detector.getGrps();
#         for nFrame, dfFrame in self.dfIndAttrs.groupby(['Frame']):  # @UnusedVariable
#             print dfFrame[["TrackId", "PosX", "PosY", "Frame"]];
#             self.grp_Detector()
#             dfTrack = self.getAvgPositions(dfTrack);
#             dfTrack = self.getSpeeds(dfTrack);
#             dfTrack = self.getAccelerations(dfTrack);
#             dfTrack = self.getHeadings(dfTrack);
#             dfTrack = self.getWithinDist(dfTrack);
#             dfTrack = self.getTime_WithinDist(dfTrack);
#             self.dfIndAttrs.update(dfTrack);
        