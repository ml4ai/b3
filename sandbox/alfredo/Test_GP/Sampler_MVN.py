import numpy as np;
import matplotlib.pyplot as pl;

def plotPts(x,y):
    pl.plot(x,y, 'bo', ms=5);
    nPad = 5;
    pl.axis([min(x)-nPad, max(x)+nPad, min(y)-nPad, max(y)+nPad]);
    pl.show();
    
def mvn_cholesky(mu, k, nsamples):
    ndims = len(mu);
    L = np.linalg.cholesky(k);
    z = np.random.randn(ndims, nsamples);
    mu = np.tile(mu, (nsamples,1)).T;
    x = mu + np.dot(L,z);
    return x;
    
def mvn_svd(mu, k, nsamples):
    ndims = len(mu);
    U,V,D = np.linalg.svd(k);  # @UnusedVariable
    V = np.diag(V);
    z = np.random.randn(ndims, nsamples);
    mu = np.tile(mu, (nsamples,1)).T;
    A = np.dot(U,np.sqrt(V));
    x = mu + np.dot(A,z);
    return x;

def mvn_python(mu, k, nsamples):
    x = np.random.multivariate_normal(mu,k,nsamples);
    return x.T;
    

if __name__ == '__main__':
    k = np.array([[6,5], 
                  [5,6]]);
    mu = np.array([8,5]);
#     s = mvn_cholesky(mu, k, 500);
#     s = mvn_svd(mu, k, 500);
    s = mvn_python(mu, k, 500);    
    plotPts(s[0],s[1]);
    
    