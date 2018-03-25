from __future__ import division;
import numpy as np;
import scipy.stats as stats;
import matplotlib.pyplot as pl;


def get_Metropolis(nIters, initSt, f_TrgPdf, f_PropQ):
    aX = np.zeros((nIters, 1));
    aX[0] = initSt;
    for i in range(nIters-1):
        #STEP 1: (SIMULATION OF X)
        q = f_PropQ(aX[i]);
        u = np.random.rand();        
        #STEP 2: (NEXT-STATE EVALUATION)
        nR = f_TrgPdf(q)/f_TrgPdf(aX[i]); #Due to Symmetric PropQ [Metropolis Algorithm]
        if u <= np.min([1,nR]): aX[i+1] = q;
        else: aX[i+1] = aX[i];
    return aX;

#Target Distributions F(x)
def f_TrgPdf(x): #Gaussian
    z = stats.norm.pdf(x, loc=0, scale=1);
    return z;
def f_TrgPdf2(x): #Mixture of Gaussians
    z1 = stats.norm.pdf(x, loc=-2.5, scale=1);
    z2 = stats.norm.pdf(x, loc=2.5, scale=1);
    aW = [0.4, 0.6];
    return aW[0]*z1 + aW[1]*z2;

#Proposal Distributions Q(x|y)
def f_PropQ(x,v=1): #Gaussian
    s = x + v*np.random.randn();
    return s;

#Plotting Samples
def plot_Samples(aSamples, nBins=100):
    nSamples = len(aSamples);
    pl.hist(aSamples, nBins, weights=np.ones(nSamples)*(1/nSamples));
    pl.show();

if __name__ == '__main__':
    nIters = 10000;
    aX = get_Metropolis(nIters, 0, f_TrgPdf2, f_PropQ);
    print 'Expectation: {:.4f}'.format(np.sum(aX)/nIters);
    plot_Samples(aX);