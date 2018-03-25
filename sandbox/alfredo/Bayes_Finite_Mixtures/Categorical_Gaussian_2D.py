from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;
    
def getModel():
    C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3]); #@UndefinedVariable
#     C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3], observed=True, value=3); #@UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda n=C: np.select([n==0, n==1, n==2, n==3], [[-5,-5], [0,0], [5,5], [10,10]]), 
                    doc='Pr[Norm|Cat]');
    N = pm.MvNormal('2-Norm_2D', mu=p_N, tau=np.eye(2,2)); #@UndefinedVariable
#     N = pm.MvNormal('2-Norm', mu=p_N, tau=np.eye(2,2), observed=True, value=[2.5,2.5]); #@UndefinedVariable
    return pm.Model([C,N]);
    
def sample_MCMC(model, nSamples):
    #Sample
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
#     #Show Graphical Model
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph.pdf");
    return mcmc;

def plot_Samples(mcmc, aBins):
    mNodes = {};
    #Show Nodes Data
    aNodes = np.sort(list(mcmc.nodes));
    for i,node in enumerate(aNodes):
        if not(node.observed): 
            mNodes[i] = node;
            print node.__name__ + ":", node.stats()["mean"], node.value;
        else: print node.__name__ + ":", node.value;
    #Plot Histogram Samples
    for i,k in enumerate(mNodes.keys()):
        node_Samples = mcmc.trace(mNodes[k].__name__)[:];
        nSamples = float(len(node_Samples));
        pl.subplot(len(mNodes), 1, i+1);
        pl.title(mNodes[k].__name__);
        if len(np.shape(node_Samples))==1:
            pl.hist(node_Samples, aBins[k], weights=np.ones(nSamples)*(1/nSamples));
        else: pl.hist2d(node_Samples[:,0], node_Samples[:,1], aBins[k]);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = sample_MCMC(getModel(), 10000);    
    plot_Samples(mcmc, aBins=[4,100]);