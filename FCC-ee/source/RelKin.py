from numpy import array

def Boost( gam, bet ):
    return array( [ [gam, 0, 0, -bet*gam],
                       [0, 1, 0, 0],
                       [0, 0, 1, 0],
                       [-bet*gam, 0, 0, gam] ] )