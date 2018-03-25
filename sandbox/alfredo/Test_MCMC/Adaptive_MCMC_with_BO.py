from MySampler_GP_PostPred import *;
import scipy.stats as stats;  # @UnusedImport
import warnings;

def get_Metropolis(nIters, initSt, f_TrgPdf, f_PropQ, v):
    aX = np.zeros((nIters, 1));
    aX[0] = initSt;
    for i in range(nIters-1):
        #STEP 1: (SIMULATION OF X)
        q = f_PropQ(aX[i], v);
        u = np.random.rand();        
        #STEP 2: (NEXT-STATE EVALUATION)
        nR = f_TrgPdf(q)/f_TrgPdf(aX[i]); #Due to Symmetric PropQ [Metropolis Algorithm]
        if u <= np.min([1,nR]): aX[i+1] = q;
        else: aX[i+1] = aX[i];
    return aX;

#Target Distributions F(x)
def f_TrgPdf(x): #Mixture of Gaussians
    z1 = stats.norm.pdf(x, loc=-4.5, scale=1);
    z2 = stats.norm.pdf(x, loc=4.5, scale=1);
    aW = [0.4, 0.6];
    return aW[0]*z1 + aW[1]*z2;

#Proposal Distributions Q(x|y)
def f_PropQ(x,v=1): #Gaussian
    s = x + v*np.random.randn();
#     while s<-10 or s>10:
#         s = x + v*np.random.randn();
    return s;

#------------------------------------------------------------------------------

#Objective Functions
def fn_Polynomial(x):
    return -((x+1)*(x-1)**2*(x-0));

#Acquisition Functions
def fn_Acq_UCB(i,x, mu, k, nMaxD):
    nK = 1;
    nUCB = mu[i] + nK*k[i,i];
    return nUCB;

def plot_BO(t, k, mu, aData, y, aSamples, iMaxX, iFig, nIters):
    #Plot Gaussian Process
    pl.ion();
    pl.subplot(3,1,1);
    pl.title('Gaussian Process ['+str(iFig+1)+'/'+str(nIters)+']');
    nPad = 2;
    var = k.diagonal();
    pl.plot(aData[0],aData[1], 'o');
    pl.gca().fill_between(t.flat, mu-var, mu+var, color="#dddddd"); #Variance
    pl.plot(t,mu, 'r'); #Mean
    pl.axis([min(t)-nPad, max(t)+nPad, -nPad, nPad]);    
    #Plot Acquisition Function
    pl.subplot(3,1,2);
    pl.title('Aquisition Function');
    pl.plot(t,y);
    pl.plot(t[iMaxX],y[iMaxX], marker='o', ms=5);
    pl.axis([min(t)-nPad, max(t)+nPad, -nPad, +nPad]);
    pl.subplot(3,1,3);
    pl.title('Samples');
    nBins = 100;
    nSamples = len(aSamples);
    pl.hist(aSamples, nBins, weights=np.ones(nSamples)*(1.0/nSamples));
    pl.savefig('./Plots_Adaptive_MCMC_BO/Fig_'+str(iFig)+'.png');
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

def eval_Samples(s):
    def get_a(l_max,x):
        aR = np.zeros((l_max,1));
        v,m = x.var(), x.mean();
        for i in range(1,l_max+1):
            aR[i-1] = get_AutoCorrelation(i,x,v,m);
        return 1.0 - (l_max**-1.0)*np.sum(np.abs(aR));
    def get_AutoCorrelation(l,x,v,m):
        n = len(x);
        nZ = 1.0/((n-l)*v);
        nSumX = np.zeros((n-l,1));
        for i in range(n-l):
            nSumX[i] = (x[i]-m)*(x[i+l]-m);
        return nZ*np.sum(nSumX);
    l = len(s);
    nWin = l-25; #int(round(l*0.9));
    aA = np.zeros((l-nWin,1));
    nZ = 1.0/(l-nWin+1);
    for k,i in enumerate(range(nWin,l)):
        aA[k] = get_a(i,s[:i+1]);
#         print k+1,aA[k];
    return nZ*np.sum(aA);

def do_Bayesian_Optimization(nIters, aOps, t):
    xd, yd, nL = None, None, 100;
    x, aS = 1, None;
    for i in range(nIters):  # @UnusedVariable
        #Run MCMC for L samples with Param x    
        s = get_Metropolis(nL, 0, f_TrgPdf, f_PropQ, x);
        #Get y from Samples drawn
        y = eval_Samples(s);
        #Update the GP with new [x,y]
        xd = np.vstack([xd,x]) if xd!=None else np.array([[x]]).T;
        yd = np.vstack([yd,y]) if yd!=None else np.array([[y]]).T;
        mu, k = get_Update_GP(aOps, t, np.array([xd,yd]));
        #Find best Param x with GP    
        x, iMaxX, aAcq = get_Best_x(t, mu, k, fn_Acq_UCB, np.max(yd));
        aS = np.vstack([aS,s]) if aS!=None else s;
        plot_BO(t, k, mu, np.array([xd,yd]), aAcq, aS, iMaxX, i, nIters);
    return xd, yd;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    t = np.linspace(0.1,10,50).reshape(-1,1); #Queries x*
    #Apply Bayesian Algorithm
    x,y = do_Bayesian_Optimization(10, [3,3], t);

