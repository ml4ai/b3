from __future__ import division;
# import matplotlib.pyplot as pl;
# import scipy.stats as stats;
import numpy as np;
import warnings;

#It's similar to CRP (and Polya Urn), but using boolean values indicating what
#dishes a client is having (assignment controlled by % of people having taken 
#such dish [by its popularity]) and amount of new dishes (controlled by poisson) 
def get_Indian_Buffet_Process(nAlpha, nPeople):
    #First customer takes poisson(alpha) dishes
    aDish_Assignments = np.ones((1,np.random.poisson(nAlpha)));
    #Check rest of customers
    for i in range(nPeople-1):  # @UnusedVariable
        #Start Next Customer
        aNew_Customer_Dishes = np.zeros((np.shape(aDish_Assignments)[1]));
        iCustomer = i+2;
        #Assign current Dishes
        for j,nDishes in enumerate(np.sum(aDish_Assignments,0)):
            if np.random.rand() <= nDishes/iCustomer:
                aNew_Customer_Dishes[j] = 1;
        #Assign Poisson(alpha/i) new Dishes
        nNew_Dishes = np.random.poisson(nAlpha/iCustomer);
        aNew_Customer_Dishes = np.append(aNew_Customer_Dishes, np.ones((1,nNew_Dishes)));
        #Add the New Costumer to the Matrix of all Customers-Dishes Assignments
        aDish_Assignments = np.hstack([aDish_Assignments, np.zeros((i+1,nNew_Dishes))]);
        aDish_Assignments = np.vstack([aDish_Assignments, aNew_Customer_Dishes]);
    return aDish_Assignments;

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
    np.set_printoptions(suppress=True, precision=3, threshold=10000, linewidth=1000);
    aDish_Assignments = get_Indian_Buffet_Process(2, 10);
    print aDish_Assignments.astype(int);