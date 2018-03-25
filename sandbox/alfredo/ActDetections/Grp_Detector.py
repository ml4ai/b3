import matplotlib.pyplot as pl;
import numpy as np;
from sklearn import cluster, mixture;  # @UnusedImport
import itertools;
from scipy import linalg;
import matplotlib as mpl;
from sklearn.preprocessing import StandardScaler;  # @UnusedImport
from sklearn.neighbors import KernelDensity;  # @UnusedImport
import scipy.cluster.hierarchy as hcluster;  # @UnusedImport
import pandas as pd;  # @UnusedImport
import warnings;  # @UnusedImport

class Grp_Detector(object):
    def __init__(self, dfIndAttrs, bSaveFrms, imgLims):
#         self.fileOut = open("./output_Tracks.txt", "w");
        self.aActors = dfIndAttrs;
        self.grpActorsMngr = GrpActorsMngr(self.aActors);
        np.random.seed(0); #Keep consistent the cluster process (start with same random seed)
        self.xLims, self.yLims = imgLims[0], imgLims[1];
        self.bSaveFrms = bSaveFrms; 
        self.eps = 2.7;
#     def getGrps(self):
#         dfGroups = [];
#         for nFrame, dfFrame in self.aActors.groupby(['Frame']):  # @UnusedVariable
#             dfFrame = dfFrame[["TrackId", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY", "Frame"]].dropna();
# #             print dfFrame[["TrackId", "AvgPosX", "AvgPosY", "SpeedX", "SpeedY", "Frame"]];
# #             aData = np.asarray(dfFrame).transpose();
# #             print aData;
#             if len(dfFrame)==0: continue;
#             aGrpsId = self.findClusters(dfFrame);            
#             dfGroupsTmp = dfFrame[["TrackId", "Frame"]];
#             dfGroupsTmp["GrpId"] = pd.Series(aGrpsId, dfGroupsTmp.index);
#             dfGroups = dfGroupsTmp if len(dfGroups)==0 else dfGroups.append(dfGroupsTmp);
# #         print dfGroups;
#             
#         return dfGroups;
        
    def findClusters(self, dfFrame):
        aVX, aVY = np.asarray(dfFrame["SpeedX"])*60, np.asarray(dfFrame["SpeedY"])*60; #50 (Max-Walk-Speed = 0.04)
        aX, aY = np.asarray(dfFrame["AvgPosX"]), np.asarray(dfFrame["AvgPosY"]);
        aId = np.asarray(dfFrame["TrackId"]);
        nFrame = dfFrame["Frame"].iloc[0];  # @UnusedVariable
#         aData = [];
#         for i in range(len(aX)):
#             aData.append([aX[i], aY[i]]);
        aData = np.asarray([aX,aY,aVX,aVY]).transpose(); #,aVX,aVY]).transpose();
#         print aData;
#         return;
#         aData = [[np.asarray([aX]).transpose()], [np.asarray([aY]).transpose()]];
#         aData = np.asarray([aX,aY]).transpose();
#         aData = StandardScaler().fit_transform(aData);
        algorithm = cluster.DBSCAN(eps=self.eps, min_samples=2);
#         algorithm = cluster.SpectralClustering(n_clusters=5, eigen_solver='arpack', affinity="rbf")
#         algorithm = cluster.MeanShift(bandwidth=40, bin_seeding=True); #print ms.bandwidth;
#         algorithm = cluster.MiniBatchKMeans(n_clusters=2)
#         algorithm = mixture.GMM(n_components=3, covariance_type='full', n_iter=100)
#         aData = aData*0.07-20;
#         aX, aY = aData[:,0], aData[:,1]
#         algorithm = mixture.DPGMM(n_components=len(aData), covariance_type='diag', alpha=10, n_iter=1)

#         colors = np.array([x for x in 'bgrcmybgrcmybgrcmybgrcmyk']);
#         colors = np.hstack([colors] * 20);
        algorithm.fit(aData);
#         try: algorithm.fit(aData);
#         except: print nFrame, aData;
        if hasattr(algorithm, 'labels_'): 
            y_pred = algorithm.labels_.astype(np.int);
        else: 
            y_pred = algorithm.predict(aData);
#         y_pred = hcluster.fclusterdata(aData, t=50, criterion="distance")
#         if len(self.grpActorsMngr.aGrpActors)>0:
#             print "[Before] Frm:", int(nFrame), "nGrpId:", self.grpActorsMngr.aGrpActors[0].nGrpId, y_pred;
        y_pred = self.grpActorsMngr.fixGrpsId(y_pred, aId);
