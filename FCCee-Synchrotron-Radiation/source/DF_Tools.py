import pandas as pd
# read general output files (debug, SAD stuff, MDISim output) to DF for analysis
class OutputToDF:

    def __init__( self, txt ):
        self.txt = txt
    
    def read_txt( self, header = 0, verbose = 0, skipLine = 0, dropDupl = 0 ):
        """
        Function to read in general text files to a data frame
            --- header:     specify an array of names for the header
            --- verbose:    set output level
            --- skipLine:   specify number of lines to drop
            --- dropDupl:   specify column on which to drop duplicates
        """
        
        self.df = pd.read_table( self.txt, sep = r'\s+', skiprows = skipLine, index_col = False )
        if header:
            self.df.columns = header
        else:
            print( " *** Warning: no header specified, inferring from file ... ")

        if dropDupl != 0:
            df = df.drop_duplicates( subset = [dropDupl], keep = 'first')
        df = self.df
        return df
    
    def plotData(self, xDat, yDat, xLabel, yLabel, verbose = 0 ):
        """
        General plotting method to examine data stored in a file
            --- xDat, yDat:     columns to plot, needs name as input
            --- xLabel, yLabel: axis labels (could be like tuple?)
            --- verbose:        output level
        """
        plt.figure( figsize = (12, 10) )
        plt.plot( self.df.xDat.tolist(), self.df.yDat.tolist() )
        plt.xlabel( xLabel ); plt.ylabel( yLabel )
        plt.title('dummy title')

