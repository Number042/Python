import numpy as np
# class Twiss_utils:

#     """
#     This class is an implementation of MDISim tools from C++ into Python. This should serve first of all as a help to understand the
#     functioning of MDISim tools
#         * The first method __init__() is a special method: class constructor or initialization method. Python calls this constructor
#           each time a new instance of this class is created
#         * 
#     """
#     def __init__(self, verbose):
#         self.verbose = verbose

#     def CourantSnderSystem(self, L, Angle, verbose):
        
#         # Start displacement vector and rotation matrix - both 0 and unity matrix by default
#         V0 = vector(0,0,0)
        
#         R = vector(0,0,L[i])

#         return R



# Define transformations required for rotations and vector calculations
#
def RotY(theta, vec):
    RotY = np.array( [[np.cos(theta), 0, np.sin(theta)], 
                     [0, 1, 0], 
                     [-np.sin(theta), 0, np.cos(theta)]] )
    rotVec = RotY @ vec
    return rotVec

# can be replaced by numpy internal norm
def vec2(vec):
    """
    Simple tool to square three-vector
    """
    return vec[0]**2 + vec[1]**2 + vec[2]**2


def FromNorm(betx, bety, alfx, alfy):
    """
    Go from normalized to real coordinates, based on twiss parameters
      -- betx,y:  beta functions in both planes
      -- alfx,y:  slope in both planes (0 at virtual point)
    """
    return np.array( [ [np.sqrt(betx), 0, 0, 0, 0, 0], 
                       [-alfx/np.sqrt(betx), 1/np.sqrt(betx), 0, 0, 0, 0], 
                       [0, 0, np.sqrt(bety), 0, 0, 0], 
                       [0, 0, -alfy/np.sqrt(bety), 1/np.sqrt(bety), 0, 0], 
                       [0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 1] ] )

def fourMom2( vec ):
    return vec[0]**2 - vec[1]**2 - vec[2]**2 - vec[3]**2

def RotFrmZ( theta, phi ):
    return np.array([[1, 0, 0, 0],
                     [0, np.cos(theta)*np.cos(phi), -np.sin(phi), np.cos(phi)*np.sin(theta)],
                     [0, np.cos(theta)*np.sin(phi), np.cos(phi), np.sin(theta)*np.sin(phi)],
                     [0, -np.sin(theta), 0, np.cos(theta)]] )

def RotToZ( theta, phi ):
    return np.array([ [1, 0, 0, 0],
                      [0, np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), -np.sin(theta)],
                      [0, -np.sin(phi), np.cos(phi), 0],
                      [0, np.cos(phi)*np.sin(theta), np.sin(theta)*np.sin(phi), np.cos(theta)] ] )

def getRotVec3(vec, verbose = 0):
    cost = vec[2]; theta = np.arccos(cost); sint = np.sin(theta)
    if verbose: print('cost = ', cost, '--> theta =', theta)
    
    # only crosscheck
    if verbose: print('sint =', sint, '--> theta =', np.arcsin(sint), ' --> theta =', np.sin(theta))

    sinphi = vec[1]/sint; phi = np.arcsin(sinphi) 
    cosphi = vec[0]/sint;

    if verbose: print('sinphi =', sinphi, '--> phi =', np.arcsin(sinphi))

    # only crosscheck
    if verbose: print('cosphi =', cosphi, '--> phi =', np.arccos(cosphi)) 

    return theta, phi


        