#         if len(self.grpActorsMngr.aGrpActors)>0:
#             print "[After] Frm:", int(nFrame), "nGrpId:", self.grpActorsMngr.aGrpActors[0].nGrpId, y_pred;
#         y_pred2 = self.grpActorsMngr.fixGrpsId([1,-1,0,-1,-1,0,-1,1],['3','6','75','140','19','149','124','125']);#y_pred, aId);
#         print y_pred2;
#         y_pred2 = self.grpActorsMngr.fixGrpsId([0,-1,1,-1,-1,1,-1,0],['3','6','75','140','19','149','124','125']);#y_pred, aId);
#         print y_pred2;
#         pl.hold(True);
        if self.bSaveFrms:
            self.plotClusters(algorithm, aData, y_pred, aId, aX, aY, nFrame);
        if (nFrame) % 100==0: print "Frame:", int(nFrame);
        return y_pred;

    def plotClusters(self, algorithm, aData, y_pred, aId, aX, aY, nFrame):
        colors = np.array([x for x in 'bgrcmybgrcmybgrcmybgrcmyk']);
        colors = np.hstack([colors] * 20);

# #         xKDE, yKDE = [], [];
# #         for i,yLbl in enumerate(y_pred):
# #             if yLbl >= 0:
# #                 xKDE.append(aX[i]);
# #                 yKDE.append(aY[i]);
# #         aDataKDE = np.asarray([xKDE,yKDE]).transpose();
# #         kde = KernelDensity(bandwidth=10, kernel='gaussian');
# #         kde.fit(aDataKDE);
# #         xk,yk = np.mgrid[0:720+10:10,0:640+10:10];
# #         xx = np.c_[xk.ravel(), yk.ravel()];
# #         zk = kde.score_samples(xx);
# #         zk = 1-np.log(-zk);
# #         zk = zk.reshape(xk.shape);
# #         pl.pcolormesh(xk,yk,zk, cmap = pl.get_cmap('gray'));
        
        pl.scatter(aX, aY, color=colors[y_pred].tolist(), s=5, alpha=1); #s=75, alpha=.5
#         pl.hold(True);
        for label, grp, x, y in zip(aId, y_pred, aX, aY):
            if grp<0: text = str(int(label));
            else: text = str(int(label))+" Grp: "+str(grp)+"";
            pl.annotate(text, xy=(x,y), xytext=(-10,10), textcoords='offset points');
            
        if hasattr(algorithm, 'cluster_centers_'):
            centers = algorithm.cluster_centers_
            center_colors = colors[:len(centers)]
            pl.scatter(centers[:, 0], centers[:, 1], s=30, c=center_colors)
        
        if hasattr(algorithm, 'means_'):
#             centers = (algorithm.means_+20)*(1/0.07)
            centers = algorithm.means_
            center_colors = colors[:len(centers)]
            pl.scatter(centers[:, 0], centers[:, 1], s=30, c=center_colors)
            #Covariances
            color_iter = itertools.cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
            plotAxis = pl.gca();
            for i, (mean, covar, color) in enumerate(zip(
                    algorithm.means_, algorithm._get_covars(), color_iter)):
#                 mean = (mean+20)*(1/0.07);
                v, w = linalg.eigh(covar)
                u = w[0] / linalg.norm(w[0])
                # As DP will not use every component it has access to, unless
                # it needs it, we shouldn't plot the redundant components.
                if not np.any(np.asarray(y_pred) == i): continue
                pl.scatter(aData[y_pred == i, 0], aData[y_pred == i, 1], .8, color=color)
                # Plot an ellipse to show the Gaussian component
                angle = np.arctan(u[1] / u[0])
                angle = 180 * angle / np.pi  # convert to degrees
                ell = mpl.patches.Ellipse(mean, v[0], v[1], 180 + angle, color=color)
                ell.set_clip_box(plotAxis.bbox)
                ell.set_alpha(0.5)
                plotAxis.add_artist(ell)

        #Show Radius of each Track Object
        axes = pl.axes();
        for x,y,l in zip(aX,aY,y_pred):
            circle = pl.Circle((x,y), radius=self.eps, color=colors[l].tolist(), alpha=.2);
            axes.add_patch(circle);
                
#         pl.xlim(-20, 720*.07-20);
#         pl.ylim(-20, 640*.07-20);
                
        pl.title("Frame: "+str(int(nFrame)));
        pl.xlim(self.xLims[0], self.xLims[1]); #pl.xlim(0, 720);
        pl.ylim(self.yLims[0], self.yLims[1]); #pl.ylim(0, 640);
        pl.ion();
        #pl.show();
        if self.bSaveFrms:
            pl.savefig('./Figures/plot'+str(int(nFrame))+'.png');
        #pl.pause(0.1);
        pl.clf();
        
