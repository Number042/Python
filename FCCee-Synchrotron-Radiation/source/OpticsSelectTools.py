import pandas as pd
import re

class DataSelection:
    
    """
    Tool-kit to refine selection on overall input data. 
    """
    
    def __init__(self, df, verbose):
        self.df = df
        self.verbose = verbose
        self._optics = []

    def opticsSelection(self, optics = 'all', verbose = 0):
        """
        Function to select specific optics, put these into a new dataframe that can be passed for further processing. 
            -- optics:  choose which otics to be put into the new frame
            -- verbose: set output level for user information
        RETURN: another frame, holding only data from selected optics
        """
        self._optics = optics
        if optics == []: raise ValueError('Optics list is empty.')
        
        # set up default (empty) frame and list, looping specified optics and appending to new df
        #
        df_opt = pd.DataFrame()
        tmpList = []

        if verbose: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Following frame(s) selected:")
            for optic in self._optics: print("--", optic)
        
        for opt in self._optics: tmpList.append( self.df[self.df.optics.str.contains(opt)] )
        if tmpList == []: raise RuntimeError('No data collected. List of frames empty:', tmpList)
    
        else:
            df_opt = df_opt.append(tmpList)
            df_opt.name = self.df.name
                
        df_opt.name = self.df.name
        return df_opt
        
    
    def get_beamShapes_and_Size(self, df, verbose = 0):
        """
        Function to read all beam types and sizes from a given frame. Allows to check for plotting if desired 
        type and/or size is/are available.
            -- df:      dataframe to pass to this function
            -- verbose: set verbosity level; defaults to 0
        """
        
        # df = self.df
        
        beamTypes = set(df.BeamShape) 
        beamSize = set(df.BeamSize)
        
        if verbose: print ("*-*-*-*-*-*-*-*-*-*-*-*-* \n Available types:", beamTypes, "\n Available sizes:", beamSize)
        
        return beamTypes, beamSize

    def splitNames(self, df, verbose = 0):
        """
        Function to split the content of the 'Name' column that is written in the default frame by 'readG4out' and 'opticsSelection'.
        It splits the strings of that column into 4 different columns for element, type, number and vacuum.
            -- df:      user needs to pass in the data frame to be splitted. If just using self object, another frame would be created
                        from class instance, regardless of possible previous optics selection.
            -- verbose: set the verbosity level
        RETURN: a frame with appended columns holding the splitted content
        """
        
        dfName = df.name
        
        if verbose == 1: 
            print ("-*-*-*-*-*-*-*-*-*-*-*-*-*- \n Selected following data frame:", df.name)
        elif verbose > 1:
            print (df.head())
            print (df.Name)
        
        # mlu -- 11-22-2018 -- new implementation of split names:
        # --> split 'Name' and reuse for shorter element name
        # --> split 'OrigVol' and replace with its plain name
        #
        df['Name'], df['type'], df['vacuum'] = df['Name'].str.split('_', 3).str 
        df['OrigVol'] = df['OrigVol'].str.split('_').str[0]
        
        df.name = dfName
        return df
        
    # Add function for aperture selection, pass this to plot_data if needed
    # extend to more detailed data filtering?
    #
    def aper_select(self, aperture, verbose):
        """
        Function to do some data filtering.
            -- aperture:    allows to choose only certain dimensions; provided by calling function
            -- verbose:     set level of verbosity, also provided by calling function
        
        RETURN: dataframe grouped wrt to aperture selection
        """
        
        df = self.df
        dfName = df.name
        
        if verbose: print ( " -*-*-*-*-*-*-*-*-*-*-*-*- \n", dfName, "holds: \n", df.keys() )
        
        # create a list of available apertures from the frame
        #
        aperList = df.CollDim.unique()
        if verbose: print ( " -*-*-*-*-*-*-*-*-*-*-*-*- \n", "List of apertures: ", aperList )
        
        # slice out SR data from overall frame df
        # pass name from df to sliced df
        #
        df_sliced = df[(df.Creator == 'SynRad') & (df.charge == 0)]
        df_sliced.name = dfName
    
        # check the df name, if collimation data, groupby apertures
        #
        if re.findall('col', df_sliced.name):
            print ("found collimator frame - groupby 'CollDim' \n ----------------------------- \n")
            if verbose: print ("available dimensions:", aperList)

        if aperture == 'all':
            # add the aperture option here?
            print ('selected all apertures!')
            grouped = df_sliced.groupby(['CollDim', 'optics', 'BeamShape'])
            
        else:
            DF = pd.DataFrame()
            
            for i in aperture:
                print ('aperture selected:', i)
                if i in aperList:
                    tmp = df_sliced[df_sliced.CollDim == i]
                    # ~ hits = df_sliced[(df_sliced.) & ()]
                    DF = DF.append(tmp)
                else:
                    raise ValueError('Selected aperture', i, 'not in the list. Available are:', aperList)
                
            grouped = DF.groupby(['CollDim', 'optics', 'BeamShape']) 

        return grouped



