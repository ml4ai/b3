from sklearn.neighbors import KernelDensity;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;

def sample_MCMC(model, nSamples, bShow_PGM=False):
    #Sample
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    #Show Graphical Model
    if bShow_PGM:
        graph = pm.graph.graph(model);
        graph.write_pdf("./graph.pdf");
    return mcmc;

def sort_Nodes(aNodes):
    mNodes, aNodes_Out = {}, [];
    for n in aNodes: mNodes[int(n.__name__.split("-")[0])] = n;
    for i in np.sort(mNodes.keys()): aNodes_Out.append(mNodes[i]);
    return aNodes_Out;

def plot_Samples(mcmc, aBins, aKDE=[], aRowCols=[], aShow=[]):
    mNodes, aKDE = {}, map(lambda i: i-1, aKDE);  
    #Show Nodes Data
    aNodes = sort_Nodes(list(mcmc.nodes));
    for i,node in enumerate(aNodes):
        if not(node.observed): 
            mNodes[i] = node;
            print node.__name__ + ":", node.stats()["mean"], node.value;
        else: print node.__name__ + ":", node.value;
    #Plot Histogram Samples
    if aRowCols==[]: aRowCols = [len(mNodes), 1];
    for k in mNodes.keys():
        if not mNodes[k].keep_trace: mNodes.pop(k);
        elif aShow!=[] and not k in aShow: mNodes.pop(k);
    for i,k in enumerate(mNodes.keys()):
        node_Samples = mcmc.trace(mNodes[k].__name__)[:];
        nSamples = float(len(node_Samples));
        pl.subplot(aRowCols[0], aRowCols[1], i+1);
        pl.title(mNodes[k].__name__);
        bKDE = aKDE!=[] and k in aKDE;
        bDirichlet = type(mNodes[k])==pm.Dirichlet; #@UndefinedVariable
        if bDirichlet:
            node_Samples = np.hstack([node_Samples, 1-np.sum(node_Samples,1)[:,np.newaxis]]);
        nDims = 1 if len(np.shape(node_Samples))==1 else np.size(node_Samples,1);
        #Show KDE
        if bKDE: kdePlot(node_Samples);
        #Show Dirichlet Histogram (Non-KDE)
        elif bDirichlet: multiHist_Plot(node_Samples, aBins[k], nDims);
        #If Samples are in 1D, show Histogram
        elif nDims==1: pl.hist(node_Samples, aBins[k], weights=np.ones(nSamples)*(1/nSamples));
        #If Samples are in 2D, show Histogram-2D
        elif nDims==2: pl.hist2d(node_Samples[:,0], node_Samples[:,1], aBins[k]);
    pl.show();
    
def multiHist_Plot(aSamples, nBins, nDims):
    aLbls = map(lambda j: str(j+1), range(nDims));
    pl.hist(aSamples, nBins, alpha=0.8, histtype='stepfilled', label=aLbls);
    pl.legend(fancybox=True, loc='upper center', ncol=4);
    
def kdePlot(aSamples, bwidth=0.07):
    nIdx = len(np.shape(aSamples));
    if nIdx==1: nSamples, nDims = len(aSamples), 1;
    else: nSamples, nDims = np.shape(aSamples);
    aX = np.vstack([0,np.linspace(0,1,nSamples)[:,np.newaxis],1]);
    pl.hold(True);
    for i in range(nDims):
        kde = KernelDensity(kernel='gaussian', bandwidth=bwidth);
        if nIdx==1: kde.fit(aSamples[:,np.newaxis]);
        else: kde.fit(aSamples[:,i][:,np.newaxis]);
        y = np.exp(kde.score_samples(aX));
        y[0], y[-1] = 0,0;
        pl.fill(aX, y, alpha=0.7, label=str(i+1));
    pl.legend(fancybox=True, loc='upper center', ncol=4);
    pl.hold(False);