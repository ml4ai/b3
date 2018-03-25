from __future__ import division;
import Plot_Sampler_Tools as pst;
import pymc as pm;
import warnings;

def run_Bernoulli_Normal():
    B = pm.Bernoulli('Bern', 0.8);  # @UndefinedVariable
    p_N1 = pm.Lambda('p_Norm', lambda k=B: [-5,5][int(k)]);
    N = pm.Normal('Norm', mu=p_N1, tau=1);  # @UndefinedVariable
    return [B,N];

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
    mcmc = pst.sample_MCMC(model, 1000);
    pst.plot_Samples(mcmc, nBins=500);
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph4.pdf");
    