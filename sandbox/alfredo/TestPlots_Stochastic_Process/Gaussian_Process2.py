from __future__ import division;
from MySampler_GP_PostPred import getKernel, getMean;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def getModel(t, iObs):
    k = getKernel(3, t);
    mu = getMean(2, t);
    aNodes = [];
    GP1 = pm.MvNormalCov('GP1', mu=mu, C=k); #@UndefinedVariable
    aNodes.append(GP1);
    for i in range(len(t)):
        aNodes.append(pm.Normal('N'+str(i+1), mu=GP1[i], tau=1/50)); #@UndefinedVariable
        if i in iObs:
            aNodes.append(pm.Normal('oN'+str(i+1), mu=GP1[i], tau=1/50, observed=True, value=-100)); #@UndefinedVariable
    return pm.Model(aNodes);

def sample_MCMC(model, nSamples): #Sample   
    mcmc = pm.MCMC(model);
    mcmc.sample(nSamples, progress_bar=True);
    return mcmc;

def plot_SP_Histograms(mcmc, t, iObs):
    def setup_Plot(sTitle, nMaxY, aRangeX):
        pl.title(sTitle);
        pl.gca().set_xlim(0,nMaxY);
        pl.gca().set_ylim(aRangeX[0],aRangeX[1]);
        pl.gca().set_xticks([]);
#         pl.gca().set_yticks([]);
    gp1_Samples = mcmc.trace('GP1')[:];
    nSamples, nT = np.shape(gp1_Samples);
    aW = np.ones(nSamples)*(1/nSamples);
#     all_Samples = np.array(gp1_Samples).reshape(-1);
#     for i in range(nT):
#         if i not in iObs:
#             np.hstack([all_Samples, np.array(mcmc.trace('N'+str(i+1))[:])]);
#     aRangeX = [np.min(all_Samples), np.max(all_Samples)];
    aRangeX = [-300, 600];
    for i in range(nT):
        #Gaussian Process 1
        pl.subplot2grid((2,nT), (0,i));
        pl.hist(gp1_Samples[:,i], bins=100, weights=aW, orientation='horizontal');
        setup_Plot("{:.1f}".format(t[i]), 0.04, aRangeX);
        #Gaussian Process 2
        pl.subplot2grid((2,nT), (1,i));
        aSamples = mcmc.trace('N'+str(i+1))[:];
        pl.hist(aSamples, bins=100, weights=aW, orientation='horizontal');
        setup_Plot("{:.1f}".format(t[i]), 0.04, aRangeX);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True);
    t = np.linspace(0.1,50,10);
    iObs = [1,2,3,8,9];
    mcmc = sample_MCMC(getModel(t, iObs), 20000);
    plot_SP_Histograms(mcmc, t, iObs);
    