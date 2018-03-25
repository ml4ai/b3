from __future__ import division;
import matplotlib.pyplot as pl;
import numpy as np;
import pymc as pm;
import warnings;

def run_Bernoulli():
    B = pm.Bernoulli('Bern', 0.4);  # @UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda B=B: np.where(B, -5, 5), doc='Pr[Norm|Bern]');
    N = pm.Normal('Norm', mu=p_N, tau=1);  # @UndefinedVariable
    model = pm.Model([B,N]);
    mcmc = pm.MCMC(model);
    mcmc.sample(1000, progress_bar=True);
    print "B:", B.stats()["mean"], B.value;
    print "N:", N.stats()["mean"], N.value;
    plot_Samples(mcmc);

def plot_Samples(mcmc):
    #Get Samples
    bern_Samples = mcmc.trace('Bern')[:];
    norm_Samples = mcmc.trace('Norm')[:];
    nSamples = float(len(bern_Samples));
    #Plot Histograms
    pl.subplot(2, 1, 1);
    pl.hist(bern_Samples, 2, weights=np.ones(nSamples)*(1/nSamples));
    pl.subplot(2, 1, 2);
    pl.hist(norm_Samples, 100, weights=np.ones(nSamples)*(1/nSamples));
    pl.show();    
#     graph = pm.graph.graph(model);
#     graph.write_pdf("./graph.pdf");

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    run_Bernoulli();