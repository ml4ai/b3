from __future__ import division;
import matplotlib.pyplot as pl;
# import scipy.stats as stats;
import numpy as np;
import warnings;
sError = "Max Limit Reached: Lambda makes the counter too big " + \
         "(make lambda or nMaxT smaller)";

def get_Poisson_Process(nLambda, nSamples, nMaxT):
    mExps, mCounts = [], {};
    for i in range(nSamples):  # @UnusedVariable
        aExps = get_Count_Sample(nLambda, nMaxT);
#         if len(aExps)==0: 
#             return None, None;
        if len(aExps)>0:
            mExps.append(aExps);
    for i in range(len(mExps)):
        k = len(mExps[i]);
        if mCounts.has_key(k): mCounts[k] += 1;
        else: mCounts[k] = 1;
    return mExps, mCounts;
    
def get_Count_Sample(nLambda, nMaxT):
    nT, aExps = 0, [];
    while nT<nMaxT and len(aExps)<nMaxT:
        nExp = np.random.exponential(1/nLambda);
        aExps.append(nExp);
        nT += nExp;
    if nT<nMaxT: 
#         print sError;
#         print "Max Time was:", nT; 
        return [];
    else: return aExps;
    
def plot_Poisson_Process(mExps, mCounts):
    print "Num. Samples:", len(mExps);
    pl.bar(mCounts.keys(), mCounts.values());
    pl.step(np.cumsum(mExps[0]), range(len(mExps[0])), 'r');
    markerline = pl.stem(np.cumsum(mExps[0]), range(len(mExps[0])), 'r.');
    pl.setp(markerline, 'markerfacecolor', 'r');
    pl.show();

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3, threshold=10000, linewidth=1000);
    mExps, mCounts = get_Poisson_Process(nLambda=0.5, nSamples=1000, nMaxT=50);
    plot_Poisson_Process(mExps, mCounts);