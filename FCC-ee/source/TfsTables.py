from pandas import read_table
import matplotlib.pyplot as plt
from numpy import pi
from Tools import rel_s

# read twiss files, should be as flexible as possible
class TfsReader:
    
    def __init__(self, tfs):
        self.tfs = tfs

    def read_twiss(self, relS = 0, verbose = 0):
        
        """
        Function to read general twiss files.
            -- relS:    choose if another column with relative S position is added (IP in the center)
            -- verbose: choose verbosity level
        """
        
        df = read_table(self.tfs, sep = r'\s+', comment = '@', index_col = False, converters = {'NAME':str, 'KEYWORD':str}) 

        # read columns and drop the first one (*) to actually match the right header
        #
        cols = df.columns
        twissHeader = cols[1:]
        if verbose: print('set twiss header:', twissHeader, '\n from cols:', cols)

        # drop last NaN column and reset header 
        # (1st single space in TWISS header causes the issue )
        #
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
        df.columns = twissHeader
        

        df = df.drop(df.index[0])
        df = df.convert_objects(convert_numeric = True)

        # determine the maximum in S
        #
        Lmax = df.S.max()

        if verbose:
            print("----------------------------------")
            print(" DF contains: \n", df.keys(), "\n data tpes are: \n", df.dtypes)
            print("----------------------------------")

        if relS: 
            print(" Add column 'rel_S' -- S position shifted with IP in the center. Using Lmax = ", Lmax)
            df["rel_S"] = df.apply( lambda row: rel_s( df, row, Lmax = Lmax ), axis = 1 )
        
        return df
    
    def read_survey(self, relS = 0, verbose = 0):
        """
        Function to read general survey files.
        """
        surveyDF = read_table(self.tfs, sep = r'\s+', comment = '@', index_col = False)
        
        # read columns and drop the first one (*) to actually match the right header
        #
        cols = surveyDF.columns
        surveyHeader = cols[1:]
        
        # drop last column and reset header
        # (1st single space in SURVEY header causes the issue)
        #
        surveyDF.drop(surveyDF.columns[len(surveyDF.columns)-1], axis=1, inplace=True)
        surveyDF.columns = surveyHeader
        
        surveyDF = surveyDF.drop(surveyDF.index[0])
        surveyDF = surveyDF.convert_objects(convert_numeric = True)

        # determine maximum in S 
        #
        Lmax = surveyDF.S.max()
        
        if verbose:
            print("----------------------------------")
            print(" DF contains: \n", surveyDF.keys(), "\n data tpes are: \n", surveyDF.dtypes)
            print("----------------------------------")

        if relS: 
            print(" Add column 'rel_S' -- S position shifted with IP in the center. Using Lmax = ", Lmax)
            surveyDF["rel_S"] = surveyDF.apply( lambda row: rel_s( surveyDF, row, Lmax = Lmax ), axis = 1 )

        return surveyDF

    def read_sad( self, relS = 0, verbose = 0 ):
        """
        Allows to read in directly the output from SAD (pseudo-twiss). Assumes much simpler header (one line)
            -- relS:    Choose whether or not relative S position is added
            -- verbose: choose verbosity level
        """

        df = read_table( self.tfs, sep = r'\s+', index_col = False )
        
        if relS: 
            print(" Add column 'rel_S' -- S position shifted with IP in the center.")
            df["rel_S"] = df.apply( lambda row: rel_s( df, row ), axis = 1 )
            
        return df

    def checkRing(self, verbose = 0):
        """
        Method to quickly check, if a sequence is closed (ring) or not. If not closed, give fudge factor (2pi - offset)
            -- df:    pass data frame to the function, for example from read_twiss
        """
        angleSum = self.tfs.ANGLE.sum()
        if self.verbose: print ("check")
        print ("---------------------------------- \n Checking, if ring is closed: \n", "angleSum = ", angleSum)
        twoPi = 2*pi
        
        if angleSum != twoPi:
            fudge = 2*pi - angleSum
            print (" ** Ring not closed - offset of: ", fudge)           

    

