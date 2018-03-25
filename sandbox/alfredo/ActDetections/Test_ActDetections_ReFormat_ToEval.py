import warnings, time;
import numpy as np;
import pandas as pd;
import pandas.io.sql as psql;
import sqlite3 as lite;

def getIndAttrs(sFileDB):
    conn = lite.connect(sFileDB);
    dfIndAttrs = psql.frame_query("SELECT * FROM IndAttrs", conn);
    return dfIndAttrs;

def reformat_dfActs(dfIndAttrs):
    aTracksId = set(dfIndAttrs[dfIndAttrs["ObjType"]=="Person"]["TrackId"]);
    aTracksId = list(np.array(list(aTracksId)).astype("int"));
    aTracksId.insert(0,"Frame");
    aActs = ["GetIn", "GetOut", "Carry", "Exchange"];
    for sAct in aActs:
        dfAct = dfIndAttrs[(dfIndAttrs["ObjType"]=="Person") & (dfIndAttrs[sAct]!="")];
        dfAct_csv = pd.DataFrame(index=range(len(dfAct)), columns=aTracksId);
        i = 0;
        for nFrm, dfAct_Frm in dfAct.groupby(["Frame"]):
            dfAct_csv["Frame"][i] = nFrm;
            for nIdx in dfAct_Frm.index:
                nObjId = int(dfAct_Frm[sAct][nIdx].split("_")[1]);
                nTrackId = int(dfAct_Frm["TrackId"][nIdx]);
                dfAct_csv[nTrackId][i] = nObjId;
            i += 1;
        dfAct_csv.to_csv("./ActDetections/Act_"+sAct+".csv", index=False);
        print "Finished with: Act_"+sAct+".csv";

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    sFileDB = './VIRAT_01.s3db';
    dfIndAttrs = getIndAttrs(sFileDB);
    t0 = time.time();
    reformat_dfActs(dfIndAttrs);
    print "Time Reformatting Activities: " + str(time.time()-t0);
    