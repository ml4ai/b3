from __future__ import division;
import matplotlib.pyplot as pl;
import scipy.stats as stats;
import numpy as np;
import warnings;

def get_Beta_Process(func_H, nA, nB, nK):
    aH = np.zeros((nK,1));
    for i in range(nK):
        aH[i] = np.random.beta(nA*func_H(i,nK), nB*(1-func_H(i,nK)));
    return aH;

def pdf_Func(x, nK):
    p = 1/nK; #Uniform
#     p = stats.norm.pdf(x,50,10); #Gaussian
    return p;

def plot_BP(aH):
    pl.bar(range(len(aH)), aH);
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3, threshold=10000, linewidth=1000);
    aH = get_Beta_Process(pdf_Func, 5, 2, 100);
    plot_BP(aH);