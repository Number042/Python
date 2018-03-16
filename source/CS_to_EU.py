class Twiss_utils:
    """
    This class is an implementation of MDISim tools from C++ into Python. This should serve first of all as a help to understand the
    functioning of MDISim tools
        * The first method __init__() is a special method: class constructor or initialization method. Python calls this constructor
          each time a new instance of this class is created
        * 
    """
    def __init__(self):
        
    def CourantSnderSystem(self, L, Angle, verbose):
        
        # Start displacement vector and rotation matrix - both 0 and unity matrix by default
        V0 = vector(0,0,0)
        
        R = vector(0,0,L[i])
        