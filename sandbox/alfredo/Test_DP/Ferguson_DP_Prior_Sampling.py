from Dirichlet_PDF import dirichlet_pdf;
import matplotlib.pyplot as pl;
import numpy as np;
import scipy.stats as stats;
import warnings;

def show_Samples_Dirichlet(aSamples_Dirichlet):
    nSamples, nDims = np.shape(aSamples_Dirichlet);
    pl.hold(True);
    pl.ion();
    for i in range(nSamples):
        pl.bar(range(nDims), aSamples_Dirichlet[i]);
        pl.show();
        pl.pause(0.01);
        pl.clf();
        
def show_AvgSamples_Dirichlet(aSamples_Dirichlet):
    nSamples, nDims = np.shape(aSamples_Dirichlet);
    aAvg = sum(aSamples_Dirichlet,0)/nSamples;
    print "\nDirichlet of Avg_Sample: %.3f" % dirichlet_pdf(aAvg, alphas), aAvg;
    pl.bar(range(nDims), aAvg);
    pl.show();
    
def get_Ferguson_DP_Samples(alpha, base_PDF, aPts, nSamples):
    aAlphas = [];
    for i in aPts:
        aAlphas.append(alpha*base_PDF(i));
    s = np.random.dirichlet(tuple(aAlphas), nSamples);
    return s, aAlphas;
    
def pdf_Func(x):
    p = stats.norm.pdf(x, loc=0, scale=1); #Gaussian
    return p;

def show_Dirichlet_PDFs(aSamples_Dirichlet, alphas, nMax=20):
    print "Dirichlet of All_Samples:";
    for s in aSamples_Dirichlet[:nMax]:
        print "%.3f" % dirichlet_pdf(s+1e-10, alphas), s, alphas;

if __name__ == "__main__":
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3);
    nSamples, nDim = 1000, 50;
    aPts = np.linspace(-10,10,nDim);
    s,alphas = get_Ferguson_DP_Samples(10, pdf_Func, aPts, nSamples);
    show_Dirichlet_PDFs(s, alphas);
    show_AvgSamples_Dirichlet(s);
#     show_Samples_Dirichlet(s);