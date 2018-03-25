from __future__ import division;
import numpy as np;
import scipy.stats as stats;
import matplotlib.pyplot as pl;


def get_MH_HierModels(nIters, initSt, f_TrgPdf, f_PropQ):
    aX = np.zeros((nIters, len(initSt)));
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

#Target Distribution F(x)
def f_TrgPdf(x): #Beta-Bernoulli
    z1 = stats.beta.pdf(x[0], 4,2);
    z2 = stats.bernoulli.pmf(x[1], x[0]);
    return z1*z2;

#Sampler & Proposal Distribution Q(x|y)
def f_PropQ(x,c=None): #Multivariate Gaussian
    if c==None: #Sampler
        z1 = stats.beta.rvs(5,5, loc=x[0]-0.5);
#         z1 = stats.norm.rvs(x[0], 0.1);
        while z1>=1 or z1<=0:
            z1 = stats.beta.rvs(5,5, loc=x[0]-0.5);
#             z1 = stats.norm.rvs(x[0], 0.1);
        z2 = stats.bernoulli.rvs(z1);
        n = np.array([z1, z2]);
    else: #Proposal Distribution Pdf Q(x|c) [Mean=c]        
        z1 = stats.beta.pdf(x[0], 5,5, loc=c[0]-0.5);
#         z1 = stats.norm.pdf(x[0], c[0], 0.1);
        cpt = np.array([[0.5,0.5],[0.5,0.5]]);
        z2 = stats.bernoulli.pmf(x[1], cpt[x[1],c[1]]);
        n = z1*z2;
    return n;

#Plotting Samples
def plot_Samples(aSamples, nBins=100):
    nSamples,nD = np.shape(aSamples);
    for i in range(nD):
        pl.subplot(2,1,i+1);
        kBins = len(set(aSamples[:,i]));
        kBins = nBins if kBins>5 else kBins;
        pl.hist(aSamples[:,i], kBins, weights=np.ones(nSamples)*(1/nSamples));
    pl.show();

if __name__ == '__main__':
    nIters = 5000;
    aX = get_MH_HierModels(nIters, [0.7,0], f_TrgPdf, f_PropQ);
    print 'Expectation: {:.4f}'.format(np.sum(aX)/nIters);#, aX;
    plot_Samples(aX);