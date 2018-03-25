import matplotlib.pyplot as pl;
import numpy as np;
import warnings;

def show_Samples_SBP():
    nSamples = 20;
    pl.hold(True);
    pl.ion();
    for i in range(nSamples):  # @UnusedVariable
        mSBP, aPi = get_SB_Process();
        plot_SPB(mSBP, aPi);
        pl.pause(0.01);
        pl.clf();
        
def get_SB_Process(): #Stick Breaking Process
    nSticks, nBeta = 50, 10;
    aBeta = np.random.beta(1, nBeta, size=nSticks);
    complements = np.cumprod(1-aBeta);
    aPi = np.multiply(aBeta, np.insert(complements[:-1],0,1));
    aTheta = np.random.normal(0,1,nSticks).round();
    mSBP = {};
    for t,p in zip(aTheta, aPi):
        if mSBP.has_key(t): mSBP[t] += p;
        else: mSBP[t] = p;
    return mSBP, aPi;

def get_Avg_SBP(nSamples):
    avg_mSBP = {};
    for i in range(nSamples):  # @UnusedVariable
        mSBP, aPi = get_SB_Process();
        for t in mSBP.keys():
            if avg_mSBP.has_key(t): avg_mSBP[t] += mSBP[t];
            else: avg_mSBP[t] = mSBP[t];
    for t in avg_mSBP.keys():
        avg_mSBP[t] /= float(nSamples);
    avg_aPi = aPi/float(nSamples);
    return avg_mSBP, avg_aPi;
    
        
def plot_SPB(mSBP, aPi):
    f, axarr = pl.subplots(2);  # @UnusedVariable
    axarr[0].bar(mSBP.keys(), mSBP.values()); #Sticks distributed over H distr. (SBP)
    axarr[0].set_title('Sample from Stick Breaking Process');
    axarr[1].bar(range(len(aPi)), aPi); #Sticks
    axarr[1].set_title('Sticks Broken by Beta distributions');
    pl.show();

if __name__ == "__main__":
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3);
    mSBP, aPi = get_Avg_SBP(100);
#     mSBP, aPi = get_SB_Process();
    plot_SPB(mSBP, aPi);
#     show_Samples_SBP();