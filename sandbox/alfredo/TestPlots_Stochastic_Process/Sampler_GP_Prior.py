from __future__ import division;
import numpy as np;
import scipy.special as sp;
import scipy.stats as stats;
import matplotlib.pyplot as pl;

def mvn_sample(mu, k, nsamples):
    x = np.random.multivariate_normal(mu,k,nsamples);
    return x.T;
#---Kernel Functions
def kConstant(x,y): #Constant
    v = 0.5; #Variance
#     if x!=y: v=0;
    return v;
def kLinear(x,y): #Linear
    v = 2; #Variance
#     if x!=y: v=0; 
#     else: print v*(x*y);
    return v*(x*y);
def kBrownian(x,y): #Brownian Motion
    v = 60; #Variance
    return v*min(x,y);
def kSq_Exp(x,y): #Squared Exponential (aka Gaussian Kernel)
    v, l = 60, 2; #Variance & Characteristic Length Scale
    return (v**2) * np.exp(-(x-y)**2/(2.0*l**2));
def kOrn_Uhl(x,y): #Ornstein-Uhlenbeck (aka Laplace Kernel)
    v, l = 2, 5; #Variance & Characteristic Length Scale
    return (v**2) * np.exp(-np.abs(x-y)/l);
def kPeriodic(x,y): #Periodic
    v, l = 2, 5; #Variance & Characteristic Length Scale
    return (v**2) * np.exp(-(2*np.sin((x-y)/2)**2)/l**2);
def kSymmetric(x,y): #Symmetric
    v = 2; #Variance
    return (v**2) * np.exp(-min(abs(x-y),abs(x+y))**2);
def kGaussian_Noise(x,y): #Gaussian Noise
    stdev = 1; #Standard Deviation
    kron_delta = 1 if x==y else 0;
    return stdev*kron_delta;
def kMatern(x,y): #Matern
    v, b, l = 1, 6, 1; #Variance, Parameter Beta & Characteristic Length Scale
    k1 = 2**(1-b)/sp.gamma(b);
    dl = (np.sqrt(2*b)*abs(x-y))/l;
    if dl==0: return 0;
    k2 = (dl**b)*sp.kn(b,dl);
    return (v**2)*k1*k2;
def kRationalQuadratic(x,y): #Rational Quadratic
    v, a = 2, 1; #Variance & Parameter Alpha
    return (v**2)*(1+abs(x-y)**2)**-a;
#---Mean Functions
def mZero(x):
    return 0;
def mLinear(x):
    return x*2;
def mAbsolute(x):
    return abs(x)*10;
def mSquared(x):
    return x**2;
def mCube(x):
    return x**3;
def mAsymptote(x):
    return 1.0/x;
def mSin(x):
    return np.sin(x);
def mDiscrete(x):
    return int(x)*2;

def getKernel(nOpc, t):
    kFunc = {0 : kConstant,
             1 : kLinear,
             2 : kBrownian,
             3 : kSq_Exp,
             4 : kOrn_Uhl,
             5 : kPeriodic,
             6 : kSymmetric,
             7 : kGaussian_Noise,
             8 : kMatern,
             9 : kRationalQuadratic};
    n = len(t);
    k = np.zeros((n,n));
    for i in range(n):
        for j in range(n):
            k[i,j] = kFunc[nOpc](t[i], t[j]);
    return k;

def getMean(nOpc, t):
    mFunc = {0 : mZero,
             1 : mLinear,
             2 : mAbsolute,
             3 : mSquared,
             4 : mCube,
             5 : mAsymptote,
             6 : mSin,
             7 : mDiscrete};
    n = len(t);
    mu = np.zeros((1,n))[0];
    for i in range(n):
        mu[i] = mFunc[nOpc](t[i]);
    return mu;

def plotGP(t, k, mu, aSamples):
    s = aSamples;
    var = k.diagonal();
    pl.gca().fill_between(t.flat, mu-var, mu+var, color="#dddddd"); #Variance
    pl.plot(t,mu, 'r'); #Mean
    for i in range(nSamples):
        pl.plot(t,s[:,i].T, marker='o', ms=5); #Function Samples
    nPadX, nPadY = 0, 0;
    extent = [min(t)-nPadX, max(t)+nPadX, np.min(s)-nPadY, np.max(s)+nPadY];
#     plotHeatMap(t, mu, k, extent);
    pl.axis(extent);
    pl.show();
    
def plotHeatMap(x, mu, k, ext):
    nPts = len(t);
    nPad = 5;
    y = np.linspace(max(mu)+nPad, min(mu)-nPad, nPts);
    z = np.zeros((nPts, nPts));
    var = k.diagonal();
    for i in range(nPts):
        z[:,i] = stats.norm.pdf(y, loc=mu[i], scale=var[i]);
    pl.imshow(z, cmap=pl.get_cmap("gray"), aspect='auto', extent=ext);

    
if __name__ == '__main__':
    nSamples = 5;
    t = np.linspace(0.1,50,10);
    k = getKernel(3, t);
    mu = getMean(3, t);
    s = mvn_sample(mu, k, nSamples);
    print "Prob of Mean Function is:", stats.multivariate_normal.pdf(mu, mu, k);
    for i in range(nSamples):
        print "Prob of Sample Function", i+1, "is:", stats.multivariate_normal.pdf(s[:,i], mu, k);
    plotGP(t, k, mu, s);
    
    