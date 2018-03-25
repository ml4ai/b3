import matplotlib.pyplot as pl;
import numpy as np;
from sklearn import cluster, mixture;
import itertools
from scipy import linalg
import matplotlib as mpl
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KernelDensity
import scipy.cluster.hierarchy as hcluster
import warnings;

class ClusteringMngr(object):
    def __init__(self, actorMngr):
        self.fileOut = open("./output_Tracks.txt", "w");
        self.aActive_Actors = actorMngr.aActive_Actors;
        self.aActors = actorMngr.aActors;
        self.grpActorsMngr = GrpActorsMngr(self.aActors);
        
    def processActors(self):
        for actor in self.aActors.values():
            if actor.bMissing: continue;
            actData = str(actor.getActorData()).translate(None,"[],'") + "\n";
#             print str(actor.getActorData()).translate(None,"[],'");
            self.fileOut.write(actData);
            
    def plotActors(self):
        warnings.filterwarnings("ignore");
        for nFrame in range(4804,5400,1): #range(4994,4995,1): #4853,1): range(4804,5400,1)
            aX, aY, aVX, aVY, aId = [], [], [], [], [];
            for actor in self.aActors.values():
                if nFrame in actor.aAllFrames:
                    nX, nY = actor.aAllX[actor.aAllFrames.index(nFrame)], actor.aAllY[actor.aAllFrames.index(nFrame)];
                    nVX, nVY = actor.aAllVX[actor.aAllFrames.index(nFrame)], actor.aAllVY[actor.aAllFrames.index(nFrame)];
                    if nX!='-' and nY!='-' and nVX!='-' and nVY!='-':
                        aX.append(nX);
                        aY.append(nY);
                        aVX.append(nVX);
                        aVY.append(nVY);
                        aId.append(str(actor.nTrackId));
            if len(aX)==0: continue;            
            self.plotClusters(nFrame, aId, aX, aY, aVX, aVY);
        warnings.resetwarnings();
        self.fileOut.close();
        
    def plotClusters(self, nFrame, aId, aX, aY, aVX, aVY):
        aVX, aVY = np.asarray(aVX)*50, np.asarray(aVY)*50;
#         aData = [];
#         for i in range(len(aX)):
#             aData.append([aX[i], aY[i]]);
        aData = np.asarray([aX,aY,aVX,aVY]).transpose(); #,aVX,aVY]).transpose();
#         aData = [[np.asarray([aX]).transpose()], [np.asarray([aY]).transpose()]];
#         aData = np.asarray([aX,aY]).transpose();
#         aData = StandardScaler().fit_transform(aData);
        algorithm = cluster.DBSCAN(eps=50, min_samples=2);
#         algorithm = cluster.SpectralClustering(n_clusters=5, eigen_solver='arpack', affinity="rbf")
#         algorithm = cluster.MeanShift(bandwidth=40, bin_seeding=True); #print ms.bandwidth;
#         algorithm = cluster.MiniBatchKMeans(n_clusters=2)
#         algorithm = mixture.GMM(n_components=3, covariance_type='full', n_iter=100)
#         aData = aData*0.07-20;
#         aX, aY = aData[:,0], aData[:,1]
#         algorithm = mixture.DPGMM(n_components=len(aData), covariance_type='diag', alpha=10, n_iter=1)

        colors = np.array([x for x in 'bgrcmybgrcmybgrcmybgrcmyk']);
        colors = np.hstack([colors] * 20);
        algorithm.fit(aData);
#         try: algorithm.fit(aData);
#         except: print nFrame, aData;
        if hasattr(algorithm, 'labels_'): 
            y_pred = algorithm.labels_.astype(np.int)
        else: 
            y_pred = algorithm.predict(aData)
#         y_pred = hcluster.fclusterdata(aData, t=50, criterion="distance")
        y_pred = self.grpActorsMngr.fixGrpsId(y_pred, aId);
