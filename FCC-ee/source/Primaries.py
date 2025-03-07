import matplotlib.pyplot as plt
from os.path import isdir, isfile
from re import findall
import uproot

class Bunch:

    def __init__(self, ntuples, emit = [], plotpath = '/tmp/', verbose = 0):
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
        
        self.emit = emit
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

        if 'Name' in columns: df['Name'] = [ name.decode("utf-8") for name in df.Name ]
        if 'OrigVol' in columns: df['OrigVol'] = [ origvol.decode("utf-8") for origvol in df.OrigVol ]
        
        # if COL != ['3.5','3.5']: print('Collimators not fully opened: \n COLH =', COLH, '\n COLV =', COLV )
        # else: print('collimators fully open.')

        return df

    def __getBeamAperInfo( self, ntuple ):

        import warnings
        from os import environ

        # input to check for beam characteristics and aperture information; works simply on filenames alone
        #
        types = 'pencil|Gaussian|Ring|Flat|Tails'
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

    def __beamSizeElm( self, twiss, nameFrmDF ):
        
        from numpy import sqrt

        nameSplt = nameFrmDF.split('_')
        if 'DRIFT' in nameSplt: nameInTwiss = '_'.join( nameSplt[:-1] )
        else: nameInTwiss = '.'.join( nameSplt[:-1] )
        
        twiss = twiss[ ['NAME','S', 'BETX','BETY'] ]
        twiss = twiss[ twiss.NAME == nameInTwiss ]
        print('Using name', nameInTwiss, ':\n', twiss)
        bmSz = sqrt( self.emit[0]*twiss.iloc[0]['BETX'] ) 
        
        return bmSz

    def initBeamDistr( self, plane = 'x', logscale = 0, save = 0):
        
        from VisualSpecs import myColors as colors
        from numpy import histogram, hstack
        columns = ['x_eu', 'y_eu', 'z_eu', 'trackLen']
        
        plt.figure(figsize = (16, 9))
        ax = plt.subplot(111)
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()

        distr = []; labels = []
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
                data = [dat*1e3 for dat in data]
                title = 'initial beam vertical plane'; xlabel = 'y [mm]'
            
            else: raise KeyError('Selected plane', plane, 'invalid')
            
            distr.append( data )
            labels.append( str(df.name) + '_' + str(self.__beamSize) + '$\\sigma$' )
            print('plane is', plane, 'title is', title)
            
            if logscale: ax.set_yscale('log')

            ax.set_title( title ); ax.set_xlabel( xlabel ); ax.set_ylabel( 'particles/bin' )
            
        # determine equal bin spacing
        #
        bins = histogram( hstack( (distr) ), bins = 100)[1]
        
        i = 0
        for datSet, tag in zip(distr, labels):
            ax.hist( datSet, bins = bins, color = colors[i], label = tag, histtype = 'step', lw = 2.5)
            i += 1

        ax.legend() 
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

    def BeamDistrElmt( self, twiss, names = [], plane = 'x', nbin = 100, save = 0 ):
        """
        Method to plot beam distributions a different elements
        """

        from VisualSpecs import myColors as colors
        from Tools import sbplSetUp

        columns = ['Name', 'x_eu', 'y_eu', 'z_eu', 'trackLen', 'Type', 'Process']
        nmElmt = int(len(names))

        for ntuple in self.ntuples:
            
            self.__getBeamAperInfo( ntuple )
            df = self.__readData( ntuple, columns )
            df = df[ df.Type == 1 ]

            if self.verbose > 1: print( 'beam passes following elements', df.Name.unique() )
            # axs = sbplSetUp( count = nmElmt, dim = [16, 9] )
            figSize = (30, 8)

            if nmElmt == 3: fig,axes = plt.subplots(1, nmElmt, sharex = False, sharey = True, figsize = figSize )
            elif nmElmt == 4: fig,axes = plt.subplots(2, 2, sharex = 'column', sharey = 'row', figsize = figSize )
            else: fig,axes = plt.subplots( 3, 3, sharex = 'column', sharey = 'row', figsize = figSize )
            
            i = 0
            
            for name in names:
        
                print( 'looking at beam distribution in', name )
                
                selection = df[ (df.Name == name) ]
                

                if plane == 'x': 
                    
                    if name == 'BWL_2_v': selection = selection[ selection.trackLen > 199 ]
                    if self.verbose: print('Number of entries =', len(selection.index) )
                    # sigm = self.__beamSizeElm( twiss, name )
                    # bmRange = [ selection.x_eu.mean() - 5*sigm, selection.x_eu.mean() + 5*sigm ]
                    # selection = selection[ (selection.x_eu > bmRange[0]) & (selection.x_eu < bmRange[1])  ]

                    # if self.verbose:
                    #     print('Using range =', bmRange, '\n number of entries in range \n', len(selection.index) )
                    
                    data = selection.x_eu*1e3
                    xlabel = 'x [mm]'
                
                elif plane == 'y': 

                    if self.verbose: print('Number of entries =', len(selection.index) )
                    data = selection.y_eu*1e3
                    xlabel = 'y [mm]'

                else: raise KeyError('Selected plane', plane, 'invalid')
                axes[i].hist( data, bins = nbin, lw = 2.5, histtype = 'step', color = colors[i] )
                axes[i].set_xlabel( xlabel )
                axes[i].set_title( name.split('_')[0] )

                i += 1
                del selection

            plt.set_ylabel = ('primaries/bin')            
            plttitle = 'parDistrElm_' + str(self.__beamType) + '_' + str(plane) + '.pdf'
            plt.tight_layout()
            if save:
                print('Saving figure as', self.plotpath + plttitle, ' ... ' )
                plt.savefig( self.plotpath + plttitle, bbox_inches = 'tight', dpi = 75 )

        return 0


        
