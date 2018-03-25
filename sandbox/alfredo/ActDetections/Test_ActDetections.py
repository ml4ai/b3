from BB_Observations import BB_Observations;
import warnings;
import numpy as np;
import time, sys;
import pandas as pd;

def detect_GetIn(dfIndAttrs, nMaxDist=5, nWinLen=10):
    dfIndAttrs["GetIn"] = ""; #Create Column "GetIn"
    dfPersons = dfIndAttrs[dfIndAttrs["ObjType"]=="Person"];  #Get Table of ONLY Persons
    #For each PersonId
    for nPersonId, dfPerson in dfPersons.groupby(["TrackId"]):
        #Get Last Person's Position
        iLast = dfPerson.index[-1];
        nX, nY = dfPerson["PosX"][iLast], dfPerson["PosY"][iLast];
        #Get nWinLen Frms after Person's Track Ended (filtering to ONLY Vehicles)
        nLastFrm = dfPerson["Frame"][iLast];
        dfWinFrms = dfIndAttrs[(dfIndAttrs["Frame"]>=nLastFrm) & 
                           (dfIndAttrs["Frame"]<=nLastFrm+nWinLen) &
                           ((dfIndAttrs["ObjType"]=="Vehicle") |
                            (dfIndAttrs["ObjType"]=="Motorcyclist") |
                            (dfIndAttrs["ObjType"]=="Bicyclist"))];
        #For each Vehicle
        for nVehicleId, dfVehicle in dfWinFrms.groupby(["TrackId"]):
            #Get Distance(Person to Vehicle)
            iFirst = dfVehicle.index[0];
            nX2, nY2 = dfVehicle["PosX"][iFirst], dfVehicle["PosY"][iFirst];
            nDist = getDist([nX,nY], [nX2,nY2]);
            if nDist <= nMaxDist:
                #Write Label "{ObjType}_{ObjId}" (in Last X Frms of Person's Rows)
                nWin_LastFrms = 20;
                dfPerson_LastFrms = dfPerson[(dfIndAttrs["Frame"]>nLastFrm-nWin_LastFrms) & 
                           (dfIndAttrs["Frame"]<=nLastFrm)];
                sLbl = dfVehicle["ObjType"][iFirst]+"_"+str(int(dfVehicle["TrackId"][iFirst]));
                dfPerson_LastFrms["GetIn"] = sLbl;
                dfIndAttrs.update(dfPerson_LastFrms);
                nFrm = int(dfVehicle["Frame"][iFirst]);
                print "GetIn: PersonId ["+str(int(nPersonId))+"], VehicleId ["+ \
                    str(int(nVehicleId))+"], Frame ["+str(nFrm)+"], Dist ["+str(nDist)+"]";
#             else:
#                 print "GetIn Failed, Dist:", nDist;
    return dfIndAttrs;

def detect_GetOut(dfIndAttrs, nMaxDist=5, nWinLen=10):
    dfIndAttrs["GetOut"] = ""; #Create Column "GetOut"
    dfPersons = dfIndAttrs[dfIndAttrs["ObjType"]=="Person"];  #Get Table of ONLY Persons
    #For each PersonId
    for nPersonId, dfPerson in dfPersons.groupby(["TrackId"]):
        #Get First Person's Position
        iFirst = dfPerson.index[0];
        nX, nY = dfPerson["PosX"][iFirst], dfPerson["PosY"][iFirst];
        #Get nWinLen Frms before Person's Track Started (filtering to ONLY Vehicles)
        nFirstFrm = dfPerson["Frame"][iFirst];
        dfWinFrms = dfIndAttrs[(dfIndAttrs["Frame"]>nFirstFrm-nWinLen) & 
                           (dfIndAttrs["Frame"]<=nFirstFrm) &
                           ((dfIndAttrs["ObjType"]=="Vehicle") |
                            (dfIndAttrs["ObjType"]=="Motorcyclist") |
                            (dfIndAttrs["ObjType"]=="Bicyclist"))];
        #For each Vehicle
        for nVehicleId, dfVehicle in dfWinFrms.groupby(["TrackId"]):
            #Get Distance(Person to Vehicle)
            iLast = dfVehicle.index[-1];
            nX2, nY2 = dfVehicle["PosX"][iLast], dfVehicle["PosY"][iLast];
            nDist = getDist([nX,nY], [nX2,nY2]);
            if nDist <= nMaxDist:
                #Write Label "{ObjType}_{ObjId}" (in Last X Frms of Person's Rows)
                nWin_LastFrms = 20;
                dfPerson_FirstFrms = dfPerson[(dfIndAttrs["Frame"]>=nFirstFrm) & 
                           (dfIndAttrs["Frame"]<=nFirstFrm+nWin_LastFrms)];
                sLbl = dfVehicle["ObjType"][iLast]+"_"+str(int(dfVehicle["TrackId"][iLast]));
                dfPerson_FirstFrms["GetOut"] = sLbl;
                dfIndAttrs.update(dfPerson_FirstFrms);
                nFrm = int(dfVehicle["Frame"][iLast]);                
                print "GetOut: PersonId ["+str(int(nPersonId))+"], VehicleId ["+ \
                    str(int(nVehicleId))+"], Frame ["+str(nFrm)+"], Dist ["+str(nDist)+"]";
