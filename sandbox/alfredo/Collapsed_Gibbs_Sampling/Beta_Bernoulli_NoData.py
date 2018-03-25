from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np  # @UnusedImport
import pymc as pm;
import warnings;

def get_Models():
    #Full Model (Beta & Bernoulli)
    nA, nB = 2,8;
    Beta = pm.Beta('Beta', alpha=nA, beta=nB);  # @UndefinedVariable
    Bern = pm.Bernoulli('Bernoulli', p=Beta);  # @UndefinedVariable
    #Collapsed Model (Bernoulli)
    nP = nA/(nA+nB);
    Bern2 = pm.Bernoulli('Bernoulli2', p=nP);  # @UndefinedVariable    
    return [Beta,Bern,Bern2];    

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = get_Models();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=1);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/Beta_Bernoulli_NoData.pdf");
