from __future__ import division;
import numpy as np;
import matplotlib.pyplot as pl;
import scipy.special as sp;
import matplotlib.patches as mpatches;

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
    v = 2; #Variance
    return v*min(x,y);
def kSq_Exp(x,y): #Squared Exponential (aka Gaussian Kernel)
    v, l = 2, 5; #Variance & Characteristic Length Scale
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
def mCircle_2D(t, iDim):
    if iDim==0:
        return np.cos(t)*10; #Dim X
    else:
        return np.sin(t)*10; #Dim Y
def mEpitrochoid_2D(t, iDim):
    R, r, d = 3, 1, 1;
    #R, r, d = 1, 1, 0; #Circle
    if iDim==0: 
        return ((R+r)*np.cos(t)-d*np.cos(t*(R+r)/r))*10; #Dim X
    else:
        return ((R+r)*np.sin(t)-d*np.sin(t*(R+r)/r))*10; #Dim Y

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

def getMean_2D(nOpc, iDim, t):
    mFunc = {0 : mCircle_2D,
             1 : mEpitrochoid_2D};
    n = len(t);
    mu = np.zeros((1,n))[0];
    for i in range(n):
        mu[i] = mFunc[nOpc](t[i], iDim);
    return mu;

def plotGP_2D(k, mu, aSamples):
    s_x, s_y = aSamples;
    mu_x, mu_y = mu;
    var = k.diagonal();
    pl.gca().fill_between(mu_x.flat, mu_y-var, mu_y+var, alpha=1, color="#dddddd"); #Variance
    pl.gca().fill_betweenx(mu_y.flat, mu_x-var, mu_x+var, alpha=1, color="#dddddd"); #Variance
    for x,y,v in zip(mu_x,mu_y,var):
        pl.gca().add_artist(mpatches.Ellipse((x,y), v*2,v*2, color='#dddddd'));
#     points = np.array([mu_x, mu_y]).T.reshape(-1, 1, 2);
#     segments = np.concatenate([points[:-1], points[1:]], axis=1);
#     lc = LineCollection(segments, linewidths=var*11, colors='#dddddd');
#     pl.gca().add_collection(lc);
    pl.errorbar(mu_x, mu_y, xerr=var, yerr=var, alpha=1, lw=1, c='lightgray');
    pl.plot(mu_x, mu_y, 'r'); #Mean
    for i in range(nSamples):
        pl.plot(s_x[:,i].T, s_y[:,i].T, marker='o', ms=5); #Function Samples
    nPad = 5;
    pl.axis([np.min(s_x)-nPad, np.max(s_x)+nPad, np.min(s_y)-nPad, np.max(s_y)+nPad]);
    pl.show();

    
if __name__ == '__main__':
    nSamples = 3;
    t = np.linspace(0,2*np.pi,100);
    k = getKernel(2, t);
    mu_x = getMean_2D(1, 0, t);
    mu_y = getMean_2D(1, 1, t);
    mu = [mu_x, mu_y];
    s_x = mvn_sample(mu_x, k, nSamples);
    s_y = mvn_sample(mu_y, k, nSamples);
    s = [s_x, s_y];
    plotGP_2D(k, mu, s);
    
    