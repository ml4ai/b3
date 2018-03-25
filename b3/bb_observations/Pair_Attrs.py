import pylab;  # @UnusedImport
import numpy as np;
import pandas as pd;

class Pair_Attrs(object):
    def __init__(self, dfIndGrp_Attrs):
        self.dfIndGrp_Attrs = dfIndGrp_Attrs;
        self.dfPairAttrs = None;
        
    def getPair_Attrs(self):
        tblDists = self.dfIndGrp_Attrs;
        tblDists2 = tblDists.copy();
        self.dfPairAttrs = pd.merge(tblDists, tblDists2, on=["Frame"], how="outer", suffixes=["_1", "_2"]);
        self.dfPairAttrs = self.dfPairAttrs[(self.dfPairAttrs["TrackId_1"]!=self.dfPairAttrs["TrackId_2"])].copy();
        self.getDistance();
        self.getRelativeDist();
        
    def getDistance(self):
        self.dfPairAttrs["Distance"] = float('nan');
        self.dfPairAttrs["Distance"] = np.sqrt((self.dfPairAttrs["AvgPosX_1"] - self.dfPairAttrs["AvgPosX_2"])**2 + 
                                   (self.dfPairAttrs["AvgPosY_1"] - self.dfPairAttrs["AvgPosY_2"])**2);
    
    def getRelativeDist(self):
        self.dfPairAttrs["RelDist"] = float('nan');
        for trackIds, grpPairsT in self.dfPairAttrs.groupby(["TrackId_1", "TrackId_2"]):  # @UnusedVariable
            grpPairsT["RelDist"] = pd.rolling_apply(grpPairsT["Distance"], 2, self.getLastDiff);
            self.dfPairAttrs.update(grpPairsT);
            
#     def getTblDists(self):
#         aCols = ['TrackId', 'Frame', 'AvgPosX', 'AvgPosY'];
#         dCols = {"GrpId":"TrackId","PosX":"AvgPosX","PosY":"AvgPosY"};
#         tblDists = self.dfIndAttrs[self.dfIndAttrs['GrpId']==-1].copy();
#         tblDists = tblDists[aCols];
#         dfGrpAttrs = self.dfGrp_Attrs.rename(columns=dCols);
#         dfGrpAttrs = dfGrpAttrs[aCols];
#         tblDists = pd.concat([tblDists, dfGrpAttrs], ignore_index=True);
#         return tblDists;
    
    def getLastDiff(self, x):
        if(not(np.isnan(x[-1])) and not(np.isnan(x[-2]))):
            nDiff = (x[-1] - x[-2]);
        else:
            nDiff = float('nan');
        return nDiff;
        