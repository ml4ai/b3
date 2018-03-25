from __future__ import division;
import scipy.special as sp;
import numpy as np;
import matplotlib.pyplot as pl;

def mvn_sample(mu, k, nsamples):
    x = np.random.multivariate_normal(mu,k,nsamples);
    return x.T;
#---Kernel Functions
def kConstant(x,y): #Constant
    v = 2; #Variance
    return v;
def kLinear(x,y): #Linear
    v = 0.01; #Variance
    return v*(x*y);
def kBrownian(x,y): #Brownian Motion
    v = 1.5; #Variance
    return v*min(x,y);
def kSq_Exp(x,y): #Squared Exponential (aka Gaussian Kernel)
    v, l = 5, 5; #Variance & Characteristic Length Scale
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
    return -(x**2/10);
def mCube(x):
    return x**3;
def mAsymptote(x):
    return 1.0/x;
def mSin(x):
    return np.sin(x);
def mDiscrete(x):
    return int(x)*2;

def getKernel_PostPred(nOpc, t, aData):
    x = aData[0];
    y = aData[1];  # @UnusedVariable
    k_11 = getKernel(nOpc, x); #Kernel of Data
    k_12 = getKernel(nOpc, t, x); #Kernel of Data-Queries
    k_22 = getKernel(nOpc, t); #Kernel of Queries
    invK_11 = np.linalg.pinv(k_11);
    prod_k = np.dot(k_12, invK_11);
    k_out = k_22 - np.dot(prod_k, k_12.T);
    return k_out;

def getMean_PostPred(nOpc, t, aData):
    x = aData[0];
    y = aData[1];
    mu_t = getMean(nOpc, t).reshape(-1,1);
    mu_x = getMean(nOpc, x).reshape(-1,1);
    k_11 = getKernel(nOpc, x); #Kernel of Data
    k_12 = getKernel(nOpc, t, x); #Kernel of Data-Queries
    invK_11 = np.linalg.pinv(k_11);
    prod_k = np.dot(k_12, invK_11);
    mu_out = mu_t + np.dot(prod_k, (y - mu_x));
    return mu_out;
    

def getKernel(nOpc, t, t2=None):
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
    n2 = len(t2) if t2!=None else n;
    t2 = t2 if t2!=None else t;
    k = np.zeros((n,n2));
    for i in range(n):
        for j in range(n2):
            k[i,j] = kFunc[nOpc](t[i], t2[j]);
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
    for i in range(np.shape(s)[1]):
        pl.plot(t,s[:,i].T, marker='o', ms=5); #Function Samples
    nPad = 5;
    pl.axis([min(t)-nPad, max(t)+nPad, np.min(s)-nPad, np.max(s)+nPad]);
    pl.show();
    
    
if __name__ == '__main__':
    nSamples = 1;
    t = np.linspace(0,10,50).reshape(-1,1); #Queries x*
    x = np.array([1,3,6]).reshape(-1,1);  #Data x
    y = np.array([1,-1,8]).reshape(-1,1); #Data y [or f(x)]
    aData = np.array([x,y]);
    mu = getMean_PostPred(2, t, aData);
    k = getKernel_PostPred(2, t, aData);
    mu = mu.reshape(1,-1)[0];
    s = mvn_sample(mu, k, nSamples);
    pl.plot(x,y, marker='*', ms=20);
    plotGP(t, k, mu, s);
    
    
#     mu = getMean(0, t);
#     k = getKernel(5, t);
#     s = mvn_sample(mu, k, nSamples);
#     plotGP(t, k, mu, s);
    
    