class GrpActorsMngr(object):
    def __init__(self, aActors):
        self.aActors = aActors;
        self.aGrpActors = []; #List of instances GrpActors
        self.nLatestGrpId = -1;
    
    def fixGrpsId(self, aGrpIds, aActorsId):        
        aNewGrpActors = [];
        aNewGrpIds = list(aGrpIds);
        nGrps = len(set(aGrpIds)) - (1 if -1 in aGrpIds else 0); # Num clusters, ignoring noise if present.
        dictGrps = {};
        #Maintain a Dictionary (Map of: GrpId -> [[List of TrackIDs],[Idxs in List]]) of all Grps found in this Frame
        for i,nGrpId in enumerate(aGrpIds): #For each person in this Frame
            if nGrpId<0: continue;
            if not(dictGrps.has_key(nGrpId)): dictGrps[nGrpId] = [[aActorsId[i]],[i]]; #Create map of Grps
            else:  #Append to current Grp
                dictGrps[nGrpId][0].append(aActorsId[i]); #Append ActorId
                dictGrps[nGrpId][1].append(i); #Append Index Location of this Actor
        #Check if Grp already exists, if not (it's new or grp members changed), then 
        for grpID in range(nGrps): #For each Group's ID found in this frame
            if not(dictGrps.has_key(grpID)): continue;
            currentGrp = self.getCurrentGrp(dictGrps[grpID][0]); #Check if this Grp already exists
            if currentGrp==None: #If it's (New Grp) or (Grp Members changed), then create Grp with correct IDs
                nGrpId = self.getPastGrpId(dictGrps[grpID][0]); #Check if Grp members changed (past ID) or it's New Grp (-1)
                newGrp = self.createNewGrp(dictGrps[grpID][0], nGrpId); #If Grp is New (nGrpId=-1), use new ID, else keep same past ID
                aNewGrpActors.append(newGrp);
                currentGrp = newGrp;
            else: #If same Grp is Found, keep its past ID (replace ID found in this frame with the ID already given)
                aNewGrpActors.append(currentGrp);
            #Fix the correct Grp Memberships (for each person with a Grp Membership)
            for j in dictGrps[grpID][1]: #For each Idx (from Grp Memberships list), fix their correct Grp Membership
                aNewGrpIds[j] = currentGrp.nGrpId; #Change to correct Grp Membership
        self.aGrpActors = aNewGrpActors;
        return aNewGrpIds;
    
    #Check if Grp members changed (past ID) or it's New Grp (-1)
    def getPastGrpId(self, aActorsId):
        for grpActors in self.aGrpActors: #For each stored Grp (past frm) check if majority (current frm) are still there
            nMatches = len(set(aActorsId).intersection(set(grpActors.aActorsId)))
            nGrp1 = nMatches/float(len(aActorsId));
            nGrp2 = nMatches/float(len(grpActors.aActorsId));
            if nGrp1>0.5 and nGrp2>0.5: #If majority stayed in past & current frame, then keep GrpID already had before
                return grpActors.nGrpId; #Keep same stored GrpID (if majority is still here)
        return -1; #Else, this detected Grp (at current frm) must be completely new, so create new one (by returning -1)
            
    #If Grp is New (nGrpId=-1), then use New ID, else keep same past ID
    def createNewGrp(self, aActorsId, nGrpId):
        if nGrpId<0: 
            self.nLatestGrpId = self.nLatestGrpId + 1;
            nGrpId = self.nLatestGrpId; #Use New Grp ID
#         aActors = [];
#         for actorId in aActorsId:
#             aActors.append(self.aActors["TrackId"==int(actorId)]);
        newGrpActors = GrpActors(aActorsId, nGrpId); #Create Grp with New or same Past ID
#         self.aGrpActors.append(newGrpActors);
        return newGrpActors;
    
    #Check if this Grp already exists
    def getCurrentGrp(self, aActorsId):
        aActorsId.sort();
        for grpActors in self.aGrpActors:
            if aActorsId==grpActors.aActorsId:
                return grpActors;
        return None;
        
class GrpActors(object):
    def __init__(self, aActorsId, nGrpId):
        self.nGrpId = nGrpId;
        self.aActorsId = [];
        self.aActors = aActorsId;
        for nTrackId in aActorsId:
            self.aActorsId.append(nTrackId); #str(nTrackId));
        self.aActorsId.sort();
        
#     def addMember(self, actor):
#         self.aActors.append(actor);
#         self.aActorsId.append(str(actor.nTrackId));
#         self.aActorsId.sort();
                        