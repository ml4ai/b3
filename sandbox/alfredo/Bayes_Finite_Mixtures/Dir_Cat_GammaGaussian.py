from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np;
import pymc as pm;
import warnings;
    
def getModel():
    D = pm.Dirichlet('1-Dirichlet', theta=[3,2,4]); #@UndefinedVariable
    C1 = pm.Categorical('2-Cat', D); #@UndefinedVariable
    C2 = pm.Categorical('10-Cat', D); #@UndefinedVariable
    C3 = pm.Categorical('11-Cat', D); #@UndefinedVariable
    G0_0 = pm.Gamma('4-Gamma0_1', alpha=1, beta=1.5); #@UndefinedVariable
    U1 = pm.Uniform('12-Unif', lower=-100, upper=500); #@UndefinedVariable
    U2 = pm.Uniform('13-Unif', lower=-100, upper=500); #@UndefinedVariable
    U3 = pm.Uniform('14-Unif', lower=-100, upper=500); #@UndefinedVariable
    N0_1 = pm.Normal('5-Norm0_1', mu=U1, tau=1); #@UndefinedVariable
    N0_2 = pm.Normal('6-Norm0_2', mu=U2, tau=1); #@UndefinedVariable
    N0_3 = pm.Normal('7-Norm0_3', mu=U3, tau=1); #@UndefinedVariable
    aMu = [N0_1.value, N0_2.value, N0_3.value];
    fL1 = lambda n=C1: np.select([n==0, n==1, n==2], aMu);
    fL2 = lambda n=C2: np.select([n==0, n==1, n==2], aMu);
    fL3 = lambda n=C3: np.select([n==0, n==1, n==2], aMu);
    p_N1 = pm.Lambda('p_Norm1', fL1, doc='Pr[Norm|Cat]');
    p_N2 = pm.Lambda('p_Norm2', fL2, doc='Pr[Norm|Cat]');
    p_N3 = pm.Lambda('p_Norm3', fL3, doc='Pr[Norm|Cat]');
    N = pm.Normal('3-Norm', mu=p_N1, tau=1); #@UndefinedVariable
    obsN1 = pm.Normal('8-Norm', mu=p_N2, tau=1, observed=True, value=0); #@UndefinedVariable @UnusedVariable
    obsN2 = pm.Normal('9-Norm', mu=p_N3, tau=1, observed=True, value=150); #@UndefinedVariable @UnusedVariable
    return pm.Model([D,C1,C2,C3,N,G0_0,N0_1,N0_2,N0_3,N,obsN1,obsN2]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = pst.sample_MCMC(getModel(), 10000);
    aBins = [100]*14;
    aBins[1] = 3;
    aBins[9] = 3;
    aBins[10] = 3;
    aHidden = [4,5,6,7,10,11];
    pst.plot_Samples(mcmc, aBins=aBins, aKDE=[], aRowCols=[6,1], aHidden=aHidden);