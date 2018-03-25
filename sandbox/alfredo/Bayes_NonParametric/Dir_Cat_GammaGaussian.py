from __future__ import division;
import Plot_Sampler_Tools as pst;
import numpy as np;
import pymc as pm;
import warnings;

def getModel():
    nA, nK = 0.05, 4;
    aDir = [nA/nK]*nK;
    D = pm.Dirichlet('1-Dirichlet', theta=aDir); #@UndefinedVariable
    C1 = pm.Categorical('2-Cat', D); #@UndefinedVariable
#     C2 = pm.Categorical('10-Cat', D); #@UndefinedVariable
#     C3 = pm.Categorical('11-Cat', D); #@UndefinedVariable
#     C4 = pm.Categorical('14-Cat', D); #@UndefinedVariable
#     C5 = pm.Categorical('15-Cat', D); #@UndefinedVariable
#     G0_0 = pm.Gamma('4-Gamma0_1', alpha=1, beta=1.5); #@UndefinedVariable
    N0_1 = pm.Normal('5-Norm0_1', mu=10, tau=1); #@UndefinedVariable
    N0_2 = pm.Normal('6-Norm0_2', mu=-10, tau=1); #@UndefinedVariable
    N0_3 = pm.Normal('7-Norm0_3', mu=30, tau=1); #@UndefinedVariable
    N0_4 = pm.Normal('16-Norm0_3', mu=-30, tau=1); #@UndefinedVariable
    aMu = [N0_1.value, N0_2.value, N0_3.value, N0_4.value];
    p_N1 = pm.Lambda('p_Norm1', lambda n=C1: aMu[n], doc='Pr[Norm|Cat]');
#     p_N2 = pm.Lambda('p_Norm2', lambda n=C2: aMu[n], doc='Pr[Norm|Cat]');
#     p_N3 = pm.Lambda('p_Norm3', lambda n=C3: aMu[n], doc='Pr[Norm|Cat]');
#     p_N4 = pm.Lambda('p_Norm4', lambda n=C4: aMu[n], doc='Pr[Norm|Cat]');
#     p_N5 = pm.Lambda('p_Norm6', lambda n=C5: aMu[n], doc='Pr[Norm|Cat]');
    N = pm.Normal('3-Norm', mu=p_N1, tau=1); #@UndefinedVariable
#     obsN1 = pm.Normal('8-Norm', mu=p_N2, tau=1, observed=True, value=40); #@UndefinedVariable @UnusedVariable
#     obsN2 = pm.Normal('9-Norm', mu=p_N3, tau=1, observed=True, value=40); #@UndefinedVariable @UnusedVariable
#     obsN3 = pm.Normal('12-Norm', mu=p_N4, tau=1, observed=True, value=-40); #@UndefinedVariable @UnusedVariable
#     obsN4 = pm.Normal('13-Norm', mu=p_N5, tau=1, observed=True, value=-40); #@UndefinedVariable @UnusedVariable
    return pm.Model([D,C1,N,N0_1,N0_2,N0_3,N0_4,N]);
#     return pm.Model([D,C1,C2,C3,N,G0_0,N0_1,N0_2,N0_3,N0_4,N,obsN1,obsN2,obsN3,obsN4]);

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    mcmc = pst.sample_MCMC(getModel(), 10000);
    aBins = [100]*len(mcmc.nodes);
    for i in [1]: aBins[i] = 4; 
    aShow = [1,2,3]; #[4,5,6,7,10,11  ,12,13,14,15,16];
    pst.plot_Samples(mcmc, aBins=aBins, aKDE=[], aRowCols=[3,1], aShow=aShow);