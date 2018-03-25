from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def run_Categorical_Normal():
    C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3]);  # @UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda node=C: np.select([node==0, node==1, node==2, node==3],
                                                       [-5, 0, 5, 10]), doc='Pr[Norm|Cat]');
    N = pm.Normal('2-Norm', mu=p_N, tau=1);  # @UndefinedVariable
    model = pm.Model([C,N]);
    mcmc = pm.MCMC(model);
    mcmc.sample(5000, progress_bar=True);
    print "C:", C.stats()["mean"], C.value;
    print "N:", N.stats()["mean"], N.value;
    plot_Samples(mcmc, aBins=[2,500]);

def plot_Samples(mcmc, aBins):
    aNodes = list(mcmc.nodes);
    for i in range(len(aNodes)):
        node_Samples = mcmc.trace(aNodes[i].__name__)[:];
        nSamples = float(len(node_Samples));
        pl.subplot(len(aNodes), 1, i+1);
        pl.title(aNodes[i].__name__);
        pl.hist(node_Samples, aBins[i], weights=np.ones(nSamples)*(1/nSamples));
    pl.show();    
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph.pdf");

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    run_Categorical_Normal();