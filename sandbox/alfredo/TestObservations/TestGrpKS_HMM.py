from BB_Observations import BB_Observations;
import pandas as pd;
import warnings;
import numpy as np;
import hmm_ext;


def getHMM_Gait(obs_seq, nInitFrm):
    states = ["Stand", "Walk", "Run"];
    n_states = len(states);
    
    start_probability = np.array([0.3, 0.5, 0.2]);
    transition_probability = np.array([
      [0.6, 0.3, 0.1],
      [0.3, 0.5, 0.2],
      [0.2, 0.3, 0.5]
    ]);
    
    model = hmm_ext.NB_GammaHMM(n_components=n_states);
    model._set_startprob(start_probability);
    model._set_transmat(transition_probability);
    model._set_shapes(np.array([1,5,30]));
    model._set_locs(np.array([0,0,0]));
    model._set_scales(np.array([1,2,1]));
    
    # predict a sequence of hidden states based on visible states
    obs_seq = np.array(obs_seq)*3; #np.array([[0.0, 0.5, 0.1], [20,26,21], [8,9,4], [30,38,27], [10,30,1]]);
    logprob, hidden_states = model.decode(obs_seq, algorithm="viterbi");
    
    aHidden_States = map(lambda x: states[x], hidden_states);
    print "Observations:", obs_seq;
    print "Hidden States:", ", ".join(aHidden_States);
    print "Posterior:", np.exp(logprob);
    
    aSgmActs, aActData = [], [];
    sInitHiddenSt = aHidden_States[0];
    nInitSgm = nInitFrm;
    for i,sHiddenSt in enumerate(aHidden_States):
        if i==0: continue;
        if sHiddenSt!=sInitHiddenSt or i==len(aHidden_States)-1:
            aActData = (sInitHiddenSt, nInitSgm, (nInitFrm+i)-1);
            aSgmActs.append(aActData);
            sInitHiddenSt = sHiddenSt;
            nInitSgm = nInitFrm+i;
    print aSgmActs;



if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    sFileDB = './PoL.s3db';
    bb_Detections = BB_Observations(sFileDB);
    dfRawData = bb_Detections.getRawData(sFileDB, 0, 25);
    dfIndAttrs = bb_Detections.getIndAttrs(dfRawData.copy());
    [dfGroups, dfGrp_Attrs] = bb_Detections.getGrpAttrs(dfIndAttrs);
    aCols = ["TrackId", "Frame", "PosX", "PosY", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY",
         "Acc", "Heading", "GrpId"];
#     print dfGroups[aCols][:31];
#     print dfGrp_Attrs[pd.notnull(dfGrp_Attrs["EndFrm"])];
    dfGrps = dfGrp_Attrs[pd.notnull(dfGrp_Attrs["EndFrm"])];
    dfGrps = dfGrps[["GrpId", "InitFrm", "EndFrm"]];
#     print "---";
    aSegments = [];
    aInitFrms = [];
    for idx in dfGrps.index: #For each Grp Segment
        nGrpId = int(dfGrps["GrpId"][idx]);
        nInitFrm, nEndFrm = int(dfGrps["InitFrm"][idx]), int(dfGrps["EndFrm"][idx]);
        aInitFrms.append(nInitFrm);
#         print nGrpId, nInitFrm, nEndFrm;
        dfGrp_Segment = dfGroups[(dfGroups["GrpId"]==nGrpId) & (dfGroups["Frame"]>=nInitFrm) & 
                       (dfGroups["Frame"]<=nEndFrm)][["TrackId", "Frame", "Speed"]];
        aGrpSgm = [];
        for nFrm, dfFrm in dfGrp_Segment.groupby(["Frame"]):
            aFrmData = dfFrm["Speed"].tolist();
#             print dfFrm;
#             print aFrmData;
            aGrpSgm.append(aFrmData);
#         print aGrpSgm;
        aSegments.append(aGrpSgm);
#     print aSegments;
#     print "Semgents:", len(aSegments);
#     print "HMM-1 Frames:", len(aSegments[0]);
#     print "HMM-2 Frames:", len(aSegments[1]);
#     print "HMM-3 Frames:", len(aSegments[2]);
    print "HMM-1 Frames:", len(aSegments[0]), "InitFrame:", aInitFrms[0];
    print aInitFrms;
    print aSegments[0];
    getHMM_Gait(aSegments[0], aInitFrms[0]);
