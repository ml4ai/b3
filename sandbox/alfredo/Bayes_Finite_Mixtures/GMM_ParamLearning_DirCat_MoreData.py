from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np
import pymc as pm;
import warnings;

def run_Categorical_Normal():
    nC = 3; #Num. Clusters
    aD = [0,1,8,9,20,21]; #Data Points
    nPts = len(aD)+1;
    #Clusters
    aUh = [pm.Uniform('UnifH'+str(i), lower=-50, upper=50) for i in range(nC)];  # @UndefinedVariable
    aNc = [pm.Normal('NormC'+str(i), mu=aUh[i], tau=1) for i in range(nC)];  # @UndefinedVariable
    #Dirichlet & Categorical Nodes
    Dir = pm.Dirichlet('Dirichlet', theta=[1]*nC);  # @UndefinedVariable
    aC = [pm.Categorical('Cat'+str(i), Dir) for i in range(nPts)];  # @UndefinedVariable
    aL = [pm.Lambda('p_Norm'+str(i), lambda k=aC[i], aNcl=aNc: aNcl[int(k)]) for i in range(nPts)];  # @UndefinedVariable
    #Points
    aN = [pm.Normal('NormX'+str(i), mu=aL[i], tau=1, observed=True, value=aD[i]) for i in range(nPts-1)];  # @UndefinedVariable
    Nz = pm.Normal('NormZ',  mu=aL[-1], tau=1);  # @UndefinedVariable
    return np.concatenate([[Nz,Dir],aUh,aNc,aC,aN]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_Categorical_Normal();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 1000);
    pst.plot_Samples(mcmc, nBins=500, nCols=3);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph7.pdf");
