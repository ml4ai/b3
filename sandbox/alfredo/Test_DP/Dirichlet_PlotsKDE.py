from sklearn.neighbors import KernelDensity;
import matplotlib.pyplot as pl;
import numpy as np;
# import sys;
# import warnings;
    
def kdePlot(aSamples, bwidth=0.08):
    nSamples, nDims = np.shape(aSamples);
    aX = np.vstack([0,np.linspace(0,1,nSamples)[:,np.newaxis],1]);
    pl.hold(True);
    for i in range(nDims):
        kde = KernelDensity(kernel='gaussian', bandwidth=bwidth);
        kde.fit(aSamples[:,i][:,np.newaxis]);
        y = np.exp(kde.score_samples(aX));
        y[0], y[-1] = 0,0;
        pl.fill(aX, y, alpha=0.7, label=str(i+1));
    pl.legend(fancybox=True, loc='upper center', ncol=4);
    pl.show();
    
if __name__ == "__main__":
    alphas = [0.05,0.9,0.05,0.05];
    s = np.random.dirichlet(tuple(alphas), 1000);
    kdePlot(s);
    
    