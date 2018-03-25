from BB_Observations import BB_Observations;
import pandas.io.sql as psql;
import sqlite3 as lite;
import pandas as pd;
import warnings;
import numpy as np;
import hmm_ext;
import time, sys;

def setGrpIds(dfGrp_Hmms):
    nMaxGrpID = max(dfGrp_Hmms["GrpId"]) + 1;
    for sGrpMembers, dfGrpTrack in dfGrp_Hmms.groupby(['GrpMembers']):
        if len(sGrpMembers.split(","))>1: continue;
        dfGrpTrack["GrpId"] = nMaxGrpID;
        nMaxGrpID += 1;
        dfGrp_Hmms.update(dfGrpTrack);
    return dfGrp_Hmms;
   
def reformat_dfGrpHmms(dfGrp_Hmms, dfIndTracks):
    aTracksId = list(np.array(list(set(dfIndTracks["TrackId"]))).astype("int"));
    aTracksId.insert(0,"Frame");
    for sAct, dfGrp_Act in dfGrp_Hmms.groupby(["Act"]):
        dfAct = pd.DataFrame(index=range(len(dfGrp_Act)), columns=aTracksId);
        i = 0;
        for nFrm, dfGrp_Frm in dfGrp_Act.groupby(["Frame"]):
            dfAct["Frame"][i] = nFrm;
            for nIdx in dfGrp_Frm.index:
                sGrpMembers = str(dfGrp_Frm["GrpMembers"][nIdx]);
                for sGrpMember in sGrpMembers.split(","):
                    dfAct[int(sGrpMember)][i] = dfGrp_Frm["GrpId"][nIdx];
            i += 1;
        dfAct.to_csv("./Groups_"+sAct+".csv", index=False);

def read_GrpAttrs(sFileDB, nStartFrm, nEndFrm):    
    conn = lite.connect(sFileDB);
    sRange = "Frame>="+str(nStartFrm)+" and Frame<="+str(nEndFrm);
    dfIndAttrs = psql.frame_query("SELECT * FROM IndAttrs WHERE " + sRange, conn);
    dfGrp_Attrs = psql.frame_query("SELECT * FROM GrpAttrs WHERE " + sRange, conn);
    return dfIndAttrs, dfGrp_Attrs;

def detect_GrpAttrs(sFileDB, sFileCSV):
    imgLims = [[-50,10],[-10,15]]; #[[0,700],[0,640]];    
    bb_Detections = BB_Observations(sFileDB, bSaveFrms=False, imgLims=imgLims);
    bb_Detections.conn = lite.connect(sFileDB);
    dfRawData = pd.read_csv(sFileCSV);
    dfRawData = dfRawData[dfRawData["ObjType"]==1]; #Filter to avoid Objects & Cars
    t0 = time.time();
    dfIndAttrs = bb_Detections.getIndAttrs(dfRawData.copy(), nWinLen=50);
    [dfGroups, dfGrp_Attrs] = bb_Detections.getGrpAttrs(dfIndAttrs);  # @UnusedVariable
    print "Time Detecting Groups & Segments: " + str(time.time()-t0);
    print "---";
    return dfIndAttrs, dfGrp_Attrs;

def getHMM_Gait(obs_seq, nInitFrm):
    states = ["Stand", "Walk", "Run"];
    n_states = len(states);
    
    start_probability = np.array([0.4, 0.5, 0.1]);
    transition_probability = np.array([
      [0.9,  0.09, 0.01], #P(x|Stand)
      [0.08,  0.9, 0.02], #P(x|Walk)
      [0.05, 0.15, 0.8]  #P(x|Run)
    ]);
    
    model = hmm_ext.NB_GammaHMM(n_components=n_states);
    model._set_startprob(start_probability);
    model._set_transmat(transition_probability);
    model._set_shapes(np.array([1,5,30]));
    model._set_locs(np.array([0,0,0]));
    model._set_scales(np.array([1,2,1]));
    
    # predict a sequence of hidden states based on visible states
    #Observed Walking Speeds
    obs_seq = np.array(obs_seq)*250; #np.array([[0.0, 0.5, 0.1], [20,26,21], [8,9,4], [30,38,27], [10,30,1]]);
    logprob, hidden_states = model.decode(obs_seq, algorithm="viterbi");  # @UnusedVariable
    
    aHidden_States = map(lambda x: states[x], hidden_states);
    #print "Observations:", obs_seq;
