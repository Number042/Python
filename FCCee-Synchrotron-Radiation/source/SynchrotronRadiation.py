import uproot
import matplotlib.pyplot as plt
from time import time
from pandas import DataFrame

class SynchrotronRadiation:
    
    def __init__(self, ntuple, plotpath, verbose = 0):
        """
        Class to study G4 output tuple; dedicated to SR photons
            -- ntuple:  path to the file that holds the data
            -- verbose: output level
        """
        
        self.ntuple = ntuple
        self.verbose = verbose
        self.plotpath = plotpath

    def readData( self, columns = ['Name','Egamma','z_eu','OrigVol','Process','Material','Creator'], beamType = 'pencil', COL = ['open','open'], optics = 'fcc_ee' ):
        """
        Provide ntuple as DataFrame
            -- beamType:    primary transverse distr - pencil, Gauss, etc
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """
        self.Thefile = uproot.open( self.ntuple )
        ## now done 'on demand' when required by specific task
        ##
        # self.df = Thefile['seco_ntuple;1'].pandas.df( columns )
        # self.df = Thefile['seco_ntuple;1'].arrays( outputtype = DataFrame )
        
        self.beamType = str(beamType)
        print('setting beamType to', self.beamType )

        COLH,COLV = COL
        if COL != ['open','open']: print('Collimators not fully opened: \n COLH =', COLH, '\n COLV =', COLV )
        else: print('collimators fully open.')

    def __fillOrigVol( self, df ):

        if 'OrigVol' not in df:
            raise Warning("*** No column OrigVol found in the data set!")
        else: 
            if self.verbose: print( 'forward filling OrigVol, replacing string \"none\" ...' )
            df['OrigVol'] = df['OrigVol'].replace( b'none' ).ffill()
        return df

    def printInfo( self ):

        if self.df is not None:
            # print("Data stored in the Ntuple: \n", self.df.columns )
            print( " ----------------------- \n", self.df.head() )

        else:
            raise RuntimeError("*** no data frame created!")

    def mergeData( self ):
        # in case there are more than 1 frame, merge them ... stuff done in Tracking better move here? mlu -- 2019-14-11
        return 
    
    ## also possible to leave this on its own and use it from Plot.py
    def defaultSRData(self, zlim = [], beam = 'all', size = 'all', Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
        """
        Method to plot data from secondary events, taking into account different beam shapes and sizes. 
            -- plotpath:    point to a directory for storing plots
            -- zlim:		array to put zmin and zmax; allows to plot only certain region; default empty 
            -- beam:        allows to select the beam shape. Available are pencil, gauss, flat and ring
            -- size:        choose beam sizes; gauss,flat and ring have to start with >0; defaults to 'all'
            -- Type:        choose which spectrum to plot - hits, origin or position
            -- nBin:        choose the binnig, defaults to 100
            -- ticks:       set the number of tickss on the xaxis (acts on binning)
            -- verbose:     switch on/off verbose output
            -- legCol:      specify number of columns in the legend box, defaults to 2
            -- save:        select whether or not the plots are dumped to pself.df files
        
        RETURNS: nothing. Simple plottig tool
        """
        from Plot import plot_defaultData
        
        defDF = self.Thefile['seco_ntuple;1'].pandas.df( ['Material', 'z_eu', 'Process'] )
        defDF['BeamShape'] = self.beamType
        if zlim:
            defDF = defDF[ (defDF.z_eu > zlim[0]) & (defDF.z_eu < zlim[1]) ]
        
        plot_defaultData( defDF, self.plotpath, beam, size, Type, nBin, ticks, verbose, legCol, save)        
        
        del defDF
        print("plotting done, deleted DF.")
        
    def energySpectrum(self, Type = 'general', magnets = [], zlim = [], save = 0):
        """
        Method to plot the energy of SR photons
            -- Type:    global spectrum or magnet specific
            -- magnets: choose which magnets to plot
            -- save:    whether or not save a copy of the plot 
        
        RETURN: the figure
        """
        from Plot import plot_Energy
        
        enrgDF = self.Thefile['seco_ntuple;1'].pandas.df( ['Egamma', 'z_eu', 'Material', 'Creator', 'Process', 'OrigVol'] )
        self.__fillOrigVol( enrgDF )
        enrgDF['BeamShape'] = self.beamType

        if zlim:
            enrgDF = enrgDF[ (enrgDF.z_eu > zlim[0]) & (enrgDF.z_eu < zlim[1]) ]

        plot_Energy( enrgDF, self.plotpath, Type = Type, save = save, magnets = magnets )

        del enrgDF
        print("plotting done, deleted DF.")

    def hitsByElement(self, elements = [], zlim = [], nBin = 100, ticks = 10, save = 0 ):
        """
        Method to select certain elements as sources and plot hits caused BY THESE elements.
        Requires full element names, no groups implemented yet.
            -- name:    list of names, has to be passed as list, even for single element
            -- nBin:    set number of bins/binning level
            -- ticks:   set the number of ticks on the xaxis (acts on binning)
            -- save:    choose to whether or not save the plot
            -- verbose: switch on/off or set level of verbosity

        RETURNS: the plot
        """
        from Plot import plotSrcHits

        elmDF = self.Thefile['seco_ntuple;1'].pandas.df( ['z_eu', 'Material', 'Creator', 'OrigVol'] )
        self.__fillOrigVol( elmDF )
        elmDF['BeamShape'] = self.beamType

        if zlim:
            elmDF = elmDF[ (elmDF.z_eu > zlim[0]) & (elmDF.z_eu < zlim[1]) ]
        plotSrcHits( elmDF, self.plotpath, elements, nBin, ticks, save, self.verbose )

        del elmDF
        print("plotting done, deleted DF.")