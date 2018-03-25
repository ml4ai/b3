from Dirichlet_PDF import dirichlet_pdf;
import matplotlib.pyplot as pl;
import numpy as np;
import sys;
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
            
def show_Dirichlet_PDFs(aSamples_Dirichlet, alphas, nMax=20):
    print "Dirichlet of All_Samples:";
    for s in aSamples_Dirichlet[:nMax]:
        print "%.3f" % dirichlet_pdf(s, alphas), s;
    
if __name__ == "__main__":
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3);
    alphas = [1e-22, 2, sys.float_info.min];
    print "%.3f" % dirichlet_pdf([0,1,0], alphas)
#     s = np.random.dirichlet(tuple(alphas), 1000);
#     show_Dirichlet_PDFs(s, alphas);
#     show_AvgSamples_Dirichlet(s);
    
    