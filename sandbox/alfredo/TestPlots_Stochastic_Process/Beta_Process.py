from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def getModel():
    nA, nB, nK, nT = 5, 2, 10, 10;  # @UnusedVariable
    nW=np.linspace(1,9,nT);
#     B = pm.Beta('1-Beta', alpha=[nA/nK]*nT, beta=[nB*(nK-1)/nK]*nT); #@UndefinedVariable
    B = pm.Beta('1-Beta', alpha=nW, beta=[nB*(nK-1)/nK]*nT); #@UndefinedVariable
#     Bern = pm.Bernoulli('2-Bern', np.linspace(0.1,0.9,nT)); #@UndefinedVariable
    return pm.Model([B]);
#     return pm.Model([B,Bern]);

def sample_MCMC(model, nSamples):
    #Sample
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    return mcmc;

def plot_SP(mcmc):
    sp_node = list(mcmc.nodes)[0];
    sp_Samples = mcmc.trace(sp_node.__name__)[:];
    nSamples, nT = np.shape(sp_Samples);
    aW = np.ones(nSamples)*(1/nSamples);
#     aHists = [];
    for i in range(nT):
        pl.subplot(1,nT, i+1);
        pl.title(str(i+1));
#         aHists.append(np.histogram(sp_Samples[i], bins=2, weights=aW)[0]);
        pl.hist(sp_Samples[:,i], bins=50, weights=aW, orientation='horizontal');
        pl.gca().set_xlim(0,0.2);
        pl.gca().set_xticks([]);
        pl.gca().set_yticks([]);
    pl.show();
        
#     print sp_Samples;
#     print nSamples, nT;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = sample_MCMC(getModel(), 1000);
    plot_SP(mcmc);
    