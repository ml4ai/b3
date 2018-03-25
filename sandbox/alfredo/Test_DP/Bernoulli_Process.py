from __future__ import division;
import matplotlib.pyplot as pl;
# import scipy.stats as stats;
import numpy as np;
import warnings;

def get_Bernoulli_Process(aH):
    nSamples = len(aH);
    aBP = np.zeros((nSamples, 1));
    for i in range(nSamples):
        aBP[i] = 1 if (np.random.rand()<aH[i]) else 0;
    return aBP;

def get_Beta_Process(func_H, nA, nB, nK):
    aH = np.zeros((nK,1));
    for i in range(nK):
        aH[i] = np.random.beta(nA*func_H(i,nK), nB*(1-func_H(i,nK)));
    return aH;

def pdf_Func(x, nK):
    p = 1/nK; #Uniform
    return p;

def plot_BP(aH, aBP):
    pl.bar(range(len(aH)), aH);
    pl.stem(range(len(aH)), aBP);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3, threshold=10000, linewidth=1000);
    aH = get_Beta_Process(pdf_Func, 5, 2, 100);
    aBP = get_Bernoulli_Process(aH);
    print np.hstack([aH, aBP]);
    plot_BP(aH, aBP);