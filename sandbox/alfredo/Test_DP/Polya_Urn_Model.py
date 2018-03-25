from __future__ import division;
import matplotlib.pyplot as pl;
import scipy.stats as stats;
import numpy as np;
import warnings;

def get_Polya_Urn_Model(base_pdf_sampler, nAlpha, nBalls):
    aBalls = [];
    for i in range(nBalls):  # @UnusedVariable
        if np.random.rand() <= nAlpha/(nAlpha + len(aBalls)):
            nNew_ball_color = base_pdf_sampler();
            aBalls.append(nNew_ball_color);
        else:
            nCurrent_ball_color = aBalls[np.random.randint(0,len(aBalls))];
            aBalls.append(nCurrent_ball_color);
    return aBalls;

def plot_Polya_Urn(aBalls):
    mBalls = {};
    for nColor in aBalls:
        if mBalls.has_key(nColor): mBalls[nColor] += 1;
        else: mBalls[nColor] = 1;
    pl.stem(mBalls.keys(), mBalls.values());
    pl.show();

def sampler_pdf_Func():
    s = stats.norm.rvs(loc=0, scale=1, size=1)[0]; #Gaussian
    return s;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3);
    aBalls = get_Polya_Urn_Model(sampler_pdf_Func, 5, 100);
    plot_Polya_Urn(aBalls);