#             else:
#                 print "GetOut Failed, Dist:", nDist;
    return dfIndAttrs;

def detect_Carry(dfIndAttrs, nMaxDist=5):
    dfIndAttrs["Carry"] = "";
    dfObjects = dfIndAttrs[dfIndAttrs["ObjType"]=="Object"];  #Get Table of ONLY Objects
    #For each ObjectId
    for nObjectId, dfObject in dfObjects.groupby(["TrackId"]):
        #Initializing Data
        nCarry, nMinPersonId = 0, -1;
        nInitFrm, nMinDist = -1, sys.maxint;
        nLastFrm = dfObject["Frame"][dfObject.index[-1]];
        bOwnerFound = False;
        #For each Frame (of this Object)
        for iObj in dfObject.index:
            #Get Object Data (Frm, Pos, Type)
            nFrm = dfObject["Frame"][iObj];
            aObjPos = [dfObject["PosX"][iObj], dfObject["PosY"][iObj]];
            sObjType = dfObject["ObjType"][iObj];
            if bOwnerFound==True:
                #Get Person's Current Distance from Object
                dfPersonFrm = dfIndAttrs[(dfIndAttrs["TrackId"]==nMinPersonId) &
                                         (dfIndAttrs["Frame"]==nFrm)];
                nDist = -1;
                if len(dfPersonFrm)>0:
                    iFirst = dfPersonFrm.index[0];
                    nX = dfPersonFrm["PosX"][iFirst];
                    nY = dfPersonFrm["PosY"][iFirst];
                    aPos = [nX, nY];
                    nDist = getDist(aPos, aObjPos);
                #If Distance > Threshold (or Person Finished), then Update Carry of Past Frms
                if nDist > nMaxDist or len(dfPersonFrm)==0 or nFrm==nLastFrm:
                    #Update Person's Carry
                    dfPersonSgm = dfIndAttrs[(dfIndAttrs["TrackId"]==nMinPersonId) &
                                             (dfIndAttrs["Frame"]>=nInitFrm) & 
                                             (dfIndAttrs["Frame"]<nFrm)];
                    dfPersonSgm["Carry"] = sObjType+"_"+str(int(nObjectId));
                    dfIndAttrs.update(dfPersonSgm);
                    #Update Object's Carry
                    dfObjSgm = dfIndAttrs[(dfIndAttrs["TrackId"]==nObjectId) &
                                          (dfIndAttrs["Frame"]>=nInitFrm) & 
                                          (dfIndAttrs["Frame"]<nFrm)];
                    dfObjSgm["Carry"] = str(int(nMinPersonId))+"_"+str(int(nCarry));
                    dfIndAttrs.update(dfObjSgm);
                    bOwnerFound = False;
                    print "Detected Carry. Frame Range "+ str([int(nInitFrm),int(nFrm)]) \
                        +", PersonId ["+str(int(nMinPersonId)) \
                        +"], ObjectId ["+str(int(nObjectId)) \
                        +"], Dist:", nDist;
            elif bOwnerFound==False:
                nMinPersonId, nMinDist = getMinDist(dfIndAttrs, nFrm, aObjPos);                
                if nMinDist <= nMaxDist:
#                     print nMinPersonId, nMinDist, int(nFrm);
                    nInitFrm = nFrm;
                    nCarry += 1;
                    bOwnerFound = True;
    return dfIndAttrs;

