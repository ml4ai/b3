from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np;
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

#     @pm.stochastic(observed=True)
#     def normalObs1(name='NormX1', parentVar=B1, parentVals=[Nc1,Nc2], value=8):
#         return pm.normal_like(x=value, mu=parentVals[int(parentVar)], tau=1);
#     @pm.stochastic(observed=True)
#     def normalObs2(name='NormX2', parentVar=B2, parentVals=[Nc1,Nc2], value=2):
#         return pm.normal_like(x=value, mu=parentVals[int(parentVar)], tau=1);
#     @pm.stochastic(observed=False)
#     def normalObsZ(name='NormZ', parentVar=B3, parentVals=[Nc1,Nc2], value=1):
#         return pm.normal_like(x=value, mu=parentVals[int(parentVar)], tau=1);

#     normalObs1 = pm.Normal('NormX1', mu=[Nc1,Nc2][int(B1)], tau=1, observed=True, value=2);  # @UndefinedVariable
#     normalObs2 = pm.Normal('NormX2', mu=[Nc1,Nc2][int(B2)], tau=1, observed=True, value=8);  # @UndefinedVariable
#     normalObsZ = pm.Normal('NormZ', mu=[Nc1,Nc2][int(B3)], tau=1);  # @UndefinedVariable

    return [Nc1,Nc2,B1,B2,B3,Uh1,Uh2,normalObs1,normalObs2,normalObsZ];
    
    
#     U = pm.Uniform('Unif', lower=-50, upper=50);  # @UndefinedVariable
#     Bet = pm.Beta('Beta', alpha=1, beta=1);  # @UndefinedVariable
#     B = pm.Bernoulli('Bern', Bet);  # @UndefinedVariable
#     B1 = pm.Bernoulli('Bern1', Bet);  # @UndefinedVariable
#     B2 = pm.Bernoulli('Bern2', Bet);  # @UndefinedVariable
#     N = pm.Normal('Norm', mu=U, tau=1)#, observed=True, value=10);  # @UndefinedVariable
#     N1 = pm.Normal('Norm1', mu=U, tau=1)#, observed=True, value=-10);  # @UndefinedVariable
#     p_N = pm.Lambda('p_Norm', lambda k=int(B): [N, N1][k]);
#     p_N1 = pm.Lambda('p_Norm1', lambda k=int(B1): [N, N1][k]);
#     p_N2 = pm.Lambda('p_Norm2', lambda k=int(B2): [N, N1][k]);
#     N2 = pm.Normal('Norm2', mu=p_N, tau=1, observed=True, value=2);  # @UndefinedVariable
#     N3 = pm.Normal('Norm3', mu=p_N1, tau=1, observed=True, value=-2);  # @UndefinedVariable
#     N4 = pm.Normal('Norm4', mu=p_N2, tau=1);  # @UndefinedVariable
#     return [N4,U,Bet,B,B1,B2,N2,N3,N,N1]#,B1,B2];


def run_Categorical_Normal():
    C = pm.Categorical('Cat', [0.2, 0.4, 0.1, 0.3]);  # @UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda node=C: [-5, 0, 5, 10][node]);
    N = pm.Normal('Norm', mu=p_N, tau=1);  # @UndefinedVariable
    return [C,N];

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
#     aNodes = run_Categorical_Normal();
    aNodes = run_Bernoulli_Normal();
    model = pst.get_Model(aNodes);    
    mcmc = pst.sample_MCMC(model, 50000);
    pst.plot_Samples(mcmc, nBins=500);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph4.pdf");
    