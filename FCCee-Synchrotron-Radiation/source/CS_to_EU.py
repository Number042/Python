from numpy import cos, sin, array, sqrt, arcsin, arccos, identity
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
    RotY = array( [[cos(theta), 0, sin(theta)], 
                     [0, 1, 0], 
                     [-sin(theta), 0, cos(theta)]] )
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
    return array( [ [sqrt(betx), 0, 0, 0, 0, 0], 
                       [-alfx/sqrt(betx), 1/sqrt(betx), 0, 0, 0, 0], 
                       [0, 0, sqrt(bety), 0, 0, 0], 
                       [0, 0, -alfy/sqrt(bety), 1/sqrt(bety), 0, 0], 
                       [0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 1] ] )

def fourMom2( vec ):
    return vec[0]**2 - vec[1]**2 - vec[2]**2 - vec[3]**2

def RotFrmZ( theta, phi ):
    return array([[1, 0, 0, 0],
                     [0, cos(theta)*cos(phi), -sin(phi), cos(phi)*sin(theta)],
                     [0, cos(theta)*sin(phi), cos(phi), sin(theta)*sin(phi)],
                     [0, -sin(theta), 0, cos(theta)]] )

def RotToZ( theta, phi ):
    return array([ [1, 0, 0, 0],
                      [0, cos(theta)*cos(phi), cos(theta)*sin(phi), -sin(theta)],
                      [0, -sin(phi), cos(phi), 0],
                      [0, cos(phi)*sin(theta), sin(theta)*sin(phi), cos(theta)] ] )

def getRotVec3(vec, verbose = 0):
    cost = vec[2]; theta = arccos(cost); sint = sin(theta)
    if verbose: print('cost = ', cost, '--> theta =', theta)
    
    # only crosscheck
    if verbose: print('sint =', sint, '--> theta =', arcsin(sint), ' --> theta =', sin(theta))

    sinphi = vec[1]/sint; phi = arcsin(sinphi) 
    cosphi = vec[0]/sint

    if verbose: print('sinphi =', sinphi, '--> phi =', arcsin(sinphi))

    # only crosscheck
    if verbose: print('cosphi =', cosphi, '--> phi =', arccos(cosphi)) 

    return theta, phi


def ToEuclidian( df, verbose = 1 ):
    """
    Function to calculate survey coordinates (EU) from TWISS S, X, Y
      -- df: data frame
      -- verbose: debug output level

    RETURN: none, adds x_EU, y_EU, z_EU and rotation matrix W to DF
    """
    
    # init arrays to store rotation matrix and V
    #
    W0 = identity(3); mats = [W0]
    V0 = array( [0, 0, 0] ); vecs = [V0]

    for i in range( df.index.min(), df.index.max() ):
        
        # collect element attributes
        #
        L = df.loc[i, 'L']
        angle = df.loc[i, 'ANGLE']
        name = df.loc[i, 'NAME']
        
        # straight element
        #
        if L == 0 or angle == 0:
            if verbose: print('straight element', name)
            R = array( [0, 0, L] )
            W = mats[i-1]
            
        # bend
        #
        else:
            if verbose: print('dipole', name)
            rho = L/angle
            R = array( [rho*(cos(angle) - 1), 0, rho*sin(angle)] )
            S = RotY(-angle, W0)
            W = mats[i-1]@S
        
        # calculate EU coords for current element (shift and rotation)
        #
        V = mats[i-1]@R + vecs[i-1]
        if verbose: print(V)
            
        # append rotation matrix and position for next iteration
        #
        mats.append(W)
        vecs.append(V)

    df['x_EU'] = [vec[0] for vec in vecs]
    df['y_EU'] = [vec[1] for vec in vecs]
    df['z_EU'] = [vec[2] for vec in vecs]
    df['W'] = mats
    
