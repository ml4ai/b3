import string
import numpy as np
import scipy.stats as stats;
from sklearn import hmm

class NB_GammaHMM(hmm._BaseHMM):
    """Hidden Markov Model with Naive Bayes Gamma emissions"""
    def __init__(self, n_components=1, startprob=None, shapes=None, locs=None,
                 scales=None, transmat=None, startprob_prior=None, 
                 transmat_prior=None, algorithm="viterbi", random_state=None, 
                 n_iter=10, thresh=1e-2, params=string.ascii_letters,
                 init_params=string.ascii_letters):
        hmm._BaseHMM.__init__(self, n_components, startprob, transmat,
                          startprob_prior=startprob_prior,
                          transmat_prior=transmat_prior, algorithm=algorithm,
                          random_state=random_state, n_iter=n_iter,
                          thresh=thresh, params=params, init_params=init_params);
        self.nHiddenStates = n_components;
        self.shapes = shapes;
        self.scales = scales;
        self.locs = locs;
        
    def _set_shapes(self, shapes):
        self.shapes = shapes;
        
    def _set_locs(self, locs):
        self.locs = locs;
        
    def _set_scales(self, scales):
        self.scales = scales;

    def _compute_log_likelihood(self, obs):
        nSt = self.nHiddenStates;
        nT = np.shape(obs)[0];
        aLogObs = np.zeros((nT, nSt));
        for t in range(nT):
            for s in range(nSt):
                x = obs[t];
                x[x==0] = 1e-10;
                nShape, nScale = self.shapes[s], self.scales[s];
                aLogPDFs = stats.gamma.logpdf(x,nShape,loc=0,scale=nScale);
                aLogObs[t,s] = np.sum(aLogPDFs);
#         print np.exp(aLogObs);
        return aLogObs;

    def _generate_sample_from_state(self, state, random_state=None):
        pass;

    def _init(self, obs, params='stmc'):
        super(NB_GammaHMM, self)._init(obs, params=params)

    def _initialize_sufficient_statistics(self):
        pass;

    def _accumulate_sufficient_statistics(self, stats, obs, framelogprob,
                                          posteriors, fwdlattice, bwdlattice,
                                          params):
        super(NB_GammaHMM, self)._accumulate_sufficient_statistics(
            stats, obs, framelogprob, posteriors, fwdlattice, bwdlattice,
            params)

    def _do_mstep(self, stats, params):
        super(NB_GammaHMM, self)._do_mstep(stats, params)
