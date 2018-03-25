from __future__ import division;
import Plot_Sampler_Tools as pst;
import pymc as pm;
import warnings;

def run_Bernoulli_Normal():
    #Cluster 1
    Uh1 = pm.Uniform('UnifH1', lower=-50, upper=50);  # @UndefinedVariable
    Nc1 = pm.Normal('NormC1', mu=Uh1, tau=1)#, observed=True, value=10);  # @UndefinedVariable
    #Cluster 2
    Uh2 = pm.Uniform('UnifH2', lower=-50, upper=50);  # @UndefinedVariable
    Nc2 = pm.Normal('NormC2', mu=Uh2, tau=1)#, observed=True, value=10);  # @UndefinedVariable
    #Points
    normalObs1 = pm.Normal('NormX1', mu=Nc1, tau=1, observed=True, value=-10);  # @UndefinedVariable
    normalObs2 = pm.Normal('NormX2', mu=Nc2, tau=1, observed=True, value=10);  # @UndefinedVariable
    return [Nc1,Nc2,Uh1,Uh2,normalObs1,normalObs2];

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_Bernoulli_Normal();
    model = pst.get_Model(aNodes);    
    mcmc = pst.sample_MCMC(model, 10000);
    pst.plot_Samples(mcmc, nBins=500);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph4.pdf");
    