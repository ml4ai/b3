from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np  # @UnusedImport
import pymc as pm;
import warnings;

def get_Models():
    #Full Model (Beta & Bernoulli)
    nA, nB = 2,1;
    aD = [0,1,1];
    Beta = pm.Beta('Beta', alpha=nA, beta=nB);  # @UndefinedVariable    
    BernD = [pm.Bernoulli('BernD_'+str(i), p=Beta, observed=True, value=aD[i]) for i in range(len(aD))];  # @UndefinedVariable @UnusedVariable
    BernQ = pm.Bernoulli('BernQ', p=Beta);  # @UndefinedVariable    
    #Collapsed Model (Bernoulli)
    nA2 = nA + sum(aD);
    nB2 = nB + len(aD) - sum(aD);
    nP = nA2/(nA2+nB2);
    BernQ2 = pm.Bernoulli('BernQ_2', p=nP);  # @UndefinedVariable    
    return np.concatenate([[Beta,BernQ,BernQ2],BernD]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = get_Models();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=1);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/Beta_Bernoulli_WithData.pdf");
