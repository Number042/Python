import matplotlib.pyplot as plt
from os.path import isdir, isfile
from re import findall
import uproot

class Bunch:

    def __init__(self, ntuples, plotpath = '/tmp/', verbose = 0):
        """
        Class to study G4 output tuple; dedicated to primaries
            -- ntuples:  list of data files (path to the files)
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
    def __readData( self, ntuple, columns = [], optics = 'fcc_ee' ):
        """
        Provide ntuple as DataFrame
            -- columns:     specify required data
            -- optics:      optional key to distinguish different machine versions
        """

        thefile = uproot.open( ntuple )
        df = thefile[b'prim_nutple;1'].pandas.df( columns )        

        if 'Names' in columns: df['Name'] = [ name.decode("utf-8") for name in df.Name ]
        if 'OrigVol' in columns: df['OrigVol'] = [ origvol.decode("utf-8") for origvol in df.OrigVol ]
        
        # if COL != ['3.5','3.5']: print('Collimators not fully opened: \n COLH =', COLH, '\n COLV =', COLV )
        # else: print('collimators fully open.')

        return df

    def __getBeamAperInfo( self, ntuple ):

        import warnings
        from os import environ

        # input to check for beam characteristics and aperture information; works simply on filenames alone
        #
        types = 'pencil|gauss|ring|flat'
        sizes = r'\d{2}|\d{1}'
        apers = r'\D(\d{4})\D|\D(\d{6})\D'

        name = str(ntuple).split(sep = '_', maxsplit = 1)[1]
        if self.verbose > 1: print( 'reading beam, size and aperture from', name )

        self.__beamType = str( findall( types, name )[0] )
        self.__beamSize = int( findall( sizes, name )[1] )
        
        if 'coll' in name: self.__aper = str( findall( apers, name )[0] )
        else: self.__aper = str(3.5)

        if self.verbose:
            print('setting beamType to', self.__beamType, '\n setting aperture to', self.__aper, 'cm \n found size', self.__beamSize )
            if self.verbose > 1: 
                print("data types: beamType =", type(self.__beamType), 'aperture =', type(self.__aper), "size =", type(self.__beamSize) ) 

    def initBeamDistr( self, plane = 'x', logscale = 0, save = 0):
        
        from VisualSpecs import myColors as colors

        columns = ['x_eu', 'y_eu', 'z_eu', 'trackLen']
        
        for ntuple in self.ntuples:
            
            self.__getBeamAperInfo( ntuple )
            df = self.__readData( ntuple, columns )
        
            if self.verbose:
                print('setting beamType to', self.__beamType, '\n setting aperture to', self.__aper, '\n found size', self.__beamSize )
            if self.verbose > 1: 
                print("data types: beamType =", type(self.__beamType), 'aperture =', type(self.__aper), "size =", type(self.__beamSize) ) 

            # select initial step, assign name to df
            #
            df = df[ df.trackLen == 0 ]
            df.name = self.__beamType  
            if self.verbose: print('Number of entries =', len(df.index) )

            if plane == 'x':
                data = df.x_eu.tolist()
                title = 'initial beam horizontal plane'; xlabel = 'x [m]'
        
            elif plane == 'y':
                data = df.y_eu.tolist()
                title = 'initial beam vertical plane'; xlabel = 'y [m]'
            
            else: raise KeyError('Selected plane', plane, 'invalid')
            
            plt.figure(figsize = (16, 9))
            ax = plt.subplot(111)
            plt.rc('grid', linestyle = "--", color = 'grey')
            plt.grid()

            ax.hist( data, bins = 100, color = colors[3], label = str(df.name) + '_' + str(self.__beamSize) + '$\\sigma$', histtype='step', lw = 2.5)
    
            print('plane is', plane, 'title is', title)
            
            ax.legend() 
            if logscale: ax.set_yscale('log')

            ax.set_title( title ); ax.set_xlabel( xlabel ); ax.set_ylabel( 'particles/bin' )
            
            plt.tight_layout()
            pltname = 'initBeam_' + str(df.name) + '_' + str(plane) + '.pdf'
            if save: 
                print( 'save plot as', self.plotpath, pltname, '...' )
                plt.savefig( self.plotpath + pltname, dpi = 75)
    
        return 0
    

    def primTrk():
        """
        Method to analyse and visualize the primary track(s)
        """
        return 0

    def BeamDistrElmt():
        """
        Method to plot beam distributions a different elements
        """
        return 0


        
