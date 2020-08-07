import uproot
from os.path import isfile, isdir
import matplotlib.pyplot as plt
import VisualSpecs
from re import findall

class Processes:
    """
    Class to do the analysis regarding photon interaction with matter. This is meant to investigate what
    happens with the synchrotron radiation that impacts on the beam pipe wall. 
    """
    
    def __init__(self, background = 'photons', ntuples = [], plotpath = '/tmp/', verbose = 0, save = 0):
        """
        Class to study G4 output tuple; dedicated to SR photons
            -- ntuple:  list of data files (path to the files)
            -- verbose: output level, if > 2, print list of elements in the tuples
        """
        
        self.background = background
        self.ntuples = ntuples
        if len( self.ntuples ) == 0: raise RuntimeError( "*** list of datafiles is empty!" )
        
        for ntuple in self.ntuples:
            if isfile( ntuple ): pass
            else: raise FileNotFoundError("Ntuple", ntuple, "doesn't exist!")

        if isdir( plotpath ): pass
        else: raise FileNotFoundError("plotpath", plotpath, "doesn't exist!")
        
        self.plotpath = plotpath
        self.verbose = verbose
        self.save = save

    # currently as private. Could also be made publicly available to create selected DFs
    def __readData( self, ntuple, columns, COL = ['open','open'], optics = 'fcc_ee' ):
        """
        Provide ntuple as DataFrame
            -- columns:     specify required data
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """

        thefile = uproot.open( ntuple )
        if self.background == 'photons': df = thefile['seco_ntuple;1'].pandas.df( columns )
        elif self.background == 'charged': df = thefile['charged_ntuple;1'].pandas.df( columns )
        else: raise ValueError("background", self.background, "is invalid.")
        
        COLH,COLV = COL
        if COL != ['open','open']: print('Collimators not fully opened: \n COLH =', COLH, '\n COLV =', COLV )
        else: print('collimators fully open.')

        return df

    def __fillOrigVol( self, df ):

        if 'OrigVol' not in df:
            raise Warning("*** No column OrigVol found in the data set!")
        else: 
            if self.verbose: print( 'forward filling OrigVol, replacing string \"none\" ...' )
            df['OrigVol'] = df['OrigVol'].replace( b'none' ).ffill()
        
        return df

    def __getBeamAperInfo( self, ntuple ):

        # input to check for beam characteristics and aperture information
        # works simply on filenames alone
        #
        #     pattern = 'pencil\d{1}|gauss\d{2}|gauss\d{1}|ring\d{2}|ring\d{1}|flat\d{2}|flat\d{1}'
        types = 'pencil|gauss|ring|flat'
        sizes = r'\d{2}|\d{1}'
        apers = r'\D(\d{4})\D'

        self.__beamType = str(findall( types, ntuple )[0] )
        self.__beamSize = int(findall( sizes, ntuple )[0] )
        self.__aper = findall( apers, ntuple )

        print('setting beamType to', self.__beamType, '\n setting aperture to', self.__aper, '\n found size', self.__beamSize )
        print("data types: beamType =", type(self.__beamType), 'aperture =', type(self.__aper), "size =", type(self.__beamSize) ) 

    def showerDistr( self, process = 'all', figSize = [15,10], xlim = [] ):
        
        """
        Method to plot a distribution of all processes taking place along the G4 tracklength
            -- process: selection of single processes possible
        """

        graph = plt.figure( figsize = (figSize[0], figSize[1]) )
        plt.title('EM showers - photon interaction with matter')
        plt.xlabel('z [m]'); plt.ylabel('entries/bin')

        if self.background == 'photons': columns = ['x_eu', 'y_eu', 'z_eu', 'Egamma', 'Process', 'Material', 'Creator']
        elif self.background == 'charged': columns = ['x_eu', 'y_eu', 'z_eu', 'Ptot', 'Mass', 'Charge', 'Process', 'Material', 'Creator']

        for ntuple in self.ntuples:

            df = self.__readData( ntuple, columns )
    
            crtrs = df[ (df.Process == 0) ].groupby(['Creator'])
        
            for crtr, subframe in crtrs:
                if crtr == 0: proc = 'undef'
                elif crtr == 1: proc = 'SynRad'
                elif crtr == 2: proc = 'phot'
                elif crtr == 3: proc = 'compt'
                elif crtr == 4: proc = 'Rayl'
                elif crtr == 5: proc = 'annihil'

                if xlim: subframe = subframe[ ( subframe.z_eu > xlim[0] ) & ( subframe.z_eu < xlim[1] ) ]
                plt.hist( subframe.z_eu, bins = 200, stacked = False, histtype = 'step', lw = 2.5, fill = False, label = proc )
            
            del df

        plt.legend(); plt.grid()
        pltname = "particlesEMShower_hitDistr_" + self.background + ".pdf" 
        
        if self.save: 
            print ("Saving figure as ", self.plotpath, pltname)
            plt.savefig( self.plotpath + pltname, bbox_inches = 'tight', dpi = 50)

        # return graph

    def showerEnerg( self, process = 'all', figsize = [15,10], Elim = [] ):

        plt.figure( figsize = ( figsize[0], figsize[1]) )
        plt.yscale('log'); plt.grid()
        plt.title('EM showers - energy distribution')
        plt.xlabel('E [keV]'); plt.ylabel('entries/bin')

        if self.background == 'photons': columns = ['x_eu', 'y_eu', 'z_eu', 'Egamma', 'Process', 'Material', 'Creator']
        elif self.background == 'charged': columns = ['x_eu', 'y_eu', 'z_eu', 'Ptot', 'Mass', 'Charge', 'Process', 'Material', 'Creator']

        for ntuple in self.ntuples:

            df = self.__readData( ntuple, columns )

            crtrs = df[ (df.Process == 0) ].groupby(['Creator'])

            for crtr, subframe in crtrs:

                if crtr == 0: proc = 'undef'
                elif crtr == 1: proc = 'SynRad'
                elif crtr == 2: proc = 'phot'
                elif crtr == 3: proc = 'compt'
                elif crtr == 4: proc = 'Rayl'
                elif crtr == 5: proc = 'annihil'

                if Elim:
                    if self.background == 'charged': subframe = subframe[ ( subframe.Ptot*1e6 > Elim[0] ) & ( subframe.Ptot*1e6 < Elim[1] ) ]
                    else: subframe = subframe[ ( subframe.Egamma*1e6 > Elim[0] ) & ( subframe.Egamma*1e6 < Elim[1]) ]

                if self.background == 'photons': enrg = subframe.Egamma*1e6                
                elif self.background == 'charged': enrg = subframe.Ptot*1e6

                plt.hist( enrg, bins = 200, stacked = False, histtype = 'step', lw = 2.5, fill = False, label = proc )

            del df
        
        # if xlim: plt.xlim( xlim[0], xlim[1] )
        plt.legend() 
        pltname = "particlesEMShowerEnrg_" + self.background + ".pdf"
        
        if self.save:  
            print ("Saving figure as ", self.plotpath, pltname )
            plt.savefig( self.plotpath + pltname, bbox_inches = 'tight', dpi = 50)
        
        if self.verbose: print('heaviest particle mass:', df.Mass.max())



    
