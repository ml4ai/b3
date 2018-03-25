from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np  # @UnusedImport
import pymc as pm;
import warnings;

def get_Models():
    #Full Model (Dirichlet & Categorical)
    aAlphas = [1,2,8,2];
    aD = [0,3,1];
    Dir = pm.Dirichlet('Dir', theta=aAlphas);  # @UndefinedVariable    
    CatD = [pm.Categorical('CatD_'+str(i), p=Dir, observed=True, value=aD[i]) for i in range(len(aD))];  # @UndefinedVariable @UnusedVariable
    CatQ = pm.Categorical('CatQ', p=Dir);  # @UndefinedVariable    
    #Collapsed Model (Categorical)
    aP = [];
    for i in range(len(aAlphas)): #For each Category, get its probability p_i
        aP.append((aAlphas[i] + aD.count(i)) / (sum(aAlphas) + len(aD)));
    CatQ2 = pm.Categorical('CatQ2', p=aP);  # @UndefinedVariable
    return np.concatenate([[Dir,CatQ,CatQ2],CatD]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = get_Models();
    model = pst.get_Model(aNodes);
    mcmc = pst.sample_MCMC(model, 5000);
    pst.plot_Samples(mcmc, nBins=500, nCols=1);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./Graphs/Dirichlet_Categorical_WithData.pdf");
