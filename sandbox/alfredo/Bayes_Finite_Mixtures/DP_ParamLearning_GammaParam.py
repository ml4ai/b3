from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np
import pymc as pm;
import warnings;

def run_DP():
    aD = [-10,-9,10,11,20,21,42,43]; #Data Points
#     nA, nC = 3, 3; #Alpha & Max No. Clusters
    nC = 5;
    nPts = len(aD)+1;
    #Clusters
    aUh = [pm.Uniform('UnifH'+str(i), lower=-50, upper=50) for i in range(nC)];  # @UndefinedVariable
#     Uh = pm.Uniform('UnifH', lower=-50, upper=60);  # @UndefinedVariable
    aNc = [pm.Normal('NormC'+str(i), mu=aUh[i], tau=1) for i in range(nC)];  # @UndefinedVariable
    #Dirichlet & Categorical Nodes
    Gam = pm.Uniform('UnifG', lower=0, upper=15);  # @UndefinedVariable
#     Gam = pm.Gamma('Gamma', alpha=2.5, beta=2);  # @UndefinedVariable
    Dir = pm.Dirichlet('Dirichlet', theta=[Gam/nC]*nC);  # @UndefinedVariable
    aC = [pm.Categorical('Cat'+str(i), Dir) for i in range(nPts)];  # @UndefinedVariable
    aL = [pm.Lambda('p_Norm'+str(i), lambda k=aC[i], aNcl=aNc: aNcl[int(k)]) for i in range(nPts)];  # @UndefinedVariable
    #Points
    aN = [pm.Normal('NormX'+str(i), mu=aL[i], tau=1, observed=True, value=aD[i]) for i in range(nPts-1)];  # @UndefinedVariable
    Nz = pm.Normal('NormZ',  mu=aL[-1], tau=1);  # @UndefinedVariable
    return np.concatenate([[Nz,Dir,Gam],aUh,aNc,aC,aN]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_DP();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=4, aShow=range(8));
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph9.pdf");
