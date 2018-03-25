from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np
import pymc as pm;
import warnings;

def run_Bernoulli_Normal():
    aD = [0,1,2,8,9];
    nPts = len(aD)+1;
    #Cluster 1
    Uh1 = pm.Uniform('UnifH1', lower=-50, upper=50);  # @UndefinedVariable
    Nc1 = pm.Normal('NormC1', mu=Uh1, tau=1)#, observed=True, value=10);  # @UndefinedVariable
    #Cluster 2
    Uh2 = pm.Uniform('UnifH2', lower=-50, upper=50);  # @UndefinedVariable
    Nc2 = pm.Normal('NormC2', mu=Uh2, tau=1)#, observed=True, value=10);  # @UndefinedVariable
    #Beta & Bernoulli Nodes
    Bet = pm.Beta('Beta', alpha=1, beta=1);  # @UndefinedVariable
    aB = [pm.Bernoulli('Bern'+str(i), Bet) for i in range(nPts)];  # @UndefinedVariable
    aL = [pm.Lambda('p_Norm1'+str(i), lambda k=aB[i], c1=Nc1, c2=Nc2: [c1,c2][int(k)]) for i in range(nPts)];  # @UndefinedVariable
    #Points
    aN = [pm.Normal('NormX'+str(i), mu=aL[i], tau=1, observed=True, value=aD[i]) for i in range(nPts-1)];  # @UndefinedVariable
    Nz = pm.Normal('NormZ',  mu=aL[-1], tau=1);  # @UndefinedVariable
    return np.concatenate([[Nz,Nc1,Nc2,Uh1,Uh2,Bet],aB,aN]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_Bernoulli_Normal();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 10000);
    pst.plot_Samples(mcmc, nBins=500);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph6.pdf");
