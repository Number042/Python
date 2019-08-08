from numpy import int, float32, sqrt, array, random, pi, sin, cos
from Tools import sbplSetUp
from CS_to_EU import getRotVec3, RotToZ, RotFrmZ
from BeamGen import Beam
import matplotlib.pyplot as plt

# input all global parameters for the beam here at initialization (as a dict)? 
class Scatter():

    def __init__(self, beamfile, tfs, Npart, HalfCross, pc, T, verbose = 0 ):
        self.beamfile = beamfile
        self.tfs = tfs
        self.Npart = int(Npart)
        self.HalfCross = HalfCross
        self.pc = pc
        self.T = T
        self.verbose = verbose

        self.m0 = 511e-6 # in [GeV]
        self.labels = ['E', '$p_x$', '$p_y$', '$p_z$']
        self.verbCond = self.verbose and self.Npart < 1e5

    def genBeam( self, elm ):
        b1 = Beam(self.beamfile, self.tfs, self.Npart, self.HalfCross, self.pc)
        b1.set_gauss( )
        p_e = b1.gen_BeamMom( elm )

        # generate beam energy based on normal distribution (2% acceptance), calculate lorentz gamma and beta
        Scatter.Ebeam = b1.gen_BeamEnergy(self.pc, 0.02*self.pc)
        Scatter.Gamm = Scatter.Ebeam/self.m0
        Scatter.Bet = sqrt(1 - 1/Scatter.Gamm**2)

        # calculate momentum (energy - restmass)
        Pbeam = sqrt( self.Ebeam**2 - self.m0**2 )

        # build incoming electron four-momentum
        # 
        Scatter.qe_in = array( [ array([enrg, pbem*vec[0], pbem*vec[1], pbem*vec[2]]) for vec,enrg,pbem in zip(p_e, self.Ebeam, Pbeam)] )
        # qe_in2= [ fourMom2(vec) for vec in qe_in]
        
        # some visualization of the inital four momentum
        #
        if self.verbCond:

            axs = sbplSetUp(4)
            for j in range(0,4):
                axs[j].hist([mom[j] for mom in Scatter.qe_in], bins = 100)
                axs[j].set_xlabel(self.labels[j])
            plt.tight_layout()


        # rotate the beam exactly to z direction (in most cases rather minor correction)
        #
        Scatter.angles_qe = array( [getRotVec3(vec) for vec in p_e] )

        Scatter.qe_in_z = array([RotToZ(ang[0], ang[1]) @ vec for vec,ang in zip(Scatter.qe_in, Scatter.angles_qe)])

        if self.verbCond:
            print( len(p_e), '\n', p_e, '\n', Scatter.qe_in, '\n', Scatter.angles_qe, '\n', Scatter.qe_in_z )
            axs = sbplSetUp(4)
            for j in range(0,4):
                axs[j].hist([mom[j] for mom in Scatter.qe_in_z], bins = 100)
                axs[j].set_xlabel(self.labels[j])
            plt.tight_layout()

    def genPhot(self):
        """
        Generate initial photon energy spectrum (in GeV) and spatial momentum distribution. 
        Also rotates the photon momenta in z direction (same amount as for the inital beam).
        """
        from Generators import genPlanck
        k = 8.617e-5 # given in [eV/K]

        values = genPlanck(self.Npart)
        Scatter.Ei = k*self.T*values/1e9
        
        
        if self.verbCond:
            print(len(Scatter.Ei), Scatter.Ei)
            plt.figure( figsize = (15,10) )
            plt.hist( Scatter.Ei, bins = 200 )
            plt.xlabel('$E_\\gamma$ [GeV]'); plt.ylabel('photons/bin')
        
        # generate cosPsi, sinPsi and phi
        #
        CosPsi = array( [random.uniform(-1,1) for i in range(self.Npart)] )
        SinPsi = array( [sqrt(1 - cos**2) for cos in CosPsi] )
        Phi = array( [random.uniform(0,2*pi) for i in range(self.Npart)] )

        # construct incoming photon four momentum and roate by same amount as qp_e_in
        Scatter.qk_in = array([array([val, val*cos(phi)*sinPsi, val*sinPsi*sin(phi), val*cosPsi ]) for val, sinPsi, cosPsi, phi in zip(self.Ei, SinPsi, CosPsi, Phi)])
        Scatter.qk_in_z = array([ RotToZ(ang[0], ang[1]) @ qk for qk,ang in zip( Scatter.qk_in, Scatter.angles_qe )])
        # qk2 = [ fourMom2(qkz) for qkz in qk_in_z ]


        # some visualization
        #
        if self.verbCond:
            print(len(Scatter.qk_in), len(Scatter.qk_in_z))  
            axs = sbplSetUp(4)
            for j in range(4):
                axs[j].hist( [vec[j] for vec in Scatter.qk_in], bins = 100 )
            axs1 = sbplSetUp(4)
            for j in range(4):
                axs1[j].hist( [vec[j] for vec in Scatter.qk_in_z], bins = 100)


            # plt.figure(); plt.plot( qk2 ); plt.xlabel('#'); plt.ylabel('$q_k^2$');


    def toREST(self):
        from RelKin import Boost

        # boost into e-rest frame along z axis
        #
        Scatter.qkstar = array( [Boost( gam, bet) @ qk for gam,bet,qk in zip(Scatter.Gamm, Scatter.Bet, Scatter.qk_in_z) ] )
        pk_star = array( [array([vec[1], vec[2], vec[3]]) for vec in Scatter.qkstar] )
        Scatter.qestar = array( [Boost( gam, bet) @ qe for gam, bet, qe in zip(Scatter.Gamm, Scatter.Bet, Scatter.qe_in_z) ] )

        # qkst2 = [ fourMom2(qkst) for qkst in qkstar ]
        # qest2 = [ fourMom2(qest) for qest in qestar ]

        Scatter.angles_from_z = [getRotVec3(pk) for pk in pk_star]

        # some visualization
        #
        if self.verbCond:
            axs = sbplSetUp(4, [10, 15])
            for j in range(0,4):
                axs[j].hist( [vec[j] for vec in Scatter.qkstar], bins = 100 ); 
                axs[j].set_xlabel(self.labels[j])

            axs1 = sbplSetUp(4, [10, 15])
            for j in range(0,4):
                axs1[j].hist( [vec[j] for vec in Scatter.qestar], bins = 100 )
            # plt.tight_layout()
            # print(len(qkstar))


    def compt(self):

        from Generators import genCompt, kratio

        cost = [ genCompt( qkst[0], self.m0 ) for qkst in Scatter.qkstar ]
        sint = [ sqrt(1 - cos**2) for cos in cost]
        phi = [ random.uniform(0,2*pi) for i in range(self.Npart)]

        # photon energy after scattering
        #
        # krat = array( [kratio(self.m0, qkst[0], costhet) for qkst, costhet in zip(Scatter.qkstar, cost)] )
        kstar = [ qkst[0]*kratio(self.m0, qkst[0], costhet) for qkst,costhet in zip(Scatter.qkstar,cost) ]

        # photon four momentum after scattering
        #
        Scatter.qkstar_sct_z = array( [ array([kst, kst*sinthet*cos(Phi), kst*sinthet*sin(Phi), kst*costhet]) for kst,sinthet,costhet,Phi in zip(kstar, sint, cost, phi)] )
        # qkstsct2 = [ fourMom2(qkstsct) for qkstsct in qkstar_sct_z ]

        if self.verbCond:

            axs = sbplSetUp(4)
            axs[0].hist( kstar, bins = 200); axs[0].set_xlabel('$E$')
            axs[2].hist( cost, bins = 200); axs[2].set_xlabel('$cos\\theta$')
            # axs[3].hist( krat, bins = 200 ); axs[3].set_xlabel('k\'/k')

            axs1 = sbplSetUp(4)
            for j in range(4):
                axs1[j].hist( [qkst[j] for qkst in Scatter.qkstar_sct_z], bins = 200)
                axs1[j].set_xlabel(self.labels[j])

            plt.tight_layout()


    def toLAB(self):
        from RelKin import Boost
        
        # First, rotate back from z
        #
        qkstar_sct = array( [RotFrmZ( ang[0], ang[1] ) @ qkstz for ang,qkstz in zip(Scatter.angles_from_z, Scatter.qkstar_sct_z)] )

        # then, boost back to LAB
        #
        qk_out_z = array( array([ Boost( gam, bet ) @ qksctz for gam,bet,qksctz in zip(Scatter.Gamm, Scatter.Bet, qkstar_sct)]) )
        # qk_out_z2 = array( [ fourMom2(qkoutz) for qkoutz in qk_out_z ] )


        # return only the final energy 'qe_out_z '
        qe_out_z = Scatter.qe_in + Scatter.qk_in - qk_out_z 
        return qe_out_z, qk_out_z



 