class PlotOptics:
    
    def __init__(self, twiss, plotpath ):
        self.df = twiss
        self.Smax = self.df.S.max()
        self.plotpath = plotpath

    def plotTwissParams( self, twissPara = [], relS = 0, figSize = [40,10], IP = 0, verbose = 0):
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
        
        if twissPara == []: print("Nothing to plot. Specify list of parameters.")
        
        graph = plt.figure( figsize = (figSize[0], figSize[1]) )
        if twissPara != [] and not relS:
            if verbose: print("plotting ", twissPara, "...")
            i = 0
            for param in twissPara:
                plt.plot( self.df.S, self.df[param], ls = '--', color = colors[i], label = param)
                i += 1
            plt.xlabel('S [m]')
            plt.legend()
        
        elif relS & ('rel_S' in self.df): 
            i = 0
            for param in twissPara:
                plt.plot( self.df.rel_S, self.df[param], color = colors[i], marker = '.', ls = '', label = param)
                i += 1
            plt.xlabel('S [m]')
            if IP: plt.xlim(-5,5)
            plt.legend()
            
        return graph


    def plotBeamSize( self, Srange, eps, delP, plane = 'x', scaleXY = 1e2, save = 0 ):
        """
        Method allows to plot horizontal or vertical beam sizes with 10 and 20 sigma envelope
            -- plane:       select horizontal (default) or vertical plane
            -- scaleXY:     scales from [m] to [cm] by default; can be changed
            -- Srange:      choose the range upstream to IP
            -- save:        optional to save a pdf copy
            -- eps, delP, scaleXY:   specify emittance and energy spread

        RETURN: the figure
        """
        from Tools import sigm
        from VisualSpecs import myColors as colors 
        from VisualSpecs import align_yaxis

        condition = (self.df.S > self.Smax - Srange) & (self.df.S <= self.Smax)
        slFr = self.df[condition]
        print('slected last', Srange, 'm upstream. Scale factor =', scaleXY)
        # init the plot and split x
        #
        fig = plt.figure( figsize = (20,10) ); ax = fig.add_subplot(111)
        twin = ax.twinx()

        # plot physical aperture
        #
        maxAper = self.df.APER.max()
        print('maximum aperture found:', maxAper)

        ax.plot( slFr.S, slFr.APER*scaleXY, lw = 3., color = colors[11] )
        ax.plot( slFr.S, -slFr.APER*scaleXY, lw = 3., color = colors[11] )
        ax.set_ylabel('aperture [cm]'); ax.set_ylim( -(maxAper+maxAper/10)*scaleXY, (maxAper+maxAper/10)*scaleXY )

        
        twin.set_ylabel('beam size $\\sigma$ [cm]')
        
        if plane == 'x':

            twin.plot( slFr.S, sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[2], label = '$\\sigma_x$' )  
            twin.plot( slFr.S, -sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[2] )

            twin.plot( slFr.S, 10*sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[3], ls = '--', label = '10$\\sigma_x$')  
            twin.plot( slFr.S, -10*sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[3], ls = '--' )  #  

            twin.plot( slFr.S, 20*sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[4], ls = ':', label = '20$\\sigma_x$' )  
            twin.plot( slFr.S, -20*sigm(slFr.BETX, slFr.DX, eps, delP, scaleXY), color = colors[4], ls = ':' )  #  
            align_yaxis(ax, 0, twin, 0); twin.set_ylim( -(maxAper+maxAper/10)*scaleXY, (maxAper+maxAper/10)*scaleXY ) 

            plt.legend()    
            plt.title('horizontal beam size and physical aperture')
            if save: print('saving fig ...'); plt.savefig( self.plotpath + 'physAprt_hrzt_beamSize100m.pdf', bbox_inches = 'tight', dpi = 70)
        
        else:

            twin.plot( slFr.S, sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[2], label = '$\\sigma_y$' )  
            twin.plot( slFr.S, -sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[2] )

            twin.plot( slFr.S, 10*sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[3], ls = '--', label = '10$\\sigma_y$')  
            twin.plot( slFr.S, -10*sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[3], ls = '--' )  #  

            twin.plot( slFr.S, 20*sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[4], ls = ':', label = '20$\\sigma_y$' )  
            twin.plot( slFr.S, -20*sigm(slFr.BETY, slFr.DY, eps, delP, scaleXY), color = colors[4], ls = ':' )  #  
            align_yaxis(ax, 0, twin, 0); twin.set_ylim( -(maxAper+maxAper/10)*scaleXY, (maxAper+maxAper/10)*scaleXY )

            plt.legend()
            plt.title('vertical beam size and physical aperture')
            if save: print('saving fig ...'); plt.savefig( self.plotpath + 'physAprt_vrt_beamSize100m.pdf', bbox_inches = 'tight', dpi = 70)

        return fig
        
        
         

