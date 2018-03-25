# ----------------------------------------------------------------------------------
# Hierarchical Binary-Template Event Generator
# 2 November 2013
# Author: Clay Morrison
# ----------------------------------------------------------------------------------

## Usage:
# () Test Beta and Exponential distributions and sampling from them
#    plot_beta               : plot Beta distribution
#    plot_beta_sample        : sample from Beta distribution and plot distribution w/ samples
#    plot_exponential        : same for Exponential
#    plot_exponential_sample : same for Exponential
#    
# () Generate and visualize hierarchical binary event data
#    At the end of this file is Model 1: a set of BinaryTemplate specifications
#    Evaluate this file and those templates will be instantiated and associate
#       'l2' is the top-level template
#    After evaluating this file, execute the following:
#       >>> data = l2.sample_hierarchy(4)   # creates 4 top-level intervals (and sub-events)
#       >>> plot_data(data)                 # creates plot of generated data

## Discussion:
# () Should previous state at a given level affect next when parent changes state,
#    or does parent determine child distribution completely?
#       - Currently, children are determined by parent
#       - It seems prior within-level state should depend on both previous 
#         within-level state and parent, as it moving to a new higher-level
#         state might require a "gradual" or "smooth" transition from previous
#         state.  
#         Likely more relevant when beyond binary/nominal to include ordinal:
#           a high-level action requiring a run might require a previous
#           sitting state to transition to standing, accelerating before run state
# () Currently child states can stay in same state when parent changes:
#     0 -------- 1 -------- 0 ----
#     1 -- 0 ----0-- 1 ---- 0 -- 1
#    This happens either b/c parent designates what state child should be in
#       OR, b/c no specific state was desingated but was choosen randonly
#    I this OK?
#    Also, should successive within-level states be allowed to stay the same?
#       - Given a ctbn model, it seems the answer should be no: when a state
#         change happens, it should always be to _another_ state.
# () See sample_ctbn_within_interval for child level sampling variants

# () Should clean up and generalize generator_spec -- right now very clumsy!

# () Templates themselves are currently not recursive
#    -- will need to change some of approach to accommodate this

import sys
import random
import scipy.stats
import numpy
import matplotlib.pyplot as plt

plt.ion()

# ----------------------------------------------------------------------------------
# Utils

def quick_histogram(data, titletext = None, num_bins = 20., barcolor='b'):
    actualmax = max(data)

    step = actualmax / num_bins
    bins = numpy.arange(0., actualmax, step) # 0.01

    plt.figure()
    n, bins, patches = plt.hist(data, bins, normed=1, histtype='bar') # histtype='stepfilled')
    plt.setp(patches, 'facecolor', barcolor, 'alpha', 0.5)

    # empirical stats
    median = numpy.median(data)
    N, (dmin, dmax), mean, uvar, bskew, bkurtosis = scipy.stats.describe(data)
    
    plt.xlabel(r'($N= {0}$, $[{1:.3f}$, ${2:.3f}]$, $median ={3:.3f}$ $\mu ={4:.3f}$, '
             .format(N, dmin, dmax, median, mean) +
             r'$\sigma ={0:.3f}$, $skew ={1:.3f}$, $kurtosis ={2:.3f}$)'
             .format(uvar, bskew, bkurtosis))
    plt.ylabel(r'$p(x)$, hist rel freq of $x$')
    plt.xlim((0,actualmax))
    if titletext: plt.title(titletext)

# ----------------------------------------------------------------------------------
# Beta test

def plot_beta(a = 5., b = 2., color = 'r', 
              loc = 0, scale = 1, new_fig = True, plot_resolution=100):
    # print 'Beta(a:', a, ', b:', b, ')'
    rv = scipy.stats.beta(a, b, loc = loc, scale = scale)
    if new_fig: plt.figure()
    x = numpy.linspace(0, numpy.minimum(rv.dist.b, 3), plot_resolution)
    plt.title(r'Beta ($\alpha = {0}$, $\beta = {1}$)'.format(a,b))
    h = plt.plot(x, rv.pdf(x), color)

