import numpy as np;

def eval_Samples(s):
    def get_a(l_max,x,v,m):
        aR = np.zeros((l_max,1));
#         v,m = x.var(), x.mean();
        for i in range(1,l_max+1):
            aR[i-1] = get_AutoCorrelation(i,x,v,m);
#             print i,x,"\n";
        n = 1.0 - (1.0/(l_max))*np.sum(np.abs(aR));
        return n;
    def get_AutoCorrelation(l,x,v,m):
        n = len(x);
        nZ = 1.0/((n-l)*v);
        nSumX = np.zeros((n-l,1));
        for i in range(n-l):
#             print x[i], x[i+l];
            nSumX[i] = (x[i]-m)*(x[i+l]-m);
        return nZ*np.sum(nSumX);
    l = len(s);
    nWin = l-10;
    aA = np.zeros((l-nWin,1));
    nZ = 1.0/(l-nWin+1);
    v,m = s.var(), s.mean();
    for k,i in enumerate(range(nWin,l)):
        aA[k] = get_a(i,s[:i+1],v,m);
    return nZ*np.sum(aA);

if __name__ == '__main__':
    s = np.arange(15)+1;
#     s = np.linspace(1,5,20);
#     s = np.random.randint(0,2,20);
#     s = np.ones(100);
#     s[5] = 0.5;
#     s = np.random.randint(1,100,100);
#     s = np.random.randn(100);
#     s = np.random.rand(100);
    print eval_Samples(s);