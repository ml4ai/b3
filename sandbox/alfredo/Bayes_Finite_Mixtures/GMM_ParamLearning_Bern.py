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
    #Bernoulli Nodes
    B1 = pm.Bernoulli('Bern1', 0.8);  # @UndefinedVariable
    B2 = pm.Bernoulli('Bern2', 0.8);  # @UndefinedVariable
    B3 = pm.Bernoulli('Bern3', 0.5);  # @UndefinedVariable
    #Points
    p_N1 = pm.Lambda('p_Norm1', lambda k=B1, c1=Nc1, c2=Nc2: [c2,c1][int(k)]);
    p_N2 = pm.Lambda('p_Norm2', lambda k=B2, c1=Nc1, c2=Nc2: [c1,c2][int(k)]);
    p_N3 = pm.Lambda('p_Norm3', lambda k=B3, c1=Nc1, c2=Nc2: [c1,c2][int(k)]);
    normalObs1 = pm.Normal('NormX1', mu=p_N1, tau=1, observed=True, value=-3);  # @UndefinedVariable
    normalObs2 = pm.Normal('NormX2', mu=p_N2, tau=1, observed=True, value=3);  # @UndefinedVariable
    normalObsZ = pm.Normal('NormZ',  mu=p_N3, tau=1);  # @UndefinedVariable
    return [Nc1,Nc2,B1,B2,B3,Uh1,Uh2,normalObs1,normalObs2,normalObsZ];

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    aNodes = run_Bernoulli_Normal();
    model = pst.get_Model(aNodes);    
    mcmc = pst.sample_MCMC(model, 10000);
    pst.plot_Samples(mcmc, nBins=500);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph4.pdf");
    