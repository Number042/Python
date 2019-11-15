import uproot
import matplotlib.pyplot as plt
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

    def readData( self, beamType = 'pencil', COL = ['open','open'], optics = 'fcc_ee' ):
        """
        Provide ntuple as DataFrame
            -- beamType:    primary transverse distr - pencil, Gauss, etc
            -- COL:         array for horizontal and vertical coll opening (COLH,COLV)
            -- optics:      optional key to distinguish different machine versions
        """
        Thefile = uproot.open( self.ntuple )
        self.df = Thefile['seco_ntuple;1'].arrays( outputtype = DataFrame )
        
        self.beamType = str(beamType)
        self.df['BeamShape'] = self.beamType
        print('setting beamType to', self.beamType )

        COLH,COLV = COL
        if COL != ['open','open']: print('Collimators not fully opened: \n COLH =', COLH, '\n COLV =', COLV )
        else: print('collimators fully open.')

        if 'OrigVol' in self.df:
            if self.verbose: print( 'forward filling OrigVol, replacing string \"none\" ...' )
            self.df['OrigVol'] = self.df['OrigVol'].replace( b'none' ).ffill()
        else: raise Warning("*** No column OrigVol found in the data set!")

        if self.verbose > 1: self.df.head()

    def mergeData( self ):
        # in case there are more than 1 frame, merge them ... stuff done in Tracking better move here? mlu -- 2019-14-11
        return 

    ## also possible to leave this on its own and use it from Plot.py
    def plot_defaultData(self, zlim = [], beam = 'all', size = 'all', Type = 'hit', nBin = 100, ticks = 10, verbose = 0, legCol = 2, save = 0):
        """
        Function to plot data from secondary events, taking into account different beam shapes and sizes. 
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
        return plot_defaultData( self.df, self.plotpath, zlim, beam, size, Type, nBin, ticks, verbose, legCol, save)

    def energySpectrum(self, Type = 'general', magnets = [], save = 0):
        """
        Function to plot the energy of SR photons
            -- Type:    global spectrum or magnet specific
            -- magnets: choose which magnets to plot
            -- save:    whether or not save a copy of the plot 
        
        RETURN: the figure
        """
        from Plot import plot_Energy
        return plot_Energy( self.df, self.plotpath, save, magnets = magnets, Type = Type )

    def srcHits(self, elements = [], zlim = [], nBin = 100, ticks = 10, save = 0 ):
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
        return plotSrcHits( self.df, self.plotpath, elements, zlim,  nBin, ticks, save, self.verbose )

    def EnrgHit( self, zlim = [] ):
        # energy of photons once they impact on the beam pipe vacuum -> Cu

        if zlim:
            print("selected range: zmin =", zlim[0], ' zmax =', zlim[1] )
            tmpdf = self.df[ (self.df.z_eu > zlim[0]) & (self.df.z_eu < zlim[1]) ]
            plt.hist( tmpdf[ (tmpdf.Creator==b'SynRad')& (tmpdf.Material==b'Cu') ].Egamma*1e6, bins = 100 )
        
        else:
            print("plot general data ...")
            plt.hist( self.df[ (self.df.Creator==b'SynRad')& (self.df.Material==b'Cu') ].Egamma*1e6, bins = 100 )
        plt.yscale('log')

        return 



            