#         y_pred2 = self.grpActorsMngr.fixGrpsId([1,-1,0,-1,-1,0,-1,1],['3','6','75','140','19','149','124','125']);#y_pred, aId);
#         print y_pred2;
#         y_pred2 = self.grpActorsMngr.fixGrpsId([0,-1,1,-1,-1,1,-1,0],['3','6','75','140','19','149','124','125']);#y_pred, aId);
#         print y_pred2;
#         pl.hold(True);

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
        
        pl.scatter(aX, aY, color=colors[y_pred].tolist(), s=75, alpha=.5);
#         pl.hold(True);
        for label, grp, x, y in zip(aId, y_pred, aX, aY):
            if grp<0: text = label;
            else: text = label+" Grp:"+str(grp);
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
                
#         pl.xlim(-20, 720*.07-20);
#         pl.ylim(-20, 640*.07-20);
                
        pl.xlim(0, 720);
        pl.ylim(0, 640);
#         pl.show();
#         pl.savefig('./Figures/plot'+str(nFrame)+'.png');
        pl.pause(0.001);
        pl.clf();
        
class GrpActorsMngr(object):
    def __init__(self, aActors):
        self.aActors = aActors;
        self.aGrpActors = [];
        self.nLatestGrpId = -1;
    
    def fixGrpsId(self, aGrpIds, aActorsId):
        aNewGrpActors = [];
        aNewGrpIds = list(aGrpIds);
        nGrps = len(set(aGrpIds)) - (1 if -1 in aGrpIds else 0); # Num clusters, ignoring noise if present.
        dictGrps = {};
        for i,nGrpId in enumerate(aGrpIds):
            if nGrpId<0: continue;
            if not(dictGrps.has_key(nGrpId)): dictGrps[nGrpId] = [[aActorsId[i]],[i]]; #Create map of Grps
            else:  #Append to current Grp
                dictGrps[nGrpId][0].append(aActorsId[i]); #Append ActorId
                dictGrps[nGrpId][1].append(i); #Append Index Location of this Actor
        for i in range(nGrps):
            if not(dictGrps.has_key(i)): continue;
            currentGrp = self.getCurrentGrp(dictGrps[i][0]);
            if currentGrp==None:
                nGrpId = self.getPastGrpId(dictGrps[i][0]);
                newGrp = self.createNewGrp(dictGrps[i][0], nGrpId); #If Grp NOT found, Create New one
                aNewGrpActors.append(newGrp);
            else: #If Grp Found replace Ids with the ID of this Grp
                aNewGrpActors.append(currentGrp);
                for j in dictGrps[i][1]:
                    aNewGrpIds[j] = currentGrp.nGrpId;
        self.aGrpActors = aNewGrpActors;
        return aNewGrpIds;
    
    def getPastGrpId(self, aActorsId):
        for grpActors in self.aGrpActors:
            nMatches = len(set(aActorsId).intersection(set(grpActors.aActorsId)))
            nGrp1 = nMatches/float(len(aActorsId));
            nGrp2 = nMatches/float(len(grpActors.aActorsId));
            if nGrp1>0.5 and nGrp2>0.5:
                return grpActors.nGrpId;
        return -1;
            
    def createNewGrp(self, aActorsId, nGrpId):
        if nGrpId<0: 
            self.nLatestGrpId = self.nLatestGrpId + 1;
            nGrpId = self.nLatestGrpId;
        aActors = [];
        for actorId in aActorsId:
            aActors.append(self.aActors[int(actorId)]);
        newGrpActors = GrpActors(aActors, nGrpId);
#         self.aGrpActors.append(newGrpActors);
        return newGrpActors;
    
    def getCurrentGrp(self, aActorsId):
        aActorsId.sort();
        for grpActors in self.aGrpActors:
            if aActorsId==grpActors.aActorsId:
                return grpActors;
        return None;
        
class GrpActors(object):
    def __init__(self, aActors, nGrpId):
        self.nGrpId = nGrpId;
        self.aActorsId = [];
        self.aActors = aActors;
        for actor in aActors:
            self.aActorsId.append(str(actor.nTrackId));
        self.aActorsId.sort();
        
    def addMember(self, actor):
        self.aActors.append(actor);
        self.aActorsId.append(str(actor.nTrackId));
        self.aActorsId.sort();
                        