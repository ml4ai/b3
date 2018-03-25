from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;
    
def getModel():
    C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3]); #@UndefinedVariable
#     C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3], observed=True, value=3); #@UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda n=C: np.select([n==0, n==1, n==2, n==3], [-5, 0, 5, 10]), 
                    doc='Pr[Norm|Cat]');
    N = pm.Normal('2-Norm', mu=p_N, tau=1); #@UndefinedVariable
#     N = pm.Normal('2-Norm', mu=p_N, tau=1, observed=True, value=2.5); #@UndefinedVariable
    return pm.Model([C,N]);
    
def sample_MCMC(model, nSamples):
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    return mcmc;

def plot_Samples(mcmc, aBins):
    mNodes = {};
    for i,node in enumerate(list(mcmc.nodes)):
        if not(node.observed): mNodes[i] = node;
        else: print node.__name__ + ":", node.value;
    for i,k in enumerate(mNodes.keys()):
        print mNodes[k].__name__ + ":", mNodes[k].stats()["mean"], mNodes[k].value;
        node_Samples = mcmc.trace(mNodes[k].__name__)[:];
        nSamples = float(len(node_Samples));
        pl.subplot(len(mNodes), 1, i+1);
        pl.title(mNodes[k].__name__);
        pl.hist(node_Samples, aBins[k], weights=np.ones(nSamples)*(1/nSamples));
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = sample_MCMC(getModel(), 10000);
    plot_Samples(mcmc, aBins=[2,500]);