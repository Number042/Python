from numpy import sqrt
class Parameters:

    def __init__( self, pc ):
        
        self.pc = pc
        self.Eb = sqrt(pc**2 - (511e-6)**2)

        # print("summarize beam parameters for pc =", self.pc )

    def set_beam_parameters( self ):

        if self.pc == 45.6:
            param = { 'Nbun':16640, 'Np':1.7e11, 'sigZ':3.5e-3, 'sigZ_BS':12.1e-3, 'epsX':.27e-9, 
                       'epsY':1e-12, 'betStX':0.15, 'betStY':0.8e-3, 'sigStX':6.4e-6,
                       'sigStY':28e-9, 'Lrnt':self.pc/511e-6, 'brho':10*self.pc/2.9979, 'Ib':1390, 'tau_BSP':19.6,  'sigmPBS':0.132, 'sigmPSR': 0.038 } 

        elif self.pc == 182.5:
            param = { 'Nbun':48, 'Np':2.3e11, 'sigZ':1.97e-3, 'sigZ_BS':2.54e-3, 'epsX':1.46e-9, 
                      'epsY':2.9e-12, 'betStX':1., 'betStY':1.6e-3, 'sigStX':38.2e-6, 
                      'sigStY':68e-9, 'Lrnt':self.pc/511e-6, 'brho':10*self.pc/2.9979, 'Ib':5.4, 'tau_BSP':3396, 'sigmPBS':0.192, 'sigmPSR':0.150 }

        print("---- Beam Parameters b1 at", self.pc, " GeV ---- \n", " Beam energy =", self.pc, 'with', param['Nbun'], 
              "bunches/beam with population of", param['Np'], 'particles \n', 
              "bunch length (SR) =", param['sigZ'], "m \n",
              "bunch length (BS) =", param['sigZ_BS'], "m \n",
              "energy spread (SR) =", param['sigmPSR'], "%\n"
              "energy spread (BS) =", param['sigmPBS'], '%\n',
            "\n emittance x,y =", param['epsX'], param['epsY'], "m \n",
            "\n Brho =", param['brho'], "\n Lorentz gamma =", param['Lrnt'], 
            "\n ----------------------------- " )

        return param