def detect_Exchange(dfIndAttrs):
    #Get All Object's Carry Activities
    dfObjects = dfIndAttrs[(dfIndAttrs["ObjType"]=="Object") &
                           (dfIndAttrs["Carry"]!="")];
    #Get Carry's Frame Ranges, Person & ObjectId involved
    aFrmRanges, aPersonIds, aObjectIds, aExchanges = [], [], [], [];
    aInitFrms, aEndFrms = [], [];
    for sCarry, dfCarry in dfObjects.groupby(["Carry"]): #For each Carry
        nInitFrm = int(dfCarry["Frame"][dfCarry.index[0]]);
        nEndFrm = int(dfCarry["Frame"][dfCarry.index[-1]]);
        aInitFrms.append(nInitFrm);
        aEndFrms.append(nEndFrm);
        aFrmRanges.append([nInitFrm, nEndFrm]);
        aPersonIds.append(int(sCarry.split("_")[0]));
        aObjectIds.append(int(dfCarry["TrackId"][dfCarry.index[0]]));
    dfCarry = pd.DataFrame(columns=["InitFrm", "EndFrm", "ObjId", "PersonId"]);
    dfCarry["InitFrm"] = aInitFrms;
    dfCarry["EndFrm"] = aEndFrms;
    dfCarry["ObjId"] = aObjectIds;
    dfCarry["PersonId"] = aPersonIds;
    print dfCarry;
    #Get Exchange's Frame Ranges, Persons & ObjectId involved    
    for nObjId, dfObj in dfCarry.groupby(["ObjId"]):
        dfObj.sort(["InitFrm"]);
        for i in range(len(dfObj)-1):
            iR1, iR2 = dfObj.index[i], dfObj.index[i+1];
            aExchanges.append([nObjId, dfObj["PersonId"][iR1], dfObj["PersonId"][iR2], 
                           dfObj["InitFrm"][iR1], dfObj["EndFrm"][iR2]]);
    #Update Exchange Rows
    dfIndAttrs["Exchange"] = "";
    for aExchange in aExchanges:
        nObjectId = aExchange[0];
        nPersonId1, nPersonId2 = aExchange[1], aExchange[2];
        nFrameInit, nFrameEnd = aExchange[3], aExchange[4];
        #Update Person's Exchange
        dfPersons = dfIndAttrs[((dfIndAttrs["TrackId"]==nPersonId1) |
                                (dfIndAttrs["TrackId"]==nPersonId2)) &
                               (dfIndAttrs["Frame"]>=nFrameInit) &
                               (dfIndAttrs["Frame"]<=nFrameEnd)];
        dfPersons["Exchange"] = "Object_"+str(nObjectId)+"_From_"+str(nPersonId1)+ \
            "_To_"+str(nPersonId2);
        dfIndAttrs.update(dfPersons);
        #Update Object's Exchange
        dfObjects = dfIndAttrs[(dfIndAttrs["TrackId"]==nObjectId) &
                               (dfIndAttrs["Frame"]>=nFrameInit) &
                               (dfIndAttrs["Frame"]<=nFrameEnd)];
        dfObjects["Exchange"] = "From_"+str(nPersonId1)+"_To_"+str(nPersonId2);
        dfIndAttrs.update(dfObjects);
    print aExchanges;
    return dfIndAttrs;

def getMinDist(dfIndAttrs, nFrm, aObjPos):
    nMinDist = sys.maxint;
    nMinPersonId = -1;
    #Get Table of ONLY Persons at Frame nFrm
    dfPersons = dfIndAttrs[(dfIndAttrs["Frame"]==nFrm) &
                           (dfIndAttrs["ObjType"]=="Person")];
    #For each ObjectId
    for nPersonId, dfPerson in dfPersons.groupby(["TrackId"]):
        iFirst = dfPerson.index[0];
        nX = dfPerson["PosX"][iFirst];
        nY = dfPerson["PosY"][iFirst];
        aPos = [nX,nY];
        nDist = getDist(aPos, aObjPos);
        if nDist < nMinDist:
            nMinDist = nDist;
            nMinPersonId = nPersonId;
    return nMinPersonId, nMinDist;

def getDist(aPos1, aPos2):
    nX1, nY1 = aPos1;
    nX2, nY2 = aPos2;
    nDist = np.sqrt((nX1-nX2)**2 + (nY1-nY2)**2);
    return nDist;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
#     sFileDB = './PoL.s3db';
    sFileDB = './VIRAT_01.s3db';
    imgLims = [[-50,10],[-10,15]]; #[[0,700],[0,640]];
    bb_Detections = BB_Observations(sFileDB, bSaveFrms=True, imgLims=imgLims);
    dfRawData = bb_Detections.getRawData(sFileDB, 0,20655); #20655 #9075
#     dfRawData = bb_Detections.getRawData(sFileDB, 0, 700);
#     dfRawData = bb_Detections.getRawData(sFileDB, 4700, 5500);
#     dfRawData = dfRawData[dfRawData["ObjType"]==1]; #Filter to avoid Objects & Cars
    t0 = time.time();
    dfIndAttrs = bb_Detections.getIndAttrs(dfRawData.copy(), nWinLen=50);
    dfIndAttrs = detect_GetIn(dfIndAttrs);
    print "Time GetIn: " + str(time.time()-t0);
    dfIndAttrs = detect_GetOut(dfIndAttrs);
    print "Time GetOut: " + str(time.time()-t0);
    dfIndAttrs = detect_Carry(dfIndAttrs);
    print "Time Carry: " + str(time.time()-t0);
    dfIndAttrs = detect_Exchange(dfIndAttrs);
    print "Time Exchange: " + str(time.time()-t0);
    bb_Detections.dfIndAttrs = dfIndAttrs;
#     print dfIndAttrs[dfIndAttrs["ObjType"]=="Person"];    
#     dfIndAttrs = dfIndAttrs[dfIndAttrs["ObjType"]=="Person"]; #Filter to avoid Objects & Cars
    print "Time Detecting Activities: " + str(time.time()-t0);
    bb_Detections.store_IndAttrs();
    

    
    