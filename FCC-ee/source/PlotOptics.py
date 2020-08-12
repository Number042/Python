from pandas import read_table
import matplotlib.pyplot as plt
from numpy import pi, double
from Tools import rel_s

class PlotOptics:
    
    def __init__(self, twiss, plotpath, verbose = 0 ):

        self.df = twiss
        self.Smax = self.df.S.max()
        self.plotpath = plotpath
        self.verbose = verbose

    def plotTwissParams( self, twissPara = [], Slim = [], relS = 0, figSize = [40,10], IP = 0 ):
        """
        Function to directly plot a set of twiss parameters
            -- twiss:       baseline twiss (DF)
            -- twissPara:   list of twiss parameters to plot (string)
            -- relS:        choose to plot with IP in the center
            -- figSize:     allows to adjust the size
            -- IP:          sets xlim to +/- 5m
            -- verbose:     set verbosity level
        """
        from VisualSpecs import myColors as colors
        
        if twissPara == []: raise KeyError("Nothing to plot. Specify list of parameters.")
        selection = None

        graph = plt.figure( figsize = (figSize[0], figSize[1]) )
        if twissPara != [] and not relS:
            if self.verbose: print("plotting ", twissPara, "...")
            i = 0
            for param in twissPara:
                plt.plot( self.df.S, self.df[param], ls = '-.', color = colors[i], label = param )
                i += 1
            plt.xlabel('S [m]')
            plt.legend()
        
        elif relS & ('rel_S' in self.df): 
            i = 0
            if Slim == []: raise KeyError('Slim must be specified!')
            
            selection = self.df[ (self.df.rel_S > Slim[0]) & (self.df.rel_S < Slim[1]) ]
            selection = selection.sort_values( by = 'rel_S' )
            
            for param in twissPara:
                
                plt.plot( selection.rel_S, selection[param], color = colors[i], ls = '-.', label = param )
                i += 1
                
            plt.xlabel('S [m]')
            if IP: plt.xlim( -5, 5 )
            plt.legend()
        
        if selection is not None: del selection

        return graph


    def plotBeamSize( self, Srange, eps, delP, collAp = 'None', plane = 'x', scaleXY = 1e2, save = 0 ):
        """
        Method allows to plot horizontal or vertical beam sizes with 10 and 20 sigma envelope
            -- plane:       select horizontal (default) or vertical plane
            -- scaleXY:     scales from [m] to [cm] by default; can be changed
            -- Srange:      choose the range upstream to IP
            -- save:        optional to save a pdf copy
            -- eps, delP, scaleXY:   specify emittance and energy spread
            -- collAp:      give a generic aperture for collimators. If left out, set to max aperture 

        RETURN: the figure
        """
        from Tools import sigm, inventAper
        from VisualSpecs import myColors as colors 
        from VisualSpecs import align_yaxis
    
        Smax =self.df.S.max()

        # plot physical aperture
        #
        maxAper =self.df.APER_1.max()
        print('maximum aperture found:', maxAper)
        print('slected last', Srange, 'm upstream. Scale factor =', scaleXY)

        if collAp == 'None': collAp = maxAper 
        print('set collAp to generic', collAp)
        
        self.df['APER'] = self.df.apply( lambda x: inventAper( x.rel_S, x.NAME, x.APER_1, collAp ), axis = 1 )
        condition = ( self.df.S > Smax - Srange ) & ( self.df.S <= Smax )
        slFr = self.df[condition]

        if 'APER' not in slFr: raise KeyError("Missing column APER")
        
        # init the plot and split x
        #
        fig = plt.figure( figsize = (20,10) ); ax = fig.add_subplot(111)
        twin = ax.twinx()

        ax.plot( slFr.S, slFr.APER*int(scaleXY), lw = 3., color = colors[10] )
        ax.plot( slFr.S, -slFr.APER*int(scaleXY), lw = 3., color = colors[10] )
        ax.set_ylabel('aperture [cm]'); ax.set_ylim( -(maxAper+maxAper/10)*int(scaleXY), (maxAper+maxAper/10)*int(scaleXY) )
        ax.set_xlabel('S [m]')
        twin.set_ylabel('beam size $\\sigma$ [cm]')
        
        if plane == 'x':

            twin.plot( slFr.S, sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[2], label = '$\\sigma_x$' )  
            twin.plot( slFr.S, -sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[2] )

            twin.plot( slFr.S, 10*sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[3], ls = '--', label = '10$\\sigma_x$')  
            twin.plot( slFr.S, -10*sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[3], ls = '--' )  #  

            twin.plot( slFr.S, 20*sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[4], ls = ':', label = '20$\\sigma_x$' )  
            twin.plot( slFr.S, -20*sigm(slFr.BETX, slFr.DX, eps, delP, int(scaleXY)), color = colors[4], ls = ':' )  #  
            align_yaxis(ax, 0, twin, 0); twin.set_ylim( -(maxAper+maxAper/10)*int(scaleXY), (maxAper+maxAper/10)*int(scaleXY) ) 

            title = 'horizontal beam size and physical aperture'
            name = 'physAprt_hrzt_beamSize100m.pdf'
        
        else:

            twin.plot( slFr.S, sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[2], label = '$\\sigma_y$' )  
            twin.plot( slFr.S, -sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[2] )

            twin.plot( slFr.S, 10*sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[3], ls = '--', label = '10$\\sigma_y$')  
            twin.plot( slFr.S, -10*sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[3], ls = '--' )  #  

            twin.plot( slFr.S, 20*sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[4], ls = ':', label = '20$\\sigma_y$' )  
            twin.plot( slFr.S, -20*sigm(slFr.BETY, slFr.DY, eps, delP, int(scaleXY)), color = colors[4], ls = ':' )  #  
            align_yaxis(ax, 0, twin, 0); twin.set_ylim( -(maxAper+maxAper/10)*int(scaleXY), (maxAper+maxAper/10)*int(scaleXY) )

            title = 'vertical beam size and physical aperture'
            name = 'physAprt_vrt_beamSize100m.pdf'

        plt.legend()
        plt.title(title)

        if save: print('saving fig ...', name); plt.savefig( self.plotpath + name, bbox_inches = 'tight', dpi = 70)

        del slFr

        return 0
        
        
         

