import sys, types;  # @UnusedImport
import numpy;  # @UnusedImport
import matplotlib.pyplot as plt;  # @UnusedImport
import pandas.io.sql as psql;
import sqlite3 as lite;
import pandas as pd;  # @UnusedImport
from Individual_Attrs import Individual_Attrs;
from Pair_Attrs import Pair_Attrs;
from Grp_Attrs import Grp_Attrs;

class BB_Observations(object):
    def __init__(self, sFileDB):
        self.sFileDB = sFileDB;
        self.dfIndAttrs, self.dfPairAttrs, self.dfGrp_Attrs = [], [], [];
    
    def getRawData(self, sFileDB, nStartFrm, nEndFrm):
        self.conn = lite.connect(sFileDB);
        sRange = "Frame>="+str(nStartFrm)+" and Frame<="+str(nEndFrm);
        dfRawData = psql.frame_query("SELECT * FROM Pol_Tracks WHERE " + sRange, self.conn);        
        return dfRawData;
    
    def getIndAttrs(self, dfRawData):
        indAttrs = Individual_Attrs(dfRawData);
        indAttrs.getIndividual_Attrs();
        self.dfIndAttrs = indAttrs.dfIndAttrs;
        return indAttrs.dfIndAttrs;
    
    def getPairAttrs(self, dfIndGrp_Attrs):
        pairAttrs = Pair_Attrs(dfIndGrp_Attrs);
        pairAttrs.getPair_Attrs();
        self.dfPairAttrs = pairAttrs.dfPairAttrs;
        return pairAttrs.dfPairAttrs;
        
    def getGrpAttrs(self, dfIndAttrs):
        grpAttrs = Grp_Attrs(dfIndAttrs);
        grpAttrs.getGrps();
        grpAttrs.getGrp_Attrs();
        self.dfGrp_Attrs = grpAttrs.dfGrp_Attrs;
        self.dfIndAttrs = grpAttrs.dfIndAttrs;
        return grpAttrs.dfIndAttrs, grpAttrs.dfGrp_Attrs;
    
    def getIndGrp_Attrs(self, dfIndAttrs, dfGrp_Attrs):
        aCols = ['TrackId', 'Frame', 'AvgPosX', 'AvgPosY'];
        dCols = {"GrpId":"TrackId","PosX":"AvgPosX","PosY":"AvgPosY"};
        dfIndGrp_Attrs = self.dfIndAttrs[self.dfIndAttrs['GrpId']==-1].copy();
        dfIndGrp_Attrs = dfIndGrp_Attrs[aCols];
        dfGrp_Attrs = self.dfGrp_Attrs.rename(columns=dCols);
        dfGrp_Attrs = dfGrp_Attrs[aCols];
        dfIndGrp_Attrs = pd.concat([dfIndGrp_Attrs, dfGrp_Attrs], ignore_index=True);
        return dfIndGrp_Attrs;
    
    def storeResults(self):
        self.storeTable(self.dfIndAttrs, "IndAttrs");
        self.storeTable(self.dfPairAttrs, "PairAttrs");
        self.storeTable(self.dfGrp_Attrs, "GrpAttrs");
        
    def storeTable(self, dataFrame, sTblName):
        self.dropTable(dataFrame, sTblName);
        self.createTable(dataFrame, sTblName);
        psql.write_frame(dataFrame, sTblName, self.conn, if_exists="append");

    def dropTable(self, dataFrame, sTable):
        if psql.table_exists(sTable, self.conn, 'sqlite'):
            psql.execute("DROP TABLE "+sTable, self.conn);
        
    def createTable(self, dataFrame, sTable):
        sCreateTbl = "CREATE TABLE "+sTable+"(";
        dTypes = {"float64":"REAL", "bool":"BOOLEAN", "unicode":"TEXT", "str":"TEXT"};
        for sCol in dataFrame.columns:
            sTypeCol = dTypes[type(dataFrame[sCol].iloc[0]).__name__];
            sCreateTbl = sCreateTbl + sCol +" "+ sTypeCol +", ";
        psql.execute(sCreateTbl[:-2]+")", self.conn);
