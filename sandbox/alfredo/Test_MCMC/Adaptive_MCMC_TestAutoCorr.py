from __future__ import division;
import numpy as np;
import scipy.stats as stats;
import matplotlib.pyplot as pl;
import time;

def eval_Samples(s):
    def get_a(l_max,x):
        aR = np.zeros((l_max,1));
        v,m = x.var(), x.mean();
        for i in range(1,l_max+1):
            aR[i-1] = get_AutoCorrelation(i,x,v,m);
        return 1.0 - (l_max**-1.0)*np.sum(np.abs(aR));
    def get_AutoCorrelation(l,x,v,m):
        n = len(x);
        nZ = 1.0/((n-l)*v);
        nSumX = np.zeros((n-l,1));
        for i in range(n-l):
            nSumX[i] = (x[i]-m)*(x[i+l]-m);
        return nZ*np.sum(nSumX);
    l = len(s);
    nWin = l-25#int(round(l*0.9));
    aA = np.zeros((l-nWin,1));
    nZ = 1.0/(l-nWin+1);
    for k,i in enumerate(range(nWin,l)):
        aA[k] = get_a(i,s[:i+1]);
#         print k+1,aA[k];
    return nZ*np.sum(aA);

def get_Metropolis(nIters, initSt, f_TrgPdf, f_PropQ, v):
    aX = np.zeros((nIters, 1));
    aV = np.zeros((nIters, 1));
    aX[0] = initSt;
    for i in range(nIters-1):
        #STEP 1: (SIMULATION OF X)
        v = get_Params(aX[:i+1]);
#         aV[i] = v;
        q = f_PropQ(aX[i], v);
        u = np.random.rand();        
        #STEP 2: (NEXT-STATE EVALUATION)
        nR = f_TrgPdf(q)/f_TrgPdf(aX[i]); #Due to Symmetric PropQ [Metropolis Algorithm]
        if u <= np.min([1,nR]): aX[i+1] = q;
        else: aX[i+1] = aX[i];
    return aX, aV;

#Compute Adaptive Parameters for Proposal Sampler
def get_Params(aX):
#     x = aX[:,0];
#     v = 1 if abs(aX[-1]-4.5)<=1.2 or abs(aX[-1]+4.5)<=1.2 else 50; #My Custom Method
#     v = 2*np.cov(x) if len(x)>1 else 1; #Method from paper "An Adaptive Metropolis Algorithm" (2001)
    v = 3;
    return v;

#Target Distributions F(x)
def f_TrgPdf2(x): #Mixture of Gaussians
    z1 = stats.norm.pdf(x, loc=-4.5, scale=1);
    z2 = stats.norm.pdf(x, loc=4.5, scale=1);
    aW = [0.4, 0.6];
    return aW[0]*z1 + aW[1]*z2;

#Proposal Distributions Q(x|y)
def f_PropQ(x,v=5): #Gaussian
    s = x + v*np.random.randn();
    return s;

#Plotting Samples
def plot_Samples(aSamples, aV, nBins=100):
    pl.subplot(2,1,1);
    pl.title('Variance');
#     pl.hist(aV, nBins);
    pl.plot(range(nIters), aV);
    pl.subplot(2,1,2);
    pl.title('Samples');
    nSamples = len(aSamples);
    pl.hist(aSamples, nBins, weights=np.ones(nSamples)*(1/nSamples));
    pl.show();

if __name__ == '__main__':
    nIters = 100;
    nScores = 10;
    aVars = np.linspace(0.5,5, nScores);
    aScores = np.zeros(nScores);
    for i,v in enumerate(aVars):
        aX, aV = get_Metropolis(nIters, 0, f_TrgPdf2, f_PropQ, v);
        t0 = time.time();
        aScores[i] = eval_Samples(aX);
        nT = time.time()-t0;
        print '{:}/{:} Score: {:.2f}, Time {:.2f}'.format(i+1,nScores,aScores[i],nT);
    pl.plot(aVars,aScores);
    pl.show();
#     plot_Samples(aX, aV);