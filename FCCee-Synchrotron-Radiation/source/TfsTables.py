import pandas as pd

# read twiss files, should be as flexible as possible
class TfsReader:
    
    def __init__(self, tfs):
        self.tfs = tfs
        
    def read_twiss(self, verbose = 0):
        
        """
        Function to read general twiss files.
        """

        df = pd.read_table(self.tfs, sep = "\s+", skiprows = 45, index_col = False) 

        # read columns and drop the first one (*) to actually match the right header
        #
        cols = df.columns
        twissHeader = cols[1:]

        # drop NaN column and reset header
        #
        df = df.dropna(axis = 1, how = 'any')
        df.columns = twissHeader

        df = df.drop(df.index[0])
        df = df.convert_objects(convert_numeric = True)

        if verbose:
            print("----------------------------------")
            print(" DF contains: \n", df.keys(), "\n data tpes are: \n", df.dtypes)
            print("----------------------------------")

        return df
    
    def read_survey(self, verbose = 0):
        """
        Function to read general survey files.
        """
        surveyDF = pd.read_table(self.tfs, sep = r'\s+', skiprows = 6, index_col = False)
        
        # read columns and drop the first one (*) to actually match the right header
        #
        cols = surveyDF.columns
        surveyHeader = cols[1:]
        
        # drop NaN column(s) and reset header
        #
        surveyDF = surveyDF.dropna( axis = 1, how = 'any' )
        surveyDF.columns = surveyHeader
        
        surveyDF = surveyDF.drop(surveyDF.index[0])
        surveyDF = surveyDF.convert_objects(convert_numeric = True)
        
        if verbose:
            print("----------------------------------")
            print(" DF contains: \n", surveyDF.keys(), "\n data tpes are: \n", surveyDF.dtypes)
            print("----------------------------------")

        return surveyDF