def plot_beta_sample(a = 5., b = 2., N = 1000, num_bins = 30):
    rv = scipy.stats.beta(a, b)
    stats = map(lambda a: a[()], rv.stats(moments='mvsk'))
    # sample = rv.rvs(size=N)
    sample = [random.betavariate(a, b) for i in range(N)]
    quick_histogram(sample,
                    r'{0} samples from $Beta(\alpha = {1}$, $\beta = {2})$'.format(N,a,b) +
                    '\n' + r'$\mu = {0:.3f}$, $\sigma={1:.3f}$, $skew={2:.3f}$, $kurtosis={3:.3f}$' \
                    .format(stats[0], stats[1], stats[2], stats[3]),
                    num_bins)
    x = numpy.linspace(0, numpy.minimum(rv.dist.b, 3))
    plt.xlim((0,1.0))
    h = plt.plot(x, rv.pdf(x))
    

# ----------------------------------------------------------------------------------
# Exponential test

def plot_exponential(scale = 6, xmax = 10, new_fig = True, plot_resolution=100):
    # print 'Exponential(scale:', scale, ')'
    rv = scipy.stats.expon(scale = scale)
    if new_fig: plt.figure()
    x = numpy.linspace(0, numpy.minimum(rv.dist.b, xmax), plot_resolution)
    plt.ylim(0, rv.pdf(0)+0.01)
    plt.title(r'$Expon(\lambda ={0})$'.format(scale))
    h = plt.plot(x, rv.pdf(x))

def plot_exponential_sample(scale = 6, N = 1000, num_bins = 30):
    rv = scipy.stats.expon(scale = scale)
    stats = map(lambda a: a[()], rv.stats(moments='mvsk'))
    # sample = rv.rvs(size=N)
    sample = [random.expovariate(1./scale) for i in range(N)]
    quick_histogram(sample,
                    r'{0} samples from $Exponen(\lambda = {1}$)'.format(N,scale) +
                    '\n' + r'$\mu = {0:.3f}$, $\sigma={1:.3f}$, $skew={2:.3f}$, $kurtosis={3:.3f}$' \
                    .format(stats[0], stats[1], stats[2], stats[3]),
                    num_bins)
    xmax = numpy.max(sample)
    x = numpy.linspace(0, xmax)
    plt.ylim(0, rv.pdf(0)+0.01)    
    h = plt.plot(x, rv.pdf(x))


# ----------------------------------------------------------------------------------

