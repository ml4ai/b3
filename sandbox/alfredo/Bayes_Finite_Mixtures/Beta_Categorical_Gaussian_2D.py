from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np;
import pymc as pm;
import warnings;
    
def getModel():
    B = pm.Beta('1-Beta', alpha=1.2, beta=5); #@UndefinedVariable
#     p_B = pm.Lambda('p_Bern', lambda b=B: np.where(b==0, 0.9, 0.1), doc='Pr[Bern|Beta]');
    C = pm.Categorical('2-Cat', [1-B, B]); #@UndefinedVariable
#     C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3], observed=True, value=3); #@UndefinedVariable
    p_N = pm.Lambda('p_Norm', lambda n=C: np.where(n==0, [0,0], [5,5]), doc='Pr[Norm|Cat]');
    N = pm.MvNormalCov('3-Norm_2D', mu=p_N, C=np.eye(2)); #@UndefinedVariable
#     N = pm.MvNormal('2-Norm', mu=p_N, tau=np.eye(2,2), observed=True, value=[2.5,2.5]); #@UndefinedVariable
    return pm.Model([B,C,N]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = pst.sample_MCMC(getModel(), 10000);
    pst.plot_Samples(mcmc, aBins=[100,2,100], aKDE=[0,0,0]);