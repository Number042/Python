import numpy as np
from BeamGen import Beam

# input all global parameters for the beam here at initialization (as a dict)? 
class Scatter():

    def __init__(self, beamfile, tfs, Npart, HalfCross, pc, elm):
        self.beamfile = beamfile
        self.tfs = tfs
        self.Npart = np.int(Npart)
        self.HalfCross = np.float32(HalfCross)
        self.pc = pc
        self.elm = elm

    def genBeam(self, home):
        b1 = Beam(home + '/Codes/Projects/FCC-ee-lattice/MadX/output/fcc_ee_b1.dat', home + '/Codes/Projects/FCC-ee-lattice/MadX/output/fcc_ee_b1_twiss.tfs', self.Npart, self.HalfCross, self.pc)
        b1.set_gauss()
        p_e = b1.gen_BeamMom( self.elm ); 

        # generate beam energy based on normal distribution (2% acceptance), calculate lorentz gamma and beta
        self.Ebeam = b1.gen_BeamEnergy(self.pc, 0.02*self.pc)
        self.Gamm = self.Ebeam/m0
        self.Bet = np.sqrt(1 - 1/self.Gamm**2)

        # calculate momentum (energy - restmass)
        self.Pbeam = np.sqrt( Ebeam**2 - m0**2 )

        # build incoming electron four-momentum
        self.qe_in = np.array( [ np.array([enrg, pbem*vec[0], pbem*vec[1], pbem*vec[2]]) for vec,enrg,pbem in zip(p_e,Ebeam,Pbeam)] )
        qe_in2= [ fourMom2(vec) for vec in qe_in]