class BinaryTemplate:
    """ Binary-state template

    Specifies a CTBN random variable (a continuous time Markov process)
    If it has children, can modulate CTBN states at lower level

    See function btg() (after BinaryTemplate class definition)
       -- this is a convenience fn for specifying BinaryTemplates 
          a little more compactly

    Member slots:
    
    self.prior := numpy.array ; element 0 represents the Bernoulli parameter
    self.intensity_matrix := numpy.matrix representing the IM for the CTBN
    self.children :=
        None  : no children, considered direct observable
        Tuple : a pair of child generator specs for state 0 and state 1
                  (determined by order in tuple: state 0 first, state 1 second)
                Generator spec is a tuple: 
                    ( <child template>, <generation pattern> )
                <child template> : a BinaryTemplate
                <generation pattern> :
                    None : use child template as CTBN and sample from CTBN 
                           across interval
                    tuple : tuple of ordered specific child states; sample 
                            state boundaries
                    integer : specifes number of states within 
                              interval, but sample which state
    self.name := string; can be used to look up template instance from BinaryTemplate.templates
    self.level := 0 = directly observable; 
        higher levels determined by max of children;
        levels currently determined at BinaryTemplate construction time
        NOTE: this needs work: should instead be based on model instance generation time
    """

    templates = {} # global store of all named instance templates
    
    def __init__(self, prior, IM, children=None, name=None, level=0, verbose=True):
        self.prior = prior
        self.intensity_matrix = IM
        self.children = children
        self.name = name
        self.level = level
        if children:
            levels = [child[0].level for child in self.children]
            self.level = max(levels) + 1

        # add named template to class global BinaryTemplate.templates
        # NOTE: does not enforce name uniqueness!  Will overwrite...
        if name: BinaryTemplate.templates[name] = self
            
        if verbose:
            print 'constructed:', self.name, ', level:', self.level, 
            if children: 
                print ', child levels: ', levels
            else:
                print

    # --------------------------------
    # Sampling methods

    def sample_state_from_prior(self):
        """
        Draw Bernouli sample from prior
        NOTE: self.prior[0] is probability of state=0, to be consisten with
              discrete prior distribution over >2 states
        """
        return 0 if random.random() > self.prior[0] else 1

    def sample_ctbn_intervals(self, n = 1, start_time = 0.0, initial_state = None):
        """ 
        Sample as ctbn for n state-change intervals
        Returns list of tuples of (<state>, <end time>, <name>)
        NOTE: Probably most appropriate for root
        """
        state = initial_state
        if initial_state == None:
            state = self.sample_state_from_prior()
        intervals = []
        for s in range(n):
            # rv = scipy.stats.expon(scale = self.q(state))
            # end_time = rv.rvs(size=1)[0] + start_time
            scale = 1. / self.q(state)
            end_time = random.expovariate(scale) + start_time
            intervals.append((start_time, end_time, state, self.name))
            state = 1 - state        # flip state
            start_time = end_time    # update start_time
        return intervals

    def sample_ctbn_within_interval_pattern(self, start_time, end_time, state_pattern, 
                                            beta_plot=False):
        """
        state_pattern := list of n states that will be assigned to sub_intervals
        Find n-1 sub_interval boundaries between start_time and end_time based on 
        ctbn exponential.

        NOTE: state_pattern can allow for sequential same states (e.g., [0, 1, 1, 1]), 
        which violates IM transition probability.  Strange?

        TODO: This should be further tested: generate a bunch of random samples from the same
        interval -- the boundaries should be normally distributed around the value of the
        proportion of the CTBN transition intensities, $q_i$, for the state_pattern sequence.
        """
        qvals = [self.q(i) for i in state_pattern]  # intensity for each state in state_pattern
        remaining_time = end_time - start_time
        sub_interval_end = start_time
        intervals = []
        if beta_plot:
            plt.figure()
            total_time = remaining_time
        for i in range(len(qvals)-1):
            a = qvals[i]          # current state intensity
            b = sum(qvals[i+1:])  # sum of intensities of remaining state_pattern
            sample = random.betavariate(a, b)  # use Beta to sample proportion
            sub_interval_length = sample * remaining_time # scale sample (proportion) by remaining_time
            remaining_time -= sub_interval_length
            sub_interval_end += sub_interval_length
            intervals.append((start_time, sub_interval_end, state_pattern[i], self.name))
            if beta_plot:
                ax = plt.gca()
                color_cycle = ax._get_lines.color_cycle
                next_color = next(color_cycle)
                beta_loc = start_time/total_time
                beta_scale = 1 - beta_loc
                plot_beta(a,b,color=next_color,
                          loc=beta_loc,
                          scale=beta_scale,
                          new_fig=False)
                interval_xrange = [start_time/total_time, sub_interval_end/total_time]
                plt.plot(interval_xrange,[0.5, 0.5],next_color,lw = 4)
                interval_xend = [sub_interval_end/total_time, sub_interval_end/total_time]
                plt.plot(interval_xend,[0, 1],next_color,lw = 2,
                         label=r'$s_{0}={1}$'.format(i,state_pattern[i]))
            start_time = sub_interval_end
        if beta_plot:
            ax = plt.gca()
            color_cycle = ax._get_lines.color_cycle
            next_color = next(color_cycle)
            interval_xrange = [start_time/total_time, end_time/total_time]
            plt.plot(interval_xrange,[0.5, 0.5],next_color,lw = 4)
            interval_xend = [end_time/total_time, end_time/total_time]
            plt.plot(interval_xend,[0, 1],next_color,lw = 2,
                     label=r'$s_{0}={1}$'.format(i+1,state_pattern[-1]))
            plt.legend(loc="upper right")
            plt.title(r'CTBN sampling (Beta) for state pattern ${0}$ in interval $[{1},{2})$' \
                      .format(state_pattern, end_time - total_time, end_time))
            plt.xlabel(r'(normalized) $t$ Time')
            plt.ylabel(r'$Beta(t | t-1, s)$')
        intervals.append((start_time, end_time, state_pattern[-1], self.name)) # last sub-interval
        return intervals
    
    def sample_ctbn_within_interval_n(self, start_time, end_time, n,
                                      beta_plot=False):
        """
        n := number of sub_intervals
        Sample start state from prior
        Find n-1 sub_interval boundaries between start_time and end_time based on
        ctbn exponential.
        """
        state = self.sample_state_from_prior()  # determine first state
        sign = -1 if state else 1               # adjust if first state = 1
        state_pattern = [ state + sign*(i % 2) for i in range(n) ] # alternating states
        return self.sample_ctbn_within_interval_pattern(start_time, end_time, 
                                                        state_pattern, 
                                                        beta_plot)

    def sample_ctbn_within_interval(self, start_time, end_time, initial_state = None):
        """
        Sample start state from prior
        Generate next states until end_time
        """
        state = initial_state
        if initial_state == None:
            state = self.sample_state_from_prior()  # determine first state
        intervals = []
        
        while start_time < end_time:
            scale = 1. / self.q(state)
            sub_interval_end_time = random.expovariate(scale) + start_time
            if sub_interval_end_time >= end_time:
                sub_interval_end_time = end_time
            intervals.append((start_time, sub_interval_end_time, state, self.name))
            state = 1 - state      # flip state
            start_time = sub_interval_end_time  # update start_time
        return intervals

    """
    Other possibilities (require expanding child_spec/generation_pattern format):
    () n > 0 and state_pattern is int : int represents start+state and alternate for n intervals
       Only sample n-1 partitions as nth is determined by end_time
    () n = 0 and state_pattern is int : start with state_pattern state, then as many as fit
    """

    # --------------------------------
    # Sample hierarchy

    # mostly for debugging: counts how many calls to sample hierarchy
    #     and recursive_sample are made
    sample_event_count = 0

    def sample_hierarchy(self, n = 1, start_time = 0.0, initial_state = None):
        """
        Currently assumes starting with sample_ctbn_intervals()
        """
        BinaryTemplate.sample_event_count = 0 # reset class global BinaryTemplate.sample_event_count
        top_intervals = self.sample_ctbn_intervals(n, start_time, initial_state)
        intervals = []
        for (start_time, end_time, state, name) in top_intervals:
            intervals += self.recursive_sample(state, start_time, end_time)
        return top_intervals + intervals

    def recursive_sample(self, state, start_time, end_time):

        BinaryTemplate.sample_event_count += 1
        print 'recursive sample:', BinaryTemplate.sample_event_count, \
          self.name, state, start_time, end_time
        
        intervals = []
        if self.children:
            child = self.children[state]
            child_template = child[0]
            generator_spec = child[1]
            new_intervals = []
            if generator_spec == None:
                new_intervals = child_template.sample_ctbn_within_interval(start_time, end_time)
            elif isinstance(generator_spec, tuple):
                new_intervals = child_template.sample_ctbn_within_interval_pattern(start_time, 
                                                                                   end_time,
                                                                                   generator_spec)
            elif isinstance(generator_spec, int):
                new_intervals = child_template.sample_ctbn_within_interval_n(start_time, 
                                                                             end_time, 
                                                                             generator_spec)
            else:
                print "ERROR: in recursive_sample(state = {0}, start_time = {1}, end_time = {2})" \
                    .format(state, start_time, end_time)
                print "generator_spec:", generator_spec
                print "(associated with child_template:", child_template.name, ")"
                print "... is not one of None, list, or int."
                sys.exit() # bail
            recursive_intervals = []
            for new_interval in new_intervals:
                new_start_time = new_interval[0]
                new_end_time = new_interval[1]
                new_state = new_interval[2]
                recursive_intervals += child_template.recursive_sample(new_state, 
                                                                       new_start_time, 
                                                                       new_end_time)
            intervals += new_intervals + recursive_intervals
        return intervals

    # --------------------------------
    # Helpers

    def q(self, i, j=None):
        if j == None:
            return -self.intensity_matrix[i,i]
        else:
            return self.intensity_matrix[i,j]

    # --------------------------------
    # Display

    def pprint(self, parent_name = None):
        print "\nBinaryTemplate '{0}'".format(self.name)
        if parent_name: 
            print "(Child of '{0}')".format(parent_name)
        else:
            print "(ROOT)"
        print "prior:", self.prior
        print "IM:\n", self.intensity_matrix
        if self.children:
            print "children: (({0}, {1}), ({2}, {3}))"\
              .format(self.children[0][0].name,
                      self.children[0][1],
                      self.children[1][0].name,
                      self.children[1][1])
        else:
            print "children: None."

    def pprint_tree(self, parent_name = None):
        """
        Print current template and all children
        """
        self.pprint(parent_name)
        if self.children:
            self.children[0][0].pprint_tree(self.name)
            self.children[1][0].pprint_tree(self.name)


