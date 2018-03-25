from __future__ import division;
import Plot_Sampler_Tools as pst;
import pymc as pm;
import warnings;
    
def getModel():
    nA, nB, nK = 5, 2, 10;
    B = pm.Beta('1-Beta', alpha=nA/nK, beta=nB*(nK-1)/nK); #@UndefinedVariable
#     p_B = pm.Lambda('p_Bern', lambda b=B: np.where(b==0, 0.9, 0.1), doc='Pr[Bern|Beta]');
    C = pm.Categorical('2-Cat', [1-B, B]); #@UndefinedVariable
#     C = pm.Categorical('1-Cat', [0.2, 0.4, 0.1, 0.3], observed=True, value=3); #@UndefinedVariable
    return pm.Model([B,C]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = pst.sample_MCMC(getModel(), 1000);    
    pst.plot_Samples(mcmc, aBins=[100,2,100], aKDE=[0,0,0]);