from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np  # @UnusedImport
import pymc as pm;
import warnings;

def get_Models():
    #Full Model (Beta & Binomial)
    nN, nA, nB = 3,5,1;
    aD = [0,3,1];
    Beta = pm.Beta('Beta', alpha=nA, beta=nB);  # @UndefinedVariable    
    BinomD = [pm.Binomial('BinomD_'+str(i), n=nN, p=Beta, observed=True, value=aD[i]) for i in range(len(aD))];  # @UndefinedVariable @UnusedVariable
    BinomQ = pm.Binomial('BinomQ', n=nN, p=Beta);  # @UndefinedVariable    
    #Collapsed Model (Binomial)
    nA2 = nA + sum(aD);
    nB2 = nB + nN*len(aD) - sum(aD);
    BetaBinQ = pm.Betabin('BetaBinQ', n=nN, alpha=nA2, beta=nB2);  # @UndefinedVariable    
    return np.concatenate([[Beta,BinomQ,BetaBinQ],BinomD]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = get_Models();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=1);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/Beta_Binomial_WithData.pdf");
