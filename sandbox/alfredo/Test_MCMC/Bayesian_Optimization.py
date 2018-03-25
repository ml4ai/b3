from MySampler_GP_PostPred import *;
import scipy.stats as stats;
import warnings;

#Objective Functions
def fn_Squared(x):
    return -x**2;

def fn_Polynomial(x):
    return -((x+1)*(x-1)**2*(x-0));

#Acquisition Functions
def fn_Acq_PI(i,x, mu, k, nMaxD):
    nEps = 0.05;
    nQ = (mu[i] - nMaxD - nEps)/k[i,i];
    return stats.norm.cdf(nQ);

def fn_Acq_EI(i,x, mu, k, nMaxD):
    nEps = 0.5;
    nQ = (mu[i] - nMaxD - nEps);
    nZ = nQ/k[i,i];
    nCDF_Z = stats.norm.cdf(nZ);
    nPDF_Z = stats.norm.pdf(nZ);
    nEI = nQ*nCDF_Z + k[i,i]*nPDF_Z if k[i,i]>0 else 0;
    return nEI;

def fn_Acq_UCB(i,x, mu, k, nMaxD):
    nK = 1;
    nUCB = mu[i] + nK*k[i,i];
    return nUCB;

def plot_BO(t, k, mu, aData, y, iMaxX, iFig, trgFn):
    #Plot Gaussian Process
    pl.ion();
    pl.subplot(2,1,1);
    nPad = 4;
    var = k.diagonal();
    s = mvn_sample(mu, k, nsamples = 1);
    pl.plot(aData[0],aData[1], marker='*', ms=20);
    pl.gca().fill_between(t.flat, mu-var, mu+var, color="#dddddd"); #Variance
    pl.plot(t,mu, 'r'); #Mean
    for i in range(np.shape(s)[1]):
        pl.plot(t,s[:,i].T, marker='o', ms=5); #Function Samples
    aTrg = trgFn(t);
    pl.plot(t,aTrg, 'k-'); #Target Function
    pl.axis([min(t)-nPad, max(t)+nPad, np.min(aTrg)-nPad, np.max(aTrg)+nPad]);    
    #Plot Acquisition Function
    pl.subplot(2,1,2);
    pl.plot(t,y);
    pl.plot(t[iMaxX],y[iMaxX], marker='*', ms=20);
    pl.axis([min(t)-nPad, max(t)+nPad, np.min(aTrg)-nPad, np.max(aTrg)+nPad]);
    pl.savefig('./Plots_BO/Fig_'+str(iFig)+'.png');
    pl.pause(1);
    pl.clf();
    pl.show();    
    
def get_Best_x(t, mu, k, fn_Acquisition, nMaxD):
    aAcq = np.zeros((len(t),1));
    for i,x in enumerate(t):
        aAcq[i] = fn_Acquisition(i,x, mu, k, nMaxD);
    iMaxX = np.argmax(aAcq);
    return t[iMaxX], iMaxX, aAcq;

def get_Update_GP(aOpcs, t, aData):
    mu = getMean_PostPred(aOpcs[0], t, aData);
    mu = mu.reshape(1,-1)[0];
    k = getKernel_PostPred(aOpcs[1], t, aData);
    return mu, k;
    
def do_Bayesian_Optimization(nIters, aOps, t, mu, k, aData, trgFn):
    xd, yd = aData[0], aData[1];
    for i in range(nIters):  # @UnusedVariable
        x, iMaxX, aAcq = get_Best_x(t, mu, k, fn_Acq_EI, np.max(yd));
        y = trgFn(x);# + np.random.randn();
        xd, yd = np.vstack([xd,x]), np.vstack([yd,y]);
        plot_BO(t, k, mu, np.array([xd,yd]), aAcq, iMaxX, i, trgFn);
        mu, k = get_Update_GP(aOps, t, np.array([xd,yd]));
    return xd, yd;

if __name__ == '__main__':
    nFigs = 1;
    warnings.filterwarnings("ignore");
    t = np.linspace(-1.5,1.5,50).reshape(-1,1); #Queries x*
    x = np.array([-1]).reshape(-1,1);  #Data x
    trgFn = fn_Polynomial; #fn_Squared;
    y = trgFn(x); #Data y [or f(x)]
    aOpcs, aData = [3,3], np.array([x,y]);
    mu, k = get_Update_GP(aOpcs, t, aData);
    #Apply Bayesian Algorithm
    x,y = do_Bayesian_Optimization(6, aOpcs, t, mu, k, aData, trgFn);

