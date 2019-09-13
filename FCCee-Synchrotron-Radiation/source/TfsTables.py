import pandas as pd
import matplotlib.pyplot as plt
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
        
        df = pd.read_table(self.tfs, sep = r'\s+', comment = '@', index_col = False, converters = {'NAME':str, 'KEYWORD':str}) 

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
        surveyDF = pd.read_table(self.tfs, sep = r'\s+', comment = '@', index_col = False)
        
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

        df = pd.read_table( self.tfs, sep = r'\s+', index_col = False )
        
        if relS: 
            print(" Add column 'rel_S' -- S position shifted with IP in the center.")
            df["rel_S"] = df.apply( lambda row: rel_s( df, row ), axis = 1 )
            
        return df
    

class PlotOptics:
    

    def __init__(self, twiss):
        self.df = twiss

    def plotTwissParams( self, twissPara = [], relS = 0, figSize = [40,10], IP = 0, verbose = 0):
        """
        Function to directly plot a set of twiss parameters
            -- twiss:       baseline twiss (DF)
            -- twissPara:   list of twiss parameters to plot (string)
            -- verbose:     set verbosity level
        """
        import VisualSpecs
        colors = VisualSpecs.myColors
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
