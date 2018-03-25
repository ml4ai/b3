from __future__ import division;
from MySampler_GP_Prior import getKernel, getMean;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def getModel(t):
    k = getKernel(3, t);
    mu = getMean(0, t);
#     k2 = np.multiply(np.eye(len(k)-1),k[:-1,:-1]);
#     k2 = np.multiply(np.eye(len(k)),k);
    GP1 = pm.MvNormalCov('GP1', mu=mu, C=k); #@UndefinedVariable
    GP2 = pm.MvNormalCov('GP2', mu=GP1[:-2], C=np.eye(len(k)-2)*50); #@UndefinedVariable
    GP3 = pm.MvNormalCov('GP3', mu=GP1[-2:], C=np.eye(2)*50, observed=True, value=[1000,1000]); #@UndefinedVariable
#     GP3 = pm.Normal('GP3', mu=GP1[-1], tau=1/k[-1,-1]); #@UndefinedVariable
    return pm.Model([GP1, GP2, GP3]);

def sample_MCMC(model, nSamples): #Sample   
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    return mcmc;

def plot_SP_Histograms(mcmc, t):
    def setup_Plot(sTitle, nMaxY, aRangeX):
        pl.title(sTitle);
        pl.gca().set_xlim(0,nMaxY);
        pl.gca().set_ylim(aRangeX[0],aRangeX[1]);
        pl.gca().set_xticks([]);
#         pl.gca().set_yticks([]);
    gp1_Samples = mcmc.trace('GP1')[:];
    gp2_Samples = mcmc.trace('GP2')[:];
#     gp3_Samples = mcmc.trace('GP3')[:];
    nSamples, nT = np.shape(gp1_Samples);
    aW = np.ones(nSamples)*(1/nSamples);
    aRangeX = [np.min(np.hstack([gp1_Samples, gp2_Samples])), 
               np.max(np.hstack([gp1_Samples, gp2_Samples]))];
    for i in range(nT):
        #Gaussian Process 1
        pl.subplot2grid((2,nT), (0,i));
        pl.hist(gp1_Samples[:,i], bins=100, weights=aW, orientation='horizontal');
        setup_Plot("{:.1f}".format(t[i]), 0.04, aRangeX);        
        #Gaussian Process 2
        pl.subplot2grid((2,nT), (1,i));
        if i<nT-2: aSamples = gp2_Samples[:,i];
        else: continue;
#         else: aSamples = gp3_Samples[:,i-(nT-2)];
        pl.hist(aSamples, bins=100, weights=aW, orientation='horizontal');
        setup_Plot("{:.1f}".format(t[i]), 0.04, aRangeX);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True);
    t = np.linspace(0.1,50,10);
    mcmc = sample_MCMC(getModel(t), 1000);
    plot_SP_Histograms(mcmc, t);
    