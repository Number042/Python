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
        self._epfac = self._elmChrg/(self._eleMass*self._gamma*self._v)

        if verbose:
            print(' ---- beam parameters are ---- \n'
                    '* mass = ', self._restEnerg, ' GeV \n'
                    '* Ebeam = ', self.Ebeam, ' GeV \n'
                    '* gamma = ', self._gamma, '\n'
                    '* Brho = ', self._Brho, '\n'
                    '* angle = ', self.angle, 'rad \n'
                    '* v = ', self._v/self._c0, 'c \n'
                    '* epfac =', self._epfac, '\n'
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
                    '* B =', self.fieldSol, 'T \n'
                    '* length = ', length, ' m \n'
                    ' ------------------------------- ')

        return [self.fieldSol, self.fieldAsol]

    def getBfield( self, position ):
        """
        Function to retrieve the field at a certain position. 
            -- position: current longitudinal particle position (z comp)
        RETURNS: tuple of  form (Bx, By, Bz)
        """
        # if solenoid length not specified, stop here
        #
        if self.sol_len == 0: raise ValueError("Solenoid length not specified: l = ", self.sol_len, 'Use setSolenoid first')
        
        # first half of the length is solenoid, second half is the asol
        #
        if 0 <= position <= (self.sol_len/np.cos(self.angle))/2: 
            cur_field = self.fieldSol
        elif (self.sol_len/np.cos(self.angle))/2 < position <= (self.sol_len/np.cos(self.angle)):
            cur_field = self.fieldAsol
        else: 
            raise OutOfFieldRange('Current position', position, 'outside solenoid length')
        
        # returns a tuple of (Bx, By, Bz)
        #
        return cur_field

    def step( self, time_max = 0, x0 = ( 0, 0, 0 ), v0 = ( 1, 1, 1 ), dt = 1e-12 ):
        """
        Function that steps through the magnet and calculates the field dependent trajectory
            -- time_max:    maximum for time range, default 0 means time required to traverse the solenoid
            -- x0:          start position
            -- dt:          increment in time
        RETURNS: lists of position and speed tuples. Further time (np array) and field (list of tuples)
        """
        # lists to store the positions. Initialized with start position as given from fct. argument
        #
        pos = [(x0[0], x0[1], x0[2])]; vel = [(v0[0], v0[1], v0[2])]; field_map = [ (0,0,0) ]
        if self.verbose: print('Starting point = ', x0, 'speed =', v0)
        
        # if a time limit is not spedified, take the time a particle needs to traverse the solenoid
        #
        if time_max == 0: time = np.arange(0, self.sol_len/self._v, dt)
        elif time_max < 0: raise ValueError('Negative time limit not allowed: time_max = ', time_max)
        else: time = np.arange(0, time_max, dt)
        
        if self.verbose > 1: print('chosen range =', time)
        
        # think about new implementation. It should use the initial position and velocity (based on entry angle)
        # then calculate positions by invoking changing velocities due to Lorentz force. 
        #
        n =1
        # for deltaS in np.arange(0,self.sol_len, ds):
        for t in time:    
            field = self.getBfield( pos[n-1][2] )
            if self.verbose > 1: print('n:', n, 'field =', field, 'at pos =', pos[n-1][2])
            field_map.append(field)
            
            # general idea: v_i = v_i-1 + dv*dt, then update
            vx = vel[n-1][0] + (vel[n-1][1]*field[2] - vel[n-1][2]*field[1])*dt 
            vy = vel[n-1][1] + (vel[n-1][2]*field[0] - vel[n-1][0]*field[2])*dt
            vz = vel[n-1][2] + (vel[n-1][0]*field[1] - vel[n-1][1]*field[0])*dt
            vel.append( (vx, vy, vz) )
            
            # general idea: x_i = x_i-1 + v_i*dt
            x = pos[n-1][0] + self._epfac*vx*dt  
            y = pos[n-1][1] + self._epfac*vy*dt 
            z = pos[n-1][2] + self._epfac*vz*dt 
            # update position
            pos.append( (x, y, z) )
            # print('current velocity =', vel[n], 'at ', pos[n], 'and field =', field)

            n += 1

        return pos, vel, list(time), field_map

    def pltField( self, posTup, fieldTup ):
        """
        Function to plot the field along longitudinal position.
            -- posTup: list of tuples storing particle position [(x,y,z)]
            -- fieldTup: list of tuples [(Bx, By, Bz)]
        RETURNS: none
        """
        z = [elm[2] for elm in posTup]
        Bz = [field[2] for field in fieldTup]; By = [field[1] for field in fieldTup]; Bx = [field[0] for field in fieldTup]
        plt.figure()
        plt.plot( z, Bz, 'b:', label = 'Bz' ); plt.plot( z, Bx, 'r:', label = 'Bx'); plt.plot( z, By, 'g:', label = 'By')
        plt.xlabel('z [m]'); plt.ylabel('B [T]'); plt.legend()
        plt.title('field along z')
        return
    
    def pltSpeed( self, posTup, velTup ):
        """
        """
        z = [elm[2] for elm in posTup]
        velX = [v[0] for v in velTup]
        velY = [v[1] for v in velTup]
        velZ = [v[2] for v in velTup]

        plt.figure()
        plt.plot( z, velX, 'r--', label = '$v_x$')
        plt.plot( z, velY, 'g--', label = '$v_y$')
        plt.plot( z, velZ, 'b--', label = '$v_z$')
        plt.xlabel('z [m]'); plt.ylabel('v [m/s]'); plt.legend()
        plt.title('speed along z')
        return

    # def pltProjections( self, xDat, yDat, zDat, fieldMap ):
    def pltProjections( self, posTup, fieldTup ):
        """
        Function to plot a 3D projection of the trajectory
            -- xDat, yDat, zDat:    lists containing the data
        """

        # data passed as lists. Sort data depending on Bz to sol and asol and repack new lists for plotting
        #
        # sol = [(xDat[inc], yDat[inc], zDat[inc]) for inc in range(0, len(fieldMap)) if fieldMap[inc][2] > 0] 
        sol = [ (posTup[inc][0], posTup[inc][1], posTup[inc][2]) for inc in range(len(fieldTup)) if fieldTup[inc][2] > 0 ]
        xSol = [ tpl[0] for tpl in sol]
        ySol = [ tpl[1] for tpl in sol]
        zSol = [ tpl[2] for tpl in sol]

        # asol= [(xDat[inc], yDat[inc], zDat[inc]) for inc in range(0, len(fieldMap)) if fieldMap[inc][2] < 0]
        asol = [ (posTup[inc][0], posTup[inc][1], posTup[inc][2]) for inc in range(len(fieldTup)) if fieldTup[inc][2] < 0]
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
