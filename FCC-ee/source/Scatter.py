import uproot
from os.path import isfile, isdir
import matplotlib.pyplot as plt
from pandas import DataFrame
from re import findall

matCodes = [2,3,4,5]

class Scattering:
    
    def __init__(self, ntuples = [], plotpath = '/tmp/', verbose = 0):
        """
        Class to study G4 output tuple; dedicated to SR photons
            -- ntuple:  list of data files (path to the files)
            -- verbose: output level, if > 2, print list of elements in the tuples
        """
        
        self.ntuples = ntuples
        if len( self.ntuples ) == 0: raise RuntimeError( "*** list of datafiles is empty!" )
        
        for ntuple in self.ntuples:
            if isfile( ntuple ): pass
            else: raise FileNotFoundError("Ntuple", ntuple, "doesn't exist!")

        if isdir( plotpath ): pass
        else: raise FileNotFoundError("plotpath", plotpath, "doesn't exist!")
        self.verbose = verbose
        self.plotpath = plotpath

    # currently as private. Could also be made publicly available to create selected DFs
    def __readData( self, ntuple, columns = [], COL = ['open','open'], optics = 'fcc_ee' ):
        """
        Provide ntuple as DataFrame
            -- columns:     specify required data
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """

        thefile = uproot.open( ntuple )
        df = thefile['seco_ntuple;1'].pandas.df( columns )
        
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

    def scatterGlobal( self, nBin = 100, xlim = [], Type = 'location', legCol = 4, save = 0 ):

        """
        Display general data of scattering events along the track.
            -- Type: which data to display, location, energy
        """
        
        # ProcNames coded: compton 3, Rayleigh 4
        #
        procs = [3,4]

        columns = ['Name', 'Egamma', 'z_eu', 'Process', 'Material', 'Creator']
        
        for ntuple in self.ntuples:

            df = self.__readData( ntuple, columns )
            self.__getBeamAperInfo( ntuple )
            df['Name'] = [ name.decode("utf-8") for name in df.Name ]

            condition = (df.Process.isin(procs)) & (df.Material.shift(1) == 1) & (df.Material.shift(-2) == 1) & (df.Name.shift(-2).str.contains("_v"))
            selection = df[ condition ]
        
        plt.figure( figsize = (12,10) )
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()
        ax = plt.subplot(111)

        if Type == 'location':
            if xlim: selection = selection[ (selection.z_eu > xlim[0]) & (selection.z_eu < xlim[1]) ]
            ax.hist( selection.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(self.__beamType), stacked = False)
            title = 'event position'
            name = 'scttrLct.pdf'
            horLab = 'Z [m]'; verLab = '$\\gamma$/bin'
            print( selection.z_eu.count(), 'scattered tracks have been identified.' )

        if Type == 'energy':
            ax.hist( selection.Egamma*1e6, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, label = str(self.__beamType), stacked = False)
            title = 'energy - scattered events'
            name = 'scttrEgam.pdf'
            horLab = 'E$_\\gamma$ [keV]'; verLab = '$\\gamma$/bin'
            plt.yscale('log')
            print( selection.z_eu.count(), 'scattered tracks have been identified with <E> =', selection.Egamma.mean()*1e6 )
        
        plt.xlabel( horLab ); plt.ylabel( verLab )
        plt.title( title )
        plt.legend()
        ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.15), ncol = legCol)

        if save: plt.savefig( self.plotpath + name, dpi = 75 )

        del df