#     print "Hidden States:", ", ".join(aHidden_States);
#     print range(nInitFrm, nInitFrm+len(aHidden_States));
    sHidden_States = "";
    for i in range(len(aHidden_States)-1):
        sHidden_States += "["+str(nInitFrm+i)+"]-"+aHidden_States[i]+", ";
    sHidden_States += "["+str(nInitFrm+len(aHidden_States)-1)+"]-"+aHidden_States[-1];
    #print "Hidden States:", sHidden_States;
    #print "Posterior:", np.exp(logprob);
    
    aSgmActs, aActData = [], [];
    sInitHiddenSt = aHidden_States[0];
    nInitSgm = nInitFrm;
    nEndFrm = -1;
    for i,sHiddenSt in enumerate(aHidden_States):
#         if i==0: continue;
        if sHiddenSt!=sInitHiddenSt or i==len(aHidden_States)-1:
            nEndFrm = (nInitFrm+i)-1 if i<len(aHidden_States)-1 else (nInitFrm+i);
            aActData = (sInitHiddenSt, nInitSgm, nEndFrm);
            aSgmActs.append(aActData);
            sInitHiddenSt = sHiddenSt;
            nInitSgm = nInitFrm+i;
    print aSgmActs;
    return aSgmActs, aHidden_States;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    nArgs = len(sys.argv);
    sFileCSV = sys.argv[1] if nArgs>=2 else "";
    sFileOut = sys.argv[2] if nArgs>=3 else "";
    sFileDB = sys.argv[3] if nArgs>=4 else "./Database.s3db";
    if nArgs<=1:
        print "Usage: python Clusterizer.py 'FileIn.csv' 'FileOut.csv' ['DataBase.s3db']"
