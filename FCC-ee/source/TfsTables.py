from pandas import read_table
import matplotlib.pyplot as plt
from numpy import pi, double
from Tools import rel_s

# read twiss files, should be as flexible as possible
class TfsReader:
    
    def __init__(self, tfs, verbose = 1):
        self.tfs = tfs
        self.verbose = verbose

    def read_twiss(self, relS = 0 ):
        
        """
        Function to read general twiss files.
            -- relS:    choose if another column with relative S position is added (IP in the center)
            -- verbose: choose verbosity level
        """
        
        specDtypes = { 0:str,   1:str,     2:float,  3:float,  4:float,  5:float,  6:float,  7:float, 8:float,   9:float, 
                      10:float, 11:float, 12:float, 13:float, 14:float, 15:float, 16:float, 17:float, 18:float, 19:float, 
                      20:float, 21:float, 22:float, 23:float, 24:float, 25:float, 26:float, 27:float, 28:float, 29:float, 30:float, 
                      31:str,   32:float, 33:float, 34:float, 35:float, 36:str,   37:float, 38:float, 39:float, 40:float, 41:float, 
                      42:float, 43:float, 44:float, 45:float, 46:float, 47:float, 48:float, 49:float, 50:float, 51:float, 52:float,
                      53:float, 54:float, 55:float, 56:float, 57:float, 58:float, 59:float, 60:float, 61:float, 62:float, 63:float, 
                      64:float, 65:float, 66:float, 67:float, 68:float, 69:float, 70:float, 71:float, 72:float, 73:float, 74:float, 
                      75:float, 76:float, 77:float, 78:float, 79:float } 

        df = read_table( self.tfs, sep = r'\s+', comment = '@', skiprows=[47], dtype = specDtypes )

        # read columns and drop the first one (*) to actually match the right header
        #
        twissHeader = df.columns[1:]
        if self.verbose: print( 'set twiss header:', twissHeader )

        # drop last NaN column and reset header 
        # (1st single space in TWISS header causes the issue )
        #
        df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)
        df.columns = twissHeader

        # determine the maximum in S
        #
        Lmax = df.S.max()

        if self.verbose:
            print("----------------------------------")
            print(" DF contains: \n", df.keys(), "\n data tpes are: \n", df.dtypes)
            print("----------------------------------")

        if relS: 
            print(" Add column 'rel_S' -- S position shifted with IP in the center. Using Lmax = ", Lmax)
            df["rel_S"] = df.apply( lambda row: rel_s( df, row, Lmax = Lmax ), axis = 1 )
        
        return df

    def read_twiss_header( self, parameter ):
        
        header = read_table( self.tfs, nrows = 45, sep = r'\s+' )
        header = header.drop( header.columns[[0, 2]], axis = 1 )
        
        header.columns = ['Parameter', 'Value']
        
        param = header.loc[ header.Parameter == parameter,'Value'].values[0]
        if parameter == 'PARTICLE': param = str( param )
        else: param = double( param )
        
        if self.verbose: print( param, type(param))

        return param
    
    def read_survey(self, relS = 0, verbose = 0):
        """
        Function to read general survey files.
        """
        
        surveyDF = read_table( self.tfs, sep = r'\s+', comment = '@', skiprows = [7], index_col = False, dtype = float )
        
        # read columns and drop the first one (*) to actually match the right header
        #
        surveyHeader = surveyDF.columns[1:]
        
        # drop last column and reset header
        # (1st single space in SURVEY header causes the issue)
        #
        surveyDF.drop( surveyDF.columns[len(surveyDF.columns)-1], axis = 1, inplace = True )
        surveyDF.columns = surveyHeader
        
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

