from __future__ import division;
import numpy as np;
import scipy.stats as stats;
import matplotlib.pyplot as pl;


def get_MH(nIters, initSt, f_TrgPdf, f_PropQ):
    aX = np.zeros((nIters, 1));
    aX[0] = initSt;
    for i in range(nIters-1):
        #STEP 1: (SIMULATION OF X)        
        q = f_PropQ(aX[i]);
        u = np.random.rand();        
        #STEP 2: (NEXT-STATE EVALUATION)
        nR = f_TrgPdf(q)/f_TrgPdf(aX[i]);
        nR *= f_PropQ(aX[i],q)/f_PropQ(q,aX[i]);
        if u <= np.min([1,nR]): 
            aX[i+1] = q;
        else: 
            aX[i+1] = aX[i];
    return aX;

#Target Distributions F(x)
def f_TrgPdf(x): #Gaussian
    z = stats.norm.pdf(x, loc=0, scale=1);
    return z;
def f_TrgPdf2(x): #Mixture of Gaussians
    z1 = stats.norm.pdf(x, loc=-2.5, scale=1);
    z2 = stats.norm.pdf(x, loc=2.5, scale=1);
    aW = [0.3, 0.7];
    return aW[0]*z1 + aW[1]*z2;
def f_TrgPdf3(x): #Mixture of Gammas
    z1 = stats.gamma.pdf(x, 3, scale=0.5);
    z2 = stats.gamma.pdf(x, 10, scale=0.5);
    aW = [0.5, 0.5];
    return aW[0]*z1 + aW[1]*z2;

#Proposal Distributions Q(x|y)
def f_PropQ(x,c=None): #Gaussian
    if c==None: n = stats.norm.rvs(loc=x, scale=1); #Get Sample
    else: n = stats.norm.pdf(x, loc=c, scale=1); #Get PDF q(x|c) [Mean=c]
    return n;
def f_PropQ2(x,c=None): #Gamma
    if c==None: n = stats.gamma.rvs(2, loc=x-2, scale=1); #Get Sample
    else: n = stats.gamma.pdf(x, 2, loc=c-2, scale=1); #Get PDF q(x|c) [Mean=c]
    return n;
def f_PropQ3(x,c=None): #Beta
    if c==None: n = stats.beta.rvs(4,2, loc=x-0.5, scale=1); #Get Sample
    else: n = stats.beta.pdf(x, 4,2, loc=c-0.5, scale=1); #Get PDF q(x|c) [Mean=c]
    return n;

#Plotting Samples
def plot_Samples(aSamples, nBins=100):
    nSamples = len(aSamples);
    pl.hist(aSamples, nBins, weights=np.ones(nSamples)*(1/nSamples));
    pl.show();

if __name__ == '__main__':
    nIters = 5000;
    aX = get_MH(nIters, 0, f_TrgPdf, f_PropQ3);
    print 'Expectation: {:.4f}'.format(np.sum(aX)/nIters);#, aX;
    plot_Samples(aX);