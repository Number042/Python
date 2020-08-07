import uproot
import warnings 
from os.path import isfile, isdir
import matplotlib.pyplot as plt
from pandas import DataFrame
from re import findall
from VisualSpecs import myColors as colors

matCodes = [2,3,4,5]

# ProcNames coded: compton 3, Rayleigh 4
#
procs = [3,4]

class Scattering:
    
    def __init__(self, ntuples = [], plotpath = '/tmp/', verbose = 0):
        """
        Class to study G4 output tuple; dedicated to SR photons
            -- ntuple:  list of data files (path to the files)
            -- verbose: output level, if > 2, print list of elements in the tuples
        """
        
        self.ntuples = ntuples
        if len( self.ntuples ) == 0: warnings.warn('No ntuples provided.', UserWarning) 
        
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
        if df.empty: raise ValueError('Empty Dataframe!')

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
        types = 'pencil|Gaussian|Ring|Flat|Tails'
        sizes = r'\d{2}|\d{1}'
        apers = r'\D(\d{4})\D|\D(\d{6})\D'

        name = str(ntuple).split(sep = '_', maxsplit = 1)[1]
        if self.verbose > 1: print( 'reading beam, size and aperture from', name )

        self.__beamType = str( findall( types, name )[0] )
        self.__beamSize = int( findall( sizes, name )[1] )
        if 'coll' in name: self.__aper = str( findall( apers, name )[0] )
        else: self.__aper = ''

        if self.verbose:
            print('setting beamType to', self.__beamType, '\n setting aperture to', self.__aper, '\n found size', self.__beamSize )
            if self.verbose > 1: 
                print("data types: beamType =", type(self.__beamType), 'aperture =', type(self.__aper), "size =", type(self.__beamSize) ) 

    def scatterGlobal( self, df = None, nBin = 100, xlim = [], Type = 'location', legCol = 4, save = 0, plotpath = '/tmp/' ):

        """
        Display general data of scattering events along the track.
            -- Type: which data to display, location, energy
        """
        
        columns = ['Name', 'Egamma', 'z_eu', 'Process', 'Material', 'Creator']
        
        # Might need to accept external data frame
        #
        if df is not None: 

            self.__beamType = 'none'
            if 'Name' not in df: raise IndexError("DF seems to not contain column 'Name'!")
            # df['Name'] = [ name.decode("utf-8") for name in df.Name ]
            selection = df
            print('Received external DF \n', selection.head())
            
        else:
            
            for ntuple in self.ntuples:

                self.__getBeamAperInfo( ntuple )
                
                df = self.__readData( ntuple, columns )
                self.__getBeamAperInfo( ntuple )
                df['Name'] = [ name.decode("utf-8") for name in df.Name ]

                if xlim: df = df[ (df.z_eu > xlim[0]) & (df.z_eu < xlim[1]) ]

                # shift(1) to access previous row; shift(-2) to access second to next 
                comptCond = (df.Process == 3) & (df.Material.shift(1) == 1) & (df.Material.shift(-2) == 1) & (df.Name.shift(-2).str.contains("_v"))
                RaylCond = (df.Process == 4) & (df.Material.shift(1) == 1) & (df.Material.shift(-2) == 1) & (df.Name.shift(-2).str.contains("_v"))
                compt = df[ comptCond ]
                rayl = df[ RaylCond ]
        
        plt.figure( figsize = (16 ,9) )
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()
        ax = plt.subplot(111)
        
        if Type == 'location':
            
            ax.hist( compt.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, color = colors[3], label = 'compton', stacked = False)
            ax.hist( rayl.z_eu, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, color = colors[4], label = 'rayleigh', stacked = False )
            title = 'scattering events - ' + str(self.__beamType)
            name = 'scttrLct.pdf'
            horLab = 'Z [m]'; verLab = '$\\gamma$/bin'
            print( compt.z_eu.count(), 'compton scattered tracks have been identified. \n', rayl.z_eu.count(), 'rayleigh scattered tracks have been identified' )

        if Type == 'energy':
            
            ax.hist( compt.Egamma*1e6, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, color = colors[3], label = 'compton', stacked = False)
            ax.hist( rayl.Egamma*1e6, bins = nBin, histtype = 'step', fill = False, linewidth = 2.5, color = colors[4], label = 'rayleigh', stacked = False)
            title = 'energy - scattered events - ' + str(self.__beamType)
            name = 'scttrEgam.pdf'
            horLab = 'E$_\\gamma$ [keV]'; verLab = '$\\gamma$/bin'
            plt.yscale('log')
            print( compt.z_eu.count(), 'compton scattered tracks have been identified with <E> =', compt.Egamma.mean()*1e6, 'keV \n',
                    rayl.z_eu.count(), 'rayleigh scattered tracks have been identified with <E> =', rayl.Egamma.mean()*1e6, 'keV' )

            # 100 keV marker
            plt.axvline(x = 100, lw = 2.5, ls = '--', color = 'red')
    
        plt.xlabel( horLab ); plt.ylabel( verLab )
        plt.title( title )
        plt.legend()
        ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.15), ncol = legCol)

        if save: plt.savefig( plotpath + name, bbox_inches = 'tight', dpi = 50 )

        del df

    def scatterMask( self ):

        columns = ['Name', 'Egamma', 'z_eu', 'Process', 'Material', 'Creator']

        for ntuple in self.ntuples:

                self.__getBeamAperInfo( ntuple )
                
                df = self.__readData( ntuple, columns )
                self.__getBeamAperInfo( ntuple )
                df['Name'] = [ name.decode("utf-8") for name in df.Name ]

                df = df[ (df.z_eu > -10) & (df.z_eu < 10) ]

                # shift(1) to access previous row; shift(-2) to access second to next 
                condition = (df.Process.isin(procs)) & (df.Material.shift(1) == 1) & (df.Material.shift(-2) == 1) & (df.Name.shift(-2).str.contains("_v"))
                selection = df[condition]

                mskQC2L = selection[ ((selection.Name == 'MASKQC2L1_2') | (selection.Name == 'DRIFT_8619')) ]; mskQC2L.name = 'MSK.QC2L'
                mskQC1L = selection[ (selection.Name.str.contains("_SRmask")) ]; mskQC1L.name = 'MSK.QC1L'
                
                print(mskQC2L.Egamma.count(), 'hits on MSK.QC2L with <E> =',  mskQC2L.Egamma.mean()*1e6, 'keV' )
                print(mskQC1L.Egamma.count(), 'hits on MSK.QC1L with <E> =',  mskQC1L.Egamma.mean()*1e6, 'keV' )

        del df