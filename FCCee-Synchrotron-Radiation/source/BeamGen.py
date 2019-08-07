from numpy import sqrt, genfromtxt, float32, array, pi, abs, cos, sin
import random as rnd
from matplotlib import pyplot as plt
from CS_to_EU import FromNorm, RotY
from TfsTables import TfsReader
from Tools import sbplSetUp

class Beam:
    
    def __init__(self, beamFile, tfs, Npart, halfCross, pc, verbose = 0):
        
        self.beamFile = beamFile
        self.tfs = tfs
        self.Npart = Npart
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
        
    def set_gauss(self, plot = 0, save = 0):
        """
        Method to plot a random Gaussian distribution in x,x' and y,y'.
        Normalization with the emittance epsx
            -- plotPath: directory to store the plots
            -- plot: switch plotting the distribution on or off
            -- save: choose whether or not the plots are dumped as pdf

        RETURNS: arrays for x,x' and y,y'
        """
        if self.verbose: print ("generate Gaussian beam with ", self.Npart, " particles.")
        
        # read beam sizes from Fields_from_tfs output. Given is already the std deviation with sqrt(eps)
        #
        beamsizeX = self.read_beam_size('x'); 
        beamsizeY = self.read_beam_size('y') 

        # horizontal plane                
        self.BeamVecX = array([ rnd.gauss( 0, beamsizeX ) for i in range(self.Npart) ] )
        self.BeamVecXprim = array([ rnd.gauss( 0, beamsizeX ) for i in range(self.Npart) ] )

        # vertical plane
        self.BeamVecY = array([ rnd.gauss( 0, beamsizeY ) for i in range(self.Npart) ] )
        self.BeamVecYprim = array([ rnd.gauss( 0, beamsizeY ) for i in range(self.Npart) ] )
        
        if self.verbose > 1: print ("BeamVecX =", self.BeamVecX, '\n', "BeamVecY =", self.BeamVecY)
        
        if plot:
            plt.figure( figsize = (15, 10) )
            plt.plot(self.BeamVecX, self.BeamVecXprim, '.', label = 'x')
            plt.plot(self.BeamVecY, self.BeamVecYprim, '.', label = 'y')
            plt.title("Gaussian Beam")
            plt.xlabel("x,y"); plt.ylabel("x',y'"); plt.legend()
            
            # if save:
            #     plt.savefig( plotPath + 'GaussianShape_' + str(self.Npart) + '.pdf', dpi = 100 ) 
            
        # better to return v_n_CS directly?
        return self.BeamVecX, self.BeamVecXprim, self.BeamVecY, self.BeamVecYprim
    
    def set_ring(self, Nsig = [2,2], plot = 0, save = 0):
        """    
        Method to create flat random distribution in x,x'.
        Normalization by +- nsig
            -- amplt: amplitude, Nsig - radius of the ring 

        RETURNS: arrays for x,x' and y,y'
        """
        
        beamsizeX = self.read_beam_size('x'); 
        beamsizeY = self.read_beam_size('y')
        
        Phi = array([2*pi*i/self.Npart for i in range(self.Npart)])
        
        # horizontal plane
        self.BeamVecX = array( [ abs(Nsig[0])*beamsizeX*cos(phi) for i,phi in zip(range(self.Npart), Phi) ] ) 
        self.BeamVecXprim = array( [ abs(Nsig[0])*beamsizeX*sin(phi) for i,phi in zip(range(self.Npart), Phi) ] ) 
        
        # vertical plane
        self.BeamVecY = array( [ abs(Nsig[1])*beamsizeY*cos(phi) for i,phi in zip(range(self.Npart),Phi) ] ) 
        self.BeamVecYprim = array( [ abs(Nsig[1])*beamsizeY*sin(phi) for i,phi in zip(range(self.Npart),Phi) ] ) 
        
        if plot:
            plt.figure(figsize = (10, 10))
            plt.plot(self.BeamVecX, self.BeamVecXprim, '.')
            plt.plot(self.BeamVecY, self.BeamVecYprim, '.')
            plt.title("Fixed Amplitude")
            plt.xlabel('x,y'); plt.ylabel('x\',y\'')
            
            # if save:
            #     plt.savefig(plotPath + 'RingShape_' + str(self.Npart) + '.pdf')
            
        return self.BeamVecX, self.BeamVecXprim, self.BeamVecY, self.BeamVecYprim

    def gen_BeamEnergy(self, Edes, acceptance):
        """
        Function to generate the beam energy according to a Gaussian distribution.
            -- Edes:        design energy
            -- acceptance:  energy acceptance of a machine
        
        RETURNS: array of beam energies of length Npart
        """

        return array([ rnd.gauss(Edes, acceptance) for i in range(self.Npart) ] )

    def gen_BeamMom(self, elm):
        """
        Function to generate the three-momentum of beam particles.
            -- elm: element at which the beam is generated (used for trafo normalized --> physical)

        RETURNS: array of single dir_EU
        """
        twiss = TfsReader(self.tfs).read_twiss( self.verbose )
        FrmNrm = FromNorm( twiss.loc[twiss['NAME'] == elm]['BETX'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['BETY'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['ALFX'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['ALFY'].item() )
        
        vecsNCS = array( [array([self.BeamVecX[i], self.BeamVecXprim[i], self.BeamVecY[i], self.BeamVecYprim[i], 0, 0]) for i in range(self.Npart) ] )
        
        vecsCS = array([ FrmNrm @ vec for vec in vecsNCS ] )
        dirsCS = array([[vec[0], vec[2], sqrt(1 - vec[0]**2 - vec[2]**2)] for vec in vecsCS ] )
        dirsEU = array([ RotY(self.HalfCross, dirCS) for dirCS in dirsCS ] )

        return dirsEU
            