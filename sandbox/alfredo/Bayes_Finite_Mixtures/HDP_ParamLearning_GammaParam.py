from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np
import pymc as pm;
import warnings;

def run_HDP():
    nC = 3; #Max No. Clusters
    Gam = pm.Uniform('Gamma0', lower=0, upper=15);  # @UndefinedVariable
    aDir = [Gam/nC]*nC;
    Dir0 = pm.Dirichlet('Dirichlet0', theta=aDir);  # @UndefinedVariable
    lDir0 = pm.Lambda('p_Dir0', lambda d=Dir0: np.concatenate([d,[1-sum(d)]]));  # @UndefinedVariable
    aNodes1 = get_DP('1', lDir0, [0,1, 20,21]);
    aNodes2 = get_DP('2', lDir0, [50,51, 70,71,72]);
    return np.concatenate([[Dir0],aNodes1,aNodes2]);

#Input: [lDir0] = Dirichlet Root, [aD] = Data Points
def get_DP(sDP, lDir0, aD):
    nPts = len(aD)+1;
    nC = len(lDir0.value);
    nMinD, nMaxD = min(aD), max(aD);
    #Clusters
    aUh = [pm.Uniform('UnifH'+str(i)+'_'+sDP, lower=nMinD-20, upper=nMaxD+20) for i in range(nC)];  # @UndefinedVariable
    aNc = [pm.Normal('NormC'+str(i)+'_'+sDP, mu=aUh[i], tau=1) for i in range(nC)];  # @UndefinedVariable
    #Dirichlet & Categorical Nodes
    Gam = pm.Uniform('Gamma1_'+sDP, lower=0, upper=15);  # @UndefinedVariable
    Dir = pm.Dirichlet('Dirichlet1_'+sDP, theta=lDir0*Gam);  # @UndefinedVariable
    aC = [pm.Categorical('Cat'+str(i)+'_'+sDP, Dir) for i in range(nPts)];  # @UndefinedVariable
    aL = [pm.Lambda('p_Norm'+str(i)+'_'+sDP, lambda k=aC[i], aNcl=aNc: aNcl[int(k)]) for i in range(nPts)];  # @UndefinedVariable
    #Points
    aN = [pm.Normal('NormX'+str(i)+'_'+sDP, mu=aL[i], tau=1, observed=True, value=aD[i]) for i in range(nPts-1)];  # @UndefinedVariable
    Nz = pm.Normal('NormZ_'+sDP,  mu=aL[-1], tau=1);  # @UndefinedVariable
    return np.concatenate([[Nz,Dir],aUh,aNc,aC,aN]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_HDP();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 1000);
    pst.plot_Samples(mcmc, nBins=500, nCols=4);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/HDP_ParamLearning_GammaParam.pdf");