#     sFileDB = "./VIRAT_01.s3db";
#     sFileCSV = "./VIRAT_01_Tracks_small.csv";
#     sFileOut = "./Groups.csv";
#     [dfGroups, dfGrp_Attrs] = read_GrpAttrs(sFileDB, 0,20655);
#     [dfGroups, dfGrp_Attrs] = read_GrpAttrs(sFileDB, 0,9075); #9075
    [dfGroups, dfGrp_Attrs] = detect_GrpAttrs(sFileDB, sFileCSV);
    dfGrps = dfGrp_Attrs[pd.notnull(dfGrp_Attrs["EndFrm"])];
    dfGrps = dfGrps[["GrpId", "GrpMembers", "InitFrm", "EndFrm"]];
    aGrpIDs, aGrpMembers, aSegments, aInitFrms, aEndFrms = [], [], [], [], [];
    aGrpSize = [];
    #Get (GrpId, GrpMembers, Speeds, InitFrm, EndFrm) from 
    #each Grp-Segment (GrpId, GrpMembers, InitFrm, EndFrm)
    for idx in dfGrps.index: #For each Grp Segment
        nGrpId = int(dfGrps["GrpId"][idx]);
        nInitFrm, nEndFrm = int(dfGrps["InitFrm"][idx]), int(dfGrps["EndFrm"][idx]);
        aGrpIDs.append([dfGrps["GrpId"][idx]]);
        aGrpSize.append([len(dfGrps["GrpMembers"][idx].split(","))]);
        aGrpMembers.append(dfGrps["GrpMembers"][idx]);
        aInitFrms.append(nInitFrm);
        aEndFrms.append(nEndFrm);
        dfGrp_Segment = dfGroups[(dfGroups["GrpId"]==nGrpId) & 
                       (dfGroups["Frame"]>=nInitFrm) & 
                       (dfGroups["Frame"]<=nEndFrm)][["TrackId", "Frame", "Speed"]];
        aGrpSgm = [];
        for nFrm, dfFrm in dfGrp_Segment.groupby(["Frame"]):
            aFrmData = dfFrm["Speed"].tolist();
            aGrpSgm.append(aFrmData);
        aSegments.append(aGrpSgm);
    #Get (GrpId, GrpMembers=TrackID, Speeds, InitFrm, EndFrm) from 
    #each Ind-Segment (GrpId=-1, GrpMembers=TrackID, InitFrm, EndFrm)
    dfIndTracks = dfGroups[["TrackId", "Frame", "Speed", "GrpId"]].dropna();
    for nTrackId, dfTrack in dfIndTracks.groupby(["TrackId"]):
        aGrpIDs.append(dfTrack["GrpId"].tolist());
        aGrpSize.append([1]*len(dfTrack));
        aGrpMembers.append(str(int(nTrackId)));
        nInitIdx, nEndIdx = dfTrack.index[0], dfTrack.index[-1];
        aInitFrms.append(int(dfTrack["Frame"][nInitIdx]));
        aEndFrms.append(int(dfTrack["Frame"][nEndIdx]));
        aSpeedsTemp = dfTrack["Speed"].tolist();
        aSpeeds = [];
        for nSpeed in aSpeedsTemp:
            aSpeeds.append([nSpeed]);
        aSegments.append(aSpeeds);
     
    #Detect Activities with HMMs
    t0 = time.time();
    print "InitFrms:", aInitFrms;
    print "EndFrms:", aEndFrms;
    aCols = ["Frame", "GrpMembers", "Act"];
    dfGrp_Hmms = pd.DataFrame(index=[], columns=aCols);
    for i in range(len(aSegments)):
        print "---";
        print "HMM", i+1, "- Segments (Hidden-States):", len(aSegments[i]), \
              "InitFrame:", aInitFrms[i], "EndFrame:", aEndFrms[i], \
              "GrpMembers:", aGrpMembers[i];
        aSgmActs, aHidden_States = getHMM_Gait(aSegments[i], aInitFrms[i]);
        nR = len(dfGrp_Hmms);
        idx = range(nR,nR+len(aHidden_States));
        dfHmm_Acts = pd.DataFrame(index=idx, columns=aCols);
        dfHmm_Acts["Frame"] = range(aInitFrms[i],aEndFrms[i]+1);
        dfHmm_Acts["GrpMembers"] = [aGrpMembers[i]]*len(dfHmm_Acts);
        dfHmm_Acts["Act"] = aHidden_States;        
        if len(aGrpIDs[i])==1 and aGrpIDs[i][0]!=-1:
            dfHmm_Acts["GrpId"] = aGrpIDs[i]*len(dfHmm_Acts);
            dfHmm_Acts["GrpSize"] = aGrpSize[i]*len(dfHmm_Acts);
        else:
            dfHmm_Acts["GrpId"] = aGrpIDs[i];
            dfHmm_Acts["GrpSize"] = aGrpSize[i];
        dfGrp_Hmms = pd.concat([dfGrp_Hmms, dfHmm_Acts]);
#         dfGrp_Hmms["Acts"][dfGrp_Hmms.index[i]] = str(aSgmActs).translate(None,"[]");
    dfGrp_Hmms = dfGrp_Hmms[(dfGrp_Hmms["GrpId"]==-1) | (dfGrp_Hmms["GrpSize"]>1)];
    dfGrp_Hmms = dfGrp_Hmms[["Act", "Frame", "GrpId", "GrpMembers"]];
    dfGrp_Hmms = setGrpIds(dfGrp_Hmms);
#     dfGrp_Hmms = pd.read_csv("./dfGrp_Hmms.csv");
#     dfIndTracks = pd.read_csv("./dfIndTracks.csv");
#     reformat_dfGrpHmms(dfGrp_Hmms, dfIndTracks);    
    print "Time with HMMs: " + str(time.time()-t0);
#     print dfGrp_Hmms;
    dfGrp_Hmms.sort(["Frame"]).to_csv(sFileOut, index=False);
