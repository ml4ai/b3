from __future__ import division;
import matplotlib.pyplot as pl;
import scipy.stats as stats;
import numpy as np;
import warnings;

#It's exactly the same as Polya Urn Model, but by using Integers & instead
#of getting a New Real sample scalar value, we just get Next New Table index.
def get_Chinese_Restaurant_Process(base_pdf_sampler, nAlpha, nPeople):
    aTable_Assignments = [1]; # first customer sits at table 1
    nNext_Open_Table = 2;  # index of the next empty table  
    for i in range(1,nPeople-1):  # @UnusedVariable
        if np.random.rand() <= nAlpha/(nAlpha + i):
            aTable_Assignments.append(nNext_Open_Table);
            nNext_Open_Table += 1;
        else:
            nCurrent_Table = aTable_Assignments[np.random.randint(0,len(aTable_Assignments))];
            aTable_Assignments.append(nCurrent_Table);
    return aTable_Assignments;

def plot_CRP(aTable_Assignments):
    mTable_Assignments = {};
    for nTable in aTable_Assignments:
        if mTable_Assignments.has_key(nTable): mTable_Assignments[nTable] += 1;
        else: mTable_Assignments[nTable] = 1;
    pl.stem(mTable_Assignments.keys(), mTable_Assignments.values());
    pl.show();

def sampler_pdf_Func():
    s = stats.norm.rvs(loc=0, scale=1, size=1)[0]; #Gaussian
    return s;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3);
    aTable_Assignments = get_Chinese_Restaurant_Process(sampler_pdf_Func, 5, 100);
    plot_CRP(aTable_Assignments);