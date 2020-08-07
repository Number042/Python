from numpy import sqrt, genfromtxt, float32, array, pi, abs, cos, sin, random
from matplotlib import pyplot as plt
from CS_to_EU import FromNorm, RotY
from TfsTables import TfsReader
from Tools import sbplSetUp, readTwissParams

class Beam:
    
    def __init__(self, beamFile, strtElm, twiss, Emit, Npart, halfCross, pc, verbose = 0):
        
        self.beamFile = beamFile
        self.strtElm = strtElm
        self.Emit = Emit
        self.twiss = twiss
        self.Npart = int(Npart)
        self.verbose = verbose
        self.HalfCross = halfCross
        self.pc = pc

        self.Eb = sqrt(pc**2 - (511e-6)**2)

        if verbose: print("Create beam. \n    * Using file ", beamFile, "\n    * Number of particles:", Npart, '\n at energy Eb =', self.Eb)

    def read_beam_size(self, dim):
        """
        Method to read in the beam gun information from the Fields_from_tfs output
            -- beamFile: .dat file to read information from

        RETURNS: array with sig_xn, sig_xn', sig_yn, sig_yn', sig_z, sig_e
        """
        
        beamsize = genfromtxt(self.beamFile, delimiter = None, skip_header = 2, max_rows = 1 )
        
        if self.verbose: print("Beam sizes:", beamsize)
        
        if dim == 'x': 
            if self.verbose: print("selected plane: ", dim, "sigma = ", beamsize[0] )
            return float32(beamsize[0])
        
        elif dim == 'y': 
            if self.verbose: print("selected plane: ", dim, "sigma = ", beamsize[2] )
            return float32(beamsize[2])

    def read_v_EU(self):

        v_eu = genfromtxt( self.beamFile, delimiter = None, skip_header = 3, max_rows = 1 )[3:]
        if self.verbose: print('reading v_EU from', self.beamFile, '=', v_eu)
        
        return array( [float32(v_eu[0]), float32(v_eu[1]), float32(v_eu[2]) ] )

    def set_pencil( self ):

        # maybe not required
        #
        phi = random.uniform(0, 2*pi)
        x = random.uniform(0,1)

        # all centered at 0 
        #
        BeamVecX     = 0*x*cos(phi)
        BeamVecXprim = 0*x*sin(phi)

        BeamVecY     = 0*x*cos(phi)
        BeamVecYprim = 0*x*sin(phi)

        return BeamVecX, BeamVecXprim, BeamVecY, BeamVecYprim
        
    def set_gauss( self ):
        """
        Method to plot a random Gaussian distribution in x,x' and y,y'.
        Normalization with the emittance epsx
            -- beamsize: specify beam size in x and y as list

        RETURNS: x,x' and y,y' in normalized coordinates
        """
        
        from random import gauss
        from Tools import Gauss

        phi = random.uniform(0, 2*pi)
        x = random.uniform(0,6)
        y = random.uniform(0,1)

        print('Beam size not provided. Read from TWISS based on start element', self.strtElm )
        sigmX = sqrt( self.twiss.loc[ self.twiss.NAME == self.strtElm,'BETX' ].values[0]*self.Emit[0] )
        sigmY = sqrt( self.twiss.loc[ self.twiss.NAME == self.strtElm,'BETY' ].values[0]*self.Emit[1] )
        beamsize = [sigmX, sigmY]
        
        val = Gauss(x)
        if y < val:

            BeamVecX     = beamsize[0]*x*cos(phi)
            BeamVecXprim = beamsize[0]*x*sin(phi)

            BeamVecY     = beamsize[1]*x*cos(phi)
            BeamVecYprim = beamsize[1]*x*sin(phi)

            if self.verbose > 1: print ("BeamVecX =", BeamVecX, '\n', "BeamVecY =", BeamVecY)
        
            return BeamVecX, BeamVecXprim, BeamVecY, BeamVecYprim
        
        else: pass

    def set_ring( self, Nsig, beamsize ):
        """    
        Method to create flat random distribution in x,x'.
        Normalization by +- nsig
            -- amplt: amplitude, Nsig - radius of the ring 

        RETURNS: arrays for x,x' and y,y'
        """
                    
        # phi = array([2*pi*i/self.Npart for i in range(self.Npart)])
        phi = random.uniform(0,2*pi)
        
        # horizontal plane -- generate x,x'
        #
        BeamVecX     = abs(Nsig[0])*beamsize[0]*cos(phi)
        BeamVecXprim = abs(Nsig[0])*beamsize[0]*sin(phi)

        # vertical plane -- generate y,y'
        #
        BeamVecY     = abs(Nsig[1])*beamsize[1]*cos(phi)
        BeamVecYprim = abs(Nsig[1])*beamsize[1]*sin(phi)

        return BeamVecX, BeamVecXprim, BeamVecY, BeamVecYprim
            
    def set_expTail( self, Nsig, beamsize):

        from numpy import log
        from Tools import Gauss, tail

        x = random.uniform(0,6)
        y = random.uniform(0,1)

        y1 = random.uniform(0,1)
        y2 = random.uniform(0,1)
        phi= random.uniform(0,2*pi)

        val = Gauss(x)        
        xval = beamsize[0]*tail(y1,y2, Nsig[0])
        yval = beamsize[1]*tail(y1,y2, Nsig[1])
        
        if y < val:

            # horizontal plane -- generate x,x'
            #
            BeamVecX     = xval*cos(phi)
            BeamVecXprim = xval*sin(phi)
            
            # vertical plane -- generate y,y'
            #
            BeamVecY     = yval*cos(phi)
            BeamVecYprim = yval*sin(phi)

            return BeamVecX, BeamVecXprim, BeamVecY, BeamVecYprim
        
        else: pass

    def generate_Bunch( self, Type = 'pencil', Nsig = [10,10] ):
        
        from numpy import log, random

        if self.strtElm:
            print( 'generating beam at', self.strtElm )

        beamsizeX = self.read_beam_size('x')
        beamsizeY = self.read_beam_size('y')

        # trafo from normalized CS to CS (at start element)
        #
        FrmNrm = FromNorm( self.twiss.loc[self.twiss.NAME == self.strtElm,'BETX'].values[0], self.twiss.loc[self.twiss.NAME == self.strtElm,'BETY'].values[0], 
                           self.twiss.loc[self.twiss.NAME == self.strtElm,'ALFX'].values[0], self.twiss.loc[self.twiss.NAME == self.strtElm,'ALFY'].values[0] )

        if self.verbose: print('At', self.strtElm, '\nFromNorm = \n', FrmNrm)

    
        v_EU = genfromtxt( self.beamFile, delimiter = None, skip_header = 3, max_rows = 1 )[3:]
        if self.verbose: print('reading EU start position from', self.beamFile, '=', v_EU, '\n', type(v_EU) )

        posEU = []; dirEU = []
        i = 0
        while i < self.Npart:
            
            # generate x,x' and y,y'
            #
            if Type == 'pencil':
                prims = self.set_pencil()
            elif Type == 'gauss':
                prims = self.set_gauss( [beamsizeX,beamsizeY] )
            elif Type == 'ring':
                prims = self.set_ring( Nsig, [beamsizeX,beamsizeY] )
            elif Type == 'tails':
                prims = self.set_expTail( Nsig, [beamsizeX,beamsizeY] )
            
            # add to v_n_CS
            #
            if prims is not None:
                # in_n_CS = array( [func returns tuple for X (based on input), func returns tuple for Y (based on input), 0, 0] ) same func
                in_n_CS = array( [prims[0], prims[1], prims[2], prims[3], 0, 0] )
                # if self.verbose > 1: print(i, prims, '\n', in_n_CS )
            
                # trafo v_n_CS to v_CS
                #
                inCS = FrmNrm @ in_n_CS
                posCS = array( [inCS[0], inCS[2], inCS[4]] )
                dirCS = array( [inCS[1], inCS[3], sqrt(1 - inCS[1]**2 - inCS[3]**2)] )

                # rot to EU
                #
                posEU.append( (RotY(-self.HalfCross, posCS) +  v_EU) )
                dirEU.append( RotY(-self.HalfCross, dirCS) ) 
                
                i += 1

        return posEU, dirEU

    def gen_BeamEnergy(self, Edes, acceptance):

        from random import gauss
        """
        Function to generate the beam energy according to a Gaussian distribution.
            -- Edes:        design energy
            -- acceptance:  energy acceptance of a machine
        
        RETURNS: array of beam energies of length Npart
        """

        return array([ gauss(Edes, acceptance) for i in range(self.Npart) ] )

    def gen_BeamMom( self, elm ):
        """
        Function to generate the three-momentum of beam particles.
            -- elm: element at which the beam is generated (used for trafo normalized --> physical)

        RETURNS: array of single dir_EU
        """
        # new way wiso implemewist: hard coded with line number for respective element.
        #
        # lineNumber =  readTwissParams( self.twiss, elm )
        # twissParam = genfromtxt( self.twiss, delimiter = None, skip_header = lineNumber, max_rows = 1 )
        # betx, alfx, bety, alfy = twissParam[3], twissParam[4], twissParam[6], twissParam[7]
        FrmNrm = FromNorm( self.twiss.loc[self.twiss.NAME == elm,'BETX'].values[0], self.twiss.loc[self.twiss.NAME == elm,'BETY'].values[0], 
                           self.twiss.loc[self.twiss.NAME == elm,'ALFX'].values[0], self.twiss.loc[self.twiss.NAME == elm,'ALFY'].values[0] )
        print('FromNorm(', elm, ') = \n', FrmNrm)

        vecsNCS = array( [array([self.BeamVecX[i], self.BeamVecXprim[i], self.BeamVecY[i], self.BeamVecYprim[i], 0, 0]) for i in range(self.Npart) ] )
        
        vecsCS = array([ FrmNrm @ vec for vec in vecsNCS ] )
        dirsCS = array([[vec[0], vec[2], sqrt(1 - vec[0]**2 - vec[2]**2)] for vec in vecsCS ] )
        dirsEU = array([ RotY(self.HalfCross, dirCS) for dirCS in dirsCS ] )

        return dirsEU, vecsCS
            