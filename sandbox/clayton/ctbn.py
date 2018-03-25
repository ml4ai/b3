import numpy
import scipy.linalg

# as column vector
P0b = numpy.matrix([[0.33, 0.33, 0.34]])

Qb = numpy.matrix([[-0.21,  0.2,  0.01],
                   [ 0.05, -0.1,  0.05],
                   [ 0.01,  0.2, -0.21]])

Mb = numpy.matrix([[0.21, 0,   0   ],
                   [0,    0.1, 0   ],
                   [0,    0,   0.21]])

PEb = numpy.matrix([[  0,      20./21.,  1./21.],
                    [ 1./2.,     0,      1./2. ],
                    [20./21.,   1./21.,    0   ]])

PEb_corrected = numpy.matrix([[  0,      20./21.,  1./21.],
                              [ 1./2.,     0,      1./2. ],
                              [ 1./21.,  20./21.,    0   ]])

USb = numpy.matrix([[-0.1,  0.05],
                    [ 0.2, -0.21]])

def Q_from_M_PE(M, PE):
    return M * (PE - numpy.eye(M.shape[0]))

def p_t_given_s(Qx, t, s):
    return numpy.asmatrix(scipy.linalg.expm(Qx * (t - s)))

def p_t(Qx, Px0, t):
    return Px0 * scipy.linalg.expm(Qx * t)

#----------------------------------

def barometric_example_subsystem_dist(t):
    entrance_dist = numpy.matrix([0.5, 0.5])
    S_intensity = numpy.matrix([[-0.1,  0.05],
                                [ 0.2, -0.21]])
    expS = scipy.linalg.expm(S_intensity * t)
    e = numpy.asmatrix(numpy.ones(entrance_dist.shape[0])).T
    return 1 - entrance_dist * expS * e

def barometric_example_subsystem_dist_direct(t):
    """ Example 2.4: distribution in time over when the pressure begins to fall. """
    return 1 - 1.0476*pow(0.960,t) + 0.0476*pow(0.7641,t)

