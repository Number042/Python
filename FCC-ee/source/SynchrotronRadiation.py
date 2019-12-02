import uproot
import matplotlib.pyplot as plt
from time import time
from pandas import DataFrame
from re import findall, split

class SynchrotronRadiation:
    
    def __init__(self, ntuples, plotpath = '/tmp/', verbose = 0):
        """
        Class to study G4 output tuple; dedicated to SR photons
            -- ntuple:  list of data files (path to the files)
            -- verbose: output level, if > 2, print list of elements in the tuples
        """
        
        self.ntuples = ntuples
        if len( self.ntuples ) == 0: raise RuntimeError( "*** list of datafiles is empty!" )
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

    def __fillOrigVol( self, df ):

        if 'OrigVol' not in df:
            raise Warning("*** No column OrigVol found in the data set!")
        else: 
            if self.verbose: print( 'forward filling OrigVol, replacing string \"none\" ...' )
            df['OrigVol'] = df['OrigVol'].replace( b'none' ).ffill()
        return df
    
    def defaultSRData(self, zlim = [], size = 'all', Type = 'hit', nBin = 100, ticks = 10, legCol = 2, save = 0):
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
        
        # settings for the plot
        #
        plt.figure(figsize = (15,10))
        ax = plt.subplot(111)
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()

        # looping over the datafiles
        #
        for ntuple in self.ntuples:
            
            if Type == 'hit': columns = ['Material', 'z_eu']
            elif Type == 'position': columns = ['z_eu']
            elif Type == 'origin': columns = ['Process','Creator','z_eu']
            
            defDF = self.__readData( ntuple, columns )
            self.__getBeamAperInfo( ntuple )

            if zlim:
                defDF = defDF[ (defDF.z_eu > zlim[0]) & (defDF.z_eu < zlim[1]) ]
        
            plot_defaultData( defDF, ax, self.plotpath, self.__beamType, size, Type, nBin, ticks, self.verbose, legCol, save)        
        
            del defDF


        # global settings for labelling and legend
        #
        plt.locator_params(axis = 'x', nbins = ticks)
        plt.ylabel("photons/bin")
        plt.xlabel("z [m]")

        plt.legend()
        ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.1), ncol = legCol)

        print("plotting done, deleted DF.")

        if save == 1:
            if Type == 'hit':
                plt.savefig( self.plotpath + "SR_hits_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
                print ('saved plot as', self.plotpath, 'SR_hits_beamshape.pdf')

            elif Type == 'position':
                plt.savefig( self.plotpath + "SR_position_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
                print ('saved plot as', self.plotpath, 'SR_position_beamshape.pdf')

            elif Type == 'origin':
                plt.savefig( self.plotpath + "SR_origin_beamshape.pdf", bbox_inches = 'tight', dpi = 150 )
                print ('saved plot as', self.plotpath, 'SR_origin_beamshape.pdf')

        
    def energySpectrum(self, Type = 'general', magnets = [], zlim = [], legCol = 2, save = 0):
        """
        Method to plot the energy of SR photons
            -- Type:    global spectrum or magnet specific
            -- magnets: choose which magnets to plot
            -- save:    whether or not save a copy of the plot 
        
        RETURN: the figure
        """
        from Plot import plot_Energy

        # settings for the plot
        #
        plt.figure( figsize = (15,10) )
        ax = plt.subplot(111)
        plt.rc('grid', linestyle = "--", color = 'grey')
        plt.grid()
        plt.yscale('log')
        plt.xlabel('E$_\\gamma$ [keV]')

        # looping over the datafiles
        #
        for ntuple in self.ntuples:
                
            if Type == 'general': columns = ['z_eu','Egamma', 'Process'] 
            elif Type == 'hit': columns = ['z_eu','Egamma', 'Material', 'Creator'] 
            else: columns = ['z_eu','Egamma', 'OrigVol', 'Creator','Process']
            
            enrgDF = self.__readData( ntuple, columns )
            self.__getBeamAperInfo( ntuple )
            
            if 'OrigVol' in columns: 
                self.__fillOrigVol( enrgDF )
                if self.verbose > 2: print( enrgDF.OrigVol.unique() )

            if zlim:
                enrgDF = enrgDF[ (enrgDF.z_eu > zlim[0]) & (enrgDF.z_eu < zlim[1]) ]

            plot_Energy( enrgDF, ax, self.plotpath, self.__beamType, Type = Type, save = save, magnets = magnets, verbose = self.verbose )
            del enrgDF

        print("plotting done, deleted DF.")
        
        plt.title( 'photon energy distribution - ' + str(Type) )
        plt.legend()
        ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.1), ncol = legCol)

        # mark a 100 keV
        plt.axvline(x = 100, lw = 2.5, ls = '--', color = 'red')
        
        if (save == 1):
            plt.savefig( self.plotpath + "SR_energy_spectrum" + str(Type) + ".pdf", bbox_inches = 'tight', dpi = 50 )
            print ('saved plot as', self.plotpath, 'SR_energy_spectrum' + str(Type) + '.pdf')
    
    def hitsByElement(self, elements = [], zlim = [], binN = 100, ticksN = 10, save = 0 ):
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

        plt.figure( figsize = (15,10) )
        ax = plt.subplot(111)
        plt.rc('grid', linestyle = '--', color = 'grey')
        plt.grid()
        plt.locator_params(axis = 'x', nbins = ticksN)    

        plt.ylabel('photons/bin'); plt.xlabel('z [m]')
        plt.title("Hits from Element(s)")
        
        # looping over datafiles
        #
        for ntuple in self.ntuples:
                
            elmDF = self.__readData( ntuple, columns = ['z_eu', 'Material', 'Creator', 'OrigVol'] )
            self.__getBeamAperInfo( ntuple )
            
            self.__fillOrigVol( elmDF )
            if self.verbose > 2: print( elmDF.OrigVol.unique() )

            if zlim:
                elmDF = elmDF[ (elmDF.z_eu > zlim[0]) & (elmDF.z_eu < zlim[1]) ]

            plotSrcHits( elmDF, ax, self.__beamType, elements )
            del elmDF

        
        plt.legend()
        ax.legend(loc = 'lower center', bbox_to_anchor = (0.5, -0.2), ncol = 6)
    
        print("plotting done, deleted DF.")
        if save == 1: 
            print ("Saving figure as ", self.plotpath, "SR_hitsFrmElmt.pdf")
            plt.savefig( self.plotpath + "SR_hitsFrmElmt.pdf", bbox_inches = 'tight', dpi = 50 )