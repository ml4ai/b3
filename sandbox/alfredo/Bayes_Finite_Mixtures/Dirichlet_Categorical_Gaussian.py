from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np;
import pymc as pm;
import warnings;
    
def getModel():
    D = pm.Dirichlet('1-Dirichlet', theta=[2,1,3,1]); #@UndefinedVariable
#     p_B = pm.Lambda('p_Bern', lambda b=B: np.where(b==0, 0.9, 0.1), doc='Pr[Bern|Beta]');
    C = pm.Categorical('2-Cat', D); #@UndefinedVariable
#     C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3], observed=True, value=3); #@UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda n=C: np.select([n==0, n==1, n==2, n==3], [-5,0,5,10]), doc='Pr[Norm|Cat]');
    N = pm.Normal('3-Norm', mu=p_N, tau=1); #@UndefinedVariable
#     N = pm.Normal('2-Norm', mu=p_N, tau=1, observed=True, value=2.5); #@UndefinedVariable
    return pm.Model([D,C,N]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = pst.sample_MCMC(getModel(), 1000);    
    pst.plot_Samples(mcmc, aBins=[100,4,100], aKDE=[]);