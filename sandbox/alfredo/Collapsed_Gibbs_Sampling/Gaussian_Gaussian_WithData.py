from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np  # @UnusedImport
import pymc as pm;
import warnings;

def get_Models():
    #Full Model (Gaussian & Gaussian)
    nMu0, nVar0, nVar = 0,1,1;
#     nTau0, nTau = 1,1;
    aD = [1.5, -2.4, -3.3];
    Norm = pm.Normal('Norm', mu=nMu0, tau=1/nVar0);  # @UndefinedVariable    
    NormD = [pm.Normal('NormD_'+str(i), mu=Norm, tau=1/nVar, observed=True, value=aD[i]) for i in range(len(aD))];  # @UndefinedVariable @UnusedVariable
    NormQ = pm.Normal('NormQ', mu=Norm, tau=1/nVar);  # @UndefinedVariable    
    #Collapsed Model (Gaussian)
    nMu1 = (nMu0/nVar0 + sum(aD)/nVar) / (1/nVar0 + len(aD)/nVar);
    nVar1 = 1/(1/nVar0 + len(aD)/nVar);
    nVar1 = 1/(nVar1 + nVar);
#     nMu1 = (nTau0*nMu0 + nTau*sum(aD)) / (nTau0 + len(aD)*nTau);
#     nTau1 = 1/(nTau0 + len(aD)*nTau) + 1/nTau;
    NormQ2 = pm.Normal('NormQ2', mu=nMu1, tau=nVar1);  # @UndefinedVariable
    return np.concatenate([[Norm,NormQ,NormQ2],NormD]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = get_Models();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=1);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/Gaussian_Gaussian_WithData.pdf");
