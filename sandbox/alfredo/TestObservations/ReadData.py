from BB_Observations import BB_Observations;
import warnings;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    sFileDB = './PoL.s3db';
    bb_Detections = BB_Observations(sFileDB);
    dfRawData = bb_Detections.getRawData(sFileDB, 0, 25);
    dfIndAttrs = bb_Detections.getIndAttrs(dfRawData.copy());
    [dfGroups, dfGrp_Attrs] = bb_Detections.getGrpAttrs(dfIndAttrs);
    dfIndGrp_Attrs = bb_Detections.getIndGrp_Attrs(dfIndAttrs, dfGrp_Attrs);
#     bb_Detections.getGrpAttrs(dfIndAttrs);
#     print dfGrps;
#     print dfGrp_Attrs;
    dfPairAttrs = bb_Detections.getPairAttrs(dfIndGrp_Attrs);
    print dfRawData[:8];
#     print dfIndAttrs[:8];
    aCols = ["TrackId", "Frame", "PosX", "PosY", "AvgPosX", "AvgPosY", "Speed", 
             "Acc", "Heading", "WithinDist", "Time_WithinDist"];
    aCols2 = ["TrackId", "Frame", "PosX", "PosY", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY",
         "Acc", "Heading", "GrpId"];
    print dfIndAttrs[aCols2][:31];
    print dfGrp_Attrs;
#     print dfPairAttrs[80:95];
    bb_Detections.storeResults();
    print "Finished!";