# ----------------------------------------------------------------------------------

def btg(prior0, im1, im2, children = None, name = None, level = None):
    """ BinaryTemplate generator
    Convenience fn that fills in repeated prior and intensity matrix
    parameters for simple BinaryTemplate
    """
    return BinaryTemplate(numpy.array([prior0, 1-prior0]), 
                          numpy.matrix([[ -im1,  im1 ],
                                        [  im2, -im2 ]]),
                          children, name)


# ----------------------------------------------------------------------------------

# NOTE: I wanted this to be a global (not instance) BinaryTemplate class method, 
#       but doesn't seem to work, so treating as separate fn
def plot_data(data):
    """
    Assumes data is list of: (start_time, end_time, state, generator_template_name)
    NOTE: generator_template_name is used to extract level of state.
          This should really be changed so that levels are intrinsic to path
          from generated data tree leaves, not template itself --- eventually
          we may want generation from templates called recursively...
          Also, eventually data streams at a given level will be per group/individual,
          with possible multiple streams per 'level'
    """
    plt.figure()
    for (start_time, end_time, state, generator_template_name) in data:
        generator_template = BinaryTemplate.templates[generator_template_name]
        level = generator_template.level + 1
        color = 'b' if state == 1 else 'y'
        
        interval_xrange = [start_time, end_time]
        interval_yrange = numpy.array([level, level])
        # plt.plot(interval_xrange, interval_yrange, color, lw = 4)
        ax = plt.gca()
        ax.fill_between(interval_xrange, interval_yrange-0.2, interval_yrange+0.2, facecolor = color)
        interval_xend = [end_time, end_time]
        interval_yend = [level - 0.45, level + 0.45]
        plt.plot(interval_xend, interval_yend, color, lw = 1)
    plt.title('Plot of hierarchical binary template data (yellow = 0, blue = 1)')
    plt.xlabel('Time')
    plt.ylabel('Level')


# ----------------------------------------------------------------------------------
# Model 1 template instances
# naming scheme: l = level, p = parent, s = parent state

l0p0s0 = btg(0.4, 2.0, 0.9, None, 'l0p0s0')
l0p0s1 = btg(0.65, 0.9, 2.0, None, 'l0p0s1')

l1p0 = btg(0.3, 7.0, 9.0, ((l0p0s0, (1,0)), (l0p0s1, None)), 'l1p0')

l0p1s0 = btg(0.2, 0.2, 0.2, None, 'l0p1s0')
l0p1s1 = btg(0.5, 1.0, 1.0, None, 'l0p1s1')

l1p1 = btg(0.6, 8.0, 5.0, ((l0p1s0, (0, 1, 0)), (l0p1s1, 2)), 'l1p1')

l2 = btg(0.5, 24.0, 12.0, ((l1p0, None), (l1p1, (1, 0))), 'l2')

