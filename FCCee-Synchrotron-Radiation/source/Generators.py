from numpy import exp, random, log, sqrt, asarray
import random as rnd

def genPlanck( stats ):
    """
    Simple generator for the energy spectrum of thermal photons. Follows the Planck distribution
        -- stats: number of overall events

    RETURNS: array of photon energies.
    """

    # define some constants; a,b,c specific for this generator
    c = .648; a = 1.266; b = -.6
    
    # define interval boundaries
    x1 = c; x2 = (log(c) - a)/b; xDiff = x2 - x1

    # basically solutions to the integrals I_1 to I_3
    p1 = x1*x1/2; p2 = x1*xDiff; p3 = -1/b*exp(a + b*x2)
    P12 = p1/(p1+p2+p3); P23 = (p1+p2)/(p1+p2+p3)

    values = []; i = 0
    while i < stats:

        # generate a couple of random numbers on (0,1)
        r1 = rnd.uniform(0,1)
        r2 = rnd.uniform(0,1)
        r3 = rnd.uniform(0,1)

        # choose which function to use, based on interval
        if r1 < P12: 
            w = x1*sqrt(r2)
            if w > (exp(w) - 1)*r3: 
                values.append(w)
                i += 1 
        elif r1 < P23: 
            w = x1 + xDiff*r2
            if w**2 > x1*(exp(w) - 1)*r3: 
                values.append(w)
                i += 1
        else: 
            w = x2 + log(r2)/b
            if w**2 > (exp(w) - 1)*exp(a + b*w)*r3: 
                values.append(w)
                i += 1
        
    return asarray(values)

def cmpt(x, m0, k):
        return (1 + x**2 + m0/(m0 + k*(1-x)) + (m0 + k*(1-x))/m0 - 2)*(m0/(m0 + k*(1-x)))**2

def genCompt( energ, m0, verbose = 0 ):
    """
    Simple generator for scattering angle follwoing the Compton cross section
        -- energ:   a photon energy
        -- m0   :   electron rest mass
        -- verbose: set level of output information

    RETURNS: value for cosine(theta) and number of events called before value was accepted
    """
    stp = 0; count = 0
    while stp < 1:
        count += 1
        cost = random.uniform(-1,1)
        r2 = random.uniform(0,1)
        if verbose: print('generate cost, r2:', cost, r2)
        if cmpt( cost, m0, energ ) > 2*r2:
            stp += 1
            if verbose: print('Counter after acceptance:', count, '\n accept cost =', cost, 'at energy =', energ)
    
    return cost, count

def kratio(m0, k, cost):
    return m0/(m0 + k*(1 - cost))

        

