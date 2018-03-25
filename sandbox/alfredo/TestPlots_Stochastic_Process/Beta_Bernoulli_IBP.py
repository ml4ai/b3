from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def getModel():
    nA, nB, nK, nT = 5, 2, 10, 10;  # @UnusedVariable
    nW=np.linspace(1,9,nT);
#     B = pm.Beta('Beta', alpha=[nA/nK]*nT, beta=[nB*(nK-1)/nK]*nT); #@UndefinedVariable
    B = pm.Beta('Beta', alpha=nW, beta=[nB*(nK-1)/nK]*nT); #@UndefinedVariable
    Bern = pm.Bernoulli('Bern', B); #@UndefinedVariable
    return pm.Model([B,Bern]);

def sample_MCMC(model, nSamples): #Sample   
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    return mcmc;

def plot_SP_Histograms(mcmc):
    def setup_Plot(sTitle, nMaxY):
        pl.title(sTitle);
        pl.gca().set_xlim(0,nMaxY);
        pl.gca().set_xticks([]);
        pl.gca().set_yticks([]);
    beta_Samples = mcmc.trace('Beta')[:];
    bern_Samples = mcmc.trace('Bern')[:];
    nSamples, nT = np.shape(beta_Samples);
    aW = np.ones(nSamples)*(1/nSamples);
    for i in range(nT):
        #Beta Process
        pl.subplot2grid((2,nT), (0,i));
        pl.hist(beta_Samples[:,i], bins=50, weights=aW, orientation='horizontal');
        setup_Plot(str(i+1), 0.1);
        #Bernoulli Process
        pl.subplot2grid((2,nT), (1,i));
        pl.hist(bern_Samples[:,i], bins=2, weights=aW, orientation='horizontal');
        setup_Plot(str(i+1), 1);
    pl.show();

def plot_SP_Samples(mcmc):
    def setup_Plot(sTitle, nMaxY):
        pl.title(sTitle);
        pl.gca().set_ylim(0,nMaxY);
        pl.gca().set_xticks([]);
        pl.gca().set_yticks([]);
    beta_Samples = mcmc.trace('Beta')[:];
    bern_Samples = mcmc.trace('Bern')[:];
    nT = np.shape(beta_Samples)[1];
    nS = 5;
    for i in range(nS):
        #Beta Process
        pl.subplot2grid((nS*2,1), (i,0));
        pl.bar(range(nT), beta_Samples[i,:]);
        setup_Plot(str(i+1), 1);
        #Bernoulli Process
        pl.subplot2grid((nS*2,1), (nS+i,0));
        pl.bar(range(nT), bern_Samples[i,:]);
        setup_Plot(str(i+1), 1.1);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = sample_MCMC(getModel(), 1000);
#     plot_SP_Samples(mcmc);
    plot_SP_Histograms(mcmc);
    