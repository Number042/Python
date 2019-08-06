import numpy as np
import random as rnd

def genPlanck( stats ):

    # define some constants; a,b,c specific for this generator
    c = .648; a = 1.266; b = -.6
    
    # define interval boundaries
    x1 = c; x2 = (np.log(c) - a)/b; xDiff = x2 - x1

    # basically solutions to the integrals I_1 to I_3
    p1 = x1*x1/2; p2 = x1*xDiff; p3 = -1/b*np.exp(a + b*x2)
    P12 = p1/(p1+p2+p3); P23 = (p1+p2)/(p1+p2+p3)

    values = []; i = 0
    while i < stats:

        # generate a couple of random numbers on (0,1)
        r1 = rnd.uniform(0,1)
        r2 = rnd.uniform(0,1)
        r3 = rnd.uniform(0,1)

        # choose which function to use, based on interval
        if r1 < P12: 
            w = x1*np.sqrt(r2)
            if w > (np.exp(w) - 1)*r3: 
                values.append(w)
                i += 1 
        elif r1 < P23: 
            w = x1 + xDiff*r2
            if w**2 > x1*(np.exp(w) - 1)*r3: 
                values.append(w)
                i += 1
        else: 
            w = x2 + np.log(r2)/b
            if w**2 > (np.exp(w) - 1)*np.exp(a + b*w)*r3: 
                values.append(w)
                i += 1
        
    return np.asarray(values)

def cmpt(x, m0, k):
        return (1 + x**2 + m0/(m0 + k*(1-x)) + (m0 + k*(1-x))/m0 - 2)*(m0/(m0 + k*(1-x)))**2

def genCompt( energ, m0, verbose = 0 ):
    vls = []; stp = 0
    while stp < 1:
        cost = np.random.uniform(-1,1)
        r2 = np.random.uniform(0,1)

        if cmpt( cost, m0, energ ) > 2*r2:
            if verbose: print('accept cost =', cost, 'at energy =', energ)
            vls.append( cost )
            stp += 1

    return cost
        

