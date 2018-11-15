from scipy import constants as cnst
from matplotlib import pyplot as plt
import numpy as np 
from mpl_toolkits.mplot3d import Axes3D

class FieldStepper:
    """
    Class to manually simulate a particle traversing the detector solenoid.
    """

    def __init__( self, Ebeam, angle = 0, verbose = 1 ):
        # data directly accessible by the user
        self.Ebeam = Ebeam
        self.verbose = verbose
        self.angle = angle
        self.sol_len = 0

        # define these as private attributes of the class
        self._restEnerg = 511e-6
        self._c0 = cnst.c
        self._elmChrg = cnst.e
        self._eleMass = cnst.m_e
        self._gamma = Ebeam/self._restEnerg
        self._Brho = 10*Ebeam/(self._c0/1e8)
        self._v = self._c0*np.sqrt( (self._gamma*self._gamma -1 )/(self._gamma*self._gamma) ) 

        if verbose:
            print(' ---- beam parameters are ---- \n'
                    '* mass = ', self._restEnerg, ' GeV \n'
                    '* Ebeam = ', self.Ebeam, ' GeV \n'
                    '* gamma = ', self._gamma, '\n'
                    '* Brho = ', self._Brho, '\n'
                    '* angle = ', self.angle, 'rad \n'
                    '* v = ', self._v/self._c0, 'c \n'
                  ' ----------------------------- ')
        
    def setSolenoid( self, length, solStr ):
        """
        Function to specify the solenoid magnet.
            -- length: the magnet length (for the moment assumes same length for asol)
            -- solStr: solenoid strength, following definition of KS in MADX
        RETURNS: list of two tuples (Bx, By, Bz) for solenoid and asolenoid
        """
        self.sol_len = length
        self.fieldSol = ( 0, 0, solStr*self._Brho ) # assume only longitudinal for the moment
        self.fieldAsol = ( 0, 0 , -solStr*self._Brho )

        if self.verbose:
            print(' ---- solenoid specified with ---- \n'
                    '* KS = ', solStr, ' \n'
                    '* length = ', length, ' m \n'
                    ' ------------------------------- ')

        return [self.fieldSol, self.fieldAsol]

    def getBfield( self, position ):
        """
        Function to retrieve the field at a certain position. 
            -- position: current particle position
        RETURNS: tuple of  form (Bx, By, Bz)
        """
        # if solenoid length not specified, stop here
        #
        if self.sol_len == 0: raise ValueError("Solenoid length not specified: l = ", self.sol_len, 'Use setSolenoid first')
        
        # first half of the length is solenoid, second half is the asol
        #
        if 0 <= position <= self.sol_len/2: 
            cur_field = self.fieldSol
        elif self.sol_len/2 < position <= self.sol_len:
            cur_field = self.fieldAsol
        else: 
            raise OutOfFieldRange('Current position', position, 'outside solenoid length')
        
        # returns a tuple of (Bx, By, Bz)
        #
        return cur_field

    def step( self, time_max = 0, x0 = ( 0, 0, 0 ), stepsize = 1e-12 ):
        """
        Function that steps through the magnet and calculates the field dependent trajectory
            -- time_max:    maximum for time range, default 0 means time required to traverse the solenoid
            -- x0:          start position
            -- stepsize:    specify the stepswidth
        RETURNS: lists of horizontal, vertical, and longitudinal position. Further time (np array) and field (list of tuples)
        """
        v = ( self._v*np.sin(self.angle), self._v*np.sin(self.angle), self._v*np.cos(self.angle) )
        
        # if a time limit is not spedified, take the time a particle needs to traverse the solenoid
        if time_max == 0: time = np.arange(0, self.sol_len/self._v, stepsize)
        elif time_max < 0: raise ValueError('Negative time limit not allowed: time_max = ', time_max)
        else: time = np.arange(0, time_max, stepsize)

        # lists to store the positions. Initialized with start position as given from fct. argument
        #
        hor = [x0[0]]; vert = [x0[1]]; longt = [x0[2]]; field_map = [ (0,0,0) ]

        if self.verbose: print('Starting point = ', '(',hor[0],vert[0],longt[0],')')
        n = 1
        for t in time:
            field = self.getBfield( longt[n-1] )
            if self.verbose > 1: print( 'field = ', field, 'at pos = ', longt[n-1], 'n = ', n )
            x = hor[n-1]   + v[0]*np.cos( field[2]*self._elmChrg/(self._eleMass*self._gamma)*t )
            y = vert[n-1]  - v[1]*np.sin( field[2]*self._elmChrg/(self._eleMass*self._gamma)*t )
            z = longt[n-1] + v[2]*t
            if self.verbose > 1: print( 'pos(n-1) = (',hor[n-1],',', vert[n-1],',', longt[n-1],') \n'
                                        'pos(n) = (', x,',', y,',', z,')' )
            hor.append(x); vert.append(y); longt.append(z); field_map.append(field)
            n += 1
        
        return hor, vert, longt, list(time), field_map

    def pltField( self, zDat, fieldDat ):
        """
        Function to plot the field along longitudinal position.
            -- zDat: range of longitudinal particle position
            -- fieldDat: list of tuples [(Bx, By, Bz)]
        RETURNS: none
        """
        Bz = [field[2] for field in fieldDat]
        plt.figure()
        plt.plot( zDat, Bz, 'b:', label = 'Bz' )
        plt.xlabel('z [m]'); plt.ylabel('B [T]'); plt.legend()
        plt.title('field along z')
        return

    def pltProjections( self, xDat, yDat, zDat, fieldMap ):
        """
        Function to plot a 3D projection of the trajectory
            -- xDat, yDat, zDat:    lists containing the data
        """

        # data passed as lists. Sort data depending on Bz to sol and asol and repack new lists for plotting
        #
        sol = [(xDat[inc], yDat[inc], zDat[inc]) for inc in range(0, len(fieldMap)) if fieldMap[inc][2] > 0] 
        xSol = [ tpl[0] for tpl in sol]
        ySol = [ tpl[1] for tpl in sol]
        zSol = [ tpl[2] for tpl in sol]

        asol= [(xDat[inc], yDat[inc], zDat[inc]) for inc in range(0, len(fieldMap)) if fieldMap[inc][2] < 0]
        xASol = [ tpl[0] for tpl in asol]
        yASol = [ tpl[1] for tpl in asol]
        zASol = [ tpl[2] for tpl in asol]

        fig = plt.figure( figsize = (15, 10))
        ax = fig.add_subplot(111, projection = '3d')
        ax.plot( zSol, xSol, ySol, 'b-')        
        ax.plot( zASol, xASol, yASol, 'r:')
        ax.set_xlabel('z$_{EU}$ [m]'); ax.set_ylabel('x$_{EU}$ [m]'); ax.set_zlabel('y$_{EU}$ [m]')
        ax.set_title('3D trajectory \n')
        fig.tight_layout()

        plt.figure( figsize = (8,8))
        ax1 = plt.subplot(221)
        ax1.plot( xSol, ySol, 'b-')
        ax1.plot( xASol, yASol, 'r:')
        ax1.set_title('xy projection')
        ax1.set_xlabel('x [m]'); ax1.set_ylabel('y [m]')
        ax1.hlines(0, ax1.get_xlim()[0], ax1.get_xlim()[1], colors = 'grey', linestyles = '--' )
        ax1.vlines(0, ax1.get_ylim()[0], ax1.get_ylim()[1], colors = 'grey', linestyles = '--' )

        ax2 = plt.subplot(222)
        ax2.plot( zSol, xSol, 'b-')
        ax2.plot( zASol, xASol, 'r:')
        ax2.set_title('zx projection')
        ax2.set_xlabel('z [m]'); ax2.set_ylabel('x [m]')

        ax3 = plt.subplot(212)
        ax3.plot( zSol, ySol, 'b-')
        ax3.plot( zASol, yASol, 'r:')
        ax3.set_title('zy projection')
        ax3.set_xlabel('z [m]'); ax3.set_ylabel('y [m]')
        plt.tight_layout()

        return 

class OutOfFieldRange( Exception ):
    pass
