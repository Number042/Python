import numpy as np
import random as rnd
from matplotlib import pyplot as plt
from CS_to_EU import FromNorm, RotY
from TfsTables import TfsReader
from Tools import sbplSetUp
class Beam:
    
    def __init__(self, beamFile, tfs, name, Npart, halfCross, pc, verbose = 0):
        
        self.beamFile = beamFile
        self.tfs = tfs
        self.name = name
        self.Npart = Npart = int(Npart)
        self.verbose = verbose
        self.HalfCross = halfCross
        self.pc = pc
        
        self.BeamVecX = []; self.BeamVecY = []
        self.BeamVecXprim = []; self.BeamVecYprim = []

        self.Eb = np.sqrt(pc**2 - (511e-6)**2)

        if verbose: print("Created:", name, "\n    * Using file ", beamFile, "\n    * Number of particles:", Npart, '\n at energy Eb =', self.Eb)
        
    def read_beam_size(self, dim):
        """
        Method to read in the beam gun information from the Fields_from_tfs output
            -- beamFile: .dat file to read information from
        RETURNS: array with sig_xn, sig_xn', sig_yn, sig_yn', sig_z, sig_e
        """
        
        beamFile = self.beamFile
        beamsize = np.genfromtxt(beamFile, delimiter = None, skip_header = 2, max_rows = 1 )
        
        if self.verbose: print("Beam sizes:", beamsize)
        
        if dim == 'x': 
            if self.verbose: print("selected plane: ", dim, "sigma = ", beamsize[0] )
            sqrtEmitX = beamsize[0]
            return sqrtEmitX
        
        elif dim == 'y': 
            if self.verbose: print("selected plane: ", dim, "sigma = ", beamsize[2] )
            sqrtEmitY = beamsize[2]
            return sqrtEmitY
        
        

    def set_gauss(self, plotPath, plot = 0, save = 0):
        """
        Method to plot a random Gaussian distribution in x,x' and y,y'.
        Normalization with the emittance epsx
            -- plotPath: directory to store the plots
            -- plot: switch plotting the distribution on or off
            -- save: choose whether or not the plots are dumped as pdf
        """
        if self.verbose: print ("generate Gaussian beam for:", self.name, " with ", self.Npart, " particles.")
        
        # read beam sizes from Fields_from_tfs output. Given is already the std deviation with sqrt(eps)
        #
        beamsizeX = self.read_beam_size('x'); 
        beamsizeY = self.read_beam_size('y')   
                        
        i = 0
        while i < self.Npart:
            
            # x plane
            self.BeamVecX.append( rnd.gauss( 0, beamsizeX) )
            self.BeamVecXprim.append( rnd.gauss( 0, beamsizeX) )
            
            # y plane
            self.BeamVecY.append( rnd.gauss( 0, beamsizeY) )
            self.BeamVecYprim.append( rnd.gauss( 0, beamsizeY) )
                                
            i += 1
            
        
        if self.verbose > 1: print ("BeamVecX =", self.BeamVecX, '\n', "BeamVecY =", self.BeamVecY)
        
        if plot:
            plt.figure( figsize = (15, 10) )
            plt.plot(self.BeamVecX, self.BeamVecXprim, '.', label = 'x')
            plt.plot(self.BeamVecY, self.BeamVecYprim, '.', label = 'y')
            plt.title("Gaussian Beam")
            plt.xlabel("x,y"); plt.ylabel("x',y'"); plt.legend()
            
            if save:
                plt.savefig( plotPath + 'GaussianShape_' + str(self.Npart) + '.pdf', dpi = 100 ) 
            
        # better to return v_n_CS directly?
        return self.BeamVecX, self.BeamVecXprim, self.BeamVecY, self.BeamVecYprim
    
    def set_ring(self, plotPath, Nsig = [2,2], plot = 0, save = 0):
        """    
        Method to create flat random distribution in x,x'.
        Normalization by +- nsig
            -- amplt: amplitude, Nsig - radius of the ring 
        """
        
        beamsizeX = self.read_beam_size('x'); 
        beamsizeY = self.read_beam_size('y')
        
        i = 0
        while i < self.Npart:
            phi = 2*np.pi*i/self.Npart
            
            # horizontal plane
            self.BeamVecX.append( np.abs(Nsig[0])*beamsizeX*np.cos(phi)) 
            self.BeamVecXprim.append( np.abs(Nsig[0])*beamsizeX*np.sin(phi)) 
            
            # vertical plane
            self.BeamVecY.append( np.abs(Nsig[1])*beamsizeY*np.cos(phi)) 
            self.BeamVecYprim.append( np.abs(Nsig[1])*beamsizeY*np.sin(phi)) 

            i += 1
        
        if plot:
            plt.figure(figsize = (10, 10))
            plt.plot(self.BeamVecX, self.BeamVecXprim, '.')
            plt.plot(self.BeamVecY, self.BeamVecYprim, '.')
            plt.title("Fixed Amplitude")
            plt.xlabel('x,y'); plt.ylabel('x\',y\'')
            
            if save:
                plt.savefig(plotPath + 'RingShape_' + str(self.Npart) + '.pdf')
            
        return self.BeamVecX, self.BeamVecXprim, self.BeamVecY, self.BeamVecYprim

    def gen_BeamMom(self, elm):
        """
        Function to generate the three-momentum of beam particles.
            -- elm: element at which the beam is generated (used for trafo normalized --> physical)
        """
        twiss = TfsReader(self.tfs).read_twiss( self.verbose )
        FrmNrm = FromNorm( twiss.loc[twiss['NAME'] == elm]['BETX'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['BETY'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['ALFX'].item(), 
                           twiss.loc[twiss['NAME'] == elm]['ALFY'].item() )
        
        # x = self.BeamVecX; px = self.BeamVecXprim
        # y = self.BeamVecY; py = self.BeamVecYprim
        vecsNCS = []
        
        i = 0
        while i < self.Npart:
            vecsNCS.append(np.array([self.BeamVecX[i], self.BeamVecXprim[i], self.BeamVecY[i], self.BeamVecYprim[i], 0, 0]))
            i += 1
        
        vecsCS = [ FrmNrm @ vec for vec in vecsNCS ]
        dirsCS = [[vec[0], vec[2], np.sqrt(1 - vec[0]**2 - vec[2]**2)] for vec in vecsCS ]
        dirsEU = [ RotY(self.HalfCross, dirCS) for dirCS in dirsCS ]

        # calculate the four momentum based on pc
        #FourMom = [ [self.pc, self.Eb*vec[0], self.Eb*vec[1], self.Eb*vec[2]] for vec in dirsEU]

        return dirsEU
            