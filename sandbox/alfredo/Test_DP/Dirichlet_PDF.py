import scipy.special as spc;

def beta(aData):
    aGammas = map(lambda x: spc.gamma(x), aData);
    mult_Gamma = reduce(lambda x,y: x*y, aGammas);
    sum_Gamma = spc.gamma(sum(aData));
    return mult_Gamma/sum_Gamma;
        
def dirichlet_pdf(x, alphas):
    nBeta = beta(alphas);
    pts = map(lambda p: p[0]**(p[1]-1), zip(x,alphas));
    nMult_pts = reduce(lambda a,b: a*b, pts);
    return nMult_pts/nBeta;